"""
UI components for the Banking AI System
"""

import streamlit as st
from typing import Dict


def display_true_autonomy_results(result: Dict):
    """Display results showing true agent autonomy"""
    
    st.markdown("---")
    st.header("🧠 True Agentic AI Results")
    
    if not result:
        st.error("❌ No results to display")
        return
    
    final_decision = result.get('final_decision', {})
    autonomy_metrics = result.get('autonomy_metrics', {})
    
    # Main status
    status = final_decision.get('final_status', 'unknown')
    if status == 'approved':
        st.success("🎉 Approved by Autonomous AI Agents!")
        st.balloons()
    elif status == 'rejected':
        st.error("❌ Rejected by Autonomous AI Agents")
    else:
        st.warning("⏳ Autonomous Agents Recommend Manual Review")
    
    # Autonomy Quality Metrics
    st.subheader("🧠 Agent Autonomy Quality")
    autonomy_quality = final_decision.get('autonomy_quality', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        doc_autonomy = autonomy_quality.get('document_agent_autonomy', 0.5)
        st.metric("Document Agent Autonomy", f"{doc_autonomy:.1%}")
    with col2:
        risk_autonomy = autonomy_quality.get('risk_agent_autonomy', 0.5)
        st.metric("Risk Agent Autonomy", f"{risk_autonomy:.1%}")
    with col3:
        coord_autonomy = autonomy_quality.get('coordination_autonomy', 0.5)
        st.metric("Coordination Autonomy", f"{coord_autonomy:.1%}")
    
    # Agent Learning and Adaptation
    st.subheader("📚 Agent Learning & Adaptation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Document Agent Autonomy:**")
        doc_metrics = autonomy_metrics.get('document_agent_autonomy', {})
        st.write(f"• Learning Instances: {doc_metrics.get('learning_instances', 0)}")
        st.write(f"• Adaptations Made: {doc_metrics.get('adaptations_count', 0)}")
        st.write(f"• Negotiations: {doc_metrics.get('negotiation_instances', 0)}")
        st.write(f"• Decisions Made: {doc_metrics.get('decisions_made', 0)}")
    
    with col2:
        st.write("**Risk Agent Autonomy:**")
        risk_metrics = autonomy_metrics.get('risk_agent_autonomy', {})
        st.write(f"• Learning Instances: {risk_metrics.get('learning_instances', 0)}")
        st.write(f"• Adaptations Made: {risk_metrics.get('adaptations_count', 0)}")
        st.write(f"• Negotiations: {risk_metrics.get('negotiation_instances', 0)}")
        st.write(f"• Decisions Made: {risk_metrics.get('decisions_made', 0)}")
    
    # Overall System Autonomy
    system_autonomy = autonomy_metrics.get('system_autonomy_score', 0.5)
    st.metric("🎯 Overall System Autonomy Score", f"{system_autonomy:.1%}")
    
    if system_autonomy > 0.8:
        st.success("🧠 High autonomy - Agents are truly learning and adapting!")
    elif system_autonomy > 0.5:
        st.info("🤖 Moderate autonomy - Agents are developing autonomous behavior")
    else:
        st.warning("📝 Building autonomy - Agents are starting to learn")
    
    # Learning Outcomes
    learning_outcomes = final_decision.get('learning_outcomes', [])
    if learning_outcomes:
        st.subheader("📖 System Learning Outcomes")
        for outcome in learning_outcomes:
            st.write(f"• {outcome}")
    
    # Next Steps
    next_steps = final_decision.get('next_steps', [])
    if next_steps:
        st.subheader("📝 Autonomous Next Steps")
        for step in next_steps:
            st.write(f"• {step}")
    
    # Show detailed agent results
    with st.expander("🔍 Detailed Agent Analysis"):
        st.json(result) 