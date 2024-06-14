import numpy as np
from main.helper import database_config

class_labels = [
    "Berdiri selama 30 detik (D01/01)",
    "Berdiri secara normal dan berjalan (D06/06)",
    "Jatuh ke depan saat mencoba duduk (F01/20)",
    "Jatuh ke belakang saat mencoba duduk (F02/21)",
    "Jatuh ke samping saat mencoba duduk (F03/22)"
]

# Menggunakan variabel global untuk menyimpan prediksi sebelumnya
previous_prediction = set()

def make_predict():
    global previous_prediction

    get_data = database_config.fetch_sensor_predictions_data()  # Mengambil data prediksi dari sensor
    predictions = []

    for data in get_data:
        predicted_class = np.argmax(data[2:7])
        status_predicted = class_labels[predicted_class]
        predictions.append(status_predicted)

    # Menyimpan prediksi yang belum pernah dikirim sebelumnya
    new_predictions = set(predictions) - previous_prediction
    previous_prediction = previous_prediction.union(set(predictions))

    print(list(new_predictions))  # Mengubah set menjadi list sebelum dikirim
    return list(new_predictions)  # Mengembalikan list prediksi baru untuk dikirim

# Contoh pemanggilan fungsi make_predict()
new_predictions = make_predict()
print("Prediksi baru:", new_predictions)
