import os
import keras
import numpy as np

from google.cloud import pubsub_v1
from google.cloud import logging
from assets.credential_key import key
from main.helper import database_config

# Memuat kredensial Google Cloud
key.get_credential_key()

# Inisialisasi logger
logging_client = logging.Client()
logger = logging_client.logger("pubsub_messages")

# Konfigurasi Google Cloud Pub/Sub
project_id = "eco-cyclist-425501-c2"
accel_subscription_name = "accel-topic-sub"
gyro_subscription_name = "gyro-topic-sub"

# Inisialisasi Pub/Sub subscriber
subscriber = pubsub_v1.SubscriberClient()
accel_subscription_path = subscriber.subscription_path(project_id, accel_subscription_name)
gyro_subscription_path = subscriber.subscription_path(project_id, gyro_subscription_name)

# Memuat model yang sudah dilatih
model_path = '../../assets/model/update_v2/resampling/model.keras'
model = keras.saving.load_model(model_path)

# Global variables to store sensor data
accel_data = None
gyro_data = None


# Fungsi untuk menerima pesan dari accel-topic
def accel_callback(message):
    global accel_data
    accel_values = message.data.decode('utf-8').split(',')
    accel_data = np.array([float(accel_values[0]), float(accel_values[1]), float(accel_values[2])])
    # accel_data = message.data.decode('utf-8').split(',')
    # accel_x = float(accel_data[0])
    # accel_y = float(accel_data[1])
    # accel_z = float(accel_data[2])

    log_message = f"Received message from accel-topic: {message.data.decode('utf-8')}"
    print(log_message)
    try:
        logger.log_text(log_message)
    except Exception as e:
        print(f"Failed to log message: {e}")

    # Proses data sensor dari pesan
    # process_accel_data(message.data)
    # print(f"Accelerometer data: X={accel_x}, Y={accel_y}, Z={accel_z}")

    message.ack()

    if accel_data is not None and gyro_data is not None:
        make_prediction_and_save()


# Fungsi untuk menerima pesan dari gyro-topic
def gyro_callback(message):
    global gyro_data
    gyro_values = message.data.decode('utf-8').split(',')
    gyro_data = np.array([float(gyro_values[0]), float(gyro_values[1]), float(gyro_values[2])])
    # gyro_data = message.data.decode('utf-8').split(',')
    # gyro_x = float(gyro_data[0])
    # gyro_y = float(gyro_data[1])
    # gyro_z = float(gyro_data[2])

    log_message = f"Received message from gyro-topic: {message.data.decode('utf-8')}"
    print(log_message)
    try:
        logger.log_text(log_message)
    except Exception as e:
        print(f"Failed to log message: {e}")

    # Proses data sensor dari pesan
    # process_gyro_data(message.data)
    # print(f"Accelerometer data: X={gyro_x}, Y={gyro_y}, Z={gyro_z}")

    message.ack()

    if accel_data is not None and gyro_data is not None:
        make_prediction_and_save()


def make_prediction_and_save():
    global accel_data, gyro_data

    try:
        # Pastikan data akselerometer dan gyroskop adalah array dengan dimensi yang sesuai
        accel_data_array = np.array(accel_data)
        gyro_data_array = np.array(gyro_data)

        # Gabungkan data akselerometer dan gyroskop
        data = np.concatenate([accel_data_array, gyro_data_array], axis=0)

        # Pastikan bentuk data sesuai dengan input model
        n_timesteps = 600
        n_channels = 6

        # Bentuk ulang data menjadi (1, n_timesteps, n_channels, 1)
        data = data.reshape(1, n_channels, n_timesteps, 1)

        # Lakukan prediksi
        prediction = model.predict(data)

        # Interpretasikan hasil prediksi
        fall_detected = np.argmax(prediction, axis=1)[0]
        print(f"Fall detected: {fall_detected}")

        # Buat dictionary dengan data sensor dan hasil prediksi
        data_dict = {
            'accel_x': accel_data[0],
            'accel_y': accel_data[1],
            'accel_z': accel_data[2],
            'gyro_x': gyro_data[0],
            'gyro_y': gyro_data[1],
            'gyro_z': gyro_data[2],
            'fall_detected': fall_detected,
            'timestamp': 'NOW()'
        }

        # Simpan data ke dalam database
        database_config.save_to_database(data_dict)
        print("Data saved to database successfully.")

        # Log hasilnya
        logger.log_text("Data saved to database: " + str(data_dict))

    except Exception as e:
        print(f"Error in make_prediction_and_save: {e}")
        logger.log_text(f"Error in make_prediction_and_save: {e}")

    finally:
        # Reset the global variables
        accel_data = None
        gyro_data = None


# Mendengarkan pesan dari accel-subscription
streaming_pull_future_accel = subscriber.subscribe(accel_subscription_path, callback=accel_callback)
print(f"Listening for messages on {accel_subscription_path}..\n")

# Mendengarkan pesan dari gyro-subscription
streaming_pull_future_gyro = subscriber.subscribe(gyro_subscription_path, callback=gyro_callback)
print(f"Listening for messages on {gyro_subscription_path}..\n")

try:
    streaming_pull_future_accel.result()
    streaming_pull_future_gyro.result()
except KeyboardInterrupt:
    streaming_pull_future_accel.cancel()
    streaming_pull_future_gyro.cancel()
