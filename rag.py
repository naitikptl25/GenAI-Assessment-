import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from google.generativeai import GenerativeModel, configure

# STEP 1: Load API Key
load_dotenv()
configure(api_key=os.getenv("GOOGLE_API_KEY"))

# STEP 2: Use Gemini Flash
gemini = GenerativeModel("gemini-2.0-flash")

# STEP 3: Create Embedding Function
embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    model_name="models/text-embedding-004"
)

# STEP 4: Load docs
def load_documents(path="data"):
    docs = []
    for f in os.listdir(path):
        with open(os.path.join(path, f), "r", encoding="utf-8") as file:
            docs.append((f, file.read()))
    return docs

documents = load_documents()

# STEP 5: Setup Chroma
client = chromadb.Client()
collection = client.create_collection(
    name="nebula_rag",
    embedding_function=embedding_fn
)

# STEP 6: Insert documents
for i, (name, text) in enumerate(documents):
    collection.add(
        documents=[text],
        metadatas=[{"source": name}],
        ids=[str(i)]
    )

# STEP 7: Query
user_query = "I just joined as a new intern. Can I work from home?"

retrieved = collection.query(
    query_texts=[user_query],
    n_results=3
)

# Highest-weight document = first retrieved
top_doc = retrieved["metadatas"][0][0]["source"]

# Use only top document's text
context_text = retrieved["documents"][0][0]

# STEP 8: Final-answer-only prompt
prompt = f"""
You are an HR policy assistant.
User question: "{user_query}"

Relevant document:
{context_text}

Respond with ONLY the final answer in 1–2 sentences.
"""

response = gemini.generate_content(prompt)

# OUTPUT
print("QUESTION:", user_query)
print("\nFINAL ANSWER:")
print(response.text.strip())

print("\nHIGHEST WEIGHT DOCUMENT:")
print(top_doc)
