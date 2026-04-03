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
    plot_prior_vs_posterior,
    plot_pos_comparison,
    plot_expected_loss,
    plot_credible_interval
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
                'ASP_Mount1': 37, 'ASP_Mount2': 21,  # Mountain operations
                'ASP_Std1': 32, 'ASP_Std2': 13,      # Standard urban
                'ASP_Climb1': 24, 'ASP_Climb2': 8    # High-risk climbing
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
        
        with st.expander("🔑 Key Difference Explained"):
            st.info("""
            **Simple Average (Gray Bars)** = Just add up all results and divide by count
            
            **Bayesian Mean (Blue Diamonds)** = Similar value BUT with uncertainty quantification
            
            **Why are they SIMILAR but NOT IDENTICAL?**
            - Bayesian = Prior belief (orange curves below) + Data → Posterior
            - With **many tasks**: data dominates → Bayesian ≈ Simple Average
            - With **few tasks**: prior still has influence → Bayesian ≠ Simple Average
            
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
        - **Satisfaction**: Normalized as (NPS+100)/200 — higher NPS = higher score
        
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
                    "satisfaction": "Customer NPS (%)"
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
        
        # Continuous Learning Simulator (BEFORE scores so updates are reflected)
        st.markdown("---")
        st.subheader("🔄 Continuous Learning Simulator")
        st.info("**Bayesian Value #3**: Watch how posteriors update as new data arrives. Add a task and see how ALL scores, rankings, and recommendations update instantly.")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sim_asp = st.selectbox("Select ASP", st.session_state.bayesian_scores['asp_id'].tolist(), key='sim_asp')
        with col2:
            sim_success = st.selectbox("Task Success?", [True, False], format_func=lambda x: "✅ Success" if x else "❌ Failure")
        with col3:
            sim_response = st.number_input("Response Time (hours)", min_value=0.5, max_value=24.0, value=4.0, step=0.5)
        with col4:
            sim_satisfaction = st.slider("Satisfaction (0-10)", 0.0, 10.0, 7.0, 0.5)
        
        if sim_asp:
            current_asp_data = st.session_state.bayesian_scores[st.session_state.bayesian_scores['asp_id'] == sim_asp].iloc[0]
            current_task_count = len(st.session_state.historical_data[st.session_state.historical_data['asp_id'] == sim_asp])
            st.markdown(f"""
            **📊 Current State for {sim_asp}:** Tasks: **{current_task_count}** | Score: **{current_asp_data['score']:.3f}** ± {current_asp_data['uncertainty']:.3f} | Success: **{current_asp_data['success_rate_mean']:.1%}** | Response: **{current_asp_data['response_time_mean']:.1f}h** | Satisfaction: **{current_asp_data['satisfaction_mean']:.1f}%**
            """)
            with st.expander(f"📋 View ALL Historical Tasks for {sim_asp} ({current_task_count} tasks)"):
                asp_tasks = st.session_state.historical_data[st.session_state.historical_data['asp_id'] == sim_asp].copy()
                asp_tasks = asp_tasks[['task_id', 'asp_id', 'complexity', 'success', 'response_time_hours', 'customer_satisfaction', 'sla_met']]
                st.dataframe(asp_tasks, use_container_width=True, hide_index=True)
        
        if st.button("➕ Add New Task & Update Posterior", type="primary"):
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
            
            with st.spinner("Updating posterior with new evidence..."):
                scorer = BayesianASPScorer()
                scorer.fit(st.session_state.historical_data, n_samples=500)
                st.session_state.bayesian_scores = scorer.score_asps(weights)
                st.session_state.scorer = scorer
            
            st.rerun()
        
        st.markdown("---")
        
        # Scores table
        st.subheader("ASP Scores Table (OUTPUT: Summary Statistics)")
        st.caption("📤 **OUTPUT**: Posterior means and 95% credible intervals for all metrics.")
        
        display_df = st.session_state.bayesian_scores.copy()
        display_df = display_df.rename(columns={
            'success_rate_mean': 'Success Rate (probability)',
            'response_time_mean': 'Response Time (hours)',
            'satisfaction_mean': 'NPS (%)'
        })
        display_df['success_rate_ci'] = display_df['success_rate_ci'].apply(lambda x: f"[{x[0]:.3f}, {x[1]:.3f}]")
        display_df['response_time_ci'] = display_df['response_time_ci'].apply(lambda x: f"[{x[0]:.3f}h, {x[1]:.3f}h]")
        display_df['satisfaction_ci'] = display_df['satisfaction_ci'].apply(lambda x: f"[{x[0]:.1f}%, {x[1]:.1f}%]")
        display_cols = ['asp_id', 'score', 'uncertainty', 
                       'Success Rate (probability)', 'success_rate_ci',
                       'Response Time (hours)', 'response_time_ci',
                       'NPS (%)', 'satisfaction_ci']
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
        - Customer Satisfaction: {best_asp['satisfaction_mean']:.1f}%
        """)
        
        # Key Business Decisions powered by Bayesian Analytics
        worst_asp = st.session_state.bayesian_scores.iloc[-1]
        scores = st.session_state.bayesian_scores
        with st.expander("💼 Key Business Decisions (Bayesian Value for Stakeholders)", expanded=True):
            st.markdown(f"""
**What Bayesian Analytics enables that simple averages cannot:**

| # | Decision | Bayesian Insight | Business Impact |
|:--|:---------|:-----------------|:----------------|
| 1 | **Best ASP selection** | {best_asp['asp_id']} scores {best_asp['score']:.3f} with {best_asp['score_ci'][0]:.3f}–{best_asp['score_ci'][1]:.3f} range | Even worst-case outperforms alternatives |
| 2 | **Avoid worst performer** | {worst_asp['asp_id']} scores {worst_asp['score']:.3f} — {((best_asp['score']-worst_asp['score'])/worst_asp['score']*100):.0f}% below best | Quantified risk of wrong choice |
| 3 | **Confidence in decision** | {best_asp['asp_id']} uncertainty ±{best_asp['uncertainty']:.3f} vs {worst_asp['asp_id']} ±{worst_asp['uncertainty']:.3f} | More data = narrower CI = safer decisions |
| 4 | **Data collection priority** | {scores.loc[scores['uncertainty'].idxmax(), 'asp_id']} has highest uncertainty (±{scores['uncertainty'].max():.3f}) | Invest in data where it matters most |
| 5 | **Per-category winners** | Mountain: {scores[scores['asp_id'].str.contains('Mount')].iloc[0]['asp_id']}, Urban: {scores[scores['asp_id'].str.contains('Std')].iloc[0]['asp_id']}, Climbing: {scores[scores['asp_id'].str.contains('Climb')].iloc[0]['asp_id']} | Right ASP for right task type |

**🎯 Bottom line**: Bayesian analytics doesn't just tell you *who is best* — it tells you **how confident** you should be in that choice, and **what could go wrong** (floor scores). This turns ASP selection from gut feeling into data-driven risk management.
            """)
        
        # Helper: CI-based risk analysis for a pair of ASPs
        def ci_risk_analysis(w, r):
            if r is None:
                return ""
            overlaps = []
            if r['success_rate_ci'][1] > w['success_rate_ci'][0]:
                overlaps.append(f"Success Rate: {r['asp_id']} best ({r['success_rate_ci'][1]:.1%}) > {w['asp_id']} worst ({w['success_rate_ci'][0]:.1%})")
            if r['response_time_ci'][0] < w['response_time_ci'][1]:
                overlaps.append(f"Response Time: {r['asp_id']} best ({r['response_time_ci'][0]:.1f}h) < {w['asp_id']} worst ({w['response_time_ci'][1]:.1f}h)")
            if r['satisfaction_ci'][1] > w['satisfaction_ci'][0]:
                overlaps.append(f"Satisfaction: {r['asp_id']} best ({r['satisfaction_ci'][1]:.1f}%) > {w['asp_id']} worst ({w['satisfaction_ci'][0]:.1f}%)")
            if overlaps:
                overlap_list = "\n".join([f"  - {o}" for o in overlaps])
                w_floor_winner = w['asp_id'] if w['score_ci'][0] > r['score_ci'][0] else r['asp_id']
                return f"""
⚠️ **CI Overlap on {len(overlaps)} metric(s)** — runner-up could outperform:

{overlap_list}

| Perspective | {w['asp_id']} | {r['asp_id']} | Choose |
|:--|:--:|:--:|:--|
| 🔻 Floor | {w['score_ci'][0]:.3f} | {r['score_ci'][0]:.3f} | **{w_floor_winner}** |
| ⚖️ Mean | {w['score']:.3f} | {r['score']:.3f} | **{w['asp_id']}** |
| 🔺 Ceiling | {w['score_ci'][1]:.3f} | {r['score_ci'][1]:.3f} | **{w['asp_id'] if w['score_ci'][1] > r['score_ci'][1] else r['asp_id']}** |"""
            else:
                return f"""
✅ **No CI overlap** — {w['asp_id']} outperforms {r['asp_id']} even in worst-case.

| Perspective | {w['asp_id']} | {r['asp_id']} |
|:--|:--:|:--:|
| 🔻 Floor | {w['score_ci'][0]:.3f} | {r['score_ci'][0]:.3f} |
| ⚖️ Mean | {w['score']:.3f} | {r['score']:.3f} |
| 🔺 Ceiling | {w['score_ci'][1]:.3f} | {r['score_ci'][1]:.3f} |"""
        
        # Helper: render category analysis as comparison table
        def render_category(cat_asps, cat_name, task_type):
            if len(cat_asps) < 2:
                return
            w = cat_asps.iloc[0]
            r = cat_asps.iloc[1]
            
            # Probability of Superiority
            samples_w = st.session_state.scorer.get_score_samples(w['asp_id'], weights)
            samples_r = st.session_state.scorer.get_score_samples(r['asp_id'], weights)
            pos_pct = (samples_w > samples_r).mean() * 100
            
            # Compute shared x-range for all 3 plots
            all_samples = np.concatenate([samples_w, samples_r])
            x_min = max(0, np.percentile(all_samples, 0.5) - 0.05)
            x_max = np.percentile(all_samples, 99.5) + 0.05
            x_range = [x_min, x_max]
            
            st.plotly_chart(
                plot_pos_comparison(samples_w, samples_r, w['asp_id'], r['asp_id'], pos_pct, x_range),
                use_container_width=True
            )
            
            ci_fig, ci_w, ci_r, ci_overlap = plot_credible_interval(samples_w, samples_r, w['asp_id'], r['asp_id'], x_range)
            st.plotly_chart(ci_fig, use_container_width=True)
            
            el_fig, el_w, el_r = plot_expected_loss(samples_w, samples_r, w['asp_id'], r['asp_id'], x_range)
            st.plotly_chart(el_fig, use_container_width=True)
            
            n_w = len(st.session_state.historical_data[st.session_state.historical_data['asp_id'] == w['asp_id']])
            n_r = len(st.session_state.historical_data[st.session_state.historical_data['asp_id'] == r['asp_id']])
            safer = w['asp_id'] if el_w < el_r else r['asp_id']
            
            # 2d: Hide metrics table and CI overlap in expander
            with st.expander("📋 Detailed Metrics & CI Overlap Analysis"):
                # Build comparison table
                def fmt_ci(ci):
                    return f"[{ci[0]:.3f}, {ci[1]:.3f}]"
                def fmt_ci_pct(ci):
                    return f"[{ci[0]:.1%}, {ci[1]:.1%}]"
                
                table_data = {
                    'Metric': ['Tasks', 'Overall Score', 'Success Rate ↑', 'Response Time (h) ↓', 'NPS (%) ↑'],
                    f"🥇 {w['asp_id']}": [
                        f"{n_w}",
                        f"{w['score']:.3f} ± {w['uncertainty']:.3f}",
                        f"{w['success_rate_mean']:.1%} {fmt_ci_pct(w['success_rate_ci'])}",
                        f"{w['response_time_mean']:.1f} {fmt_ci(w['response_time_ci'])}",
                        f"{w['satisfaction_mean']:.1f}% {fmt_ci(w['satisfaction_ci'])}"
                    ],
                    f"🥈 {r['asp_id']}": [
                        f"{n_r}",
                        f"{r['score']:.3f} ± {r['uncertainty']:.3f}",
                        f"{r['success_rate_mean']:.1%} {fmt_ci_pct(r['success_rate_ci'])}",
                        f"{r['response_time_mean']:.1f} {fmt_ci(r['response_time_ci'])}",
                        f"{r['satisfaction_mean']:.1f}% {fmt_ci(r['satisfaction_ci'])}"
                    ],
                    'Winner': [
                        f"{w['asp_id'] if n_w > n_r else r['asp_id']} (more data)",
                        f"{w['asp_id']} (+{w['score']-r['score']:.3f})",
                        f"{w['asp_id'] if w['success_rate_mean'] > r['success_rate_mean'] else r['asp_id']} (higher ↑)",
                        f"{w['asp_id'] if w['response_time_mean'] < r['response_time_mean'] else r['asp_id']} (lower ↓)",
                        f"{w['asp_id'] if w['satisfaction_mean'] > r['satisfaction_mean'] else r['asp_id']} (higher ↑)"
                    ]
                }
                st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
                
                # 2c: CI overlap analysis (no recommendation, no "collect more data")
                st.markdown(ci_risk_analysis(w, r))
            
            # Business Value Summary Table with medals
            st.markdown(f"#### 📊 Quantified Business Value: {w['asp_id']} vs {r['asp_id']}")
            
            # 4: CI verdict with justification
            if ci_overlap:
                ci_w_width = ci_w[1] - ci_w[0]
                ci_r_width = ci_r[1] - ci_r[0]
                wider = r['asp_id'] if ci_r_width > ci_w_width else w['asp_id']
                wider_n = n_r if ci_r_width > ci_w_width else n_w
                # Estimate: to halve CI width, need ~4x more data
                needed = wider_n * 3
                ci_verdict = f"⚠️ Overlap — {wider} needs ~{needed} tasks (currently {wider_n}) to narrow CI"
            else:
                ci_verdict = "✅ No overlap — clear winner"
            
            bv_data = {
                'Metric': [
                    '🎯 Probability of Superiority',
                    '📏 95% Credible Interval',
                    '🛡️ Expected Loss'
                ],
                f"🥇 {w['asp_id']}": [
                    f"Wins {pos_pct:.0f}% of samples",
                    f"[{ci_w[0]:.3f}, {ci_w[1]:.3f}]",
                    f"E(Loss) = {el_w:.3f}"
                ],
                f"🥈 {r['asp_id']}": [
                    f"Wins {100-pos_pct:.0f}% of samples",
                    f"[{ci_r[0]:.3f}, {ci_r[1]:.3f}]",
                    f"E(Loss) = {el_r:.3f}"
                ],
                'Verdict': [
                    f"{'🟢' if pos_pct >= 75 else '🟡' if pos_pct >= 60 else '🔴'} {w['asp_id'] if pos_pct > 50 else r['asp_id']} is superior",
                    ci_verdict,
                    f"🛡️ {safer} is the safer choice"
                ]
            }
            st.dataframe(pd.DataFrame(bv_data), use_container_width=True, hide_index=True)
            
            if pos_pct >= 90:
                conf_label = "🟢 Very High Confidence"
            elif pos_pct >= 75:
                conf_label = "🟡 Moderate Confidence"
            elif pos_pct >= 60:
                conf_label = "🟠 Low Confidence"
            else:
                conf_label = "🔴 Very Low Confidence"
            st.markdown(f"**Recommendation**: For {task_type}, choose **{w['asp_id']}** — {conf_label} (PoS: {pos_pct:.0f}%)")
        
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
            
            **2. Score Formula & Risk Bounds:**
            
            `Score = SuccessRate × {weights['success_rate']:.0%} + ResponseNorm × {weights['response_time']:.0%} + Satisfaction/10 × {weights['satisfaction']:.0%}`
            
            where `ResponseNorm = 1/(1 + hours/10)` (lower time → higher score)
            
            Each score has three values derived from the 95% credible intervals:
            - 🔻 **Floor (worst-case)** = score using lower CI bounds for success & satisfaction, upper CI for response time
            - ⚖️ **Mean** = score using posterior means
            - 🔺 **Ceiling (best-case)** = score using upper CI bounds for success & satisfaction, lower CI for response time
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
