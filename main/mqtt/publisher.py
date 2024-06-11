import paho.mqtt.client as mqtt
from google.cloud import pubsub_v1
from assets.credential_key import key

key.get_credential_key()

mqtt_port = 1883
mqtt_broker = "34.101.48.71"
gyro_topic = "sensor/mpu6050/gyro"
accel_topic = "sensor/mpu6050/accel"

project_id = "eco-cyclist-425501-c2"
pubsub_gyro_topic_id = "gyro-topic"
pubsub_accel_topic_id = "accel-topic"

publisher = pubsub_v1.PublisherClient()
gyro_topic_path = publisher.topic_path(project_id, pubsub_gyro_topic_id)
accel_topic_path = publisher.topic_path(project_id, pubsub_accel_topic_id)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe(accel_topic)
    client.subscribe(gyro_topic)


def on_message(client, userdata, msg):
    print(f"Message received from topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == accel_topic:
        future = publisher.publish(accel_topic_path, msg.payload)
        future.result()
    elif msg.topic == gyro_topic:
        future = publisher.publish(gyro_topic_path, msg.payload)
        future.result()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port)
client.loop_forever()