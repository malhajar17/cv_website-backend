from celery import Celery
from .databaseUtils import save_recording_url, create_session
from .recordingUtils import upload_to_blob


cv_backend_synchronizer = Celery('cv_backend_synchronizer', broker='redis://localhost:6379/0')

@cv_backend_synchronizer.task
def process_recording(recording):
    url = upload_to_blob(recording)
    save_recording_url(url)

@cv_backend_synchronizer.task
def create_new_session(account_id):
    create_session(account_id)
