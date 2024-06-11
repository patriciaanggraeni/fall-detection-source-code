import time
from tabulate import tabulate
from google.cloud import storage
from assets.credential_key import key

# memuat kunci credential
key.get_credential_key()

# set clientnya
client = storage.Client()
project_id = "eco-cyclist-425501-c2"

# menambungkan project beserta bucketnya
client.project = project_id
buckets = client.list_buckets()

# memasukkan daftar bucket ke dalam list
bucket_list = [(bucket.name, time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(bucket.time_created.timestamp()))) for bucket in buckets]

# membuat header tabel
headers = ["Bucket Name", "Created"]

# menampilkan daftar bucket yang tersedia menggunakan tabel
print(tabulate(bucket_list, headers=headers, tablefmt="grid"))