# Dashboard Clarifications - Module 1

## Section Clarifications (Input vs Output)

### a) 📁 View Historical Data - **INPUT (Prior Knowledge)**
**Type**: INPUT to the Bayesian model
**Description**: Historical performance data from past ASP tasks
**Contains**:
- ASP Profiles: Specializations, experience, team size, certifications
- Performance Summary: Aggregated success rates, response times, satisfaction scores
**Purpose**: This is your "prior knowledge" - the evidence the Bayesian model uses to learn about ASP performance patterns

**Key Point**: This is NOT a Bayesian prior in the technical sense (those are the Gamma/Beta distributions in the code), but rather the observed data that updates those priors into posteriors.

---

### b) ⚙️ Model Configuration - **INPUT (Hyperparameters)**
**Type**: INPUT to the scoring function
**Description**: User-defined weights that control how metrics are combined
**Contains**:
- Success Rate Weight (0.0 - 1.0): How important is task completion?
- Response Time Weight (0.0 - 1.0): How important is speed?
- Customer Satisfaction Weight (0.0 - 1.0): How important is customer feedback?

**Purpose**: These hyperparameters let you adapt the model to your business priorities without retraining

**Key Point**: These are NOT learned by the model - they are business decisions you make based on current priorities (e.g., SLA commitments, customer retention goals)

---

### c) 📈 ASP Bayesian Scores with Uncertainty - **OUTPUT (Sampled Posterior)**
**Type**: OUTPUT from Bayesian inference
**Description**: Posterior probability distributions sampled via MCMC (Markov Chain Monte Carlo)
**Contains**:
- Overall scores for each ASP (weighted combination of metrics)
- Error bars showing 95% credible intervals
- Uncertainty quantification (±values)

**Purpose**: These are the model's predictions AFTER seeing the historical data

**Technical Details**:
- 500 MCMC samples drawn from posterior distributions
- Each sample represents a plausible set of parameter values
- Mean of samples = point estimate
- 2.5th and 97.5th percentiles = 95% credible interval

**Key Point**: This IS the sampled posterior - the probability distribution of ASP scores given the observed data

---

### d) Detailed Metric Analysis - **OUTPUT (Posterior Distributions)**
**Type**: OUTPUT from Bayesian inference
**Description**: Individual metric posteriors for each ASP

**Three Metrics with Units**:

1. **Success Rate (probability, 0-1)**
   - Unit: Probability (0.0 = never succeeds, 1.0 = always succeeds)
   - Example: 0.85 = 85% success rate
   - 95% CI shows uncertainty range

2. **Response Time (hours)**
   - Unit: Hours
   - Example: 4.5 hours = average time from task assignment to completion
   - 95% CI: [3.2h, 6.1h] means true average likely between 3.2 and 6.1 hours

3. **Customer Satisfaction (1-5 scale)**
   - Unit: Rating on 1-5 scale (1 = very dissatisfied, 5 = very satisfied)
   - Example: 4.2/5 = customers are generally satisfied
   - 95% CI shows uncertainty in true satisfaction level

**Purpose**: Drill down into specific performance dimensions to understand WHY an ASP scored high/low

---

## Units Summary Table

| Metric | Unit | Range | Interpretation |
|--------|------|-------|----------------|
| Success Rate | Probability | 0.0 - 1.0 | 0.85 = 85% of tasks completed successfully |
| Response Time | Hours | 0+ | 4.5 = average 4.5 hours to complete task |
| Customer Satisfaction | Rating | 1 - 5 | 4.2 = customers rate service 4.2 out of 5 |
| Overall Score | Weighted combination | 0.0 - 1.0 | Higher = better overall performance |
| Uncertainty | ± Score units | 0+ | ±0.05 = score could vary by 0.05 in either direction |

---

## Variance Between ASPs

### Updated Data Generation for Higher Differentiation:

**ASP_A (Mountain Operations)**:
- Base success: 72% (moderate)
- Response multiplier: 1.5x (slower due to terrain)
- Satisfaction baseline: 3.8/5
- **Variance: MODERATE (±15%)** - terrain variability

**ASP_B (Standard Tasks)**:
- Base success: 88% (high)
- Response multiplier: 0.6x (fast)
- Satisfaction baseline: 4.6/5
- **Variance: LOW (±8%)** - very consistent, predictable work

**ASP_C (High-Risk Climbing)**:
- Base success: 60% (lower due to difficulty)
- Response multiplier: 2.2x (much slower, weather dependent)
- Satisfaction baseline: 3.5/5
- **Variance: HIGH (±25%)** - weather and conditions create high variability

### Why Different Variances Matter:
- **ASP_B**: Narrow credible intervals (reliable, predictable)
- **ASP_C**: Wide credible intervals (high uncertainty, risky choice)
- **ASP_A**: Medium credible intervals (moderate risk)

This variance differentiation is now visible in:
1. Error bars on the scores chart (ASP_C has longest bars)
2. Width of credible intervals in the table
3. Uncertainty values in Key Insights

---

## Key Insights Synchronization

The Key Insights section now dynamically pulls:

✅ **Current hyperparameter values** from sliders
✅ **Actual ASP scores** from Bayesian inference results
✅ **Actual success rates** with 95% CIs
✅ **Actual response times** with 95% CIs (in hours)
✅ **Actual satisfaction scores** with 95% CIs (1-5 scale)
✅ **ASP specializations** from profile data
✅ **Uncertainty rankings** (highest/lowest uncertainty ASPs)
✅ **All three ASPs** ranked with full metrics

**Updates automatically when**:
- You change slider values
- You re-run the analysis
- Data is regenerated

---

## Bayesian Workflow Summary

```
INPUT (Historical Data)
    ↓
[Bayesian Model with Priors]
    ↓
MCMC Sampling (500 iterations)
    ↓
OUTPUT (Posterior Distributions)
    ↓
INPUT (Hyperparameters/Weights)
    ↓
Weighted Scoring Function
    ↓
OUTPUT (Final ASP Rankings)
```

---

## Business Value Speech

See `BAYESIAN_BUSINESS_VALUE.md` for the complete 10-sentence executive summary and detailed ROI analysis.

**Key Takeaway**: Bayesian analytics delivers measurable business value through:
1. Risk-aware decisions (uncertainty quantification)
2. Data efficiency (works with limited history)
3. Adaptive prioritization (instant re-weighting)
4. Transparent explainability (stakeholder trust)
5. Continuous learning (always up-to-date)

**ROI Example**: $575,000 annual value from reduced selection errors, faster procurement, better SLA compliance, and improved customer satisfaction.
