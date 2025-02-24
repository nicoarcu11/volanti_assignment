import logging
from supabase import Client

logger = logging.getLogger(__name__)

def get_order_status(supabase: Client, order_id: str):
    try:
        if not order_id:
            logger.warning("Attempted to get order status with empty order_id")
            return "Se requiere un número de pedido válido."
            
        response = supabase.table("orders").select("*").eq("id", order_id).execute()
        order = response.data

        if order:
            try:
                order_products = order[0]["order"]
                product_details = []
                for product_id in order_products:
                    try:
                        product_response = supabase.table("products").select("*").eq("id", product_id).execute()
                        if product_response.data:
                            product_details.append(product_response.data[0])
                        else:
                            logger.warning(f"Product not found: {product_id}")
                    except Exception as e:
                        logger.error(f"Error fetching product {product_id}: {str(e)}")
                
                # Attach product details to order avoiding 'embedding', 'created_at', 'id' and 'price' fields
                order[0]["products"] = [{k: v for k, v in product.items() if k not in ['embedding', 'created_at', 'id', 'price']} for product in product_details]
                logger.info(f"Order {order_id} retrieved successfully with {len(product_details)} products")
                return order[0] 
            except KeyError as e:
                logger.error(f"Key error while processing order {order_id}: {str(e)}")
                return "Error al procesar los datos del pedido."
            except Exception as e:
                logger.error(f"Unexpected error processing order {order_id}: {str(e)}")
                return "Error al procesar el pedido."
        else:
            logger.info(f"Order not found: {order_id}")
            return "No se encontró un pedido con el ID proporcionado."
    except Exception as e:
        logger.error(f"Database error when fetching order {order_id}: {str(e)}")
        return "Error al buscar el pedido. Por favor, intente nuevamente más tarde."