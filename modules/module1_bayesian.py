"""Module 1: Bayesian Analytics for ASP Selection."""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from typing import Dict, Tuple


class BayesianASPScorer:
    """Bayesian model for ASP performance scoring with uncertainty."""
    
    def __init__(self):
        self.model = None
        self.trace = None
        self.asp_ids = None
        
    def fit(self, historical_data: pd.DataFrame, n_samples: int = 500):
        """Fit Bayesian model to historical ASP performance data."""
        self.asp_ids = historical_data['asp_id'].unique()
        cat = pd.Categorical(historical_data['asp_id'])
        asp_idx = cat.codes
        self.asp_ids = np.array(cat.categories)
        
        with pm.Model() as self.model:
            # Success rate: Beta-Binomial (conjugate prior)
            alpha_success = pm.Gamma('alpha_success', alpha=1, beta=0.5, shape=len(self.asp_ids))
            beta_success = pm.Gamma('beta_success', alpha=1, beta=0.5, shape=len(self.asp_ids))
            
            success_rate = pm.Beta('success_rate', alpha=alpha_success, beta=beta_success, 
                                  shape=len(self.asp_ids))
            
            pm.Bernoulli('success_obs', p=success_rate[asp_idx], 
                        observed=historical_data['success'].values)
            
            # Response time: LogNormal (always positive, right-skewed)
            # Prior: median ≈ 3h, σ=1
            response_log_mu = pm.Normal('response_log_mu', mu=np.log(3), sigma=1, shape=len(self.asp_ids))
            response_log_sigma = pm.HalfNormal('response_log_sigma', sigma=1, shape=len(self.asp_ids))
            
            pm.Lognormal('response_obs', mu=response_log_mu[asp_idx], sigma=response_log_sigma[asp_idx],
                     observed=historical_data['response_time_hours'].values)
            
            # Satisfaction: Truncated Normal (0-10 NPS scale), prior μ=7, σ=3
            satisfaction_mu = pm.TruncatedNormal('satisfaction_mu', mu=7, sigma=3, lower=0, upper=10, shape=len(self.asp_ids))
            satisfaction_sigma = pm.HalfNormal('satisfaction_sigma', sigma=2, shape=len(self.asp_ids))
            
            pm.TruncatedNormal('satisfaction_obs', mu=satisfaction_mu[asp_idx], 
                     sigma=satisfaction_sigma[asp_idx], lower=0, upper=10,
                     observed=historical_data['customer_satisfaction'].values)
            
            self.trace = pm.sample(n_samples, tune=500, return_inferencedata=True, 
                                  random_seed=42, progressbar=False, cores=1,
                                  target_accept=0.95)
    
    def predict_performance(self, asp_id: str) -> Dict[str, Tuple[float, float, float]]:
        """Predict performance metrics for an ASP with uncertainty bounds."""
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        asp_position = np.where(self.asp_ids == asp_id)[0][0]
        
        success_samples = self.trace.posterior['success_rate'].values[:, :, asp_position].flatten()
        # LogNormal: exp(log_mu) gives median response time in hours
        log_mu_samples = self.trace.posterior['response_log_mu'].values[:, :, asp_position].flatten()
        response_samples = np.exp(log_mu_samples)  # median of lognormal
        satisfaction_samples = self.trace.posterior['satisfaction_mu'].values[:, :, asp_position].flatten()
        
        def get_stats(samples):
            return (np.mean(samples), 
                   np.percentile(samples, 2.5), 
                   np.percentile(samples, 97.5))
        
        return {
            'success_rate': get_stats(success_samples),
            'response_time': get_stats(response_samples),
            'satisfaction': get_stats(satisfaction_samples)
        }
    
    def score_asps(self, weights: Dict[str, float] = None) -> pd.DataFrame:
        """Score all ASPs using weighted combination of metrics."""
        if weights is None:
            weights = {'success_rate': 0.4, 'response_time': 0.3, 'satisfaction': 0.3}
        
        results = []
        
        for asp_id in self.asp_ids:
            metrics = self.predict_performance(asp_id)
            
            success_norm = metrics['success_rate'][0]
            response_norm = 1 / (1 + metrics['response_time'][0] / 10)
            satisfaction_norm = metrics['satisfaction'][0] / 10
            
            score = (weights['success_rate'] * success_norm + 
                    weights['response_time'] * response_norm +
                    weights['satisfaction'] * satisfaction_norm)
            
            uncertainty = np.mean([
                metrics['success_rate'][2] - metrics['success_rate'][1],
                (metrics['response_time'][2] - metrics['response_time'][1]) / 10,
                (metrics['satisfaction'][2] - metrics['satisfaction'][1]) / 10
            ])
            
            results.append({
                'asp_id': asp_id,
                'score': score,
                'uncertainty': uncertainty,
                'success_rate_mean': metrics['success_rate'][0],
                'success_rate_ci': (metrics['success_rate'][1], metrics['success_rate'][2]),
                'response_time_mean': metrics['response_time'][0],
                'response_time_ci': (metrics['response_time'][1], metrics['response_time'][2]),
                'satisfaction_mean': metrics['satisfaction'][0],
                'satisfaction_ci': (metrics['satisfaction'][1], metrics['satisfaction'][2])
            })
        
        df = pd.DataFrame(results)
        return df.sort_values('score', ascending=False).reset_index(drop=True)
