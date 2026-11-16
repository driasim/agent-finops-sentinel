# `agent-finops-sentinel` 💰

[![CI](https://github.com/driasim/agent-finops-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/driasim/agent-finops-sentinel/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Real-time token budget enforcement, FinOps cost attribution, and runaway spend prevention for LLM agents.**

Without strict financial controls, a single looping or misconfigured LLM agent can consume thousands of dollars in API credits overnight.

`agent-finops-sentinel` monitors prompt/completion tokens and dollar costs in real-time across organizations, departments, and users. It alerts teams at soft thresholds (80%) and trips a **hard cut-off** to block rogue agents before financial runaway occurs.

---

## ⚡ Quickstart

### Installation

```bash
git clone https://github.com/driasim/agent-finops-sentinel.git
cd agent-finops-sentinel
pip install -e .
```

### Python SDK Usage

```python
from finops_sentinel.models import BudgetPolicy
from finops_sentinel.sentinel import FinOpsSentinel, BudgetExceededError

sentinel = FinOpsSentinel()

# 1. Define Department Policy
sentinel.set_policy(
    BudgetPolicy(
        tenant_id="customer-support",
        daily_budget_usd=25.00,
        soft_warning_threshold_pct=80.0,
        hard_cutoff_enabled=True,
    )
)

# 2. Record Agent Spend
try:
    summary = sentinel.check_and_record_spend(
        tenant_id="customer-support",
        user_id="alice",
        agent_id="support-bot-1",
        model="gpt-4o",
        prompt_tokens=1500,
        completion_tokens=250,
        cost_usd=0.007,
    )
    print(f"Consumed: {summary.pct_consumed}% of daily budget.")
except BudgetExceededError as e:
    print("Agent request blocked to protect budget:", e)
```

---

## 🧪 Running Tests

```bash
pytest -v tests/
```

---

## 📄 License
MIT © Ibrahim Aliyu Saddique (`@driasim`)
