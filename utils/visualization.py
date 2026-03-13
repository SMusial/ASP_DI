"""Visualization utilities for the ASP Decision Intelligence platform."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def plot_asp_scores_with_uncertainty(scores_df: pd.DataFrame) -> go.Figure:
    """Plot ASP scores with uncertainty intervals."""
    fig = go.Figure()
    
    scores_df = scores_df.sort_values('score', ascending=True)
    
    fig.add_trace(go.Bar(
        y=scores_df['asp_id'],
        x=scores_df['score'],
        orientation='h',
        error_x=dict(
            type='data',
            array=scores_df['uncertainty'],
            visible=True
        ),
        marker=dict(
            color=scores_df['score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Score")
        ),
        text=scores_df['score'].round(3),
        textposition='auto',
    ))
    
    fig.update_layout(
        title="ASP Bayesian Scores with Uncertainty",
        xaxis_title="Score (0-1)",
        yaxis_title="ASP",
        height=400,
        showlegend=False
    )
    
    return fig


def plot_metric_distributions(scores_df: pd.DataFrame, metric: str) -> go.Figure:
    """Plot distribution of a specific metric across ASPs with credible intervals."""
    fig = go.Figure()
    
    mean_col = f'{metric}_mean'
    ci_col = f'{metric}_ci'
    
    scores_df = scores_df.sort_values(mean_col, ascending=False)
    
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
        'satisfaction': 'Customer Satisfaction (1-5)'
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
        'customer_satisfaction': 'mean',
        'cost': 'mean'
    }).reset_index()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Success Rate', 'Avg Response Time (hrs)', 
                       'Customer Satisfaction', 'Avg Cost ($)')
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
        go.Bar(x=summary['asp_id'], y=summary['customer_satisfaction'], 
               name='Satisfaction', marker_color='lightgreen'),
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
    # Calculate simple averages
    simple_avg = historical_data.groupby('asp_id').agg({
        'success': 'mean',
        'response_time_hours': 'mean',
        'customer_satisfaction': 'mean'
    }).reset_index()
    
    # Merge with Bayesian results
    comparison = scores_df[['asp_id', 'success_rate_mean', 'response_time_mean', 
                            'satisfaction_mean', 'uncertainty']].merge(
        simple_avg, on='asp_id'
    )
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Success Rate', 'Response Time (hours)', 'Satisfaction (1-5)')
    )
    
    # Success Rate
    fig.add_trace(
        go.Bar(x=comparison['asp_id'], y=comparison['success'], 
               name='Simple Average', marker_color='lightgray', showlegend=True),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=comparison['asp_id'], y=comparison['success_rate_mean'],
                   mode='markers', marker=dict(size=12, color='blue', symbol='diamond'),
                   name='Bayesian Mean', showlegend=True),
        row=1, col=1
    )
    
    # Response Time
    fig.add_trace(
        go.Bar(x=comparison['asp_id'], y=comparison['response_time_hours'],
               name='Simple Average', marker_color='lightgray', showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=comparison['asp_id'], y=comparison['response_time_mean'],
                   mode='markers', marker=dict(size=12, color='blue', symbol='diamond'),
                   name='Bayesian Mean', showlegend=False),
        row=1, col=2
    )
    
    # Satisfaction
    fig.add_trace(
        go.Bar(x=comparison['asp_id'], y=comparison['customer_satisfaction'],
               name='Simple Average', marker_color='lightgray', showlegend=False),
        row=1, col=3
    )
    fig.add_trace(
        go.Scatter(x=comparison['asp_id'], y=comparison['satisfaction_mean'],
                   mode='markers', marker=dict(size=12, color='blue', symbol='diamond'),
                   name='Bayesian Mean', showlegend=False),
        row=1, col=3
    )
    
    fig.update_layout(
        height=400,
        title_text="Bayesian vs Simple Average Comparison",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


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
        response_shape = scorer.trace.posterior['response_shape'].values[:, :, asp_position].flatten()
        response_rate = scorer.trace.posterior['response_rate'].values[:, :, asp_position].flatten()
        samples = response_shape / response_rate
        title = f"Response Time Posterior Distribution - {asp_id}"
        xaxis_title = "Response Time (hours)"
    elif metric == 'satisfaction':
        samples = scorer.trace.posterior['satisfaction_mu'].values[:, :, asp_position].flatten()
        title = f"Satisfaction Posterior Distribution - {asp_id}"
        xaxis_title = "Satisfaction (1-5 scale)"
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
