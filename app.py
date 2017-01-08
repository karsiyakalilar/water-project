"""
    This is an image processing micro-app for "We-Are-Water"
    It uses Flask to serve a landing page where a client can
    apply a watermark to their images

    Images are temporarily stored in a ./uploads folder
    and are processed and saved to ./target_images 
    and are returned to the client

    A scheduled maintenance jobs cleans upload directories ever so often

"""
import os
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from gen_watermark import generate

import glob
from apscheduler.schedulers.background import BackgroundScheduler

# Constants
FIVER = 5
FIFTEEN_MINUTES = 60 * 15
THRITY_MINUTES = 60 * 30
HOURLY = 60 * 60

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['TARGET_FOLDER'] = './target_images/'
app.config['ASSET_FOLDER'] = './assets/'
app.config["WATERMARK_IMAGE"] = "./assets/water.png"

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

## start and schedule jobs
def maintain_dirs():
    """
      Checks upload and target directories and removes file if necessary
    """
    with app.app_context():
        upload_folder = app.config['UPLOAD_FOLDER']
        target_images_folder = app.config["TARGET_FOLDER"]

        current_uploaded_items = glob.glob(upload_folder + "*")
        current_target_folder_items = glob.glob(target_images_folder + "wm_*")

        if len(current_uploaded_items) > 0:
            print("upload folder count: %s " % len(current_uploaded_items))
            [os.remove(i) for i in current_uploaded_items]
        else:
            print("nothing to remove in upload folder")

        if len(current_target_folder_items) > 0:
            print("target folder count: %s " % len(current_target_folder_items))
            [os.remove(i) for i in current_target_folder_items]
            
        else:
            print("nothing to remove in target folder")

apsched = BackgroundScheduler()
apsched.add_job(maintain_dirs, 'interval', seconds=THRITY_MINUTES)
apsched.start()
## TODO: refactor into a different file
print("Initialized mainter")

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)

        # Move the file form the temporal folder to
        # the upload folder we setup
        full_originating_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(full_originating_path)
        
        watermarked_image_name = "wm_" + filename
        full_destination_path = os.path.join(app.config['TARGET_FOLDER'], watermarked_image_name)

        try:
            print("Generating watermark")
            generate(full_originating_path, 
                     full_destination_path,
                     app.config["WATERMARK_IMAGE"])
        except:
            print("Something went wrong")
            return redirect(url_for('err_file'), filename="something_wrong")

        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        print("Giving the uploaded file back")
        return redirect(url_for('target_file',
                                filename=watermarked_image_name))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/err/<filename>')
def err_file(filename):
    return send_from_directory(app.config['ASSET_FOLDER'],
                               filename)

@app.route('/targets/<filename>')
def target_file(filename):
    return render_template('target.html', 
                          imageURL=url_for('target_images', filename=filename))
                          # imageURL=os.path.join(app.config['TARGET_FOLDER'], filename))

@app.route('/target_images/<filename>')
def target_images(filename):
    return send_from_directory(app.config['TARGET_FOLDER'],filename)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8000"),
        debug=True
    )


# using the scaffold code from here:
# http://code.runnable.com/UhLMQLffO1YSAADK/handle-a-post-request-in-flask-for-python