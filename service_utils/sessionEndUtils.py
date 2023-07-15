import glob
import os

from azure.storage.blob import BlobServiceClient


def upload_recordings_and_get_urls(recordings_path):
    connect_str = os.getenv('AZURE_STORAGE_BLOB_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    gs_urls = []
    re_urls = []

    for filename in os.listdir(recordings_path):
        if filename.startswith('gs'):
            container_name = 'generated-speech'
            urls = gs_urls
        elif filename.startswith('re'):
            container_name = 'recorded-speech'
            urls = re_urls
        else:
            continue  # skip files that don't start with 'gs' or 're'

        blob_client = blob_service_client.get_blob_client(container_name, filename)
        with open(os.path.join(recordings_path, filename), "rb") as data:
            blob_client.upload_blob(data,overwrite=True)
        urls.append(blob_client.url)
    # After all files have been uploaded, delete them from the directory
    for filename in glob.glob(os.path.join(recordings_path, 'gs*')):
        os.remove(filename)

    for filename in glob.glob(os.path.join(recordings_path, 're*')):
        os.remove(filename)

    return gs_urls, re_urls

def extract_info_from_links(links):
    result = []
    for link in links:
        parts = link.split('/')[-1].split('_')  # Split the last part of the URL
        if len(parts) != 4 or parts[0] not in ['gs', 're']:  # Check if the URL follows the expected format
            continue
        account_id = int(parts[1])
        session_id = int(parts[2])
        sequence = int(parts[3].split('.')[0])  # Remove the file extension from the sequence number
        result.append({
            "accountID": account_id,
            "sessionID": session_id,
            "sequence": sequence,
            "link": link
        })
    return result
