# Agentic Long-Term Memory: Prototype Plan for The Agency

## 🎯 Objective

Implement and test a long-term memory system that:

* Stores meaningful facts, preferences, and events.
* Retrieves relevant context during interactions.
* Updates or prunes memories as needed.

---

## 🧪 Phase 1: Minimal Viable Memory Agent (MVM-A)

### ✅ Core Functions:

1. **Memory Storage**: Accepts and embeds entries.
2. **Memory Retrieval**: Queries based on relevance to incoming prompts.
3. **Memory Update/Prune**: Adjusts or removes stale/conflicting memory.

---

## 📦 Stack Options

| Component  | Options                         |
| ---------- | ------------------------------- |
| Vector DB  | FAISS (local), Weaviate (HTTP)  |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM        | LM Studio model or GPT-4o       |
| Storage    | JSON/SQLite (for metadata)      |
| Framework  | Bare Python or LangChain        |

---

## 🧠 Memory Schema v1

```json
{
  "memory_type": "fact",   // ["fact", "preference", "event"]
  "summary": "Mark prefers vector DBs for persistent memory.",
  "metadata": {
    "timestamp": "2025-06-26T13:00:00Z",
    "tags": ["preference", "agency-core"],
    "source": "chat-0626T13"
  }
}
```

---

## 🛠️ Plan of Action

### 1. `memory_store.py`

* Embeds new memory
* Stores to vector DB
* Supports relevance queries

### 2. `memory_agent.py`

* Wraps LM call
* Injects retrieved memories
* Sends prompt with context

### 3. `memory_test.py`

Simple CLI tester:

```bash
$ python memory_test.py "What do I like for memory persistence?"
```

Returns:

> Injected context + LLM reply.

### 4. Bonus: Memory Updater

* Detect changes (e.g., "Forget that...")
* Modify memory store accordingly

---

## 🧭 Decision Needed

Choose one to proceed:

* **💻 FAISS** (local, private, fast)
* **🌐 Weaviate** (easier HTTP testing)

---

## 🧩 Future Enhancements

* Summary condensation & aging
* Episodic vs semantic memory layering
* Custom pruning rules & event logging
* Memory visualization dashboard
