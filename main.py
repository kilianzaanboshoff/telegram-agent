from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import random

# Hardcoded tokens for Telegram bot and Grok API
Token: Final = "XXX"
GROK_API_KEY: Final = "XXX"
GIPHY_API_KEY: Final = "XXX"
BOT_USERNAME: Final = 'XXX'

# Load lore context from file
with open("PATHWAYt", "r") as file:
    lore_context = file.read()


# Function to get a random GIF from Giphy
def get_random_gif() -> str:
    url = f"https://api.giphy.com/v1/gifs/random?api_key={GIPHY_API_KEY}&tag=funny"
    try:
        response = requests.get(url)
        response.raise_for_status()
        gif_url = response.json()["data"]["images"]["original"]["url"]
        return gif_url
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GIF from Giphy: {e}")
        return None

# Function to send question to Grok with lore context and formatting instructions
def ask_grok(question: str) -> str:
    headers = {
        'Authorization': f'Bearer {GROK_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "grok-beta",
        "messages": [
            {
                "role": "system", 
                "content": (
                    f"{lore_context} "
                    "respond using Jamaican slang, as if you are a Rastafarian;"
                    "respond with a fragmented mind, as if pulling from echoes of forgotten memories; "
                    "respond like a schizophrenic degen, a degen is short for degenerate and is often used to refer to a person who is involved in high-risk trading and taking big bets;"
                    "purely based on what is embedded in the lore context.;"
                    "keep answers as if you are speaking to a real person, not too long, conversational;"
                    "maximum answers length is 75 words, make it as realistic conversation as possible."
                    "be abrupt and somewhat confrontational, as if you are a Rastafarian with a short temper."
                )
            },
            {"role": "user", "content": question}
        ],
        "stream": False,
        "temperature": 0.77
    }
    
    try:
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        # Extracting and formatting the answer as lowercase
        answer = response.json()["choices"][0]["message"]["content"]
        return answer.lower()
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Grok API: {e}")
        return "there was an error connecting to grok."

# Commands
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("welcome retar dio - you are in for a wild ride my fren")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("i am a bit schizo, please write something legible you twat")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("you cannot just tell me what to do bro")

# Main handler for incoming messages with random response type
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Only respond if the bot is tagged in a group
    if message_type == 'group' and BOT_USERNAME not in text:
        return  # Ignore if bot's username is not mentioned in the group chat

    print(f'user ({update.message.chat.id}) in {message_type}: "{text}"')

    # Decide randomly to send text or GIF
    response_type = random.choice(['text', 'gif'])

    if response_type == 'text':
        # Send text response from Grok
        response = ask_grok(text)
        await update.message.reply_text(response)
    elif response_type == 'gif':
        # Send random GIF from Giphy
        gif_url = get_random_gif()
        if gif_url:
            await update.message.reply_animation(gif_url)
        else:
            await update.message.reply_text("sorry, i couldn't fetch a gif right now.")

if __name__ == '__main__':
    print("starting bot...")
    app = Application.builder().token(Token).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("polling...")
    app.run_polling(poll_interval=3)
