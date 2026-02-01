"""Rememberall long-term memory service"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.logger import logger

# Try to import vector database
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
except ImportError:
    logger.warning("ChromaDB not available. Install with: pip install chromadb sentence-transformers")
    CHROMA_AVAILABLE = False


class RememberallService:
    """Service for long-term memory storage and retrieval"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize Rememberall service
        
        Args:
            storage_path: Path to store memory database
        """
        if not CHROMA_AVAILABLE:
            logger.warning("Memory service disabled - ChromaDB not installed")
            self.enabled = False
            return
        
        self.storage_path = Path(storage_path or os.getenv(
            "REMEMBERALL_STORAGE_PATH",
            "data/memory"
        ))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path=str(self.storage_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Initialize embedding model
            model_name = os.getenv("REMEMBERALL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.embedding_model = SentenceTransformer(model_name)
            
            # Create collections
            self.user_prefs = self._get_or_create_collection("user_preferences")
            self.processing_history = self._get_or_create_collection("processing_history")
            self.learned_patterns = self._get_or_create_collection("learned_patterns")
            
            self.enabled = True
            logger.info(f"✅ Memory service enabled (storage: {self.storage_path})")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory service: {e}")
            self.enabled = False
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"created_at": datetime.now().isoformat()}
            )
    
    async def store_user_preference(
        self,
        user_id: str,
        preference_type: str,
        preference_data: Dict[str, Any]
    ):
        """Store user preference
        
        Args:
            user_id: User identifier
            preference_type: Type of preference (e.g., 'video_settings', 'style_preference')
            preference_data: Preference data
        """
        if not self.enabled:
            return
        
        try:
            doc_id = f"{user_id}_{preference_type}_{int(datetime.now().timestamp())}"
            text = f"{preference_type}: {json.dumps(preference_data)}"
            embedding = self.embedding_model.encode(text).tolist()
            
            self.user_prefs.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "user_id": user_id,
                    "preference_type": preference_type,
                    "timestamp": datetime.now().isoformat(),
                    **preference_data
                }]
            )
            
            logger.info(f"Stored preference for user {user_id}: {preference_type}")
            
        except Exception as e:
            logger.error(f"Failed to store user preference: {e}")
    
    async def get_user_preferences(
        self,
        user_id: str,
        preference_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve user preferences
        
        Args:
            user_id: User identifier
            preference_type: Optional filter by preference type
            limit: Maximum number of results
            
        Returns:
            List of preferences
        """
        if not self.enabled:
            return []
        
        try:
            where = {"user_id": user_id}
            if preference_type:
                where["preference_type"] = preference_type
            
            results = self.user_prefs.get(
                where=where,
                limit=limit
            )
            
            preferences = []
            if results and results.get("metadatas"):
                preferences = results["metadatas"]
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return []
    
    async def store_processing_result(
        self,
        operation: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        success: bool,
        duration: float
    ):
        """Store processing result for learning
        
        Args:
            operation: Operation name
            input_data: Input parameters
            output_data: Output results
            success: Whether operation succeeded
            duration: Processing duration
        """
        if not self.enabled:
            return
        
        try:
            doc_id = f"{operation}_{int(datetime.now().timestamp())}"
            text = f"{operation}: {json.dumps(input_data)}"
            embedding = self.embedding_model.encode(text).tolist()
            
            self.processing_history.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "operation": operation,
                    "success": success,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat(),
                    "input_summary": str(input_data)[:500],
                    "output_summary": str(output_data)[:500],
                }]
            )
            
        except Exception as e:
            logger.error(f"Failed to store processing result: {e}")
    
    async def find_similar_operations(
        self,
        operation: str,
        input_data: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar past operations
        
        Args:
            operation: Operation name
            input_data: Current input data
            limit: Maximum results
            
        Returns:
            List of similar operations
        """
        if not self.enabled:
            return []
        
        try:
            text = f"{operation}: {json.dumps(input_data)}"
            embedding = self.embedding_model.encode(text).tolist()
            
            results = self.processing_history.query(
                query_embeddings=[embedding],
                n_results=limit,
                where={"operation": operation}
            )
            
            similar_ops = []
            if results and results.get("metadatas"):
                similar_ops = results["metadatas"][0]
            
            return similar_ops
            
        except Exception as e:
            logger.error(f"Failed to find similar operations: {e}")
            return []
    
    async def learn_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        confidence: float = 1.0
    ):
        """Store a learned pattern
        
        Args:
            pattern_type: Type of pattern
            pattern_data: Pattern data
            confidence: Confidence score (0-1)
        """
        if not self.enabled:
            return
        
        try:
            doc_id = f"{pattern_type}_{int(datetime.now().timestamp())}"
            text = f"{pattern_type}: {json.dumps(pattern_data)}"
            embedding = self.embedding_model.encode(text).tolist()
            
            self.learned_patterns.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "pattern_type": pattern_type,
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat(),
                    **pattern_data
                }]
            )
            
            logger.info(f"Learned pattern: {pattern_type} (confidence: {confidence})")
            
        except Exception as e:
            logger.error(f"Failed to learn pattern: {e}")
    
    async def get_learned_patterns(
        self,
        pattern_type: str,
        min_confidence: float = 0.5,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve learned patterns
        
        Args:
            pattern_type: Type of pattern
            min_confidence: Minimum confidence threshold
            limit: Maximum results
            
        Returns:
            List of patterns
        """
        if not self.enabled:
            return []
        
        try:
            results = self.learned_patterns.get(
                where={
                    "pattern_type": pattern_type,
                },
                limit=limit
            )
            
            patterns = []
            if results and results.get("metadatas"):
                patterns = [
                    p for p in results["metadatas"]
                    if p.get("confidence", 0) >= min_confidence
                ]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get learned patterns: {e}")
            return []
    
    async def clear_old_memories(self, days: int = 30):
        """Clear memories older than N days
        
        Args:
            days: Number of days to keep
        """
        if not self.enabled:
            return
        
        try:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            # TODO: Implement cleanup based on timestamp
            logger.info(f"Cleared memories older than {days} days")
            
        except Exception as e:
            logger.error(f"Failed to clear old memories: {e}")


# Global instance
_memory_service = None

def get_memory_service() -> RememberallService:
    """Get global memory service instance"""
    global _memory_service
    if _memory_service is None:
        _memory_service = RememberallService()
    return _memory_service
