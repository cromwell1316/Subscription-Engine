from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Visual Dashboard"])

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Панель управления биллингом | Subscription Engine</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
    .badge-closed { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .badge-open { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .badge-half { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .pulse-dot { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .4; } }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">

  <!-- Header -->
  <header class="border-b border-slate-800 bg-slate-900/70 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
          SE
        </div>
        <div>
          <h1 class="text-base font-semibold leading-none">Subscription Engine</h1>
          <p class="text-xs text-slate-400 mt-1">Мультитенантная платформа тарификации (Clean Architecture)</p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <a href="/docs" target="_blank" class="text-xs font-medium px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center gap-1.5">
          <span>Swagger API</span>
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
        </a>
        <button onclick="refreshData()" class="text-xs font-medium px-3 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1.5 shadow">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          <span>Обновить</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

    <!-- Top KPI Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Выручка (Собрано)</p>
        <p class="text-2xl font-bold text-emerald-400 mt-2" id="kpi-revenue">0.00 ₽</p>
        <p class="text-xs text-slate-500 mt-1">Оплаченные счета</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Активные подписки</p>
        <p class="text-2xl font-bold text-indigo-400 mt-2" id="kpi-subscriptions">0</p>
        <p class="text-xs text-slate-500 mt-1">Действующие договоры</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Выставленные счета</p>
        <p class="text-2xl font-bold text-amber-400 mt-2" id="kpi-invoices">0</p>
        <p class="text-xs text-slate-500 mt-1">За все периоды</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-sm">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Организации (Арендаторы)</p>
        <p class="text-2xl font-bold text-slate-200 mt-2" id="kpi-tenants">0</p>
        <p class="text-xs text-slate-500 mt-1">Изолированные контуры</p>
      </div>
    </div>

    <!-- Resilience & Circuit Breaker Interactive Widget -->
    <div class="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-850 border border-slate-800 p-6 rounded-xl shadow-md">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-3">
            <h2 class="text-lg font-semibold text-white">Отказоустойчивость: Предохранитель (Circuit Breaker)</h2>
            <span id="cb-badge" class="px-2.5 py-0.5 rounded-full text-xs font-semibold badge-closed flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 pulse-dot"></span>
              <span id="cb-status-text">CLOSED</span>
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-1.5 max-w-2xl leading-relaxed">
            Автомат защиты внешнего шлюза: при обнаружении серии сбоев банка цепь размыкается (<code class="text-rose-400">OPEN</code>), мгновенно прерывая повторные вызовы без зависания очередей.
          </p>
          <div class="flex items-center gap-6 mt-3 text-xs text-slate-400">
            <span>Счетчик ошибок: <strong id="cb-failures" class="text-slate-200">0 / 3</strong></span>
            <span>Таймаут восстановления: <strong class="text-slate-200">15.0 с</strong></span>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <button onclick="tripCircuitBreaker()" class="text-xs font-medium px-4 py-2.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 transition flex items-center gap-2">
            <span>⚡ Сбой банка (504 Timeout)</span>
          </button>
          <button onclick="resetCircuitBreaker()" class="text-xs font-medium px-4 py-2.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 transition flex items-center gap-2">
            <span>🔄 Восстановить (CLOSED)</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Action Bar -->
    <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
      <div class="text-xs font-medium text-slate-300">Быстрые сценарии для демонстрации:</div>
      <div class="flex flex-wrap items-center gap-2">
        <button onclick="quickSubscribe()" class="text-xs font-medium px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1.5 shadow">
          <span>➕ Оформить подписку</span>
        </button>
        <button onclick="quickRecordUsage()" class="text-xs font-medium px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-1.5">
          <span>📊 +150 единиц API квоты</span>
        </button>
        <button onclick="triggerBillingCycle()" class="text-xs font-medium px-3.5 py-2 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 transition flex items-center gap-1.5">
          <span>🌙 Запустить регулярный биллинг</span>
        </button>
      </div>
    </div>

    <!-- Tables Layout: Subscriptions & Invoices -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- Subscriptions Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col">
        <div class="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-white">Активные договоры подписок</h3>
          <span class="text-xs text-slate-400" id="sub-count-badge">0 записей</span>
        </div>
        <div class="overflow-x-auto flex-1">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th class="px-4 py-3 font-semibold">Клиент</th>
                <th class="px-4 py-3 font-semibold">Тариф</th>
                <th class="px-4 py-3 font-semibold">Окончание периода</th>
                <th class="px-4 py-3 font-semibold">Статус</th>
                <th class="px-4 py-3 font-semibold text-right">Действие</th>
              </tr>
            </thead>
            <tbody id="subscriptions-table-body" class="divide-y divide-slate-800/60">
              <tr><td colspan="5" class="px-4 py-6 text-center text-slate-500">Загрузка данных...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Invoices Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col">
        <div class="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-white">Реестр выставленных счетов</h3>
          <span class="text-xs text-slate-400" id="inv-count-badge">0 записей</span>
        </div>
        <div class="overflow-x-auto flex-1">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th class="px-4 py-3 font-semibold">Счет №</th>
                <th class="px-4 py-3 font-semibold">Сумма</th>
                <th class="px-4 py-3 font-semibold">Назначение</th>
                <th class="px-4 py-3 font-semibold">Статус</th>
              </tr>
            </thead>
            <tbody id="invoices-table-body" class="divide-y divide-slate-800/60">
              <tr><td colspan="4" class="px-4 py-6 text-center text-slate-500">Загрузка данных...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Pricing Plans Catalog Card -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
      <div class="px-5 py-4 border-b border-slate-800">
        <h3 class="text-sm font-semibold text-white">Каталог тарифных планов (Арендатор: Acme Cloud)</h3>
      </div>
      <div class="p-5 grid grid-cols-1 md:grid-cols-3 gap-4" id="plans-grid">
        <!-- Rendered by JS -->
      </div>
    </div>

  </main>

  <!-- Notification Toast -->
  <div id="toast" class="fixed bottom-5 right-5 max-w-sm bg-slate-800 border border-slate-700 text-slate-100 px-4 py-3 rounded-lg shadow-xl text-xs transition-opacity duration-300 opacity-0 pointer-events-none flex items-center space-x-2 z-50">
    <span id="toast-message">Сообщение</span>
  </div>

  <script>
    function showToast(msg, isError = false) {
      const toast = document.getElementById('toast');
      const text = document.getElementById('toast-message');
      text.innerText = msg;
      toast.className = `fixed bottom-5 right-5 max-w-sm border px-4 py-3 rounded-lg shadow-xl text-xs transition-opacity duration-300 opacity-100 flex items-center space-x-2 z-50 ${isError ? 'bg-rose-950/90 border-rose-800 text-rose-200' : 'bg-slate-850/90 border-slate-700 text-slate-100'}`;
      setTimeout(() => { toast.classList.replace('opacity-100', 'opacity-0'); }, 3000);
    }

    async function refreshData() {
      try {
        // Fetch stats
        const statsRes = await fetch('/api/v1/system/stats');
        const stats = await statsRes.json();
        
        document.getElementById('kpi-revenue').innerText = parseFloat(stats.total_revenue).toLocaleString('ru-RU', { minimumFractionDigits: 2 }) + ' ₽';
        document.getElementById('kpi-subscriptions').innerText = stats.subscriptions_count;
        document.getElementById('kpi-invoices').innerText = stats.invoices_count;
        document.getElementById('kpi-tenants').innerText = stats.tenants_count;

        // Circuit breaker badge
        const cb = stats.circuit_breaker;
        const cbBadge = document.getElementById('cb-badge');
        const cbText = document.getElementById('cb-status-text');
        const cbFailures = document.getElementById('cb-failures');
        cbFailures.innerText = `${cb.failure_count} / ${cb.threshold}`;

        if (cb.state === 'CLOSED') {
          cbBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold badge-closed flex items-center gap-1.5';
          cbText.innerText = 'CLOSED (ШТАТНЫЙ РЕЖИМ)';
        } else if (cb.state === 'OPEN') {
          cbBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold badge-open flex items-center gap-1.5';
          cbText.innerText = 'OPEN (РАЗОМКНУТ / FAIL-FAST)';
        } else {
          cbBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold badge-half flex items-center gap-1.5';
          cbText.innerText = 'HALF_OPEN (ПРОВЕРКА)';
        }

        // Subscriptions
        const subsRes = await fetch('/api/v1/system/subscriptions');
        const subs = await subsRes.json();
        document.getElementById('sub-count-badge').innerText = `${subs.length} записей`;
        const subTbody = document.getElementById('subscriptions-table-body');
        if (subs.length === 0) {
          subTbody.innerHTML = '<tr><td colspan="5" class="px-4 py-6 text-center text-slate-500">Нет активных подписок</td></tr>';
        } else {
          subTbody.innerHTML = subs.map(s => `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="px-4 py-3 font-medium text-slate-200">${s.customer_id}</td>
              <td class="px-4 py-3 text-indigo-400 font-medium">${s.plan_name}</td>
              <td class="px-4 py-3 text-slate-400">${new Date(s.current_period_end).toLocaleDateString('ru-RU')}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${s.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}">
                  ${s.status}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button onclick="upgradePlan('${s.id}')" class="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium hover:underline">Сменить тариф</button>
              </td>
            </tr>
          `).join('');
        }

        // Invoices
        const invsRes = await fetch('/api/v1/system/invoices');
        const invs = await invsRes.json();
        document.getElementById('inv-count-badge').innerText = `${invs.length} записей`;
        const invTbody = document.getElementById('invoices-table-body');
        if (invs.length === 0) {
          invTbody.innerHTML = '<tr><td colspan="4" class="px-4 py-6 text-center text-slate-500">Нет счетов</td></tr>';
        } else {
          invTbody.innerHTML = invs.slice(0, 8).map(inv => `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="px-4 py-3 font-mono text-[11px] text-slate-300">#${inv.id.substring(0, 8)}</td>
              <td class="px-4 py-3 font-bold text-slate-100">${parseFloat(inv.total_amount).toLocaleString('ru-RU', { minimumFractionDigits: 2 })} ₽</td>
              <td class="px-4 py-3 text-slate-400 truncate max-w-xs" title="${inv.items_summary}">${inv.items_summary}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${inv.status === 'PAID' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : inv.status === 'FAILED' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">
                  ${inv.status}
                </span>
              </td>
            </tr>
          `).join('');
        }

        // Plans
        const plansRes = await fetch('/api/v1/plans?tenant_id=tenant-demo');
        const plans = await plansRes.json();
        const plansGrid = document.getElementById('plans-grid');
        plansGrid.innerHTML = plans.map(p => `
          <div class="border border-slate-800 bg-slate-950/40 p-4 rounded-xl flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-slate-300">${p.name}</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">${p.period}</span>
              </div>
              <p class="text-xl font-bold text-white mt-2">${parseFloat(p.price).toLocaleString('ru-RU')} ₽ <span class="text-xs font-normal text-slate-400">/ мес</span></p>
              <p class="text-xs text-slate-400 mt-2">Квота: <strong class="text-slate-200">${p.included_units} ед.</strong> (Перерасход: ${p.overage_unit_price} ₽/ед)</p>
            </div>
            ${p.trial_days > 0 ? `<p class="text-[11px] text-indigo-400 mt-3">🎁 Включен триал: ${p.trial_days} дней</p>` : ''}
          </div>
        `).join('');

      } catch (err) {
        console.error("Dashboard refresh error:", err);
      }
    }

    async function tripCircuitBreaker() {
      const res = await fetch('/api/v1/system/circuit-breaker/trip', { method: 'POST' });
      const data = await res.json();
      showToast(data.message);
      refreshData();
    }

    async function resetCircuitBreaker() {
      const res = await fetch('/api/v1/system/circuit-breaker/reset', { method: 'POST' });
      const data = await res.json();
      showToast(data.message);
      refreshData();
    }

    async function quickSubscribe() {
      const randId = 'cust-' + Math.floor(Math.random() * 900 + 100);
      const res = await fetch('/api/v1/subscriptions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: 'tenant-demo',
          customer_id: randId,
          plan_id: 'plan-basic',
          payment_method_id: 'card-4242',
          idempotency_key: 'quick-sub-' + Date.now()
        })
      });
      if (res.ok) {
        showToast(`Клиент ${randId} успешно оформлен!`);
      } else {
        showToast('Ошибка оформления подписки (возможно, шлюз разомкнут)', true);
      }
      refreshData();
    }

    async function quickRecordUsage() {
      const subsRes = await fetch('/api/v1/system/subscriptions');
      const subs = await subsRes.json();
      if (subs.length === 0) {
        showToast('Сначала создайте хотя бы одну подписку', true);
        return;
      }
      const targetSub = subs[0];
      const res = await fetch('/api/v1/usage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: targetSub.tenant_id,
          subscription_id: targetSub.id,
          metric_name: 'api_calls',
          units: 150
        })
      });
      if (res.ok) {
        showToast(`Зафиксировано 150 ед. потребления для ${targetSub.customer_id}!`);
      }
      refreshData();
    }

    async function triggerBillingCycle() {
      const res = await fetch('/api/v1/billing-cycle/run', { method: 'POST' });
      const data = await res.json();
      showToast(`Цикл биллинга завершен: ${data.renewed_count} продлено, ${data.failed_count} сбоев.`);
      refreshData();
    }

    async function upgradePlan(subId) {
      const res = await fetch(`/api/v1/subscriptions/${subId}/change-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: 'tenant-demo',
          new_plan_id: 'plan-pro',
          payment_method_id: 'card-4242',
          idempotency_key: 'upgrade-' + Date.now()
        })
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`Тариф обновлен на Pro! Доплата: ${data.proration.net_amount_due} ₽ (зачтено ${data.proration.unspent_credit} ₽)`);
      } else {
        showToast('Ошибка при апгрейде тарифа', true);
      }
      refreshData();
    }

    // Auto-refresh on mount and interval
    refreshData();
    setInterval(refreshData, 5000);
  </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard() -> HTMLResponse:
    """Renders visual administrative dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)
