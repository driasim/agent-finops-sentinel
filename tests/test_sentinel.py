"""Unit tests for agent-finops-sentinel."""

import pytest
from finops_sentinel.models import BudgetPolicy
from finops_sentinel.sentinel import FinOpsSentinel, BudgetExceededError


def test_spend_recording():
    sentinel = FinOpsSentinel()
    policy = BudgetPolicy(tenant_id="dev-team", daily_budget_usd=10.0)
    sentinel.set_policy(policy)

    summary = sentinel.check_and_record_spend(
        tenant_id="dev-team",
        user_id="alice",
        agent_id="coding-bot",
        model="gpt-4o",
        prompt_tokens=1000,
        completion_tokens=200,
        cost_usd=0.005,
    )
    assert summary.total_spend_usd == 0.005
    assert summary.is_throttled is False
    assert summary.warning_triggered is False


def test_soft_warning_threshold():
    sentinel = FinOpsSentinel()
    policy = BudgetPolicy(tenant_id="dev-team", daily_budget_usd=1.00, soft_warning_threshold_pct=80.0)
    sentinel.set_policy(policy)

    summary = sentinel.check_and_record_spend(
        tenant_id="dev-team",
        user_id="alice",
        agent_id="coding-bot",
        model="gpt-4o",
        prompt_tokens=5000,
        completion_tokens=1000,
        cost_usd=0.85,
    )
    assert summary.warning_triggered is True
    assert summary.is_throttled is False


def test_hard_cutoff_blocks_runaway_agent():
    sentinel = FinOpsSentinel()
    policy = BudgetPolicy(tenant_id="dev-team", daily_budget_usd=0.50, hard_cutoff_enabled=True)
    sentinel.set_policy(policy)

    # First call within budget
    sentinel.check_and_record_spend(
        tenant_id="dev-team",
        user_id="alice",
        agent_id="looping-bot",
        model="gpt-4o",
        prompt_tokens=2000,
        completion_tokens=500,
        cost_usd=0.40,
    )

    # Second call breaches limit -> throws BudgetExceededError
    with pytest.raises(BudgetExceededError):
        sentinel.check_and_record_spend(
            tenant_id="dev-team",
            user_id="alice",
            agent_id="looping-bot",
            model="gpt-4o",
            prompt_tokens=2000,
            completion_tokens=500,
            cost_usd=0.20,
        )
