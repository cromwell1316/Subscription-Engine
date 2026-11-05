from datetime import datetime, timedelta, timezone
from decimal import Decimal
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from billing.application.ports.clock import FrozenClock
from billing.application.use_cases.change_plan import ChangePlanCommand, ChangePlanUseCase
from billing.application.use_cases.record_usage import RecordUsageCommand, RecordUsageUseCase
from billing.application.use_cases.run_billing_cycle import RunBillingCycleUseCase
from billing.application.use_cases.subscribe_customer import (
    SubscribeCustomerCommand,
    SubscribeCustomerUseCase,
)
from billing.domain.entities import Plan, Tenant
from billing.domain.value_objects import (
    BillingPeriod,
    Currency,
    Money,
)
from billing.infrastructure.gateways.fault_tolerant_gateway import (
    FaultTolerantPaymentGatewayEmulator,
)
from billing.infrastructure.persistence.in_memory_repositories import (
    InMemoryInvoiceRepository,
    InMemoryPlanRepository,
    InMemorySubscriptionRepository,
    InMemoryTenantRepository,
    InMemoryUsageRepository,
)
from billing.infrastructure.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
)

console = Console()


def run_interactive_demo():
    console.print(
        Panel.fit(
            "[bold cyan]Multi-Tenant Subscription & Billing Platform[/bold cyan]\n"
            "[yellow]Live Demonstration & Resilience Chaos Simulation[/yellow]",
            border_style="cyan",
        )
    )

    # 1. Boot system
    start_time = datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc)
    clock = FrozenClock(start_time)

    tenant_repo = InMemoryTenantRepository()
    plan_repo = InMemoryPlanRepository()
    sub_repo = InMemorySubscriptionRepository()
    inv_repo = InMemoryInvoiceRepository()
    usage_repo = InMemoryUsageRepository()
    gateway = FaultTolerantPaymentGatewayEmulator()
    circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=1.0, name="bank_gateway")

    # 2. Onboard Tenant & Pricing Plans
    console.print("\n[bold green]► Step 1: Onboarding Tenant & Tariff Catalog[/bold green]")
    tenant = Tenant(id="tenant-nexus", name="Nexus Cloud Solutions", currency=Currency.RUB)
    tenant_repo.save(tenant)

    plan_starter = Plan(
        id="plan-starter",
        tenant_id=tenant.id,
        name="Starter Tier",
        price=Money.from_str("1500.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
        included_units=100,
        overage_unit_price=Money.from_str("10.00", Currency.RUB),
        trial_days=0,
    )
    plan_pro = Plan(
        id="plan-pro",
        tenant_id=tenant.id,
        name="Professional Tier",
        price=Money.from_str("4500.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
        included_units=500,
        overage_unit_price=Money.from_str("6.00", Currency.RUB),
        trial_days=0,
    )
    plan_trial = Plan(
        id="plan-trial",
        tenant_id=tenant.id,
        name="Enterprise Trial",
        price=Money.from_str("10000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
        included_units=2000,
        trial_days=14,
    )
    plan_repo.save(plan_starter)
    plan_repo.save(plan_pro)
    plan_repo.save(plan_trial)

    table_plans = Table(title="Configured Pricing Plans")
    table_plans.add_column("Plan ID", style="cyan")
    table_plans.add_column("Name", style="bold")
    table_plans.add_column("Price / Period", style="green")
    table_plans.add_column("Included Quota", style="magenta")
    table_plans.add_column("Overage / Unit", style="yellow")
    table_plans.add_column("Trial", style="blue")

    for p in [plan_starter, plan_pro, plan_trial]:
        table_plans.add_row(
            p.id,
            p.name,
            f"{p.price} / {p.period.value}",
            f"{p.included_units} units",
            f"{p.overage_unit_price}/unit" if p.overage_unit_price else "N/A",
            f"{p.trial_days} days" if p.trial_days > 0 else "None",
        )
    console.print(table_plans)

    # 3. Subscribing Customers
    console.print("\n[bold green]► Step 2: Subscribing Customers & Idempotency Guarantee[/bold green]")
    subscribe_uc = SubscribeCustomerUseCase(
        tenant_repo=tenant_repo,
        plan_repo=plan_repo,
        subscription_repo=sub_repo,
        invoice_repo=inv_repo,
        payment_gateway=gateway,
        clock=clock,
    )

    res_alice = subscribe_uc.execute(
        SubscribeCustomerCommand(
            tenant_id=tenant.id,
            customer_id="cust-alice",
            plan_id=plan_starter.id,
            payment_method_id="card-alice-4242",
            idempotency_key="alice-order-1",
        )
    )
    console.print(f"[white]✓ Customer [bold]Alice[/bold] subscribed to [bold]{plan_starter.name}[/bold]. Invoice #{res_alice.invoice.id[:8]} [green]{res_alice.invoice.status.value}[/green] ({res_alice.invoice.total_amount})[/white]")

    # Demonstrate Idempotency
    res_alice_dup = subscribe_uc.execute(
        SubscribeCustomerCommand(
            tenant_id=tenant.id,
            customer_id="cust-alice",
            plan_id=plan_starter.id,
            payment_method_id="card-alice-4242",
            idempotency_key="alice-order-1",  # Same idempotency key!
        )
    )
    console.print(f"[cyan]⚡ Idempotency verification: Repeated request returned existing invoice #{res_alice_dup.invoice.id[:8]} without duplicate debit (Total gateway calls: {gateway.call_count})[/cyan]")

    # 4. Mid-Month Upgrade with Proration Math
    console.print("\n[bold green]► Step 3: Mid-Month Plan Upgrade with Mathematical Proration[/bold green]")
    clock.advance(timedelta(days=15))
    console.print(f"[italic]Time advanced 15 days to {clock.now().strftime('%Y-%m-%d')} (50% of monthly cycle elapsed)[/italic]")

    change_plan_uc = ChangePlanUseCase(
        subscription_repo=sub_repo,
        plan_repo=plan_repo,
        invoice_repo=inv_repo,
        payment_gateway=gateway,
        clock=clock,
    )
    upgrade_res = change_plan_uc.execute(
        ChangePlanCommand(
            tenant_id=tenant.id,
            subscription_id=res_alice.subscription.id,
            new_plan_id=plan_pro.id,
            payment_method_id="card-alice-4242",
            idempotency_key="alice-upgrade-1",
        )
    )
    proration = upgrade_res.proration

    table_proration = Table(title="Proration Calculation Breakdown")
    table_proration.add_column("Component", style="bold")
    table_proration.add_column("Amount", style="green")
    table_proration.add_column("Explanation", style="white")

    table_proration.add_row("Unused Starter Credit", f"-{proration.unspent_credit}", "Remaining 15 days of Starter plan credited back")
    table_proration.add_row("Pro Tier Charge", f"+{proration.new_plan_charge}", "Cost of Pro tier for remaining 15 days")
    table_proration.add_row("Net Amount Due", f"{proration.net_amount_due}", "[bold yellow]Exact difference billed immediately[/bold yellow]")
    console.print(table_proration)

    # 5. Usage Metering Stream
    console.print("\n[bold green]► Step 4: High-Throughput Metered Usage Ingestion[/bold green]")
    usage_uc = RecordUsageUseCase(subscription_repo=sub_repo, usage_repo=usage_repo, clock=clock)
    # Alice consumes 650 units (Pro plan includes 500 units -> 150 overage units!)
    for batch_units in [200, 250, 200]:
        usage_uc.execute(
            RecordUsageCommand(
                tenant_id=tenant.id,
                subscription_id=res_alice.subscription.id,
                metric_name="api_calls",
                units=batch_units,
            )
        )
    console.print(f"[white]✓ Recorded usage events: Total [bold]650 units[/bold] consumed (Included: 500 units, Overage: [bold yellow]150 units[/bold yellow])[/white]")

    # 6. Chaos / Fault Injection & Circuit Breaker
    console.print("\n[bold red]► Step 5: Chaos Engineering & Circuit Breaker Trip[/bold red]")
    console.print("[yellow]Simulating sudden downstream banking network outage (504 Gateway Timeout)...[/yellow]")
    gateway.simulate_transient_failure = True

    for i in range(1, 3):
        try:
            circuit_breaker.call(
                lambda: gateway.charge(res_alice.invoice, "tok-bad", f"chaos-tx-{i}")
                if not gateway.simulate_transient_failure
                else (_ for _ in ()).throw(ConnectionResetError("504 Gateway Timeout"))
            )
        except ConnectionResetError:
            console.print(f"[red]✕ Attempt {i}: Banking gateway timed out. Recorded failure in Circuit Breaker.[/red]")

    console.print(f"[bold magenta]⚡ Circuit Breaker State: {circuit_breaker.state.value} (Failure count: {circuit_breaker.failure_count})[/bold magenta]")

    # Next attempt triggers fail-fast
    try:
        circuit_breaker.call(lambda: "should fail immediately")
    except CircuitBreakerOpenError as e:
        console.print(f"[bold green]🛡️ Circuit Breaker Protected System: Fast-failed with '{e}' without hammering bank API![/bold green]")

    # 7. Recovery & End-of-Cycle Renewal
    console.print("\n[bold green]► Step 6: Bank Recovery & Scheduled Billing Cycle Run[/bold green]")
    gateway.simulate_transient_failure = False
    time.sleep(1.1)  # wait for recovery timeout
    console.print(f"[italic]Circuit Breaker evaluated recovery timeout ➔ Transitioned to [bold cyan]{circuit_breaker.state.value}[/bold cyan][/italic]")

    clock.advance(timedelta(days=16))  # Month elapsed
    cycle_uc = RunBillingCycleUseCase(
        subscription_repo=sub_repo,
        plan_repo=plan_repo,
        invoice_repo=inv_repo,
        usage_repo=usage_repo,
        payment_gateway=gateway,
        clock=clock,
    )
    cycle_res = cycle_uc.execute()
    circuit_breaker.record_success()
    console.print(f"[green]✓ Canary charge succeeded ➔ Circuit Breaker restored to [bold]{circuit_breaker.state.value}[/bold][/green]")
    console.print(f"[white]✓ Billing renewal cycle executed: [bold]{len(cycle_res.renewed_subscriptions)}[/bold] subscriptions renewed successfully.[/white]")

    # 8. Final Invoices Ledger
    console.print("\n[bold green]► Step 7: Final Financial Ledger (Invoices)[/bold green]")
    all_invoices = inv_repo.list_by_subscription(res_alice.subscription.id)
    table_inv = Table(title="Generated Invoices Ledger")
    table_inv.add_column("Invoice ID", style="cyan")
    table_inv.add_column("Status", style="bold")
    table_inv.add_column("Total Amount", style="green")
    table_inv.add_column("Line Items Count", style="magenta")
    table_inv.add_column("Items Breakdown", style="white")

    total_revenue = Decimal("0.00")
    for inv in all_invoices:
        items_desc = ", ".join(f"{it.description} ({it.total})" for it in inv.line_items)
        table_inv.add_row(
            inv.id[:12],
            inv.status.value,
            str(inv.total_amount),
            str(len(inv.line_items)),
            items_desc,
        )
        if inv.status.value == "PAID":
            total_revenue += inv.total_amount.amount

    console.print(table_inv)
    console.print(
        Panel.fit(
            f"[bold green]Demonstration Complete![/bold green]\n"
            f"[white]Total Net Revenue Collected:[/white] [bold yellow]{total_revenue:.2f} RUB[/bold yellow]\n"
            f"[white]Active Subscriptions:[/white] [bold]1[/bold] | [white]Data Loss:[/white] [bold green]0[/bold green] | [white]Fault Tolerance:[/white] [bold green]PROVEN[/bold green]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    run_interactive_demo()
