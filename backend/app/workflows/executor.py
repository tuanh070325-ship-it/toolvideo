"""Workflow execution engine"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
import asyncio

from app.nodes import (
    BaseNode,
    VideoDownloadNode,
    VideoProcessNode,
    VideoExportNode,
    LTXGenerationNode,
    VideoAnalyzerNode,
    VideoTrimNode,
    VideoResizeNode,
    VideoMergeNode,
    VideoReupNode,
    AudioMixNode,
    TTSGenerationNode,
    HighlightExtractionNode,
    ImageToVideoNode,
)
from app.core.logger import logger


class WorkflowExecutor:
    """Execute workflows by running nodes in correct order"""
    
    # Node registry
    NODE_CLASSES = {
        "VideoDownload": VideoDownloadNode,
        "VideoProcess": VideoProcessNode,
        "VideoExport": VideoExportNode,
        "LTXGeneration": LTXGenerationNode,
        "TTSGeneration": TTSGenerationNode,
        "ImageToVideo": ImageToVideoNode,
        "VideoAnalyzer": VideoAnalyzerNode,
        "HighlightExtraction": HighlightExtractionNode,
        "VideoTrim": VideoTrimNode,
        "VideoResize": VideoResizeNode,
        "VideoMerge": VideoMergeNode,
        "VideoReup": VideoReupNode,
        "AudioMix": AudioMixNode,
    }
    
    def __init__(self):
        """Initialize workflow executor"""
        self.execution_history: List[Dict] = []
    
    async def execute_workflow(
        self,
        workflow: Dict[str, Any],
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a complete workflow
        
        Args:
            workflow: Workflow definition with nodes and connections
            inputs: Initial input values
            
        Returns:
            Final outputs from workflow
        """
        execution_id = f"exec_{int(datetime.now().timestamp())}"
        
        logger.info(f"Starting workflow execution: {execution_id}")
        logger.info(f"Workflow: {workflow.get('name', 'Unnamed')}")
        
        try:
            # Build execution graph
            nodes = self._build_nodes(workflow["nodes"])
            execution_order = self._topological_sort(
                workflow["nodes"],
                workflow["connections"]
            )
            
            # Execute nodes in order
            node_outputs = {}
            node_outputs.update(inputs)  # Add initial inputs
            
            # Create map of node definitions for quick lookup
            node_defs = {n["id"]: n for n in workflow["nodes"]}
            
            for node_id in execution_order:
                node = nodes[node_id]
                node_def = node_defs[node_id]
                
                # Gather inputs for this node
                node_inputs = self._gather_node_inputs(
                    node,
                    node_def,
                    workflow["connections"],
                    node_outputs
                )
                
                # Execute node
                logger.info(f"Executing node: {node.name} ({node_id})")
                outputs = await node.run(node_inputs)
                
                # Store outputs
                for output_name, output_value in outputs.items():
                    node_outputs[f"{node_id}.{output_name}"] = output_value
            
            # Extract final outputs
            final_outputs = self._extract_final_outputs(
                workflow["nodes"],
                node_outputs
            )
            
            # Record execution
            execution_record = {
                "execution_id": execution_id,
                "workflow_id": workflow.get("id"),
                "workflow_name": workflow.get("name"),
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "outputs": final_outputs
            }
            self.execution_history.append(execution_record)
            
            logger.info(f"✅ Workflow execution completed: {execution_id}")
            
            return {
                "execution_id": execution_id,
                "status": "success",
                "outputs": final_outputs
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}")
            
            execution_record = {
                "execution_id": execution_id,
                "workflow_id": workflow.get("id"),
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
            self.execution_history.append(execution_record)
            
            raise
    
    def _build_nodes(self, node_defs: List[Dict]) -> Dict[str, BaseNode]:
        """Build node instances from definitions"""
        nodes = {}
        
        for node_def in node_defs:
            node_id = node_def["id"]
            node_type = node_def["type"]
            
            if node_type not in self.NODE_CLASSES:
                raise ValueError(f"Unknown node type: {node_type}")
            
            node_class = self.NODE_CLASSES[node_type]
            nodes[node_id] = node_class(node_id)
        
        return nodes
    
    def _topological_sort(
        self,
        nodes: List[Dict],
        connections: List[Dict]
    ) -> List[str]:
        """Sort nodes in execution order using topological sort
        
        Args:
            nodes: List of node definitions
            connections: List of connections between nodes
            
        Returns:
            List of node IDs in execution order
        """
        # Build adjacency list
        graph = {node["id"]: [] for node in nodes}
        in_degree = {node["id"]: 0 for node in nodes}
        
        for conn in connections:
            source = conn["source_node"]
            target = conn["target_node"]
            graph[source].append(target)
            in_degree[target] += 1
        
        # Find nodes with no incoming edges
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            # Reduce in-degree for neighbors
            for neighbor in graph[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(nodes):
            raise ValueError("Workflow contains cycles")
        
        return result
    
    def _gather_node_inputs(
        self,
        node: BaseNode,
        node_def: Dict[str, Any],
        connections: List[Dict],
        node_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather inputs for a node from definition and previous outputs
        
        Args:
            node: Node object
            node_def: Node definition from workflow (contains static inputs)
            connections: Workflow connections
            node_outputs: All node outputs so far
            
        Returns:
            Dictionary of inputs for the node
        """
        # Start with static inputs from definition
        inputs = node_def.get("inputs", {}).copy()
        
        # Override with dynamic inputs from connections
        for conn in connections:
            if conn["target_node"] == node.node_id:
                source_node = conn["source_node"]
                source_output = conn["source_output"]
                target_input = conn["target_input"]
                
                output_key = f"{source_node}.{source_output}"
                if output_key in node_outputs:
                    inputs[target_input] = node_outputs[output_key]
        
        return inputs
    
    def _extract_final_outputs(
        self,
        nodes: List[Dict],
        node_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract final outputs from workflow execution
        
        Args:
            nodes: Node definitions
            node_outputs: All node outputs
            
        Returns:
            Final workflow outputs
        """
        # Find output nodes (nodes with no outgoing connections)
        # For now, just return all outputs
        return node_outputs
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        return self.execution_history[-limit:]


# Global executor instance
_executor = None

def get_workflow_executor() -> WorkflowExecutor:
    """Get global workflow executor instance"""
    global _executor
    if _executor is None:
        _executor = WorkflowExecutor()
    return _executor
