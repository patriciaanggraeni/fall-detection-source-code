import time
import numpy as np
import paho.mqtt.client as mqtt

from google.cloud import logging
from main.processing import predictor
from assets.credential_key import key
from main.helper import database_config
from sklearn.linear_model import LinearRegression

key.get_credential_key()

logging_client = logging.Client()
logger = logging_client.logger("mqtt_messages")

mqtt_port = 1883
mqtt_broker = "34.101.48.71"
gyro_topic = "sensor/mpu6050/gyro"
accel_topic = "sensor/mpu6050/accel"

data_buffer = []
save_interval = 1
message_count = 0
start_time = time.time()
interpolation_target = 600
last_save_time = time.time()


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe(accel_topic)
    client.subscribe(gyro_topic)


def on_message(client, userdata, msg):
    global data_buffer, last_save_time
    global start_time, message_count

    sensor_data = msg.payload.decode('utf-8')
    sensor_array = [float("{:.2f}".format(float(data))) for data in sensor_data.split(',')]
    data_buffer.append(sensor_array)

    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {time.time()}")

    if len(data_buffer) >= interpolation_target:
       save_and_clear_buffer()


def interpolate_data(data):
    target_length = interpolation_target
    original_length = len(data)

    if original_length > target_length:
        return data

    step = original_length / target_length

    interpolated_data = []
    for i in range(target_length):
        index = int(i * step)
        interpolated_data.append(data[index])

    return interpolated_data


def save_and_clear_buffer():
    global data_buffer, last_save_time

    if data_buffer:
        interpolated_data_buffer = [interpolate_data(data) for data in data_buffer]
        result = predictor.make_prediction(data_buffer[:interpolation_target])

        print(f"Hasil Prediksi: {result}")
        print("=======================================================================\n")
        database_config.save_to_database(interpolated_data_buffer, result[0])

        last_save_time = time.time()
        data_buffer.clear()
        last_save_time = time.time()

    print("Data saved to database.")


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(mqtt_broker, mqtt_port)
print(f"Listening for messages on {gyro_topic} and {accel_topic}...\n")
mqtt_client.loop_forever()
