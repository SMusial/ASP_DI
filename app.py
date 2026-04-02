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
    plot_posterior_distributions,
    plot_prior_distributions,
    plot_prior_vs_posterior
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
        st.session_state.asp_profiles = generate_asp_profiles(n_asps=6)
        # Different data volumes per ASP to demonstrate uncertainty handling
        st.session_state.historical_data = generate_historical_performance(
            st.session_state.asp_profiles, 
            n_tasks_per_asp={
                'ASP_Mount1': 14, 'ASP_Mount2': 8,   # Mountain operations
                'ASP_Std1': 12, 'ASP_Std2': 5,       # Standard urban
                'ASP_Climb1': 9, 'ASP_Climb2': 3     # High-risk climbing
            }
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
        
        st.info("""
        **🔑 Key Difference Explained:**
        
        **Simple Average (Gray Bars)** = Just add up all results and divide by count
        - Example: 5 tasks, 4 successful → 4/5 = 80% success rate
        - Problem: Doesn't tell you if this is reliable or just luck
        
        **Bayesian Mean (Blue Diamonds)** = Similar value BUT with uncertainty quantification
        - Same example: 4/5 = 80% (similar to simple average)
        - BUT Bayesian also calculates: "This 80% could really be anywhere from 60-90%" (shown in error bars)
        
        **Why are they SIMILAR but NOT IDENTICAL?**
        - Bayesian = Prior belief (orange curves below) + Data → Posterior
        - With **many tasks** (30): data dominates → Bayesian ≈ Simple Average
        - With **few tasks** (5): prior still has influence → Bayesian ≠ Simple Average
        - The error bars (mustaches) show how much uncertainty remains
        
        **Why This Matters:**
        - ASP with 100% success from 2 tasks → Simple average says "perfect!" 
        - Bayesian says "probably 50-95%, need more data" → safer decision
        """)
        
        st.plotly_chart(
            plot_prior_distributions(),
            use_container_width=True
        )
        st.caption("☝️ These are our **prior beliefs** before seeing any data. The Bayesian model combines these priors with the actual task data to produce the posterior (blue diamonds below).")
        
        st.plotly_chart(
            plot_bayesian_vs_simple_average(st.session_state.bayesian_scores, st.session_state.historical_data),
            use_container_width=True
        )
        
        st.markdown("### 📊 Prior vs Posterior — How Data Updated Our Beliefs")
        st.caption("Orange dashed = our initial beliefs (priors). Solid lines = updated beliefs after seeing data (posteriors). Notice how ASPs with more data have narrower, more confident posteriors.")
        st.plotly_chart(
            plot_prior_vs_posterior(st.session_state.scorer),
            use_container_width=True
        )
        
        # Overall scores
        st.markdown("### ASP Bayesian Scores with Uncertainty (OUTPUT: Sampled Posterior)")
        st.caption("📤 **OUTPUT**: Posterior probability distributions sampled via MCMC. Each score represents the mean of the posterior, with error bars showing 95% credible intervals.")
        st.warning(f"""
        **📐 How is the Score calculated?**
        
        Score = (Success Rate × {weights['success_rate']:.0%}) + (Response Time × {weights['response_time']:.0%}) + (Satisfaction × {weights['satisfaction']:.0%})
        
        It is a **weighted average** of three normalized metrics:
        - **Success Rate** (0-1): Used directly as probability
        - **Response Time**: Normalized as 1/(1 + hours/10) — lower time = higher score
        - **Satisfaction**: Normalized as rating/10 — higher rating = higher score
        
        Each metric is multiplied by its weight (set in Model Configuration above), then summed.
        """)
        st.plotly_chart(
            plot_asp_scores_with_uncertainty(st.session_state.bayesian_scores),
            use_container_width=True
        )
        
        # Full Posterior Distributions
        st.markdown("### 📊 Full Posterior Distributions (Complete Uncertainty View)")
        st.caption("📤 **OUTPUT**: Complete probability distributions showing all 500 MCMC samples. This is what Bayesian gives you that simple averages cannot.")
        
        # Single metric selector at the top
        col1, col2 = st.columns(2)
        with col1:
            metric_choice = st.selectbox(
                "Select Metric to Analyze",
                ["success_rate", "response_time", "satisfaction"],
                format_func=lambda x: {
                    "success_rate": "Success Rate (probability, 0-1)",
                    "response_time": "Response Time (hours)",
                    "satisfaction": "Customer Satisfaction (0-10 NPS)"
                }[x],
                key='unified_metric_selector'
            )
        with col2:
            dist_asp = st.selectbox("Select ASP", st.session_state.bayesian_scores['asp_id'].tolist(), key='dist_asp')
        
        # Show full distribution for selected ASP and metric
        st.plotly_chart(
            plot_posterior_distributions(st.session_state.scorer, dist_asp, metric_choice),
            use_container_width=True
        )
        
        # Detailed metrics comparison across all ASPs
        st.subheader("Detailed Metric Analysis Across All ASPs")
        st.caption("📤 **OUTPUT**: Compare the selected metric across all ASPs with uncertainty intervals.")
        
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
            'satisfaction_mean': 'Satisfaction (0-10 NPS)'
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
                       'Satisfaction (0-10 NPS)', 'satisfaction_ci']
        
        st.dataframe(
            display_df[display_cols].style.background_gradient(subset=['score'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Recommendation with CI-based risk analysis
        best_asp = st.session_state.bayesian_scores.iloc[0]
        asp_profile = st.session_state.asp_profiles[st.session_state.asp_profiles['asp_id']==best_asp['asp_id']]
        specialization = asp_profile['specialization'].values[0] if 'specialization' in asp_profile.columns else 'general work'
        
        st.success(f"""
        **🏆 Recommended ASP: {best_asp['asp_id']}** ({specialization})
        - Score: {best_asp['score']:.3f} ± {best_asp['uncertainty']:.3f}
        - Success Rate: {best_asp['success_rate_mean']:.1%}
        - Avg Response Time: {best_asp['response_time_mean']:.1f} hours
        - Customer Satisfaction: {best_asp['satisfaction_mean']:.2f}/10
        """)
        
        # Helper: CI-based risk analysis for a pair of ASPs
        def ci_risk_analysis(w, r):
            if r is None:
                return ""
            overlaps = []
            if r['success_rate_ci'][1] > w['success_rate_ci'][0]:
                overlaps.append(f"Success Rate: {r['asp_id']} best case ({r['success_rate_ci'][1]:.1%}) > {w['asp_id']} worst case ({w['success_rate_ci'][0]:.1%})")
            if r['response_time_ci'][0] < w['response_time_ci'][1]:
                overlaps.append(f"Response Time: {r['asp_id']} best case ({r['response_time_ci'][0]:.1f}h) < {w['asp_id']} worst case ({w['response_time_ci'][1]:.1f}h)")
            if r['satisfaction_ci'][1] > w['satisfaction_ci'][0]:
                overlaps.append(f"Satisfaction: {r['asp_id']} best case ({r['satisfaction_ci'][1]:.2f}) > {w['asp_id']} worst case ({w['satisfaction_ci'][0]:.2f})")
            if overlaps:
                overlap_text = "\n                - ".join(overlaps)
                return f"""
                
⚠️ **Risk Analysis (CI Overlap on {len(overlaps)} metric(s))**:
                The runner-up COULD outperform the winner in some scenarios:
                - {overlap_text}
                
🎯 **Decision Guidance**:
                - **Risk-averse** (worst-case): Consider {r['asp_id']} if its floor ({r['score'] - r['uncertainty']:.3f}) is acceptable
                - **Risk-neutral** (mean): Choose {w['asp_id']} ({w['score']:.3f} vs {r['score']:.3f})
                - **Action**: Collect more data to narrow CIs and increase decision confidence"""
            else:
                return f"""
                
✅ **Risk Analysis**: No CI overlap — {w['asp_id']} outperforms {r['asp_id']} even in worst-case. High-confidence decision."""
        
        # Helper: render category analysis as comparison table
        def render_category(cat_asps, cat_name, task_type):
            if len(cat_asps) < 2:
                return
            w = cat_asps.iloc[0]
            r = cat_asps.iloc[1]
            
            # Build comparison table
            def fmt_ci(ci):
                return f"[{ci[0]:.2f}, {ci[1]:.2f}]"
            def fmt_ci_pct(ci):
                return f"[{ci[0]:.1%}, {ci[1]:.1%}]"
            
            n_w = len(st.session_state.historical_data[st.session_state.historical_data['asp_id'] == w['asp_id']])
            n_r = len(st.session_state.historical_data[st.session_state.historical_data['asp_id'] == r['asp_id']])
            
            table_data = {
                'Metric': ['Tasks', 'Overall Score', 'Success Rate ↑', 'Response Time (h) ↓', 'Satisfaction ↑'],
                f"🥇 {w['asp_id']}": [
                    f"{n_w}",
                    f"{w['score']:.3f} ± {w['uncertainty']:.3f}",
                    f"{w['success_rate_mean']:.1%} {fmt_ci_pct(w['success_rate_ci'])}",
                    f"{w['response_time_mean']:.1f} {fmt_ci(w['response_time_ci'])}",
                    f"{w['satisfaction_mean']:.2f} {fmt_ci(w['satisfaction_ci'])}"
                ],
                f"🥈 {r['asp_id']}": [
                    f"{n_r}",
                    f"{r['score']:.3f} ± {r['uncertainty']:.3f}",
                    f"{r['success_rate_mean']:.1%} {fmt_ci_pct(r['success_rate_ci'])}",
                    f"{r['response_time_mean']:.1f} {fmt_ci(r['response_time_ci'])}",
                    f"{r['satisfaction_mean']:.2f} {fmt_ci(r['satisfaction_ci'])}"
                ],
                'Winner': [
                    f"{w['asp_id'] if n_w > n_r else r['asp_id']} (more data)",
                    f"{w['asp_id']} (+{w['score']-r['score']:.3f})",
                    f"{w['asp_id'] if w['success_rate_mean'] > r['success_rate_mean'] else r['asp_id']} (higher ↑ better)",
                    f"{w['asp_id'] if w['response_time_mean'] < r['response_time_mean'] else r['asp_id']} (lower ↓ better)",
                    f"{w['asp_id'] if w['satisfaction_mean'] > r['satisfaction_mean'] else r['asp_id']} (higher ↑ better)"
                ]
            }
            
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
            
            # Risk analysis
            st.markdown(ci_risk_analysis(w, r))
            st.markdown(f"**Recommendation**: For {task_type}, choose **{w['asp_id']}**")
        
        # Insights
        with st.expander("💡 Key Insights (Dynamic - Based on Current Results)"):
            top_asp = st.session_state.bayesian_scores.iloc[0]
            
            def get_specialization(asp_id):
                asp_prof = st.session_state.asp_profiles[st.session_state.asp_profiles['asp_id']==asp_id]
                return asp_prof['specialization'].values[0] if 'specialization' in asp_prof.columns else 'N/A'
            
            mountain_asps = st.session_state.bayesian_scores[st.session_state.bayesian_scores['asp_id'].str.contains('Mount')].sort_values('score', ascending=False)
            std_asps = st.session_state.bayesian_scores[st.session_state.bayesian_scores['asp_id'].str.contains('Std')].sort_values('score', ascending=False)
            climb_asps = st.session_state.bayesian_scores[st.session_state.bayesian_scores['asp_id'].str.contains('Climb')].sort_values('score', ascending=False)
            
            st.markdown(f"""
            **Bayesian Analytics Results Summary:**
            
            **1. Current Model Configuration (Hyperparameters):**
            - Success Rate Weight: **{weights['success_rate']:.1%}** - {"🔴 High priority" if weights['success_rate'] > 0.4 else "🟡 Moderate priority" if weights['success_rate'] > 0.2 else "⚪ Low priority"}
            - Response Time Weight: **{weights['response_time']:.1%}** - {"🔴 High priority" if weights['response_time'] > 0.4 else "🟡 Moderate priority" if weights['response_time'] > 0.2 else "⚪ Low priority"}
            - Customer Satisfaction Weight: **{weights['satisfaction']:.1%}** - {"🔴 High priority" if weights['satisfaction'] > 0.4 else "🟡 Moderate priority" if weights['satisfaction'] > 0.2 else "⚪ Low priority"}
            """)
            
            st.markdown("---")
            st.markdown("### 🏔️ Mountain Operations Analysis")
            render_category(mountain_asps, "Mountain", "mountain terrain tasks")
            
            st.markdown("---")
            st.markdown("### 🏙️ Standard Urban Tasks Analysis")
            render_category(std_asps, "Standard", "standard urban tasks")
            
            st.markdown("---")
            st.markdown("### 🧗 High-Risk Climbing Analysis")
            render_category(climb_asps, "Climbing", "high-risk climbing tasks")
            
            st.markdown("---")
            st.markdown(f"""
            **Overall Best ASP Across All Categories:**
            🏆 **{top_asp['asp_id']}** - {get_specialization(top_asp['asp_id'])}
            - Overall Score: **{top_asp['score']:.3f}** ± {top_asp['uncertainty']:.3f}
            
            **Uncertainty Analysis:**
            - Highest uncertainty: **{st.session_state.bayesian_scores.loc[st.session_state.bayesian_scores['uncertainty'].idxmax(), 'asp_id']}** (±{st.session_state.bayesian_scores['uncertainty'].max():.3f}) - less reliable data, need more tasks
            - Lowest uncertainty: **{st.session_state.bayesian_scores.loc[st.session_state.bayesian_scores['uncertainty'].idxmin(), 'asp_id']}** (±{st.session_state.bayesian_scores['uncertainty'].min():.3f}) - more reliable data
            
            **Next Steps:**
            - Module 2: Causal inference to understand *why* performance differs
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
            sim_satisfaction = st.slider("Satisfaction", 0.0, 10.0, 7.0, 0.5)
        
        # Always show current state and store it for comparison
        if sim_asp:
            current_asp_data = st.session_state.bayesian_scores[st.session_state.bayesian_scores['asp_id'] == sim_asp].iloc[0]
            current_task_count = len(st.session_state.historical_data[st.session_state.historical_data['asp_id'] == sim_asp])
            
            # Store current state in session for before/after comparison
            if 'before_state' not in st.session_state or st.session_state.get('last_sim_asp') != sim_asp:
                st.session_state.before_state = {
                    'asp_id': sim_asp,
                    'task_count': current_task_count,
                    'score': current_asp_data['score'],
                    'uncertainty': current_asp_data['uncertainty'],
                    'success_rate_mean': current_asp_data['success_rate_mean'],
                    'success_rate_ci': current_asp_data['success_rate_ci'],
                    'response_time_mean': current_asp_data['response_time_mean'],
                    'response_time_ci': current_asp_data['response_time_ci'],
                    'satisfaction_mean': current_asp_data['satisfaction_mean'],
                    'satisfaction_ci': current_asp_data['satisfaction_ci']
                }
                st.session_state.last_sim_asp = sim_asp
            
            st.markdown(f"""
            **📊 Current State for {sim_asp}:**
            - Tasks completed: **{current_task_count}**
            - Score: **{current_asp_data['score']:.3f}** ± {current_asp_data['uncertainty']:.3f}
            - Success Rate: **{current_asp_data['success_rate_mean']:.1%}** (95% CI: [{current_asp_data['success_rate_ci'][0]:.1%}, {current_asp_data['success_rate_ci'][1]:.1%}])
            - Response Time: **{current_asp_data['response_time_mean']:.1f} hours** (95% CI: [{current_asp_data['response_time_ci'][0]:.1f}h, {current_asp_data['response_time_ci'][1]:.1f}h])
            - Satisfaction: **{current_asp_data['satisfaction_mean']:.2f}/10** (95% CI: [{current_asp_data['satisfaction_ci'][0]:.2f}, {current_asp_data['satisfaction_ci'][1]:.2f}])
            """)
            
            # Show ALL historical tasks for this ASP
            with st.expander(f"📋 View ALL Historical Tasks for {sim_asp} ({current_task_count} tasks)"):
                asp_tasks = st.session_state.historical_data[st.session_state.historical_data['asp_id'] == sim_asp].copy()
                asp_tasks = asp_tasks[['task_id', 'asp_id', 'complexity', 'success', 'response_time_hours', 'customer_satisfaction', 'sla_met']]
                st.dataframe(asp_tasks, use_container_width=True, hide_index=True)
        
        if st.button("➕ Add New Task & Update Posterior", type="primary"):
            # Get before state from session
            before_state = st.session_state.before_state
            
            # DEBUG: Show what we're adding
            st.write(f"**DEBUG - Adding task:** Success={sim_success}, Response={sim_response}h, Satisfaction={sim_satisfaction}")
            st.write(f"**DEBUG - Before state score:** {before_state['score']:.3f}")
            
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
            
            # DEBUG: Check data for this ASP
            asp_data = st.session_state.historical_data[st.session_state.historical_data['asp_id'] == sim_asp]
            st.write(f"**DEBUG - Total tasks for {sim_asp}:** {len(asp_data)}")
            st.write(f"**DEBUG - ASP IDs in last 3 rows:**")
            st.write(asp_data[['asp_id', 'success', 'response_time_hours', 'customer_satisfaction']].tail(3))
            
            # Re-run Bayesian inference with updated data
            with st.spinner("Updating posterior with new evidence..."):
                scorer = BayesianASPScorer()
                scorer.fit(st.session_state.historical_data, n_samples=500)
                st.session_state.bayesian_scores = scorer.score_asps(weights)
                st.session_state.scorer = scorer
            
            # DEBUG: Show after state
            after_asp = st.session_state.bayesian_scores[st.session_state.bayesian_scores['asp_id'] == sim_asp].iloc[0]
            st.write(f"**DEBUG - After state score:** {after_asp['score']:.3f}")
            
            # Get after state
            after_asp = st.session_state.bayesian_scores[st.session_state.bayesian_scores['asp_id'] == sim_asp].iloc[0]
            after_task_count = len(st.session_state.historical_data[st.session_state.historical_data['asp_id'] == sim_asp])
            
            # Update before_state for next comparison
            st.session_state.before_state = {
                'asp_id': sim_asp,
                'task_count': after_task_count,
                'score': after_asp['score'],
                'uncertainty': after_asp['uncertainty'],
                'success_rate_mean': after_asp['success_rate_mean'],
                'success_rate_ci': after_asp['success_rate_ci'],
                'response_time_mean': after_asp['response_time_mean'],
                'response_time_ci': after_asp['response_time_ci'],
                'satisfaction_mean': after_asp['satisfaction_mean'],
                'satisfaction_ci': after_asp['satisfaction_ci']
            }
            
            st.success(f"✅ Added new task for {sim_asp}! Posterior updated.")
            
            # Show before/after comparison in table format
            st.markdown("### 📈 Before vs After Comparison")
            
            # Calculate uncertainties (half of CI width)
            before_success_unc = (before_state['success_rate_ci'][1] - before_state['success_rate_ci'][0]) / 2
            after_success_unc = (after_asp['success_rate_ci'][1] - after_asp['success_rate_ci'][0]) / 2
            before_response_unc = (before_state['response_time_ci'][1] - before_state['response_time_ci'][0]) / 2
            after_response_unc = (after_asp['response_time_ci'][1] - after_asp['response_time_ci'][0]) / 2
            before_satisfaction_unc = (before_state['satisfaction_ci'][1] - before_state['satisfaction_ci'][0]) / 2
            after_satisfaction_unc = (after_asp['satisfaction_ci'][1] - after_asp['satisfaction_ci'][0]) / 2
            
            # Create comparison dataframe
            comparison_data = {
                'Metric': [
                    'Tasks Completed',
                    'Overall Score',
                    'Success Rate',
                    'Response Time (hours)',
                    'Customer Satisfaction (0-10 NPS)'
                ],
                'Before': [
                    f"{before_state['task_count']}",
                    f"{before_state['score']:.3f} ± {before_state['uncertainty']:.3f}",
                    f"{before_state['success_rate_mean']:.1%} ± {before_success_unc:.1%}",
                    f"{before_state['response_time_mean']:.2f} ± {before_response_unc:.2f}",
                    f"{before_state['satisfaction_mean']:.2f} ± {before_satisfaction_unc:.2f}"
                ],
                'After': [
                    f"{after_task_count}",
                    f"{after_asp['score']:.3f} ± {after_asp['uncertainty']:.3f}",
                    f"{after_asp['success_rate_mean']:.1%} ± {after_success_unc:.1%}",
                    f"{after_asp['response_time_mean']:.2f} ± {after_response_unc:.2f}",
                    f"{after_asp['satisfaction_mean']:.2f} ± {after_satisfaction_unc:.2f}"
                ],
                'Change': [
                    f"+{after_task_count - before_state['task_count']}",
                    f"{(after_asp['score'] - before_state['score']):+.3f}",
                    f"{(after_asp['success_rate_mean'] - before_state['success_rate_mean']):+.1%}",
                    f"{(after_asp['response_time_mean'] - before_state['response_time_mean']):+.2f}",
                    f"{(after_asp['satisfaction_mean'] - before_state['satisfaction_mean']):+.2f}"
                ]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Display as styled table
            st.dataframe(
                comparison_df.style.set_properties(**{
                    'text-align': 'left',
                    'font-size': '14px',
                    'border': '1px solid #ddd'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('font-weight', 'bold')]},
                    {'selector': 'td', 'props': [('padding', '8px')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
            
            score_change = after_asp['score'] - before_state['score']
            uncertainty_change = after_asp['uncertainty'] - before_state['uncertainty']
            
            st.info(f"""
            **🔍 What Changed:**
            - **Task Added**: {'✅ Success' if sim_success else '❌ Failure'}, {sim_response}h response, {sim_satisfaction}/5 satisfaction
            - **Score Impact**: {score_change:+.3f} points ({(score_change/before_state['score']*100):+.1f}%)
            - **Uncertainty Impact**: {uncertainty_change:+.3f} ({"✅ Decreased - more confident!" if uncertainty_change < 0 else "⚠️ Increased - less confident"})
            - **Key Insight**: {"This task improved the ASP's performance!" if score_change > 0 else "This task decreased the ASP's performance." if score_change < 0 else "This task had minimal impact on performance."}
            - **Bayesian Learning**: The posterior distribution updated based on this new evidence, demonstrating continuous learning without retraining.
            """)

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
