import os
import pandas as pd
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import google.generativeai as genai

# -------------------------------------------------------------------
# 🧠 Step 1: Pretty serialize Excel into text documents
# -------------------------------------------------------------------
def pretty_serialize_excel(file_path):
    df = pd.read_excel(file_path)
    docs = []

    for _, row in df.iterrows():
        doc = (
            f"In IPL {row['Year']}, {row['Team']} played {row['Mat']} matches, "
            f"won {row['Won']}, lost {row['Lost']}, tied {row['Tied']}, "
            f"and had {row['N/R']} no results. They scored {row['For']} runs and "
            f"conceded {row['Against']} runs. Their net run rate was {row['Net R/R']}, "
            f"and they earned {row['Points']} points, finishing in position {row['Position']}."
        )
        docs.append(doc)

    return docs

# -------------------------------------------------------------------
# ⚙️ Step 2: Configure Gemini
# -------------------------------------------------------------------
try:
    genai.configure(api_key="secret_google_key")
except ValueError as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please set your API key.")
    exit()

# -------------------------------------------------------------------
# 🧩 Step 3: Ask Gemini
# -------------------------------------------------------------------
def ask_gemini(collection, query, k=3):
    if not collection:
        return "Error: ChromaDB collection not available."

    # Query Chroma for relevant docs
    results = collection.query(query_texts=[query], n_results=k)
    docs = results['documents'][0]
    context = "\n".join(docs)

    prompt = f"""You are an IPL statistics assistant.

Use the context below to answer the question precisely and only using the given data.

Context:
\"\"\"{context}\"\"\"

Question: {query}

Answer:"""

    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini API call: {e}"

# -------------------------------------------------------------------
# 🧮 Step 4: Create or load Chroma collection
# -------------------------------------------------------------------
def create_chroma_collection(texts, embedding_fn):
    client = chromadb.PersistentClient(path="./chroma_db")

    try:
        collection = client.get_or_create_collection(
            name="ipl_stats",
            embedding_function=embedding_fn
        )
    except Exception as e:
        print(f"Error creating/getting collection: {e}")
        return None

    if collection.count() == 0:
        print("Adding documents to Chroma collection...")
        ids = [f"id_{i}" for i in range(len(texts))]
        metadatas = [{"row": i} for i in range(len(texts))]
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print("✅ Documents added to Chroma.")
    else:
        print("ℹ️ Collection already populated. Skipping document addition.")

    return collection

# -------------------------------------------------------------------
# 🧰 Step 5: Initialization
# -------------------------------------------------------------------
EXCEL_FILE = "./data/data_set.xlsx"  # 👈 Adjust path to your local file
if not os.path.exists(EXCEL_FILE):
    print(f"❌ Error: Excel file '{EXCEL_FILE}' not found.")
    exit()

# Use local sentence-transformer embeddings
embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

texts = pretty_serialize_excel(EXCEL_FILE)
collection = create_chroma_collection(texts, embedding_fn)

# -------------------------------------------------------------------
# 🚀 Step 6: RAG pipeline function
# -------------------------------------------------------------------
def rag_pipeline(query):
    return ask_gemini(collection, query)

# -------------------------------------------------------------------
# 💬 Step 7: Optional CLI for local testing
# -------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        user_query = input("\nAsk a question about IPL stats (or type 'exit'): ")
        if user_query.lower() in ["exit", "quit"]:
            print("👋 Exiting.")
            break
        try:
            answer = rag_pipeline(user_query)
            print("\n📣 Gemini's Answer:")
            print(answer)
        except Exception as e:
            print(f"❌ Error: {e}")
