import firebase_admin
from firebase_admin import credentials, storage
import streamlit as st

STORAGE_BUCKET = "reefchecktest.firebasestorage.app"


sa_info = dict(st.secrets["gcp_service_account"])

with open("serviceAccount.json", "w") as f:
    f.write(json.dumps(sa_info))

# authentication
@st.cache_resource
def get_database_session(url):
    cred = credentials.Certificate(load_json("serviceAccount.json"))
    firebase_admin.initialize_app(cred, {
            'storageBucket': STORAGE_BUCKET
        })

# call the authentication function
get_database_session(STORAGE_BUCKET)

# upload file
def upload_file(file_path, destination_blob_name):
    """Uploads a file to the bucket."""
    # Get a reference to the cloud storage bucket
    bucket = storage.bucket()

    # Create a blob with a "path" and upload the file
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)

    # Make the blob publicly viewable
    blob.make_public()
    print(f"File uploaded to {blob.public_url}")
