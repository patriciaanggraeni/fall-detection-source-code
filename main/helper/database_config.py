import psycopg2
from datetime import datetime


def create_connection(is_replica=False):
    if is_replica:
        return psycopg2.connect(
            dbname="fall-detection-database-replica",
            user="Anggara191",
            password="buat_tugas_proyek",
            host="34.128.112.193",
            port="5432"
        )
    else:
        return psycopg2.connect(
            dbname="fall-detection",
            user="Anggara191",
            password="buat_tugas_proyek",
            host="34.128.79.147",
            port="5432"
        )


def save_to_database(sensor_data, predictions):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        accel_data = sensor_data[0]
        gyro_data = sensor_data[1]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO sensor_data (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            accel_data[0], accel_data[1],
            accel_data[2], gyro_data[0],
            gyro_data[1], gyro_data[2],
            timestamp
        ))

        sensor_data_id = cursor.fetchone()[0]
        print("\n=====================================")
        print(f"Inserted sensor_data with id: {sensor_data_id}")
        print("=====================================\n")

        predictions = [float(x) for x in predictions]
        cursor.execute("""
            INSERT INTO sensor_predictions (sensor_data_id, task_t01, task_t06, task_t20, task_t21, task_t22, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            sensor_data_id, predictions[0], predictions[1],
            predictions[2], predictions[3],
            predictions[4], timestamp
        ))

        connection.commit()
    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_sensor_predictions_data():
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT 
                id, sensor_data_id, task_t01, 
                task_t06, task_t20, task_t21, 
                task_t22, timestamp 
            FROM 
                sensor_predictions
        """)
        rows = cursor.fetchall()

        return [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in rows]

    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_sensor_data():
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT 
                id, accel_x, accel_y, 
                accel_z, gyro_x, gyro_y, 
                gyro_z, timestamp        
            FROM 
                sensor_data
        """)
        rows = cursor.fetchall()

        return [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in rows]

    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
