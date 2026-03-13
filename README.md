# ASP Decision Intelligence Platform

A demonstration of decision intelligence concepts applied to Authorized Service Provider (ASP) selection in telecom networks.

## Modules

1. **Bayesian Analytics** - Probabilistic scoring with uncertainty quantification
2. **Causal Inference** - Understanding causal relationships (Coming soon)
3. **Reinforcement Learning** - Adaptive optimization (Coming soon)
4. **Multi-Agent System** - Collaborative decision making (Coming soon)

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Project Structure

```
ASP_DI/
├── app.py                 # Main Streamlit application
├── modules/
│   ├── module1_bayesian.py
│   ├── module2_causal.py
│   ├── module3_rl.py
│   └── module4_multiagent.py
├── data/
│   └── asp_data.py        # Sample data generation
├── utils/
│   └── visualization.py   # Shared visualization utilities
└── requirements.txt
```
