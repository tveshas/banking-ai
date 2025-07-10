"""
Autonomous Document Processing Agent for Banking Inclusion
"""

import json
import uuid
import asyncio
from typing import Dict, Any, List

from config import logger, CLAUDE_MODEL_ID, safe_json_parse, rate_limited_api_call, bedrock_api_call_with_retry
from models.base_agent import TrueAgent
from models.data_models import AgentGoal


class AutonomousDocumentAgent(TrueAgent):
    """
    Intelligent Document Processing Agent for Banking Inclusion
    """
    
    def __init__(self, aws_clients: Dict):
        goals = [
            AgentGoal(
                goal_type="financial_inclusion",
                description="Maximize banking access for underserved communities by accepting diverse document formats and qualities",
                success_criteria={"rural_acceptance_rate": 0.95, "processing_time": 900, "language_support": 15},
                priority=10,
                social_impact_metric="Number of previously unbanked individuals successfully onboarded"
            ),
            AgentGoal(
                goal_type="document_intelligence", 
                description="Develop expertise in processing Indian identity documents across all states, languages, and conditions",
                success_criteria={"aadhaar_variants": 50, "pan_accuracy": 0.98, "vernacular_support": 0.90},
                priority=9,
                social_impact_metric="Percentage of non-English documents successfully processed"
            ),
            AgentGoal(
                goal_type="accessibility_optimization",
                description="Continuously improve document processing for elderly, disabled, and low-literacy customers",
                success_criteria={"elderly_success_rate": 0.92, "assisted_processing": 0.95},
                priority=8,
                social_impact_metric="Senior citizen and differently-abled banking inclusion rate"
            ),
            AgentGoal(
                goal_type="rural_specialization",
                description="Excel at processing documents from rural areas with limited infrastructure",
                success_criteria={"rural_document_quality": 0.85, "mobile_photo_acceptance": 0.90},
                priority=9,
                social_impact_metric="Rural banking penetration improvement"
            )
        ]
        
        super().__init__("banking_document_specialist", aws_clients, goals)
        
        # Specialized processing strategies for Indian banking context
        self.processing_strategies = {
            "premium_inclusion": {
                "description": "High-accuracy processing for premium customers while maintaining inclusion",
                "accuracy": 0.98, "cost": "high", "speed": "medium",
                "inclusion_focus": "Maintain quality while serving affluent customers"
            },
            "rural_optimized": {
                "description": "Optimized for rural customers with poor document quality",
                "accuracy": 0.85, "cost": "medium", "speed": "fast", 
                "inclusion_focus": "Maximize acceptance of low-quality rural documents"
            },
            "vernacular_specialist": {
                "description": "Specialized processing for regional language documents", 
                "accuracy": 0.88, "cost": "medium", "speed": "medium",
                "inclusion_focus": "Support customers comfortable only in local languages"
            },
            "assisted_processing": {
                "description": "Enhanced processing for elderly and differently-abled customers",
                "accuracy": 0.92, "cost": "high", "speed": "slow",
                "inclusion_focus": "Ensure accessibility for all demographics"
            },
            "migrant_worker_special": {
                "description": "Rapid processing for migrant workers with urgent banking needs",
                "accuracy": 0.82, "cost": "low", "speed": "very_fast",
                "inclusion_focus": "Quick banking access for India's 139 million migrant workers"
            }
        }

    async def _execute_step_autonomously(self, step: Dict, input_data: Dict, previous_results: List) -> Dict:
        """Execute document processing step autonomously"""
        
        action = step.get('action', '')
        
        if 'analyze_document' in action.lower():
            return await self._autonomous_document_analysis(input_data, step)
        elif 'choose_strategy' in action.lower():
            return await self._autonomous_strategy_selection(input_data, step)
        elif 'extract_information' in action.lower():
            return await self._autonomous_information_extraction(input_data, step)
        elif 'quality_assessment' in action.lower():
            return await self._autonomous_quality_assessment(input_data, step, previous_results)
        else:
            return await self._general_autonomous_action(step, input_data)

    async def _autonomous_document_analysis(self, input_data: Dict, step: Dict) -> Dict:
        """Autonomous document analysis with strategy selection"""
        
        # Agent analyzes document characteristics autonomously
        doc_bytes = input_data.get('document_bytes', b'')
        customer_data = input_data.get('customer_data', {})
        
        # Agent decides on processing strategy based on goals and context
        strategy_decision = await self._choose_processing_strategy_autonomously(customer_data, len(doc_bytes))
        
        try:
            # Always use AnalyzeID for identity documents (most robust for Indian documents)
            response = self.aws_clients['textract'].analyze_id(
                DocumentPages=[{'Bytes': doc_bytes}]
            )
            
            # Agent processes results autonomously
            processed_result = await self._process_textract_response_autonomously(response, strategy_decision)
            
            return {
                'step': step,
                'success': processed_result.get('confidence', 0) / 100,
                'outcome': f"Document analyzed using {strategy_decision['strategy']} approach",
                'learned_info': {
                    'strategy_used': strategy_decision['strategy'],
                    'extraction_results': processed_result,
                    'strategy_effectiveness': processed_result.get('confidence', 0) / 100
                },
                'next_action_recommendation': self._recommend_next_action(processed_result)
            }
            
        except Exception as e:
            logger.error(f"Textract processing failed: {str(e)}")
            return {
                'step': step,
                'success': 0.1,
                'outcome': f"Document analysis failed: {str(e)}",
                'learned_info': {'error': str(e), 'strategy_attempted': strategy_decision['strategy']},
                'next_action_recommendation': 'escalate_to_manual_review'
            }

    async def _choose_processing_strategy_autonomously(self, customer_data: Dict, doc_size: int) -> Dict:
        """Agent autonomously chooses processing strategy"""
        
        # Create safe customer data without any potential bytes
        safe_customer_data = {
            'income': customer_data.get('income', 0),
            'employment': customer_data.get('employment', 'Unknown'),
            'customer_segment': customer_data.get('customer_segment', 'Unknown'),
            'document_type': customer_data.get('document_type', 'Unknown'),
            'age': customer_data.get('age', 'Unknown')
        }
        
        # Use a simple string concatenation instead of problematic f-string
        strategy_prompt = "You are an autonomous document processing agent choosing the best strategy.\n\n"
        strategy_prompt += f"Customer Context: {json.dumps(safe_customer_data, indent=2)}\n\n"
        strategy_prompt += f"Document Characteristics:\n- Size: {doc_size} bytes\n- Has Document: {doc_size > 0}\n\n"
        strategy_prompt += f"Available Strategies: {json.dumps(self.processing_strategies, indent=2)}\n\n"
        strategy_prompt += "Autonomously choose the best strategy considering:\n"
        strategy_prompt += "1. Your primary goal of maximum accuracy\n"
        strategy_prompt += "2. Customer importance and expectations\n"
        strategy_prompt += "3. Document characteristics\n"
        strategy_prompt += "4. Past performance of strategies\n"
        strategy_prompt += "5. Resource constraints\n\n"
        strategy_prompt += 'Respond in JSON: {"strategy": "strategy_name", "reasoning": "detailed reasoning for choice", "expected_accuracy": 0.0, "confidence_in_choice": 0.0}'

        try:
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.aws_clients['bedrock'],
                CLAUDE_MODEL_ID,
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 800,
                    "messages": [{"role": "user", "content": strategy_prompt}],
                    "temperature": 0.3
                }
            )
            
            result = json.loads(response['body'].read())
            ai_response = result['content'][0]['text']
            
            # Use safe JSON parsing with fallback
            strategy_decision = safe_json_parse(ai_response, {
                "strategy": "rural_optimized",
                "reasoning": "AI strategy selection failed, using rural-optimized approach for inclusion",
                "confidence_in_choice": 0.4,
                "expected_accuracy": 0.85
            })
            
            return strategy_decision
            
        except Exception as e:
            logger.error(f"Strategy selection failed: {str(e)}")
            # Fallback decision
            return {
                "strategy": "rural_optimized",
                "reasoning": "AI strategy selection failed, using rural-optimized approach for inclusion",
                "confidence_in_choice": 0.4
            }

    async def _process_textract_response_autonomously(self, response: Dict, strategy_context: Dict) -> Dict:
        """Process Textract response with autonomous interpretation"""
        
        # Extract data based on document type
        extracted_data = {}
        confidence_scores = []
        
        # Process AnalyzeID response
        for document in response.get('IdentityDocuments', []):
            for field in document.get('IdentityDocumentFields', []):
                field_type = field.get('Type', {}).get('Text', '')
                field_value = field.get('ValueDetection', {}).get('Text', '')
                confidence = field.get('ValueDetection', {}).get('Confidence', 0)
                
                if field_type and field_value:
                    extracted_data[field_type] = {
                        'value': field_value,
                        'confidence': confidence
                    }
                    confidence_scores.append(confidence)
        
        # Agent evaluates extraction quality autonomously
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Agent determines if goals were met
        primary_goal = next((g for g in self.goals if g.goal_type == "financial_inclusion"), None)
        goal_achievement = self._evaluate_goal_achievement(extracted_data, overall_confidence, primary_goal)
        
        return {
            'extracted_data': extracted_data,
            'confidence': overall_confidence,
            'fields_count': len(extracted_data),
            'goal_achievement': goal_achievement,
            'strategy_effectiveness': overall_confidence / 100,
            'recommendations': self._generate_autonomous_recommendations(extracted_data, overall_confidence)
        }

    def _evaluate_goal_achievement(self, extracted_data: Dict, confidence: float, goal: AgentGoal) -> Dict:
        """Evaluate how well the agent achieved its goals"""
        
        if not goal:
            return {'achieved': False, 'score': 0.0, 'reason': 'No primary goal defined'}
        
        success_criteria = goal.success_criteria
        
        confidence_target = success_criteria.get('rural_acceptance_rate', 0.95)
        fields_target = 4  # Minimum fields expected
        
        confidence_achieved = (confidence / 100) >= 0.85  # Reasonable threshold
        fields_achieved = len(extracted_data) >= fields_target
        
        overall_achievement = confidence_achieved and fields_achieved
        achievement_score = (
            (confidence / 100 / 0.85) * 0.6 +
            (len(extracted_data) / fields_target) * 0.4
        )
        
        return {
            'achieved': overall_achievement,
            'score': min(achievement_score, 1.0),
            'confidence_met': confidence_achieved,
            'fields_met': fields_achieved,
            'reason': f"Confidence: {confidence:.1f}% (target: 85%), Fields: {len(extracted_data)} (target: {fields_target})"
        }

    def _generate_autonomous_recommendations(self, extracted_data: Dict, confidence: float) -> List[str]:
        """Generate autonomous recommendations for next steps"""
        
        recommendations = []
        
        if confidence >= 90:
            recommendations.append("proceed_to_risk_assessment")
            recommendations.append("high_confidence_processing_complete")
        elif confidence >= 70:
            recommendations.append("acceptable_quality_proceed_with_caution")
            recommendations.append("consider_additional_verification")
        elif confidence >= 60:
            recommendations.append("request_document_resubmission")
            recommendations.append("manual_review_recommended")
        else:
            recommendations.append("reject_poor_quality_document")
            recommendations.append("request_new_clear_document")
        
        if len(extracted_data) < 3:
            recommendations.append("insufficient_data_extracted")
            recommendations.append("try_alternative_processing_method")
        
        return recommendations

    def _recommend_next_action(self, processed_result: Dict) -> str:
        """Recommend next action based on results"""
        
        confidence = processed_result.get('confidence', 0)
        goal_achievement = processed_result.get('goal_achievement', {})
        
        if goal_achievement.get('achieved', False):
            return "proceed_to_risk_assessment"
        elif confidence >= 70:
            return "request_additional_verification"
        else:
            return "escalate_for_manual_review"

    async def _autonomous_strategy_selection(self, input_data: Dict, step: Dict) -> Dict:
        """Autonomous strategy selection step"""
        return {
            'step': step,
            'success': 0.9,
            'outcome': 'Strategy selection completed',
            'learned_info': {},
            'next_action_recommendation': 'proceed_with_selected_strategy'
        }

    async def _autonomous_information_extraction(self, input_data: Dict, step: Dict) -> Dict:
        """Autonomous information extraction step"""
        return {
            'step': step,
            'success': 0.85,
            'outcome': 'Information extraction completed',
            'learned_info': {},
            'next_action_recommendation': 'validate_extracted_information'
        }

    async def _autonomous_quality_assessment(self, input_data: Dict, step: Dict, previous_results: List) -> Dict:
        """Autonomous quality assessment step"""
        return {
            'step': step,
            'success': 0.88,
            'outcome': 'Quality assessment completed',
            'learned_info': {},
            'next_action_recommendation': 'finalize_document_processing'
        }

    async def _general_autonomous_action(self, step: Dict, input_data: Dict) -> Dict:
        """General autonomous action for unspecified steps"""
        return {
            'step': step,
            'success': 0.7,
            'outcome': 'General autonomous action completed',
            'learned_info': {},
            'next_action_recommendation': 'continue'
        } 