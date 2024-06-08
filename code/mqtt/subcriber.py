import os
from google.cloud import pubsub_v1
from google.cloud import logging
from assets.credential_key import key

key.get_credential_key()

logging_client = logging.Client()
logger = logging_client.logger("pubsub_messages")

project_id = "eco-cyclist-425501-c2"
accel_subscription_name = "accel-topic-sub"
gyro_subscription_name = "gyro-topic-sub"

subscriber = pubsub_v1.SubscriberClient()
accel_subscription_path = subscriber.subscription_path(project_id, accel_subscription_name)
gyro_subscription_path = subscriber.subscription_path(project_id, gyro_subscription_name)


def accel_callback(message):
    accel_data = message.data.decode('utf-8').split(',')
    accel_x = float(accel_data[0])
    accel_y = float(accel_data[1])
    accel_z = float(accel_data[2])

    print(f"Accelerometer data: x = {accel_x}, y = {accel_y}, z = {accel_z}")

    result = f"Accelerometer data: x = {accel_x}, y = {accel_y}, z = {accel_z}"
    logger.log_text(result)
    message.ack()


def gyro_callback(message):
    gyro_data = message.data.decode('utf-8').split(',')
    gyro_x = float(gyro_data[0])
    gyro_y = float(gyro_data[1])
    gyro_z = float(gyro_data[2])

    print(f"Gyroscope data: x = {gyro_x}, y = {gyro_y}, z = {gyro_z} \n")

    result = f"Gyroscope data: x = {gyro_x}, y = {gyro_y}, z = {gyro_z} \n"
    logger.log_text(result)
    message.ack()


streaming_pull_future_accel = subscriber.subscribe(accel_subscription_path, callback=accel_callback)
print(f"Listening for messages on {accel_subscription_path}..")

streaming_pull_future_gyro = subscriber.subscribe(gyro_subscription_path, callback=gyro_callback)
print(f"Listening for messages on {gyro_subscription_path}..\n")

try:
    streaming_pull_future_accel.result()
    streaming_pull_future_gyro.result()
except KeyboardInterrupt:
    streaming_pull_future_accel.cancel()
    streaming_pull_future_gyro.cancel()
