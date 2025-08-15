"""
Yordamchi funksiyalar
Ma'lumotlarni formatlash va boshqa utility funksialar
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

def format_currency(amount: float, currency: str = "UZS") -> str:
    """Pulni formatlash"""
    try:
        return f"{amount:,.0f} {currency}"
    except:
        return f"{amount} {currency}"

def format_date(date_str: str) -> str:
    """Sanani formatlash"""
    try:
        if not date_str:
            return "Noma'lum"
        
        # ISO formatdagi sanani o'qish
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return date_str

def format_order_status(status: str) -> str:
    """Buyurtma holatini formatlash"""
    status_map = {
        "pending": "⏳ Kutilmoqda",
        "confirmed": "✅ Tasdiqlangan",
        "cancelled": "❌ Bekor qilingan",
        "shipped": "🚚 Yuborilgan",
        "delivered": "📦 Yetkazilgan",
        "returned": "↩️ Qaytarilgan",
        "processing": "🔄 Ishlanmoqda",
        "ready_to_ship": "📋 Yuborishga tayyor",
        "in_transit": "🚛 Yo'lda",
        "awaiting_payment": "💳 To'lov kutilmoqda"
    }
    return status_map.get(status.lower(), f"🔄 {status}")

def format_order_status_v2(status: str) -> str:
    """Buyurtma holatini formatlash (v2) - OpenAPI spetsifikatsiyasiga asoslanib"""
    status_map = {
        "CREATED": "🆕 Yaratilgan",
        "PACKING": "📦 Tayyorlanmoqda",
        "PENDING_DELIVERY": "⏳ Yuborish kutilmoqda",
        "DELIVERING": "🚚 Yuborilmoqda",
        "DELIVERED": "📦 Yetkazilgan",
        "ACCEPTED_AT_DP": "✅ DP da qabul qilingan",
        "DELIVERED_TO_CUSTOMER_DELIVERY_POINT": "📦 Mijozga yetkazilgan",
        "COMPLETED": "✅ Tugallangan",
        "CANCELED": "❌ Bekor qilingan",
        "PENDING_CANCELLATION": "⏳ Bekor qilish kutilmoqda",
        "RETURNED": "↩️ Qaytarilgan"
    }
    return status_map.get(status, f"🔄 {status}")

def format_product_info(product: Dict) -> str:
    """Mahsulot ma'lumotlarini formatlash"""
    try:
        name = product.get('name', 'Noma\'lum mahsulot')
        sku = product.get('sku', 'N/A')
        price = product.get('price', 0)
        stock = product.get('stock', 0)
        
        text = f"📦 <b>{name}</b>\n"
        text += f"🏷 SKU: <code>{sku}</code>\n"
        text += f"💰 Narx: {format_currency(price)}\n"
        text += f"📊 Qoldiq: {stock} dona\n"
        
        return text
    except Exception as e:
        return "Ma'lumotni formatlashda xatolik"

def format_order_info(order: Dict) -> str:
    """Buyurtma ma'lumotlarini formatlash"""
    try:
        order_id = order.get('id', 'N/A')
        status = order.get('status', 'unknown')
        total = order.get('total', 0)
        date = order.get('created_at', '')
        customer = order.get('customer_name', 'Noma\'lum')
        
        text = f"🛒 <b>Buyurtma #{order_id}</b>\n"
        text += f"👤 Mijoz: {customer}\n"
        text += f"📅 Sana: {format_date(date)}\n"
        text += f"📊 Holat: {format_order_status(status)}\n"
        text += f"💰 Summa: {format_currency(total)}\n"
        
        return text
    except Exception as e:
        return "Buyurtma ma'lumotini formatlashda xatolik"

def format_order_info_v2(order: Dict) -> str:
    """Buyurtma ma'lumotlarini formatlash (v2) - OpenAPI spetsifikatsiyasiga asoslanib"""
    try:
        order_id = order.get('id', 'N/A')
        status = order.get('status', 'unknown')
        price = order.get('price', 0)
        date_created = order.get('dateCreated', '')
        shop_id = order.get('shopId', 'N/A')
        scheme = order.get('scheme', 'FBS')
        
        text = f"🛒 <b>Buyurtma #{order_id}</b>\n"
        text += f"🏪 Do'kon ID: {shop_id}\n"
        text += f"📅 Sana: {format_date(date_created)}\n"
        text += f"📊 Holat: {format_order_status_v2(status)}\n"
        text += f"💰 Narx: {format_currency(price)}\n"
        text += f"🚚 Turi: {scheme}\n"
        
        # Buyurtma elementlari haqida ma'lumot
        order_items = order.get('orderItems', [])
        if order_items:
            text += f"📦 Mahsulotlar: {len(order_items)} ta\n"
        
        return text
    except Exception as e:
        return "Buyurtma ma'lumotini formatlashda xatolik (v2)"

def format_finance_data(data: Dict) -> str:
    """Moliyaviy ma'lumotlarni formatlash"""
    try:
        text = "💰 <b>Moliyaviy hisobot</b>\n\n"
        
        if 'revenue' in data:
            text += f"📈 Daromad: {format_currency(data['revenue'])}\n"
        
        if 'expenses' in data:
            text += f"📉 Xarajatlar: {format_currency(data['expenses'])}\n"
        
        if 'profit' in data:
            text += f"💵 Foyda: {format_currency(data['profit'])}\n"
        
        if 'orders_count' in data:
            text += f"🛒 Buyurtmalar soni: {data['orders_count']}\n"
        
        return text
    except Exception as e:
        return "Moliyaviy ma'lumotlarni formatlashda xatolik"

def format_finance_expenses_v2(payments: List[Dict]) -> str:
    """Moliyaviy xarajatlarni formatlash (v2) - OpenAPI spetsifikatsiyasiga asoslanib"""
    try:
        text = "💰 <b>Moliyaviy xarajatlar</b>\n\n"
        
        for i, payment in enumerate(payments, 1):
            payment_id = payment.get('id', 'N/A')
            name = payment.get('name', 'Noma\'lum')
            amount = payment.get('paymentPrice', 0)
            status = payment.get('status', 'unknown')
            date_created = payment.get('dateCreated', '')
            source = payment.get('source', 'N/A')
            
            text += f"{i}. <b>{escape_html(name)}</b>\n"
            text += f"   🆔 ID: {payment_id}\n"
            text += f"   💰 Summa: {format_currency(amount)}\n"
            text += f"   📊 Holat: {format_payment_status_v2(status)}\n"
            text += f"   📅 Sana: {format_date(date_created)}\n"
            text += f"   🔗 Manba: {source}\n\n"
        
        return text
    except Exception as e:
        return "Moliyaviy xarajatlarni formatlashda xatolik (v2)"

def format_shop_info(shop: Dict) -> str:
    """Do'kon ma'lumotlarini formatlash"""
    try:
        name = shop.get('name', 'Noma\'lum do\'kon')
        shop_id = shop.get('id', 'N/A')
        status = shop.get('status', 'unknown')
        
        text = f"🏪 <b>{name}</b>\n"
        text += f"🆔 ID: <code>{shop_id}</code>\n"
        text += f"📊 Holat: {format_order_status(status)}\n"
        
        if 'description' in shop:
            text += f"📝 Tavsif: {shop['description']}\n"
        
        return text
    except Exception as e:
        return "Do'kon ma'lumotini formatlashda xatolik"

def paginate_list(items: List, page: int = 1, per_page: int = 5) -> Dict:
    """Ro'yxatni sahifalash"""
    try:
        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page
        
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        page_items = items[start_index:end_index]
        
        return {
            'items': page_items,
            'current_page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    except Exception as e:
        return {
            'items': [],
            'current_page': 1,
            'total_pages': 1,
            'total_items': 0,
            'has_next': False,
            'has_prev': False
        }

def truncate_text(text: str, max_length: int = 100) -> str:
    """Matnni qisqartirish"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def escape_html(text: str) -> str:
    """HTML belglarini escape qilish"""
    if not text:
        return ""
    
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")
    
    return text

def format_error_message(error: str) -> str:
    """Xatolik xabarini formatlash"""
    return f"❌ <b>Xatolik:</b> {escape_html(error)}"

def format_success_message(message: str) -> str:
    """Muvaffaqiyat xabarini formatlash"""
    return f"✅ <b>Muvaffaqiyat:</b> {escape_html(message)}"

def format_info_message(message: str) -> str:
    """Ma'lumot xabarini formatlash"""
    return f"ℹ️ <b>Ma'lumot:</b> {escape_html(message)}"

def validate_api_key(api_key: str) -> bool:
    """API kalitni tekshirish"""
    if not api_key or len(api_key.strip()) < 10:
        return False
    
    # Asosiy format tekshiruvi
    return True

def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """Xavfsiz qiymat olish"""
    try:
        return data.get(key, default)
    except:
        return default

def format_list_message(items: List[Dict], formatter_func, title: str = "Ro'yxat") -> str:
    """Ro'yxat xabarini formatlash"""
    if not items:
        return f"📭 <b>{title}</b>\n\nMa'lumotlar topilmadi."
    
    text = f"📋 <b>{title}</b>\n\n"
    
    for i, item in enumerate(items, 1):
        text += f"{i}. {formatter_func(item)}\n"
        if i < len(items):
            text += "➖➖➖➖➖➖➖➖\n"
    
    return text

def format_payment_status_v2(status: str) -> str:
    """To'lov holatini formatlash (v2) - OpenAPI spetsifikatsiyasiga asoslanib"""
    status_map = {
        "CREATED": "🆕 Yaratilgan",
        "REFUNDED": "↩️ Qaytarilgan",
        "CONFIRMED": "✅ Tasdiqlangan",
        "CANCELED": "❌ Bekor qilingan"
    }
    return status_map.get(status, f"🔄 {status}")

def format_return_status(status: str) -> str:
    """Qaytarish holatini formatlash - OpenAPI spetsifikatsiyasiga asoslanib"""
    status_map = {
        "COMPLETED": "✅ Tugallangan",
        "PENDING": "⏳ Kutilmoqda",
        "CANCELED": "❌ Bekor qilingan",
        "ASSEMBLED": "📦 Yig'ilgan"
    }
    return status_map.get(status, f"🔄 {status}")

def format_return_type(type_return: str) -> str:
    """Qaytarish turini formatlash - OpenAPI spetsifikatsiyasiga asoslanib"""
    type_map = {
        "DEFECTED": "❌ Nuqsonli",
        "RETURN": "↩️ Oddiy qaytarish",
        "FBS": "🚚 FBS qaytarish"
    }
    return type_map.get(type_return, f"🔄 {type_return}")

def format_finance_orders_v2(order_items: List[Dict]) -> str:
    """Moliyaviy buyurtmalarni formatlash (v2) - OpenAPI spetsifikatsiyasiga asoslanib"""
    try:
        text = "💰 <b>Moliyaviy buyurtmalar</b>\n\n"
        
        for i, order in enumerate(order_items, 1):
            order_id = order.get('orderId', 'N/A')
            sku_title = order.get('skuTitle', 'Noma\'lum')
            amount = order.get('amount', 0)
            seller_price = order.get('sellerPrice', 0)
            commission = order.get('commission', 0)
            seller_profit = order.get('sellerProfit', 0)
            date = order.get('date', 0)
            
            text += f"{i}. <b>Buyurtma #{order_id}</b>\n"
            text += f"   🏷 SKU: {escape_html(sku_title)}\n"
            text += f"   📦 Miqdori: {amount} dona\n"
            text += f"   💰 Narx: {format_currency(seller_price)}\n"
            text += f"   💸 Komissiya: {format_currency(commission)}\n"
            text += f"   💵 Foyda: {format_currency(seller_profit)}\n"
            text += f"   📅 Sana: {format_date(date)}\n\n"
        
        return text
    except Exception as e:
        return "Moliyaviy buyurtmalarni formatlashda xatolik (v2)"
