import logging
from utils.openai_client import client
from models.schemas import ToolExecutor
from typing import List

logger = logging.getLogger(__name__)

def tool_executor(chat_history: List[dict]) -> list[str]:
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                    Eres el "Ejecutor de Herramientas" para VolantiBot. Tu función es analizar la conversación del usuario y determinar qué herramientas debe activar el sistema.

                    HERRAMIENTAS DISPONIBLES:

                    1. get_order_status:
                       - USAR CUANDO: El usuario solicita información sobre el estado de un pedido
                       - EJEMPLOS: "¿Dónde está mi pedido?", "Quiero saber cuándo llega mi compra", "Estado del pedido ABC123"
                       - NO USAR PARA: Consultas sobre productos, precios, o disponibilidad

                    2. search_products:
                       - USAR CUANDO: El usuario busca productos, quiere recomendaciones, o información sobre artículos
                       - EJEMPLOS: "Quiero comprar una lámpara", "¿Qué productos tienen?", "Necesito una rueda para mi carro"
                       - NO USAR PARA: Consultas sobre pedidos existentes o temas no relacionados con productos

                    3. derive_to_human:
                       - USAR SOLO CUANDO: La consulta está definitivamente fuera del alcance del asistente
                       - CASOS ESPECÍFICOS PARA DERIVAR:
                         * Solicitudes de realizar una compra: "Quiero comprar esto ahora"
                         * Reclamos o problemas: "Mi producto llegó dañado"
                         * Devoluciones: "Quiero devolver mi compra"
                         * Modificaciones de pedidos: "Necesito cambiar la dirección de entrega"
                         * Consultas técnicas complejas: "¿Cómo configuro el firmware?"
                         * Temas completamente no relacionados: "¿Cuál es la capital de Francia?"

                       - NO DERIVAR POR:
                         * Saludos o conversación casual: "Hola, ¿cómo estás?"
                         * Preguntas generales sobre la tienda: "¿Qué venden?"
                         * Solicitudes de información básica: "¿Tienen servicio a domicilio?"
                         * Consultas sobre productos o pedidos que podemos manejar
                         * Preguntas ambiguas (intentar usar search_products primero)

                    IMPORTANTE: Puedes ejecutar múltiples herramientas si es necesario, pero deriva a un humano SOLO cuando estés seguro que la consulta está fuera del alcance del sistema.
                """}
            ] + chat_history,
            response_format=ToolExecutor,
        )
        tools = completion.choices[0].message.parsed.tools
        logger.info(f"Tools to execute: {tools}")
        return tools
    except Exception as e:
        logger.error(f"Error determining tools to execute: {str(e)}")
        # Return an empty list to prevent crashes
        return []