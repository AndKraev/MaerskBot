import logging
import os

from cachetools import TTLCache
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from services import fetch_from_list
from shipment import Shipment, parse_response
from text import parse_request_text, report_text, text_for_shipment


def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text(
        "Hi! This is Maersk tracking bot.\n"
        "Please send a container or transport document number to "
        "track your shipment. You can send up to 10 shipments at "
        "a time."
    )


def echo_requests(update: Update, context: CallbackContext) -> None:
    """Turns on and off sending reports to admin with request and response details."""
    if context.args:
        if context.args[0].strip().lower() == "true":
            context.bot_data["echo_requests"] = True
            update.message.reply_text("Requests will be now mirrored.")

        elif context.args[0].strip().lower() == "false":
            context.bot_data["echo_requests"] = False
            update.message.reply_text("Requests will not be mirrored anymore.")


def track(update: Update, context: CallbackContext) -> None:
    """Handles shipments and send response to a user. If shipment is not cached,
    the data is fetched from maersk api. Also sends reports to admin if activated
    """
    cache = context.dispatcher.bot_data["cache"]
    shipment_numbers = parse_request_text(update.message.text.upper())
    request_list = [shipment for shipment in shipment_numbers if shipment not in cache]

    if request_list:
        for req, res in zip(request_list, fetch_from_list(request_list)):
            parsed_res = parse_response(res)
            if isinstance(parsed_res, Shipment):
                cache[req] = text_for_shipment(parsed_res)
            else:
                cache[req] = f"{req} - {parsed_res}"

    for number in shipment_numbers:
        reply = cache[number]
        update.message.reply_text(reply, parse_mode="HTML")

        # Mirror messages to admin with report
        if context.dispatcher.bot_data["echo_requests"]:
            if update.effective_chat.id != context.dispatcher.bot_data["admin_chat_id"]:
                context.bot.send_message(
                    chat_id=context.dispatcher.bot_data["admin_chat_id"],
                    text=report_text(number, reply, update.effective_chat.username),
                    parse_mode="HTML",
                )


def main(updater: Updater, cache: TTLCache, admin_id: int) -> None:
    """Main function that launches bot and registers handlers."""
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Set echo_requests to True
    dispatcher.bot_data["echo_requests"] = True
    dispatcher.bot_data["admin_chat_id"] = admin_id
    dispatcher.bot_data["cache"] = cache

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        CommandHandler("echo", echo_requests, filters=Filters.chat(admin_id))
    )
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), track))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    main(
        Updater(os.environ["MAERSK_BOT"]),
        TTLCache(maxsize=500, ttl=3600),
        admin_id=1525941072,
    )
