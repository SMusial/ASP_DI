"""Visualization utilities for the ASP Decision Intelligence platform."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


# Define consistent ASP ordering
ASP_ORDER = ['ASP_Mount1', 'ASP_Mount2', 'ASP_Std1', 'ASP_Std2', 'ASP_Climb1', 'ASP_Climb2']

def sort_asps(df: pd.DataFrame) -> pd.DataFrame:
    """Sort ASPs in consistent order: Mountain, Standard, Climbing (1 before 2)."""
    if 'asp_id' in df.columns:
        # Create categorical with fixed order
        df['asp_id'] = pd.Categorical(df['asp_id'], categories=ASP_ORDER, ordered=True)
        return df.sort_values('asp_id').reset_index(drop=True)
    return df


def plot_asp_scores_with_uncertainty(scores_df: pd.DataFrame) -> go.Figure:
    """Plot ASP scores with uncertainty intervals."""
    fig = go.Figure()
    
    scores_df = sort_asps(scores_df)
    
    # Bars without error bars — clean look
    fig.add_trace(go.Bar(
        y=scores_df['asp_id'],
        x=scores_df['score'],
        orientation='h',
        marker=dict(
            color=scores_df['score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Score")
        ),
        name='Score',
        showlegend=False,
    ))
    
    # Error bars as separate diamond markers at the score value
    fig.add_trace(go.Scatter(
        y=scores_df['asp_id'],
        x=scores_df['score'],
        mode='markers',
        marker=dict(size=8, color='red', symbol='diamond'),
        error_x=dict(
            type='data',
            array=scores_df['uncertainty'],
            visible=True,
            color='red',
            thickness=2,
            width=6
        ),
        name='95% CI',
        showlegend=True,
    ))
    
    # Text annotations above the error bars
    for i, row in scores_df.iterrows():
        fig.add_annotation(
            y=row['asp_id'],
            x=row['score'] + row['uncertainty'] + 0.02,
            text=f"{row['score']:.3f} ± {row['uncertainty']:.3f}",
            showarrow=False,
            font=dict(size=12),
            xanchor='left',
        )
    
    max_x = max(row['score'] + row['uncertainty'] for _, row in scores_df.iterrows()) + 0.25
    fig.update_layout(
        title="ASP Bayesian Scores with Uncertainty",
        xaxis_title="Score (0-1)",
        xaxis=dict(range=[0, max_x]),
        yaxis_title="ASP",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_metric_distributions(scores_df: pd.DataFrame, metric: str) -> go.Figure:
    """Plot distribution of a specific metric across ASPs with credible intervals."""
    fig = go.Figure()
    
    mean_col = f'{metric}_mean'
    ci_col = f'{metric}_ci'
    
    scores_df = sort_asps(scores_df)
    
    ci_lower = [ci[0] for ci in scores_df[ci_col]]
    ci_upper = [ci[1] for ci in scores_df[ci_col]]
    
    fig.add_trace(go.Scatter(
        x=scores_df['asp_id'],
        y=scores_df[mean_col],
        mode='markers',
        marker=dict(size=10, color='blue'),
        name='Mean',
        error_y=dict(
            type='data',
            symmetric=False,
            array=[u - m for u, m in zip(ci_upper, scores_df[mean_col])],
            arrayminus=[m - l for m, l in zip(scores_df[mean_col], ci_lower)],
        )
    ))
    
    metric_titles = {
        'success_rate': 'Success Rate',
        'response_time': 'Response Time (hours)',
        'satisfaction': 'Customer NPS (%)'
    }
    
    fig.update_layout(
        title=f"{metric_titles.get(metric, metric)} - Posterior Distributions",
        xaxis_title="ASP",
        yaxis_title=metric_titles.get(metric, metric),
        height=400,
        showlegend=False
    )
    
    return fig


def plot_performance_comparison(historical_data: pd.DataFrame) -> go.Figure:
    """Create multi-metric comparison across ASPs."""
    summary = historical_data.groupby('asp_id').agg({
        'success': 'mean',
        'response_time_hours': 'mean',
        'cost': 'mean'
    }).reset_index()
    # Compute NPS per ASP
    def calc_nps(group):
        p = (group['customer_satisfaction'] >= 9).sum()
        d = (group['customer_satisfaction'] <= 6).sum()
        return (p - d) / len(group) * 100
    summary['nps'] = historical_data.groupby('asp_id').apply(calc_nps).values
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Success Rate', 'Avg Response Time (hrs)', 
                       'NPS (%)', 'Avg Cost ($)')
    )
    
    fig.add_trace(
        go.Bar(x=summary['asp_id'], y=summary['success'], name='Success Rate',
               marker_color='lightblue'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=summary['asp_id'], y=summary['response_time_hours'], 
               name='Response Time', marker_color='lightcoral'),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=summary['asp_id'], y=summary['nps'], 
               name='NPS (%)', marker_color='lightgreen'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(x=summary['asp_id'], y=summary['cost'], 
               name='Cost', marker_color='lightyellow'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Historical Performance Overview")
    
    return fig


def plot_data_sufficiency(historical_data: pd.DataFrame) -> go.Figure:
    """Visualize data availability per ASP to show uncertainty sources."""
    task_counts = historical_data.groupby('asp_id').size().reset_index(name='n_tasks')
    task_counts = sort_asps(task_counts)
    
    fig = go.Figure(go.Bar(
        x=task_counts['asp_id'],
        y=task_counts['n_tasks'],
        marker=dict(
            color=task_counts['n_tasks'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Tasks")
        ),
        text=task_counts['n_tasks'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Historical Data Availability per ASP",
        xaxis_title="ASP",
        yaxis_title="Number of Tasks",
        height=400
    )
    
    return fig


def plot_bayesian_vs_simple_average(scores_df: pd.DataFrame, historical_data: pd.DataFrame) -> go.Figure:
    """Compare Bayesian estimates with simple averages to show value."""
    # Calculate simple averages + NPS
    simple_avg = historical_data.groupby('asp_id').agg({
        'success': 'mean',
        'response_time_hours': 'mean',
    }).reset_index()
    # Compute simple NPS per ASP
    def calc_nps(group):
        promoters = (group['customer_satisfaction'] >= 9).sum()
        detractors = (group['customer_satisfaction'] <= 6).sum()
        return (promoters - detractors) / len(group) * 100
    simple_nps = historical_data.groupby('asp_id').apply(calc_nps).reset_index()
    simple_nps.columns = ['asp_id', 'nps']
    simple_avg = simple_avg.merge(simple_nps, on='asp_id')
    
    # Merge with Bayesian results
    comparison = scores_df[['asp_id', 'success_rate_mean', 'response_time_mean', 
                            'satisfaction_mean', 'uncertainty', 
                            'success_rate_ci', 'response_time_ci', 'satisfaction_ci']].merge(
        simple_avg, on='asp_id'
    )
    
    # Sort in consistent order
    comparison = sort_asps(comparison)
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Success Rate', 'Response Time (hours)', 'NPS (%)')
    )
    
    # Success Rate
    fig.add_trace(
        go.Bar(x=comparison['asp_id'], y=comparison['success'], 
               name='Simple Average', marker_color='lightgray', showlegend=True),
        row=1, col=1
    )
    # Add Bayesian with error bars
    success_ci_lower = [ci[0] for ci in comparison['success_rate_ci']]
    success_ci_upper = [ci[1] for ci in comparison['success_rate_ci']]
    fig.add_trace(
        go.Scatter(x=comparison['asp_id'], y=comparison['success_rate_mean'],
                   mode='markers', marker=dict(size=12, color='blue', symbol='diamond'),
                   name='Bayesian Mean',
                   error_y=dict(
                       type='data',
                       symmetric=False,
                       array=[u - m for u, m in zip(success_ci_upper, comparison['success_rate_mean'])],
                       arrayminus=[m - l for m, l in zip(comparison['success_rate_mean'], success_ci_lower)],
                       color='blue',
                       thickness=2,
                       width=4
                   ),
                   showlegend=True),
        row=1, col=1
    )
    
    # Response Time
    fig.add_trace(
        go.Bar(x=comparison['asp_id'], y=comparison['response_time_hours'],
               name='Simple Average', marker_color='lightgray', showlegend=False),
        row=1, col=2
    )
    response_ci_lower = [ci[0] for ci in comparison['response_time_ci']]
    response_ci_upper = [ci[1] for ci in comparison['response_time_ci']]
    fig.add_trace(
        go.Scatter(x=comparison['asp_id'], y=comparison['response_time_mean'],
                   mode='markers', marker=dict(size=12, color='blue', symbol='diamond'),
                   name='Bayesian Mean',
                   error_y=dict(
                       type='data',
                       symmetric=False,
                       array=[u - m for u, m in zip(response_ci_upper, comparison['response_time_mean'])],
                       arrayminus=[m - l for m, l in zip(comparison['response_time_mean'], response_ci_lower)],
                       color='blue',
                       thickness=2,
                       width=4
                   ),
                   showlegend=False),
        row=1, col=2
    )
    
    # NPS
    fig.add_trace(
        go.Bar(x=comparison['asp_id'], y=comparison['nps'],
               name='Simple Average', marker_color='lightgray', showlegend=False),
        row=1, col=3
    )
    satisfaction_ci_lower = [ci[0] for ci in comparison['satisfaction_ci']]
    satisfaction_ci_upper = [ci[1] for ci in comparison['satisfaction_ci']]
    fig.add_trace(
        go.Scatter(x=comparison['asp_id'], y=comparison['satisfaction_mean'],
                   mode='markers', marker=dict(size=12, color='blue', symbol='diamond'),
                   name='Bayesian Mean',
                   error_y=dict(
                       type='data',
                       symmetric=False,
                       array=[u - m for u, m in zip(satisfaction_ci_upper, comparison['satisfaction_mean'])],
                       arrayminus=[m - l for m, l in zip(comparison['satisfaction_mean'], satisfaction_ci_lower)],
                       color='blue',
                       thickness=2,
                       width=4
                   ),
                   showlegend=False),
        row=1, col=3
    )
    
    fig.update_layout(
        height=400,
        title_text="Bayesian vs Simple Average Comparison (Blue error bars = Uncertainty)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(rangemode="tozero")
    
    return fig


def plot_prior_distributions() -> go.Figure:
    """Plot the prior distributions used in the Bayesian model."""
    import numpy as np
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            'Success Rate Prior: Beta(α~Gamma(1,0.5), β~Gamma(1,0.5))',
            'Response Time Prior: LogNormal(μ=ln(2), σ=1) — median≈2h, max 12h',
            'NPS Prior: Normal(μ=0%, σ=50%)'
        )
    )
    
    # Success rate prior: sample from Beta with Gamma hyperpriors
    np.random.seed(42)
    alphas = np.random.gamma(1, 1/0.5, 2000)
    betas = np.random.gamma(1, 1/0.5, 2000)
    success_prior = np.random.beta(np.clip(alphas, 0.01, None), np.clip(betas, 0.01, None))
    
    x_s = np.linspace(0, 1, 200)
    hist_s, edges_s = np.histogram(success_prior, bins=200, range=(0, 1), density=True)
    fig.add_trace(
        go.Scatter(x=x_s, y=hist_s, mode='lines', fill='tozeroy',
                   line=dict(color='rgba(255,165,0,0.8)'), fillcolor='rgba(255,165,0,0.2)',
                   name='Prior', showlegend=True),
        row=1, col=1
    )
    
    # Response time prior: LogNormal(ln(3), 1) — right-skewed, always positive
    x_r = np.linspace(0.1, 12, 200)
    from scipy.stats import lognorm
    y_r = lognorm.pdf(x_r, s=1, scale=np.exp(np.log(3)))
    fig.add_trace(
        go.Scatter(x=x_r, y=y_r, mode='lines', fill='tozeroy',
                   line=dict(color='rgba(255,165,0,0.8)'), fillcolor='rgba(255,165,0,0.2)',
                   name='Prior', showlegend=False),
        row=1, col=2
    )
    
    # NPS prior: Normal(0, 50) in percentage
    x_sat = np.linspace(-100, 100, 200)
    from scipy.stats import norm
    y_sat = norm.pdf(x_sat, loc=0, scale=50)
    fig.add_trace(
        go.Scatter(x=x_sat, y=y_sat, mode='lines', fill='tozeroy',
                   line=dict(color='rgba(255,165,0,0.8)'), fillcolor='rgba(255,165,0,0.2)',
                   name='Prior', showlegend=False),
        row=1, col=3
    )
    
    fig.update_layout(
        height=300,
        title_text="Prior Distributions (our initial beliefs BEFORE seeing any data)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(title_text="Success Rate (probability)", row=1, col=1)
    fig.update_xaxes(title_text="Response Time (hours)", row=1, col=2)
    fig.update_xaxes(title_text="NPS (%)", row=1, col=3)
    fig.update_yaxes(title_text="Density", row=1, col=1)
    
    return fig


def plot_prior_vs_posterior(scorer) -> go.Figure:
    """Plot prior vs aggregated posterior, then aggregated vs individual ASP posteriors."""
    from scipy.stats import lognorm, norm
    
    fig = make_subplots(rows=2, cols=3, subplot_titles=(
        'Success Rate', 'Response Time (hours)', 'NPS (%)',
        'Success Rate', 'Response Time (hours)', 'NPS (%)'),
        vertical_spacing=0.15,
        row_titles=['Prior vs Aggregated Posterior', 'Aggregated vs Individual ASPs'])
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # --- Compute priors ---
    np.random.seed(42)
    alphas = np.random.gamma(1, 1/0.5, 5000)
    betas = np.random.gamma(1, 1/0.5, 5000)
    success_prior = np.random.beta(np.clip(alphas, 0.01, None), np.clip(betas, 0.01, None))
    x_s = np.linspace(0, 1, 200)
    hist_s, _ = np.histogram(success_prior, bins=200, range=(0, 1), density=True)
    
    x_r = np.linspace(0.1, 12, 200)
    y_r = lognorm.pdf(x_r, s=1, scale=2)
    
    x_sat = np.linspace(-100, 100, 200)
    from scipy.stats import norm
    y_sat = norm.pdf(x_sat, loc=0, scale=50)
    
    # --- Compute aggregated posteriors ---
    all_success = np.concatenate([scorer.trace.posterior['success_rate'].values[:, :, np.where(scorer.asp_ids == a)[0][0]].flatten() for a in scorer.asp_ids])
    agg_s_h, agg_s_e = np.histogram(all_success, bins=80, density=True)
    agg_s_x = (agg_s_e[:-1] + agg_s_e[1:]) / 2
    
    all_resp = np.concatenate([np.exp(scorer.trace.posterior['response_log_mu'].values[:, :, np.where(scorer.asp_ids == a)[0][0]].flatten()) for a in scorer.asp_ids])
    all_resp = np.clip(all_resp, 0, 12)
    agg_r_h, agg_r_e = np.histogram(all_resp, bins=80, range=(0, 12), density=True)
    agg_r_x = (agg_r_e[:-1] + agg_r_e[1:]) / 2
    
    all_sat = np.concatenate([scorer.trace.posterior['nps_mu'].values[:, :, np.where(scorer.asp_ids == a)[0][0]].flatten() * 100 for a in scorer.asp_ids])
    agg_sat_h, agg_sat_e = np.histogram(all_sat, bins=80, density=True)
    agg_sat_x = (agg_sat_e[:-1] + agg_sat_e[1:]) / 2
    
    # === ROW 1: Prior (orange dashed) vs Aggregated Posterior (white thick) ===
    fig.add_trace(go.Scatter(x=x_s, y=hist_s, mode='lines', fill='tozeroy',
        line=dict(color='rgba(255,165,0,0.6)', width=2, dash='dash'),
        fillcolor='rgba(255,165,0,0.1)', name='Prior', legendgroup='prior', showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=x_r, y=y_r, mode='lines', fill='tozeroy',
        line=dict(color='rgba(255,165,0,0.6)', width=2, dash='dash'),
        fillcolor='rgba(255,165,0,0.1)', name='Prior', legendgroup='prior', showlegend=False), row=1, col=2)
    fig.add_trace(go.Scatter(x=x_sat, y=y_sat, mode='lines', fill='tozeroy',
        line=dict(color='rgba(255,165,0,0.6)', width=2, dash='dash'),
        fillcolor='rgba(255,165,0,0.1)', name='Prior', legendgroup='prior', showlegend=False), row=1, col=3)
    
    fig.add_trace(go.Scatter(x=agg_s_x, y=agg_s_h, mode='lines',
        line=dict(color='white', width=3), name='Aggregated Posterior',
        legendgroup='agg', showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=agg_r_x, y=agg_r_h, mode='lines',
        line=dict(color='white', width=3), name='Aggregated Posterior',
        legendgroup='agg', showlegend=False), row=1, col=2)
    fig.add_trace(go.Scatter(x=agg_sat_x, y=agg_sat_h, mode='lines',
        line=dict(color='white', width=3), name='Aggregated Posterior',
        legendgroup='agg', showlegend=False), row=1, col=3)
    
    # === ROW 2: Aggregated (white thick) vs Individual ASPs (colored thin) ===
    fig.add_trace(go.Scatter(x=agg_s_x, y=agg_s_h, mode='lines',
        line=dict(color='white', width=3), name='Aggregated Posterior',
        legendgroup='agg', showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=agg_r_x, y=agg_r_h, mode='lines',
        line=dict(color='white', width=3), name='Aggregated Posterior',
        legendgroup='agg', showlegend=False), row=2, col=2)
    fig.add_trace(go.Scatter(x=agg_sat_x, y=agg_sat_h, mode='lines',
        line=dict(color='white', width=3), name='Aggregated Posterior',
        legendgroup='agg', showlegend=False), row=2, col=3)
    
    for i, asp_id in enumerate(ASP_ORDER):
        if asp_id not in scorer.asp_ids:
            continue
        asp_pos = np.where(scorer.asp_ids == asp_id)[0][0]
        color = colors[i % len(colors)]
        
        s_samples = scorer.trace.posterior['success_rate'].values[:, :, asp_pos].flatten()
        h, e = np.histogram(s_samples, bins=50, density=True)
        fig.add_trace(go.Scatter(x=(e[:-1]+e[1:])/2, y=h, mode='lines',
            line=dict(color=color, width=2), name=asp_id,
            legendgroup=asp_id, showlegend=True), row=2, col=1)
        
        log_mu = scorer.trace.posterior['response_log_mu'].values[:, :, asp_pos].flatten()
        r_samples = np.exp(log_mu)
        r_samples = np.clip(r_samples, 0, 12)
        h, e = np.histogram(r_samples, bins=50, range=(0, 12), density=True)
        fig.add_trace(go.Scatter(x=(e[:-1]+e[1:])/2, y=h, mode='lines',
            line=dict(color=color, width=2), name=asp_id,
            legendgroup=asp_id, showlegend=False), row=2, col=2)
        
        sat_samples = scorer.trace.posterior['nps_mu'].values[:, :, asp_pos].flatten() * 100
        h, e = np.histogram(sat_samples, bins=50, density=True)
        fig.add_trace(go.Scatter(x=(e[:-1]+e[1:])/2, y=h, mode='lines',
            line=dict(color=color, width=2), name=asp_id,
            legendgroup=asp_id, showlegend=False), row=2, col=3)
    
    fig.update_layout(height=700,
        title_text="Prior vs Posterior — How Data Updated Our Beliefs",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(rangemode="tozero")
    return fig



def plot_pos_comparison(samples_w, samples_r, name_w, name_r, pos_pct, x_range=None):
    """Plot posterior score distributions for two ASPs with PoS annotation."""
    fig = go.Figure()
    h_w, e_w = np.histogram(samples_w, bins=60, density=True)
    h_r, e_r = np.histogram(samples_r, bins=60, density=True)
    fig.add_trace(go.Scatter(x=(e_w[:-1]+e_w[1:])/2, y=h_w, mode='lines', fill='tozeroy',
        line=dict(color='#2ca02c', width=3), fillcolor='rgba(44,160,44,0.25)', name=f"\U0001f947 {name_w}"))
    fig.add_trace(go.Scatter(x=(e_r[:-1]+e_r[1:])/2, y=h_r, mode='lines', fill='tozeroy',
        line=dict(color='#d62728', width=3), fillcolor='rgba(214,39,40,0.25)', name=f"\U0001f948 {name_r}"))
    if pos_pct >= 90:
        verdict = "\U0001f7e2 Very High Confidence"
    elif pos_pct >= 75:
        verdict = "\U0001f7e1 Moderate Confidence"
    elif pos_pct >= 60:
        verdict = "\U0001f7e0 Low Confidence"
    else:
        verdict = "\U0001f534 Essentially a Coin Flip"
    fig.update_layout(height=350, margin=dict(t=120, b=60),
        title=dict(text=f"<b>Probability of Superiority (PoS)</b><br><span style='font-size:16px'>{name_w} beats {name_r} in <b>{pos_pct:.0f}%</b> of posterior samples — {verdict}</span>", font=dict(size=18)),
        xaxis_title="Score", yaxis_title="Density",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    if x_range:
        fig.update_xaxes(range=x_range)
    fig.update_yaxes(rangemode="tozero")
    return fig


def plot_expected_loss(samples_w, samples_r, name_w, name_r, x_range=None, cost_per_point=100000):
    """Plot Expected Loss: E(Loss|choose A) = mean(max(0, score_B - score_A))."""
    loss_choose_w = np.maximum(0, samples_r - samples_w)
    loss_choose_r = np.maximum(0, samples_w - samples_r)
    el_w = loss_choose_w.mean()
    el_r = loss_choose_r.mean()
    cpp = cost_per_point
    fig = go.Figure()
    
    def fmt_dollar(v):
        return f"${v:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    
    pos_w = loss_choose_w[loss_choose_w > 0]
    pos_r = loss_choose_r[loss_choose_r > 0]
    
    if len(pos_w) > 2:
        h_w, e_w = np.histogram(pos_w * cpp, bins=min(50, len(pos_w)), density=True)
        fig.add_trace(go.Scatter(x=(e_w[:-1]+e_w[1:])/2, y=h_w, mode='lines', fill='tozeroy',
            line=dict(color='#2ca02c', width=2), fillcolor='rgba(44,160,44,0.2)',
            name=f"Loss if choosing {name_w} (E={fmt_dollar(el_w*cpp)})"))
    if len(pos_r) > 2:
        h_r, e_r = np.histogram(pos_r * cpp, bins=min(50, len(pos_r)), density=True)
        fig.add_trace(go.Scatter(x=(e_r[:-1]+e_r[1:])/2, y=h_r, mode='lines', fill='tozeroy',
            line=dict(color='#d62728', width=2), fillcolor='rgba(214,39,40,0.2)',
            name=f"Loss if choosing {name_r} (E={fmt_dollar(el_r*cpp)})"))
    
    safer = name_w if el_w < el_r else name_r
    ratio = max(el_w, el_r) / max(min(el_w, el_r), 0.001)
    savings = abs(el_r - el_w) * cpp
    if el_w == 0 and el_r == 0:
        subtitle = f"<span style='font-size:16px'>Both ASPs have zero expected loss — identical performance</span>"
    elif el_w == 0:
        subtitle = f"<span style='font-size:16px'>{name_w} never loses to {name_r} — choosing {name_w} saves <b>{fmt_dollar(el_r*cpp)}</b> per single ASP task</span>"
    elif el_r == 0:
        subtitle = f"<span style='font-size:16px'>{name_r} never loses to {name_w} — choosing {name_r} saves <b>{fmt_dollar(el_w*cpp)}</b> per single ASP task</span>"
    else:
        subtitle = (f"<span style='font-size:16px'>E(Loss|{name_w}) = {fmt_dollar(el_w*cpp)} — E(Loss|{name_r}) = {fmt_dollar(el_r*cpp)}</span><br>"
            f"<span style='font-size:14px'>\U0001f6e1\ufe0f Safer: <b>{safer}</b> — saves <b>{fmt_dollar(savings)}</b> per single ASP task ({ratio:.1f}× less risk)</span>")
    
    fig.update_layout(height=350, margin=dict(t=120, b=60),
        title=dict(text=f"<b>Expected Loss (The \"Safety\" Metric)</b><br>{subtitle}", font=dict(size=18)),
        xaxis_title="Expected Loss ($)", yaxis_title="Density",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    if x_range:
        fig.update_xaxes(range=[0, (x_range[1] - x_range[0]) * cpp])
    fig.update_yaxes(rangemode="tozero")
    return fig, el_w, el_r


def plot_credible_interval(samples_w, samples_r, name_w, name_r, x_range=None):
    """Plot 95% Credible Intervals for both ASPs side by side."""
    ci_w = (np.percentile(samples_w, 2.5), np.percentile(samples_w, 97.5))
    ci_r = (np.percentile(samples_r, 2.5), np.percentile(samples_r, 97.5))
    mean_w, mean_r = samples_w.mean(), samples_r.mean()
    overlap = ci_w[0] < ci_r[1] and ci_r[0] < ci_w[1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[ci_w[0], ci_w[1]], y=[name_w, name_w], mode='lines+markers',
        line=dict(color='#2ca02c', width=6), marker=dict(size=12, symbol='line-ns', line_width=3),
        name=f"\U0001f947 {name_w} [{ci_w[0]:.3f}, {ci_w[1]:.3f}]"))
    fig.add_trace(go.Scatter(x=[mean_w], y=[name_w], mode='markers',
        marker=dict(size=14, color='#2ca02c', symbol='diamond'), showlegend=False))
    fig.add_trace(go.Scatter(x=[ci_r[0], ci_r[1]], y=[name_r, name_r], mode='lines+markers',
        line=dict(color='#d62728', width=6), marker=dict(size=12, symbol='line-ns', line_width=3),
        name=f"\U0001f948 {name_r} [{ci_r[0]:.3f}, {ci_r[1]:.3f}]"))
    fig.add_trace(go.Scatter(x=[mean_r], y=[name_r], mode='markers',
        marker=dict(size=14, color='#d62728', symbol='diamond'), showlegend=False))
    if overlap:
        ol_left = max(ci_w[0], ci_r[0])
        ol_right = min(ci_w[1], ci_r[1])
        fig.add_vrect(x0=ol_left, x1=ol_right, fillcolor="rgba(255,165,0,0.15)", line_width=0,
            annotation_text="overlap", annotation_position="top")
        verdict = f"\u26a0\ufe0f CIs overlap [{ol_left:.3f}, {ol_right:.3f}] \u2014 decision has uncertainty"
    else:
        verdict = f"\u2705 No CI overlap \u2014 {name_w} is clearly superior"
    fig.update_layout(height=300, margin=dict(t=120, b=60),
        title=dict(text=f"<b>95% Credible Intervals (The \"Range\" Proof)</b><br><span style='font-size:16px'>{verdict}</span>", font=dict(size=18)),
        xaxis_title="Score",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    if x_range:
        fig.update_xaxes(range=x_range)
    return fig, ci_w, ci_r, overlap


def plot_posterior_distributions(scorer, asp_id: str, metric: str = 'success_rate') -> go.Figure:
    """Plot full posterior distribution for a specific ASP and metric."""
    if scorer.trace is None:
        return go.Figure()
    
    asp_position = np.where(scorer.asp_ids == asp_id)[0][0]
    
    if metric == 'success_rate':
        samples = scorer.trace.posterior['success_rate'].values[:, :, asp_position].flatten()
        title = f"Success Rate Posterior Distribution - {asp_id}"
        xaxis_title = "Success Rate (probability)"
    elif metric == 'response_time':
        log_mu = scorer.trace.posterior['response_log_mu'].values[:, :, asp_position].flatten()
        samples = np.exp(log_mu)
        title = f"Response Time Posterior Distribution - {asp_id}"
        xaxis_title = "Response Time (hours)"
    elif metric == 'satisfaction':
        samples = scorer.trace.posterior['nps_mu'].values[:, :, asp_position].flatten() * 100
        title = f"NPS Posterior Distribution - {asp_id}"
        xaxis_title = "NPS (%)"
    else:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=samples,
        nbinsx=50,
        name='Posterior Samples',
        marker_color='steelblue',
        opacity=0.7
    ))
    
    # Add mean line
    mean_val = np.mean(samples)
    fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                  annotation_text=f"Mean: {mean_val:.3f}")
    
    # Add 95% CI lines
    ci_lower = np.percentile(samples, 2.5)
    ci_upper = np.percentile(samples, 97.5)
    fig.add_vline(x=ci_lower, line_dash="dot", line_color="orange",
                  annotation_text=f"2.5%: {ci_lower:.3f}", annotation_position="top left")
    fig.add_vline(x=ci_upper, line_dash="dot", line_color="orange",
                  annotation_text=f"97.5%: {ci_upper:.3f}", annotation_position="top right")
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title="Frequency",
        height=400,
        showlegend=False
    )
    
    return fig
