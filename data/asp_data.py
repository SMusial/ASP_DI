"""Generate sample ASP (Authorized Service Provider) data for demonstration."""

import numpy as np
import pandas as pd


def generate_asp_profiles(n_asps: int = 10, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic ASP profiles with base characteristics."""
    np.random.seed(seed)
    
    if n_asps == 6:
        # Specialized profiles for 6 ASPs (2 per category)
        return pd.DataFrame({
            'asp_id': ['ASP_Mount1', 'ASP_Mount2', 'ASP_Std1', 'ASP_Std2', 'ASP_Climb1', 'ASP_Climb2'],
            'specialization': [
                'Mountain Operations', 'Mountain Operations',
                'Standard Urban Tasks', 'Standard Urban Tasks',
                'High-Risk Climbing (OHS)', 'High-Risk Climbing (OHS)'
            ],
            'region': ['Mountain', 'Mountain', 'Urban', 'Urban', 'High-Altitude', 'High-Altitude'],
            'years_experience': [12, 8, 5, 3, 15, 10],
            'team_size': [15, 10, 25, 20, 10, 8],
            'certified_technicians': [12, 8, 18, 15, 10, 7],
            'weather_capability': [
                'Moderate', 'Moderate',
                'Good Weather Only', 'Good Weather Only',
                'All Weather (Wind/Rain/Snow)', 'All Weather (Wind/Rain/Snow)'
            ],
            'ohs_certified': [True, True, False, False, True, True]
        })
    elif n_asps == 3:
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
        asp_id = asp['asp_id']
        
        # Mountain Operations
        if asp_id == 'ASP_Mount1':
            base_quality = 0.75
            response_multiplier = 1.4
            satisfaction_base = 8.0
            quality_variance = 0.12
        elif asp_id == 'ASP_Mount2':
            base_quality = 0.68  # Less experienced
            response_multiplier = 1.6
            satisfaction_base = 7.4
            quality_variance = 0.18
        
        # Standard Urban Tasks
        elif asp_id == 'ASP_Std1':
            base_quality = 0.90
            response_multiplier = 0.6
            satisfaction_base = 9.4
            quality_variance = 0.07
        elif asp_id == 'ASP_Std2':
            base_quality = 0.82  # Less experienced
            response_multiplier = 0.8
            satisfaction_base = 8.6
            quality_variance = 0.12
        
        # High-Risk Climbing
        elif asp_id == 'ASP_Climb1':
            base_quality = 0.65
            response_multiplier = 2.0
            satisfaction_base = 7.4
            quality_variance = 0.22
        elif asp_id == 'ASP_Climb2':
            base_quality = 0.55  # Less experienced
            response_multiplier = 2.5
            satisfaction_base = 6.6
            quality_variance = 0.30
        
        # Legacy 3-ASP support
        elif asp_id == 'ASP_A':
            base_quality = 0.72
            response_multiplier = 1.5
            satisfaction_base = 7.6
            quality_variance = 0.15
        elif asp_id == 'ASP_B':
            base_quality = 0.88
            response_multiplier = 0.6
            satisfaction_base = 9.2
            quality_variance = 0.08
        elif asp_id == 'ASP_C':
            base_quality = 0.60
            response_multiplier = 2.2
            satisfaction_base = 7.0
            quality_variance = 0.25
        
        # Generic fallback
        else:
            base_quality = 0.5 + (asp['years_experience'] / 30) + (asp['certified_technicians'] / 100)
            base_quality = min(base_quality, 0.95)
            response_multiplier = 1.0
            satisfaction_base = 8.0
            quality_variance = 0.12
        
        for task_id in range(n_tasks):
            complexity = np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.5, 0.2])
            
            # ASP-specific complexity handling
            if 'Std' in asp_id and complexity == 'High':
                complexity_factor = 0.45  # Standard ASPs struggle with complex tasks
            elif 'Climb' in asp_id and complexity == 'High':
                complexity_factor = 0.90  # Climbing ASPs excel at high complexity
            elif 'Mount' in asp_id and complexity == 'High':
                complexity_factor = 0.75  # Mountain ASPs moderate at high complexity
            else:
                complexity_factor = {'Low': 1.0, 'Medium': 0.85, 'High': 0.65}[complexity]
            
            # Add variance to quality for each task
            task_quality = base_quality + np.random.normal(0, quality_variance)
            task_quality = np.clip(task_quality, 0.1, 0.99)
            
            success_prob = task_quality * complexity_factor
            success = np.random.random() < success_prob
            
            # Add variance to response time (reduced right skew)
            response_time = np.random.gamma(3, 0.5/task_quality) * response_multiplier * (1 + 0.3 * (complexity == 'High'))
            response_time *= np.random.uniform(0.85, 1.15)
            response_time = min(response_time, 12.0)  # cap at 12h
            
            # Cost: Climb highest, Mount middle, Std lowest
            if 'Climb' in asp_id:
                cost_multiplier = 2.5
            elif 'Mount' in asp_id:
                cost_multiplier = 1.3
            else:
                cost_multiplier = 1.0
            base_cost = {'Low': 500, 'Medium': 1500, 'High': 3000}[complexity]
            cost = base_cost * cost_multiplier * np.random.uniform(0.8, 1.2)
            
            if success:
                satisfaction = np.random.normal(satisfaction_base - (response_time / 10), 1.2)
            else:
                satisfaction = np.random.normal(4.0, 1.5)
            satisfaction = np.clip(satisfaction, 0, 10)
            
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
