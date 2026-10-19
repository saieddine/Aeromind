"""Hybrid GraphRAG retrieval: persisted graph + read-only Chroma collection."""
from __future__ import annotations
import re
from typing import Any, Callable, Dict, List

def _norm(s): return " ".join(re.findall(r"[a-z0-9]+",(s or "").casefold()))

class HybridRetriever:
    """`embed_query(question)` must return one vector from the existing embedding model."""
    def __init__(self, graph_retriever, collection, embed_query: Callable[[str], List[float]], *,
                 aircraft_id="a320", document_id="a320_ac_0624", vector_top_k=5, graph_top_k=10):
        if not callable(embed_query): raise TypeError("embed_query must be callable")
        self.graph_retriever, self.collection, self.embed_query = graph_retriever, collection, embed_query
        self.aircraft_id, self.document_id = aircraft_id, document_id
        self.vector_top_k, self.graph_top_k = max(1,int(vector_top_k)), max(1,int(graph_top_k))

    def retrieve(self, question: str) -> Dict[str, Any]:
        edges = self.graph_retriever.retrieve(question, top_k=self.graph_top_k)
        chunks = self._retrieve_vectors(question)
        return {"graph_edges":edges,"vector_chunks":chunks,"evidence":self._fuse(edges,chunks)}

    def _retrieve_vectors(self, question):
        emb=self.embed_query(question)
        if hasattr(emb,"tolist"): emb=emb.tolist()
        if not isinstance(emb,(list,tuple)) or not emb: raise ValueError("embed_query must return a non-empty vector")
        result=self.collection.query(query_embeddings=[list(emb)], n_results=self.vector_top_k,
            where={"$and":[{"aircraft_id":self.aircraft_id},{"document_id":self.document_id}]},
            include=["documents","metadatas","distances"])
        ids=(result.get("ids") or [[]])[0]; docs=(result.get("documents") or [[]])[0]
        metas=(result.get("metadatas") or [[]])[0]; distances=(result.get("distances") or [[]])[0]
        out=[]
        for i,cid in enumerate(ids):
            m=metas[i] if i<len(metas) and metas[i] else {}
            out.append({"chunk_id":cid,"text":docs[i] if i<len(docs) else "",
                "document_id":m.get("document_id",self.document_id),"aircraft_id":m.get("aircraft_id",self.aircraft_id),
                "document":m.get("document"),"section":m.get("section"),"concept":m.get("concept"),
                "page":m.get("page"),"content_type":m.get("content_type"),
                "distance":distances[i] if i<len(distances) else None,"retrieval_method":"chroma_vector"})
        return out

    @staticmethod
    def _fuse(edges, chunks):
        evidence=[]; seen=set()
        for e in edges:
            if not (e.get("evidence") or "").strip(): continue
            evidence.append({"kind":"graph_relation","text":f'{e.get("source_entity")} --[{e.get("predicate")}]--> {e.get("target_entity")}\\nEvidence: {e.get("evidence")}',
                "document_id":e.get("document_id"),"aircraft_id":e.get("aircraft_id"),"document":e.get("document"),
                "section":e.get("section"),"page":e.get("page"),"chunk_id":e.get("chunk_id"),
                "extraction_method":e.get("extraction_method"),"evidence_validated":e.get("evidence_validated"),"score":e.get("score")})
        for c in chunks:
            cid=str(c.get("chunk_id") or ""); key=cid or _norm(c.get("text") or "")
            if key in seen: continue
            seen.add(key)
            evidence.append({"kind":"vector_chunk","text":c.get("text") or "","document_id":c.get("document_id"),
                "aircraft_id":c.get("aircraft_id"),"document":c.get("document"),"section":c.get("section"),
                "concept":c.get("concept"),"page":c.get("page"),"chunk_id":cid,
                "retrieval_method":c.get("retrieval_method"),"distance":c.get("distance")})
        return evidence
