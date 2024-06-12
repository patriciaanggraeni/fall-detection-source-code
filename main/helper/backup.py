def sensor_callback(message):
    global data_buffer

    sensor_data = message.data.decode('utf-8')
    sensor_array = [float(val) for val in sensor_data.split(',')]
    data_buffer.append(sensor_array)

    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {time.time()}")

    message.ack()

    if len(data_buffer) >= 600:
        predictor.make_prediction(data_buffer)

        # for data in data_buffer:
        #     database_config.save_to_database(data, predictions)

        data_buffer.clear()

    if len(data_buffer) >= 600:
        for sensor_array in data_buffer:
            # Pecah data sensor menjadi variabel-variabel
            gyro_x, gyro_y, gyro_z = sensor_array[:3]
            accel_x, accel_y, accel_z = sensor_array[3:]

            # Lakukan prediksi dan simpan ke database
            predictions = predictor.make_prediction(sensor_array)
            database_config.save_to_database((gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z), predictions)

        # Bersihkan data buffer setelah selesai diproses
        data_buffer.clear()


data_buffer = []


def sensor_callback(message):
    global data_buffer

    sensor_data = message.data.decode('utf-8')
    sensor_array = [float(val) for val in sensor_data.split(',')]
    data_buffer.append(sensor_array)

    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {time.time()}")

    message.ack()

    if len(data_buffer) >= 600:
        predictions = predictor.make_prediction(data_buffer)
        print(f"Hasil Prediksi: {predictions}")

        # Pastikan panjang prediksi sesuai dengan panjang data_buffer
        if len(predictions) == len(data_buffer):
            for data, prediction in zip(data_buffer, predictions):
                # Prediksi mungkin berbentuk array numpy, ubah menjadi list
                prediction_list = prediction.tolist()
                database_config.save_to_database(data, prediction_list)

        data_buffer.clear()


import psycopg2
from datetime import datetime

# Koneksi ke database
conn = psycopg2.connect(
    dbname="fall-detection",
    user="Anggara191",
    password="buat_tugas_proyek",
    host="34.128.79.147",
    port="5432"
)
cur = conn.cursor()


def save_to_database(sensor_data, predictions):
    global conn, cur

    timestamp = datetime.now()

    insert_sensor_data_query = '''
    INSERT INTO sensor_data (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    '''
    cur.execute(insert_sensor_data_query, (
        sensor_data[0], sensor_data[1],
        sensor_data[2], sensor_data[3],
        sensor_data[4], sensor_data[5],
        timestamp)
    )

    sensor_data_id = cur.fetchone()[0]

    insert_predictions_query = '''
    INSERT INTO sensor_predictions (sensor_data_id, task_T01, task_T06, task_T20, task_T21, task_T22)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    cur.execute(insert_predictions_query, (sensor_data_id, *predictions))

    conn.commit()
    print("Data berhasil dimasukkan ke dalam database.")

def sensor_callback(message):
    global data_buffer

    sensor_data = message.data.decode('utf-8')
    sensor_array = [float(val) for val in sensor_data.split(',')]
    data_buffer.append(sensor_array)

    message.ack()

    if len(data_buffer) >= 600:
        predictions = predictor.make_prediction(data_buffer)
        print(f"Hasil Prediksi: {predictions}")

        # Pastikan panjang prediksi sesuai dengan panjang data_buffer
        if len(predictions) == len(data_buffer):
            for data, prediction in zip(data_buffer, predictions):
                # Prediksi mungkin berbentuk array numpy, ubah menjadi list
                prediction_list = prediction.tolist()
                database_config.save_to_database(data, prediction_list)

        data_buffer.clear()

    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {datetime.time()}")

    message.ack()



######################################################
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
    if msg.topic == accel_topic:
        future = publisher.publish(accel_topic_path, msg.payload)
        future.result()
    elif msg.topic == gyro_topic:
        future = publisher.publish(gyro_topic_path, msg.payload)
        future.result()

    print(f"Message received from topic {msg.topic}: {msg.payload.decode()}")


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(mqtt_broker, mqtt_port)
mqtt_client.loop_forever()

def on_message(client, userdata, msg):
    global data_buffer

    sensor_data = msg.payload.decode('utf-8')
    sensor_array = [float(val) for val in sensor_data.split(',')]
    data_buffer.append(sensor_array)

    print(f"Received message: {sensor_data}")
    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {time.time()}")

    if len(data_buffer) >= 600:
        predictions = predictor.make_prediction(data_buffer)
        print(f"Hasil Prediksi: {predictions}")
        print(f"Length of predictions: {len(predictions)}")
        print(f"Length of data_buffer: {len(data_buffer)}")

        # Check if predictions is a single prediction or multiple predictions
        if len(predictions) == 1 and len(data_buffer) > 1:
            # Duplicate the single prediction for each data point in the buffer
            predictions = predictions * len(data_buffer)
        elif len(predictions) != len(data_buffer):
            print("Error: Length of predictions does not match length of data buffer.")
            return

        for data, prediction in zip(data_buffer, predictions):
            # Prediksi mungkin berbentuk array numpy, ubah menjadi list
            prediction_list = prediction.tolist()
            print(f"Saving data: {data} with prediction: {prediction_list}")
            database_config.save_to_database(data, prediction_list)

        data_buffer.clear()


def on_message(client, userdata, msg):
    global data_buffer

    sensor_data = msg.payload.decode('utf-8')
    sensor_array = [float(data) for data in sensor_data.split(',')]
    data_buffer.append(sensor_array)

    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {time.time()}")

    if len(data_buffer) >= 600:
        predict = predictor.make_prediction(data_buffer)
        database_config.save_to_database(data_buffer, predict)

def save_to_database(sensor_data, predictions):
    global conn, cur

    timestamp = datetime.now()

    insert_sensor_data_query = '''
    INSERT INTO sensor_data (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    '''
    cur.execute(insert_sensor_data_query, (
        sensor_data[0],  # accel_x
        sensor_data[1],  # accel_y
        sensor_data[2],  # accel_z
        sensor_data[3],  # gyro_x
        sensor_data[4],  # gyro_y
        sensor_data[5],  # gyro_z
        timestamp
    ))
    sensor_data_id = cur.fetchone()[0]

    insert_predictions_query = '''
    INSERT INTO sensor_predictions (sensor_data_id, task_t01, task_t06, task_t20, task_t21, task_t22)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    cur.execute(insert_predictions_query, (
        sensor_data_id,
        predictions[0],
        predictions[1],
        predictions[2],
        predictions[3],
        predictions[4]
    ))

    conn.commit()
    print("Data berhasil dimasukkan ke dalam database.")

def on_message(client, userdata, msg):
    global data_buffer

    sensor_data = msg.payload.decode('utf-8')
    sensor_array = [float(data) for data in sensor_data.split(',')]
    data_buffer.append(sensor_array)

    print(f"Current buffer length: {len(data_buffer)}")
    print(f"Received message at: {time.time()}")
    print(f"Panjang dari array 2d: {len(data_buffer)}")

    if len(data_buffer) >= 600:
        accel_data = data_buffer[0]
        gyro_data = data_buffer[1]

        print(f"Data buffer before prediction: {data_buffer}")
        predict = predictor.make_prediction(data_buffer)
        print(f"Predictions: {predict}")

        database_config.save_to_database(accel_data, gyro_data, predict)
        data_buffer.clear()


def save_to_database(data_buffer, predictions):
    connection = None
    cursor = None
    timestamp = datetime.now()

    try:
        connection = create_connection()
        cursor = connection.cursor()

        for data, prediction in zip(data_buffer, predictions):
            accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = data
            insert_sensor_data_query = '''
            INSERT INTO sensor_data (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            '''
            cursor.execute(insert_sensor_data_query, (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, timestamp))
            sensor_data_id = cursor.fetchone()[0]

            insert_predictions_query = '''
            INSERT INTO sensor_predictions (sensor_data_id, task_t01, task_t06, task_t20, task_t21, task_t22)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_predictions_query, (sensor_data_id, prediction[0], prediction[1], prediction[2], prediction[3], prediction[4]))

        connection.commit()
        print("Data berhasil dimasukkan ke dalam database.")

    except Exception as error:
        print(f"Failed to insert record into database table: {error}")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()