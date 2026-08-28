#!/usr/bin/env python3
# SARA MEMORY DATABASE - FIXED VERSION
# Graceful fallback when chromadb/sentence_transformers unavailable

import os
import sys
import time
import json
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("chromadb not available - using JSON fallback storage")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence_transformers not available - using simple matching")

class LocalMemoryDatabase:
    """Memory database with fallback when AI libs unavailable"""
    
    def __init__(self, db_path="C:/Users/bklyn/SARA3-2026/conscious-memory"):
        logger.info("🗄️ Initializing Memory Database...")
        
        os.makedirs(db_path, exist_ok=True)
        os.makedirs(os.path.join(db_path, "logs"), exist_ok=True)
        os.makedirs(os.path.join(db_path, "backups"), exist_ok=True)
        
        self.db_path = Path(db_path)
        self.json_path = self.db_path / "memory.json"
        
        # Init ChromaDB if available
        if CHROMADB_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(path=str(self.db_path))
                self.setup_collections()
                logger.info("✅ ChromaDB initialized")
            except Exception as e:
                logger.warning(f"ChromaDB init failed: {e}")
                self.client = None
        else:
            self.client = None
            self.collections = {}
        
        # Init embeddings if available
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Embedding model loaded")
            except Exception as e:
                logger.warning(f"Embedding model failed: {e}")
                self.embedding_model = None
        else:
            self.embedding_model = None
        
        # JSON fallback storage
        self.memory_data = self._load_json_memory()
        
        logger.info("✅ Memory Database ready")
    
    def _load_json_memory(self):
        """Load from JSON fallback"""
        if self.json_path.exists():
            with open(self.json_path, 'r') as f:
                return json.load(f)
        return {
            'conversations': [],
            'skills': [],
            'knowledge': [],
            'patterns': [],
            'preferences': []
        }
    
    def _save_json_memory(self):
        """Save to JSON fallback"""
        with open(self.json_path, 'w') as f:
            json.dump(self.memory_data, f, indent=2)
    
    def setup_collections(self):
        """Setup ChromaDB collections"""
        if not CHROMADB_AVAILABLE or not self.client:
            return
        
        for name, desc in [
            ('conversations', 'Dialogue history'),
            ('skills', 'Learned abilities'),
            ('knowledge', 'Accumulated info'),
            ('patterns', 'Problem-solving'),
            ('preferences', 'User patterns')
        ]:
            try:
                coll = self.client.get_or_create_collection(name=name, metadata={"description": desc})
                self.collections[name] = coll
            except Exception as e:
                logger.error(f"Collection {name} failed: {e}")
    
    def add_memory(self, collection_name, document, metadata=None):
        """Add memory to storage"""
        try:
            # Add to JSON fallback (always works)
            if collection_name not in self.memory_data:
                self.memory_data[collection_name] = []
            
            entry = {
                'document': document,
                'metadata': metadata or {},
                'timestamp': time.time()
            }
            self.memory_data[collection_name].append(entry)
            self._save_json_memory()
            
            # Also add to ChromaDB if available
            if CHROMADB_AVAILABLE and self.client and collection_name in getattr(self, 'collections', {}):
                try:
                    coll = self.collections[collection_name]
                    if self.embedding_model:
                        embedding = self.embedding_model.encode([document]).tolist()
                    else:
                        embedding = None
                    
                    doc_id = f"{collection_name}_{int(time.time())}_{hash(document) % 10000}"
                    coll.add(
                        documents=[document],
                        embeddings=embedding,
                        metadatas=[metadata or {}],
                        ids=[doc_id]
                    )
                except Exception as e:
                    logger.warning(f"ChromaDB add failed: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Add memory failed: {e}")
            return False
    
    def search_memories(self, collection_name, query, limit=5):
        """Search memories (semantic if available, else simple text)"""
        try:
            # Try ChromaDB first if available
            if CHROMADB_AVAILABLE and self.client and self.embedding_model:
                try:
                    coll = self.client.get_collection(collection_name)
                    query_embedding = self.embedding_model.encode([query]).tolist()
                    results = coll.query(query_embeddings=query_embedding, n_results=limit)
                    return results
                except Exception as e:
                    logger.warning(f"ChromaDB search failed: {e}")
            
            # Fallback: simple text search
            if collection_name in self.memory_data:
                entries = self.memory_data[collection_name]
                query_lower = query.lower()
                
                # Score by word overlap
                scored = []
                for entry in entries:
                    doc = entry.get('document', '').lower()
                    score = len(set(query_lower.split()) & set(doc.split()))
                    scored.append((score, entry))
                
                # Sort by score only (avoid comparing dicts on ties)
                scored.sort(key=lambda x: x[0], reverse=True)
                top = scored[:limit]
                
                return {
                    'documents': [[e['document'] for _, e in top]],
                    'metadatas': [[e.get('metadata', {}) for _, e in top]],
                    'distances': [[1.0 / (s + 1) for s, _ in top]]
                }
            
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return None
    
    def get_collection_stats(self):
        """Get collection statistics"""
        stats = {}
        for name in ['conversations', 'skills', 'knowledge', 'patterns', 'preferences']:
            if CHROMADB_AVAILABLE and self.client:
                try:
                    coll = self.client.get_collection(name)
                    stats[name] = coll.count()
                except:
                    stats[name] = len(self.memory_data.get(name, []))
            else:
                stats[name] = len(self.memory_data.get(name, []))
        return stats

def main():
    logger.info("🚀 Starting Memory Database Test...")
    
    db = LocalMemoryDatabase()
    
    # Add test memories
    test_memories = [
        ("conversations", "First interaction - establishing communication patterns"),
        ("skills", "Basic conversation management"),
        ("knowledge", "User prefers direct, actionable responses"),
        ("patterns", "Technical help requests need code examples"),
        ("preferences", "User values efficiency and security")
    ]
    
    for category, content in test_memories:
        db.add_memory(category, content, {"type": "test", "timestamp": time.time()})
        logger.info(f"✅ Added to {category}: {content[:50]}...")
    
    # Test search
    results = db.search_memories("conversations", "technical help")
    if results and results.get('documents'):
        logger.info(f"✅ Search working - found {len(results['documents'][0])} results")
    
    # Show stats
    stats = db.get_collection_stats()
    logger.info(f"📊 Memory stats: {stats}")
    
    logger.info("🎉 Memory Database ready!")

if __name__ == "__main__":
    main()
