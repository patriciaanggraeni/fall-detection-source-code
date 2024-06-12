import psycopg2
from datetime import datetime


def create_connection():
    return psycopg2.connect(
        dbname="fall-detection",
        user="Anggara191",
        password="buat_tugas_proyek",
        host="34.128.79.147",
        port="5432"
    )


def save_to_database(sensor_data):
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
              VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            accel_data[0], accel_data[1],
            accel_data[2], gyro_data[0],
            gyro_data[1], gyro_data[2],
            timestamp
        ))

        connection.commit()
        print("\n\n===================================")
        print("DATA BERHASIL DI SIMPAN KE DATABASE")
        print("===================================\n\n")
    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


