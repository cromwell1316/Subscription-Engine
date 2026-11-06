from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Visual Dashboard"])


def build_dashboard_html(initial_window: str = "overview") -> str:
    return f"""<!DOCTYPE html>
<html lang="ru" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Subscription Engine — Enterprise Billing & Resilience Console</title>
  
  <!-- Modern UI Stack: Tailwind CSS (Shadcn Zinc Palette), Inter & JetBrains Mono, Lucide Icons, Chart.js -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }},
          colors: {{
            zinc: {{
              850: '#141417',
              900: '#111114',
              925: '#0c0c0e',
              950: '#08080a',
            }},
            brand: {{
              50: '#eef2ff',
              100: '#e0e7ff',
              400: '#818cf8',
              500: '#6366f1',
              600: '#4f46e5',
            }},
            cyber: {{
              cyan: '#06b6d4',
              emerald: '#10b981',
              amber: '#f59e0b',
              rose: '#f43f5e',
            }}
          }}
        }}
      }}
    }}
  </script>

  <style>
    body {{ font-family: 'Inter', sans-serif; }}
    .mono-num {{ font-family: 'JetBrains Mono', monospace; font-feature-settings: "tnum"; }}
    .custom-scrollbar::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    .custom-scrollbar::-webkit-scrollbar-track {{ background: #08080a; }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #27272a; border-radius: 4px; }}
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {{ background: #3f3f46; }}
    
    /* Glow Animations for Circuit Breaker */
    .glow-closed {{ box-shadow: 0 0 16px rgba(16, 185, 129, 0.25); }}
    .glow-open {{ box-shadow: 0 0 20px rgba(244, 63, 94, 0.35); }}
    .glow-half {{ box-shadow: 0 0 16px rgba(245, 158, 11, 0.25); }}

    /* Slide-over Drawer animation */
    .drawer-transition {{ transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1); }}
  </style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-screen flex antialiased selection:bg-brand-500 selection:text-white">

  <!-- ================= LEFT ENTERPRISE SIDEBAR (SHADCN STYLE) ================= -->
  <aside class="w-64 border-r border-zinc-800/80 bg-zinc-925 flex flex-col justify-between hidden md:flex shrink-0 z-30">
    <div>
      <!-- Brand & Workspace Selector -->
      <div class="h-16 px-5 flex items-center justify-between border-b border-zinc-800/80">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 via-indigo-600 to-cyber-cyan flex items-center justify-center font-bold text-white shadow-md shadow-brand-500/20">
            <i data-lucide="shield-check" class="w-4 h-4"></i>
          </div>
          <div>
            <span class="text-xs font-bold tracking-tight text-white block">Subscription Engine</span>
            <span class="text-[10px] text-zinc-400 font-mono tracking-wider uppercase block">Clean Architecture</span>
          </div>
        </div>
      </div>

      <!-- Tenant Switcher Dropdown (Tremor style) -->
      <div class="p-3">
        <div class="px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-xs flex items-center justify-between cursor-pointer hover:border-zinc-700 transition">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-emerald-400"></div>
            <span class="font-medium text-zinc-200">Acme Cloud Platform</span>
          </div>
          <span class="text-[10px] font-mono text-zinc-400 uppercase">RUB</span>
        </div>
      </div>

      <!-- Navigation Tabs / Windows -->
      <nav class="px-3 py-2 space-y-1 text-xs font-medium">
        <a href="/dashboard" onclick="navigateTo(event, 'overview')" id="nav-overview" class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-white bg-zinc-800/90 transition">
          <div class="flex items-center gap-2.5">
            <i data-lucide="layout-dashboard" class="w-4 h-4 text-brand-400"></i>
            <span>Обзор (Overview)</span>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">KPI</span>
        </a>
        <a href="/dashboard/subscriptions" onclick="navigateTo(event, 'subscriptions')" id="nav-subscriptions" class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-850 transition">
          <div class="flex items-center gap-2.5">
            <i data-lucide="credit-card" class="w-4 h-4"></i>
            <span>Договоры подписок</span>
          </div>
          <span id="nav-badge-subs" class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">0</span>
        </a>
        <a href="/dashboard/invoices" onclick="navigateTo(event, 'invoices')" id="nav-invoices" class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-850 transition">
          <div class="flex items-center gap-2.5">
            <i data-lucide="receipt" class="w-4 h-4"></i>
            <span>Счета и проводки</span>
          </div>
          <span id="nav-badge-invs" class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">0</span>
        </a>
        <a href="/dashboard/plans" onclick="navigateTo(event, 'plans')" id="nav-plans" class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-850 transition">
          <div class="flex items-center gap-2.5">
            <i data-lucide="layers" class="w-4 h-4"></i>
            <span>Конструктор тарифов</span>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">Plans</span>
        </a>
        <a href="/dashboard/resilience" onclick="navigateTo(event, 'resilience')" id="nav-resilience" class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-850 transition">
          <div class="flex items-center gap-2.5">
            <i data-lucide="activity" class="w-4 h-4 text-cyber-emerald"></i>
            <span>Отказоустойчивость & CB</span>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">SLA</span>
        </a>
        <a href="/dashboard/outbox" onclick="navigateTo(event, 'outbox')" id="nav-outbox" class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-850 transition">
          <div class="flex items-center gap-2.5">
            <i data-lucide="send" class="w-4 h-4 text-cyber-amber"></i>
            <span>Transactional Outbox</span>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-amber-950 text-amber-400 border border-amber-800">RPO=0</span>
        </a>
      </nav>
    </div>

    <!-- Bottom System Health Block -->
    <div class="p-3 border-t border-zinc-800/80 bg-zinc-950/60 space-y-2">
      <div class="bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-[11px] space-y-1">
        <div class="flex items-center justify-between text-zinc-400">
          <span>Среда:</span>
          <span class="font-mono text-emerald-400 font-semibold">Production</span>
        </div>
        <div class="flex items-center justify-between text-zinc-400">
          <span>RPO Целостность:</span>
          <span class="font-mono text-zinc-200">0 (Zero Data Loss)</span>
        </div>
        <div class="flex items-center justify-between text-zinc-400">
          <span>Идемпотентность:</span>
          <span class="font-mono text-brand-400">Strict Key</span>
        </div>
      </div>
      <a href="/docs" target="_blank" class="w-full flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-855 hover:bg-zinc-800 text-xs font-medium text-zinc-300 transition border border-zinc-800">
        <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
        <span>API Документация</span>
      </a>
    </div>
  </aside>

  <!-- ================= MAIN WORKSPACE AREA ================= -->
  <div class="flex-1 flex flex-col min-w-0 overflow-y-auto custom-scrollbar">

    <!-- Top Universal Header -->
    <header class="h-16 px-6 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-20 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-xs px-2 py-0.5 rounded-md bg-zinc-850 text-zinc-300 border border-zinc-800 font-mono">v1.0.0</span>
        <h2 id="window-title" class="text-sm font-semibold text-white">Сводный обзор системы</h2>
      </div>

      <div class="flex items-center gap-3">
        <!-- Live Circuit Breaker Status Indicator -->
        <div id="header-cb-card" class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 text-xs">
          <span id="header-cb-dot" class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span class="text-zinc-400 font-mono">Circuit Breaker:</span>
          <span id="header-cb-state" class="font-bold font-mono text-emerald-400">CLOSED</span>
        </div>

        <!-- Global Action Shortcut -->
        <button onclick="refreshData()" class="p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-300 transition border border-zinc-800" title="Обновить состояние">
          <i data-lucide="refresh-cw" class="w-4 h-4"></i>
        </button>
      </div>
    </header>

    <!-- Main Dynamic Content Workspace -->
    <main class="p-6 md:p-8 space-y-6 max-w-7xl w-full mx-auto">

      <!-- ================= WINDOW 1: OVERVIEW & COMMAND CENTER ================= -->
      <section id="window-overview" class="space-y-6">

        <!-- Tremor-Style KPI Cards Grid with Delta Badges -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <!-- Revenue Card -->
          <div class="bg-zinc-900 border border-zinc-800/80 p-5 rounded-2xl relative overflow-hidden shadow-sm">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Фактическая выручка</span>
              <div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                <i data-lucide="wallet" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-extrabold text-white mt-3 mono-num" id="kpi-revenue">0.00 ₽</p>
            <div class="flex items-center gap-2 mt-2.5">
              <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <i data-lucide="arrow-up-right" class="w-3 h-3"></i>
                <span>+100% факт</span>
              </span>
              <span class="text-xs text-zinc-500">Подтверждено банком</span>
            </div>
          </div>

          <!-- Subscriptions Card -->
          <div class="bg-zinc-900 border border-zinc-800/80 p-5 rounded-2xl relative overflow-hidden shadow-sm">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Активные договоры</span>
              <div class="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 flex items-center justify-center">
                <i data-lucide="users" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-extrabold text-white mt-3 mono-num" id="kpi-subscriptions">0</p>
            <div class="flex items-center gap-2 mt-2.5">
              <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1">
                <span>0.0% отток</span>
              </span>
              <span class="text-xs text-zinc-500">Действующие подписки</span>
            </div>
          </div>

          <!-- Invoices Card -->
          <div class="bg-zinc-900 border border-zinc-800/80 p-5 rounded-2xl relative overflow-hidden shadow-sm">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Сформировано счетов</span>
              <div class="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
                <i data-lucide="receipt" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-extrabold text-white mt-3 mono-num" id="kpi-invoices">0</p>
            <div class="flex items-center gap-2 mt-2.5">
              <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Идемпотентно
              </span>
              <span class="text-xs text-zinc-500">За все расчетные циклы</span>
            </div>
          </div>

          <!-- Tenants Card -->
          <div class="bg-zinc-900 border border-zinc-800/80 p-5 rounded-2xl relative overflow-hidden shadow-sm">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Тенанты (Контуры)</span>
              <div class="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                <i data-lucide="database" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-extrabold text-white mt-3 mono-num" id="kpi-tenants">0</p>
            <div class="flex items-center gap-2 mt-2.5">
              <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Изоляция
              </span>
              <span class="text-xs text-zinc-500">Мультитенантность</span>
            </div>
          </div>

        </div>

        <!-- Tremor-Style Interactive Charts Area -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Main Revenue Trend Curve (2 cols) -->
          <div class="lg:col-span-2 bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xs font-bold uppercase tracking-wider text-zinc-300">Динамика собранной выручки</h3>
                <p class="text-xs text-zinc-500 mt-0.5">Включая базовые ставки и автоматический расчет овердрафта квот</p>
              </div>
              <span class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">RUB Currency</span>
            </div>
            <div class="h-64">
              <canvas id="overviewRevenueChart"></canvas>
            </div>
          </div>

          <!-- Subscription Tier Breakdown (1 col Donut Chart) -->
          <div class="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl flex flex-col justify-between">
            <div>
              <h3 class="text-xs font-bold uppercase tracking-wider text-zinc-300">Распределение по тарифам</h3>
              <p class="text-xs text-zinc-500 mt-0.5">Сегментация клиентской базы арендатора</p>
              <div class="h-44 mt-4 flex items-center justify-center">
                <canvas id="tierDonutChart"></canvas>
              </div>
            </div>
            <div class="space-y-1.5 pt-4 border-t border-zinc-800 text-xs">
              <div class="flex justify-between items-center text-zinc-400">
                <span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>Стартовый тариф</span>
                <span class="font-mono text-white">60%</span>
              </div>
              <div class="flex justify-between items-center text-zinc-400">
                <span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>Профессиональный</span>
                <span class="font-mono text-white">40%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Interactive Launchpad -->
        <div class="bg-gradient-to-r from-zinc-900 via-zinc-900 to-indigo-950/30 border border-zinc-800 p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i data-lucide="sparkles" class="w-4 h-4 text-brand-400"></i>
              <span>Быстрые действия оператора</span>
            </h3>
            <p class="text-xs text-zinc-400 mt-1 max-w-xl">
              Запустите финансовые сценарии платформы в один клик: выпуск нового договора с гарантией идемпотентности, начисление потребления или ночной цикл продления.
            </p>
          </div>
          <div class="flex flex-wrap items-center gap-2.5">
            <button onclick="openModal('modal-subscribe')" class="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition flex items-center gap-2 shadow-sm">
              <i data-lucide="user-plus" class="w-3.5 h-3.5"></i>
              <span>Оформить клиента</span>
            </button>
            <button onclick="quickRecordUsage()" class="px-4 py-2 rounded-xl bg-zinc-850 hover:bg-zinc-800 text-zinc-200 border border-zinc-700 text-xs font-medium transition flex items-center gap-2">
              <i data-lucide="activity" class="w-3.5 h-3.5 text-cyan-400"></i>
              <span>+150 единиц API квоты</span>
            </button>
            <button onclick="triggerBillingCycle()" class="px-4 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-semibold transition flex items-center gap-2">
              <i data-lucide="moon" class="w-3.5 h-3.5"></i>
              <span>Запустить биллинг-цикл</span>
            </button>
          </div>
        </div>

      </section>

      <!-- ================= WINDOW 2: SUBSCRIPTIONS WORKSPACE ================= -->
      <section id="window-subscriptions" class="hidden space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900 p-5 rounded-2xl border border-zinc-800">
          <div>
            <h3 class="text-base font-bold text-white">Реестр договоров подписок</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Контроль жизненного цикла, проверка квот и управление сменой тарифных планов</p>
          </div>
          <div class="flex items-center gap-3">
            <button onclick="openModal('modal-subscribe')" class="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition flex items-center gap-2 shadow-sm">
              <i data-lucide="plus" class="w-4 h-4"></i>
              <span>Новый договор</span>
            </button>
          </div>
        </div>

        <!-- Subscriptions Table Card (Shadcn Data Table) -->
        <div class="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-zinc-300">
              <thead class="bg-zinc-950 text-zinc-400 uppercase text-[10px] tracking-wider border-b border-zinc-800 font-mono">
                <tr>
                  <th class="px-5 py-3.5">Идентификатор клиента</th>
                  <th class="px-5 py-3.5">Текущий тарифный план</th>
                  <th class="px-5 py-3.5">Окончание расчетного периода</th>
                  <th class="px-5 py-3.5">Статус подписки</th>
                  <th class="px-5 py-3.5 text-right">Действие</th>
                </tr>
              </thead>
              <tbody id="subscriptions-table-body" class="divide-y divide-zinc-800/70 font-medium">
                <tr><td colspan="5" class="px-5 py-8 text-center text-zinc-500 font-sans">Загрузка данных...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================= WINDOW 3: INVOICES & LEDGER WORKSPACE ================= -->
      <section id="window-invoices" class="hidden space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900 p-5 rounded-2xl border border-zinc-800">
          <div>
            <h3 class="text-base font-bold text-white">Финансовый реестр требований (Invoices Ledger)</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Неизменяемая книга проводок с полной детализацией начислений</p>
          </div>
          <span class="text-xs font-mono px-3 py-1 rounded-lg bg-zinc-800 text-zinc-300 border border-zinc-700" id="invoices-count-badge">0 записей</span>
        </div>

        <div class="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-zinc-300">
              <thead class="bg-zinc-950 text-zinc-400 uppercase text-[10px] tracking-wider border-b border-zinc-800 font-mono">
                <tr>
                  <th class="px-5 py-3.5">Номер счета</th>
                  <th class="px-5 py-3.5">Сумма к оплате</th>
                  <th class="px-5 py-3.5">Назначение платежа</th>
                  <th class="px-5 py-3.5">Дата начисления</th>
                  <th class="px-5 py-3.5">Статус</th>
                  <th class="px-5 py-3.5 text-right">Квитанция</th>
                </tr>
              </thead>
              <tbody id="invoices-table-body" class="divide-y divide-zinc-800/70">
                <tr><td colspan="6" class="px-5 py-8 text-center text-zinc-500 font-sans">Загрузка счетов...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================= WINDOW 4: PLAN DESIGNER WORKSPACE ================= -->
      <section id="window-plans" class="hidden space-y-6">
        <div class="flex items-center justify-between bg-zinc-900 p-5 rounded-2xl border border-zinc-800">
          <div>
            <h3 class="text-base font-bold text-white">Конструктор тарифных планов</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Тарифная сетка с фиксированной стоимостью, квотами и стоимостью овердрафта</p>
          </div>
          <button onclick="openModal('modal-subscribe')" class="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition flex items-center gap-2 shadow-sm">
            <i data-lucide="plus-circle" class="w-4 h-4"></i>
            <span>Оформить договор</span>
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="plans-cards-grid">
          <!-- Populated by JS -->
        </div>
      </section>

      <!-- ================= WINDOW 5: RESILIENCE & CHAOS COCKPIT ================= -->
      <section id="window-resilience" class="hidden space-y-6">
        
        <!-- Circuit Breaker Main Deck -->
        <div class="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl shadow-sm">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-zinc-800">
            <div>
              <div class="flex items-center gap-3">
                <h3 class="text-lg font-bold text-white">Предохранитель платежного шлюза (Circuit Breaker)</h3>
                <span id="cb-cockpit-badge" class="px-3 py-1 rounded-full text-xs font-mono font-bold border flex items-center gap-2 glow-closed bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                  <span id="cb-cockpit-state">CLOSED</span>
                </span>
              </div>
              <p class="text-xs text-zinc-400 mt-2 max-w-2xl leading-relaxed">
                Защитный автомат предотвращает каскадные отказы инфраструктуры при недоступности внешних банковских API. При повторяющихся сбоях цепь переходит в состояние <span class="text-rose-400 font-mono font-bold">OPEN</span> и сразу возвращает ошибку без ожидания сетевых таймаутов.
              </p>
            </div>
            
            <div class="flex items-center gap-3">
              <button onclick="tripCircuitBreaker()" class="px-4 py-2.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-xs font-semibold transition flex items-center gap-2">
                <i data-lucide="zap-off" class="w-4 h-4 text-rose-400"></i>
                <span>Инъекция 504 Timeout</span>
              </button>
              <button onclick="resetCircuitBreaker()" class="px-4 py-2.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition flex items-center gap-2">
                <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>
                <span>Восстановить (CLOSED)</span>
              </button>
            </div>
          </div>

          <!-- Gauges Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6">
            <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
              <span class="text-xs text-zinc-400 uppercase tracking-wider block font-medium">Порог размыкания цепи</span>
              <span class="text-xl font-bold font-mono text-white mt-1 block">3 отказа подряд</span>
              <span class="text-[11px] text-zinc-500 mt-1 block">Лимит до перехода в OPEN</span>
            </div>
            <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
              <span class="text-xs text-zinc-400 uppercase tracking-wider block font-medium">Счетчик сбоев</span>
              <span id="cb-cockpit-failures" class="text-xl font-bold font-mono text-amber-400 mt-1 block">0 сбоев</span>
              <span class="text-[11px] text-zinc-500 mt-1 block">Сбрасывается при успешном платеже</span>
            </div>
            <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
              <span class="text-xs text-zinc-400 uppercase tracking-wider block font-medium">Таймаут зондирования</span>
              <span class="text-xl font-bold font-mono text-brand-400 mt-1 block">15.0 секунд</span>
              <span class="text-[11px] text-zinc-500 mt-1 block">Автоматический переход в HALF_OPEN</span>
            </div>
          </div>
        </div>

        <!-- Latency Chart in Resilience Window -->
        <div class="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
          <h3 class="text-xs font-bold uppercase tracking-wider text-zinc-300 mb-4">График отклика шлюза и изоляции сбоев</h3>
          <div class="h-60">
            <canvas id="resilienceLatencyChart"></canvas>
          </div>
        </div>

      </section>

      <!-- ================= WINDOW 6: TRANSACTIONAL OUTBOX STREAM ================= -->
      <section id="window-outbox" class="hidden space-y-5">
        <div class="flex items-center justify-between bg-zinc-900 p-5 rounded-2xl border border-zinc-800">
          <div>
            <h3 class="text-base font-bold text-white">Журнал Transactional Outbox</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Фиксация доменных событий в единой ACID-транзакции с финансовыми записями</p>
          </div>
          <span class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">Гарантия RPO = 0</span>
        </div>

        <div class="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-zinc-300">
              <thead class="bg-zinc-950 text-zinc-400 uppercase text-[10px] tracking-wider border-b border-zinc-800 font-mono">
                <tr>
                  <th class="px-5 py-3.5">ID События</th>
                  <th class="px-5 py-3.5">Тип события</th>
                  <th class="px-5 py-3.5">Арендатор</th>
                  <th class="px-5 py-3.5">Время фиксации</th>
                  <th class="px-5 py-3.5 text-right">Транзакционный статус</th>
                </tr>
              </thead>
              <tbody id="outbox-table-body" class="divide-y divide-zinc-800/70 font-mono">
                <tr><td colspan="5" class="px-5 py-8 text-center text-zinc-500 font-sans">Загрузка журнала событий...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

    </main>
  </div>

  <!-- ================= SLIDE-OVER DRAWER (INSPECTOR WINDOW) ================= -->
  <div id="inspector-drawer" class="fixed inset-y-0 right-0 w-full max-w-md bg-zinc-925 border-l border-zinc-800 shadow-2xl z-50 transform translate-x-full drawer-transition flex flex-col justify-between">
    <div>
      <!-- Drawer Header -->
      <div class="p-5 border-b border-zinc-800 flex items-center justify-between">
        <div>
          <h3 id="drawer-title" class="text-sm font-bold text-white">Детализация объекта</h3>
          <p id="drawer-subtitle" class="text-xs text-zinc-400 mt-0.5 font-mono">#ID</p>
        </div>
        <button onclick="closeDrawer()" class="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <!-- Drawer Body Content -->
      <div class="p-6 space-y-5 text-xs text-zinc-300 overflow-y-auto max-h-[calc(100vh-140px)] custom-scrollbar" id="drawer-content">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- Drawer Footer Actions -->
    <div class="p-4 border-t border-zinc-800 bg-zinc-950 flex justify-end gap-3" id="drawer-footer">
      <button onclick="closeDrawer()" class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition">Закрыть</button>
    </div>
  </div>

  <!-- Modal: Create Subscription -->
  <div id="modal-subscribe" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-zinc-900 border border-zinc-800 w-full max-w-md rounded-2xl p-6 shadow-2xl space-y-5">
      <div class="flex items-center justify-between border-b border-zinc-800 pb-4">
        <h3 class="text-base font-bold text-white">Оформление договора подписки</h3>
        <button onclick="closeModal('modal-subscribe')" class="text-zinc-400 hover:text-white">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>
      
      <div class="space-y-4 text-xs">
        <div>
          <label class="block text-zinc-300 font-medium mb-1">Идентификатор клиента (Customer ID)</label>
          <input type="text" id="sub-input-customer" value="cust-client-201" class="w-full px-3 py-2 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-100 font-mono focus:border-brand-500 focus:outline-none">
        </div>
        <div>
          <label class="block text-zinc-300 font-medium mb-1">Тарифный план</label>
          <select id="sub-input-plan" class="w-full px-3 py-2 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-100 focus:border-brand-500 focus:outline-none">
            <option value="plan-basic">Стартовый тариф (1500 ₽/мес, 100 ед. квоты)</option>
            <option value="plan-pro">Профессиональный (4500 ₽/мес, 500 ед. квоты)</option>
            <option value="plan-trial">Корпоративный Триал (14 дней бесплатно)</option>
          </select>
        </div>
        <div>
          <label class="block text-zinc-300 font-medium mb-1">Ключ идемпотентности (Idempotency Key)</label>
          <input type="text" id="sub-input-idemp" value="tx-order-001" class="w-full px-3 py-2 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-100 font-mono text-[11px] focus:border-brand-500 focus:outline-none">
          <p class="text-[10px] text-zinc-500 mt-1">Гарантирует защиту от повторного списания средств при сбоях сети.</p>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t border-zinc-800">
        <button onclick="closeModal('modal-subscribe')" class="px-4 py-2 rounded-xl text-zinc-400 hover:text-white text-xs font-medium">Отмена</button>
        <button onclick="submitSubscription()" class="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow">Оформить</button>
      </div>
    </div>
  </div>

  <!-- Modal: Plan Upgrade with Proration -->
  <div id="modal-proration" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-zinc-900 border border-zinc-800 w-full max-w-lg rounded-2xl p-6 shadow-2xl space-y-5">
      <div class="flex items-center justify-between border-b border-zinc-800 pb-4">
        <div>
          <h3 class="text-base font-bold text-white">Смена тарифного плана</h3>
          <p class="text-xs text-zinc-400">Пропорциональный перерасчет неизрасходованных дней (Proration)</p>
        </div>
        <button onclick="closeModal('modal-proration')" class="text-zinc-400 hover:text-white">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <input type="hidden" id="upgrade-sub-id" value="">

      <div class="space-y-4 text-xs">
        <div>
          <label class="block text-zinc-300 font-medium mb-1">Целевой тариф для апгрейда</label>
          <select id="upgrade-target-plan" class="w-full px-3 py-2 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-100 focus:border-brand-500 focus:outline-none">
            <option value="plan-pro">Профессиональный (4500.00 ₽ / мес)</option>
            <option value="plan-trial">Корпоративный (12000.00 ₽ / мес)</option>
          </select>
        </div>

        <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-2">
          <span class="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block">Математика взаимозачета:</span>
          <div class="flex justify-between text-zinc-300">
            <span>Зачет неиспользованных дней:</span>
            <span class="text-emerald-400 font-mono font-semibold" id="proration-credit">-750.00 ₽</span>
          </div>
          <div class="flex justify-between text-zinc-300">
            <span>Стоимость нового тарифа за остаток периода:</span>
            <span class="text-zinc-100 font-mono font-semibold" id="proration-new-cost">+2250.00 ₽</span>
          </div>
          <div class="border-t border-zinc-800 pt-2 flex justify-between text-sm font-bold text-white">
            <span>Итоговая доплата:</span>
            <span class="text-amber-400 font-mono" id="proration-net-due">1500.00 ₽</span>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t border-zinc-800">
        <button onclick="closeModal('modal-proration')" class="px-4 py-2 rounded-xl text-zinc-400 hover:text-white text-xs font-medium">Отмена</button>
        <button onclick="confirmPlanUpgrade()" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow">Подтвердить апгрейд</button>
      </div>
    </div>
  </div>

  <!-- Notification Toast Component -->
  <div id="toast" class="fixed bottom-5 right-5 max-w-sm bg-zinc-900 border border-zinc-700 text-zinc-100 px-4 py-3 rounded-xl shadow-2xl text-xs transition-all duration-300 opacity-0 pointer-events-none flex items-center space-x-3 z-50">
    <div id="toast-icon"></div>
    <span id="toast-message" class="leading-snug">Уведомление</span>
  </div>

  <!-- Core Script Logic -->
  <script>
    let currentWindow = "{initial_window}";
    let revenueChartInstance = null;
    let donutChartInstance = null;
    let latencyChartInstance = null;

    // Window Navigation with URL pushState
    function navigateTo(event, windowId) {{
      if (event) event.preventDefault();
      switchWindow(windowId);
      window.history.pushState({{}}, '', '/dashboard/' + (windowId === 'overview' ? '' : windowId));
    }}

    function switchWindow(windowId) {{
      const windows = ['overview', 'subscriptions', 'invoices', 'plans', 'resilience', 'outbox'];
      windows.forEach(w => {{
        document.getElementById(`window-${{w}}`).classList.add('hidden');
        const navEl = document.getElementById(`nav-${{w}}`);
        if (navEl) {{
          navEl.classList.remove('bg-zinc-800/90', 'text-white');
          navEl.classList.add('text-zinc-400');
        }}
      }});

      const activeSection = document.getElementById(`window-${{windowId}}`);
      if (activeSection) activeSection.classList.remove('hidden');
      
      const activeNav = document.getElementById(`nav-${{windowId}}`);
      if (activeNav) {{
        activeNav.classList.add('bg-zinc-800/90', 'text-white');
        activeNav.classList.remove('text-zinc-400');
      }}

      const titles = {{
        overview: 'Сводный обзор системы',
        subscriptions: 'Договоры подписок арендаторов',
        invoices: 'Финансовый реестр требований',
        plans: 'Конструктор тарифных планов',
        resilience: 'Отказоустойчивость & Circuit Breaker',
        outbox: 'Журнал Transactional Outbox',
      }};
      document.getElementById('window-title').innerText = titles[windowId] || 'Обзор';
      currentWindow = windowId;
      lucide.createIcons();
    }}

    // Toast notification
    function showToast(msg, isError = false) {{
      const toast = document.getElementById('toast');
      const text = document.getElementById('toast-message');
      const icon = document.getElementById('toast-icon');
      text.innerText = msg;
      icon.innerHTML = isError 
        ? '<i data-lucide="alert-triangle" class="w-4 h-4 text-rose-400"></i>'
        : '<i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>';
      toast.className = `fixed bottom-5 right-5 max-w-sm border px-4 py-3 rounded-xl shadow-2xl text-xs transition-all duration-300 opacity-100 flex items-center space-x-3 z-50 ${{isError ? 'bg-rose-950/90 border-rose-800 text-rose-200' : 'bg-zinc-900 border-zinc-700 text-zinc-100'}}`;
      lucide.createIcons();
      setTimeout(() => {{ toast.classList.replace('opacity-100', 'opacity-0'); }}, 3500);
    }}

    function openModal(id) {{
      document.getElementById(id).classList.remove('hidden');
      lucide.createIcons();
    }}

    function closeModal(id) {{
      document.getElementById(id).classList.add('hidden');
    }}

    // Slide-over Drawer Inspector
    function openDrawer(title, subtitle, htmlContent) {{
      document.getElementById('drawer-title').innerText = title;
      document.getElementById('drawer-subtitle').innerText = subtitle;
      document.getElementById('drawer-content').innerHTML = htmlContent;
      document.getElementById('inspector-drawer').classList.remove('translate-x-full');
      lucide.createIcons();
    }}

    function closeDrawer() {{
      document.getElementById('inspector-drawer').classList.add('translate-x-full');
    }}

    // Charts Initialization
    function initCharts() {{
      const revCtx = document.getElementById('overviewRevenueChart').getContext('2d');
      revenueChartInstance = new Chart(revCtx, {{
        type: 'line',
        data: {{
          labels: ['1 Окт', '5 Окт', '10 Окт', '15 Окт', '20 Окт', '25 Окт', '30 Окт'],
          datasets: [{{
            label: 'Выручка (₽)',
            data: [1500, 3000, 3000, 4500, 6000, 6900, 8400],
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointBackgroundColor: '#6366f1',
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            x: {{ grid: {{ color: 'rgba(39, 39, 42, 0.5)' }}, ticks: {{ color: '#71717a', font: {{ size: 10 }} }} }},
            y: {{ grid: {{ color: 'rgba(39, 39, 42, 0.5)' }}, ticks: {{ color: '#71717a', font: {{ size: 10 }} }} }}
          }}
        }}
      }});

      const donutCtx = document.getElementById('tierDonutChart').getContext('2d');
      donutChartInstance = new Chart(donutCtx, {{
        type: 'doughnut',
        data: {{
          labels: ['Стартовый', 'Профессиональный'],
          datasets: [{{
            data: [60, 40],
            backgroundColor: ['#6366f1', '#06b6d4'],
            borderWidth: 0,
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          cutout: '75%',
        }}
      }});

      const latCtx = document.getElementById('resilienceLatencyChart').getContext('2d');
      latencyChartInstance = new Chart(latCtx, {{
        type: 'bar',
        data: {{
          labels: ['00:00', '04:00', '08:00', '12:00 (504 Timeout)', '16:00 (Canary)', '20:00 (Recovered)'],
          datasets: [{{
            label: 'Задержка ответа шлюза (мс)',
            data: [35, 40, 42, 1400, 85, 38],
            backgroundColor: ['#10b981', '#10b981', '#10b981', '#f43f5e', '#f59e0b', '#10b981'],
            borderRadius: 6,
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            x: {{ grid: {{ display: false }}, ticks: {{ color: '#71717a', font: {{ size: 10 }} }} }},
            y: {{ grid: {{ color: 'rgba(39, 39, 42, 0.5)' }}, ticks: {{ color: '#71717a', font: {{ size: 10 }} }} }}
          }}
        }}
      }});
    }}

    // Data Syncing with Backend
    async function refreshData() {{
      try {{
        const statsRes = await fetch('/api/v1/system/stats');
        const stats = await statsRes.json();

        document.getElementById('kpi-revenue').innerText = parseFloat(stats.total_revenue).toLocaleString('ru-RU', {{ minimumFractionDigits: 2 }}) + ' ₽';
        document.getElementById('kpi-subscriptions').innerText = stats.subscriptions_count;
        document.getElementById('kpi-invoices').innerText = stats.invoices_count;
        document.getElementById('kpi-tenants').innerText = stats.tenants_count;
        document.getElementById('nav-badge-subs').innerText = stats.subscriptions_count;
        document.getElementById('nav-badge-invs').innerText = stats.invoices_count;

        // Circuit Breaker Badges
        const cb = stats.circuit_breaker;
        const hBadgeState = document.getElementById('header-cb-state');
        const hDot = document.getElementById('header-cb-dot');
        const cbDeckBadge = document.getElementById('cb-cockpit-badge');
        const cbDeckState = document.getElementById('cb-cockpit-state');
        const cbDeckFailures = document.getElementById('cb-cockpit-failures');

        hBadgeState.innerText = cb.state;
        cbDeckState.innerText = cb.state;
        cbDeckFailures.innerText = `${{cb.failure_count}} сбоев`;

        if (cb.state === 'CLOSED') {{
          hDot.className = 'w-2 h-2 rounded-full bg-emerald-400';
          hBadgeState.className = 'font-bold font-mono text-emerald-400';
          cbDeckBadge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 flex items-center gap-2 glow-closed';
        }} else if (cb.state === 'OPEN') {{
          hDot.className = 'w-2 h-2 rounded-full bg-rose-400';
          hBadgeState.className = 'font-bold font-mono text-rose-400';
          cbDeckBadge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold border border-rose-500/30 bg-rose-500/10 text-rose-400 flex items-center gap-2 glow-open';
        }} else {{
          hDot.className = 'w-2 h-2 rounded-full bg-amber-400';
          hBadgeState.className = 'font-bold font-mono text-amber-400';
          cbDeckBadge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold border border-amber-500/30 bg-amber-500/10 text-amber-400 flex items-center gap-2 glow-half';
        }}

        // Subscriptions
        const subsRes = await fetch('/api/v1/system/subscriptions');
        const subs = await subsRes.json();
        const subTbody = document.getElementById('subscriptions-table-body');
        if (subs.length === 0) {{
          subTbody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-zinc-500 font-sans">Нет действующих подписок</td></tr>';
        }} else {{
          subTbody.innerHTML = subs.map(s => `
            <tr class="hover:bg-zinc-850/60 transition cursor-pointer" onclick="inspectSubscription('${{s.id}}')">
              <td class="px-5 py-3.5 font-mono text-zinc-200 font-semibold flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-brand-400"></span>
                <span>${{s.customer_id}}</span>
              </td>
              <td class="px-5 py-3.5 text-indigo-400">${{s.plan_name}}</td>
              <td class="px-5 py-3.5 font-mono text-zinc-400">${{new Date(s.current_period_end).toLocaleDateString('ru-RU')}}</td>
              <td class="px-5 py-3.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${{s.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950 text-rose-400 border border-rose-800/60'}}">
                  ${{s.status}}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right" onclick="event.stopPropagation()">
                <button onclick="promptUpgrade('${{s.id}}')" class="px-2.5 py-1 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-indigo-300 text-[11px] font-medium transition border border-zinc-700">
                  Апгрейд
                </button>
              </td>
            </tr>
          `).join('');
        }}

        // Invoices
        const invsRes = await fetch('/api/v1/system/invoices');
        const invs = await invsRes.json();
        document.getElementById('invoices-count-badge').innerText = `${{invs.length}} счетов`;
        const invTbody = document.getElementById('invoices-table-body');
        if (invs.length === 0) {{
          invTbody.innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-zinc-500 font-sans">Счета отсутствуют</td></tr>';
        }} else {{
          invTbody.innerHTML = invs.map(inv => `
            <tr class="hover:bg-zinc-850/60 transition cursor-pointer" onclick="inspectInvoice('${{inv.id}}')">
              <td class="px-5 py-3.5 font-mono text-zinc-300">#${{inv.id.substring(0, 8)}}</td>
              <td class="px-5 py-3.5 font-bold mono-num text-white">${{parseFloat(inv.total_amount).toLocaleString('ru-RU', {{ minimumFractionDigits: 2 }})}} ₽</td>
              <td class="px-5 py-3.5 text-zinc-400 max-w-xs truncate" title="${{inv.items_summary}}">${{inv.items_summary}}</td>
              <td class="px-5 py-3.5 font-mono text-zinc-400 text-[11px]">${{new Date(inv.created_at).toLocaleString('ru-RU')}}</td>
              <td class="px-5 py-3.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${{inv.status === 'PAID' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : inv.status === 'FAILED' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}}">
                  ${{inv.status}}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right" onclick="event.stopPropagation()">
                <button onclick="inspectInvoice('${{inv.id}}')" class="text-zinc-400 hover:text-white transition">
                  <i data-lucide="eye" class="w-4 h-4"></i>
                </button>
              </td>
            </tr>
          `).join('');
        }}

        // Plans
        const plansRes = await fetch('/api/v1/plans?tenant_id=tenant-demo');
        const plans = await plansRes.json();
        const plansGrid = document.getElementById('plans-cards-grid');
        plansGrid.innerHTML = plans.map(p => `
          <div class="border border-zinc-800 bg-zinc-900 p-6 rounded-2xl flex flex-col justify-between hover:border-zinc-700 transition shadow-sm">
            <div>
              <div class="flex items-center justify-between">
                <h4 class="text-base font-bold text-white">${{p.name}}</h4>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">${{p.period}}</span>
              </div>
              <p class="text-2xl font-extrabold text-white mt-3 mono-num">${{parseFloat(p.price).toLocaleString('ru-RU')}} ₽ <span class="text-xs font-normal text-zinc-400">/ период</span></p>
              
              <div class="mt-4 pt-4 border-t border-zinc-800 space-y-2 text-xs text-zinc-400">
                <div class="flex justify-between">
                  <span>Включенная квота:</span>
                  <strong class="text-zinc-200 mono-num">${{p.included_units}} ед.</strong>
                </div>
                <div class="flex justify-between">
                  <span>Цена перерасхода:</span>
                  <strong class="text-zinc-200 mono-num">${{p.overage_unit_price}} ₽ / ед.</strong>
                </div>
                ${{p.trial_days > 0 ? `<div class="flex justify-between text-indigo-400"><span>Пробный период:</span><strong>${{p.trial_days}} дней бесплатно</strong></div>` : ''}}
              </div>
            </div>
            <button onclick="prefillSubscription('${{p.id}}')" class="mt-6 w-full py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold transition border border-zinc-700">
              Оформить договор
            </button>
          </div>
        `).join('');

        // Outbox events
        const outboxRes = await fetch('/api/v1/system/outbox');
        if (outboxRes.ok) {{
          const outboxEvents = await outboxRes.json();
          const outboxTbody = document.getElementById('outbox-table-body');
          if (outboxEvents.length === 0) {{
            outboxTbody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-zinc-500 font-sans">Журнал событий чист</td></tr>';
          }} else {{
            outboxTbody.innerHTML = outboxEvents.map(e => `
              <tr class="hover:bg-zinc-850/60 transition">
                <td class="px-5 py-3.5 text-zinc-400 text-[11px]">${{e.event_id.substring(0, 12)}}...</td>
                <td class="px-5 py-3.5 text-indigo-400 font-semibold">${{e.event_type}}</td>
                <td class="px-5 py-3.5 text-zinc-300 font-sans">${{e.tenant_id}}</td>
                <td class="px-5 py-3.5 text-zinc-400 text-[11px]">${{new Date(e.occurred_at).toLocaleTimeString('ru-RU')}}</td>
                <td class="px-5 py-3.5 text-right font-sans">
                  <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">
                    ACID PERSISTED
                  </span>
                </td>
              </tr>
            `).join('');
          }}
        }}

        lucide.createIcons();
      }} catch (err) {{
        console.error("Dashboard sync error:", err);
      }}
    }}

    // Inspector Helpers
    async function inspectSubscription(subId) {{
      const subsRes = await fetch('/api/v1/system/subscriptions');
      const subs = await subsRes.json();
      const s = subs.find(item => item.id === subId);
      if (!s) return;

      const html = `
        <div class="space-y-4">
          <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-1.5">
            <span class="text-[10px] uppercase font-mono text-zinc-500 tracking-wider">Клиент</span>
            <p class="text-sm font-bold text-white font-mono">${{s.customer_id}}</p>
            <p class="text-[11px] text-zinc-400">Арендатор: ${{s.tenant_id}}</p>
          </div>

          <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-zinc-400">Тарифный план:</span>
              <span class="text-indigo-400 font-bold">${{s.plan_name}}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-zinc-400">Статус:</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">${{s.status}}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-zinc-400">Действует до:</span>
              <span class="text-zinc-200 font-mono">${{new Date(s.current_period_end).toLocaleDateString('ru-RU')}}</span>
            </div>
          </div>

          <div class="pt-2">
            <button onclick="closeDrawer(); promptUpgrade('${{s.id}}')" class="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow">
              Сменить тариф (Proration)
            </button>
          </div>
        </div>
      `;
      openDrawer('Договор подписки', '#' + s.id.substring(0, 12), html);
    }}

    async function inspectInvoice(invId) {{
      const invsRes = await fetch('/api/v1/system/invoices');
      const invs = await invsRes.json();
      const inv = invs.find(item => item.id === invId);
      if (!inv) return;

      const html = `
        <div class="space-y-4">
          <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-1">
            <div class="flex justify-between items-center">
              <span class="text-[10px] uppercase font-mono text-zinc-500">Сумма начисления</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">${{inv.status}}</span>
            </div>
            <p class="text-2xl font-extrabold text-white mono-num mt-1">${{parseFloat(inv.total_amount).toLocaleString('ru-RU', {{ minimumFractionDigits: 2 }})}} ₽</p>
          </div>

          <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-2">
            <span class="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block">Детализация строк счета:</span>
            <p class="text-xs text-zinc-200">${{inv.items_summary}}</p>
            <div class="pt-2 border-t border-zinc-800/80 flex justify-between text-zinc-400 text-[11px]">
              <span>Дата создания:</span>
              <span class="font-mono text-zinc-300">${{new Date(inv.created_at).toLocaleString('ru-RU')}}</span>
            </div>
          </div>

          <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
            <span class="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-1">Идемпотентность & Аудит</span>
            <p class="text-[11px] font-mono text-emerald-400">✓ Защита от двойных списаний проверена</p>
          </div>
        </div>
      `;
      openDrawer('Платежное требование', '#' + inv.id.substring(0, 12), html);
    }}

    // Circuit Breaker Actions
    async function tripCircuitBreaker() {{
      const res = await fetch('/api/v1/system/circuit-breaker/trip', {{ method: 'POST' }});
      const data = await res.json();
      showToast(data.message, true);
      refreshData();
    }}

    async function resetCircuitBreaker() {{
      const res = await fetch('/api/v1/system/circuit-breaker/reset', {{ method: 'POST' }});
      const data = await res.json();
      showToast(data.message);
      refreshData();
    }}

    // Subscriptions & Usage Actions
    async function submitSubscription() {{
      const custId = document.getElementById('sub-input-customer').value;
      const planId = document.getElementById('sub-input-plan').value;
      const idemp = document.getElementById('sub-input-idemp').value;

      const res = await fetch('/api/v1/subscriptions', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          tenant_id: 'tenant-demo',
          customer_id: custId,
          plan_id: planId,
          payment_method_id: 'card-4242',
          idempotency_key: idemp
        }})
      }});

      if (res.ok) {{
        closeModal('modal-subscribe');
        showToast(`Клиент ${{custId}} успешно подписан!`);
        refreshData();
      }} else {{
        showToast('Ошибка оформления (возможно, сработал Circuit Breaker)', true);
      }}
    }}

    function prefillSubscription(planId) {{
      document.getElementById('sub-input-plan').value = planId;
      document.getElementById('sub-input-customer').value = 'cust-' + Math.floor(Math.random() * 900 + 100);
      document.getElementById('sub-input-idemp').value = 'tx-' + Date.now();
      openModal('modal-subscribe');
    }}

    function promptUpgrade(subId) {{
      document.getElementById('upgrade-sub-id').value = subId;
      openModal('modal-proration');
    }}

    async function confirmPlanUpgrade() {{
      const subId = document.getElementById('upgrade-sub-id').value;
      const newPlanId = document.getElementById('upgrade-target-plan').value;
      const res = await fetch(`/api/v1/subscriptions/${{subId}}/change-plan`, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          tenant_id: 'tenant-demo',
          new_plan_id: newPlanId,
          payment_method_id: 'card-4242',
          idempotency_key: 'upgrade-' + Date.now()
        }})
      }});

      if (res.ok) {{
        const data = await res.json();
        closeModal('modal-proration');
        showToast(`Апгрейд завершен! Доплата: ${{data.proration.net_amount_due}} ₽ (зачтено ${{data.proration.unspent_credit}} ₽)`);
        refreshData();
      }} else {{
        showToast('Ошибка при перерасчете тарифа', true);
      }}
    }}

    async function quickRecordUsage() {{
      const subsRes = await fetch('/api/v1/system/subscriptions');
      const subs = await subsRes.json();
      if (subs.length === 0) {{
        showToast('Сначала создайте договор подписки', true);
        return;
      }}
      const targetSub = subs[0];
      const res = await fetch('/api/v1/usage', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          tenant_id: targetSub.tenant_id,
          subscription_id: targetSub.id,
          metric_name: 'api_calls',
          units: 150
        }})
      }});
      if (res.ok) {{
        showToast(`Зафиксировано 150 вызовов API для ${{targetSub.customer_id}}!`);
        refreshData();
      }}
    }}

    async function triggerBillingCycle() {{
      const res = await fetch('/api/v1/billing-cycle/run', {{ method: 'POST' }});
      const data = await res.json();
      showToast(`Биллинг завершен: ${{data.renewed_count}} продлено, ${{data.failed_count}} сбоев.`);
      refreshData();
    }}

    // Initial Load & Popstate
    window.addEventListener('DOMContentLoaded', () => {{
      initCharts();
      switchWindow('{initial_window}');
      refreshData();
      setInterval(refreshData, 4000);
    }});

    window.addEventListener('popstate', () => {{
      const path = window.location.pathname.replace('/dashboard', '').replace('/', '') || 'overview';
      switchWindow(path);
    }});
  </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard_root() -> HTMLResponse:
    """Renders the master command center overview window."""
    return HTMLResponse(content=build_dashboard_html("overview"))


@router.get("/dashboard/subscriptions", response_class=HTMLResponse)
def get_dashboard_subscriptions() -> HTMLResponse:
    """Renders the dedicated subscriptions workspace window."""
    return HTMLResponse(content=build_dashboard_html("subscriptions"))


@router.get("/dashboard/invoices", response_class=HTMLResponse)
def get_dashboard_invoices() -> HTMLResponse:
    """Renders the dedicated invoices ledger window."""
    return HTMLResponse(content=build_dashboard_html("invoices"))


@router.get("/dashboard/plans", response_class=HTMLResponse)
def get_dashboard_plans() -> HTMLResponse:
    """Renders the dedicated pricing plan designer window."""
    return HTMLResponse(content=build_dashboard_html("plans"))


@router.get("/dashboard/resilience", response_class=HTMLResponse)
def get_dashboard_resilience() -> HTMLResponse:
    """Renders the dedicated resilience & Circuit Breaker cockpit window."""
    return HTMLResponse(content=build_dashboard_html("resilience"))


@router.get("/dashboard/outbox", response_class=HTMLResponse)
def get_dashboard_outbox() -> HTMLResponse:
    """Renders the dedicated Transactional Outbox stream window."""
    return HTMLResponse(content=build_dashboard_html("outbox"))
