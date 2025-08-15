"""
Ma'lumotlar bazasi bilan ishlash moduli
SQLite3 yordamida foydalanuvchi ma'lumotlarini saqlash
"""

import sqlite3
import logging
from typing import Optional, Union
from config import DATABASE_FILE
from datetime import datetime

logger = logging.getLogger(__name__)

def init_database():
    """Ma'lumotlar bazasini yaratish va jadvallarni o'rnatish"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Foydalanuvchilar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                api_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked INTEGER DEFAULT 0
            )
        """)
        
        # last_activity ustunini qo'shish (agar mavjud bo'lmasa)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except:
            pass  # Ustun allaqachon mavjud
        
        # is_blocked ustunini qo'shish (agar mavjud bo'lmasa)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0")
        except:
            pass  # Ustun allaqachon mavjud
        
        # Admin foydalanuvchilar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                added_date TEXT,
                permissions TEXT DEFAULT 'ALL'
            )
            """)
        
        # Xabar yuborish tarixi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                message_text TEXT,
                sent_date TEXT,
                success_count INTEGER,
                failed_count INTEGER,
                total_count INTEGER
            )
        """)
        
        # Foydalanuvchi harakatlari
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT,
                action_data TEXT,
                action_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Ma'lumotlar bazasi muvaffaqiyatli yaratildi")
        
    except Exception as e:
        logger.error(f"Ma'lumotlar bazasini yaratishda xatolik: {e}")
        raise

def save_user_api_key(user_id: int, api_key: str, username: Optional[str] = None, 
                     first_name: Optional[str] = None, last_name: Optional[str] = None):
    """Foydalanuvchi API kalitini saqlash"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Foydalanuvchi mavjudligini tekshirish
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Mavjud foydalanuvchini yangilash
            cursor.execute("""
                UPDATE users 
                SET api_key = ?, username = ?, first_name = ?, last_name = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (api_key, username, first_name, last_name, user_id))
        else:
            # Yangi foydalanuvchi qo'shish
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, api_key)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, api_key))
        
        conn.commit()
        conn.close()
        logger.info(f"Foydalanuvchi {user_id} uchun API kalit saqlandi")
        return True
        
    except Exception as e:
        logger.error(f"API kalitni saqlashda xatolik: {e}")
        return False

def get_user_api_key(user_id: int) -> Optional[str]:
    """Foydalanuvchi API kalitini olish"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT api_key FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0]
        return None
        
    except Exception as e:
        logger.error(f"API kalitni olishda xatolik: {e}")
        return None

def is_user_blocked(user_id: int) -> bool:
    """Foydalanuvchi bloklangan ekanligini tekshirish"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT is_blocked FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result and result[0]:
            return True
        return False
        
    except Exception as e:
        logger.error(f"Foydalanuvchi bloklangan ekanligini tekshirishda xatolik: {e}")
        return False

def delete_user_api_key(user_id: int) -> bool:
    """Foydalanuvchi API kalitini o'chirish"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET api_key = NULL WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"Foydalanuvchi {user_id} uchun API kalit o'chirildi")
        return True
        
    except Exception as e:
        logger.error(f"API kalitni o'chirishda xatolik: {e}")
        return False

def user_exists(user_id: int) -> bool:
    """Foydalanuvchi mavjudligini tekshirish"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
        
    except Exception as e:
        logger.error(f"Foydalanuvchi mavjudligini tekshirishda xatolik: {e}")
        return False

def update_user_activity(user_id: int):
    """Foydalanuvchi faolligini yangilash"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # last_activity ustunini tekshirish
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_activity' not in columns:
            # Ustun yo'q bo'lsa qo'shish
            cursor.execute("ALTER TABLE users ADD COLUMN last_activity TEXT")
            conn.commit()
        
        cursor.execute("""
            UPDATE users 
            SET last_activity = ? 
            WHERE user_id = ?
        """, (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Foydalanuvchi faolligini yangilashda xatolik: {e}")
        return False

def get_user_stats():
    """Foydalanuvchilar statistikasini olish"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Umumiy foydalanuvchilar soni
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Faol foydalanuvchilar (son 7 kunda)
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE last_activity > datetime('now', '-7 days')
            """)
            active_users = cursor.fetchone()[0]
        except:
            active_users = 0  # last_activity ustuni yo'q bo'lsa
        
        # Bloklangan foydalanuvchilar
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        blocked_users = cursor.fetchone()[0]
        
        # API kalitlari soni
        cursor.execute("SELECT COUNT(*) FROM users WHERE api_key IS NOT NULL AND api_key != ''")
        api_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'blocked_users': blocked_users,
            'api_users': api_users
        }
        
    except Exception as e:
        logger.error(f"Statistikani olishda xatolik: {e}")
        return {}

def get_all_users(limit: int = 100):
    """Barcha foydalanuvchilarni olish"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, first_name, last_name, api_key, is_blocked, 
                   created_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'has_api': bool(row[4]),
                'is_blocked': bool(row[5]),
                'last_activity': row[6] if len(row) > 6 else None,
                'created_at': row[6] if len(row) > 6 else row[5]
            })
        
        conn.close()
        return users
        
    except Exception as e:
        logger.error(f"Foydalanuvchilarni olishda xatolik: {e}")
        return []

def block_user(user_id: int) -> bool:
    """Foydalanuvchini bloklash"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Foydalanuvchini bloklashda xatolik: {e}")
        return False

def unblock_user(user_id: int) -> bool:
    """Foydalanuvchining blokini olib tashlash"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET is_blocked = 0 WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Foydalanuvchining blokini olib tashlashda xatolik: {e}")
        return False

def save_broadcast_history(admin_id: int, message_text: str, success_count: int, 
                          failed_count: int, total_count: int):
    """Xabar yuborish tarixini saqlash"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO broadcast_history 
            (admin_id, message_text, sent_date, success_count, failed_count, total_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (admin_id, message_text, datetime.now().isoformat(), 
              success_count, failed_count, total_count))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Xabar yuborish tarixini saqlashda xatolik: {e}")
        return False
