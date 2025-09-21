from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

TOKEN = "8113723791:AAHHldi8i5D6YTPwweojLE1gdqfCnXXVmoA"

def start(update, context):
    update.message.reply_text("📄 Send me a .txt file and I’ll remove duplicates for you.")

def handle_document(update, context):
    doc = update.message.document

    if not doc.file_name.endswith(".txt"):
        update.message.reply_text("❌ Please send a valid .txt file.")
        return

    # Download the file
    original_name = doc.file_name
    base_name = os.path.splitext(original_name)[0]
    cleaned_name = f"{base_name}.txt"

    file = doc.get_file()
    file.download(original_name)

    # Read, deduplicate, and write output
    with open(original_name, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned = list(dict.fromkeys(line.strip() for line in lines if line.strip()))

    with open(cleaned_name, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned))

    # Send back the cleaned file
    with open(cleaned_name, "rb") as f:
        context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename=cleaned_name)

    update.message.reply_text(f"✅ Done! Duplicates removed. File: `{cleaned_name}`", parse_mode='Markdown')

    # Cleanup temp files
    os.remove(original_name)
    os.remove(cleaned_name)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
