from pathlib import Path
from google.cloud import storage
from assets.credential_key import key

# Setel variabel lingkungan untuk kredensial akun layanan
key.get_credential_key()

# Inisialisasi klien Google Cloud Storage
client = storage.Client()

# Fungsi untuk mengunduh seluruh struktur folder dari bucket ke dalam folder dataset lokal
bucket_name = "fall-detection-bucket"
prefix = 'sensor_data/'
dl_dir = '../../assets/dataset/'

storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)
blobs = bucket.list_blobs(prefix=prefix)  # Get list of files
for blob in blobs:
    if blob.name.endswith("/"):
        continue
    file_split = blob.name.split("/")
    directory = "/".join(file_split[0:-1])
    Path(directory).mkdir(parents=True, exist_ok=True)
    blob.download_to_filename(blob.name)
