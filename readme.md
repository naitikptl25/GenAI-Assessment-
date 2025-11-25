# Retrieval-Augmented Generation (RAG) System

This project implements a lightweight Retrieval-Augmented Generation (RAG) pipeline using **ChromaDB**, **Google Gemini Flash**, and **Google text-embedding-004** to answer HR-related questions based on company policy documents.

The system loads multiple text policy files, embeds them, retrieves the most relevant document for a user query, and generates a concise final answer using Gemini Flash.

---

## 1. Document Loading
- All policy documents placed in the `data` directory are automatically read.
- Each file's content is stored with its file name as metadata.
- These documents form the knowledge base for the RAG model.

---

## 2. Embedding Generation
- The project uses **Google's `text-embedding-004` model** to create vector embeddings for each document.
- These embeddings allow efficient semantic searching.
- ChromaDB stores vectors and metadata for retrieval.

---

## 3. Vector Database (ChromaDB)
- A new Chroma collection is created to store:
  - Document text  
  - Embeddings  
  - Metadata (file names)
- Each document is inserted with a unique ID.
- Chroma performs similarity search to find the most relevant policy.

---

## 4. Query + Retrieval Logic
- A user asks a question such as *“Can I work from home as a new intern?”*
- The query is embedded using the same embedding model.
- Chroma returns the **top 3 most relevant policy documents**.
- The system selects the **highest-weight document** (rank #1) for final answering.
- Only the top document is used to avoid hallucination or mixing policies.

---

## 5. Conflict Logic (How We Solved Conflicting Policies)
Sometimes two documents may both be relevant but contain contradictory rules (e.g., one says WFH allowed, one says not allowed).

We solved this by:
1. Retrieving multiple documents, but  
2. **Always selecting the first-ranked (highest similarity score) document** as the authoritative source.
3. The prompt instructs Gemini to rely *only* on this top document.
4. This avoids mixing conflicting information.

The system does **not** use date-based logic or rule-based ranking — the embeddings naturally assign higher weight to the most specific, most relevant policy.

---

## 6. Final Answer Generation
- Gemini Flash is used to generate the final response.
- A strict prompt is used:
  - Only final answer  
  - No policy summaries  
  - 1–2 sentences  
  - Must use only the retrieved document  
- This ensures the answer is concise and grounded.

---

## 7. Cost Analysis (Scalable System)
Estimated cost when scaled to a realistic production workload.

### **Scenario**
- **10,000 documents** in the knowledge base  
- **5,000 user queries per day**

### **Costs**
1. **Embeddings (one-time cost)**
   - 10k documents × ~1,000 tokens each ≈ 10M tokens
   - text-embedding-004 ≈ **$0.13 per 1M tokens**
   - **Total embedding cost ≈ $1.30 (one time)**

2. **Daily Queries**
   - Each query:
     - Embedding of user query ≈ 50 tokens
     - Gemini Flash generation ≈ 100–150 tokens  
   - Total tokens/day ≈ ~500k
   - Gemini Flash cost ≈ **$0.10 per 1M output tokens**
   - Embedding cost ≈ **$0.13 per 1M tokens**

   **Daily total ≈ $0.10–0.15 per day**

### **Monthly estimate**
→ **~$4–$5 per month** for 5,000 queries/day  
→ Highly scalable & extremely cost-efficient.

---

## 8. Summary of Pipeline
- Load HR policy documents  
- Embed using Google embedding model  
- Store embeddings in ChromaDB  
- Retrieve top document with similarity search  
- Pass document + question to Gemini Flash  
- Generate a grounded 1–2 sentence HR policy answer  

This setup is ideal for building fast, low-cost internal HR assistants or document-based chatbots.

