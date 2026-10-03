import telebot
bot_token = '6077494792:AAHHVmsK5vSHclA-XNRZoegj35mAvXMabHw'

bot = telebot.TeleBot(bot_token)

# Function to send a file to a Telegram chat
def send_file(file_path, chat_id):
    try:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id, file)
        print(f"File sent to chat {chat_id}")
    except Exception as e:
        print(f"Failed to send file to chat {chat_id}: {e}")

# Main function to prompt and send the file
def telegramBot(pdf_filename):
    group_1_chat_id = '-1002266381119'  # Distribution Internal Group
    group_2_chat_id = '-4042324815'     # Distribution Delivery Group

    send_to_group_1 = input("Send report to Distribution Internal Group? (y/n): ").strip().lower()
    if send_to_group_1 == 'y':
        send_file(pdf_filename, group_1_chat_id)

    send_to_group_2 = input("Send report to Distribution Delivery Group? (y/n): ").strip().lower()
    if send_to_group_2 == 'y':
        send_file(pdf_filename, group_2_chat_id)

# Example usage
# telegram_bot("your_report.pdf")
