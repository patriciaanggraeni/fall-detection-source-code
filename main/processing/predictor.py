import numpy as np
import tensorflow as tf
from assets.credential_key import key
from google.cloud import logging

key.get_credential_key()
logging_client = logging.Client()
logger = logging_client.logger("pubsub_messages")

model = tf.keras.models.load_model("../../assets/model/update_v2/resampling/model.keras")


def make_prediction(data_buffer):
    try:
        data = np.array(data_buffer[:600])
        data_buffer.clear()

        data = data.reshape((1, data.shape[0], data.shape[1], 1))

        prediction = model.predict(data)

        print(f"Hasil Prediksi: {prediction}")
        return prediction

    except ValueError as e:
        print(f"Error reshaping data: {e}")
        return

