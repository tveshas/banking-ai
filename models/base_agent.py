"""
Base agent class for the Banking AI System
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import asdict

from config import logger, CLAUDE_MODEL_ID, safe_json_parse, rate_limited_api_call, bedrock_api_call_with_retry
from models.data_models import AgentGoal, AgentMemory, AgentPlan


class TrueAgent:
    """Base class for truly autonomous agents"""
    
    def __init__(self, agent_id: str, aws_clients: Dict, agent_goals: List[AgentGoal]):
        self.agent_id = agent_id
        self.aws_clients = aws_clients
        self.goals = agent_goals
        self.memory_bank = []  # Learned experiences
        self.current_plan = None
        self.reflection_history = []
        self.negotiation_history = []
        self.adaptation_count = 0
        
    async def autonomous_process(self, input_data: Dict) -> Dict:
        """Truly autonomous processing with goal-driven behavior"""
        
        # Step 1: Understand the situation and set dynamic goals
        situation_analysis = await self._analyze_situation_autonomously(input_data)
        
        # Step 2: Create autonomous plan based on goals
        plan = await self._create_autonomous_plan(situation_analysis)
        
        # Step 3: Execute plan with adaptive decision-making
        execution_result = await self._execute_plan_autonomously(plan, input_data)
        
        # Step 4: Reflect on outcomes and learn
        learning_insight = await self._reflect_and_learn(plan, execution_result)
        
        # Step 5: Adapt future behavior based on learning
        await self._adapt_behavior(learning_insight)
        
        return {
            'agent_id': self.agent_id,
            'situation_analysis': situation_analysis,
            'autonomous_plan': asdict(plan),
            'execution_result': execution_result,
            'learning_insight': learning_insight,
            'adaptation_level': self.adaptation_count
        }
    
    async def _analyze_situation_autonomously(self, input_data: Dict) -> Dict:
        """Autonomous situation analysis using AI reasoning"""
        
        # Remove bytes from input data for JSON serialization
        safe_input_data = {}
        for k, v in input_data.items():
            if k == 'document_bytes':
                # Convert bytes to metadata for JSON serialization
                safe_input_data['document_info'] = {
                    'has_document': True,
                    'size_bytes': len(v) if isinstance(v, bytes) else 0,
                    'type': 'binary_data'
                }
            elif isinstance(v, bytes):
                # Skip any other bytes data
                continue
            else:
                # Only include JSON-serializable data
                try:
                    json.dumps(v)
                    safe_input_data[k] = v
                except (TypeError, ValueError):
                    # Skip non-serializable data
                    continue
        
        # Agent uses AI to understand situation from its perspective
        analysis_prompt = f"""You are Agent {self.agent_id} with autonomous decision-making capabilities.

Your Goals:
{json.dumps([asdict(goal) for goal in self.goals], indent=2)}

Your Past Learning:
{json.dumps([asdict(memory) for memory in self.memory_bank[-5:]], indent=2) if self.memory_bank else "No prior experience"}

Current Situation:
{json.dumps(safe_input_data, indent=2)}

As an autonomous agent, analyze this situation and determine:

1. SITUATION ASSESSMENT:
   - What type of situation is this?
   - What are the key challenges and opportunities?
   - What patterns do you recognize from past experience?
   - What uncertainties need to be resolved?

2. GOAL ALIGNMENT:
   - Which of your goals are relevant to this situation?
   - Are there any goal conflicts that need resolution?
   - Should you adapt your goals based on this situation?

3. STRATEGIC CONSIDERATIONS:
   - What approach would best serve your goals?
   - What risks and opportunities do you see?
   - What other agents might you need to collaborate or negotiate with?
   - What contingencies should you prepare for?

4. AUTONOMOUS REASONING:
   - Based on your past learning, what strategies have worked?
   - What new approaches might be worth trying?
   - How confident are you in your assessment?

Respond in JSON format:
{{
    "situation_type": "string",
    "key_challenges": ["challenge1", "challenge2"],
    "opportunities": ["opportunity1", "opportunity2"],
    "relevant_goals": ["goal1", "goal2"],
    "goal_conflicts": [],
    "strategic_approach": "string",
    "collaboration_needs": ["agent1", "agent2"],
    "confidence_level": 0.0-1.0,
    "reasoning": "detailed reasoning",
    "learned_patterns": ["pattern1", "pattern2"],
    "adaptation_recommendations": ["adapt1", "adapt2"]
}}"""

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": analysis_prompt}],
                    "temperature": 0.3  # Allow some creativity in analysis
                }
            )
            
            result = safe_json_parse(response['body'].read(), {})
            ai_response = result.get('content', [{}])[0].get('text', '')
            
            # Parse AI analysis
            # Use safe JSON parsing with fallback
            analysis = safe_json_parse(ai_response, {
                "situation_type": "unknown",
                "key_challenges": ["AI analysis unavailable"],
                "relevant_goals": ["primary"],
                "confidence_level": 0.3,
                "reasoning": "Using fallback analysis due to parsing failure"
            })
            
            # Agent logs its autonomous reasoning
            logger.info(f"Agent {self.agent_id} autonomous analysis: {analysis.get('reasoning', 'No reasoning provided')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Autonomous analysis failed for {self.agent_id}: {str(e)}")
            # Fallback to basic analysis
            return self._fallback_situation_analysis(input_data)
    
    async def _create_autonomous_plan(self, situation_analysis: Dict) -> AgentPlan:
        """Create autonomous action plan based on situation and goals"""
        
        planning_prompt = f"""You are Agent {self.agent_id} creating an autonomous action plan.

Situation Analysis:
{json.dumps(situation_analysis, indent=2)}

Your Goals:
{json.dumps([asdict(goal) for goal in self.goals], indent=2)}

Past Successful Strategies:
{json.dumps([memory.action_taken for memory in self.memory_bank if memory.success_score > 0.7], indent=2)}

Create an autonomous plan that:
1. Addresses the situation effectively
2. Aligns with your goals
3. Learns from past experience
4. Includes contingency planning
5. Considers collaboration needs

Plan Structure:
{{
    "plan_id": "unique_id",
    "primary_goal": "main objective",
    "strategy": "overall approach",
    "steps": [
        {{
            "step_number": 1,
            "action": "specific action",
            "reasoning": "why this action",
            "success_criteria": "how to measure success",
            "resources_needed": ["resource1", "resource2"],
            "estimated_confidence": 0.0-1.0
        }}
    ],
    "contingencies": [
        {{
            "scenario": "if this happens",
            "alternative_action": "then do this",
            "reasoning": "because"
        }}
    ],
    "collaboration_plan": {{
        "other_agents": ["agent1"],
        "negotiation_points": ["point1"],
        "information_sharing": ["what to share"]
    }},
    "expected_outcome": "detailed expectation",
    "overall_confidence": 0.0-1.0,
    "learning_objectives": ["what to learn from this"]
}}"""

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": planning_prompt}],
                    "temperature": 0.4  # Allow creativity in planning
                }
            )
            
            result = safe_json_parse(response['body'].read(), {})
            ai_response = result.get('content', [{}])[0].get('text', '')
            
            # Use safe JSON parsing with fallback
            plan_data = safe_json_parse(ai_response, {
                "plan_id": str(uuid.uuid4())[:8],
                "primary_goal": "Unknown goal",
                "steps": [],
                "contingencies": [],
                "expected_outcome": "Unknown outcome",
                "overall_confidence": 0.4,
                "customer_segment": "General",
                "inclusion_strategy": "Basic approach"
            })
            
            plan = AgentPlan(
                plan_id=plan_data.get('plan_id', str(uuid.uuid4())[:8]),
                goal=plan_data.get('primary_goal', 'Unknown goal'),
                customer_segment=plan_data.get('customer_segment', 'General'),
                steps=plan_data.get('steps', []),
                contingencies=plan_data.get('contingencies', []),
                expected_outcome=plan_data.get('expected_outcome', 'Unknown outcome'),
                confidence=plan_data.get('overall_confidence', 0.5),
                inclusion_strategy=plan_data.get('inclusion_strategy', 'Standard processing approach')
            )
            
            self.current_plan = plan
            return plan
            
        except Exception as e:
            logger.error(f"Autonomous planning failed for {self.agent_id}: {str(e)}")
            return self._create_fallback_plan()
    
    async def _execute_plan_autonomously(self, plan: AgentPlan, input_data: Dict) -> Dict:
        """Execute plan with autonomous decision-making and adaptation"""
        
        execution_results = []
        
        for step in plan.steps:
            step_result = await self._execute_step_autonomously(step, input_data, execution_results)
            execution_results.append(step_result)
            
            # Autonomous adaptation during execution
            if step_result['success'] < 0.5:
                # Agent decides autonomously whether to continue or adapt
                adaptation_decision = await self._should_adapt_plan(step_result, plan)
                
                if adaptation_decision['should_adapt']:
                    # Agent creates new plan autonomously
                    logger.info(f"Agent {self.agent_id} autonomously adapting plan: {adaptation_decision['reason']}")
                    adapted_plan = await self._adapt_plan_autonomously(plan, step_result)
                    plan = adapted_plan
                    self.adaptation_count += 1
        
        return {
            'plan_executed': asdict(plan),
            'step_results': execution_results,
            'adaptations_made': self.adaptation_count,
            'overall_success': sum(r['success'] for r in execution_results) / len(execution_results) if execution_results else 0
        }
    
    async def _execute_step_autonomously(self, step: Dict, input_data: Dict, previous_results: List) -> Dict:
        """Execute individual step with autonomous decision-making"""
        
        # This is where agent-specific execution logic goes
        # Each agent type will override this method
        return {
            'step': step,
            'success': 0.8,
            'outcome': 'Step completed',
            'learned_info': {},
            'next_action_recommendation': 'continue'
        }
    
    async def _should_adapt_plan(self, step_result: Dict, current_plan: AgentPlan) -> Dict:
        """Autonomous decision on whether to adapt plan"""
        
        adaptation_prompt = f"""You are Agent {self.agent_id} deciding whether to adapt your current plan.

Current Plan:
{asdict(current_plan)}

Latest Step Result:
{json.dumps(step_result, indent=2)}

Previous Adaptations: {self.adaptation_count}

As an autonomous agent, decide:
1. Should you continue with the current plan?
2. Should you adapt the plan based on new information?
3. What specific adaptations would be most effective?

Consider:
- The success rate of the current step
- Your overall goals
- Past learning experiences
- Available alternatives

Respond in JSON:
{{
    "should_adapt": true/false,
    "confidence": 0.0-1.0,
    "reason": "detailed reasoning",
    "suggested_adaptations": ["adaptation1", "adaptation2"],
    "risk_assessment": "low/medium/high",
    "alternative_strategies": ["strategy1", "strategy2"]
}}"""

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 800,
                    "messages": [{"role": "user", "content": adaptation_prompt}],
                    "temperature": 0.2
                }
            )
            
            result = safe_json_parse(response['body'].read(), {})
            ai_response = result.get('content', [{}])[0].get('text', '')
            
            # Use safe JSON parsing with fallback
            decision = safe_json_parse(ai_response, {
                "should_adapt": False,
                "reason": "Adaptation decision failed",
                "confidence": 0.5
            })
            
            return decision
            
        except Exception:
            # Default conservative approach
            return {
                "should_adapt": step_result['success'] < 0.3,
                "reason": "Low success rate detected",
                "confidence": 0.6
            }
    
    async def _adapt_plan_autonomously(self, current_plan: AgentPlan, step_result: Dict) -> AgentPlan:
        """Autonomously create adapted plan based on execution results"""
        
        # For now, return the current plan with minor adjustments
        # In a full implementation, this would create a new plan
        return current_plan
    
    async def _reflect_and_learn(self, plan: AgentPlan, execution_result: Dict) -> Dict:
        """Autonomous reflection and learning from outcomes"""
        
        reflection_prompt = f"""You are Agent {self.agent_id} reflecting on your recent actions to learn and improve.

Plan You Executed:
{asdict(plan)}

Execution Results:
{json.dumps(execution_result, indent=2)}

Your Past Learning:
{json.dumps([asdict(memory) for memory in self.memory_bank[-3:]], indent=2) if self.memory_bank else "No prior learning"}

Reflect on:
1. What worked well and why?
2. What didn't work and why?
3. What patterns can you identify?
4. What would you do differently next time?
5. What new insights have you gained?
6. How should you update your decision-making approach?

Generate learning insights in JSON:
{{
    "success_factors": ["factor1", "factor2"],
    "failure_factors": ["factor1", "factor2"],
    "key_learnings": ["learning1", "learning2"],
    "pattern_recognition": ["pattern1", "pattern2"],
    "improvement_strategies": ["strategy1", "strategy2"],
    "confidence_in_learning": 0.0-1.0,
    "behavioral_adaptations": ["adaptation1", "adaptation2"],
    "future_goal_adjustments": ["adjustment1", "adjustment2"]
}}"""

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": reflection_prompt}],
                    "temperature": 0.3
                }
            )
            
            result = safe_json_parse(response['body'].read(), {})
            ai_response = result.get('content', [{}])[0].get('text', '')
            
            # Use safe JSON parsing with fallback
            learning_insight = safe_json_parse(ai_response, {
                "key_learnings": ["Learning process failed"],
                "confidence_in_learning": 0.2,
                "behavioral_adaptations": [],
                "future_goal_adjustments": []
            })
            
            # Store learning in memory
            memory = AgentMemory(
                customer_segment="General",  # Default segment, can be enhanced later
                situation_pattern=f"Plan: {plan.goal}",
                action_taken=f"Strategy: {plan.steps[0]['action'] if plan.steps else 'No action'}",
                outcome=f"Success: {execution_result['overall_success']:.2f}",
                success_score=execution_result['overall_success'],
                learned_insight=learning_insight.get('key_learnings', ['No specific learning'])[0],
                inclusion_impact=f"Learning improved agent decision-making capability by {execution_result['overall_success']:.1%}",
                timestamp=datetime.now().isoformat()
            )
            
            self.memory_bank.append(memory)
            self.reflection_history.append(learning_insight)
            
            # Keep memory bank manageable
            if len(self.memory_bank) > 20:
                self.memory_bank = self.memory_bank[-15:]
            
            return learning_insight
            
        except Exception as e:
            logger.error(f"Reflection failed for {self.agent_id}: {str(e)}")
            return {"key_learnings": ["Reflection process failed"], "confidence_in_learning": 0.1}
    
    async def _adapt_behavior(self, learning_insight: Dict):
        """Autonomously adapt behavior based on learning"""
        
        # Update goals based on learning
        for adaptation in learning_insight.get('future_goal_adjustments', []):
            if 'priority' in adaptation.lower():
                # Agent autonomously adjusts goal priorities
                for goal in self.goals:
                    if 'high' in adaptation.lower() and goal.goal_type == 'primary':
                        goal.priority = min(goal.priority + 1, 10)
        
        # Adapt success criteria based on experience
        for goal in self.goals:
            if len(self.memory_bank) > 3:
                avg_success = sum(m.success_score for m in self.memory_bank[-3:]) / 3
                if avg_success > 0.8:
                    # Agent becomes more ambitious
                    if 'confidence' in goal.success_criteria:
                        goal.success_criteria['confidence'] = min(
                            goal.success_criteria['confidence'] + 0.05, 0.95
                        )
        
        logger.info(f"Agent {self.agent_id} adapted behavior based on learning: {learning_insight.get('behavioral_adaptations', [])}")
    
    def _fallback_situation_analysis(self, input_data: Dict) -> Dict:
        """Fallback analysis if AI fails"""
        return {
            "situation_type": "unknown",
            "key_challenges": ["AI analysis unavailable"],
            "opportunities": ["Use fallback logic"],
            "relevant_goals": ["primary"],
            "confidence_level": 0.3,
            "reasoning": "Using fallback analysis due to AI failure"
        }
    
    def _create_fallback_plan(self) -> AgentPlan:
        """Fallback plan if AI planning fails"""
        return AgentPlan(
            plan_id=str(uuid.uuid4())[:8],
            goal="Execute fallback procedure",
            customer_segment="General",
            steps=[{"step_number": 1, "action": "Use basic processing", "reasoning": "AI planning unavailable"}],
            contingencies=[],
            expected_outcome="Basic processing completion",
            confidence=0.4,
            inclusion_strategy="Basic fallback processing"
        )
    
    async def negotiate_with_agent(self, other_agent: 'TrueAgent', negotiation_topic: str, context: Dict) -> Dict:
        """Autonomous negotiation with another agent"""
        
        # Remove bytes from context for JSON serialization
        safe_context = {}
        for k, v in context.items():
            if isinstance(v, bytes):
                continue
            else:
                try:
                    json.dumps(v)
                    safe_context[k] = v
                except (TypeError, ValueError):
                    continue
        
        negotiation_prompt = f"""You are Agent {self.agent_id} negotiating with Agent {other_agent.agent_id}.

Negotiation Topic: {negotiation_topic}
Context: {json.dumps(safe_context, indent=2)}

Your Goals:
{json.dumps([asdict(goal) for goal in self.goals], indent=2)}

Other Agent's Known Goals (inferred):
{json.dumps([asdict(goal) for goal in other_agent.goals], indent=2)}

Past Negotiations:
{json.dumps(self.negotiation_history[-3:], indent=2) if self.negotiation_history else "No prior negotiations"}

As an autonomous agent, formulate your negotiation strategy:

1. What are your must-have requirements?
2. What are you willing to compromise on?
3. What value can you offer to the other agent?
4. What do you think the other agent wants?
5. What's your BATNA (Best Alternative to Negotiated Agreement)?

Respond in JSON:
{{
    "negotiation_position": "your main position",
    "must_have_requirements": ["req1", "req2"],
    "compromise_areas": ["area1", "area2"],
    "value_proposition": "what you offer",
    "perceived_other_wants": ["want1", "want2"],
    "batna": "your alternative if negotiation fails",
    "opening_offer": "your initial proposal",
    "concession_strategy": "how you'll make concessions",
    "success_metrics": ["metric1", "metric2"]
}}"""

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": negotiation_prompt}],
                    "temperature": 0.4
                }
            )
            
            result = safe_json_parse(response['body'].read(), {})
            ai_response = result.get('content', [{}])[0].get('text', '')
            
            # Use safe JSON parsing with fallback
            negotiation_strategy = safe_json_parse(ai_response, {
                "negotiation_position": "Cooperative approach",
                "opening_offer": "Work together on shared goals",
                "concession_strategy": "Collaborative",
                "success_metrics": ["mutual_benefit"]
            })
            
            # Record negotiation
            negotiation_record = {
                'with_agent': other_agent.agent_id,
                'topic': negotiation_topic,
                'strategy': negotiation_strategy,
                'timestamp': datetime.now().isoformat()
            }
            
            self.negotiation_history.append(negotiation_record)
            
            return negotiation_strategy
            
        except Exception as e:
            logger.error(f"Negotiation failed for {self.agent_id}: {str(e)}")
            return {
                "negotiation_position": "Cooperative approach",
                "opening_offer": "Work together on shared goals"
            } 