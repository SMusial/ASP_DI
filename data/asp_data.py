"""Generate sample ASP (Authorized Service Provider) data for demonstration."""

import numpy as np
import pandas as pd


def generate_asp_profiles(n_asps: int = 10, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic ASP profiles with base characteristics."""
    np.random.seed(seed)
    
    if n_asps == 3:
        # Specialized profiles for 3 ASPs
        return pd.DataFrame({
            'asp_id': ['ASP_A', 'ASP_B', 'ASP_C'],
            'specialization': [
                'Mountain Operations',
                'Standard Tasks',
                'High-Risk Climbing (OHS Restricted)'
            ],
            'region': ['Mountain', 'Urban', 'High-Altitude'],
            'years_experience': [12, 5, 15],
            'team_size': [15, 25, 10],
            'certified_technicians': [12, 18, 10],
            'weather_capability': ['Moderate', 'Good Weather Only', 'All Weather (Wind/Rain/Snow)'],
            'ohs_certified': [True, False, True]
        })
    else:
        # Generic profiles for other counts
        asp_names = [f"ASP_{chr(65+i)}" for i in range(n_asps)]
        regions = np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_asps)
        years_experience = np.random.randint(1, 15, n_asps)
        team_size = np.random.randint(5, 50, n_asps)
        
        return pd.DataFrame({
            'asp_id': asp_names,
            'region': regions,
            'years_experience': years_experience,
            'team_size': team_size,
            'certified_technicians': np.random.randint(2, team_size, n_asps)
        })


def generate_historical_performance(asp_profiles: pd.DataFrame, 
                                   n_tasks_per_asp=50,
                                   seed: int = 42) -> pd.DataFrame:
    """Generate historical task performance data for ASPs.
    
    Args:
        n_tasks_per_asp: int or dict. If dict, maps asp_id to task count.
    """
    np.random.seed(seed)
    
    records = []
    
    for _, asp in asp_profiles.iterrows():
        # Determine task count
        if isinstance(n_tasks_per_asp, dict):
            n_tasks = n_tasks_per_asp.get(asp['asp_id'], 30)
        else:
            n_tasks = n_tasks_per_asp
        
        # Differentiated performance based on specialization with HIGHER VARIANCE
        if asp['asp_id'] == 'ASP_A':
            # Mountain operations - moderate success, slower response, MODERATE VARIANCE
            base_quality = 0.72
            response_multiplier = 1.5
            satisfaction_base = 3.8
            quality_variance = 0.15  # moderate variance
        elif asp['asp_id'] == 'ASP_B':
            # Standard tasks - high success on simple, fast response, LOW VARIANCE (consistent)
            base_quality = 0.88
            response_multiplier = 0.6
            satisfaction_base = 4.6
            quality_variance = 0.08  # low variance - very consistent
        elif asp['asp_id'] == 'ASP_C':
            # High-risk climbing - lower success, variable response, HIGH VARIANCE (weather dependent)
            base_quality = 0.60
            response_multiplier = 2.2
            satisfaction_base = 3.5
            quality_variance = 0.25  # high variance - weather dependent
        else:
            # Generic
            base_quality = 0.5 + (asp['years_experience'] / 30) + (asp['certified_technicians'] / 100)
            base_quality = min(base_quality, 0.95)
            response_multiplier = 1.0
            satisfaction_base = 4.0
            quality_variance = 0.12
        
        for task_id in range(n_tasks):
            complexity = np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.5, 0.2])
            
            # ASP-specific complexity handling
            if asp['asp_id'] == 'ASP_B' and complexity == 'High':
                complexity_factor = 0.45  # Struggles significantly with complex tasks
            elif asp['asp_id'] == 'ASP_C' and complexity == 'High':
                complexity_factor = 0.90  # Excels at high complexity
            else:
                complexity_factor = {'Low': 1.0, 'Medium': 0.85, 'High': 0.65}[complexity]
            
            # Add variance to quality for each task
            task_quality = base_quality + np.random.normal(0, quality_variance)
            task_quality = np.clip(task_quality, 0.1, 0.99)
            
            success_prob = task_quality * complexity_factor
            success = np.random.random() < success_prob
            
            # Add variance to response time
            response_time = np.random.gamma(2, 1/task_quality) * response_multiplier * (1 + 0.5 * (complexity == 'High'))
            response_time *= np.random.uniform(0.7, 1.3)  # Additional variance
            
            base_cost = {'Low': 500, 'Medium': 1500, 'High': 3000}[complexity]
            cost = base_cost * np.random.uniform(0.8, 1.2) * (1 + 0.1 * task_quality)
            
            if success:
                satisfaction = np.random.normal(satisfaction_base - (response_time / 20), 0.6)
            else:
                satisfaction = np.random.normal(2.3, 0.8)
            satisfaction = np.clip(satisfaction, 1, 5)
            
            records.append({
                'asp_id': asp['asp_id'],
                'task_id': f"{asp['asp_id']}_T{task_id}",
                'complexity': complexity,
                'success': success,
                'response_time_hours': round(response_time, 2),
                'cost': round(cost, 2),
                'customer_satisfaction': round(satisfaction, 2),
                'sla_met': response_time < 24 and success
            })
    
    return pd.DataFrame(records)
