"""Demonstration of real-time agent token budgeting and spend protection."""

from rich.console import Console
from rich.table import Table
from finops_sentinel.models import BudgetPolicy
from finops_sentinel.sentinel import FinOpsSentinel, BudgetExceededError

console = Console()

def run():
    sentinel = FinOpsSentinel()
    policy = BudgetPolicy(
        tenant_id="customer-support-agents",
        daily_budget_usd=5.00,
        soft_warning_threshold_pct=80.0,
        hard_cutoff_enabled=True,
    )
    sentinel.set_policy(policy)

    console.print("\n[bold blue]=== Simulating Agent Spend Stream ===[/bold blue]")

    simulated_calls = [
        ("user_1", "gpt-4o", 25000, 3000, 1.20),
        ("user_2", "gpt-4o", 50000, 6000, 2.40),
        ("user_3", "gpt-4o", 20000, 2000, 0.90), # Pushes over 80% (Warning)
        ("user_4", "gpt-4o", 30000, 5000, 1.50), # Breaches 100% (Hard cutoff)
    ]

    for uid, model, p_tokens, c_tokens, cost in simulated_calls:
        try:
            summary = sentinel.check_and_record_spend(
                tenant_id="customer-support-agents",
                user_id=uid,
                agent_id="support-agent-v1",
                model=model,
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                cost_usd=cost,
            )
            status = "[yellow]WARNING (>80%)[/yellow]" if summary.warning_triggered else "[green]OK[/green]"
            console.print(f"Recorded ${cost:.2f} for {uid} | Total Spent: ${summary.total_spend_usd:.2f} ({summary.pct_consumed}%) | Status: {status}")
        except BudgetExceededError as err:
            console.print(f"[bold red]⛔ HARD CUTOFF TRIGGERED on {uid}:[/bold red] {err}")

    final_summary = sentinel.get_summary("customer-support-agents")
    table = Table(title="Tenant Budget Final Report")
    table.add_column("Tenant ID")
    table.add_column("Spend (USD)")
    table.add_column("Budget Limit")
    table.add_column("Tokens Processed")
    table.add_column("State")

    table.add_row(
        final_summary.tenant_id,
        f"${final_summary.total_spend_usd:.2f}",
        f"${final_summary.budget_limit_usd:.2f}",
        str(final_summary.total_tokens),
        "[red]BLOCKED[/red]" if final_summary.is_throttled else "[green]ACTIVE[/green]",
    )
    console.print("\n")
    console.print(table)

if __name__ == "__main__":
    run()
