from supabase import create_client, Client
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import List, Dict
import random
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize the Supabase client
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def clear_tables():
    """Clear existing data from tables"""
    try:
        logger.info("Limpiando tablas existentes...")
        # Delete all records by using a condition that's always true
        supabase.table("orders").delete().neq('id', 0).execute()
        supabase.table("products").delete().neq('id', 0).execute()
        logger.info("Tablas limpiadas exitosamente")
    except Exception as e:
        logger.error(f"Error al limpiar tablas: {e}")
        raise

def generate_products() -> List[Dict]:
    """Generate a diverse set of products in Spanish"""
    return [
        # Herramientas / Tools
        {"name": "Destornillador Phillips", "description": "Destornillador de alta calidad con punta Phillips para trabajos de precisión.", "price": 8.99},
        {"name": "Martillo de Carpintero", "description": "Martillo resistente con mango ergonómico para trabajos de construcción.", "price": 12.50},
        {"name": "Llave Ajustable 8\"", "description": "Llave inglesa de acero inoxidable con ajuste preciso.", "price": 15.75},
        {"name": "Set de Destornilladores (10 piezas)", "description": "Conjunto completo de destornilladores de precisión para todo tipo de proyectos.", "price": 24.99},
        {"name": "Sierra Circular Eléctrica", "description": "Sierra potente para cortes precisos en madera y otros materiales.", "price": 89.99},
        
        # Accesorios para Coches / Car Accessories
        {"name": "Rueda de Repuesto Universal", "description": "Rueda de emergencia compatible con múltiples modelos de vehículos.", "price": 45.99},
        {"name": "Limpiaparabrisas Premium", "description": "Par de limpiaparabrisas de alta durabilidad resistentes a condiciones extremas.", "price": 22.50},
        {"name": "Cubierta para Volante", "description": "Funda para volante de cuero sintético con diseño ergonómico.", "price": 18.25},
        {"name": "Organizador para Maletero", "description": "Organizador plegable para mantener el maletero ordenado.", "price": 29.99},
        {"name": "Cargador USB para Coche", "description": "Cargador rápido con dos puertos USB para dispositivos móviles.", "price": 14.50},
        
        # Iluminación / Lighting
        {"name": "Lámpara de Escritorio LED", "description": "Lámpara moderna con luz ajustable y bajo consumo energético.", "price": 32.99},
        {"name": "Lámpara de Pie Moderna", "description": "Elegante lámpara de pie con altura ajustable y luz cálida.", "price": 79.50},
        {"name": "Tira de Luces LED 5m", "description": "Tira flexible de luces LED con control remoto y múltiples colores.", "price": 24.75},
        {"name": "Bombilla Inteligente WiFi", "description": "Bombilla controlable desde el móvil compatible con asistentes de voz.", "price": 19.99},
        {"name": "Lámpara Solar para Jardín", "description": "Conjunto de 4 lámparas solares para iluminación exterior.", "price": 34.50},
        
        # Electrónica / Electronics
        {"name": "Auriculares Bluetooth", "description": "Auriculares inalámbricos con cancelación de ruido y gran autonomía.", "price": 59.99},
        {"name": "Altavoz Portátil Resistente al Agua", "description": "Altavoz compacto con sonido 360° y resistencia IPX7.", "price": 45.75},
        {"name": "Cargador Inalámbrico", "description": "Base de carga rápida compatible con todos los smartphones modernos.", "price": 29.99},
        {"name": "Batería Externa 10000mAh", "description": "Powerbank de alta capacidad con carga rápida para múltiples dispositivos.", "price": 25.50},
        {"name": "Adaptador HDMI a USB-C", "description": "Adaptador de alta velocidad para conectar dispositivos modernos a pantallas.", "price": 18.99},
        
        # Hogar / Home
        {"name": "Set de Sartenes Antiadherentes", "description": "Conjunto de 3 sartenes de diferentes tamaños con recubrimiento premium.", "price": 64.99},
        {"name": "Almohada Ergonómica", "description": "Almohada con espuma viscoelástica para un descanso óptimo.", "price": 39.50},
        {"name": "Cafetera Programable", "description": "Cafetera automática con temporizador y función de mantener caliente.", "price": 55.75},
        {"name": "Set de Cuchillos de Cocina", "description": "Conjunto profesional de 5 cuchillos con soporte de madera.", "price": 49.99},
        {"name": "Robot Aspirador Inteligente", "description": "Aspirador automático con mapeo y control por aplicación móvil.", "price": 199.50},
    ]

def insert_products(products: List[Dict]) -> List[str]:
    """Insert products into database and return their IDs"""
    product_ids = []
    for product in products:
        product["created_at"] = datetime.now(timezone.utc).isoformat()
        try:
            response = supabase.table("products").insert(product).execute()
            if response.data:
                product_ids.append(response.data[0]["id"])
                logger.info(f"Producto añadido: {product['name']}")
            else:
                logger.error(f"Error al insertar producto: {product}")
        except Exception as e:
            logger.error(f"Error al insertar producto {product['name']}: {e}")
    
    return product_ids

def generate_orders(product_ids: List[str]) -> List[Dict]:
    """Generate varied orders with the products"""
    # Status options
    statuses = ["Procesando", "Enviado", "Entregado", "Cancelado"]
    weights = [0.3, 0.4, 0.2, 0.1]  # Probability weights
    
    orders = []
    for i in range(15):  # Create 15 orders
        # Select random products for this order (1-4 products)
        order_products = random.sample(product_ids, random.randint(1, 4))
        
        # Calculate total based on selected products
        total = 0
        for product_id in order_products:
            try:
                response = supabase.table("products").select("price").eq("id", product_id).execute()
                if response.data:
                    total += response.data[0]["price"]
            except Exception as e:
                logger.error(f"Error al obtener precio del producto {product_id}: {e}")
        
        # Add random shipping cost (5-15)
        shipping = round(random.uniform(5, 15), 2)
        total = round(total + shipping, 2)
        
        # Select random status with weighted probability
        status = random.choices(statuses, weights=weights, k=1)[0]
        
        # Set created_at date (1-30 days ago)
        days_ago = random.randint(1, 30)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        # Set estimated delivery based on status
        if status == "Procesando":
            est_delivery = created_at + timedelta(days=random.randint(5, 10))
        elif status == "Enviado":
            est_delivery = created_at + timedelta(days=random.randint(2, 5))
        elif status == "Entregado":
            est_delivery = created_at + timedelta(days=random.randint(1, 3))
            # Ensure delivery date is in the past
            if est_delivery > datetime.now(timezone.utc):
                est_delivery = datetime.now(timezone.utc) - timedelta(days=1)
        else:  # Canceled
            est_delivery = None
        
        orders.append({
            "status": status,
            "estimated_delivery": est_delivery.isoformat() if est_delivery else None,
            "order": order_products,
            "total_paid": total,
            "created_at": created_at.isoformat()
        })
    
    return orders

def insert_orders(orders: List[Dict]):
    """Insert orders into database"""
    for i, order in enumerate(orders):
        try:
            response = supabase.table("orders").insert(order).execute()
            if response.data:
                logger.info(f"Pedido {i+1} añadido con ID: {response.data[0]['id']}")
            else:
                logger.error(f"Error al insertar pedido {i+1}")
        except Exception as e:
            logger.error(f"Error al insertar pedido {i+1}: {e}")

if __name__ == "__main__":
    try:
        # Clear existing data
        clear_tables()
        
        # Generate and insert products
        products = generate_products()
        product_ids = insert_products(products)
        
        if product_ids:
            # Generate and insert orders
            orders = generate_orders(product_ids)
            insert_orders(orders)
            
            logger.info(f"\nBase de datos poblada exitosamente con {len(products)} productos y {len(orders)} pedidos!")
        else:
            logger.error("No se pudieron insertar productos. Proceso abortado.")
    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")