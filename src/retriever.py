from .vector_store import VectorStore

def retrieve_context(query, store=None, top_k=8):
    store=store or VectorStore()
    return store.search(query, n_results=top_k)

def format_context(results):
    return '\n\n'.join(f"[{i+1}] {r['metadata'].get('source')} | {r['metadata'].get('section')} | similarity={r['similarity']}:\n{r['text']}" for i,r in enumerate(results))
