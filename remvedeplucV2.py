from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("TOKEN")  # safer than hardcoding

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📄 Send me a .txt file and I’ll remove duplicates for you.")

# Handle txt documents
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("❌ Please send a valid .txt file.")
        return

    # Download file
    original_name = doc.file_name
    base_name = os.path.splitext(original_name)[0]
    cleaned_name = f"{base_name}_cleaned.txt"

    file = await doc.get_file()
    await file.download_to_drive(original_name)

    # Read, deduplicate, and write
    with open(original_name, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned = list(dict.fromkeys(line.strip() for line in lines if line.strip()))

    with open(cleaned_name, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned))

    # Send back cleaned file
    with open(cleaned_name, "rb") as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            filename=cleaned_name
        )

    await update.message.reply_text(f"✅ Done! Duplicates removed. File: `{cleaned_name}`", parse_mode='Markdown')

    # Cleanup
    os.remove(original_name)
    os.remove(cleaned_name)

# Main
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("text/plain"), handle_document))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
