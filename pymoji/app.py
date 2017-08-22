"""Initializes and configures the Emojivision web app."""
from datetime import datetime
import logging
import time

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from google.cloud import error_reporting
import google.cloud.logging
from werkzeug.utils import secure_filename

from pymoji.constants import CLOUD_ROOT, PROJECT_ID, STATIC_DIR
from pymoji.faces import process_cloud, process_local
from pymoji.utils import allowed_file, get_output_name


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


@APP.route('/emojivision/<input_filename>')
def emojivision(input_filename):
    """Handles the results page."""
    input_filename = input_filename or 'face-input.jpg'
    output_filename = get_output_name(input_filename)

    if APP.testing:
        input_image_url = url_for('static', filename='uploads/' + input_filename)
        output_image_url = url_for('static', filename='gen/' + output_filename)
    else:
        input_image_url = CLOUD_ROOT + 'uploads/' + input_filename
        output_image_url = CLOUD_ROOT + 'gen/' + output_filename

    # TODO Google Cloud Storage
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

            if APP.testing:
                process_local(image, input_filename)
            else:
                process_cloud(image, input_filename, image.content_type)

            return redirect(url_for('emojivision', input_filename=input_filename))

        return redirect(request.url)

    return render_template("form.html")


@APP.route('/favicon.ico')
def favicon():
    """Flex those guns!"""
    return send_from_directory(STATIC_DIR, 'favicon.ico')


@APP.route("/robots.txt")
def robots_txt():
    """Keeps the Robot Parade at bay."""
    return send_from_directory(STATIC_DIR, 'robots.txt')


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
