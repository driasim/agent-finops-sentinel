"""FinOps sentinel service tracking token budgets and blocking runaway costs."""

import uuid
from typing import Dict, List, Optional
from finops_sentinel.models import BudgetPolicy, SpendRecord, TenantUsageSummary


class BudgetExceededError(Exception):
    """Raised when an agent attempt exceeds tenant budget limits."""
    pass


class FinOpsSentinel:
    """Monitors real-time token spend and enforces budget ceilings."""

    def __init__(self):
        self.policies: Dict[str, BudgetPolicy] = {}
        self.spend_records: Dict[str, List[SpendRecord]] = {}

    def set_policy(self, policy: BudgetPolicy):
        self.policies[policy.tenant_id] = policy
        if policy.tenant_id not in self.spend_records:
            self.spend_records[policy.tenant_id] = []

    def check_and_record_spend(
        self,
        tenant_id: str,
        user_id: str,
        agent_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
    ) -> TenantUsageSummary:
        policy = self.policies.get(tenant_id)
        if not policy:
            # Default fallback policy if none configured
            policy = BudgetPolicy(tenant_id=tenant_id, daily_budget_usd=100.0)
            self.set_policy(policy)

        current_summary = self.get_summary(tenant_id)

        # Check hard cut-off
        if policy.hard_cutoff_enabled and (current_summary.total_spend_usd + cost_usd) > policy.daily_budget_usd:
            raise BudgetExceededError(
                f"Daily spend limit of ${policy.daily_budget_usd:.2f} exceeded for tenant '{tenant_id}'. Request rejected."
            )

        # Record spend
        rec = SpendRecord(
            record_id=f"rec-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            user_id=user_id,
            agent_id=agent_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=round(cost_usd, 6),
        )
        self.spend_records[tenant_id].append(rec)

        return self.get_summary(tenant_id)

    def get_summary(self, tenant_id: str) -> TenantUsageSummary:
        records = self.spend_records.get(tenant_id, [])
        policy = self.policies.get(tenant_id, BudgetPolicy(tenant_id=tenant_id))

        total_spend = sum(r.cost_usd for r in records)
        total_tokens = sum(r.prompt_tokens + r.completion_tokens for r in records)

        pct = (total_spend / policy.daily_budget_usd) * 100 if policy.daily_budget_usd > 0 else 0.0

        return TenantUsageSummary(
            tenant_id=tenant_id,
            total_spend_usd=round(total_spend, 4),
            total_tokens=total_tokens,
            budget_limit_usd=policy.daily_budget_usd,
            pct_consumed=round(pct, 1),
            is_throttled=(total_spend >= policy.daily_budget_usd),
            warning_triggered=(pct >= policy.soft_warning_threshold_pct),
        )
