"""Initializes and configures the Emojivision web app."""
from datetime import datetime
import logging

from flask import Flask, flash, redirect, render_template, request, url_for
from google.cloud import error_reporting
import google.cloud.logging

from pymoji.constants import OUTPUT_PATH, PROJECT_ID, TEMP_FILENAME, TEMP_PATH
from pymoji.faces import main
from pymoji.utils import generate_output_name, save_to_cloud


APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'so-so-secret' # change this
# IMPORTANT: be extremely careful with config['TRAP_HTTP_EXCEPTIONS']
# Setting to True will break Google App Engine load balancers!!!
# (this probably has to do with GAE expecting a 404 at /_ah/healthcheck)

# Configure logging
if not APP.testing:
    LOGGER = google.cloud.logging.Client(project=PROJECT_ID)
    # Attaches a Google Stackdriver logging handler to the root logger
    LOGGER.setup_logging(logging.INFO)


@APP.after_request
def after_request(response):
    """Standard Flask post-request hook."""

    # Quick and dirty hack to wipe out caching for now
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, '\
        'pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    # Security-related best practice headers
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-XSS-Protection', '1')
    return response


@APP.route('/emojivision')
def emojivision():
    """Handles the results page."""
    input_image_url = request.args.get('input_image_url')
    output_image_url = request.args.get('output_image_url')
    return render_template(
        'result.html',
        input_image_url=input_image_url,
        output_image_url=output_image_url
    )


@APP.route('/', methods=['GET', 'POST'])
def index():
    """Handles the index page."""
    if request.method == 'POST':
        # check if the post request has an image
        if 'image' not in request.files:
            flash('No image')
            return redirect(request.url)
        image = request.files['image']
        # if user does not select file, browser submits an empty part sans filename
        if image.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # handle valid files
        if image and image.filename:
            # default urls for test image
            input_image_url = url_for('static', filename=TEMP_FILENAME)
            output_image_url = url_for('static', filename='gen/face-input-output.jpg')
            image.save(TEMP_PATH)
            image.close()
            main(TEMP_PATH, OUTPUT_PATH)

            # upload images to google cloud storage
            if not APP.testing:
                with open(TEMP_PATH, 'rb') as input_image:
                    input_image_url = save_to_cloud(input_image, image.filename, image.content_type)
                with open(OUTPUT_PATH, 'rb') as output_image:
                    output_filename = generate_output_name(image.filename)
                    output_image_url = save_to_cloud(output_image, output_filename,
                        image.content_type)

            return redirect(url_for('emojivision',
                input_image_url=input_image_url,
                output_image_url=output_image_url))

        return redirect(request.url)

    return render_template("form.html")


@APP.route("/robots.txt")
def robots_txt():
    """Keeps the Robot Parade at bay."""
    return "User-agent: *\nDisallow: /\n"


@APP.errorhandler(500)
def server_error(error):
    """Error handler that reports exceptions to Stackdriver Error Reporting.

    Note that this is only used iff DEBUG=False
    """
    http_context = error_reporting.build_flask_context(request)
    error_client = error_reporting.Client(project=PROJECT_ID)
    error_client.report_exception(http_context=http_context)
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(error), 500
