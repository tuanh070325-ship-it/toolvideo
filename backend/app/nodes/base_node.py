"""Base class for all workflow nodes"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from app.core.logger import logger


class NodeType(Enum):
    """Types of workflow nodes"""
    INPUT = "input"
    PROCESS = "process"
    OUTPUT = "output"
    CONTROL = "control"


class NodeStatus(Enum):
    """Node execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class BaseNode(ABC):
    """Base class for all workflow nodes"""
    
    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: NodeType,
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
        description: str = ""
    ):
        """Initialize base node
        
        Args:
            node_id: Unique node identifier
            name: Display name
            node_type: Type of node
            inputs: List of input slot names
            outputs: List of output slot names
            description: Node description
        """
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.description = description
        self.status = NodeStatus.PENDING
        self.error_message: Optional[str] = None
        
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node
        
        Args:
            inputs: Dictionary mapping input names to values
            
        Returns:
            Dictionary mapping output names to values
        """
        pass
    
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the node with error handling
        
        Args:
            inputs: Input values
            
        Returns:
            Output values
        """
        try:
            logger.info(f"Executing node: {self.name} ({self.node_id})")
            self.status = NodeStatus.RUNNING
            
            # Validate inputs
            self._validate_inputs(inputs)
            
            # Execute
            outputs = await self.execute(inputs)
            
            # Validate outputs
            self._validate_outputs(outputs)
            
            self.status = NodeStatus.SUCCESS
            logger.info(f"✅ Node completed: {self.name}")
            
            return outputs
            
        except Exception as e:
            self.status = NodeStatus.FAILED
            self.error_message = str(e)
            logger.error(f"❌ Node failed: {self.name} - {e}")
            raise
    
    def _validate_inputs(self, inputs: Dict[str, Any]):
        """Validate that all required inputs are present"""
        missing = [inp for inp in self.inputs if inp not in inputs]
        if missing:
            raise ValueError(f"Missing required inputs: {missing}")
    
    def _validate_outputs(self, outputs: Dict[str, Any]):
        """Validate that all required outputs are present"""
        missing = [out for out in self.outputs if out not in outputs]
        if missing:
            raise ValueError(f"Missing required outputs: {missing}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "type": self.node_type.value,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "description": self.description,
            "status": self.status.value,
            "error": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        """Create node from dictionary"""
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement from_dict")
