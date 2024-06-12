import time
import datetime
import paho.mqtt.client as mqtt
from google.cloud import logging
from assets.credential_key import key
from main.processing import predictor
from main.helper import database_config

key.get_credential_key()

logging_client = logging.Client()
logger = logging_client.logger("mqtt_messages")

mqtt_port = 1883
mqtt_broker = "34.101.48.71"
gyro_topic = "sensor/mpu6050/gyro"
accel_topic = "sensor/mpu6050/accel"

data_buffer = []


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe(accel_topic)
    client.subscribe(gyro_topic)


last_save_time = time.time()


def on_message(client, userdata, msg):
    global data_buffer, last_save_time

    # Decode payload dari pesan MQTT dan konversi menjadi list float
    sensor_data = msg.payload.decode('utf-8')
    sensor_array = [float(data) for data in sensor_data.split(',')]

    # Tambahkan data ke dalam buffer
    data_buffer.append(sensor_array)

    # Cetak panjang buffer dan waktu penerimaan pesan
    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {time.time()}")

    # Jika buffer mencapai 600 data atau telah berlalu 1 detik, simpan data ke database
    if len(data_buffer) >= 600 or time.time() - last_save_time >= 1:
        save_and_clear_buffer()
        last_save_time = time.time()


def save_and_clear_buffer():
    global data_buffer

    # Simpan data ke database
    database_config.save_to_database(data_buffer)

    # Bersihkan buffer
    data_buffer.clear()

    print("Data saved to database.")


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(mqtt_broker, mqtt_port)
print(f"Listening for messages on {gyro_topic} and {accel_topic}...\n")
mqtt_client.loop_forever()
