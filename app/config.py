import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "openai/gpt-4o-mini"

KNOWLEDGE_BASE_DIR = "knowledge-base"
ORDERS_FILE = "data/orders.json"

TOP_K = 5