from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Visual Dashboard"])

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ru" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Subscription Engine — Enterprise Billing & Resilience Console</title>
  
  <!-- Modern UI Stack: Tailwind CSS, Inter & JetBrains Mono fonts, Lucide Icons, Chart.js -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          },
          colors: {
            brand: {
              50: '#eef2ff',
              100: '#e0e7ff',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
            },
            surface: {
              DEFAULT: '#0f172a',
              card: '#1e293b',
              border: '#334155',
              subtle: '#090d16',
            }
          }
        }
      }
    }
  </script>

  <style>
    body { font-family: 'Inter', sans-serif; }
    .mono-num { font-family: 'JetBrains Mono', monospace; font-feature-settings: "tnum"; }
    .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: #0f172a; }
    .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    .pulse-glow { animation: pulse-glow 2s infinite; }
    @keyframes pulse-glow {
      0%, 100% { box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
      50% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.1); }
    }
    .pulse-glow-red { animation: pulse-glow-red 1.5s infinite; }
    @keyframes pulse-glow-red {
      0%, 100% { box-shadow: 0 0 18px rgba(239, 68, 68, 0.5); }
      50% { box-shadow: 0 0 6px rgba(239, 68, 68, 0.2); }
    }
  </style>
</head>
<body class="bg-surface-subtle text-slate-100 min-h-screen flex antialiased selection:bg-brand-500 selection:text-white">

  <!-- Left Enterprise Sidebar -->
  <aside class="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between hidden md:flex shrink-0">
    <div>
      <!-- Brand Logo -->
      <div class="h-16 px-6 flex items-center gap-3 border-b border-slate-800">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center font-bold text-white shadow-lg shadow-brand-500/20">
          <i data-lucide="shield-check" class="w-5 h-5"></i>
        </div>
        <div>
          <span class="text-sm font-bold tracking-tight text-white block">Subscription Engine</span>
          <span class="text-[10px] text-slate-400 font-mono tracking-wider uppercase block">Clean Architecture</span>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <nav class="p-4 space-y-1.5 text-xs font-medium">
        <button onclick="switchTab('overview')" id="nav-overview" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-white bg-slate-800/80 transition">
          <i data-lucide="layout-dashboard" class="w-4 h-4 text-brand-400"></i>
          <span>Сводный обзор</span>
        </button>
        <button onclick="switchTab('subscriptions')" id="nav-subscriptions" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition">
          <i data-lucide="credit-card" class="w-4 h-4"></i>
          <span>Договоры подписок</span>
        </button>
        <button onclick="switchTab('invoices')" id="nav-invoices" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition">
          <i data-lucide="receipt" class="w-4 h-4"></i>
          <span>Счета и транзакции</span>
        </button>
        <button onclick="switchTab('plans')" id="nav-plans" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition">
          <i data-lucide="layers" class="w-4 h-4"></i>
          <span>Тарифная сетка</span>
        </button>
        <button onclick="switchTab('resilience')" id="nav-resilience" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition">
          <i data-lucide="activity" class="w-4 h-4 text-emerald-400"></i>
          <span>Отказоустойчивость & CB</span>
        </button>
        <button onclick="switchTab('outbox')" id="nav-outbox" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition">
          <i data-lucide="send" class="w-4 h-4 text-amber-400"></i>
          <span>Transactional Outbox</span>
        </button>
      </nav>
    </div>

    <!-- Bottom System Status -->
    <div class="p-4 border-t border-slate-800/80 bg-slate-950/60">
      <div class="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-[11px] space-y-1">
        <div class="flex items-center justify-between text-slate-400">
          <span>Среда:</span>
          <span class="font-mono text-emerald-400 font-semibold">Production-ready</span>
        </div>
        <div class="flex items-center justify-between text-slate-400">
          <span>RPO Гарантия:</span>
          <span class="font-mono text-slate-200">0 (Zero Data Loss)</span>
        </div>
        <div class="flex items-center justify-between text-slate-400">
          <span>Идемпотентность:</span>
          <span class="font-mono text-brand-400">Enforced</span>
        </div>
      </div>
      <a href="/docs" target="_blank" class="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition">
        <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
        <span>OpenAPI / Swagger</span>
      </a>
    </div>
  </aside>

  <!-- Main Workspace -->
  <div class="flex-1 flex flex-col min-w-0 overflow-y-auto custom-scrollbar">

    <!-- Top Header -->
    <header class="h-16 px-6 border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-40 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">v1.0.0</span>
        <h2 id="current-tab-title" class="text-sm font-semibold text-white">Сводный обзор системы</h2>
      </div>
      <div class="flex items-center gap-3">
        <!-- Live Circuit Breaker status badge in top header -->
        <div id="header-cb-indicator" class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-xs font-medium">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span class="text-slate-400 font-mono">Circuit Breaker:</span>
          <span id="header-cb-state" class="font-bold text-emerald-400 font-mono">CLOSED</span>
        </div>
        <button onclick="refreshData()" class="p-2 rounded-lg bg-slate-850 hover:bg-slate-800 text-slate-300 transition border border-slate-800" title="Обновить данные">
          <i data-lucide="refresh-cw" class="w-4 h-4"></i>
        </button>
      </div>
    </header>

    <!-- Page Body -->
    <main class="p-6 md:p-8 space-y-6 max-w-7xl w-full mx-auto">

      <!-- ================= SECTION: OVERVIEW ================= -->
      <div id="tab-overview" class="space-y-6">
        
        <!-- KPI Metrics Grid (Stripe / Tremor style) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div class="bg-slate-900 border border-slate-800/80 p-5 rounded-xl relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Собранная выручка</span>
              <div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                <i data-lucide="banknote" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-bold text-white mt-3 mono-num" id="kpi-revenue">0.00 ₽</p>
            <div class="flex items-center gap-1.5 mt-2 text-xs text-emerald-400">
              <i data-lucide="trending-up" class="w-3.5 h-3.5"></i>
              <span>100% подтвержденных начислений</span>
            </div>
          </div>

          <div class="bg-slate-900 border border-slate-800/80 p-5 rounded-xl relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Активные договоры</span>
              <div class="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 flex items-center justify-center">
                <i data-lucide="users" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-bold text-white mt-3 mono-num" id="kpi-subscriptions">0</p>
            <div class="flex items-center gap-1.5 mt-2 text-xs text-slate-400">
              <i data-lucide="shield" class="w-3.5 h-3.5 text-brand-400"></i>
              <span>Без просроченных выплат</span>
            </div>
          </div>

          <div class="bg-slate-900 border border-slate-800/80 p-5 rounded-xl relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Выставленные счета</span>
              <div class="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
                <i data-lucide="file-text" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-bold text-white mt-3 mono-num" id="kpi-invoices">0</p>
            <div class="flex items-center gap-1.5 mt-2 text-xs text-slate-400">
              <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-amber-400"></i>
              <span>Строгая идемпотентность</span>
            </div>
          </div>

          <div class="bg-slate-900 border border-slate-800/80 p-5 rounded-xl relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Арендаторы (Тенанты)</span>
              <div class="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
                <i data-lucide="building" class="w-4 h-4"></i>
              </div>
            </div>
            <p class="text-2xl font-bold text-white mt-3 mono-num" id="kpi-tenants">0</p>
            <div class="flex items-center gap-1.5 mt-2 text-xs text-purple-400">
              <i data-lucide="lock" class="w-3.5 h-3.5"></i>
              <span>Полная изоляция данных</span>
            </div>
          </div>

        </div>

        <!-- Charts Grid (Financial & Latency Curves) -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xs font-semibold uppercase text-slate-400 tracking-wider">Динамика финансовых потоков</h3>
                <p class="text-xs text-slate-500 mt-0.5">Регулярные списания и расчет овердрафта квот</p>
              </div>
              <span class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">RUB</span>
            </div>
            <div class="h-64">
              <canvas id="revenueChart"></canvas>
            </div>
          </div>

          <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xs font-semibold uppercase text-slate-400 tracking-wider">Мониторинг задержек шлюза</h3>
                <p class="text-xs text-slate-500 mt-0.5">Всплески отказов банка и реакция Circuit Breaker</p>
              </div>
              <span class="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">p99 Latency</span>
            </div>
            <div class="h-64">
              <canvas id="latencyChart"></canvas>
            </div>
          </div>
        </div>

        <!-- Quick Demo Action Deck -->
        <div class="bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 p-6 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 class="text-sm font-semibold text-white flex items-center gap-2">
              <i data-lucide="play" class="w-4 h-4 text-brand-400"></i>
              <span>Интерактивные сценарии демонстрации</span>
            </h3>
            <p class="text-xs text-slate-400 mt-1 max-w-xl">
              Проверьте архитектурные инварианты прямо сейчас: генерация повторных вызовов с гарантией идемпотентности, искусственный срыв соединения и ночной расчет начислений.
            </p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button onclick="openModal('modal-subscribe')" class="px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium transition flex items-center gap-1.5 shadow-sm">
              <i data-lucide="user-plus" class="w-3.5 h-3.5"></i>
              <span>Оформить клиента</span>
            </button>
            <button onclick="quickRecordUsage()" class="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition flex items-center gap-1.5">
              <i data-lucide="bar-chart-2" class="w-3.5 h-3.5"></i>
              <span>+150 API вызовов</span>
            </button>
            <button onclick="triggerBillingCycle()" class="px-3.5 py-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-medium transition flex items-center gap-1.5">
              <i data-lucide="moon" class="w-3.5 h-3.5"></i>
              <span>Ночной биллинг</span>
            </button>
          </div>
        </div>

      </div>

      <!-- ================= SECTION: SUBSCRIPTIONS ================= -->
      <div id="tab-subscriptions" class="hidden space-y-4">
        <div class="flex items-center justify-between bg-slate-900 p-4 rounded-xl border border-slate-800">
          <div>
            <h3 class="text-sm font-semibold text-white">Управление договорами подписок</h3>
            <p class="text-xs text-slate-400 mt-0.5">Жизненный цикл договоров, контроль расчетных периодов и смена планов</p>
          </div>
          <button onclick="openModal('modal-subscribe')" class="px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium transition flex items-center gap-1.5 shadow-sm">
            <i data-lucide="plus" class="w-3.5 h-3.5"></i>
            <span>Новая подписка</span>
          </button>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-300">
              <thead class="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th class="px-5 py-3.5">Клиент (Customer ID)</th>
                  <th class="px-5 py-3.5">Тарифный план</th>
                  <th class="px-5 py-3.5">Период действия</th>
                  <th class="px-5 py-3.5">Статус договора</th>
                  <th class="px-5 py-3.5 text-right">Действия</th>
                </tr>
              </thead>
              <tbody id="subscriptions-table-body" class="divide-y divide-slate-800/60 font-medium">
                <tr><td colspan="5" class="px-5 py-8 text-center text-slate-500">Загрузка договоров...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ================= SECTION: INVOICES ================= -->
      <div id="tab-invoices" class="hidden space-y-4">
        <div class="flex items-center justify-between bg-slate-900 p-4 rounded-xl border border-slate-800">
          <div>
            <h3 class="text-sm font-semibold text-white">Реестр платежных требований (Ledger)</h3>
            <p class="text-xs text-slate-400 mt-0.5">Неизменяемый журнал финансовых списаний с гарантией идемпотентности</p>
          </div>
          <span class="text-xs font-mono text-slate-400" id="invoices-count-label">0 счетов</span>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-300">
              <thead class="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th class="px-5 py-3.5">Идентификатор счета</th>
                  <th class="px-5 py-3.5">Сумма начисления</th>
                  <th class="px-5 py-3.5">Назначение платежа</th>
                  <th class="px-5 py-3.5">Дата выставления</th>
                  <th class="px-5 py-3.5">Статус</th>
                </tr>
              </thead>
              <tbody id="invoices-table-body" class="divide-y divide-slate-800/60">
                <tr><td colspan="5" class="px-5 py-8 text-center text-slate-500">Загрузка счетов...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ================= SECTION: PLANS ================= -->
      <div id="tab-plans" class="hidden space-y-4">
        <div class="flex items-center justify-between bg-slate-900 p-4 rounded-xl border border-slate-800">
          <div>
            <h3 class="text-sm font-semibold text-white">Каталог тарифных сеток</h3>
            <p class="text-xs text-slate-400 mt-0.5">Тарифы с фиксированной ставкой, лимитами квот и ценой за перерасход</p>
          </div>
          <span class="text-xs text-slate-400">Организация: Acme Cloud Platform</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="plans-cards-grid">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- ================= SECTION: RESILIENCE & CIRCUIT BREAKER ================= -->
      <div id="tab-resilience" class="hidden space-y-6">
        
        <!-- Circuit Breaker Visual Deck -->
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-slate-800">
            <div>
              <div class="flex items-center gap-3">
                <h3 class="text-lg font-bold text-white">Предохранитель платежного шлюза (Circuit Breaker)</h3>
                <span id="cb-deck-badge" class="px-3 py-1 rounded-full text-xs font-mono font-bold border flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                  <span id="cb-deck-state">CLOSED</span>
                </span>
              </div>
              <p class="text-xs text-slate-400 mt-2 max-w-2xl leading-relaxed">
                Автомат отказоустойчивости изолирует сетевые сбои банка. При достижении порогового значения ошибок система мгновенно переходит в <span class="text-rose-400 font-mono font-semibold">OPEN</span>, блокируя лавину запросов и сохраняя доступность локального ядра.
              </p>
            </div>
            
            <div class="flex items-center gap-3">
              <button onclick="tripCircuitBreaker()" class="px-4 py-2.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-xs font-medium transition flex items-center gap-2">
                <i data-lucide="zap-off" class="w-4 h-4 text-rose-400"></i>
                <span>Инъекция 504 Gateway Timeout</span>
              </button>
              <button onclick="resetCircuitBreaker()" class="px-4 py-2.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-medium transition flex items-center gap-2">
                <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>
                <span>Восстановить (CLOSED)</span>
              </button>
            </div>
          </div>

          <!-- Circuit Breaker Internal Metrics -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6">
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800/80">
              <span class="text-xs text-slate-400 uppercase tracking-wider block">Порог срабатывания</span>
              <span class="text-xl font-bold font-mono text-white mt-1 block">3 подряд отказа</span>
              <span class="text-[11px] text-slate-500 mt-1 block">Лимит до перехода в OPEN</span>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800/80">
              <span class="text-xs text-slate-400 uppercase tracking-wider block">Текущий счетчик сбоев</span>
              <span id="cb-deck-failures" class="text-xl font-bold font-mono text-amber-400 mt-1 block">0 ошибок</span>
              <span class="text-[11px] text-slate-500 mt-1 block">Сбрасывается при успехе</span>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800/80">
              <span class="text-xs text-slate-400 uppercase tracking-wider block">Таймаут зондирования</span>
              <span class="text-xl font-bold font-mono text-indigo-400 mt-1 block">15.0 секунд</span>
              <span class="text-[11px] text-slate-500 mt-1 block">Переход в режим HALF_OPEN</span>
            </div>
          </div>
        </div>

        <!-- Smart Dunning Section -->
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <h3 class="text-sm font-semibold text-white flex items-center gap-2">
            <i data-lucide="clock" class="w-4 h-4 text-brand-400"></i>
            <span>Политика повторных списаний (Smart Dunning Engine)</span>
          </h3>
          <p class="text-xs text-slate-400 mt-1 leading-relaxed">
            В случае временного сетевого сбоя система не спамит банк одинаковыми интервалами, а вычисляет время следующей попытки по формуле экспоненциального бэкоффа со случайным джиттером (<code class="text-slate-300">Base * Multiplier^Attempt + Jitter</code>).
          </p>
          <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div class="border border-slate-800 bg-slate-950/60 p-3 rounded-lg">
              <span class="text-slate-400">Попытка 1:</span> <span class="font-mono text-white font-semibold">через ~4 часа</span>
            </div>
            <div class="border border-slate-800 bg-slate-950/60 p-3 rounded-lg">
              <span class="text-slate-400">Попытка 2:</span> <span class="font-mono text-white font-semibold">через ~8 часов (+джиттер)</span>
            </div>
            <div class="border border-slate-800 bg-slate-950/60 p-3 rounded-lg">
              <span class="text-slate-400">Попытка 3:</span> <span class="font-mono text-white font-semibold">через ~16 часов (финал)</span>
            </div>
          </div>
        </div>

      </div>

      <!-- ================= SECTION: TRANSACTIONAL OUTBOX ================= -->
      <div id="tab-outbox" class="hidden space-y-4">
        <div class="flex items-center justify-between bg-slate-900 p-4 rounded-xl border border-slate-800">
          <div>
            <h3 class="text-sm font-semibold text-white">Журнал Transactional Outbox (Аудит событий)</h3>
            <p class="text-xs text-slate-400 mt-0.5">События фиксируются в единой транзакции со счетами, гарантируя доставку без потерь</p>
          </div>
          <span class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Zero Data Loss</span>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-300">
              <thead class="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th class="px-5 py-3.5">ID События</th>
                  <th class="px-5 py-3.5">Тип доменного события</th>
                  <th class="px-5 py-3.5">Арендатор</th>
                  <th class="px-5 py-3.5">Время фиксации</th>
                  <th class="px-5 py-3.5">Статус</th>
                </tr>
              </thead>
              <tbody id="outbox-table-body" class="divide-y divide-slate-800/60 font-mono">
                <tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Загрузка журнала событий...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </main>
  </div>

  <!-- Modal: Subscribe Customer -->
  <div id="modal-subscribe" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-2xl p-6 shadow-2xl space-y-5">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <h3 class="text-base font-bold text-white">Оформление договора подписки</h3>
        <button onclick="closeModal('modal-subscribe')" class="text-slate-400 hover:text-white">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>
      
      <div class="space-y-4 text-xs">
        <div>
          <label class="block text-slate-300 font-medium mb-1">Идентификатор клиента (Customer ID)</label>
          <input type="text" id="sub-input-customer" value="cust-client-201" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 font-mono focus:border-brand-500 focus:outline-none">
        </div>
        <div>
          <label class="block text-slate-300 font-medium mb-1">Тарифный план</label>
          <select id="sub-input-plan" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 focus:border-brand-500 focus:outline-none">
            <option value="plan-basic">Стартовый тариф (1500 ₽/мес, 100 ед. квоты)</option>
            <option value="plan-pro">Профессиональный (4500 ₽/мес, 500 ед. квоты)</option>
            <option value="plan-trial">Корпоративный Триал (14 дней бесплатно)</option>
          </select>
        </div>
        <div>
          <label class="block text-slate-300 font-medium mb-1">Ключ идемпотентности (Idempotency Key)</label>
          <input type="text" id="sub-input-idemp" value="tx-order-001" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 font-mono text-[11px] focus:border-brand-500 focus:outline-none">
          <p class="text-[10px] text-slate-500 mt-1">Гарантирует защиту от повторного списания средств при сбоях сети.</p>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
        <button onclick="closeModal('modal-subscribe')" class="px-4 py-2 rounded-lg text-slate-400 hover:text-white text-xs font-medium">Отмена</button>
        <button onclick="submitSubscription()" class="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow">Оформить</button>
      </div>
    </div>
  </div>

  <!-- Modal: Plan Upgrade with Proration -->
  <div id="modal-proration" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl p-6 shadow-2xl space-y-5">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 class="text-base font-bold text-white">Смена тарифного плана</h3>
          <p class="text-xs text-slate-400">Автоматический пропорциональный перерасчет (Proration)</p>
        </div>
        <button onclick="closeModal('modal-proration')" class="text-slate-400 hover:text-white">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <input type="hidden" id="upgrade-sub-id" value="">

      <div class="space-y-4 text-xs">
        <div>
          <label class="block text-slate-300 font-medium mb-1">Целевой тариф для апгрейда</label>
          <select id="upgrade-target-plan" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 focus:border-brand-500 focus:outline-none">
            <option value="plan-pro">Профессиональный (4500.00 ₽ / мес)</option>
            <option value="plan-trial">Корпоративный (12000.00 ₽ / мес)</option>
          </select>
        </div>

        <!-- Proration Formula Card -->
        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Математика взаимозачета:</span>
          <div class="flex justify-between text-slate-300">
            <span>Неизрасходованный остаток старого тарифа:</span>
            <span class="text-emerald-400 font-mono font-semibold" id="proration-credit">Зачет в чек</span>
          </div>
          <div class="flex justify-between text-slate-300">
            <span>Стоимость нового тарифа до конца периода:</span>
            <span class="text-slate-100 font-mono font-semibold" id="proration-new-cost">Расчет...</span>
          </div>
          <div class="border-t border-slate-800 pt-2 flex justify-between text-sm font-bold text-white">
            <span>К доплате прямо сейчас:</span>
            <span class="text-amber-400 font-mono" id="proration-net-due">Точная разница</span>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
        <button onclick="closeModal('modal-proration')" class="px-4 py-2 rounded-lg text-slate-400 hover:text-white text-xs font-medium">Отмена</button>
        <button onclick="confirmPlanUpgrade()" class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow">Подтвердить апгрейд</button>
      </div>
    </div>
  </div>

  <!-- Notification Toast Component -->
  <div id="toast" class="fixed bottom-5 right-5 max-w-sm bg-slate-900 border border-slate-700 text-slate-100 px-4 py-3 rounded-xl shadow-2xl text-xs transition-all duration-300 opacity-0 pointer-events-none flex items-center space-x-3 z-50">
    <div id="toast-icon"></div>
    <span id="toast-message" class="leading-snug">Уведомление</span>
  </div>

  <!-- App Script Logic -->
  <script>
    let currentTab = 'overview';
    let revenueChartInstance = null;
    let latencyChartInstance = null;

    // Switch Tabs
    function switchTab(tabId) {
      const tabs = ['overview', 'subscriptions', 'invoices', 'plans', 'resilience', 'outbox'];
      tabs.forEach(t => {
        document.getElementById(`tab-${t}`).classList.add('hidden');
        document.getElementById(`nav-${t}`).classList.remove('bg-slate-800/80', 'text-white');
        document.getElementById(`nav-${t}`).classList.add('text-slate-400');
      });

      document.getElementById(`tab-${tabId}`).classList.remove('hidden');
      document.getElementById(`nav-${tabId}`).classList.add('bg-slate-800/80', 'text-white');
      document.getElementById(`nav-${tabId}`).classList.remove('text-slate-400');

      const titles = {
        overview: 'Сводный обзор системы',
        subscriptions: 'Договоры подписок арендаторов',
        invoices: 'Реестр счетов и платежных поручений',
        plans: 'Тарифная сетка и лимиты',
        resilience: 'Отказоустойчивость & Circuit Breaker',
        outbox: 'Журнал Transactional Outbox',
      };
      document.getElementById('current-tab-title').innerText = titles[tabId] || 'Обзор';
      currentTab = tabId;
      lucide.createIcons();
    }

    function showToast(msg, isError = false) {
      const toast = document.getElementById('toast');
      const text = document.getElementById('toast-message');
      const icon = document.getElementById('toast-icon');
      text.innerText = msg;
      icon.innerHTML = isError 
        ? '<i data-lucide="alert-triangle" class="w-4 h-4 text-rose-400"></i>'
        : '<i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>';
      toast.className = `fixed bottom-5 right-5 max-w-sm border px-4 py-3 rounded-xl shadow-2xl text-xs transition-all duration-300 opacity-100 flex items-center space-x-3 z-50 ${isError ? 'bg-rose-950/90 border-rose-800 text-rose-200' : 'bg-slate-900 border-slate-700 text-slate-100'}`;
      lucide.createIcons();
      setTimeout(() => { toast.classList.replace('opacity-100', 'opacity-0'); }, 3500);
    }

    function openModal(id) {
      document.getElementById(id).classList.remove('hidden');
      lucide.createIcons();
    }

    function closeModal(id) {
      document.getElementById(id).classList.add('hidden');
    }

    // Initialize Charts
    function initCharts() {
      const revCtx = document.getElementById('revenueChart').getContext('2d');
      revenueChartInstance = new Chart(revCtx, {
        type: 'line',
        data: {
          labels: ['1 Окт', '5 Окт', '10 Окт', '15 Окт', '20 Окт', '25 Окт', '30 Окт'],
          datasets: [{
            label: 'Выручка (₽)',
            data: [1500, 3000, 3000, 4500, 6000, 6900, 8400],
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointBackgroundColor: '#6366f1',
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
            y: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8', font: { size: 10 } } }
          }
        }
      });

      const latCtx = document.getElementById('latencyChart').getContext('2d');
      latencyChartInstance = new Chart(latCtx, {
        type: 'bar',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            label: 'Задержка (мс)',
            data: [42, 38, 45, 120, 55, 40],
            backgroundColor: 'rgba(16, 185, 129, 0.7)',
            borderRadius: 4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
            y: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8', font: { size: 10 } } }
          }
        }
      });
    }

    // Refresh Data from APIs
    async function refreshData() {
      try {
        const statsRes = await fetch('/api/v1/system/stats');
        const stats = await statsRes.json();
        
        document.getElementById('kpi-revenue').innerText = parseFloat(stats.total_revenue).toLocaleString('ru-RU', { minimumFractionDigits: 2 }) + ' ₽';
        document.getElementById('kpi-subscriptions').innerText = stats.subscriptions_count;
        document.getElementById('kpi-invoices').innerText = stats.invoices_count;
        document.getElementById('kpi-tenants').innerText = stats.tenants_count;

        // Circuit Breaker Indicators
        const cb = stats.circuit_breaker;
        const hBadge = document.getElementById('header-cb-state');
        hBadge.innerText = cb.state;
        
        const deckBadge = document.getElementById('cb-deck-badge');
        const deckState = document.getElementById('cb-deck-state');
        const deckFailures = document.getElementById('cb-deck-failures');
        deckFailures.innerText = `${cb.failure_count} сбоев`;
        deckState.innerText = cb.state;

        if (cb.state === 'CLOSED') {
          hBadge.className = 'font-bold text-emerald-400 font-mono';
          deckBadge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 flex items-center gap-2 pulse-glow';
        } else if (cb.state === 'OPEN') {
          hBadge.className = 'font-bold text-rose-400 font-mono';
          deckBadge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold border border-rose-500/30 bg-rose-500/10 text-rose-400 flex items-center gap-2 pulse-glow-red';
        } else {
          hBadge.className = 'font-bold text-amber-400 font-mono';
          deckBadge.className = 'px-3 py-1 rounded-full text-xs font-mono font-bold border border-amber-500/30 bg-amber-500/10 text-amber-400 flex items-center gap-2';
        }

        // Subscriptions
        const subsRes = await fetch('/api/v1/system/subscriptions');
        const subs = await subsRes.json();
        const subTbody = document.getElementById('subscriptions-table-body');
        if (subs.length === 0) {
          subTbody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Нет действующих подписок</td></tr>';
        } else {
          subTbody.innerHTML = subs.map(s => `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="px-5 py-3.5 font-mono text-slate-200">${s.customer_id}</td>
              <td class="px-5 py-3.5 text-indigo-400">${s.plan_name}</td>
              <td class="px-5 py-3.5 font-mono text-slate-400">${new Date(s.current_period_end).toLocaleDateString('ru-RU')}</td>
              <td class="px-5 py-3.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${s.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950 text-rose-400 border border-rose-800/60'}">
                  ${s.status}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right">
                <button onclick="promptUpgrade('${s.id}')" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 text-[11px] font-medium transition border border-slate-700">
                  Апгрейд тарифа
                </button>
              </td>
            </tr>
          `).join('');
        }

        // Invoices
        const invsRes = await fetch('/api/v1/system/invoices');
        const invs = await invsRes.json();
        document.getElementById('invoices-count-label').innerText = `${invs.length} счетов в журнале`;
        const invTbody = document.getElementById('invoices-table-body');
        if (invs.length === 0) {
          invTbody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Счета отсутствуют</td></tr>';
        } else {
          invTbody.innerHTML = invs.map(inv => `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="px-5 py-3.5 font-mono text-slate-300">#${inv.id.substring(0, 8)}</td>
              <td class="px-5 py-3.5 font-bold mono-num text-white">${parseFloat(inv.total_amount).toLocaleString('ru-RU', { minimumFractionDigits: 2 })} ₽</td>
              <td class="px-5 py-3.5 text-slate-400 max-w-xs truncate" title="${inv.items_summary}">${inv.items_summary}</td>
              <td class="px-5 py-3.5 font-mono text-slate-400 text-[11px]">${new Date(inv.created_at).toLocaleString('ru-RU')}</td>
              <td class="px-5 py-3.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${inv.status === 'PAID' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : inv.status === 'FAILED' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">
                  ${inv.status}
                </span>
              </td>
            </tr>
          `).join('');
        }

        // Plans
        const plansRes = await fetch('/api/v1/plans?tenant_id=tenant-demo');
        const plans = await plansRes.json();
        const plansGrid = document.getElementById('plans-cards-grid');
        plansGrid.innerHTML = plans.map(p => `
          <div class="border border-slate-800 bg-slate-900 p-5 rounded-2xl flex flex-col justify-between hover:border-slate-700 transition">
            <div>
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-white">${p.name}</h4>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">${p.period}</span>
              </div>
              <p class="text-2xl font-bold text-white mt-3 mono-num">${parseFloat(p.price).toLocaleString('ru-RU')} ₽ <span class="text-xs font-normal text-slate-400">/ расчетный период</span></p>
              
              <div class="mt-4 pt-4 border-t border-slate-800 space-y-2 text-xs text-slate-400">
                <div class="flex justify-between">
                  <span>Включенная квота:</span>
                  <strong class="text-slate-200 mono-num">${p.included_units} ед.</strong>
                </div>
                <div class="flex justify-between">
                  <span>Цена за перерасход:</span>
                  <strong class="text-slate-200 mono-num">${p.overage_unit_price} ₽ / ед.</strong>
                </div>
                ${p.trial_days > 0 ? `<div class="flex justify-between text-indigo-400"><span>Пробный период:</span><strong>${p.trial_days} дней</strong></div>` : ''}
              </div>
            </div>
            <button onclick="prefillSubscription('${p.id}')" class="mt-5 w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition border border-slate-700">
              Выбрать тариф
            </button>
          </div>
        `).join('');

        // Outbox events
        const outboxRes = await fetch('/api/v1/system/outbox');
        if (outboxRes.ok) {
          const outboxEvents = await outboxRes.json();
          const outboxTbody = document.getElementById('outbox-table-body');
          if (outboxEvents.length === 0) {
            outboxTbody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Журнал событий чист</td></tr>';
          } else {
            outboxTbody.innerHTML = outboxEvents.map(e => `
              <tr class="hover:bg-slate-800/40 transition">
                <td class="px-5 py-3.5 text-slate-400 text-[11px]">${e.event_id.substring(0, 12)}...</td>
                <td class="px-5 py-3.5 text-indigo-400 font-semibold">${e.event_type}</td>
                <td class="px-5 py-3.5 text-slate-300 font-sans">${e.tenant_id}</td>
                <td class="px-5 py-3.5 text-slate-400 text-[11px]">${new Date(e.occurred_at).toLocaleTimeString('ru-RU')}</td>
                <td class="px-5 py-3.5 font-sans">
                  <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">
                    PERSISTED (ACID)
                  </span>
                </td>
              </tr>
            `).join('');
          }
        }

      } catch (err) {
        console.error("Dashboard sync error:", err);
      }
    }

    // Circuit Breaker Actions
    async function tripCircuitBreaker() {
      const res = await fetch('/api/v1/system/circuit-breaker/trip', { method: 'POST' });
      const data = await res.json();
      showToast(data.message, true);
      refreshData();
    }

    async function resetCircuitBreaker() {
      const res = await fetch('/api/v1/system/circuit-breaker/reset', { method: 'POST' });
      const data = await res.json();
      showToast(data.message);
      refreshData();
    }

    // Business Actions
    async function submitSubscription() {
      const custId = document.getElementById('sub-input-customer').value;
      const planId = document.getElementById('sub-input-plan').value;
      const idemp = document.getElementById('sub-input-idemp').value;

      const res = await fetch('/api/v1/subscriptions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: 'tenant-demo',
          customer_id: custId,
          plan_id: planId,
          payment_method_id: 'card-4242',
          idempotency_key: idemp
        })
      });

      if (res.ok) {
        closeModal('modal-subscribe');
        showToast(`Клиент ${custId} успешно подписан!`);
        refreshData();
      } else {
        showToast('Ошибка оформления (возможно, сработал Circuit Breaker)', true);
      }
    }

    function prefillSubscription(planId) {
      document.getElementById('sub-input-plan').value = planId;
      document.getElementById('sub-input-customer').value = 'cust-' + Math.floor(Math.random() * 900 + 100);
      document.getElementById('sub-input-idemp').value = 'tx-' + Date.now();
      openModal('modal-subscribe');
    }

    function promptUpgrade(subId) {
      document.getElementById('upgrade-sub-id').value = subId;
      openModal('modal-proration');
    }

    async function confirmPlanUpgrade() {
      const subId = document.getElementById('upgrade-sub-id').value;
      const newPlanId = document.getElementById('upgrade-target-plan').value;
      const res = await fetch(`/api/v1/subscriptions/${subId}/change-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: 'tenant-demo',
          new_plan_id: newPlanId,
          payment_method_id: 'card-4242',
          idempotency_key: 'upgrade-' + Date.now()
        })
      });

      if (res.ok) {
        const data = await res.json();
        closeModal('modal-proration');
        showToast(`Апгрейд завершен! Доплата: ${data.proration.net_amount_due} ₽ (зачтено ${data.proration.unspent_credit} ₽)`);
        refreshData();
      } else {
        showToast('Ошибка при перерасчете тарифа', true);
      }
    }

    async function quickRecordUsage() {
      const subsRes = await fetch('/api/v1/system/subscriptions');
      const subs = await subsRes.json();
      if (subs.length === 0) {
        showToast('Сначала создайте договор подписки', true);
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
        showToast(`Зафиксировано 150 вызовов API для ${targetSub.customer_id}!`);
        refreshData();
      }
    }

    async function triggerBillingCycle() {
      const res = await fetch('/api/v1/billing-cycle/run', { method: 'POST' });
      const data = await res.json();
      showToast(`Биллинг завершен: ${data.renewed_count} продлено, ${data.failed_count} сбоев.`);
      refreshData();
    }

    // Startup
    window.addEventListener('DOMContentLoaded', () => {
      initCharts();
      refreshData();
      lucide.createIcons();
      setInterval(refreshData, 4000);
    });
  </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard() -> HTMLResponse:
    """Renders visual enterprise administrative dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)
