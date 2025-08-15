#!/usr/bin/env python3
"""
Telegram Bot for Marketplace Sellers - Main Entry Point
O'zbekiston bozori sotuvchilari uchun Telegram bot
"""

import os
import logging
from flask import Flask, jsonify
from telebot import TeleBot
from telebot.types import BotCommand
from config import BOT_TOKEN
from bot_handlers import register_handlers
from database import init_database
from admin_panel import create_admin_panel

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app yaratish (Railway uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "MarketBot is running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot": "running"})

def main():
    """Bot dasturini ishga tushirish"""
    try:
        # Ma'lumotlar bazasini ishga tushirish
        init_database()
        logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi")
        
        # Bot obyektini yaratish
        bot = TeleBot(BOT_TOKEN)
        logger.info("Bot muvaffaqiyatli yaratildi")
        
        # Bot buyruqlarini o'rnatish
        commands = [
            BotCommand("start", "Botni ishga tushirish"),
            BotCommand("help", "Yordam"),
            BotCommand("api", "API kalitini boshqarish"),
            BotCommand("menu", "Asosiy menyu"),
            BotCommand("status", "API holati")
        ]
        bot.set_my_commands(commands)
        
        # Handlerlarni ro'yxatdan o'tkazish
        register_handlers(bot)
        logger.info("Barcha handlerlar ro'yxatdan o'tkazildi")
        
        # Admin panelni yaratish
        admin_panel = create_admin_panel(bot)
        logger.info("Admin panel muvaffaqiyatli yaratildi")
        
        # Botni ishga tushirish
        logger.info("Bot ishga tushmoqda...")
        
        # Railway da ishga tushirish uchun
        if os.getenv('RAILWAY_ENVIRONMENT'):
            # Railway da web server bilan ishga tushirish
            port = int(os.getenv('PORT', 8000))
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            # Lokal da bot polling bilan ishga tushirish
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
        raise

if __name__ == "__main__":
    main()

# Railway uchun Flask app ni export qilish
# Bu app Railway da ishlatiladi
