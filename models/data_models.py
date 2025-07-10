"""
Data models for the Banking AI System
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class AgentGoal:
    """Agent's autonomous goal definition for banking inclusion"""
    goal_type: str
    description: str
    success_criteria: Dict[str, Any]
    priority: int
    social_impact_metric: str  # How this goal impacts financial inclusion
    deadline: Optional[str] = None

@dataclass
class AgentMemory:
    """Agent's learning memory from banking decisions"""
    customer_segment: str  # Rural, Urban, Semi-Urban, Migrant, etc.
    situation_pattern: str
    action_taken: str
    outcome: str
    success_score: float
    learned_insight: str
    inclusion_impact: str  # Impact on financial inclusion
    timestamp: str

@dataclass
class AgentPlan:
    """Agent's autonomous banking action plan"""
    plan_id: str
    goal: str
    customer_segment: str  # Target demographic
    steps: List[Dict[str, Any]]
    contingencies: List[Dict[str, Any]]
    expected_outcome: str
    confidence: float
    inclusion_strategy: str  # How this helps underserved communities 