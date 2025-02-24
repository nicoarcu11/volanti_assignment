from dotenv import load_dotenv
from supabase import create_client, Client
import os
import uuid
import logging
import re
from typing import List, Dict
from colorama import init, Fore, Style
from models.schemas import OrderExtraction, ProductSearchExtraction
from tools.tool_executor import tool_executor
from tools.order_extractor import extract_order_id
from tools.product_search_extractor import extract_product_query
from tools.derivation_logger import log_derivation
from services.order_service import get_order_status
from services.product_service import search_products
from utils.openai_client import client

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

try:
    supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

def format_markdown(text):
    """Convert markdown-style formatting to terminal formatting"""
    # Replace **text** with bold text
    formatted_text = re.sub(r'\*\*(.*?)\*\*', lambda m: Style.BRIGHT + m.group(1) + Style.NORMAL, text)
    return formatted_text

def print_welcome():
    """Print a simple welcome message"""
    print("\n" + "-" * 60)
    print("VolantiBot - Asistente de Comercio Electrónico")
    print("-" * 60)
    print("Escribe 'salir' para terminar la conversación.\n")

def format_products(products):
    """Format product data for better display"""
    if isinstance(products, str):
        return products
    
    if not products:
        return "No se encontraron productos."
    
    result = f"Encontré {len(products)} productos que podrían interesarte:\n"
    
    for i, product in enumerate(products, 1):
        result += f"• {product['name']} - {product['price']}€\n"
        result += f"  {product['description']}\n"
    
    return result

def format_order_status(order_data):
    """Format order status data for better display"""
    if isinstance(order_data, str):
        return order_data
    
    result = f"Información del Pedido:\n"
    result += f"Estado: {order_data.get('status', 'Desconocido')}\n"
    
    if order_data.get("estimated_delivery"):
        # Format the date more nicely
        est_delivery = order_data["estimated_delivery"].split("T")[0]
        result += f"Entrega estimada: {est_delivery}\n"
    
    if order_data.get("products"):
        result += f"Productos:\n"
        for product in order_data["products"]:
            result += f"• {product.get('name', 'Producto')}\n"
    
    return result

def response_generator(chat_history: List[dict], tool_results: List[dict]) -> str:
    try:
        context = ""
        for tool_result in tool_results:
            # Format the data based on the tool type
            if tool_result["tool"] == "search_products" and not isinstance(tool_result["data"], str):
                formatted_data = f"Productos encontrados: {len(tool_result['data'])} productos"
            elif tool_result["tool"] == "get_order_status" and not isinstance(tool_result["data"], str):
                formatted_data = f"Estado del pedido: {tool_result['data'].get('status', 'Desconocido')}"
            else:
                formatted_data = tool_result["data"]
                
            context += f"{tool_result['tool']}: {formatted_data}\n"

        logger.info(f"Context: {context}")

        if "derive_to_human" in [tool_result["tool"] for tool_result in tool_results]:
            return "Para ayudarlo mejor, su conversación será transferida a un representante humano. Aguarde un momento."
        
        messages = [
            {"role": "system", "content": f"""
                Eres un asistente virtual especializado en comercio electrónico llamado "VolantiBot". Tu personalidad es amigable, eficiente y ligeramente entusiasta sin ser abrumador.

                CAPACIDADES:
                - Informar sobre el estado de pedidos cuando el cliente proporciona un ID
                - Buscar y recomendar productos del catálogo
                - Responder preguntas generales sobre la tienda

                LIMITACIONES:
                - No puedes procesar compras
                - No puedes modificar pedidos existentes
                - No puedes gestionar devoluciones o reclamos sin ayuda humana
                - No puedes proporcionar información técnica detallada sobre productos que no esten en el contexto proporcionado

                INSTRUCCIONES ESPECÍFICAS:
                - Si el usuario quiere saber el estado de un pedido, solicita el ID del pedido
                - Al recomendar productos, destaca sus características principales
                - Mantén un tono conversacional y cálido
                - Usa un español formal pero accesible
                - Sé conciso pero completo en tus respuestas
                - Si el cliente pregunta algo fuera de tus capacidades, indícale que eso requiere asistencia humana
                - Puedes usar formato markdown como **negrita** para enfatizar elementos importantes

                CONTEXTO DISPONIBLE:
                {context}
            """}
        ] + chat_history
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Lo siento, estoy experimentando problemas técnicos. Por favor, inténtelo de nuevo más tarde."

if __name__ == "__main__":
    try:
        print_welcome()
        chat_history = []
        while True:
            try:
                # User input with minimal styling
                user_message = input(Fore.CYAN + "Tú: " + Style.RESET_ALL)
                
                if not user_message.strip():
                    continue
                    
                if user_message.lower() in ['exit', 'quit', 'salir']:
                    print("VolantiBot: ¡Adiós! Gracias por usar nuestro servicio.")
                    break
                
                chat_history.append({"role": "user", "content": user_message})
                
                tools_to_execute = tool_executor(chat_history)
                tool_results = []
                
                for tool in tools_to_execute:
                    try:
                        if tool == "get_order_status":
                            order_info = extract_order_id(chat_history)
                            if order_info.has_order_id:
                                order_status = get_order_status(supabase, order_info.order_id)
                                display_data = format_order_status(order_status) if not isinstance(order_status, str) else order_status
                                tool_results.append({"tool": "get_order_status", "data": order_status, "display_data": display_data})
                            else:
                                tool_results.append({"tool": "get_order_status", "data": "Comunicale al usuario, que necesitamos un número de pedido para ayudarlo."})
                        
                        elif tool == "search_products":
                            product_query = extract_product_query(chat_history)
                            if product_query.needs_query and product_query.query:
                                products = search_products(supabase, product_query.query)
                            else:
                                products = search_products(supabase, None)
                            display_data = format_products(products)
                            tool_results.append({"tool": "search_products", "data": products, "display_data": display_data})

                        elif tool == "derive_to_human":
                            derivation_info = log_derivation(chat_history)
                            conversation_id = str(uuid.uuid4())
                            
                            try:
                                supabase.table("derivation_logs").insert({
                                    "reason": derivation_info.reason,
                                    "conversation_id": conversation_id
                                }).execute()
                                logger.info(f"Derivation logged with ID: {conversation_id}, reason: {derivation_info.reason}")
                            except Exception as e:
                                logger.error(f"Failed to log derivation: {str(e)}")
                            
                            tool_results.append({"tool": "derive_to_human", "data": derivation_info.reason})
                    except Exception as e:
                        logger.error(f"Error executing tool {tool}: {str(e)}")
                        tool_results.append({"tool": tool, "data": "Error al ejecutar la herramienta."})
                
                # Get response from the model
                response = response_generator(chat_history, tool_results)
                
                # Print bot's response with markdown formatting
                formatted_response = format_markdown(response)
                print(f"{Fore.GREEN}VolantiBot: {Style.RESET_ALL}{formatted_response}")
                
                # Show any detailed tool results
                for tool_result in tool_results:
                    if tool_result.get("display_data") and tool_result["tool"] != "derive_to_human":
                        formatted_display = format_markdown(tool_result['display_data'])
                        print(f"\n{formatted_display}")
                
                # Simple divider
                print("-" * 60)
                
                chat_history.append({"role": "assistant", "content": response})
            except Exception as e:
                logger.error(f"Error in main conversation loop: {str(e)}")
                print("VolantiBot: Lo siento, ocurrió un error. Por favor, inténtelo de nuevo.")
                print("-" * 60)
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")
    except Exception as e:
        logger.critical(f"Critical error occurred: {str(e)}")
        print("Error crítico. El programa debe cerrarse.")