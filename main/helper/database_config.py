import psycopg2


def save_to_database(data):
    try:
        # Ganti dengan kredensial database Anda
        conn = psycopg2.connect(
            dbname="fall-detection",
            user="Anggara191",
            password="buat_tugas_proyek",
            host="34.128.79.147",
            port="5432"
        )
        cur = conn.cursor()

        # Query untuk memasukkan data
        query = """
        INSERT INTO sensor_data (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, fall_detected, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cur.execute(query, (
            data['accel_x'], data['accel_y'], data['accel_z'],
            data['gyro_x'], data['gyro_y'], data['gyro_z'],
            data['fall_detected']
        ))

        conn.commit()
        cur.close()
        conn.close()
        print("Data inserted successfully")

    except Exception as e:
        print(f"Error saving data to database: {e}")
        raise
