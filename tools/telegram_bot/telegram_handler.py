import logging
import os
from pathlib import Path
from typing import Iterator, Iterable

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from telegram.message import Message
from telegram.message import MessageEntity

from llm_tools.translator import Translator
from telegram_bot.telegram_message import TelegramMessage
from utils import init_logger

init_logger()


logger = logging.getLogger("telegram_bot")


def translate(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler
    for messages coming from the Bot API
    """

    # Print to console
    logger.info(f"{update.message.from_user.first_name} wrote {update.message.text}")

    message: Message = context.bot.send_message(
        chat_id=update.message.chat_id,
        text="wait a minute",
        # To preserve the markdown, we attach entities (bold, italic...)
        entities=update.message.entities,
        parse_mode="html",
    )

    try:
        _answer_to_tg(context=context, message=message, update=update)
    except Exception as e:
        logger.error(f"Got an error: {e.__class__.__name__.capitalize()}({str(e)})")
        context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=message.message_id,
            text="Something went wrong",
            entities=[],
        )


def _answer_to_tg(context: CallbackContext,
                  message: Message,
                  update: Update):
    api_key = os.getenv("OPENAI_API_KEY")
    translator = Translator(api_key=api_key)
    text = ""
    answer = translator.translate_stream(update.message.text)
    answer_for_telegram = _stream2telegram(answer)
    entities = []
    for item in answer_for_telegram:
        if item.text.strip() == "":
            continue
        text += "\n"
        entity = MessageEntity(
            type=item.entity_type, offset=len(text), length=len(item.text)
        )
        text += item.text
        if item.entity_type:
            entities.append(entity)
        message = context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=message.message_id,
            text=text,
            entities=entities,
        )


def menu(update: Update, context: CallbackContext) -> None:
    """
    This handler sends a menu with the inline buttons we pre-assigned above
    """

    context.bot.send_message(
        update.message.from_user.id,
        (
            "Это бот-словарь сербского языка.\n"
            "This is a serbian-russian dictionary\n"
            "Ово je српско-руски речник\n\n"
            "Send me a word, I'll translate it\n"
        ),
    )


def _to_markdown(text: str, hide: bool = False) -> TelegramMessage:
    if hide:
        entity_type = "spoiler"
    elif text.strip().startswith("<h3>"):
        entity_type = "bold"
    elif "<i>" in text:
        entity_type = "italic"
    elif "<details>" in text:
        entity_type = "spoiler"
    else:
        entity_type = None

    text = text.replace("<h3>", "").replace("</h3>", "")
    text = text.replace("<p>", "").replace("</p>", "")
    text = text.replace("<b>", "").replace("</b>", "")
    text = text.replace("<i>", "").replace("</i>", "")
    text = text.replace("<br>", "\n").replace("</br>", "\n")
    text = text.replace("<details>", "").replace("</details>", "")
    text = text.replace("normal_form:", "")
    text = text.replace("translation:", "")
    text = text.replace("synonyms:", "Синонимы:")
    text = text.replace(" explanation:", "Объяснение:")
    text += "\n"
    return TelegramMessage(text=text, entity_type=entity_type)


def _stream2telegram(answer: Iterable[str]) -> Iterator[TelegramMessage]:
    accum = ""
    hide = False
    for item in answer:
        for letter in item:
            if letter != "\n":
                accum += letter
            else:
                yield _to_markdown(accum, hide=hide)
                hide = False
                if "<p> Перевод: </p>" in accum or "<p> Perevod: </p>" in accum:
                    hide = True
                accum = ""
    if accum.strip():
        yield _to_markdown(accum, hide=hide)


def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token=token)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("translate", translate))
    dispatcher.add_handler(CommandHandler("menu", menu))

    # Echo any message that is not a command
    dispatcher.add_handler(MessageHandler(~Filters.command, translate))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == "__main__":
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent.parent / ".env"
    assert env_path.exists(), f"{env_path.as_posix()} does not exist"
    load_dotenv(dotenv_path=env_path)
    main()
