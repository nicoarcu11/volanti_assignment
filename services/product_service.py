import logging
from supabase import Client
from typing import List, Dict, Optional
import numpy as np
from utils.openai_client import generate_query_embedding

logger = logging.getLogger(__name__)

def cosine_similarity(a: list[float], b: list[float]) -> float:
    try:
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return 0.0

def search_products(supabase: Client, query: Optional[str]):
    try:
        if not query:
            logger.info("No query provided, returning all products")
            try:
                products = supabase.table("products").select("id, name, description, price").execute().data
                return products[:5]  # Return top 5 products
            except Exception as e:
                logger.error(f"Error fetching all products: {str(e)}")
                return "Error al buscar productos."
        
        try:
            query_embedding = generate_query_embedding(query)
            logger.info(f"Generated embedding for query: {query}")
        except Exception as e:
            logger.error(f"Error generating embedding for query '{query}': {str(e)}")
            # Fallback to simple search if embedding fails
            try:
                products = supabase.table("products").select("id, name, description, price").ilike("name", f"%{query}%").execute().data
                logger.info(f"Fallback search for '{query}' returned {len(products)} products")
                return products[:5]
            except Exception as e:
                logger.error(f"Error in fallback search: {str(e)}")
                return "Error al buscar productos."
        
        top_n = 5
        try:
            products = supabase.table("products").select("id, name, description, price, embedding").execute().data
            logger.info(f"Fetched {len(products)} products for similarity search")
        except Exception as e:
            logger.error(f"Error fetching products for similarity search: {str(e)}")
            return "Error al buscar productos."
            
        similarities = []
        for product in products:
            try:
                product_embedding = product.get("embedding")
                if not product_embedding:
                    logger.warning(f"Product {product.get('id')} has no embedding")
                    continue
                    
                similarity = cosine_similarity(query_embedding, product_embedding)
                similarities.append((product, similarity))
            except Exception as e:
                logger.error(f"Error processing product {product.get('id')}: {str(e)}")
                continue
                
        # Ordenar por similitud descendente
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_products = [prod for prod, sim in similarities[:top_n]]

        # Return top products without the embeddings
        for product in top_products:
            if "embedding" in product:
                del product["embedding"]

        logger.info(f"Returning {len(top_products)} products for query '{query}'")
        return top_products
    except Exception as e:
        logger.error(f"Unexpected error in search_products: {str(e)}")
        return "Error al buscar productos. Por favor, intente nuevamente."