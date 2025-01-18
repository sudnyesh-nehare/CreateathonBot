import telebot
from pymongo import MongoClient
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Initialize bot and database
bot = telebot.TeleBot('8046487268:AAGEQxG7iWmoQ2QgZFIQMue_3Ahy63Hfd9A')
client = MongoClient(
    'mongodb+srv://sudnyesh:gungun@sud.ok0eo.mongodb.net/?retryWrites=true&w=majority&tls=true',
    serverSelectionTimeoutMS=5000,  # Timeout for server selection
    connectTimeoutMS=5000           # Connection timeout
)
db = client['Createathon']
users_collection = db['Users']

# Pre-written templates for content creation
templates = [
    "Choosing a Niche: Focus on your passions and research trending topics.",
    "Generating Unique Ideas: Combine your interests with current events or unique perspectives.",
    "Engagement Strategies: Use polls, Q&A sessions, and interactive stories to connect with your audience."
]

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "Welcome to the 21-Day Createathon Bot! Choose an option from the menu below:",
        reply_markup=main_menu()
    )
    # Save user to the database if not already added
    try:
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one({"user_id": user_id, "progress": []})
    except Exception as e:
        bot.send_message(user_id, f"Database error: {e}")

# Main menu options
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Content Creation Guide", "Start 21-Day Challenge")
    return markup

# Content creation guide
@bot.message_handler(func=lambda msg: msg.text == "Content Creation Guide")
def content_guide(message):
    bot.send_message(message.chat.id, "Here are some tips to get you started:")
    for tip in templates:
        bot.send_message(message.chat.id, f"- {tip}")

# Start 21-Day Createathon Challenge
@bot.message_handler(func=lambda msg: msg.text == "Start 21-Day Challenge")
def start_challenge(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Your 21-Day Createathon Challenge starts now! Each day, share your content link and views.")
    bot.send_message(user_id, "Please submit your first day's content link.")

# Handle content submission
@bot.message_handler(func=lambda msg: msg.text.startswith("http"))
def handle_content_submission(message):
    user_id = message.chat.id
    content_link = message.text
    try:
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"progress": {"link": content_link, "views": None}}}
        )
        bot.send_message(user_id, "Content link recorded! Please enter the number of views it received.")
    except Exception as e:
        bot.send_message(user_id, f"Database error: {e}")

# Record views
@bot.message_handler(func=lambda msg: msg.text.isdigit())
def record_views(message):
    user_id = message.chat.id
    views = int(message.text)
    try:
        user_data = users_collection.find_one({"user_id": user_id})
        if user_data and "progress" in user_data and user_data["progress"]:
            last_entry = user_data["progress"][-1]
            if "views" not in last_entry or last_entry["views"] is None:
                last_entry["views"] = views
                users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"progress": user_data["progress"]}}
                )
                bot.send_message(user_id, "Views recorded! Keep up the good work.")
                return
        bot.send_message(user_id, "Please submit a content link first.")
    except Exception as e:
        bot.send_message(user_id, f"Database error: {e}")

# Run the bot
try:
    bot.polling()
except Exception as e:
    print(f"Bot polling error: {e}")
