import os
import time
import asyncio
import threading
import pandas as pd
import paho.mqtt.client as mqtt

from typing import Final
from main.helper import get_predict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, \
    filters, ContextTypes

# Mendeklarasikan variabel konstan TOKEN dan BOT_USERNAME
TOKEN: Final = '7436003581:AAFS5Bs811Q-lqOXYZlWHqhd39_RO_80F0c'
BOT_USERNAME: Final = '@Falldetectionkelompok2_bot'

# Mendefinisikan konstanta untuk setiap tahap dalam percakapan
USERNAME, RELATIONSHIP, CONFIRM, EDIT, CONNECT, ACCOUNT = range(6)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_keyboard = [
        ["/subscribe", "/contactlist"],
        ["/connect", "/disconnect"],
        ["/myaccount"]
    ]
    await update.message.reply_text('Halo! Selamat datang di Bot Telegram Kami',
                                    reply_markup=ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True))


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Username Anda?\n\nJika ingin membatalkan pendaftaran silahkan ketik /cancel')
    return USERNAME


async def username_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = update.message.text.strip()
    if not user_username.replace(" ", "").isalpha():
        await update.message.reply_text('Username tidak boleh mengandung simbol atau angka.')
        return USERNAME
    else:
        context.user_data['username'] = user_username
        if context.user_data.get('edit_mode'):
            context.user_data['edit_mode'] = False
            await show_confirmation(update, context)
            return CONFIRM
        reply_keyboard = [['Orang Tua', 'Saudara']]
        await update.message.reply_text(
            "Apa hubungan anda dengan buah hati?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return RELATIONSHIP


async def relationship_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    relationship = update.message.text
    context.user_data['relationship'] = relationship
    if context.user_data.get('edit_mode'):
        context.user_data['edit_mode'] = False
        await show_confirmation(update, context)
        return CONFIRM
    await show_confirmation(update, context)
    return CONFIRM


async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    biodata = (f"--- Berikut Biodata Anda ---\n"
               f"Username Anda: {user_data['username']}\n"
               f"Hubungan: {user_data['relationship']}\n\n"
               "Apakah Anda ingin menyimpan biodata ini?")

    keyboard = [
        [InlineKeyboardButton("Setuju", callback_data='setuju')],
        [InlineKeyboardButton("Edit", callback_data='edit')],
        [InlineKeyboardButton("Batalkan", callback_data='batalkan')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(biodata, reply_markup=reply_markup)


async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'setuju':
        save_to_excel(context.user_data)
        await query.edit_message_text(text="Biodata Anda telah disimpan. Terima kasih! ")
        return ConversationHandler.END
    elif query.data == 'edit':
        keyboard = [
            [InlineKeyboardButton("Username Anda", callback_data='edit_username')],
            [InlineKeyboardButton("Hubungan", callback_data='edit_relationship')],
            [InlineKeyboardButton("Batal", callback_data='batal')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Bagian mana yang ingin Anda edit?", reply_markup=reply_markup)
        return EDIT
    elif query.data == 'batalkan':
        await query.edit_message_text(text="Pendaftaran Anda telah dibatalkan.")
        return ConversationHandler.END


async def edit_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['edit_mode'] = True  # Set edit mode

    if query.data == 'edit_username':
        await query.edit_message_text(text="Username Anda?")
        return USERNAME
    elif query.data == 'edit_relationship':
        reply_keyboard = [['Saudara', 'Orang Tua']]
        await query.message.reply_text(
            text="Apa hubungan anda dengan buah hati?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return RELATIONSHIP
    elif query.data == 'batal':
        await show_confirmation(query, context)  # Menampilkan kembali formulir konfirmasi
        return CONFIRM
    elif query.data == 'cancel':
        await query.edit_message_text(text="Pendaftaran Anda telah dibatalkan.")
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Pendaftaran dibatalkan.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Terhubung ke MQTT. Anda akan mulai menerima pesan dari topik.")


async def disconnect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Terputus dari MQTT. Anda tidak akan lagi menerima pesan dari topik.")


async def contactlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_list = (
        'Daftar Kontak Darurat:\n'
        '<a href="Call:+0812-8008-6700">081280086700</a> - Ambulance Kota Malang\n'
        '<a href="Call:+0851-6169-0119">085161690119</a> - Ambulance Kota Batu\n'
        '<a href="tel:+03413906868">(0341) 3906868</a> - Ambulance Kabupaten Malang\n'
    )
    await update.message.reply_text(contact_list, parse_mode='HTML')


async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    if not user_data:
        await update.message.reply_text("Anda belum terdaftar. Silakan daftar terlebih dahulu /subscribe.")
        return ConversationHandler.END

    biodata = (f"--- Detail Akun Anda ---\n"
               f"Username Anda: {user_data['username']}\n"
               f"Hubungan: {user_data['relationship']}\n\n"
               "Apakah Anda ingin mengedit detail akun Anda?")

    keyboard = [
        [InlineKeyboardButton("Username Anda", callback_data='edit_username')],
        [InlineKeyboardButton("Hubungan", callback_data='edit_relationship')],
        [InlineKeyboardButton("Kembali", callback_data='kembali')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(biodata, reply_markup=reply_markup)
    return ACCOUNT


async def account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['edit_mode'] = True

    if query.data == 'edit_username':
        await query.edit_message_text(text="Username Anda?")
        return USERNAME
    elif query.data == 'edit_relationship':
        reply_keyboard = [['Orang Tua', 'Saudara']]
        await query.message.reply_text(
            text="Apa hubungan anda?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return RELATIONSHIP
    elif query.data == 'kembali':
        await account_command(query, context)
        return ACCOUNT


async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    predictions = get_predict.make_predict()

    if not predictions:
        await update.message.reply_text('Tidak ada hasil prediksi yang tersedia saat ini.')
        return

    predictions_text = "".join(predictions)
    await update.message.reply_text(text=f"Hasil Prediksi:\n{predictions_text}")


def save_to_excel(user_data):
    df = pd.DataFrame([user_data])
    directory = "C:\\fall-detect"

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, 'registrations.xlsx')

    try:
        if os.path.exists(file_path):
            with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                if 'Sheet1' in writer.book.sheetnames:
                    start_row = writer.sheets['Sheet1'].max_row
                    df.to_excel(writer, index=False, header=False, startrow=start_row)
                else:
                    df.to_excel(writer, index=False, header=True)
        else:
            df.to_excel(file_path, index=False)
        print(f'File saved to {file_path}')
    except Exception as e:
        print(f'Error saving file: {e}')


def run_bot_app():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe', subscribe_command)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username_received)],
            RELATIONSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, relationship_received)],
            CONFIRM: [CallbackQueryHandler(confirm_handler)],
            EDIT: [CallbackQueryHandler(edit_choice_handler)],
            CONNECT: [CallbackQueryHandler(connect_command)],
            ACCOUNT: [CallbackQueryHandler(account_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True
    )

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('predict', predict_command))
    app.add_handler(CommandHandler('connect', connect_command))
    app.add_handler(CommandHandler('disconnect', disconnect_command))
    app.add_handler(CommandHandler('contactlist', contactlist_command))
    app.add_handler(CommandHandler('account', account_command))
    app.add_handler(conv_handler)

    print('Bot is polling...')
    app.run_polling(poll_interval=5)


if __name__ == '__main__':
    run_bot_app()
