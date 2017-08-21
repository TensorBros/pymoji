"""Initializes and configures the Emojivision web app."""
from datetime import datetime
import logging
import os
import time

from flask import Flask, flash, redirect, render_template, request, url_for
from google.cloud import error_reporting
import google.cloud.logging
from werkzeug.utils import secure_filename

from pymoji.constants import OUTPUT_DIR, PROJECT_ID
from pymoji.faces import process_cloud, process_local
from pymoji.utils import allowed_file, generate_output_name


APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'so-so-secret' # change this
# IMPORTANT: be extremely careful with config['TRAP_HTTP_EXCEPTIONS']
# Setting to True will break Google App Engine load balancers!!!
# (this probably has to do with GAE expecting a 404 at /_ah/healthcheck)
APP.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB upload limit

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
        if image and allowed_file(image.filename):
            timestamp = int(round(time.time() * 1000))
            input_filename = str(timestamp) + '_' + secure_filename(image.filename)
            output_filename = generate_output_name(input_filename)
            local_output_path = os.path.join(OUTPUT_DIR, output_filename)
            input_image_url = None
            output_image_url = None

            if APP.testing:
                (input_image_url, output_image_url) = process_local(image, input_filename,
                    output_filename, local_output_path)
            else:
                (input_image_url, output_image_url) = process_cloud(image, input_filename,
                    output_filename, local_output_path)

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
