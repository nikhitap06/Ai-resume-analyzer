import os, hashlib, time
import chromadb
from .embeddings import EmbeddingModel

class VectorStore:
    def __init__(self, path=None, collection='resume_analyzer'):
        self.path = path or os.getenv('CHROMA_DIR','vector_db/chroma')
        self.client = chromadb.PersistentClient(path=self.path)
        self.collection = self.client.get_or_create_collection(collection, metadata={'hnsw:space':'cosine'})
        self.embedder = EmbeddingModel()
    def add_documents(self, documents, metadatas):
        if not documents: return
        ids=[hashlib.sha1((d+str(m)).encode()).hexdigest() for d,m in zip(documents,metadatas)]
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=self.embedder.encode(documents).tolist())
    def search(self, query, n_results=6, where=None):
        if self.collection.count()==0: return []
        result=self.collection.query(query_embeddings=self.embedder.encode(query).tolist(), n_results=min(n_results,self.collection.count()), where=where, include=['documents','metadatas','distances'])
        return [{'text':d,'metadata':m,'similarity':round(1-float(dist),4)} for d,m,dist in zip(result['documents'][0],result['metadatas'][0],result['distances'][0])]
    def count(self): return self.collection.count()

def index_knowledge_base(store, directory='knowledge_base'):
    docs=[]; metas=[]
    for name in sorted(os.listdir(directory)) if os.path.isdir(directory) else []:
        if not name.endswith('.md'): continue
        text=open(os.path.join(directory,name),encoding='utf-8').read()
        for i,chunk in enumerate([x.strip() for x in text.split('\n\n') if x.strip()]):
            docs.append(chunk); metas.append({'document_type':'knowledge_base','section':name,'source':name,'chunk':str(i),'timestamp':str(time.time())})
    store.add_documents(docs,metas)
