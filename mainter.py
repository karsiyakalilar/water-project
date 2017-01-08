import os
import glob
from apscheduler.scheduler import Scheduler


def maintain_dirs():
    """
      Checks upload and target directories and cleans
    """
    with app.app_context():
      upload_folder = app.config['UPLOAD_FOLDER']
      target_images_folder = app.config["TARGET_FOLDER"]

      current_uploaded_items = glob.glob(upload_folder + "*")
      current_target_folder_items = glob.glob(target_images_folder, "wm_*")

      if len(current_uploaded_items) > 0:
        print("upload folder count: %s " % len(current_uploaded_items))
        print("removing yoself")

      if len(current_target_folder_items) > 0:
        print("target folder count: %s " % len(current_target_folder_items))
        print("removing yoself")

FIVER = 5
FIFTEEN_MINUTES = 60 * 15
THRITY_MINUTES = 60 * 30
HOURLY = 60 * 60

@app.before_first_request
def initialize():
    apsched = Scheduler()
    apsched.start()
    apsched.add_interval_job(maintain_dirs, seconds=FIVER)
