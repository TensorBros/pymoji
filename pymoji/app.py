from datetime import datetime
import logging
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from google.cloud import error_reporting
import google.cloud.logging

from pymoji.constants import OUTPUT_PATH, PROJECT_ID, TEMP_FILENAME, TEMP_PATH
from pymoji.faces import main


app = Flask(__name__)
app.config['SECRET_KEY'] = 'so-so-secret' # change this
# IMPORTANT: be extremely careful with config['TRAP_HTTP_EXCEPTIONS']
# Setting to True will break Google App Engine load balancers!!!
# (this probably has to do with GAE expecting a 404 at /_ah/healthcheck)

# Configure logging
if not app.testing:
    client = google.cloud.logging.Client(project=PROJECT_ID)
    # Attaches a Google Stackdriver logging handler to the root logger
    client.setup_logging(logging.INFO)


@app.after_request
def after_request(response):
    # Quick and dirty hack to wipe out caching for now
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    # Security-related best practice headers
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-XSS-Protection', '1')
    return response


@app.route('/emojivision')
def emojivision():
    input_image_url = url_for('static', filename=TEMP_FILENAME)
    output_image_url = None

    if os.path.isfile(OUTPUT_PATH):
        output_image_url = url_for('static', filename='gen/face-input-output.jpg')

    return render_template('result.html',
        input_image_url=input_image_url,
        output_image_url=output_image_url)


@app.route('/', methods=['GET', 'POST'])
def index():
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
        if image and image.filename:
            image.save(TEMP_PATH)
            image.close()
        main(TEMP_PATH, OUTPUT_PATH)

        return redirect(url_for('emojivision'))

    return render_template("form.html")


@app.route("/robots.txt")
def robots_txt():
    return "User-agent: *\nDisallow: /\n"


@app.errorhandler(500)
def server_error(e):
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
    """.format(e), 500
