"""
Autonomous Orchestrator for coordinating multiple agents
"""

import json
import uuid
import asyncio
import streamlit as st
from typing import Dict, Any, List
from dataclasses import asdict

from config import logger, CLAUDE_MODEL_ID, safe_json_parse, rate_limited_api_call, bedrock_api_call_with_retry
from agents.document_agent import AutonomousDocumentAgent
from agents.risk_agent import AutonomousRiskAgent


class AutonomousOrchestrator:
    """Orchestrator for truly autonomous agents"""
    
    def __init__(self, aws_clients: Dict):
        self.aws_clients = aws_clients
        self.agents = {
            'document': AutonomousDocumentAgent(aws_clients),
            'risk': AutonomousRiskAgent(aws_clients)
        }
        self.negotiation_history = []
        self.coordination_strategies = ["sequential", "parallel", "negotiated", "competitive"]
    
    async def autonomous_coordination(self, application_data: Dict) -> Dict:
        """Autonomous coordination of multiple agents"""
        
        application_id = application_data.get('application_id')
        
        # Step 1: Let agents negotiate coordination strategy
        coordination_strategy = await self._negotiate_coordination_strategy(application_data)
        
        # Step 2: Execute coordinated processing
        if coordination_strategy['strategy'] == 'sequential':
            result = await self._sequential_processing(application_data)
        elif coordination_strategy['strategy'] == 'parallel':
            result = await self._parallel_processing(application_data)
        elif coordination_strategy['strategy'] == 'negotiated':
            result = await self._negotiated_processing(application_data)
        else:
            result = await self._sequential_processing(application_data)  # Fallback
        
        # Step 3: Autonomous final decision synthesis
        final_decision = await self._autonomous_decision_synthesis(result)
        
        return {
            'application_id': application_id,
            'coordination_strategy': coordination_strategy,
            'agent_results': result,
            'final_decision': final_decision,
            'autonomy_metrics': self._calculate_autonomy_metrics()
        }
    
    def _inject_document_bytes(self, application_data: Dict) -> Dict:
        """Inject document bytes into application data when needed for processing"""
        # Check if document_bytes already exists in the data
        if 'document_bytes' in application_data:
            return application_data
        # If we have stored bytes, inject them
        if hasattr(self, '_document_bytes'):
            return {**application_data, 'document_bytes': self._document_bytes}
        return application_data
    
    async def _negotiate_coordination_strategy(self, application_data: Dict) -> Dict:
        """Let agents negotiate how they want to coordinate"""
        
        # Get each agent's preference for coordination
        doc_preference = await self.agents['document'].negotiate_with_agent(
            self.agents['risk'],
            "coordination_strategy",
            application_data
        )
        
        risk_preference = await self.agents['risk'].negotiate_with_agent(
            self.agents['document'],
            "coordination_strategy", 
            application_data
        )
        
        # Orchestrator facilitates negotiation
        negotiation_prompt = f"""You are an autonomous orchestrator facilitating agent coordination.

Document Agent Preference:
{json.dumps(doc_preference, indent=2)}

Risk Agent Preference:
{json.dumps(risk_preference, indent=2)}

Available Strategies:
- sequential: Document agent first, then risk agent (traditional)
- parallel: Both agents work simultaneously (faster)
- negotiated: Agents collaborate and share interim results
- competitive: Agents work independently and best result wins

Application Context:
{json.dumps(application_data.get('customer_data', {}), indent=2)}

Determine the best coordination strategy considering:
1. Agent preferences and capabilities
2. Application complexity and urgency
3. Quality vs speed tradeoffs
4. Collaboration benefits

Respond in JSON:
{{
    "strategy": "strategy_name",
    "reasoning": "why this strategy is best",
    "expected_benefits": ["benefit1", "benefit2"],
    "potential_risks": ["risk1", "risk2"],
    "success_metrics": ["metric1", "metric2"],
    "coordination_details": {{
        "information_sharing": "how agents will share info",
        "decision_making": "how final decision will be made",
        "conflict_resolution": "how to handle disagreements"
    }}
}}"""

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": negotiation_prompt}],
                    "temperature": 0.3
                }
            )
            
            result = json.loads(response['body'].read())
            ai_response = result['content'][0]['text']
            
            # Use safe JSON parsing with fallback
            strategy = safe_json_parse(ai_response, {
                "strategy": "sequential",
                "reasoning": "Default coordination due to negotiation failure",
                "coordination_details": {"information_sharing": "basic"}
            })
            
            return strategy
            
        except Exception as e:
            logger.error(f"Coordination strategy negotiation failed: {str(e)}")
            return {
                "strategy": "sequential",
                "reasoning": "Default coordination due to negotiation failure",
                "coordination_details": {"information_sharing": "basic"}
            }
    
    async def _sequential_processing(self, application_data: Dict) -> Dict:
        """Sequential autonomous processing"""
        
        # Document agent processes first
        st.info("🤖 Document Agent: Processing autonomously...")
        doc_data = self._inject_document_bytes(application_data)
        doc_result = await self.agents['document'].autonomous_process(doc_data)

        # Risk agent processes with document results
        enhanced_data = {**application_data, 'document_result': doc_result}
        st.info("🤖 Risk Agent: Processing autonomously...")
        risk_result = await self.agents['risk'].autonomous_process(enhanced_data)
        
        return {
            'processing_type': 'sequential',
            'document_result': doc_result,
            'risk_result': risk_result,
            'agent_interactions': []
        }

    
    async def _parallel_processing(self, application_data: Dict) -> Dict:
        """Parallel autonomous processing"""
        
        st.info("🤖 Both Agents: Processing in parallel...")
        
        # Both agents process simultaneously with proper data
        doc_data = self._inject_document_bytes(application_data)
        doc_task = self.agents['document'].autonomous_process(doc_data)
        risk_task = self.agents['risk'].autonomous_process(application_data)
        
        doc_result, risk_result = await asyncio.gather(doc_task, risk_task)
        
        return {
            'processing_type': 'parallel',
            'document_result': doc_result,
            'risk_result': risk_result,
            'agent_interactions': []
        }

    
    async def _negotiated_processing(self, application_data: Dict) -> Dict:
        """Negotiated collaborative processing"""
        
        st.info("🤖 Agents: Collaborating and negotiating...")
        
        # Document agent starts
        doc_data = self._inject_document_bytes(application_data)
        doc_result = await self.agents['document'].autonomous_process(doc_data)
        
        # Agents negotiate based on initial results
        negotiation = await self.agents['document'].negotiate_with_agent(
            self.agents['risk'],
            "processing_collaboration",
            {'document_result': doc_result}
        )
        
        # Risk agent processes with negotiated approach
        enhanced_data = {
            **application_data, 
            'document_result': doc_result,
            'negotiation_outcome': negotiation
        }
        risk_result = await self.agents['risk'].autonomous_process(enhanced_data)
        
        return {
            'processing_type': 'negotiated',
            'document_result': doc_result,
            'risk_result': risk_result,
            'agent_interactions': [negotiation]
        }
    
    async def _autonomous_decision_synthesis(self, agent_results: Dict) -> Dict:
        """Autonomous synthesis of agent decisions"""
        
        # Remove any bytes data from agent results for JSON serialization
        safe_agent_results = {}
        for k, v in agent_results.items():
            if isinstance(v, bytes):
                continue
            elif isinstance(v, dict):
                # Recursively clean nested dictionaries
                safe_v = {}
                for k2, v2 in v.items():
                    if not isinstance(v2, bytes):
                        try:
                            json.dumps(v2)
                            safe_v[k2] = v2
                        except (TypeError, ValueError):
                            continue
                safe_agent_results[k] = safe_v
            else:
                try:
                    json.dumps(v)
                    safe_agent_results[k] = v
                except (TypeError, ValueError):
                    continue
        
        synthesis_prompt = f"""You are an autonomous orchestrator synthesizing agent decisions.

Agent Processing Results:
{json.dumps(safe_agent_results, indent=2)}

Each agent has processed autonomously with their own goals, learning, and adaptations.

Perform autonomous decision synthesis considering:
1. Each agent's autonomous conclusions and confidence
2. The learning and adaptations each agent made
3. Any negotiations or collaborations that occurred
4. Overall goal alignment and conflict resolution
5. Quality of autonomous reasoning from each agent

Synthesize into final decision in JSON:
{{
    "final_status": "approved/rejected/manual_review",
    "synthesis_confidence": 0.0-1.0,
    "synthesis_reasoning": "detailed reasoning for final decision",
    "agent_consensus": "agreement/disagreement/partial",
    "key_factors": ["factor1", "factor2"],
    "autonomy_quality": {{
        "document_agent_autonomy": 0.0-1.0,
        "risk_agent_autonomy": 0.0-1.0,
        "coordination_autonomy": 0.0-1.0
    }},
    "next_steps": ["step1", "step2"],
    "learning_outcomes": ["outcome1", "outcome2"],
    "system_adaptations": ["adaptation1", "adaptation2"]
}}"""

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": synthesis_prompt}],
                    "temperature": 0.2
                }
            )
            
            result = json.loads(response['body'].read())
            ai_response = result['content'][0]['text']
            
            # Use safe JSON parsing with fallback
            from config import safe_json_parse
            synthesis = safe_json_parse(ai_response, {
                "final_status": "manual_review",
                "synthesis_reasoning": "Autonomous synthesis failed, requiring human review",
                "synthesis_confidence": 0.3,
                "agent_consensus": "disagreement"
            })
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Autonomous decision synthesis failed: {str(e)}")
            return {
                "final_status": "manual_review",
                "synthesis_reasoning": "Autonomous synthesis failed, requiring human review",
                "synthesis_confidence": 0.3,
                "autonomy_quality": {
                    "document_agent_autonomy": 0.5,
                    "risk_agent_autonomy": 0.5,
                    "coordination_autonomy": 0.3
                }
            }
    
    def _calculate_autonomy_metrics(self) -> Dict:
        """Calculate metrics for true autonomy"""
        
        doc_agent = self.agents['document']
        risk_agent = self.agents['risk']
        
        return {
            'document_agent_autonomy': {
                'decisions_made': len(doc_agent.memory_bank),
                'adaptations_count': doc_agent.adaptation_count,
                'learning_instances': len(doc_agent.reflection_history),
                'negotiation_instances': len(doc_agent.negotiation_history)
            },
            'risk_agent_autonomy': {
                'decisions_made': len(risk_agent.memory_bank),
                'adaptations_count': risk_agent.adaptation_count,
                'learning_instances': len(risk_agent.reflection_history),
                'negotiation_instances': len(risk_agent.negotiation_history)
            },
            'system_autonomy_score': self._calculate_overall_autonomy_score()
        }
    
    def _calculate_overall_autonomy_score(self) -> float:
        """Calculate overall system autonomy score"""
        
        doc_agent = self.agents['document']
        risk_agent = self.agents['risk']
        
        # Factors that indicate true autonomy
        autonomy_factors = [
            len(doc_agent.memory_bank) > 0,  # Has learning history
            len(risk_agent.memory_bank) > 0,
            doc_agent.adaptation_count > 0,  # Has adapted behavior
            risk_agent.adaptation_count > 0,
            len(doc_agent.negotiation_history) > 0,  # Has negotiated
            len(risk_agent.negotiation_history) > 0,
            len(doc_agent.reflection_history) > 0,  # Has reflected
            len(risk_agent.reflection_history) > 0
        ]
        
        autonomy_score = sum(autonomy_factors) / len(autonomy_factors)
        return autonomy_score 