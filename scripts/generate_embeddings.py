import logging
from openai import OpenAI
from supabase import Client, create_client
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

try:
    # Configurar clientes
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
except Exception as e:
    logger.error(f"Error initializing clients: {e}")
    raise

def generate_embedding(text: str) -> list[float]:
    """Generate embedding for the given text"""
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding for '{text[:30]}...': {e}")
        raise

def main():
    """Main function to generate and store embeddings"""
    try:
        logger.info("Iniciando generación de embeddings...")
        
        # Obtener productos
        products = supabase.table("products").select("id, name, description").execute().data
        logger.info(f"Se encontraron {len(products)} productos")
        
        success_count = 0
        error_count = 0
        
        for product in products:
            try:
                # Combine name and description for better semantic search
                text = f"{product['name']} {product.get('description', '')}"
                
                # Generate embedding
                embedding = generate_embedding(text)
                
                # Update product with embedding
                supabase.table("products").update({"embedding": embedding}).eq("id", product["id"]).execute()
                
                success_count += 1
                logger.info(f"Embedding generado para: {product['name']}")
            except Exception as e:
                error_count += 1
                logger.error(f"Error al procesar producto {product.get('name', product.get('id'))}: {e}")
        
        logger.info(f"Proceso completado: {success_count} exitosos, {error_count} con errores")
    except Exception as e:
        logger.error(f"Error en el proceso principal: {e}")

if __name__ == "__main__":
    main()