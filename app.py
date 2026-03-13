"""ASP Decision Intelligence Platform - Main Streamlit Application."""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import timedelta
from data.asp_data import generate_asp_profiles, generate_historical_performance
from modules.module1_bayesian import BayesianASPScorer
from utils.visualization import (
    plot_asp_scores_with_uncertainty,
    plot_metric_distributions,
    plot_performance_comparison,
    plot_data_sufficiency,
    plot_bayesian_vs_simple_average,
    plot_posterior_distributions
)

st.set_page_config(page_title="ASP Decision Intelligence", layout="wide")

st.title("🎯 ASP Decision Intelligence Platform")
st.markdown("**Demonstrating Decision Intelligence for Authorized Service Provider Selection**")

# Sidebar
st.sidebar.header("Configuration")
module = st.sidebar.selectbox(
    "Select Module",
    ["Module 1: Bayesian Analytics", 
     "Module 2: Causal Inference (Coming Soon)",
     "Module 3: Reinforcement Learning (Coming Soon)",
     "Module 4: Multi-Agent System (Coming Soon)"]
)

# Generate data
if 'data_generated' not in st.session_state:
    start_time = time.time()
    with st.spinner("Generating sample data..."):
        st.session_state.asp_profiles = generate_asp_profiles(n_asps=3)
        # Different data volumes per ASP to demonstrate uncertainty handling
        st.session_state.historical_data = generate_historical_performance(
            st.session_state.asp_profiles, 
            n_tasks_per_asp={'ASP_A': 30, 'ASP_B': 15, 'ASP_C': 5}  # Varying data volumes
        )
        st.session_state.data_generated = True
    elapsed = time.time() - start_time
    st.session_state.data_gen_time = str(timedelta(seconds=int(elapsed)))

# Module 1: Bayesian Analytics
if module == "Module 1: Bayesian Analytics":
    st.header("📊 Module 1: Bayesian Analytics")
    
    st.info("🔑 **Key Insight**: Bayesian methods quantify uncertainty in ASP performance predictions, helping you make confident decisions even with limited data.")
    
    st.markdown("""
    **Key Concept**: Use Bayesian inference to score ASPs while quantifying uncertainty.
    
    **Why Bayesian?**
    - Handles incomplete data gracefully
    - Provides probability distributions, not just point estimates
    - Naturally incorporates prior knowledge
    - Quantifies uncertainty in predictions
    """)
    
    # Show data overview
    with st.expander("📁 View Historical Data (INPUT: Prior Knowledge)"):
        st.caption("📥 **INPUT**: Historical performance data used as evidence for Bayesian inference. This represents your prior knowledge about ASP performance.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ASP Profiles")
            st.dataframe(st.session_state.asp_profiles, use_container_width=True)
        
        with col2:
            st.subheader("Performance Summary")
            summary = st.session_state.historical_data.groupby('asp_id').agg({
                'success': ['mean', 'count'],
                'response_time_hours': 'mean',
                'customer_satisfaction': 'mean'
            }).round(3)
            st.dataframe(summary, use_container_width=True)
        
        st.plotly_chart(
            plot_performance_comparison(st.session_state.historical_data),
            use_container_width=True
        )
        
        st.plotly_chart(
            plot_data_sufficiency(st.session_state.historical_data),
            use_container_width=True
        )
    
    # Model configuration
    st.subheader("⚙️ Model Configuration (INPUT: Hyperparameters)")
    st.caption("📥 **INPUT**: Hyperparameters that control how different metrics are weighted in the final score.")
    
    st.markdown("""
    **Configure how different performance metrics are weighted in the final ASP score:**
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Success Rate Weight**")
        st.caption("How important is task completion success? (0.0 = not important, 1.0 = most important)")
        weight_success = st.slider("Success Rate", 0.0, 1.0, 0.4, 0.05, key='slider_success',
                                   label_visibility='collapsed')
    with col2:
        st.markdown("**Response Time Weight**")
        st.caption("How important is fast response? (0.0 = speed doesn't matter, 1.0 = speed is critical)")
        weight_response = st.slider("Response Time", 0.0, 1.0, 0.3, 0.05, key='slider_response',
                                    label_visibility='collapsed')
    with col3:
        st.markdown("**Satisfaction Weight**")
        st.caption("How important is customer satisfaction? (0.0 = ignore feedback, 1.0 = prioritize satisfaction)")
        weight_satisfaction = st.slider("Satisfaction", 0.0, 1.0, 0.3, 0.05, key='slider_satisfaction',
                                       label_visibility='collapsed')
    
    # Track slider changes
    current_weights = (weight_success, weight_response, weight_satisfaction)
    if 'previous_weights' not in st.session_state:
        st.session_state.previous_weights = current_weights
        st.session_state.slider_start_time = time.time()
    
    if current_weights != st.session_state.previous_weights:
        elapsed = time.time() - st.session_state.slider_start_time
        st.caption(f"⏱️ Configuration updated in {str(timedelta(seconds=int(elapsed)))}")
        st.session_state.previous_weights = current_weights
        st.session_state.slider_start_time = time.time()
    
    total_weight = weight_success + weight_response + weight_satisfaction
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum to {total_weight:.2f}. They will be normalized to 1.0")
        weight_success /= total_weight
        weight_response /= total_weight
        weight_satisfaction /= total_weight
    
    weights = {
        'success_rate': weight_success,
        'response_time': weight_response,
        'satisfaction': weight_satisfaction
    }
    
    # Run Bayesian model
    if st.button("🚀 Run Bayesian Analysis", type="primary"):
        start_time = time.time()
        with st.spinner("Running Bayesian inference (MCMC sampling)..."):
            scorer = BayesianASPScorer()
            scorer.fit(st.session_state.historical_data, n_samples=500)
            st.session_state.bayesian_scores = scorer.score_asps(weights)
            st.session_state.scorer = scorer
        elapsed = time.time() - start_time
        st.session_state.analysis_time = str(timedelta(seconds=int(elapsed)))
        st.success(f"✅ Analysis complete! ⏱️ Time: {st.session_state.analysis_time}")
    
    # Display results
    if 'bayesian_scores' in st.session_state:
        st.subheader("📈 Results (OUTPUT)")
        st.caption("📤 **OUTPUT**: Posterior distributions from Bayesian inference - these are the model's predictions with uncertainty quantification.")
        
        # Bayesian vs Simple Average Comparison
        st.markdown("### 🎯 Bayesian Value Demonstration: vs Simple Averages")
        st.info("**Key Insight**: Bayesian estimates are similar to simple averages BUT provide uncertainty quantification. Notice how ASPs with less data (ASP_C: 5 tasks) have wider uncertainty than those with more data (ASP_A: 30 tasks).")
        st.plotly_chart(
            plot_bayesian_vs_simple_average(st.session_state.bayesian_scores, st.session_state.historical_data),
            use_container_width=True
        )
        
        # Overall scores
        st.markdown("### ASP Bayesian Scores with Uncertainty (OUTPUT: Sampled Posterior)")
        st.caption("📤 **OUTPUT**: Posterior probability distributions sampled via MCMC. Each score represents the mean of the posterior, with error bars showing 95% credible intervals.")
        st.plotly_chart(
            plot_asp_scores_with_uncertainty(st.session_state.bayesian_scores),
            use_container_width=True
        )
        
        # Full Posterior Distributions
        st.markdown("### 📊 Full Posterior Distributions (Complete Uncertainty View)")
        st.caption("📤 **OUTPUT**: Complete probability distributions showing all 500 MCMC samples. This is what Bayesian gives you that simple averages cannot.")
        
        col1, col2 = st.columns(2)
        with col1:
            dist_asp = st.selectbox("Select ASP", st.session_state.bayesian_scores['asp_id'].tolist(), key='dist_asp')
        with col2:
            dist_metric = st.selectbox("Select Metric", 
                                      ["success_rate", "response_time", "satisfaction"],
                                      format_func=lambda x: {
                                          "success_rate": "Success Rate",
                                          "response_time": "Response Time",
                                          "satisfaction": "Satisfaction"
                                      }[x],
                                      key='dist_metric')
        
        st.plotly_chart(
            plot_posterior_distributions(st.session_state.scorer, dist_asp, dist_metric),
            use_container_width=True
        )
        
        # Detailed metrics
        st.subheader("Detailed Metric Analysis (OUTPUT: Posterior Distributions)")
        st.caption("📤 **OUTPUT**: Individual metric posteriors showing uncertainty in each performance dimension.")
        
        metric_choice = st.selectbox(
            "Select Metric to Visualize",
            ["success_rate", "response_time", "satisfaction"],
            format_func=lambda x: {
                "success_rate": "Success Rate (probability, 0-1)",
                "response_time": "Response Time (hours)",
                "satisfaction": "Customer Satisfaction (1-5 scale)"
            }[x]
        )
        
        st.plotly_chart(
            plot_metric_distributions(st.session_state.bayesian_scores, metric_choice),
            use_container_width=True
        )
        
        # Scores table
        st.subheader("ASP Scores Table (OUTPUT: Summary Statistics)")
        st.caption("📤 **OUTPUT**: Posterior means and 95% credible intervals for all metrics.")
        display_df = st.session_state.bayesian_scores.copy()
        
        # Rename columns with units
        display_df = display_df.rename(columns={
            'success_rate_mean': 'Success Rate (probability)',
            'response_time_mean': 'Response Time (hours)',
            'satisfaction_mean': 'Satisfaction (1-5 scale)'
        })
        
        display_df['success_rate_ci'] = display_df['success_rate_ci'].apply(
            lambda x: f"[{x[0]:.3f}, {x[1]:.3f}]"
        )
        display_df['response_time_ci'] = display_df['response_time_ci'].apply(
            lambda x: f"[{x[0]:.2f}h, {x[1]:.2f}h]"
        )
        display_df['satisfaction_ci'] = display_df['satisfaction_ci'].apply(
            lambda x: f"[{x[0]:.2f}, {x[1]:.2f}]"
        )
        
        # Select and reorder columns
        display_cols = ['asp_id', 'score', 'uncertainty', 
                       'Success Rate (probability)', 'success_rate_ci',
                       'Response Time (hours)', 'response_time_ci',
                       'Satisfaction (1-5 scale)', 'satisfaction_ci']
        
        st.dataframe(
            display_df[display_cols].style.background_gradient(subset=['score'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Recommendation
        best_asp = st.session_state.bayesian_scores.iloc[0]
        asp_profile = st.session_state.asp_profiles[st.session_state.asp_profiles['asp_id']==best_asp['asp_id']]
        specialization = asp_profile['specialization'].values[0] if 'specialization' in asp_profile.columns else 'general work'
        
        st.success(f"""
        **🏆 Recommended ASP: {best_asp['asp_id']}** ({specialization})
        - Score: {best_asp['score']:.3f} ± {best_asp['uncertainty']:.3f}
        - Success Rate: {best_asp['success_rate_mean']:.1%}
        - Avg Response Time: {best_asp['response_time_mean']:.1f} hours
        - Customer Satisfaction: {best_asp['satisfaction_mean']:.2f}/5
        """)
        
        # Insights
        with st.expander("💡 Key Insights (Dynamic - Based on Current Results)"):
            top_asp = st.session_state.bayesian_scores.iloc[0]
            second_asp = st.session_state.bayesian_scores.iloc[1] if len(st.session_state.bayesian_scores) > 1 else None
            third_asp = st.session_state.bayesian_scores.iloc[2] if len(st.session_state.bayesian_scores) > 2 else None
            
            # Get actual specializations
            def get_specialization(asp_id):
                asp_prof = st.session_state.asp_profiles[st.session_state.asp_profiles['asp_id']==asp_id]
                return asp_prof['specialization'].values[0] if 'specialization' in asp_prof.columns else 'N/A'
            
            st.markdown(f"""
            **Bayesian Analytics Results Summary:**
            
            **1. Current Model Configuration (Hyperparameters):**
            - Success Rate Weight: **{weights['success_rate']:.1%}** - {"🔴 High priority" if weights['success_rate'] > 0.4 else "🟡 Moderate priority" if weights['success_rate'] > 0.2 else "⚪ Low priority"}
            - Response Time Weight: **{weights['response_time']:.1%}** - {"🔴 High priority" if weights['response_time'] > 0.4 else "🟡 Moderate priority" if weights['response_time'] > 0.2 else "⚪ Low priority"}
            - Customer Satisfaction Weight: **{weights['satisfaction']:.1%}** - {"🔴 High priority" if weights['satisfaction'] > 0.4 else "🟡 Moderate priority" if weights['satisfaction'] > 0.2 else "⚪ Low priority"}
            
            **2. ASP Rankings (Posterior Means from MCMC Sampling):**
            
            🥇 **1st Place: {top_asp['asp_id']}** - {get_specialization(top_asp['asp_id'])}
            - Overall Score: **{top_asp['score']:.3f}** ± {top_asp['uncertainty']:.3f}
            - Success Rate: **{top_asp['success_rate_mean']:.1%}** (95% CI: [{top_asp['success_rate_ci'][0]:.1%}, {top_asp['success_rate_ci'][1]:.1%}])
            - Response Time: **{top_asp['response_time_mean']:.1f} hours** (95% CI: [{top_asp['response_time_ci'][0]:.1f}h, {top_asp['response_time_ci'][1]:.1f}h])
            - Satisfaction: **{top_asp['satisfaction_mean']:.2f}/5** (95% CI: [{top_asp['satisfaction_ci'][0]:.2f}, {top_asp['satisfaction_ci'][1]:.2f}])
            
            {f'''🥈 **2nd Place: {second_asp['asp_id']}** - {get_specialization(second_asp['asp_id'])}
            - Overall Score: **{second_asp['score']:.3f}** ± {second_asp['uncertainty']:.3f}
            - Success Rate: **{second_asp['success_rate_mean']:.1%}** (95% CI: [{second_asp['success_rate_ci'][0]:.1%}, {second_asp['success_rate_ci'][1]:.1%}])
            - Response Time: **{second_asp['response_time_mean']:.1f} hours** (95% CI: [{second_asp['response_time_ci'][0]:.1f}h, {second_asp['response_time_ci'][1]:.1f}h])
            - Satisfaction: **{second_asp['satisfaction_mean']:.2f}/5** (95% CI: [{second_asp['satisfaction_ci'][0]:.2f}, {second_asp['satisfaction_ci'][1]:.2f}])''' if second_asp is not None else ""}
            
            {f'''🥉 **3rd Place: {third_asp['asp_id']}** - {get_specialization(third_asp['asp_id'])}
            - Overall Score: **{third_asp['score']:.3f}** ± {third_asp['uncertainty']:.3f}
            - Success Rate: **{third_asp['success_rate_mean']:.1%}** (95% CI: [{third_asp['success_rate_ci'][0]:.1%}, {third_asp['success_rate_ci'][1]:.1%}])
            - Response Time: **{third_asp['response_time_mean']:.1f} hours** (95% CI: [{third_asp['response_time_ci'][0]:.1f}h, {third_asp['response_time_ci'][1]:.1f}h])
            - Satisfaction: **{third_asp['satisfaction_mean']:.2f}/5** (95% CI: [{third_asp['satisfaction_ci'][0]:.2f}, {third_asp['satisfaction_ci'][1]:.2f}])''' if third_asp is not None else ""}
            
            **3. Uncertainty Quantification:**
            - Highest uncertainty: **{st.session_state.bayesian_scores.loc[st.session_state.bayesian_scores['uncertainty'].idxmax(), 'asp_id']}** (±{st.session_state.bayesian_scores['uncertainty'].max():.3f}) - less reliable data
            - Lowest uncertainty: **{st.session_state.bayesian_scores.loc[st.session_state.bayesian_scores['uncertainty'].idxmin(), 'asp_id']}** (±{st.session_state.bayesian_scores['uncertainty'].min():.3f}) - more reliable data
            
            **4. ASP Specialization Context:**
            - **ASP_A**: Mountain operations - moderate success, slower response due to terrain challenges
            - **ASP_B**: Standard urban tasks - high success on simple work, fast response, struggles with high complexity
            - **ASP_C**: High-risk climbing with OHS certification - handles extreme weather (wind/rain/snow), variable performance
            
            **5. Business Recommendation:**
            Choose **{top_asp['asp_id']}** for tasks matching their specialization: *{get_specialization(top_asp['asp_id'])}*
            
            **Next Steps:**
            - Module 2: Causal inference to understand *why* performance differs (e.g., weather impact on ASP_C)
            - Module 3: Reinforcement learning to optimize ASP selection over time
            - Module 4: Multi-agent negotiation for complex multi-objective scenarios
            """)
        
        # Continuous Learning Simulator
        st.markdown("---")
        st.subheader("🔄 Continuous Learning Simulator")
        st.info("**Bayesian Value #3**: Watch how posteriors update as new data arrives. This demonstrates continuous learning without retraining.")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sim_asp = st.selectbox("Select ASP", st.session_state.bayesian_scores['asp_id'].tolist(), key='sim_asp')
        with col2:
            sim_success = st.selectbox("Task Success?", [True, False], format_func=lambda x: "✅ Success" if x else "❌ Failure")
        with col3:
            sim_response = st.number_input("Response Time (hours)", min_value=0.5, max_value=24.0, value=4.0, step=0.5)
        with col4:
            sim_satisfaction = st.slider("Satisfaction", 1.0, 5.0, 3.5, 0.5)
        
        if st.button("➕ Add New Task & Update Posterior", type="primary"):
            # Add new task to historical data
            new_task = pd.DataFrame([{
                'asp_id': sim_asp,
                'task_id': f"{sim_asp}_NEW_{len(st.session_state.historical_data)}",
                'complexity': 'Medium',
                'success': sim_success,
                'response_time_hours': sim_response,
                'cost': 1500.0,
                'customer_satisfaction': sim_satisfaction,
                'sla_met': sim_response < 24 and sim_success
            }])
            
            st.session_state.historical_data = pd.concat([st.session_state.historical_data, new_task], ignore_index=True)
            
            # Re-run Bayesian inference with updated data
            with st.spinner("Updating posterior with new evidence..."):
                scorer = BayesianASPScorer()
                scorer.fit(st.session_state.historical_data, n_samples=500)
                st.session_state.bayesian_scores = scorer.score_asps(weights)
                st.session_state.scorer = scorer
            
            st.success(f"✅ Added new task for {sim_asp}! Posterior updated. Notice how uncertainty changes.")
            st.rerun()

else:
    st.info("🚧 This module is under development. Stay tuned!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**About**")
st.sidebar.markdown("""
This platform demonstrates progressive decision intelligence concepts:
1. Bayesian Analytics
2. Causal Inference
3. Reinforcement Learning
4. Multi-Agent Systems
""")
