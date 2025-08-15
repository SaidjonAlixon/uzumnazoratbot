"""
Marketplace API bilan ishlash moduli
UZUM MARKET API integration
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from config import API_BASE_URL, API_HEADERS

logger = logging.getLogger(__name__)

class MarketplaceAPIClient:
    """Marketplace API mijozi"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = API_BASE_URL
        self.headers = {
            **API_HEADERS,
            "Authorization": api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def test_connection(self) -> bool:
        """API ulanishini tekshirish"""
        try:
            # API ulanishini tekshirish uchun FBS stocks endpoint (rasmda ko'rsatilgan)
            response = self.session.get(f"{self.base_url}/v2/fbs/sku/stocks", timeout=10)
            logger.info(f"API test response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"API test failed with response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API ulanishini tekshirishda xatolik: {e}")
            return False
    
    # FBS (Fulfillment by Seller) metodlari
    def get_fbs_orders(self, shop_ids: List[int] = None, status: str = "CREATED") -> Optional[Dict]:
        """FBS buyurtmalarini olish - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            params = {}
            
            if shop_ids:
                params['shopIds'] = shop_ids
            if status:
                params['status'] = status
            
            response = self.session.get(f"{self.base_url}/v1/fbs/orders", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS buyurtmalarini olishda xatolik: {e}")
            return None
    
    def get_fbs_order_details(self, order_id: str) -> Optional[Dict]:
        """FBS buyurtma tafsilotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/fbs/order/{order_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS buyurtma tafsilotlarini olishda xatolik: {e}")
            return None
    
    def cancel_fbs_order(self, order_id: str) -> bool:
        """FBS buyurtmani bekor qilish"""
        try:
            response = self.session.post(f"{self.base_url}/v1/fbs/order/{order_id}/cancel")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FBS buyurtmani bekor qilishda xatolik: {e}")
            return False
    
    def confirm_fbs_order(self, order_id: str) -> bool:
        """FBS buyurtmani tasdiqlash"""
        try:
            response = self.session.post(f"{self.base_url}/v1/fbs/order/{order_id}/confirm")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FBS buyurtmani tasdiqlashda xatolik: {e}")
            return False
    
    def get_fbs_return_reasons(self) -> Optional[List]:
        """FBS qaytarish sabablarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/fbs/order/return-reasons")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS qaytarish sabablarini olishda xatolik: {e}")
            return None
    
    def get_fbs_orders_count(self, shop_ids: List[int] = None, status: str = "CREATED", 
                           date_from: int = None, date_to: int = None) -> Optional[Dict]:
        """FBS buyurtmalar sonini olish - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            params = {}
            
            if shop_ids:
                params['shopIds'] = shop_ids
            if status:
                params['status'] = status
            if date_from:
                params['dateFrom'] = date_from
            if date_to:
                params['dateTo'] = date_to
            
            response = self.session.get(f"{self.base_url}/v2/fbs/orders/count", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS buyurtmalar sonini olishda xatolik: {e}")
            return None
    
    def get_fbs_stocks(self) -> Optional[List]:
        """FBS SKU qoldiqlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v2/fbs/sku/stocks")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS qoldiqlarini olishda xatolik: {e}")
            return None
    
    def update_fbs_stocks(self, stocks_data: List[Dict]) -> bool:
        """FBS SKU qoldiqlarini yangilash"""
        try:
            response = self.session.post(
                f"{self.base_url}/v2/fbs/sku/stocks",
                json=stocks_data
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FBS qoldiqlarini yangilashda xatolik: {e}")
            return False
    
    # Finance metodlari
    def get_finance_expenses(self, page: int = 0, size: int = 20, shop_id: int = None, 
                           shop_ids: List[int] = None, date_from: int = None, date_to: int = None,
                           sources: List[str] = None) -> Optional[Dict]:
        """Moliyaviy xarajatlarni olish - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            params = {
                'page': page,
                'size': size
            }
            
            if shop_id:
                params['shopId'] = shop_id
            if shop_ids:
                params['shopIds'] = shop_ids
            if date_from:
                params['dateFrom'] = date_from
            if date_to:
                params['dateTo'] = date_to
            if sources:
                params['sources'] = sources
            
            response = self.session.get(f"{self.base_url}/v1/finance/expenses", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Moliyaviy xarajatlarni olishda xatolik: {e}")
            return None
    
    def get_finance_orders(self, page: int = 0, size: int = 20, group: bool = False, 
                          date_from: int = None, date_to: int = None, statuses: List[str] = None,
                          shop_ids: List[int] = None) -> Optional[Dict]:
        """Moliyaviy buyurtmalar ro'yxatini olish - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            params = {
                'page': page,
                'size': size,
                'group': group
            }
            
            if date_from:
                params['dateFrom'] = date_from
            if date_to:
                params['dateTo'] = date_to
            if statuses:
                params['statuses'] = statuses
            if shop_ids:
                params['shopIds'] = shop_ids
            
            response = self.session.get(f"{self.base_url}/v1/finance/orders", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Moliyaviy buyurtmalarni olishda xatolik: {e}")
            return None
    
    # Invoice metodlari
    def get_invoices(self, size: int = 50, page: int = 0) -> Optional[List]:
        """Hisob-fakturalar ro'yxatini olish - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            params = {
                'size': min(size, 50),  # Maksimum 50
                'page': page
            }
            
            response = self.session.get(f"{self.base_url}/v1/invoice", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Hisob-fakturalarni olishda xatolik: {e}")
            return None
    
    def get_invoice_returns(self, return_id: int = None, page: int = 0, size: int = 50) -> Optional[List]:
        """Hisob-faktura qaytarishlarini olish - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            params = {
                'page': page,
                'size': min(size, 50)  # Maksimum 50
            }
            
            if return_id:
                params['returnId'] = return_id
            
            response = self.session.get(f"{self.base_url}/v1/return", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Hisob-faktura qaytarishlarini olishda xatolik: {e}")
            return None
    
    def get_shop_invoice(self, shop_id: str) -> Optional[Dict]:
        """Do'kon hisob-fakturasini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/shop/{shop_id}/invoice")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Do'kon hisob-fakturasini olishda xatolik: {e}")
            return None
    
    def get_shop_invoice_products(self, shop_id: str) -> Optional[List]:
        """Do'kon hisob-faktura mahsulotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/shop/{shop_id}/invoice/products")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Do'kon hisob-faktura mahsulotlarini olishda xatolik: {e}")
            return None
    
    def get_shop_invoice_return(self, shop_id: str) -> Optional[Dict]:
        """Do'kon hisob-faktura qaytarishini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/shop/{shop_id}/return")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Do'kon hisob-faktura qaytarishini olishda xatolik: {e}")
            return None
    
    def get_shop_return_details(self, shop_id: str, return_id: str) -> Optional[Dict]:
        """Do'kon qaytarish tafsilotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/shop/{shop_id}/return/{return_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Do'kon qaytarish tafsilotlarini olishda xatolik: {e}")
            return None
    
    # Product metodlari
    def update_product_price(self, shop_id: int, data: Dict) -> bool:
        """Mahsulot narxini yangilash - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            response = self.session.post(
                f"{self.base_url}/v1/product/{shop_id}/sendPriceData",
                json=data
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Mahsulot narxini yangilashda xatolik: {e}")
            return False
    
    def get_product_by_sku(self, shop_id: str) -> Optional[Dict]:
        """SKU bo'yicha mahsulotni olish"""
        try:
            params = {
                'page': 0,
                'size': 20,
                'filter': 'ALL'
            }
            response = self.session.get(f"{self.base_url}/v1/product/shop/{shop_id}", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Mahsulotni olishda xatolik: {e}")
            return None
    
    def search_products(self, shop_id: int, search_query: str = "", page: int = 0, size: int = 20, 
                       sort_by: str = "DEFAULT", order: str = "ASC", filter_type: str = "ALL", 
                       product_rank: str = None) -> Optional[Dict]:
        """Mahsulotlarni qidirish (OpenAPI spetsifikatsiyasiga asoslanib)"""
        try:
            params = {
                'page': page,
                'size': size,
                'sortBy': sort_by,
                'order': order,
                'filter': filter_type
            }
            
            if search_query:
                params['searchQuery'] = search_query
            if product_rank:
                params['productRank'] = product_rank
            
            response = self.session.get(
                f"{self.base_url}/v1/product/shop/{shop_id}", 
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Mahsulot qidirishda xatolik: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Mahsulot qidirishda xatolik: {e}")
            return None
    
    # Shop metodlari  
    def get_shops(self) -> Optional[List]:
        """Do'konlar ro'yxatini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/shops")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Do'konlar ro'yxatini olishda xatolik: {e}")
            return None
    
    def get_shop_invoice_by_id(self, shop_id: int, page: int = 0, size: int = 20) -> Optional[Dict]:
        """Do'kon bo'yicha hisob-fakturalarni olish"""
        try:
            params = {'page': page, 'size': size}
            response = self.session.get(f"{self.base_url}/v1/shop/{shop_id}/invoice", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Do'kon hisob-fakturasini olishda xatolik: {e}")
            return None
    
    def get_shop_invoice_products(self, shop_id: int, invoice_id: int) -> Optional[Dict]:
        """Hisob-faktura mahsulotlarini olish"""
        try:
            params = {'invoiceId': invoice_id}
            response = self.session.get(f"{self.base_url}/v1/shop/{shop_id}/invoice/products", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Hisob-faktura mahsulotlarini olishda xatolik: {e}")
            return None
    
    def get_shop_returns(self, shop_id: int, page: int = 0, size: int = 20) -> Optional[Dict]:
        """Do'kon qaytarishlarini olish"""
        try:
            params = {'page': page, 'size': size}
            response = self.session.get(f"{self.base_url}/v1/shop/{shop_id}/return", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Do'kon qaytarishlarini olishda xatolik: {e}")
            return None
    
    # Finance metodlari
    def get_finance_seller_payment_info(self) -> Optional[Dict]:
        """Moliyaviy to'lov ma'lumotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/finance/seller-payment-info")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Moliyaviy to'lov ma'lumotlarini olishda xatolik: {e}")
            return None
    
    def get_finance_commission_info(self) -> Optional[Dict]:
        """Komissiya ma'lumotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/finance/commission-info")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Komissiya ma'lumotlarini olishda xatolik: {e}")
            return None
    
    # FBS qo'shimcha metodlari
    def get_fbs_orders_v2(self, page: int = 0, size: int = 20, status: str = "CREATED", 
                          shop_ids: List[int] = None, date_from: int = None, date_to: int = None) -> Optional[Dict]:
        """FBS buyurtmalarini olish (v2) - OpenAPI spetsifikatsiyasiga asoslanib"""
        try:
            params = {
                'page': page, 
                'size': size,
                'status': status
            }
            
            if shop_ids:
                params['shopIds'] = shop_ids
            if date_from:
                params['dateFrom'] = date_from
            if date_to:
                params['dateTo'] = date_to
            
            response = self.session.get(f"{self.base_url}/v2/fbs/orders", params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS buyurtmalarini olishda xatolik: {e}")
            return None
    
    def get_fbs_order_by_id(self, order_id: str) -> Optional[Dict]:
        """FBS buyurtma tafsilotlarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/fbs/order/{order_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS buyurtma tafsilotlarini olishda xatolik: {e}")
            return None
    
    def confirm_fbs_order_v2(self, order_id: str) -> bool:
        """FBS buyurtmani tasdiqlash"""
        try:
            response = self.session.post(f"{self.base_url}/v1/fbs/order/{order_id}/confirm")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FBS buyurtmani tasdiqlashda xatolik: {e}")
            return False
    
    def cancel_fbs_order_v2(self, order_id: str, reason_id: int) -> bool:
        """FBS buyurtmani bekor qilish"""
        try:
            data = {"reasonId": reason_id}
            response = self.session.post(f"{self.base_url}/v1/fbs/order/{order_id}/cancel", json=data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FBS buyurtmani bekor qilishda xatolik: {e}")
            return False
    
    def get_fbs_return_reasons(self) -> Optional[Dict]:
        """FBS qaytarish sabablarini olish"""
        try:
            response = self.session.get(f"{self.base_url}/v1/fbs/order/return-reasons")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS qaytarish sabablarini olishda xatolik: {e}")
            return None
    
    def get_fbs_sku_stocks_v2(self) -> Optional[Dict]:
        """FBS SKU qoldiqlarini olish (v2)"""
        try:
            response = self.session.get(f"{self.base_url}/v2/fbs/sku/stocks")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"FBS SKU qoldiqlarini olishda xatolik: {e}")
            return None
    
    def update_fbs_sku_stocks(self, stock_data: Dict) -> bool:
        """FBS SKU qoldiqlarini yangilash"""
        try:
            response = self.session.post(f"{self.base_url}/v2/fbs/sku/stocks", json=stock_data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FBS SKU qoldiqlarini yangilashda xatolik: {e}")
            return False
