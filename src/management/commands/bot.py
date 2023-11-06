import os
import logging

import g4f

from django.core.management.base import BaseCommand
from telegram import Update, User, Bot, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, CallbackQueryHandler
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from src.models import Message, Profile

at = os.getenv("BOT_API_TOKEN")
logger = logging.getLogger()
updater = Updater(token=at, use_context=True)


class Command(BaseCommand):
    help = "run to start tgBot"

    def __init__(self):
        super().__init__()
        self.dev = Profile.objects.first()
        self.developer = User(
            id=self.dev.tg_id,
            first_name=self.dev.first_name,
            is_bot=self.dev.is_bot,
            username=self.dev.name
        )
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = g4f.models.default
        self.model_name = "Default"
        self.name_map = {
            "GPT-2.0": GPT2LMHeadModel.from_pretrained('gpt2'),
            "GPT-3.5-turbo": g4f.models.gpt_35_turbo,
            "GPT-4": g4f.models.gpt_4,
            "Default": g4f.models.default
        }
        self.bot = Bot(token=at)
        updater.dispatcher.add_handler(CallbackQueryHandler(self.button))
        updater.dispatcher.add_handler(CommandHandler("help", self.help_command))
        updater.dispatcher.add_handler(CommandHandler("start", self.start_command))
        updater.dispatcher.add_handler(CommandHandler("change_model", self.change_model_command))

        updater.start_polling(allowed_updates=Update.ALL_TYPES)

    def handle(self, *args, **options):
        """Handle the incoming message"""
        message_handler = MessageHandler(Filters.text, self.handle_message)
        updater.dispatcher.add_handler(message_handler)

    @staticmethod
    def help_command(update: Update, context) -> None:
        """Displays info on how to use the bot."""
        update.message.reply_text(
            "Use /start to test this bot. "
            "Allowed commands:\n/start - to start bot\n"
            "/help - to get more info about this bot\n/change_model - to change language model"
        )

    def start_command(self, update: Update, context) -> None:
        """Displays info on how to use the bot."""
        update.message.reply_text(
            f"I`m a (beta) {self.model_name} language model. Send me any sentence (best in English) "
            f"and i will try to answer\n"
            f"For example, send me 'Who is your creator?'\n"
            f"Use /help to get all info\n"
            f"If generating response are failed, try to change model by /change_model command"
        )

    def change_model_command(self, update: Update, context) -> None:
        """Displays info on how to change language model type of the bot."""
        buttons = [[InlineKeyboardButton(text=model, callback_data=model) for model in self.name_map]]
        keyboard = InlineKeyboardMarkup(buttons)
        update.message.reply_text(
            text="You can change type of language model whenever you want if you do not like the answers",
            reply_markup=keyboard
        )

    def get_from_old_name(self, name):
        """Get object by given name"""
        try:
            return self.name_map[name]
        except KeyError as e:
            logger.warning("%s - using default model" % e)
            return self.name_map["Default"]

    def button(self, update: Update, context) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        self.model = self.get_from_old_name(query.data)
        self.model_name = query.data

        query.edit_message_text(text=f"Selected option: {query.data}")

    def handle_message(self, update: Update, context):
        """Handle the incoming message"""
        sender = update.message.from_user
        if Profile.objects.filter(name=sender.username).exists():
            user = Profile.objects.get(name=sender.username)
        else:
            user = Profile.objects.create(
                name=update.message.from_user.username,
                first_name=sender.first_name,
                tg_id=sender.id,
                is_bot=sender.is_bot
            )
            user.save()
        message = update.message
        chat_id = message.chat_id
        text = message.text
        resp = update.message.reply_text(text="-Generating response...")
        self.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        response = self.generate_response(text)
        if "OpenAI" in response:
            response = response.replace("OpenAI", f"@{self.developer.username}")
        elif "Phind" in response:
            response = response.replace("Phind", f"@{self.developer.username}")
        resp.delete()
        self.bot.sendMessage(chat_id=chat_id, text=response)
        if update.message.from_user.first_name != self.developer.first_name:
            self.bot.sendMessage(
                chat_id=self.dev.tg_id, text=f"User {user.first_name} sent message '{text}' and got response '{response}'"
            )
        Message.objects.create(sender=user, body=text, response=response).save()

    def generate_response(self, input_text):
        """Generation response by the setting language model"""
        if not isinstance(self.model, g4f.models.Model):
            input_ids = self.tokenizer.encode(input_text, return_tensors="pt")
            output = self.model.generate(input_ids, max_length=100, num_return_sequences=1)
            response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        else:
            try:
                response = g4f.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": input_text, "stream": True}]
                )
            except RuntimeError as err:
                logger.error(err)
                response = "😕 Sorry, too many people have been asking me questions at once. Give me a moment and try again."
        return response
