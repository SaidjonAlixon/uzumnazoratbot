"""
Telegram bot handlerlari
Barcha bot funksionalligini boshqarish
"""

import logging
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from database import save_user_api_key, get_user_api_key, delete_user_api_key, update_user_activity
from api_client import MarketplaceAPIClient
from keyboards import *
from utils import *
from config import MESSAGES

logger = logging.getLogger(__name__)

# Foydalanuvchilar holati
user_states = {}

# Bot obyektini global o'zgaruvchi sifatida saqlash
bot = None

def check_user_blocked(user_id: int) -> bool:
    """Foydalanuvchi bloklangan ekanligini tekshirish va maxsus xabar yuborish"""
    from database import is_user_blocked
    if is_user_blocked(user_id):
        # Bloklangan foydalanuvchilar uchun maxsus xabar va tugma
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        # Config dan admin username ni olish
        try:
            from config import ADMIN_CONFIG
            admin_username = ADMIN_CONFIG.get("admin_username", "Tolov_admini_btu")
        except:
            admin_username = "Tolov_admini_btu"
        
        blocked_keyboard = InlineKeyboardMarkup()
        blocked_keyboard.add(
            InlineKeyboardButton(
                "📞 Adminga murojaat qilish", 
                url=f"https://t.me/{admin_username}"
            )
        )
        
        bot.send_message(
            user_id,
            "❌ <b>Sizning botdan foydalanish huquqingiz cheklangan!</b>\n\n"
            "💳 <b>To'lovni amalga oshirish uchun iltimos adminga murojaat qiling!</b>\n\n"
            "🔒 Siz admin tomonidan bloklangan. Savollaringiz yoki to'lov bo'yicha ma'lumot uchun "
            "admin bilan bog'laning.",
            parse_mode="HTML",
            reply_markup=blocked_keyboard
        )
        return True
    return False

def register_handlers(telegram_bot: TeleBot):
    global bot
    bot = telegram_bot
    """Barcha handlerlarni ro'yxatdan o'tkazish"""
    
    @bot.message_handler(commands=['start'])
    def handle_start(message: Message):
        """Start buyrug'ini bajarish"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            
            # Foydalanuvchi bloklangan ekanligini tekshirish
            if check_user_blocked(user_id):
                return
            
            # Foydalanuvchi faolligini yangilash
            update_user_activity(user_id)
            
            # Foydalanuvchi API kalitini tekshirish
            api_key = get_user_api_key(user_id)
            
            if api_key:
                # API ulanishini tekshirish
                api_client = MarketplaceAPIClient(api_key)
                if api_client.test_connection():
                    # Admin ekanligini tekshirish
                    from admin_panel import AdminPanel
                    admin_panel = AdminPanel(bot)
                    is_admin = admin_panel.is_admin(user_id)
                    
                    bot.send_message(
                        message.chat.id,
                        MESSAGES["welcome"] + "\n\n" + MESSAGES["api_status_connected"],
                        parse_mode="HTML",
                        reply_markup=get_main_menu_keyboard(is_admin=is_admin)
                    )
                else:
                    bot.send_message(
                        message.chat.id,
                        MESSAGES["api_invalid"],
                        parse_mode="HTML",
                        reply_markup=get_api_management_keyboard()
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    MESSAGES["welcome_no_api"],
                    parse_mode="HTML",
                    reply_markup=get_api_management_keyboard()
                )
        except Exception as e:
            logger.error(f"Start handlerida xatolik: {e}")
            bot.send_message(message.chat.id, MESSAGES["error"], parse_mode="HTML")
    
    @bot.message_handler(commands=['help'])
    def handle_help(message: Message):
        """Yordam buyrug'ini bajarish"""
        bot.send_message(
            message.chat.id,
            MESSAGES["help"],
            parse_mode="HTML"
        )
    
    @bot.message_handler(commands=['api'])
    def handle_api_command(message: Message):
        """API buyrug'ini bajarish"""
        bot.send_message(
            message.chat.id,
            MESSAGES["api_prompt"],
            parse_mode="HTML",
            reply_markup=get_api_management_keyboard()
        )
    
    @bot.message_handler(commands=['menu'])
    def handle_menu_command(message: Message):
        """Menyu buyrug'ini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        # Admin ekanligini tekshirish
        from admin_panel import AdminPanel
        admin_panel = AdminPanel(bot)
        is_admin = admin_panel.is_admin(user_id)
        
        if not api_key:
            bot.send_message(
                message.chat.id,
                MESSAGES["no_api"],
                parse_mode="HTML",
                reply_markup=get_api_management_keyboard()
            )
            return
        
        bot.send_message(
            message.chat.id,
            MESSAGES["main_menu"],
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(is_admin=is_admin)
        )
    
    @bot.message_handler(commands=['status'])
    def handle_status_command(message: Message):
        """API holati buyrug'ini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        if not api_key:
            bot.send_message(
                message.chat.id,
                MESSAGES["api_status_disconnected"],
                parse_mode="HTML"
            )
            return
        
        # API ulanishini tekshirish
        bot.send_message(message.chat.id, MESSAGES["api_testing"], parse_mode="HTML")
        
        api_client = MarketplaceAPIClient(api_key)
        if api_client.test_connection():
            bot.send_message(
                message.chat.id,
                MESSAGES["api_status_connected"],
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                message.chat.id,
                MESSAGES["api_status_disconnected"],
                parse_mode="HTML"
            )
    
    @bot.message_handler(func=lambda message: message.text == "📦 FBS Buyurtmalar")
    def handle_fbs_orders_button(message: Message):
        """FBS buyurtmalar tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        if not api_key:
            bot.send_message(message.chat.id, MESSAGES["no_api"], parse_mode="HTML")
            return
        
        bot.send_message(
            message.chat.id,
            "📦 <b>FBS Buyurtmalar bo'limi</b>\n\nKerakli amalni tanlang:",
            parse_mode="HTML",
            reply_markup=get_fbs_menu_keyboard()
        )
    
    @bot.message_handler(func=lambda message: message.text == "📊 FBS Statistika")
    def handle_fbs_statistics_button(message: Message):
        """FBS statistika tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        if not api_key:
            bot.send_message(message.chat.id, MESSAGES["no_api"], parse_mode="HTML")
            return
        
        bot.send_message(
            message.chat.id,
            "📊 <b>FBS Statistika bo'limi</b>\n\nKerakli ma'lumotni tanlang:",
            parse_mode="HTML",
            reply_markup=get_fbs_statistics_keyboard()
        )
    
    @bot.message_handler(func=lambda message: message.text == "💰 Moliyaviy hisobot")
    def handle_finance_button(message: Message):
        """Moliyaviy hisobot tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        if not api_key:
            bot.send_message(message.chat.id, MESSAGES["no_api"], parse_mode="HTML")
            return
        
        bot.send_message(
            message.chat.id,
            "💰 <b>Moliyaviy hisobot bo'limi</b>\n\nKerakli ma'lumotni tanlang:",
            parse_mode="HTML",
            reply_markup=get_finance_menu_keyboard()
        )
    
    @bot.message_handler(func=lambda message: message.text == "🔐 Admin Panel")
    def handle_admin_panel_button(message: Message):
        """Admin panel tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
        
        # Admin ekanligini tekshirish
        from admin_panel import AdminPanel
        admin_panel = AdminPanel(bot)
        
        if not admin_panel.is_admin(user_id):
            bot.send_message(
                message.chat.id,
                "❌ Sizda admin huquqi yo'q!",
                parse_mode="HTML"
            )
            return
        
        # Admin panel ochish
        admin_text = "🔐 <b>Admin Panel</b>\n\nKerakli amalni tanlang:"
        
        bot.send_message(
            message.chat.id,
            admin_text,
            parse_mode="HTML",
            reply_markup=admin_panel.get_admin_keyboard()
        )
    
    # Admin callback handlerlari
    @bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
    def admin_callback_handler(call: CallbackQuery):
        """Admin callback handlerlari"""
        try:
            user_id = call.from_user.id
            
            # Admin ekanligini tekshirish
            from admin_panel import AdminPanel
            admin_panel = AdminPanel(bot)
            
            if not admin_panel.is_admin(user_id):
                bot.answer_callback_query(call.id, "❌ Sizda admin huquqi yo'q!")
                return
            
            data = call.data
            logger.info(f"Admin callback: {data} from user {user_id}")
            
            # Callback javobini darhol yuborish
            bot.answer_callback_query(call.id, f"✅ {data} bajarilmoqda...")
            
            if data == "admin_stats":
                admin_panel.handle_admin_stats(call)
            elif data == "admin_users":
                admin_panel.handle_admin_users(call)
            elif data == "admin_broadcast":
                admin_panel.handle_admin_broadcast(call)
            elif data == "admin_block":
                admin_panel.handle_admin_block(call)
            elif data == "admin_unblock":
                admin_panel.handle_admin_unblock(call)
            elif data == "admin_add_admin":
                admin_panel.handle_admin_add_admin(call)
            elif data == "admin_api_keys":
                admin_panel.handle_admin_api_keys(call)
            elif data == "admin_all_api_keys":
                admin_panel.handle_admin_all_api_keys(call)
            elif data == "admin_activity":
                admin_panel.handle_admin_activity(call)
            elif data == "admin_user_management":
                admin_panel.handle_admin_user_management(call)
            elif data == "admin_main_menu":
                admin_panel.handle_admin_main_menu(call)
            elif data == "admin_back":
                admin_panel.handle_admin_back(call)
            else:
                logger.warning(f"Noma'lum admin callback: {data}")
                bot.answer_callback_query(call.id, f"❌ Noma'lum buyruq: {data}")
                
        except Exception as e:
            logger.error(f"Admin callback handlerda xatolik: {e}")
            try:
                bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi!")
            except:
                pass
    
    # Admin bloklash va blokni olib tashlash xabarlarini qayta ishlash
    @bot.message_handler(func=lambda message: message.text and message.text.isdigit())
    def handle_admin_user_id_input(message: Message):
        """Admin foydalanuvchi ID ni qabul qilish"""
        try:
            user_id = message.from_user.id
            
            # Foydalanuvchi bloklangan ekanligini tekshirish
            if check_user_blocked(user_id):
                return
            
            # Admin ekanligini tekshirish
            from admin_panel import AdminPanel
            admin_panel = AdminPanel(bot)
            
            if not admin_panel.is_admin(user_id):
                return
            
            # Foydalanuvchi holatini tekshirish
            from telebot.handler_backends import State, StatesGroup
            current_state = bot.get_state(user_id, message.chat.id)
            
            if current_state == "waiting_for_block_user_id":
                # Foydalanuvchini bloklash
                target_user_id = int(message.text)
                if admin_panel.block_user(target_user_id):
                    # Bloklangan foydalanuvchiga xabar yuborish
                    try:
                        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
                        
                        blocked_keyboard = InlineKeyboardMarkup()
                        # Config dan admin username ni olish
                        try:
                            from config import ADMIN_CONFIG
                            admin_username = ADMIN_CONFIG.get("admin_username", "Tolov_admini_btu")
                        except:
                            admin_username = "Tolov_admini_btu"
                        
                        blocked_keyboard.add(
                            InlineKeyboardButton(
                                "📞 Adminga murojaat qilish", 
                                url=f"https://t.me/{admin_username}"
                            )
                        )
                        
                        bot.send_message(
                            target_user_id,
                            "❌ <b>Sizning botdan foydalanish huquqingiz cheklangan!</b>\n\n"
                            "💳 <b>To'lovni amalga oshirish uchun iltimos adminga murojaat qiling!</b>\n\n"
                            "🔒 Siz admin tomonidan bloklangan. Savollaringiz yoki to'lov bo'yicha ma'lumot uchun "
                            "admin bilan bog'laning.",
                            parse_mode="HTML",
                            reply_markup=blocked_keyboard
                        )
                    except:
                        pass
                    
                    # Admin ga natija xabarini yuborish
                    bot.reply_to(
                        message,
                        f"✅ <b>Foydalanuvchi bloklandi!</b>\n\n"
                        f"🆔 ID: {target_user_id}\n"
                        f"🔒 Holat: Bloklangan\n"
                        f"📝 Izoh: Foydalanuvchi botdan foydalanishi cheklangan",
                        parse_mode="HTML"
                    )
                    
                    # Holatni tozalash
                    bot.delete_state(user_id, message.chat.id)
                else:
                    bot.reply_to(message, "❌ Foydalanuvchini bloklashda xatolik yuz berdi!")
                    
            elif current_state == "waiting_for_unblock_user_id":
                # Foydalanuvchining blokini olib tashlash
                target_user_id = int(message.text)
                if admin_panel.unblock_user(target_user_id):
                    # Blokdan chiqarilgan foydalanuvchiga xabar yuborish
                    try:
                        bot.send_message(
                            target_user_id,
                            "✅ <b>Sizning botdan foydalanish huquqingiz tiklandi!</b>\n\n"
                            "🎉 Tabriklaymiz! Admin tomonidan blokdan chiqarildingiz.\n\n"
                            "🚀 Endi botning barcha funksiyalaridan foydalanishingiz mumkin!\n\n"
                            "💡 Botni qayta ishga tushirish uchun /start buyrug'ini bosing.",
                            parse_mode="HTML"
                        )
                    except:
                        pass
                    
                    # Admin ga natija xabarini yuborish
                    bot.reply_to(
                        message,
                        f"✅ <b>Foydalanuvchi blokdan chiqarildi!</b>\n\n"
                        f"🆔 ID: {target_user_id}\n"
                        f"🔓 Holat: Blokdan chiqarildi\n"
                        f"📝 Izoh: Foydalanuvchi endi botdan foydalana oladi",
                        parse_mode="HTML"
                    )
                    
                    # Holatni tozalash
                    bot.delete_state(user_id, message.chat.id)
                else:
                    bot.reply_to(message, "❌ Foydalanuvchining blokini olib tashlashda xatolik yuz berdi!")
                    
        except Exception as e:
            logger.error(f"Admin foydalanuvchi ID ni qayta ishlashda xatolik: {e}")
            bot.reply_to(message, "❌ Xatolik yuz berdi!")
    
    @bot.message_handler(func=lambda message: message.text == "💳 Hisob-fakturalar")
    def handle_invoices_button(message: Message):
        """Hisob-fakturalar tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        if not api_key:
            bot.send_message(message.chat.id, MESSAGES["no_api"], parse_mode="HTML")
            return
        
        bot.send_message(
            message.chat.id,
            "💳 <b>Hisob-fakturalar bo'limi</b>\n\nKerakli ma'lumotni tanlang:",
            parse_mode="HTML",
            reply_markup=get_invoice_menu_keyboard()
        )
    
    @bot.message_handler(func=lambda message: message.text == "🛍 Mahsulotlar")
    def handle_products_button(message: Message):
        """Mahsulotlar tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        if not api_key:
            bot.send_message(message.chat.id, MESSAGES["no_api"], parse_mode="HTML")
            return
        
        bot.send_message(
            message.chat.id,
            "🛍 <b>Mahsulotlar bo'limi</b>\n\nKerakli amalni tanlang:",
            parse_mode="HTML",
            reply_markup=get_product_menu_keyboard()
        )
    
    @bot.message_handler(func=lambda message: message.text == "🏪 Do'konlarim")
    def handle_shops_button(message: Message):
        """Do'konlarim tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        api_key = get_user_api_key(user_id)
        
        if not api_key:
            bot.send_message(message.chat.id, MESSAGES["no_api"], parse_mode="HTML")
            return
        
        bot.send_message(
            message.chat.id,
            "🏪 <b>Do'konlarim bo'limi</b>\n\nKerakli ma'lumotni tanlang:",
            parse_mode="HTML",
            reply_markup=get_shop_menu_keyboard()
        )
    
    @bot.message_handler(func=lambda message: message.text == "⚙️ Sozlamalar")
    def handle_settings_button(message: Message):
        """Sozlamalar tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        bot.send_message(
            message.chat.id,
            "⚙️ <b>Sozlamalar</b>\n\nKerakli amalni tanlang:",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )
    
    @bot.message_handler(func=lambda message: message.text == "📞 Yordam")
    def handle_help_button(message: Message):
        """Yordam tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        help_text = """📞 <b>Yordam va qo'llab-quvvatlash</b>

🔧 <b>Texnik yordam:</b>
- Bot ishlamasa, /start buyrug'ini bosing
- API kalit noto'g'ri bo'lsa, yangi kalit kiriting
- Ma'lumotlar yuklanmasa, internet aloqangizni tekshiring

📋 <b>Asosiy buyruqlar:</b>
/start - Botni qayta ishga tushirish
/menu - Asosiy menyuni ko'rsatish
/api - API kalitini boshqarish
/status - API holatini tekshirish
/help - Bu yordam

💡 <b>Maslahatlar:</b>
- API kalitingizni hech kimga bermang
- Muntazam ravishda API holatini tekshiring
- Barcha amallar o'zbek tilida amalga oshiriladi

👥 <b>Qo'llab-quvvatlash:</b>
Savollaringiz bo'lsa, "👥 Qo'llab quvvatlash guruhi" tugmasini bosing!"""
        
        bot.send_message(
            message.chat.id,
            help_text,
            parse_mode="HTML"
        )
    
    @bot.message_handler(func=lambda message: message.text == "👥 Qo'llab quvvatlash guruhi")
    def handle_support_group_button(message: Message):
        """Qo'llab-quvvatlash guruhi tugmasini bajarish"""
        user_id = message.from_user.id
        
        # Foydalanuvchi bloklangan ekanligini tekshirish
        if check_user_blocked(user_id):
            return
            
        support_text = (
            "👥 <b>Qo'llab quvvatlash guruhi</b>\n\n"
            "Texnik yordam va savol-javoblar uchun qo'llab-quvvatlash guruhimizga qo'shiling:\n\n"
            "💡 <b>Guruhda siz:</b>\n"
            "• Bot ishlatish bo'yicha savollaringizni bera olasiz\n"
            "• Texnik muammolarni hal qilishingiz mumkin\n"
            "• Boshqa foydalanuvchilar bilan tajriba almashishingiz mumkin\n"
            "• Yangi funksiyalar haqida ma'lumot olishingiz mumkin\n\n"
            "🚀 <b>Guruhga qo'shilish uchun tugmani bosing:</b>"
        )
        
        # Inline klaviatura bilan guruhga o'tish tugmasi
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("Guruhga o'tish", url="https://t.me/unb_uz")
        )
        
        bot.send_message(
            message.chat.id,
            support_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    
    @bot.message_handler(func=lambda message: message.from_user and isinstance(user_states.get(message.from_user.id), dict) and user_states.get(message.from_user.id, {}).get("state") == "waiting_product_search")
    def handle_product_search_input(message: Message):
        """Mahsulot qidirish so'rovini qayta ishlash"""
        try:
            user_id = message.from_user.id
            
            # Foydalanuvchi bloklangan ekanligini tekshirish
            if check_user_blocked(user_id):
                return
                
            search_query = message.text.strip()
            user_state = user_states.get(user_id, {})
            shop_id = user_state.get("shop_id", 1)
            
            if not search_query:
                bot.send_message(
                    message.chat.id,
                    "❌ Qidirish so'rovi bo'sh bo'lishi mumkin emas!",
                    parse_mode="HTML"
                )
                return
            
            # API kalitni olish
            api_key = get_user_api_key(user_id)
            if not api_key:
                bot.send_message(
                    message.chat.id,
                    MESSAGES["no_api"],
                    parse_mode="HTML"
                )
                return
            
            # Qidirish jarayonini boshlash
            bot.send_message(
                message.chat.id,
                f"🔍 <b>Qidiruv:</b> '{search_query}'\n\n⏳ Ma'lumotlar yuklanmoqda...",
                parse_mode="HTML"
            )
            
            # API orqali mahsulotlarni qidirish - OpenAPI spetsifikatsiyasiga asoslanib
            api_client = MarketplaceAPIClient(api_key)
            results = api_client.search_products(
                shop_id=shop_id, 
                search_query=search_query, 
                page=0, 
                size=10,
                sort_by="DEFAULT",
                order="ASC",
                filter_type="ALL"
            )
            
            if results and 'productList' in results and results['productList']:
                products = results['productList'][:5]  # Birinchi 5 ta natija
                text = f"🔍 <b>Qidiruv natijalari: '{search_query}'</b>\n\n"
                
                for i, product in enumerate(products, 1):
                    name = product.get('title', 'Noma\'lum mahsulot')
                    sku_title = product.get('skuTitle', 'N/A')
                    price = product.get('price', 0)
                    quantity_active = product.get('quantityActive', 0)
                    quantity_fbs = product.get('quantityFbs', 0)
                    
                    text += f"{i}. <b>{escape_html(name)}</b>\n"
                    text += f"   🏷 SKU: <code>{sku_title}</code>\n"
                    text += f"   💰 Narx: {format_currency(price)}\n"
                    text += f"   📊 Faol qoldiq: {quantity_active} dona\n"
                    text += f"   🚚 FBS qoldiq: {quantity_fbs} dona\n\n"
                
                # Umumiy natijalar soni
                total = results.get('totalProductsAmount', len(products))
                if total > len(products):
                    text += f"📈 Umumiy natijalar: {total} ta mahsulot topildi"
            else:
                text = f"🔍 <b>Qidiruv: '{search_query}'</b>\n\n"
                text += "📭 Hech qanday mahsulot topilmadi.\n\n"
                text += "💡 Maslahat:\n"
                text += "• Mahsulot nomini to'liq yozing\n"
                text += "• SKU raqamini tekshiring\n"
                text += "• Imlo xatolarini to'g'rilang"
            
            bot.send_message(
                message.chat.id,
                text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
            
            # User state ni tozalash
            user_states[user_id] = None
            
        except Exception as e:
            logger.error(f"Mahsulot qidirishda xatolik: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Qidiruvda xatolik yuz berdi. Qaytadan urinib ko'ring.",
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
            user_states[user_id] = None
    
    @bot.message_handler(func=lambda message: message.from_user and isinstance(user_states.get(message.from_user.id), dict) and user_states.get(message.from_user.id, {}).get("state") == "waiting_price_update")
    def handle_price_update_input(message: Message):
        """Narx yangilash so'rovini qayta ishlash"""
        try:
            user_id = message.from_user.id
            
            # Foydalanuvchi bloklangan ekanligini tekshirish
            if check_user_blocked(user_id):
                return
                
            price_input = message.text.strip()
            user_state = user_states.get(user_id, {})
            shop_id = user_state.get("shop_id", 1)
            
            # Format tekshirish: SKU:PRICE
            if ':' not in price_input:
                bot.send_message(
                    message.chat.id,
                    "❌ Noto'g'ri format!\n\nTo'g'ri format: <code>SKU:NARX</code>\nMisol: <code>ABC123:150000</code>",
                    parse_mode="HTML"
                )
                return
            
            try:
                sku, price_str = price_input.split(':', 1)
                sku = sku.strip()
                price = float(price_str.strip())
                
                if not sku or price <= 0:
                    raise ValueError("Invalid SKU or price")
                    
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "❌ Noto'g'ri format!\n\nSKU va narx to'g'ri kiritilganini tekshiring.\nMisol: <code>ABC123:150000</code>",
                    parse_mode="HTML"
                )
                return
            
            # API kalitni olish
            api_key = get_user_api_key(user_id)
            if not api_key:
                bot.send_message(
                    message.chat.id,
                    MESSAGES["no_api"],
                    parse_mode="HTML"
                )
                return
            
            # Narx yangilash jarayonini boshlash
            bot.send_message(
                message.chat.id,
                f"💰 <b>Narx yangilanmoqda...</b>\n\n🏷 SKU: <code>{sku}</code>\n💵 Yangi narx: {format_currency(price)}",
                parse_mode="HTML"
            )
            
            # API orqali narx yangilash - OpenAPI spetsifikatsiyasiga asoslanib
            api_client = MarketplaceAPIClient(api_key)
            
            # Avval mahsulotni topamiz
            product_results = api_client.search_products(
                shop_id=shop_id,
                search_query=sku,
                page=0,
                size=1,
                filter_type="WITH_SKU"
            )
            
            if product_results and 'productList' in product_results and product_results['productList']:
                product = product_results['productList'][0]
                product_id = product.get('productId')
                
                if product_id:
                    # Yangi OpenAPI formatida narx yangilash
                    price_data = {
                        "skuList": [
                            {
                                "skuId": product.get('skuList', [{}])[0].get('skuId') if product.get('skuList') else None,
                                "fullPrice": int(price),
                                "sellPrice": int(price),
                                "skuTitle": sku
                            }
                        ]
                    }
                    
                    success = api_client.update_product_price(shop_id, price_data)
                else:
                    success = False
            else:
                success = False
            
            if success:
                text = f"✅ <b>Narx muvaffaqiyatli yangilandi!</b>\n\n"
                text += f"🏷 SKU: <code>{sku}</code>\n"
                text += f"💰 Yangi narx: {format_currency(price)}\n"
                text += f"🏪 Do'kon ID: {shop_id}"
            else:
                text = f"❌ <b>Narx yangilashda xatolik!</b>\n\n"
                text += f"🏷 SKU: <code>{sku}</code>\n"
                text += f"💡 Tekshiring:\n"
                text += f"• SKU to'g'ri kiritilganmi\n"
                text += f"• Mahsulot mavjudmi\n"
                text += f"• Narx munosib miqdordami"
            
            bot.send_message(
                message.chat.id,
                text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
            
            # User state ni tozalash
            user_states[user_id] = None
            
        except Exception as e:
            logger.error(f"Narx yangilashda xatolik: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Narx yangilashda xatolik yuz berdi. Qaytadan urinib ko'ring.",
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
            user_states[user_id] = None
    
    @bot.message_handler(func=lambda message: message.from_user and user_states.get(message.from_user.id) == "waiting_api_key")
    def handle_api_key_input(message: Message):
        """API kalit kiritishni qayta ishlash"""
        try:
            user_id = message.from_user.id
            
            # Foydalanuvchi bloklangan ekanligini tekshirish
            if check_user_blocked(user_id):
                return
                
            api_key = message.text.strip()
            
            if not api_key or len(api_key.strip()) < 10:
                bot.send_message(
                    message.chat.id,
                    "❌ <b>Noto'g'ri API kalit formati!</b>\n\nIltimos, to'g'ri API kalitni kiriting.",
                    parse_mode="HTML"
                )
                return
            
            # API kalitni tekshirish
            bot.send_message(message.chat.id, MESSAGES["api_testing"], parse_mode="HTML")
            
            api_client = MarketplaceAPIClient(api_key)
            if api_client.test_connection():
                # API kalitni saqlash
                if save_user_api_key(
                    user_id, api_key, 
                    message.from_user.username,
                    message.from_user.first_name,
                    message.from_user.last_name
                ):
                    user_states[user_id] = None
                    bot.send_message(
                        message.chat.id,
                        MESSAGES["api_saved"],
                        parse_mode="HTML",
                        reply_markup=get_main_menu_keyboard()
                    )
                else:
                    bot.send_message(
                        message.chat.id,
                        "❌ <b>API kalitni saqlashda xatolik!</b>\n\nQaytadan urinib ko'ring.",
                        parse_mode="HTML"
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    MESSAGES["api_invalid"],
                    parse_mode="HTML"
                )
                
        except Exception as e:
            logger.error(f"API kalit kiritishda xatolik: {e}")
            bot.send_message(message.chat.id, MESSAGES["error"], parse_mode="HTML")
    
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call: CallbackQuery):
        """Callback querylarni qayta ishlash"""
        try:
            user_id = call.from_user.id
            
            # Foydalanuvchi bloklangan ekanligini tekshirish
            if check_user_blocked(user_id):
                return
                
            data = call.data
            
            # API kalitini olish
            api_key = get_user_api_key(user_id)
            
            if data == "main_menu":
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(
                    call.message.chat.id,
                    MESSAGES["main_menu"],
                    parse_mode="HTML",
                    reply_markup=get_main_menu_keyboard()
                )
            
            elif data == "add_api":
                user_states[user_id] = "waiting_api_key"
                bot.edit_message_text(
                    MESSAGES["api_prompt"],
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML"
                )
            
            elif data == "change_api":
                user_states[user_id] = "waiting_api_key"
                bot.edit_message_text(
                    "🔄 <b>Yangi API kalitni kiriting:</b>",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML"
                )
            
            elif data == "delete_api":
                bot.edit_message_text(
                    "🗑 <b>API kalitni o'chirishni xohlaysizmi?</b>\n\n<i>Bu amalni qaytarib bo'lmaydi!</i>",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=get_confirmation_keyboard("delete_api")
                )
            
            elif data == "confirm_delete_api":
                if delete_user_api_key(user_id):
                    bot.edit_message_text(
                        MESSAGES["api_deleted"],
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="HTML",
                        reply_markup=get_api_management_keyboard()
                    )
                else:
                    bot.edit_message_text(
                        "❌ <b>API kalitni o'chirishda xatolik!</b>",
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="HTML"
                    )
            
            elif data == "check_api_status":
                if not api_key:
                    bot.edit_message_text(
                        MESSAGES["api_status_disconnected"],
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="HTML",
                        reply_markup=get_api_management_keyboard()
                    )
                    return
                
                api_client = MarketplaceAPIClient(api_key)
                if api_client.test_connection():
                    bot.edit_message_text(
                        MESSAGES["api_status_connected"],
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="HTML",
                        reply_markup=get_back_to_main_keyboard()
                    )
                else:
                    bot.edit_message_text(
                        MESSAGES["api_status_disconnected"],
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="HTML",
                        reply_markup=get_settings_keyboard()
                    )
            
            # FBS handlerlari
            elif data == "fbs_orders":
                if api_key:
                    handle_fbs_orders_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_orders_count":
                if api_key:
                    handle_fbs_orders_count_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_stocks":
                if api_key:
                    handle_fbs_stocks_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_return_reasons":
                if api_key:
                    handle_fbs_return_reasons_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_update_stocks":
                if api_key:
                    handle_fbs_update_stocks_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_order_details":
                if api_key:
                    handle_fbs_order_details_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_shop_statistics":
                if api_key:
                    handle_fbs_shop_statistics_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_date_statistics":
                if api_key:
                    handle_fbs_date_statistics_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_status_statistics":
                if api_key:
                    handle_fbs_status_statistics_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_stock_statistics":
                if api_key:
                    handle_fbs_stock_statistics_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_finance_statistics":
                if api_key:
                    handle_fbs_finance_statistics_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_missing_items":
                if api_key:
                    handle_fbs_missing_items_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "fbs_missing_statistics":
                if api_key:
                    handle_fbs_missing_statistics_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            # Finance handlerlari
            elif data == "finance_expenses":
                if api_key:
                    handle_finance_expenses_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "finance_orders":
                if api_key:
                    handle_finance_orders_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "finance_payment_info":
                if api_key:
                    handle_finance_payment_info_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "finance_commission":
                if api_key:
                    handle_finance_commission_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            # Invoice handlerlari
            elif data == "invoices":
                if api_key:
                    handle_invoices_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "invoice_returns":
                if api_key:
                    handle_invoice_returns_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "invoice_products":
                if api_key:
                    handle_invoice_products_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "shop_invoices":
                if api_key:
                    handle_shop_invoices_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            # Product handlerlari
            elif data == "product_search":
                if api_key:
                    handle_product_search_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "product_update_price":
                if api_key:
                    handle_product_price_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            # Shop handlerlari
            elif data == "shops_list":
                if api_key:
                    handle_shops_list_callback(call, api_key)
                else:
                    bot.edit_message_text(MESSAGES["no_api"], call.message.chat.id, call.message.message_id, parse_mode="HTML")
            
            elif data == "cancel_action":
                bot.edit_message_text(
                    "❌ <b>Amal bekor qilindi</b>",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=get_back_to_main_keyboard()
                )
            
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Callback queryni qayta ishlashda xatolik: {e}")
            bot.answer_callback_query(call.id, "Xatolik yuz berdi!")

def handle_fbs_orders_callback(call: CallbackQuery, api_key: str):
    """FBS buyurtmalarni ko'rsatish - OpenAPI spetsifikatsiyasiga asoslanib"""
    if not api_key:
        bot.edit_message_text(
            MESSAGES["no_api"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        
        # Avval do'konlar ro'yxatini olamiz
        shops = api_client.get_shops()
        shop_ids = []
        if shops and isinstance(shops, list):
            shop_ids = [shop.get('id') for shop in shops if shop.get('id')]
        
        # Yangi OpenAPI spetsifikatsiyasiga asoslanib FBS buyurtmalarni olamiz
        orders = api_client.get_fbs_orders_v2(
            page=0, 
            size=10, 
            status="CREATED",
            shop_ids=shop_ids if shop_ids else None
        )
        
        if orders and orders.get('payload', {}).get('orders'):
            orders_list = orders['payload']['orders'][:10]  # Faqat birinchi 10 ta
            text = format_list_message(orders_list, format_order_info_v2, "FBS Buyurtmalar (Yangi)")
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"FBS buyurtmalarni olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_orders_count_callback(call: CallbackQuery, api_key: str):
    """FBS buyurtmalar sonini ko'rsatish - OpenAPI spetsifikatsiyasiga asoslanib"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        
        # Avval do'konlar ro'yxatini olamiz
        shops = api_client.get_shops()
        shop_ids = []
        if shops and isinstance(shops, list):
            shop_ids = [shop.get('id') for shop in shops if shop.get('id')]
        
        # Yangi OpenAPI spetsifikatsiyasiga asoslanib buyurtmalar sonini olamiz
        count_data = api_client.get_fbs_orders_count(
            shop_ids=shop_ids if shop_ids else None,
            status="CREATED"
        )
        
        if count_data and count_data.get('payload'):
            count = count_data['payload']
            text = "📊 <b>FBS Buyurtmalar statistikasi</b>\n\n"
            text += f"📦 Yaratilgan buyurtmalar: {count} ta\n"
            text += f"🏪 Do'konlar soni: {len(shop_ids) if shop_ids else 0} ta\n"
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"FBS buyurtmalar sonini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_stocks_callback(call: CallbackQuery, api_key: str):
    """FBS qoldiqlarni ko'rsatish"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        stocks = api_client.get_fbs_stocks()
        
        if stocks:
            text = format_list_message(stocks[:10], format_product_info, "FBS Qoldiqlar")
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"FBS qoldiqlarni olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_return_reasons_callback(call: CallbackQuery, api_key: str):
    """FBS qaytarish sabablarini ko'rsatish"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        reasons = api_client.get_fbs_return_reasons()
        
        if reasons:
            text = "🔄 <b>Qaytarish sabablari</b>\n\n"
            for i, reason in enumerate(reasons, 1):
                unknown_reason = "Noma'lum sabab"
                text += f"{i}. {reason.get('name', unknown_reason)}\n"
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Qaytarish sabablarini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_finance_expenses_callback(call: CallbackQuery, api_key: str):
    """Moliyaviy xarajatlarni ko'rsatish - OpenAPI spetsifikatsiyasiga asoslanib"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        
        # Avval do'konlar ro'yxatini olamiz
        shops = api_client.get_shops()
        shop_ids = []
        if shops and isinstance(shops, list):
            shop_ids = [shop.get('id') for shop in shops if shop.get('id')]
        
        # Yangi OpenAPI spetsifikatsiyasiga asoslanib xarajatlarni olamiz
        expenses = api_client.get_finance_expenses(
            page=0,
            size=10,
            shop_ids=shop_ids if shop_ids else None
        )
        
        if expenses and expenses.get('payload', {}).get('payments'):
            payments = expenses['payload']['payments'][:10]
            text = format_finance_expenses_v2(payments)
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Moliyaviy xarajatlarni olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_finance_orders_callback(call: CallbackQuery, api_key: str):
    """Moliyaviy buyurtmalarni ko'rsatish - OpenAPI spetsifikatsiyasiga asoslanib"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        
        # Avval do'konlar ro'yxatini olamiz
        shops = api_client.get_shops()
        shop_ids = []
        if shops and isinstance(shops, list):
            shop_ids = [shop.get('id') for shop in shops if shop.get('id')]
        
        # Yangi OpenAPI spetsifikatsiyasiga asoslanib moliyaviy buyurtmalarni olamiz
        orders = api_client.get_finance_orders(
            page=0,
            size=10,
            group=False,
            shop_ids=shop_ids if shop_ids else None
        )
        
        if orders and orders.get('payload', {}).get('orderItems'):
            order_items = orders['payload']['orderItems'][:10]
            text = format_finance_orders_v2(order_items)
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Moliyaviy buyurtmalarni olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_invoices_callback(call: CallbackQuery, api_key: str):
    """Hisob-fakturalarni ko'rsatish - OpenAPI spetsifikatsiyasiga asoslanib"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        
        # Yangi OpenAPI spetsifikatsiyasiga asoslanib hisob-fakturalarni olamiz
        invoices = api_client.get_invoices(size=10, page=0)
        
        if invoices:
            text = "💳 <b>Hisob-fakturalar</b>\n\n"
            for i, invoice in enumerate(invoices[:10], 1):
                invoice_id = invoice.get('id', 'N/A')
                invoice_number = invoice.get('invoiceNumber', 'N/A')
                full_price = invoice.get('fullPrice', 0)
                date_created = invoice.get('dateCreated', '')
                shop_title = invoice.get('shopTitle', 'Noma\'lum do\'kon')
                
                text += f"{i}. <b>Faktura #{invoice_number}</b>\n"
                text += f"   🆔 ID: {invoice_id}\n"
                text += f"   🏪 Do'kon: {escape_html(shop_title)}\n"
                text += f"   💰 Summa: {format_currency(full_price)}\n"
                text += f"   📅 Sana: {format_date(date_created)}\n\n"
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Hisob-fakturalarni olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_invoice_returns_callback(call: CallbackQuery, api_key: str):
    """Hisob-faktura qaytarishlarini ko'rsatish - OpenAPI spetsifikatsiyasiga asoslanib"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        
        # Yangi OpenAPI spetsifikatsiyasiga asoslanib qaytarishlarni olamiz
        returns = api_client.get_invoice_returns(page=0, size=10)
        
        if returns:
            text = "↩️ <b>Hisob-faktura qaytarishlari</b>\n\n"
            for i, return_item in enumerate(returns[:10], 1):
                return_id = return_item.get('id', 'N/A')
                external_number = return_item.get('externalNumber', 'N/A')
                status = return_item.get('status', 'unknown')
                date_created = return_item.get('dateCreated', '')
                type_return = return_item.get('type', 'RETURN')
                
                text += f"{i}. <b>Qaytarish #{external_number}</b>\n"
                text += f"   🆔 ID: {return_id}\n"
                text += f"   📊 Holat: {format_return_status(status)}\n"
                text += f"   🏷 Turi: {format_return_type(type_return)}\n"
                text += f"   📅 Sana: {format_date(date_created)}\n\n"
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Hisob-faktura qaytarishlarini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_product_search_callback(call: CallbackQuery, api_key: str):
    """Mahsulot qidirishni boshlash"""
    try:
        # Avval do'konlar ro'yxatini olamiz
        api_client = MarketplaceAPIClient(api_key)
        shops = api_client.get_shops()
        
        if not shops:
            bot.edit_message_text(
                "❌ Do'konlar topilmadi yoki API xatoligi",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=get_back_to_main_keyboard()
            )
            return
        
        # Birinchi do'konni tanlaymiz yoki foydalanuvchiga tanlash imkonini beramiz
        if isinstance(shops, list) and len(shops) > 0:
            shop_id = shops[0].get('id', 1)  # Birinchi do'kon ID si
        else:
            shop_id = 1  # Default shop ID
        
        bot.edit_message_text(
            "🔍 <b>Mahsulot qidirish</b>\n\n" +
            "Mahsulot nomini yoki artikulini yozing:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
        # Keyingi xabar uchun user state ni saqlaymiz
        user_states[call.from_user.id] = {
            "state": "waiting_product_search",
            "shop_id": shop_id
        }
        
    except Exception as e:
        logger.error(f"Mahsulot qidirishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_product_price_callback(call: CallbackQuery, api_key: str):
    """Mahsulot narxini yangilash"""
    try:
        # Avval do'konlar ro'yxatini olamiz
        api_client = MarketplaceAPIClient(api_key)
        shops = api_client.get_shops()
        
        if not shops:
            bot.edit_message_text(
                "❌ Do'konlar topilmadi yoki API xatoligi",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=get_back_to_main_keyboard()
            )
            return
        
        # Birinchi do'konni tanlaymiz
        if isinstance(shops, list) and len(shops) > 0:
            shop_id = shops[0].get('id', 1)
        else:
            shop_id = 1
        
        bot.edit_message_text(
            "💰 <b>Narx yangilash</b>\n\n" +
            "Quyidagi formatda ma'lumot kiriting:\n" +
            "<code>SKU:YANGI_NARX</code>\n\n" +
            "Misol: <code>ABC123:150000</code>\n" +
            "(150,000 so'm uchun)",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
        # Keyingi xabar uchun user state ni saqlaymiz
        user_states[call.from_user.id] = {
            "state": "waiting_price_update",
            "shop_id": shop_id
        }
        
    except Exception as e:
        logger.error(f"Narx yangilashda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_shops_list_callback(call: CallbackQuery, api_key: str):
    """Do'konlar ro'yxatini ko'rsatish"""
    if not api_key:
        return
    
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        shops = api_client.get_shops()
        
        if shops:
            text = format_list_message(shops, format_shop_info, "Do'konlar")
        else:
            text = MESSAGES["no_data"]
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Do'konlar ro'yxatini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_update_stocks_callback(call: CallbackQuery, api_key: str):
    """FBS qoldiqlarni yangilash"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        stocks = api_client.get_fbs_sku_stocks_v2()
        
        if stocks and 'data' in stocks:
            text = "📋 <b>FBS Qoldiqlar (yangilanadi)</b>\n\n"
            data = stocks['data']
            if isinstance(data, list) and len(data) > 0:
                for i, stock in enumerate(data[:5], 1):
                    sku = stock.get('sku', 'N/A')
                    available = stock.get('availableAmount', 0)
                    reserved = stock.get('reservedAmount', 0)
                    
                    text += f"{i}. 🏷 SKU: <code>{sku}</code>\n"
                    text += f"   📦 Mavjud: {available}\n"
                    text += f"   🔒 Band: {reserved}\n\n"
                    
                text += "💡 Qoldiqlarni yangilash uchun API so'rov yuborilishi mumkin."
            else:
                text += "📭 Qoldiqlar topilmadi."
        else:
            text = "📋 <b>FBS Qoldiqlar</b>\n\n📭 Ma'lumotlar topilmadi."
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Qoldiqlarni yangilashda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_order_details_callback(call: CallbackQuery, api_key: str):
    """FBS buyurtma tafsilotlari"""
    try:
        bot.edit_message_text(
            "🆔 <b>Buyurtma tafsilotlari</b>\n\n" +
            "Bu funksiya hozircha ishlab chiqilmoqda.\n" +
            "Tez orada buyurtma ID orqali tafsilotli ma'lumot olish imkoniyati qo'shiladi!\n\n" +
            "💡 Kelgusida buyurtma ID kiriting va to'liq ma'lumot oling.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Buyurtma tafsilotlarini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_finance_payment_info_callback(call: CallbackQuery, api_key: str):
    """Moliyaviy to'lov ma'lumotlari"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        payment_info = api_client.get_finance_seller_payment_info()
        
        if payment_info and 'data' in payment_info:
            data = payment_info['data']
            text = "💳 <b>To'lov ma'lumotlari</b>\n\n"
            
            # Asosiy to'lov ma'lumotlari
            balance = data.get('balance', 0)
            pending = data.get('pendingAmount', 0)
            text += f"💰 Joriy balans: {format_currency(balance)}\n"
            text += f"⏳ Kutilayotgan: {format_currency(pending)}\n\n"
            
            # Bank ma'lumotlari (agar mavjud bo'lsa)
            if 'bankAccount' in data:
                bank_info = data['bankAccount']
                text += f"🏦 Bank: {bank_info.get('bankName', 'N/A')}\n"
                text += f"💳 Hisob: {bank_info.get('accountNumber', 'N/A')}\n"
        else:
            text = "💳 <b>To'lov ma'lumotlari</b>\n\n📭 Ma'lumotlar topilmadi."
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"To'lov ma'lumotlarini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_finance_commission_callback(call: CallbackQuery, api_key: str):
    """Moliyaviy komissiya ma'lumotlari"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        commission_info = api_client.get_finance_commission_info()
        
        if commission_info and 'data' in commission_info:
            data = commission_info['data']
            text = "💰 <b>Komissiya ma'lumotlari</b>\n\n"
            
            total_commission = data.get('totalCommission', 0)
            monthly_commission = data.get('monthlyCommission', 0)
            commission_rate = data.get('commissionRate', 0)
            
            text += f"📊 Umumiy komissiya: {format_currency(total_commission)}\n"
            text += f"📅 Oylik komissiya: {format_currency(monthly_commission)}\n"
            text += f"📈 Komissiya stavkasi: {commission_rate}%\n"
        else:
            text = "💰 <b>Komissiya ma'lumotlari</b>\n\n📭 Ma'lumotlar topilmadi."
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Komissiya ma'lumotlarini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_invoice_products_callback(call: CallbackQuery, api_key: str):
    """Hisob-faktura mahsulotlari"""
    try:
        bot.edit_message_text(
            "📋 <b>Hisob-faktura mahsulotlari</b>\n\n" +
            "Bu funksiya hozircha ishlab chiqilmoqda.\n" +
            "Tez orada faktura mahsulotlarini ko'rish imkoniyati qo'shiladi!\n\n" +
            "💡 Kelgusida faktura ID kiriting va mahsulotlar ro'yxatini oling.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Faktura mahsulotlarini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_shop_invoices_callback(call: CallbackQuery, api_key: str):
    """Do'kon fakturaları"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        # Avval do'konlar ro'yxatini olamiz
        api_client = MarketplaceAPIClient(api_key)
        shops = api_client.get_shops()
        
        if not shops:
            bot.edit_message_text(
                "❌ Do'konlar topilmadi yoki API xatoligi",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=get_back_to_main_keyboard()
            )
            return
        
        # Birinchi do'konning hisob-fakturalarini olamiz
        if isinstance(shops, list) and len(shops) > 0:
            shop_id = shops[0].get('id', 1)
            shop_name = shops[0].get('name', 'Do\'kon #1')
        else:
            shop_id = 1
            shop_name = "Do'kon #1"
        
        invoices = api_client.get_shop_invoice_by_id(shop_id, page=0, size=10)
        
        if invoices:
            text = f"📄 <b>{escape_html(shop_name)} hisob-fakturaları</b>\n\n"
            
            if isinstance(invoices, list) and len(invoices) > 0:
                for i, invoice in enumerate(invoices[:5], 1):
                    invoice_id = invoice.get('id', 'N/A')
                    invoice_date = invoice.get('date', 'N/A')
                    invoice_total = invoice.get('total', 0)
                    
                    text += f"{i}. 📋 ID: {invoice_id}\n"
                    text += f"   📅 Sana: {invoice_date}\n"
                    text += f"   💰 Summa: {format_currency(invoice_total)}\n\n"
            else:
                text += "📭 Hisob-fakturalar topilmadi."
        else:
            text = f"📄 <b>{escape_html(shop_name)} hisob-fakturaları</b>\n\n📭 Ma'lumotlar topilmadi."
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Do'kon fakturalarini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

# Yangi FBS statistika handlerlari
def handle_fbs_shop_statistics_callback(call: CallbackQuery, api_key: str):
    """Do'kon bo'yicha FBS statistika"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        shops = api_client.get_shops()
        
        if shops and isinstance(shops, list):
            text = "🏪 <b>Do'kon bo'yicha FBS statistika</b>\n\n"
            
            for i, shop in enumerate(shops[:5], 1):
                shop_id = shop.get('id', 'N/A')
                shop_name = shop.get('name', 'Noma\'lum do\'kon')
                
                # Har bir do'kon uchun buyurtmalar sonini olamiz
                orders_count = api_client.get_fbs_orders_count(
                    shop_ids=[shop_id] if shop_id != 'N/A' else None,
                    status="CREATED"
                )
                
                count = orders_count.get('payload', 0) if orders_count else 0
                
                text += f"{i}. <b>{escape_html(shop_name)}</b>\n"
                text += f"   🆔 ID: {shop_id}\n"
                text += f"   📦 Buyurtmalar: {count} ta\n\n"
        else:
            text = "🏪 <b>Do'kon bo'yicha FBS statistika</b>\n\n📭 Do'konlar topilmadi."
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Do'kon bo'yicha FBS statistikani olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_date_statistics_callback(call: CallbackQuery, api_key: str):
    """Sana bo'yicha FBS statistika"""
    try:
        bot.edit_message_text(
            "📅 <b>Sana bo'yicha FBS statistika</b>\n\n" +
            "Bu funksiya hozircha ishlab chiqilmoqda.\n" +
            "Tez orada sana bo'yicha filtrlash imkoniyati qo'shiladi!\n\n" +
            "💡 Kelgusida sana oralig'ini tanlang va statistikani ko'ring.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Sana bo'yicha FBS statistikani olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_status_statistics_callback(call: CallbackQuery, api_key: str):
    """Status bo'yicha FBS statistika"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        shops = api_client.get_shops()
        shop_ids = []
        if shops and isinstance(shops, list):
            shop_ids = [shop.get('id') for shop in shops if shop.get('id')]
        
        text = "🔄 <b>Status bo'yicha FBS statistika</b>\n\n"
        
        # Asosiy statuslar bo'yicha statistika
        statuses = ["CREATED", "PACKING", "DELIVERING", "COMPLETED", "CANCELED"]
        
        for status in statuses:
            count_data = api_client.get_fbs_orders_count(
                shop_ids=shop_ids if shop_ids else None,
                status=status
            )
            
            count = count_data.get('payload', 0) if count_data else 0
            status_text = format_order_status_v2(status)
            
            text += f"{status_text}: {count} ta\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Status bo'yicha FBS statistikani olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_stock_statistics_callback(call: CallbackQuery, api_key: str):
    """Qoldiq bo'yicha FBS statistika"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        stocks = api_client.get_fbs_sku_stocks_v2()
        
        if stocks and 'data' in stocks:
            data = stocks['data']
            if isinstance(data, list) and len(data) > 0:
                text = "📦 <b>Qoldiq bo'yicha FBS statistika</b>\n\n"
                
                # Umumiy statistika
                total_sku = len(data)
                total_available = sum(stock.get('availableAmount', 0) for stock in data)
                total_reserved = sum(stock.get('reservedAmount', 0) for stock in data)
                
                text += f"🏷 Umumiy SKU: {total_sku} ta\n"
                text += f"📦 Mavjud qoldiq: {total_available} dona\n"
                text += f"🔒 Band qoldiq: {total_reserved} dona\n\n"
                
                # Top 5 SKU lar
                text += "📊 Top 5 SKU lar:\n"
                top_stocks = sorted(data, key=lambda x: x.get('availableAmount', 0), reverse=True)[:5]
                
                for i, stock in enumerate(top_stocks, 1):
                    sku = stock.get('sku', 'N/A')
                    available = stock.get('availableAmount', 0)
                    text += f"{i}. {sku}: {available} dona\n"
            else:
                text = "📦 <b>Qoldiq bo'yicha FBS statistika</b>\n\n📭 Ma'lumotlar topilmadi."
        else:
            text = "📦 <b>Qoldiq bo'yicha FBS statistika</b>\n\n📭 Ma'lumotlar topilmadi."
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Qoldiq bo'yicha FBS statistikani olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_finance_statistics_callback(call: CallbackQuery, api_key: str):
    """Moliyaviy FBS statistika"""
    try:
        bot.edit_message_text(
            "💰 <b>Moliyaviy FBS statistika</b>\n\n" +
            "Bu funksiya hozircha ishlab chiqilmoqda.\n" +
            "Tez orada moliyaviy ma'lumotlar bilan statistika qo'shiladi!\n\n" +
            "💡 Kelgusida daromad, xarajat va foyda statistikasini ko'ring.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Moliyaviy FBS statistikani olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

# Yangi yo'qolgan tovarlar handlerlari
def handle_fbs_missing_items_callback(call: CallbackQuery, api_key: str):
    """Yo'qolgan tovarlar ro'yxati"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        
        # Avval do'konlar ro'yxatini olamiz
        shops = api_client.get_shops()
        if not shops or not isinstance(shops, list):
            bot.edit_message_text(
                "❌ Do'konlar topilmadi yoki API xatoligi",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=get_back_to_main_keyboard()
            )
            return
        
        text = "🔍 <b>Yo'qolgan tovarlar ro'yxati</b>\n\n"
        
        # Har bir do'kon uchun yo'qolgan tovarlarni qidiramiz
        for i, shop in enumerate(shops[:3], 1):  # Faqat birinchi 3 ta do'kon
            shop_id = shop.get('id')
            shop_name = shop.get('name', 'Noma\'lum do\'kon')
            
            if not shop_id:
                continue
            
            text += f"🏪 <b>{escape_html(shop_name)}</b>\n"
            
            # Do'kon mahsulotlarini olamiz va yo'qolganlarni topamiz
            try:
                products = api_client.get_shop_products_by_shop_id(
                    shop_id=shop_id,
                    size=20,
                    page=0,
                    filter="WITHOUT_REQUIRED_FILTERS"  # Yo'qolgan tovarlar uchun
                )
                
                if products and 'productList' in products:
                    product_list = products['productList']
                    missing_count = 0
                    
                    for product in product_list[:5]:  # Faqat birinchi 5 ta mahsulot
                        sku_list = product.get('skuList', [])
                        for sku in sku_list:
                            if sku.get('quantityMissing', 0) > 0:
                                missing_count += 1
                                if missing_count <= 3:  # Har do'kon uchun max 3 ta
                                    sku_title = sku.get('skuTitle', 'N/A')
                                    missing_qty = sku.get('quantityMissing', 0)
                                    text += f"   ❌ {sku_title}: {missing_qty} dona yo'q\n"
                    
                    if missing_count == 0:
                        text += "   ✅ Yo'qolgan tovarlar yo'q\n"
                    elif missing_count > 3:
                        text += f"   ... va yana {missing_count - 3} ta\n"
                else:
                    text += "   📭 Mahsulotlar topilmadi\n"
                
            except Exception as e:
                text += f"   ⚠️ Xatolik: {str(e)[:50]}...\n"
            
            text += "\n"
        
        if len(shops) > 3:
            text += f"📊 <i>Jami {len(shops)} ta do'kon mavjud. Faqat birinchi 3 tasi ko'rsatildi.</i>\n\n"
        
        text += "💡 <b>Yo'qolgan tovarlar haqida:</b>\n"
        text += "• Bu tovarlar omborda yo'q yoki yetarli emas\n"
        text += "• Buyurtmalar bajarilmaydi\n"
        text += "• Tez orada to'ldirish kerak\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Yo'qolgan tovarlarni olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

def handle_fbs_missing_statistics_callback(call: CallbackQuery, api_key: str):
    """Yo'qolgan tovarlar statistikasi"""
    try:
        bot.edit_message_text(
            MESSAGES["data_loading"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        api_client = MarketplaceAPIClient(api_key)
        shops = api_client.get_shops()
        
        if not shops or not isinstance(shops, list):
            bot.edit_message_text(
                "❌ Do'konlar topilmadi yoki API xatoligi",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=get_back_to_main_keyboard()
            )
            return
        
        text = "📊 <b>Yo'qolgan tovarlar statistikasi</b>\n\n"
        
        total_missing = 0
        total_products = 0
        shop_missing_data = []
        
        # Har bir do'kon uchun statistika
        for shop in shops:
            shop_id = shop.get('id')
            shop_name = shop.get('name', 'Noma\'lum do\'kon')
            
            if not shop_id:
                continue
            
            try:
                products = api_client.get_shop_products_by_shop_id(
                    shop_id=shop_id,
                    size=50,
                    page=0,
                    filter="ALL"
                )
                
                if products and 'productList' in products:
                    product_list = products['productList']
                    shop_missing = 0
                    shop_total = len(product_list)
                    
                    for product in product_list:
                        sku_list = product.get('skuList', [])
                        for sku in sku_list:
                            missing_qty = sku.get('quantityMissing', 0)
                            if missing_qty > 0:
                                shop_missing += missing_qty
                    
                    total_missing += shop_missing
                    total_products += shop_total
                    
                    if shop_missing > 0:
                        shop_missing_data.append({
                            'name': shop_name,
                            'missing': shop_missing,
                            'total': shop_total
                        })
                
            except Exception as e:
                logger.error(f"Do'kon {shop_id} uchun ma'lumotlarni olishda xatolik: {e}")
                continue
        
        # Umumiy statistika
        text += f"📈 <b>Umumiy statistika:</b>\n"
        text += f"🏪 Do'konlar soni: {len(shops)} ta\n"
        text += f"📦 Jami mahsulotlar: {total_products} ta\n"
        text += f"❌ Yo'qolgan tovarlar: {total_missing} dona\n"
        
        if total_products > 0:
            missing_percentage = (total_missing / total_products) * 100
            text += f"📊 Yo'qolgan foizi: {missing_percentage:.1f}%\n"
        
        text += "\n🏪 <b>Do'kon bo'yicha:</b>\n"
        
        # Do'konlar bo'yicha saralangan statistika
        shop_missing_data.sort(key=lambda x: x['missing'], reverse=True)
        
        for i, shop_data in enumerate(shop_missing_data[:5], 1):
            shop_name = shop_data['name']
            missing = shop_data['missing']
            total = shop_data['total']
            percentage = (missing / total * 100) if total > 0 else 0
            
            text += f"{i}. <b>{escape_html(shop_name)}</b>\n"
            text += f"   ❌ Yo'qolgan: {missing} dona\n"
            text += f"   📦 Jami: {total} ta\n"
            text += f"   📊 Foizi: {percentage:.1f}%\n\n"
        
        if len(shop_missing_data) > 5:
            text += f"📋 <i>Jami {len(shop_missing_data)} ta do'konda yo'qolgan tovarlar mavjud.</i>\n\n"
        
        # Tavsiyalar
        text += "💡 <b>Tavsiyalar:</b>\n"
        text += "• Yo'qolgan tovarlarni tez orada to'ldiring\n"
        text += "• Ombordagi qoldiqlarni muntazam tekshiring\n"
        text += "• Buyurtmalar bajarilmasligini oldini oling\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=get_back_to_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Yo'qolgan tovarlar statistikasini olishda xatolik: {e}")
        bot.edit_message_text(
            MESSAGES["error"],
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
