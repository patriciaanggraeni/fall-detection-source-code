import os
import keras
import joblib
import numpy as np

# Gunakan os.path untuk mendapatkan jalur absolut dari file pkl
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, "../../assets/pkl/update/dataset/dataset_v01.pkl")

# Periksa apakah file ada di jalur tersebut
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"File {dataset_path} tidak ditemukan.")

dataset = joblib.load(dataset_path)
model = keras.saving.load_model(os.path.join(current_dir, '../../assets/model/update_v2/resampling/model.keras'))


# Cetak ukuran dataset
print("Ukuran dataset:", dataset.shape)

n_timesteps = dataset.shape[1]
n_channels = dataset.shape[2]

print("Timesteps:", n_timesteps)
print("Channels:", n_channels)


def predict_fall(accel_data, gyro_data):
    data = np.concatenate([accel_data, gyro_data], axis=0)
    data = data.reshape(1, -1)
    data = data.reshape(1, n_channels, n_timesteps, 1)
    prediction = model.predict(data)
    fall_detected = np.argmax(prediction, axis=1)[0]

    return fall_detected

