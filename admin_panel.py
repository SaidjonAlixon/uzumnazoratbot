"""
Admin Panel - MarketBot boshqaruvi uchun
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self, bot: TeleBot, db_path: str = "users.db"):
        self.bot = bot
        self.db_path = db_path
        self.admin_users = set()  # Admin foydalanuvchilar ID lari
        
        # Admin foydalanuvchilarni yuklash
        self.load_admin_users()
        
        # Default admin ni qo'shish (agar yo'q bo'lsa)
        self.add_default_admin()
        
        # Admin handlerlarni ro'yxatdan o'tkazish
        self.register_handlers()
        
        logger.info("Admin panel yaratildi va handlerlar ro'yxatdan o'tkazildi")
    
    def load_admin_users(self):
        """Admin foydalanuvchilarni ma'lumotlar bazasidan yuklash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Admin foydalanuvchilar jadvalini yaratish (agar mavjud bo'lmasa)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    added_date TEXT,
                    permissions TEXT
                )
            ''')
            
            # Admin foydalanuvchilarni olish
            cursor.execute('SELECT user_id FROM admin_users')
            admin_ids = cursor.fetchall()
            
            for (user_id,) in admin_ids:
                self.admin_users.add(user_id)
            
            conn.close()
            logger.info(f"Admin foydalanuvchilar yuklandi: {len(self.admin_users)} ta")
            
        except Exception as e:
            logger.error(f"Admin foydalanuvchilarni yuklashda xatolik: {e}")
    
    def add_default_admin(self):
        """Default admin ni qo'shish (agar yo'q bo'lsa)"""
        try:
            # Config dan default admin ID ni olish
            from config import ADMIN_CONFIG
            default_admin_id = ADMIN_CONFIG.get("default_admin_id")
            
            if default_admin_id and default_admin_id not in self.admin_users:
                success = self.add_admin(
                    user_id=default_admin_id,
                    username="DefaultAdmin",
                    full_name="Default Administrator"
                )
                if success:
                    logger.info(f"Default admin qo'shildi: {default_admin_id}")
                else:
                    logger.error(f"Default admin qo'shishda xatolik: {default_admin_id}")
                    
        except ImportError:
            logger.warning("ADMIN_CONFIG topilmadi, default admin qo'shilmaydi")
        except Exception as e:
            logger.error(f"Default admin qo'shishda xatolik: {e}")
    
    def is_admin(self, user_id: int) -> bool:
        """Foydalanuvchi admin ekanligini tekshirish"""
        return user_id in self.admin_users
    
    def add_admin(self, user_id: int, username: str = None, full_name: str = None) -> bool:
        """Yangi admin qo'shish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO admin_users (user_id, username, full_name, added_date, permissions)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, full_name, datetime.now().isoformat(), "ALL"))
            
            conn.commit()
            conn.close()
            
            self.admin_users.add(user_id)
            logger.info(f"Yangi admin qo'shildi: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Admin qo'shishda xatolik: {e}")
            return False
    
    def remove_admin(self, user_id: int) -> bool:
        """Admin huquqini olib tashlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM admin_users WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            self.admin_users.discard(user_id)
            logger.info(f"Admin huquqi olib tashlandi: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Admin huquqini olib tashlashda xatolik: {e}")
            return False
    
    def get_user_stats(self) -> Dict:
        """Foydalanuvchilar statistikasini olish"""
        try:
            logger.info("Getting user stats...")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Umumiy foydalanuvchilar soni
            logger.info("Counting total users...")
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            logger.info(f"Total users: {total_users}")
            
            # Faol foydalanuvchilar (son 7 kunda)
            try:
                logger.info("Counting active users...")
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute('SELECT COUNT(*) FROM users WHERE last_activity > ?', (week_ago,))
                active_users = cursor.fetchone()[0]
                logger.info(f"Active users: {active_users}")
            except Exception as active_error:
                logger.warning(f"Active users error: {active_error}")
                active_users = 0
            
            # Bloklangan foydalanuvchilar
            logger.info("Counting blocked users...")
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_blocked = 1')
            blocked_users = cursor.fetchone()[0]
            logger.info(f"Blocked users: {blocked_users}")
            
            # API kalitlari soni
            logger.info("Counting API users...")
            cursor.execute('SELECT COUNT(*) FROM users WHERE api_key IS NOT NULL AND api_key != ""')
            api_users = cursor.fetchone()[0]
            logger.info(f"API users: {api_users}")
            
            conn.close()
            
            stats = {
                'total_users': total_users,
                'active_users': active_users,
                'blocked_users': blocked_users,
                'api_users': api_users
            }
            logger.info(f"Final stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Statistikani olishda xatolik: {e}")
            return {}
    
    def get_all_users(self, limit: int = 100) -> List[Dict]:
        """Barcha foydalanuvchilarni olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, api_key, is_blocked, created_at
                FROM users 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'full_name': f"{row[2] or ''} {row[3] or ''}".strip() or "Noma'lum",
                    'has_api': bool(row[4]),
                    'is_blocked': bool(row[5]),
                    'registration_date': row[6]
                })
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Foydalanuvchilarni olishda xatolik: {e}")
            return []
    
    def get_all_users_with_api_keys(self, limit: int = 100) -> List[Dict]:
        """Barcha foydalanuvchilarni API kalitlari bilan olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, api_key, is_blocked, created_at
                FROM users 
                WHERE api_key IS NOT NULL AND api_key != ''
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'full_name': f"{row[2] or ''} {row[3] or ''}".strip() or "Noma'lum",
                    'api_key': row[4],
                    'is_blocked': bool(row[5]),
                    'registration_date': row[6]
                })
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Foydalanuvchilarni API kalitlari bilan olishda xatolik: {e}")
            return []
    
    def block_user(self, user_id: int) -> bool:
        """Foydalanuvchini bloklash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Foydalanuvchi bloklandi: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Foydalanuvchini bloklashda xatolik: {e}")
            return False
    
    def unblock_user(self, user_id: int) -> bool:
        """Foydalanuvchining blokini olib tashlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET is_blocked = 0 WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Foydalanuvchining bloki olib tashlandi: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Foydalanuvchining blokini olib tashlashda xatolik: {e}")
            return False
    
    def send_message_to_all(self, message_text: str, admin_id: int) -> Dict:
        """Barcha foydalanuvchilarga xabar yuborish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Faqat bloklanmagan foydalanuvchilarni olish
            cursor.execute('SELECT user_id FROM users WHERE is_blocked = 0')
            user_ids = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            success_count = 0
            failed_count = 0
            
            for user_id in user_ids:
                try:
                    self.bot.send_message(user_id, message_text, parse_mode="HTML")
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Xabar yuborishda xatolik {user_id}: {e}")
            
            # Natijani admin ga yuborish
            result_text = f"📢 <b>Xabar yuborish natijasi:</b>\n\n"
            result_text += f"✅ Muvaffaqiyatli: {success_count} ta\n"
            result_text += f"❌ Xatolik: {failed_count} ta\n"
            result_text += f"📊 Jami: {len(user_ids)} ta"
            
            self.bot.send_message(admin_id, result_text, parse_mode="HTML")
            
            return {
                'success': success_count,
                'failed': failed_count,
                'total': len(user_ids)
            }
            
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")
            return {}
    
    def get_admin_keyboard(self) -> InlineKeyboardMarkup:
        """Admin panel klaviaturasi"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        # Asosiy admin funksiyalari
        keyboard.add(
            InlineKeyboardButton("📊 Bot statistikasi", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")
        )
        
        keyboard.add(
            InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast"),
            InlineKeyboardButton("🔑 API kalitlar", callback_data="admin_api_keys")
        )
        
        keyboard.add(
            InlineKeyboardButton("🔐 Barcha API kalitlar", callback_data="admin_all_api_keys")
        )
        
        keyboard.add(
            InlineKeyboardButton("🔒 Foydalanuvchilarni boshqarish", callback_data="admin_user_management"),
            InlineKeyboardButton("📈 Faollik statistikasi", callback_data="admin_activity")
        )
        
        keyboard.add(
            InlineKeyboardButton("➕ Admin qo'shish", callback_data="admin_add_admin"),
            InlineKeyboardButton("🔙 Asosiy menyu", callback_data="admin_main_menu")
        )
        
        return keyboard
    
    def register_handlers(self):
        """Admin handlerlarni ro'yxatdan o'tkazish"""
        
        @self.bot.message_handler(commands=['admin'])
        def admin_command(message: Message):
            """Admin panel buyrug'i"""
            logger.info(f"Admin command from user {message.from_user.id}")
            
            if not self.is_admin(message.from_user.id):
                logger.warning(f"Non-admin user {message.from_user.id} tried to access admin panel")
                self.bot.reply_to(message, "❌ Sizda admin huquqi yo'q!")
                return
            
            admin_text = "🔐 <b>Admin Panel</b>\n\nKerakli amalni tanlang:"
            
            try:
                self.bot.send_message(
                    message.chat.id,
                    admin_text,
                    parse_mode="HTML",
                    reply_markup=self.get_admin_keyboard()
                )
                logger.info(f"Admin panel sent to user {message.from_user.id}")
            except Exception as e:
                logger.error(f"Admin panel yuborishda xatolik: {e}")
        
        # Callback handlerlarni bot_handlers.py da ro'yxatdan o'tkazamiz
        pass
    
    def handle_admin_back(self, call: CallbackQuery):
        """Admin panelga qaytish"""
        try:
            logger.info("Handling admin_back")
            admin_text = "🔐 <b>Admin Panel</b>\n\nKerakli amalni tanlang:"
            
            try:
                self.bot.edit_message_text(
                    admin_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=self.get_admin_keyboard()
                )
                logger.info("Admin panel message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    admin_text,
                    parse_mode="HTML",
                    reply_markup=self.get_admin_keyboard()
                )
                logger.info("New admin panel message sent")
            
        except Exception as e:
            logger.error(f"Admin panelga qaytishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Orqaga qaytishda xatolik!")
    
    def handle_admin_stats(self, call: CallbackQuery):
        """Admin statistika"""
        try:
            logger.info("Handling admin_stats")
            stats = self.get_user_stats()
            logger.info(f"Stats received: {stats}")
            
            text = "📊 <b>Bot statistikasi</b>\n\n"
            text += f"👥 Umumiy foydalanuvchilar: {stats.get('total_users', 0)} ta\n"
            text += f"✅ Faol foydalanuvchilar: {stats.get('active_users', 0)} ta\n"
            text += f"❌ Bloklangan: {stats.get('blocked_users', 0)} ta\n"
            text += f"🔑 API kalitlari: {stats.get('api_users', 0)} ta\n\n"
            text += f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            logger.info("Attempting to edit message...")
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("Stats message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                logger.info("Sending new message instead...")
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New stats message sent")
            
        except Exception as e:
            logger.error(f"Admin statistikani ko'rsatishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Statistika olinmadi!")
    
    def handle_admin_users(self, call: CallbackQuery):
        """Admin foydalanuvchilar ro'yxati"""
        try:
            logger.info("Handling admin_users")
            users = self.get_all_users(limit=20)
            
            text = "👥 <b>Foydalanuvchilar ro'yxati</b>\n\n"
            
            for i, user in enumerate(users[:10], 1):
                status = "❌" if user['is_blocked'] else "✅"
                api_status = "🔑" if user['has_api'] else "🔒"
                username = user['username'] or "Noma'lum"
                
                text += f"{i}. {status} {api_status} <b>{username}</b>\n"
                text += f"   ID: {user['user_id']}\n"
                text += f"   Sana: {user['registration_date'][:10] if user['registration_date'] else 'Noma''lum'}\n\n"
            
            if len(users) > 10:
                text += f"📋 Jami {len(users)} ta foydalanuvchi\n"
                text += "Keyingi sahifani ko'rish uchun tugmani bosing"
            
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("🔒 Bloklash", callback_data="admin_block_user"),
                InlineKeyboardButton("🔓 Blokni olib tashlash", callback_data="admin_unblock_user")
            )
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("Users message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New users message sent")
            
        except Exception as e:
            logger.error(f"Admin foydalanuvchilarni ko'rsatishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Foydalanuvchilar olinmadi!")
    
    def handle_admin_broadcast(self, call: CallbackQuery):
        """Admin xabar yuborish"""
        try:
            logger.info("Handling admin_broadcast")
            text = "📢 <b>Xabar yuborish</b>\n\n"
            text += "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring.\n\n"
            text += "💡 Xabar HTML formatda bo'lishi mumkin.\n"
            text += "❌ Bekor qilish uchun /cancel yozing."
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("Broadcast message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New broadcast message sent")
            
        except Exception as e:
            logger.error(f"Admin xabar yuborishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Xabar yuborish ochilmadi!")
    
    def handle_admin_block(self, call: CallbackQuery):
        """Admin bloklash"""
        try:
            logger.info("Handling admin_block")
            text = "🔒 <b>Foydalanuvchini bloklash</b>\n\n"
            text += "Bloklamoqchi bo'lgan foydalanuvchi Telegram ID sini yuboring.\n\n"
            text += "💡 Foydalanuvchi ID sini bilish uchun /admin_users buyrug'ini bosing.\n"
            text += "❌ Bekor qilish uchun /cancel yozing."
            
            # Foydalanuvchi ID ni kutish holatini saqlash
            self.bot.set_state(call.from_user.id, "waiting_for_block_user_id", call.message.chat.id)
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("Block message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New block message sent")
            
        except Exception as e:
            logger.error(f"Admin bloklashda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Bloklash ochilmadi!")
    
    def handle_admin_unblock(self, call: CallbackQuery):
        """Admin blokni olib tashlash"""
        try:
            logger.info("Handling admin_unblock")
            text = "🔓 <b>Blokni olib tashlash</b>\n\n"
            text += "Blokini olib tashlamoqchi bo'lgan foydalanuvchi Telegram ID sini yuboring.\n\n"
            text += "💡 Bloklangan foydalanuvchilar ro'yxatini ko'rish uchun /admin_users buyrug'ini bosing.\n"
            text += "❌ Bekor qilish uchun /cancel yozing."
            
            # Foydalanuvchi ID ni kutish holatini saqlash
            self.bot.set_state(call.from_user.id, "waiting_for_unblock_user_id", call.message.chat.id)
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("Unblock message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New unblock message sent")
            
        except Exception as e:
            logger.error(f"Admin blokni olib tashlashda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Blokni olib tashlash ochilmadi!")
    
    def handle_admin_add_admin(self, call: CallbackQuery):
        """Admin qo'shish"""
        try:
            logger.info("Handling admin_add_admin")
            text = "➕ <b>Yangi admin qo'shish</b>\n\n"
            text += "Admin qo'shmoqchi bo'lgan foydalanuvchi ID sini yuboring.\n\n"
            text += "💡 Foydalanuvchi ID sini bilish uchun /admin_users buyrug'ini bosing.\n"
            text += "❌ Bekor qilish uchun /cancel yozing."
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("Add admin message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New add admin message sent")
            
        except Exception as e:
            logger.error(f"Admin qo'shishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Admin qo'shish ochilmadi!")
    
    def handle_admin_api_keys(self, call: CallbackQuery):
        """Admin API kalitlar"""
        try:
            logger.info("Handling admin_api_keys")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, api_key, created_at 
                FROM users 
                WHERE api_key IS NOT NULL AND api_key != ""
                ORDER BY created_at DESC
                LIMIT 10
            ''')
            
            api_users = cursor.fetchall()
            conn.close()
            
            text = "🔑 <b>API kalitlar</b>\n\n"
            
            if api_users:
                for i, (user_id, username, api_key, created_at) in enumerate(api_users, 1):
                    username = username or "Noma'lum"
                    
                    text += f"{i}. <b>{username}</b>\n"
                    text += f"   ID: {user_id}\n"
                    text += f"   API: <code>{api_key}</code>\n"
                    text += f"   Sana: {created_at[:10] if created_at else 'Noma''lum'}\n\n"
            else:
                text += "📭 API kalitlari topilmadi"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("API keys message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New API keys message sent")
            
        except Exception as e:
            logger.error(f"Admin API kalitlarni ko'rsatishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ API kalitlar olinmadi!")
    
    def handle_admin_all_api_keys(self, call: CallbackQuery):
        """Admin barcha API kalitlar"""
        try:
            logger.info("Handling admin_all_api_keys")
            
            # Barcha foydalanuvchilarni API kalitlari bilan olish
            users = self.get_all_users_with_api_keys(limit=50)
            
            text = "🔐 <b>Barcha foydalanuvchilar API kalitlari</b>\n\n"
            
            if users:
                for i, user in enumerate(users, 1):
                    username = user['username'] or "Noma'lum"
                    full_name = user['full_name'] or "Noma'lum"
                    api_key = user['api_key']
                    status = "❌" if user['is_blocked'] else "✅"
                    date = user['registration_date'][:10] if user['registration_date'] else 'Noma''lum'
                    
                    text += f"{i}. {status} <b>{username}</b>\n"
                    text += f"   👤 Ism: {full_name}\n"
                    text += f"   🆔 ID: {user['user_id']}\n"
                    text += f"   🔑 API: <code>{api_key}</code>\n"
                    text += f"   📅 Sana: {date}\n\n"
                
                text += f"📊 Jami: {len(users)} ta foydalanuvchi API kalit bilan"
            else:
                text += "📭 API kalitlari topilmadi"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("All API keys message edited successfully")
                self.bot.answer_callback_query(call.id, "✅ Barcha API kalitlar ko'rsatildi!")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New all API keys message sent")
                self.bot.answer_callback_query(call.id, "✅ Barcha API kalitlar yuborildi!")
            
        except Exception as e:
            logger.error(f"Admin barcha API kalitlarda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Barcha API kalitlar olinmadi!")
    
    def handle_admin_activity(self, call: CallbackQuery):
        """Admin faollik"""
        try:
            logger.info("Handling admin_activity")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Bugungi faol foydalanuvchilar
            today = datetime.now().date().isoformat()
            try:
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(created_at) = ?
                ''', (today,))
                today_active = cursor.fetchone()[0]
            except:
                today_active = 0
            
            # Haftalik faol foydalanuvchilar
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            try:
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE created_at > ?
                ''', (week_ago,))
                week_active = cursor.fetchone()[0]
            except:
                week_active = 0
            
            # Oylik faol foydalanuvchilar
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            try:
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE created_at > ?
                ''', (month_ago,))
                month_active = cursor.fetchone()[0]
            except:
                month_active = 0
            
            conn.close()
            
            text = "📈 <b>Faollik statistikasi</b>\n\n"
            text += f"📅 Bugun: {today_active} ta\n"
            text += f"📅 Hafta: {week_active} ta\n"
            text += f"📅 Oy: {month_active} ta\n\n"
            text += f"🕐 Yangilangan: {datetime.now().strftime('%H:%M')}"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("Activity message edited successfully")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                # Xabarni tahrirlashda xatolik bo'lsa, yangi xabar yuborish
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New activity message sent")
            
        except Exception as e:
            logger.error(f"Admin faollikni ko'rsatishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Faollik olinmadi!")
    
    def handle_admin_user_management(self, call: CallbackQuery):
        """Admin foydalanuvchilarni boshqarish"""
        try:
            logger.info("Handling admin_user_management")
            text = "🔒 <b>Foydalanuvchilarni boshqarish</b>\n\n"
            text += "Kerakli amalni tanlang:"
            
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("🔒 Foydalanuvchini bloklash", callback_data="admin_block"),
                InlineKeyboardButton("🔓 Blokni olib tashlash", callback_data="admin_unblock")
            )
            keyboard.add(
                InlineKeyboardButton("👥 Foydalanuvchilar ro'yxati", callback_data="admin_users"),
                InlineKeyboardButton("📊 Bloklangan foydalanuvchilar", callback_data="admin_blocked_users")
            )
            keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("User management message edited successfully")
                self.bot.answer_callback_query(call.id, "✅ Foydalanuvchilarni boshqarish ochildi!")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info("New user management message sent")
                self.bot.answer_callback_query(call.id, "✅ Foydalanuvchilarni boshqarish yuborildi!")
            
        except Exception as e:
            logger.error(f"Admin foydalanuvchilarni boshqarishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Foydalanuvchilarni boshqarish ochilmadi!")
    
    def handle_admin_main_menu(self, call: CallbackQuery):
        """Admin panelga asosiy menyuga qaytish"""
        try:
            logger.info("Handling admin_main_menu")
            
            # Asosiy menyu klaviaturasini olish
            from keyboards import get_main_menu_keyboard
            main_keyboard = get_main_menu_keyboard(is_admin=True)
            
            text = "🏠 <b>Asosiy menyu</b>\n\nKerakli bo'limni tanlang:"
            
            try:
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=main_keyboard
                )
                logger.info("Main menu message edited successfully")
                self.bot.answer_callback_query(call.id, "✅ Asosiy menyuga qaytildi!")
            except Exception as edit_error:
                logger.error(f"Xabarni tahrirlashda xatolik: {edit_error}")
                self.bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode="HTML",
                    reply_markup=main_keyboard
                )
                logger.info("New main menu message sent")
                self.bot.answer_callback_query(call.id, "✅ Asosiy menyu yuborildi!")
            
        except Exception as e:
            logger.error(f"Admin asosiy menyuga qaytishda xatolik: {e}")
            self.bot.answer_callback_query(call.id, "❌ Asosiy menyuga qaytishda xatolik!")

# Admin panel yaratish
def create_admin_panel(bot: TeleBot) -> AdminPanel:
    """Admin panel yaratish"""
    return AdminPanel(bot)
