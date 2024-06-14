import os

from main.processing import predictor
from main.chatbot import telegram_chatbot
from main.mqtt import publisher, subcriber
from main.helper import database_config, get_predict


def main():
    # publisher.connect_to_mqtt()
    # subcriber.connect_to_mqt()

    bot_app = telegram_chatbot.run_bot_app()
    bot_app.run()


if __name__ == "__main__":
    main()
