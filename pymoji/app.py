"""Hooks up the routes for the Emojivision web app."""
from datetime import datetime
import logging
import os

from flask import flash, redirect, render_template, request, send_from_directory, url_for
from google.cloud import error_reporting

from pymoji import APP, PROJECT_ID
from pymoji.constants import CLOUD_ROOT, DEMO_PATH, OUTPUT_DIR
from pymoji.faces import process_cloud, process_local
from pymoji.utils import allowed_file, download_json, get_json_name, get_output_name, load_json


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


@APP.route('/emojivision/')
def emojivision_index():
    """Launches a demo run and redirects to the results."""
    with open(DEMO_PATH, 'rb') as image:
        run_args = {
            'image_stream': image,
            'filename': 'demo.jpg',
            'renderer': request.form.get('renderer', 'emoji')
        }
        print('Processing run: {}'.format(run_args))

        id_filename = None
        if APP.testing:
            id_filename = process_local(**run_args)
        else:
            run_args['mime_type'] = 'image/jpeg'
            id_filename = process_cloud(**run_args)

        return redirect(url_for('emojivision', id_filename=id_filename))

    # fallback on root index
    return redirect(url_for('index'))


@APP.route('/emojivision/<id_filename>')
def emojivision(id_filename):
    """Serves the results page for the given ID-filename.

    Args:
        id_filename: a unique filename string
    """
    kwargs = {} # data payload for template

    output_filename = get_output_name(id_filename)
    json_filename = get_json_name(id_filename)

    if APP.testing:
        kwargs['input_image_url'] = url_for('static', filename='uploads/' + id_filename)
        kwargs['output_image_url'] = url_for('static', filename='gen/' + output_filename)
        kwargs['json_url'] = url_for('static', filename='gen/' + json_filename)
    else:
        kwargs['input_image_url'] = CLOUD_ROOT + PROJECT_ID + '/uploads/' + id_filename
        kwargs['output_image_url'] = CLOUD_ROOT + PROJECT_ID + '/gen/' + output_filename
        kwargs['json_url'] = CLOUD_ROOT + PROJECT_ID + '/gen/' + json_filename

    # hidden mode for live debugging
    is_haxxx_mode = request.args.get('haxxx', APP.debug)
    if is_haxxx_mode:
        kwargs['is_haxxx_mode'] = is_haxxx_mode
        if APP.testing:
            json_path = os.path.join(OUTPUT_DIR, json_filename)
            with open(json_path) as json_file:
                kwargs['json_data'] = load_json(json_file)
        else:
            kwargs['json_data'] = download_json(kwargs['json_url'])

    return render_template('result.html', **kwargs)


@APP.route('/', methods=['GET', 'POST'])
def index():
    """Serves the upload form index page. Sucessful submissions redirect to the
    results page for the uploaded ID-filename."""
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
            run_args = {
                'image_stream': image,
                'filename': image.filename,
                'renderer': request.form.get('renderer', 'emoji')
            }
            print('Processing run: {}'.format(run_args))

            id_filename = None
            if APP.testing:
                id_filename = process_local(**run_args)
            else:
                run_args['mime_type'] = image.content_type
                id_filename = process_cloud(**run_args)

            return redirect(url_for('emojivision', id_filename=id_filename))

        flash('File type not allowed')
        return redirect(request.url)

    kwargs = {}

    # hidden mode for live debugging
    is_haxxx_mode = request.args.get('haxxx', APP.debug)
    if is_haxxx_mode:
        kwargs['is_haxxx_mode'] = is_haxxx_mode

    id_filename = request.args.get('id_filename', '')
    if id_filename:
        kwargs['id_filename'] = id_filename

    return render_template("form.html", **kwargs)


@APP.route('/favicon.ico')
def favicon():
    """Flex those guns!"""
    return send_from_directory('static', 'favicon.ico')


@APP.route("/robots.txt")
def robots_txt():
    """Keeps the Robot Parade at bay."""
    return send_from_directory('static', 'robots.txt')


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
