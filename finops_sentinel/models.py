"""Data models for budget tracking and tenant spend allocation."""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BudgetPolicy(BaseModel):
    tenant_id: str
    daily_budget_usd: float = 50.0
    monthly_budget_usd: float = 1000.0
    soft_warning_threshold_pct: float = 80.0
    hard_cutoff_enabled: bool = True


class SpendRecord(BaseModel):
    record_id: str
    tenant_id: str
    user_id: str
    agent_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TenantUsageSummary(BaseModel):
    tenant_id: str
    total_spend_usd: float = 0.0
    total_tokens: int = 0
    budget_limit_usd: float
    pct_consumed: float = 0.0
    is_throttled: bool = False
    warning_triggered: bool = False
