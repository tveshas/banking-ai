"""
Autonomous Customer Segmentation for Indian Banking
AI Agent intelligently determines rural/urban classification using AWS Bedrock
"""

import json
import asyncio
from typing import Dict, List
from config import logger, CLAUDE_MODEL_ID, bedrock_api_call_with_retry
from utils.aws_clients import get_aws_clients


class AutonomousCustomerSegmentation:
    """
    Truly autonomous customer segmentation using AI intelligence
    The agent figures out rural/urban classification on its own
    """
    
    def __init__(self, aws_clients: Dict = None):
        self.aws_clients = aws_clients or get_aws_clients()
        self.bedrock_runtime = self.aws_clients.get('bedrock_runtime') if self.aws_clients else None
        self.process_log = []  # Track the entire process
    
    async def autonomous_segmentation(self, pincode: str = None, income: int = 0, 
                                     process_callback=None, **kwargs) -> Dict:
        """
        Let the AI agent autonomously determine customer segment with full process tracking
        """
        
        # Initialize process tracking
        self.process_log = []
        self._log_process("🚀 Starting Autonomous Customer Segmentation", process_callback)
        self._log_process(f"📍 Input Data: Pincode={pincode}, Income=₹{income:,}", process_callback)
        
        # Check AWS Bedrock availability
        if not self.bedrock_runtime:
            self._log_process("⚠️ AWS Bedrock unavailable - switching to fallback mode", process_callback)
            return await self._fallback_with_process(pincode, income, process_callback)
        
        self._log_process("✅ AWS Bedrock connected - activating autonomous AI agent", process_callback)
        
        # Prepare autonomous analysis
        self._log_process("🧠 AI Agent: Analyzing Indian geographic and economic patterns", process_callback)
        
        analysis_prompt = f"""
You are an autonomous banking AI agent specializing in Indian customer segmentation. 
Your goal is to intelligently classify customers as Rural, Urban, or Semi-Urban based on available data.

Customer Information:
- Pincode: {pincode or 'Not provided'}
- Annual Income: ₹{income:,}
- Additional Context: {kwargs}

CRITICAL PINCODE KNOWLEDGE - Use this to guide your analysis:

URBAN AREAS (Definite Urban Classification):
- Gurgaon/Gurugram (122xxx): Major financial hub, NCR, Fortune 500 companies
  * 122001-122050: Central Gurgaon, highly urban
  * 122018: South City II - Premium urban area
- Mumbai (400xxx): Financial capital
- Delhi (110xxx): National capital  
- Bangalore (560xxx): IT capital
- Chennai (600xxx): Major metro
- Hyderabad (500xxx): IT hub
- Pune (411xxx): Major city
- Kolkata (700xxx): Major metro
- Noida (201xxx): NCR IT hub
- Faridabad (121xxx): NCR industrial

SEMI-URBAN AREAS:
- Tier-2 cities: Chandigarh, Lucknow, Jaipur, Ahmedabad
- District headquarters with good infrastructure
- Industrial towns near metros

RURAL AREAS:
- Village pincodes (usually lower population density)
- Agricultural regions
- Remote/tribal areas

Task: Use your knowledge of Indian geography, economics, and demographics to autonomously determine:
1. Customer segment (Rural/Urban/Semi-Urban)
2. Confidence level (0.0 to 1.0) 
3. Your reasoning process
4. Banking recommendations

SPECIAL ATTENTION: If pincode starts with 122xxx (Gurgaon), classify as URBAN with high confidence.

Consider factors like:
- Specific pincode knowledge above
- Income levels typical for different regions
- Economic development patterns across India
- Infrastructure and connectivity indicators

Think autonomously and provide your intelligent analysis.

Respond in this exact JSON format:
{{
    "customer_segment": "Rural|Urban|Semi-Urban",
    "confidence": 0.85,
    "reasoning": "Detailed explanation of your autonomous analysis",
    "geographic_analysis": "What the pincode tells you about location",
    "economic_analysis": "What the income suggests about lifestyle/location",
    "banking_recommendations": ["rec1", "rec2", "rec3"]
}}
"""

        try:
            # Call autonomous AI agent
            self._log_process("🤖 Calling AWS Bedrock Claude AI agent for autonomous analysis", process_callback)
            response = await self._call_bedrock_ai(analysis_prompt, process_callback)
            
            # Parse agent's autonomous decision
            self._log_process("📊 AI Agent: Processing autonomous decision", process_callback)
            result = await self._parse_agent_response(response, pincode, income, process_callback)
            
            self._log_process(f"✅ Autonomous Analysis Complete: {result['customer_segment']} "
                            f"({result['confidence']:.0%} confidence)", process_callback)
            
            # Add process log to result
            result['process_log'] = self.process_log
            result['agent_status'] = 'fully_autonomous'
            
            return result
            
        except Exception as e:
            self._log_process(f"❌ AI Agent Error: {str(e)}", process_callback)
            self._log_process("🔄 Switching to fallback analysis", process_callback)
            return await self._fallback_with_process(pincode, income, process_callback)
    
    async def _call_bedrock_ai(self, prompt: str, process_callback=None) -> str:
        """Call AWS Bedrock for autonomous AI analysis with process tracking"""
        
        try:
            self._log_process("📡 Sending request to AWS Bedrock Claude model with retry protection", process_callback)
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Use retry mechanism for Bedrock API calls
            response = await bedrock_api_call_with_retry(
                self.bedrock_runtime,
                CLAUDE_MODEL_ID,
                request_body
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text']
            
            self._log_process(f"✅ AWS Bedrock Response Received: {len(ai_response)} characters", process_callback)
            self._log_process(f"🧠 AI Agent Reasoning Preview: {ai_response[:100]}...", process_callback)
            
            return ai_response
            
        except Exception as e:
            self._log_process(f"❌ AWS Bedrock Call Failed: {str(e)}", process_callback)
            logger.error(f"Bedrock AI call failed: {str(e)}")
            raise
    
    async def _parse_agent_response(self, ai_response: str, pincode: str, income: int, 
                                   process_callback=None) -> Dict:
        """Parse the autonomous agent's response with process tracking"""
        
        try:
            self._log_process("🔍 Parsing AI agent's autonomous decision", process_callback)
            
            # Clean and extract JSON from AI response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = ai_response[json_start:json_end]
            
            self._log_process("🧹 Cleaning JSON response from control characters", process_callback)
            # Clean any control characters that might cause JSON parsing issues
            json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
            
            self._log_process("📋 Validating AI agent's decision structure", process_callback)
            agent_decision = json.loads(json_str)
            
            # Validate agent's decision
            valid_segments = ['Rural', 'Urban', 'Semi-Urban']
            if agent_decision.get('customer_segment') not in valid_segments:
                raise ValueError(f"Invalid segment: {agent_decision.get('customer_segment')}")
            
            confidence = float(agent_decision.get('confidence', 0.5))
            if not 0.0 <= confidence <= 1.0:
                confidence = max(0.0, min(1.0, confidence))
            
            # CRITICAL: Override for known urban areas if AI misclassified
            original_segment = agent_decision['customer_segment']
            if pincode and self._is_definitely_urban_pincode(pincode):
                if original_segment != 'Urban':
                    self._log_process(f"🔧 CORRECTING: AI said {original_segment}, but {pincode} is definitely Urban", process_callback)
                    agent_decision['customer_segment'] = 'Urban'
                    confidence = max(0.85, confidence)  # High confidence for known urban areas
                    agent_decision['reasoning'] = f"Corrected from {original_segment} to Urban based on pincode knowledge: {pincode} is in Gurgaon NCR"
            
            self._log_process(f"✅ AI Decision Validated: {agent_decision['customer_segment']} "
                            f"with {confidence:.0%} confidence", process_callback)
            
            return {
                'customer_segment': agent_decision['customer_segment'],
                'confidence': round(confidence, 2),
                'pincode': pincode or 'Not provided',
                'income': income,
                'reasoning': agent_decision.get('reasoning', 'AI autonomous analysis'),
                'geographic_analysis': agent_decision.get('geographic_analysis', 'Location analysis'),
                'economic_analysis': agent_decision.get('economic_analysis', 'Income analysis'),
                'banking_recommendations': agent_decision.get('banking_recommendations', []),
                'classification_method': 'autonomous_ai_analysis',
                'agent_intelligence': 'aws_bedrock_claude',
                'raw_ai_response': ai_response[:500] + "..." if len(ai_response) > 500 else ai_response
            }
            
        except Exception as e:
            self._log_process(f"❌ Failed to parse AI response: {str(e)}", process_callback)
            logger.error(f"Failed to parse agent response: {str(e)}")
            logger.error(f"AI Response: {ai_response}")
            return await self._fallback_with_process(pincode, income, process_callback)
    
    async def _fallback_with_process(self, pincode: str, income: int, process_callback=None) -> Dict:
        """Fallback classification with full process tracking"""
        
        self._log_process("🔧 Activating Fallback Analysis Engine", process_callback)
        
        # First check: Pincode-based classification (overrides income)
        if pincode and self._is_definitely_urban_pincode(pincode):
            segment = 'Urban'
            confidence = 0.85
            reason = f"Pincode {pincode} is in a major urban area (Fallback classification)"
            self._log_process(f"📍 Pincode {pincode} identified as major urban area → Urban classification", process_callback)
        else:
            # Fallback to income-based classification
            self._log_process("📊 Analyzing income patterns for basic classification", process_callback)
            
            if income <= 300000:
                segment = 'Rural'
                confidence = 0.60
                reason = "Low income suggests rural customer (AI unavailable)"
                self._log_process(f"💰 Income ₹{income:,} ≤ ₹3,00,000 → Rural classification", process_callback)
            elif income >= 700000:
                segment = 'Urban'
                confidence = 0.60
                reason = "High income suggests urban customer (AI unavailable)"
                self._log_process(f"💰 Income ₹{income:,} ≥ ₹7,00,000 → Urban classification", process_callback)
            else:
                segment = 'Semi-Urban'
                confidence = 0.50
                reason = "Middle income - unclear without AI analysis"
                self._log_process(f"💰 Income ₹{income:,} in middle range → Semi-Urban classification", process_callback)
        
        self._log_process("🏦 Generating basic banking recommendations", process_callback)
        
        basic_recommendations = []
        if segment == 'Rural':
            basic_recommendations = ['Rural banking services', 'Agricultural loans', 'Micro-finance']
        elif segment == 'Urban':
            basic_recommendations = ['Premium banking', 'Investment products', 'Credit cards']
        else:
            basic_recommendations = ['Flexible banking options', 'Small business loans']
        
        self._log_process(f"✅ Fallback Analysis Complete: {segment} ({confidence:.0%} confidence)", process_callback)
        
        result = {
            'customer_segment': segment,
            'confidence': confidence,
            'pincode': pincode or 'Not provided',
            'income': income,
            'reasoning': reason,
            'geographic_analysis': 'Fallback mode - AI unavailable',
            'economic_analysis': f'Income-based classification: ₹{income:,}',
            'banking_recommendations': basic_recommendations,
            'classification_method': 'fallback_basic_rules',
            'agent_intelligence': 'fallback_mode',
            'process_log': self.process_log,
            'agent_status': 'fallback_only'
        }
        
        return result
    
    def _is_definitely_urban_pincode(self, pincode: str) -> bool:
        """Check if a pincode is definitely in a major urban area"""
        if not pincode:
            return False
        
        # Known major urban pincode patterns
        urban_patterns = [
            '122',  # Gurgaon/Gurugram (NCR)
            '121',  # Faridabad (NCR)
            '201',  # Noida (NCR)
            '110',  # Delhi
            '400',  # Mumbai
            '560',  # Bangalore
            '600',  # Chennai
            '500',  # Hyderabad
            '411',  # Pune
            '700',  # Kolkata
            '380',  # Ahmedabad
            '302',  # Jaipur
            '226',  # Lucknow
        ]
        
        # Check if pincode starts with any urban pattern
        for pattern in urban_patterns:
            if pincode.startswith(pattern):
                return True
        
        return False
    
    def _log_process(self, message: str, callback=None):
        """Log process step and optionally call callback for real-time updates"""
        timestamp = asyncio.get_event_loop().time()
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'step': len(self.process_log) + 1
        }
        self.process_log.append(log_entry)
        logger.info(f"Step {log_entry['step']}: {message}")
        
        # Call callback for real-time UI updates if provided
        if callback:
            callback(log_entry)


# Convenience function for easy usage with process tracking
async def get_customer_segment_autonomous(pincode: str = None, income: int = 0, 
                                        process_callback=None, **kwargs) -> Dict:
    """
    Autonomous AI-powered customer segment classification with full process visibility
    
    Args:
        pincode: 6-digit Indian pincode
        income: Annual income in INR
        process_callback: Function to call for real-time process updates
        **kwargs: Any other customer data for AI analysis
    
    Returns:
        Dict with autonomous AI segment classification and full process log
    """
    segmenter = AutonomousCustomerSegmentation()
    return await segmenter.autonomous_segmentation(
        pincode=pincode, income=income, process_callback=process_callback, **kwargs
    )


# Synchronous wrapper for Streamlit compatibility
def get_customer_segment(pincode: str = None, income: int = 0, process_callback=None, **kwargs) -> Dict:
    """
    Synchronous wrapper for Streamlit with process tracking
    """
    try:
        # Run the autonomous AI analysis with process tracking
        result = asyncio.run(get_customer_segment_autonomous(
            pincode=pincode, income=income, process_callback=process_callback, **kwargs
        ))
        return result
    except Exception as e:
        logger.error(f"Autonomous segmentation error: {str(e)}")
        # Return fallback result with error info
        segmenter = AutonomousCustomerSegmentation()
        fallback_result = asyncio.run(segmenter._fallback_with_process(pincode, income, process_callback))
        fallback_result['error'] = str(e)
        return fallback_result


# Example usage and testing
if __name__ == "__main__":
    # Test autonomous AI segmentation with process tracking
    def print_process(log_entry):
        print(f"  {log_entry['step']:2d}. {log_entry['message']}")
    
    test_cases = [
        {'pincode': '400001', 'income': 800000, 'name': 'Mumbai Test'},
        {'pincode': '261001', 'income': 200000, 'name': 'UP Rural Test'},
    ]
    
    print("Testing Autonomous AI Customer Segmentation with Full Process Tracking:")
    print("=" * 80)
    
    for case in test_cases:
        name = case.pop('name')
        print(f"\n🧪 {name}:")
        print("-" * 50)
        
        result = get_customer_segment(process_callback=print_process, **case)
        
        print(f"\n📊 Final Result:")
        print(f"   Segment: {result['customer_segment']} ({result['confidence']:.0%} confidence)")
        print(f"   Method: {result['classification_method']}")
        print(f"   Agent Status: {result.get('agent_status', 'unknown')}")
        print(f"   Total Steps: {len(result.get('process_log', []))}") 