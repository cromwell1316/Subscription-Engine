from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Visual Dashboard"])


def build_dashboard_html(initial_window: str = "overview") -> str:
    return f"""<!DOCTYPE html>
<html lang="ru" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Subscription Engine — FinTech Billing & Resilience Workstation</title>
  
  <!-- Modern FinTech Stack: Tailwind CSS (FinTech Slate & Emerald Palette), Lucide Icons, Chart.js -->
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
            slate: {{
              850: '#111827',
              900: '#0b0f19',
              925: '#070b12',
              950: '#030712',
            }},
            fintech: {{
              emerald: '#10b981',
              mint: '#34d399',
              teal: '#14b8a6',
              cyan: '#06b6d4',
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
    .custom-scrollbar::-webkit-scrollbar-track {{ background: #030712; }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 4px; }}
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {{ background: #334155; }}
    
    /* Glowing states for FinTech Emerald theme */
    .glow-emerald {{ box-shadow: 0 0 20px rgba(16, 185, 129, 0.28); }}
    .glow-rose {{ box-shadow: 0 0 24px rgba(244, 63, 94, 0.35); }}
    .glow-amber {{ box-shadow: 0 0 20px rgba(245, 158, 11, 0.28); }}
    .glow-cyan {{ box-shadow: 0 0 20px rgba(6, 182, 212, 0.28); }}

    /* Drawer & Modal transitions */
    .drawer-transition {{ transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1); }}
    .modal-backdrop {{ backdrop-filter: blur(8px); background-color: rgba(3, 7, 18, 0.75); }}

    /* Tremor Tracker Block Styles */
    .tracker-block {{
      transition: transform 0.15s ease, filter 0.15s ease;
    }}
    .tracker-block:hover {{
      transform: scaleY(1.4);
      filter: brightness(1.25);
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex antialiased selection:bg-emerald-500 selection:text-slate-950">

  <!-- ================= LEFT SIDEBAR (SLATE & EMERALD) ================= -->
  <aside class="w-64 border-r border-slate-800/80 bg-slate-925 flex flex-col justify-between hidden lg:flex shrink-0 z-30">
    <div>
      <!-- Brand & Platform Header -->
      <div class="h-16 px-5 flex items-center justify-between border-b border-slate-800/80">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600 flex items-center justify-center font-bold text-slate-950 shadow-lg shadow-emerald-500/20">
            <i data-lucide="shield-check" class="w-5 h-5 text-slate-950"></i>
          </div>
          <div>
            <span class="text-xs font-bold tracking-tight text-white block">Subscription Engine</span>
            <span class="text-[10px] text-emerald-400 font-mono tracking-wider uppercase block">FinTech • Hexagonal</span>
          </div>
        </div>
      </div>

      <!-- Tenant Switcher Dropdown (Tremor style) -->
      <div class="p-3">
        <div class="px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs flex items-center justify-between shadow-sm">
          <div class="flex items-center gap-2.5">
            <div class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></div>
            <div>
              <span class="font-medium text-slate-200 block text-xs">Acme Cloud Platform</span>
              <span class="text-[10px] text-slate-400 font-mono">tenant-demo</span>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800/60 uppercase">RUB</span>
        </div>
      </div>

      <!-- Navigation Workspaces (Multi-Window Launcher) -->
      <div class="px-3 pt-2">
        <p class="px-3 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold mb-1.5">Рабочие окна</p>
        <nav class="space-y-1 text-xs font-medium">
          <button onclick="openWindowTab('overview')" id="sidebar-nav-overview" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-white bg-slate-850 border border-emerald-500/30 transition shadow-sm">
            <div class="flex items-center gap-2.5">
              <i data-lucide="layout-dashboard" class="w-4 h-4 text-emerald-400"></i>
              <span>1. Сводный обзор (Overview)</span>
            </div>
            <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">KPI</span>
          </button>
          
          <button onclick="openWindowTab('subscriptions')" id="sidebar-nav-subscriptions" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition">
            <div class="flex items-center gap-2.5">
              <i data-lucide="credit-card" class="w-4 h-4 text-teal-400"></i>
              <span>2. Договоры подписок</span>
            </div>
            <span id="nav-badge-subs" class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">0</span>
          </button>

          <button onclick="openWindowTab('invoices')" id="sidebar-nav-invoices" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition">
            <div class="flex items-center gap-2.5">
              <i data-lucide="receipt" class="w-4 h-4 text-amber-400"></i>
              <span>3. Счета и проводки</span>
            </div>
            <span id="nav-badge-invs" class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">0</span>
          </button>

          <button onclick="openWindowTab('resilience')" id="sidebar-nav-resilience" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition">
            <div class="flex items-center gap-2.5">
              <i data-lucide="activity" class="w-4 h-4 text-rose-400"></i>
              <span>4. Отказоустойчивость & CB</span>
            </div>
            <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-rose-950/80 text-rose-400 border border-rose-800/80">SLA</span>
          </button>

          <button onclick="openWindowTab('usage')" id="sidebar-nav-usage" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition">
            <div class="flex items-center gap-2.5">
              <i data-lucide="gauge" class="w-4 h-4 text-cyan-400"></i>
              <span>5. Учет квот и потребления</span>
            </div>
            <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/80">API</span>
          </button>

          <button onclick="openWindowTab('outbox')" id="sidebar-nav-outbox" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition">
            <div class="flex items-center gap-2.5">
              <i data-lucide="send" class="w-4 h-4 text-emerald-400"></i>
              <span>6. Transactional Outbox</span>
            </div>
            <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">RPO=0</span>
          </button>

          <button onclick="openWindowTab('plans')" id="sidebar-nav-plans" class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition">
            <div class="flex items-center gap-2.5">
              <i data-lucide="layers" class="w-4 h-4 text-purple-400"></i>
              <span>7. Конструктор тарифов</span>
            </div>
            <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">Tiers</span>
          </button>
        </nav>
      </div>
    </div>

    <!-- Bottom System SLA Status Card -->
    <div class="p-3 border-t border-slate-800/80 bg-slate-950/70 space-y-2.5">
      <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-3 text-[11px] space-y-1.5 shadow-sm">
        <div class="flex items-center justify-between text-slate-400">
          <span>Среда биллинга:</span>
          <span class="font-mono text-emerald-400 font-semibold flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Live Core
          </span>
        </div>
        <div class="flex items-center justify-between text-slate-400">
          <span>RPO гарантия:</span>
          <span class="font-mono text-slate-200">0 (Zero Data Loss)</span>
        </div>
        <div class="flex items-center justify-between text-slate-400">
          <span>Идемпотентность:</span>
          <span class="font-mono text-emerald-400 font-semibold">Strict Key (AES)</span>
        </div>
      </div>
      
      <div class="flex gap-2">
        <button onclick="openCommandPalette()" class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-850 text-xs font-medium text-slate-300 transition border border-slate-800">
          <i data-lucide="command" class="w-3.5 h-3.5 text-emerald-400"></i>
          <span>Команды (Ctrl+K)</span>
        </button>
        <a href="/docs" target="_blank" class="p-2 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-400 hover:text-slate-200 border border-slate-800 transition" title="Swagger OpenAPI">
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </a>
      </div>
    </div>
  </aside>

  <!-- ================= MASTER WORKSPACE ================= -->
  <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

    <!-- TOP HEADER: Split-View Controls & Circuit Breaker Cockpit Indicator -->
    <header class="h-16 px-6 border-b border-slate-800/80 bg-slate-925/90 backdrop-blur-md sticky top-0 z-20 flex items-center justify-between shrink-0">
      
      <!-- Left: Mobile Menu + Title + Breadcrumbs -->
      <div class="flex items-center gap-3">
        <button onclick="toggleMobileSidebar()" class="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white lg:hidden">
          <i data-lucide="menu" class="w-5 h-5"></i>
        </button>
        <div class="flex items-center gap-2.5">
          <span class="text-xs px-2 py-0.5 rounded-md bg-emerald-950/80 text-emerald-300 border border-emerald-800/80 font-mono font-semibold">FinTech Engine</span>
          <h2 id="window-title" class="text-sm font-bold text-white tracking-tight">Сводный обзор системы</h2>
        </div>
      </div>

      <!-- Right: Multi-Window Split Toggle + Live Breaker Pill + Quick Actions -->
      <div class="flex items-center gap-3">
        
        <!-- DUAL SPLIT-VIEW TOGGLE BUTTON -->
        <button id="btn-split-toggle" onclick="toggleSplitView()" class="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-900 hover:bg-slate-850 text-xs font-medium text-slate-300 transition shadow-sm" title="Включить просмотр двух окон рядом">
          <i data-lucide="columns-2" class="w-4 h-4 text-emerald-400"></i>
          <span class="hidden sm:inline">Сплит-экран</span>
          <span id="badge-split-status" class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">Выкл</span>
        </button>

        <!-- Live Circuit Breaker Indicator Pill -->
        <div id="header-cb-card" class="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-900 text-xs shadow-sm">
          <span id="header-cb-dot" class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          <span class="text-slate-400 font-mono hidden md:inline">Circuit Breaker:</span>
          <span id="header-cb-state" class="font-bold font-mono text-emerald-400">CLOSED</span>
        </div>

        <!-- Quick Refresh -->
        <button onclick="refreshData()" class="p-2 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-300 transition border border-slate-800" title="Обновить состояние всех окон">
          <i data-lucide="refresh-cw" class="w-4 h-4"></i>
        </button>
      </div>
    </header>

    <!-- ================= HORIZONTAL WINDOW TABS BAR (BROWSER / IDE STYLE) ================= -->
    <div class="bg-slate-950 border-b border-slate-800/80 px-4 py-1.5 flex items-center justify-between overflow-x-auto custom-scrollbar shrink-0">
      <div id="window-tabs-container" class="flex items-center gap-1.5">
        <!-- Dynamically populated window tabs with close 'x' buttons -->
      </div>

      <!-- Add Window Dropdown Button -->
      <div class="relative ml-2">
        <button onclick="toggleNewWindowMenu()" class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-850 text-xs text-slate-300 border border-slate-800 transition">
          <i data-lucide="plus" class="w-3.5 h-3.5 text-emerald-400"></i>
          <span class="text-[11px] font-medium hidden sm:inline">Окно</span>
        </button>
        <div id="dropdown-new-window" class="absolute right-0 mt-1 w-56 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-1.5 hidden z-40 space-y-1 text-xs">
          <button onclick="openWindowTab('overview'); toggleNewWindowMenu();" class="w-full text-left px-3 py-1.5 rounded-lg text-slate-200 hover:bg-slate-800 flex items-center gap-2">
            <i data-lucide="layout-dashboard" class="w-3.5 h-3.5 text-emerald-400"></i> Сводный обзор
          </button>
          <button onclick="openWindowTab('subscriptions'); toggleNewWindowMenu();" class="w-full text-left px-3 py-1.5 rounded-lg text-slate-200 hover:bg-slate-800 flex items-center gap-2">
            <i data-lucide="credit-card" class="w-3.5 h-3.5 text-teal-400"></i> Договоры подписок
          </button>
          <button onclick="openWindowTab('invoices'); toggleNewWindowMenu();" class="w-full text-left px-3 py-1.5 rounded-lg text-slate-200 hover:bg-slate-800 flex items-center gap-2">
            <i data-lucide="receipt" class="w-3.5 h-3.5 text-amber-400"></i> Счета и проводки
          </button>
          <button onclick="openWindowTab('resilience'); toggleNewWindowMenu();" class="w-full text-left px-3 py-1.5 rounded-lg text-slate-200 hover:bg-slate-800 flex items-center gap-2">
            <i data-lucide="activity" class="w-3.5 h-3.5 text-rose-400"></i> Отказоустойчивость & CB
          </button>
          <button onclick="openWindowTab('usage'); toggleNewWindowMenu();" class="w-full text-left px-3 py-1.5 rounded-lg text-slate-200 hover:bg-slate-800 flex items-center gap-2">
            <i data-lucide="gauge" class="w-3.5 h-3.5 text-cyan-400"></i> Учет квот и потребления
          </button>
          <button onclick="openWindowTab('outbox'); toggleNewWindowMenu();" class="w-full text-left px-3 py-1.5 rounded-lg text-slate-200 hover:bg-slate-800 flex items-center gap-2">
            <i data-lucide="send" class="w-3.5 h-3.5 text-emerald-400"></i> Transactional Outbox
          </button>
          <button onclick="openWindowTab('plans'); toggleNewWindowMenu();" class="w-full text-left px-3 py-1.5 rounded-lg text-slate-200 hover:bg-slate-800 flex items-center gap-2">
            <i data-lucide="layers" class="w-3.5 h-3.5 text-purple-400"></i> Конструктор тарифов
          </button>
        </div>
      </div>
    </div>

    <!-- ================= DYNAMIC MULTI-WINDOW WORKSPACE ================= -->
    <main class="flex-1 overflow-y-auto custom-scrollbar p-5 md:p-7 bg-slate-950">
      
      <!-- SINGLE VIEW CONTAINER -->
      <div id="single-window-viewport" class="max-w-7xl mx-auto space-y-6">
        <!-- The active window template will be cloned/rendered here -->
        <div id="primary-window-slot"></div>
      </div>

      <!-- DUAL SPLIT-VIEW CONTAINER (SIDE-BY-SIDE 50/50) -->
      <div id="split-window-viewport" class="hidden grid grid-cols-1 xl:grid-cols-2 gap-6 w-full">
        <!-- Left Pane (Primary Window) -->
        <div class="bg-slate-925 border border-slate-800/90 rounded-2xl p-5 shadow-xl flex flex-col min-h-[700px]">
          <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <h3 id="split-left-title" class="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">Окно 1 (Primary)</h3>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">Left Dock</span>
          </div>
          <div id="split-left-slot" class="flex-1 overflow-y-auto custom-scrollbar"></div>
        </div>

        <!-- Right Pane (Secondary Window with selector) -->
        <div class="bg-slate-925 border border-slate-800/90 rounded-2xl p-5 shadow-xl flex flex-col min-h-[700px]">
          <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-teal-400"></span>
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">Окно 2 (Secondary):</h3>
            </div>
            <select id="split-secondary-selector" onchange="changeSecondaryWindow(this.value)" class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 font-medium focus:outline-none focus:border-emerald-500">
              <option value="resilience">Отказоустойчивость & CB (Chaos Lab)</option>
              <option value="subscriptions">Договоры подписок</option>
              <option value="invoices">Счета и проводки</option>
              <option value="usage">Учет квот и потребления</option>
              <option value="outbox">Transactional Outbox</option>
              <option value="overview">Сводный обзор</option>
            </select>
          </div>
          <div id="split-right-slot" class="flex-1 overflow-y-auto custom-scrollbar"></div>
        </div>
      </div>

    </main>
  </div>

  <!-- ================= WINDOW CONTENT TEMPLATES (HIDDEN DOCK) ================= -->
  <div id="window-templates" class="hidden">

    <!-- ================= 1. OVERVIEW WINDOW ================= -->
    <div id="template-overview" class="space-y-6">

      <!-- Tremor Callout: Architectural Guarantee -->
      <div class="bg-gradient-to-r from-emerald-950/60 via-slate-900 to-teal-950/40 border border-emerald-500/30 rounded-2xl p-4 flex items-center justify-between shadow-lg shadow-emerald-950/20">
        <div class="flex items-center gap-3.5">
          <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
            <i data-lucide="shield-check" class="w-5 h-5"></i>
          </div>
          <div>
            <h4 class="text-xs font-bold text-white tracking-wide">Доменное ядро активно: Идемпотентность и перерасчет защищены</h4>
            <p class="text-[11px] text-slate-400 mt-0.5">Все операции списаний и прорации математически изолированы в слое Domain и защищены от дубликатов по ключу идемпотентности.</p>
          </div>
        </div>
        <div class="hidden sm:flex items-center gap-2">
          <span class="text-[10px] font-mono px-2 py-1 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-800/80 font-bold">RPO=0 Active</span>
        </div>
      </div>

      <!-- Tremor-Style KPI Cards Grid with Delta Badges -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <!-- Revenue Card -->
        <div class="bg-slate-900 border border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-sm hover:border-slate-700 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Фактическая выручка</span>
            <div class="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <i data-lucide="wallet" class="w-4 h-4"></i>
            </div>
          </div>
          <p class="text-2xl font-extrabold text-white mt-3 mono-num" id="kpi-revenue">0.00 ₽</p>
          <div class="flex items-center gap-2 mt-2.5">
            <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <i data-lucide="trending-up" class="w-3 h-3"></i>
              <span>+100% факт</span>
            </span>
            <span class="text-xs text-slate-500">Подтверждено банком</span>
          </div>
        </div>

        <!-- Subscriptions Card -->
        <div class="bg-slate-900 border border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-sm hover:border-slate-700 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Активные договоры</span>
            <div class="w-8 h-8 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center">
              <i data-lucide="users" class="w-4 h-4"></i>
            </div>
          </div>
          <p class="text-2xl font-extrabold text-white mt-3 mono-num" id="kpi-subscriptions">0</p>
          <div class="flex items-center gap-2 mt-2.5">
            <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20 flex items-center gap-1">
              <span>0.0% отток (Churn)</span>
            </span>
            <span class="text-xs text-slate-500">Действующие подписки</span>
          </div>
        </div>

        <!-- Invoices Card -->
        <div class="bg-slate-900 border border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-sm hover:border-slate-700 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Сформировано счетов</span>
            <div class="w-8 h-8 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <i data-lucide="receipt" class="w-4 h-4"></i>
            </div>
          </div>
          <p class="text-2xl font-extrabold text-white mt-3 mono-num" id="kpi-invoices">0</p>
          <div class="flex items-center gap-2 mt-2.5">
            <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1">
              <span>100% проводка</span>
            </span>
            <span class="text-xs text-slate-500">Включая прорацию</span>
          </div>
        </div>

        <!-- Resilience Status Card -->
        <div class="bg-slate-900 border border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-sm hover:border-slate-700 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">SLA Доступности</span>
            <div class="w-8 h-8 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <i data-lucide="activity" class="w-4 h-4"></i>
            </div>
          </div>
          <p class="text-2xl font-extrabold text-white mt-3 mono-num">99.98%</p>
          <div class="flex items-center gap-2 mt-2.5">
            <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <span>RPO=0</span>
            </span>
            <span class="text-xs text-slate-500">Smart Dunning & CB</span>
          </div>
        </div>
      </div>

      <!-- ================= TREMOR TRACKER: LIVE SYSTEM TELEMETRY TIMELINE ================= -->
      <div class="bg-slate-900 border border-slate-800/90 rounded-2xl p-5 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2 font-mono">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
              Tremor Tracker: Монитор доступности платежного шлюза (SLA Uptime)
            </h4>
            <p class="text-[11px] text-slate-400 mt-0.5">Непрерывная фиксация ответов внешнего банка, задержек и срабатываний Circuit Breaker</p>
          </div>
          <div class="flex items-center gap-3 text-xs text-slate-400 font-mono">
            <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded bg-emerald-500"></span> 200 OK</span>
            <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded bg-amber-500"></span> Retry</span>
            <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded bg-rose-500"></span> Outage</span>
          </div>
        </div>

        <!-- 40 Segmented Blocks representing timeline -->
        <div class="grid grid-cols-40 gap-1 h-9 p-1 rounded-xl bg-slate-950 border border-slate-800/80 items-center" id="tremor-tracker-bar">
          <!-- Dynamically populated 40 blocks -->
        </div>

        <div class="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-1 border-t border-slate-800/60">
          <span>T - 40 минут назад</span>
          <span>Среднее время ответа (p95): 42 мс</span>
          <span>Текущий момент (Live)</span>
        </div>
      </div>

      <!-- Main Visual Analytics: Revenue Growth & Portfolio Doughnut -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left: Line Area Chart for Revenue Trend -->
        <div class="lg:col-span-2 bg-slate-900 border border-slate-800/90 p-5 rounded-2xl shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold text-white">Динамика подтвержденной выручки (MRR Trend)</h3>
              <p class="text-xs text-slate-400">Фактические списания с банковских карт за последние 6 расчетных периодов</p>
            </div>
            <span class="text-xs font-mono px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">FinTech Analytics</span>
          </div>
          <div class="h-64 relative">
            <canvas id="chart-revenue-mrr"></canvas>
          </div>
        </div>

        <!-- Right: Status Distribution Doughnut Chart -->
        <div class="bg-slate-900 border border-slate-800/90 p-5 rounded-2xl shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-bold text-white">Портфель подписок</h3>
              <p class="text-xs text-slate-400">Распределение по статусам</p>
            </div>
          </div>
          <div class="h-52 relative flex items-center justify-center">
            <canvas id="chart-status-donut"></canvas>
          </div>
          <div class="pt-2 border-t border-slate-800/80 space-y-1.5 text-xs">
            <div class="flex items-center justify-between text-slate-300">
              <span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> Активные (Active)</span>
              <span class="font-mono font-bold" id="donut-active-cnt">0</span>
            </div>
            <div class="flex items-center justify-between text-slate-300">
              <span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span> В очереди ретраев (Dunning)</span>
              <span class="font-mono font-bold" id="donut-pastdue-cnt">0</span>
            </div>
            <div class="flex items-center justify-between text-slate-300">
              <span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-slate-500"></span> Отмененные (Canceled)</span>
              <span class="font-mono font-bold" id="donut-canceled-cnt">0</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tremor BarList: Top Clients & Quick Engineering Actions Bar -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Tremor BarList: Ranking by Value -->
        <div class="bg-slate-900 border border-slate-800/90 p-5 rounded-2xl shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2 font-mono">
              <i data-lucide="bar-chart-2" class="w-4 h-4 text-emerald-400"></i>
              Рейтинг клиентов по MRR и квотам (Tremor BarList)
            </h3>
            <span class="text-[10px] font-mono text-slate-400">Топ-3</span>
          </div>
          
          <div class="space-y-3 pt-2" id="tremor-barlist-container">
            <!-- Populated by JS -->
          </div>
        </div>

        <!-- Quick Interactive Simulator Action Deck -->
        <div class="bg-slate-900 border border-slate-800/90 p-5 rounded-2xl shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <i data-lucide="sliders" class="w-4 h-4 text-teal-400"></i>
              Быстрые действия биллинг-движка
            </h3>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">Interactive</span>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <button onclick="openModal('modal-subscribe')" class="flex items-center gap-3 p-3 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-800 transition text-left group">
              <div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center group-hover:scale-110 transition">
                <i data-lucide="user-plus" class="w-4 h-4"></i>
              </div>
              <div>
                <p class="text-xs font-semibold text-white">Новая подписка</p>
                <p class="text-[10px] text-slate-400">Оформить договор</p>
              </div>
            </button>

            <button onclick="openModal('modal-proration')" class="flex items-center gap-3 p-3 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-800 transition text-left group">
              <div class="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-400 flex items-center justify-center group-hover:scale-110 transition">
                <i data-lucide="repeat" class="w-4 h-4"></i>
              </div>
              <div>
                <p class="text-xs font-semibold text-white">Смена тарифа</p>
                <p class="text-[10px] text-slate-400">Прорация дней</p>
              </div>
            </button>

            <button onclick="quickRecordUsage()" class="flex items-center gap-3 p-3 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-800 transition text-left group">
              <div class="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center group-hover:scale-110 transition">
                <i data-lucide="zap" class="w-4 h-4"></i>
              </div>
              <div>
                <p class="text-xs font-semibold text-white">+150 вызовов API</p>
                <p class="text-[10px] text-slate-400">Фиксация расхода</p>
              </div>
            </button>

            <button onclick="triggerBillingCycle()" class="flex items-center gap-3 p-3 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-800 transition text-left group">
              <div class="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center group-hover:scale-110 transition">
                <i data-lucide="play" class="w-4 h-4"></i>
              </div>
              <div>
                <p class="text-xs font-semibold text-white">Биллинг-цикл</p>
                <p class="text-[10px] text-slate-400">Продление договоров</p>
              </div>
            </button>
          </div>
        </div>

      </div>

    </div>

    <!-- ================= 2. SUBSCRIPTIONS WINDOW ================= -->
    <div id="template-subscriptions" class="space-y-5">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="text-base font-bold text-white">Реестр договоров подписок (Subscription Matrix)</h3>
          <p class="text-xs text-slate-400">Управление жизненным циклом, тарифами и очередью списаний</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="openModal('modal-subscribe')" class="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-600/20 transition">
            <i data-lucide="plus" class="w-4 h-4"></i>
            <span>Оформить договор</span>
          </button>
          <button onclick="openModal('modal-proration')" class="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-800 text-xs font-medium transition">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-teal-400"></i>
            <span>Перерасчет тарифа</span>
          </button>
        </div>
      </div>

      <!-- Subscriptions Data Table (Shadcn style) -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
              <tr>
                <th class="px-5 py-3.5">Клиент</th>
                <th class="px-5 py-3.5">Тарифный план</th>
                <th class="px-5 py-3.5">Статус договора</th>
                <th class="px-5 py-3.5">Окончание периода</th>
                <th class="px-5 py-3.5">Ретраи банка</th>
                <th class="px-5 py-3.5 text-right">Действие</th>
              </tr>
            </thead>
            <tbody id="subs-table-body" class="divide-y divide-slate-800/70">
              <tr><td colspan="6" class="px-5 py-8 text-center text-slate-500">Загрузка договоров...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ================= 3. INVOICES WINDOW ================= -->
    <div id="template-invoices" class="space-y-5">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="text-base font-bold text-white">Финансовые счета и проводки (Invoices Ledger)</h3>
          <p class="text-xs text-slate-400">Бухгалтерский журнал начислений, прорации и идемпотентных платежей</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="triggerBillingCycle()" class="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-800 text-xs font-medium transition">
            <i data-lucide="play" class="w-3.5 h-3.5 text-amber-400"></i>
            <span>Запустить закрытие цикла</span>
          </button>
        </div>
      </div>

      <!-- Invoices Data Table -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
              <tr>
                <th class="px-5 py-3.5">ID Счета</th>
                <th class="px-5 py-3.5">Клиент</th>
                <th class="px-5 py-3.5">Статус</th>
                <th class="px-5 py-3.5">Сумма требования</th>
                <th class="px-5 py-3.5">Статьи начислений</th>
                <th class="px-5 py-3.5 text-right">Дата создания</th>
              </tr>
            </thead>
            <tbody id="invoices-table-body" class="divide-y divide-slate-800/70 font-mono">
              <tr><td colspan="6" class="px-5 py-8 text-center text-slate-500 font-sans">Загрузка реестра счетов...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ================= 4. RESILIENCE & CIRCUIT BREAKER WINDOW ================= -->
    <div id="template-resilience" class="space-y-6">
      
      <!-- Cockpit Overview Banner -->
      <div class="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <span class="text-xs font-mono uppercase tracking-wider text-rose-400 font-bold px-2 py-0.5 rounded bg-rose-950/80 border border-rose-800/80">Fault Tolerance Cockpit</span>
              <span class="text-xs text-slate-400">• Паттерн Circuit Breaker</span>
            </div>
            <h3 class="text-xl font-extrabold text-white">Лаборатория отказоустойчивости платежного шлюза</h3>
            <p class="text-xs text-slate-400 max-w-xl">
              Защищает ядро биллинга от каскадных сбоев при падении банка (504 Gateway Timeout). При достижении 3 сбоев шлюз размыкается в <span class="font-mono text-rose-400 font-semibold">OPEN</span>, исключая подвисания пула соединений.
            </p>
          </div>

          <div class="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-950 border border-slate-800 min-w-[200px]" id="resilience-state-card">
            <span class="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Текущее состояние</span>
            <span id="resilience-state-text" class="text-2xl font-black font-mono text-emerald-400 mt-1">CLOSED</span>
            <span id="resilience-failure-count" class="text-[11px] font-mono text-slate-400 mt-1">0 / 3 сбоев</span>
          </div>
        </div>
      </div>

      <!-- Dynamic Tremor Alert Callout -->
      <div id="resilience-callout" class="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/20 text-xs text-emerald-300 flex items-start gap-3">
        <i data-lucide="check-circle" class="w-5 h-5 text-emerald-400 shrink-0 mt-0.5"></i>
        <div>
          <span class="font-bold block">Платежный шлюз банка в штатном режиме (CLOSED)</span>
          <span class="text-slate-400 text-[11px]">Транзакции подтверждаются в реальном времени. Сбоев не зафиксировано.</span>
        </div>
      </div>

      <!-- Chaos Engineering Controls Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        <!-- Simulate Outage Card -->
        <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-4">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-rose-500/10 text-rose-400 flex items-center justify-center">
              <i data-lucide="zap-off" class="w-5 h-5"></i>
            </div>
            <div>
              <h4 class="text-sm font-bold text-white">Инъекция сбоя банка (504 Timeout)</h4>
              <p class="text-xs text-slate-400">Эмулирует внезапное падение процессинга</p>
            </div>
          </div>
          <p class="text-xs text-slate-400">
            Переводит эмулятор шлюза в режим сбоев и принудительно переводит Circuit Breaker в режим <span class="font-mono text-rose-400">OPEN</span>. Все новые попытки списаний будут сразу уходить в Smart Dunning.
          </p>
          <button onclick="tripCircuitBreaker()" class="w-full py-2.5 px-4 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs shadow-lg shadow-rose-600/20 transition flex items-center justify-center gap-2">
            <i data-lucide="alert-triangle" class="w-4 h-4"></i>
            <span>Имитировать сбой банка (Trip to OPEN)</span>
          </button>
        </div>

        <!-- Restore Gateway Card -->
        <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-4">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <i data-lucide="shield-check" class="w-5 h-5"></i>
            </div>
            <div>
              <h4 class="text-sm font-bold text-white">Восстановление шлюза (Reset)</h4>
              <p class="text-xs text-slate-400">Нормализация сетевого канала банка</p>
            </div>
          </div>
          <p class="text-xs text-slate-400">
            Сбрасывает счетчик сбоев в 0, переводит предохранитель в <span class="font-mono text-emerald-400">CLOSED</span> и возобновляет успешную обработку платежей в штатном режиме.
          </p>
          <button onclick="resetCircuitBreaker()" class="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition flex items-center justify-center gap-2">
            <i data-lucide="refresh-cw" class="w-4 h-4 text-emerald-400"></i>
            <span>Сбросить предохранитель (Reset to CLOSED)</span>
          </button>
        </div>

      </div>

      <!-- Smart Dunning Policy Timeline -->
      <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-4">
        <h4 class="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <i data-lucide="clock" class="w-4 h-4 text-amber-400"></i>
          Политика умных повторов (Smart Dunning Retry Strategy)
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="font-mono text-[10px] text-emerald-400 font-bold">1-я попытка</span>
            <p class="font-semibold text-white">Мгновенно (Live)</p>
            <p class="text-[10px] text-slate-500">При штатном биллинге</p>
          </div>
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="font-mono text-[10px] text-amber-400 font-bold">2-я попытка</span>
            <p class="font-semibold text-white">+4 часа задержка</p>
            <p class="text-[10px] text-slate-500">Экспоненциальный откат</p>
          </div>
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="font-mono text-[10px] text-amber-400 font-bold">3-я попытка</span>
            <p class="font-semibold text-white">+12 часов задержка</p>
            <p class="text-[10px] text-slate-500">Проверка счета клиента</p>
          </div>
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="font-mono text-[10px] text-rose-400 font-bold">Финал</span>
            <p class="font-semibold text-white">Приостановка (PAST_DUE)</p>
            <p class="text-[10px] text-slate-500">Отключение сервиса</p>
          </div>
        </div>
      </div>

    </div>

    <!-- ================= 5. USAGE & QUOTAS WINDOW ================= -->
    <div id="template-usage" class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 class="text-base font-bold text-white">Учет потребления и квот API (Metering & Quotas)</h3>
          <p class="text-xs text-slate-400">Контроль лимитов тарифов, расчет перерасхода (Usage-based billing)</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="quickRecordUsage()" class="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-600/20 transition">
            <i data-lucide="plus" class="w-4 h-4"></i>
            <span>Зафиксировать +150 вызовов</span>
          </button>
        </div>
      </div>

      <!-- Tremor CategoryBar: Quota Consumption Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="usage-quotas-grid">
        <!-- Rendered by JS -->
      </div>

      <!-- Usage Records Stream Table -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div class="p-4 border-b border-slate-800 flex items-center justify-between">
          <h4 class="text-xs font-bold text-white uppercase tracking-wider font-mono">Журнал фиксации потребления API</h4>
          <span class="text-[10px] font-mono text-slate-400">Stream Live</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
              <tr>
                <th class="px-5 py-3.5">ID записи</th>
                <th class="px-5 py-3.5">Клиент</th>
                <th class="px-5 py-3.5">Подписка</th>
                <th class="px-5 py-3.5">Объем (Единицы)</th>
                <th class="px-5 py-3.5 text-right">Время фиксации</th>
              </tr>
            </thead>
            <tbody id="usage-table-body" class="divide-y divide-slate-800/70 font-mono">
              <tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Загрузка журнала потребления...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ================= 6. OUTBOX STREAM WINDOW ================= -->
    <div id="template-outbox" class="space-y-5">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-base font-bold text-white">Transactional Outbox Stream (RPO = 0)</h3>
          <p class="text-xs text-slate-400">Гарантия целостности данных: доменные события сохраняются в единой транзакции с изменениями</p>
        </div>
        <span class="text-xs font-mono px-2.5 py-1 rounded-xl bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">At-Least-Once Delivery</span>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
              <tr>
                <th class="px-5 py-3.5">ID События</th>
                <th class="px-5 py-3.5">Тип доменного события</th>
                <th class="px-5 py-3.5">Арендатор</th>
                <th class="px-5 py-3.5">Время фиксации</th>
                <th class="px-5 py-3.5 text-right">Транзакционный статус</th>
              </tr>
            </thead>
            <tbody id="outbox-table-body" class="divide-y divide-slate-800/70 font-mono">
              <tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Загрузка событий outbox...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ================= 7. PLANS WINDOW ================= -->
    <div id="template-plans" class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-base font-bold text-white">Каталог тарифных планов (Pricing Tier Matrix)</h3>
          <p class="text-xs text-slate-400">Параметры квот, триал-периодов и стоимости единицы перерасхода</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Plan 1 -->
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between shadow-sm hover:border-slate-700 transition">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">Стартовый</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">plan-basic</span>
            </div>
            <div>
              <p class="text-3xl font-extrabold text-white mono-num">1 500 ₽ <span class="text-xs font-normal text-slate-400">/ месяц</span></p>
              <p class="text-xs text-slate-400 mt-1">Идеально для индивидуальных проектов</p>
            </div>
            <ul class="text-xs text-slate-300 space-y-2.5 pt-4 border-t border-slate-800">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> 100 включенных вызовов API</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> 10.00 ₽ / вызов сверх лимита</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> Авто-прорация при апгрейде</li>
            </ul>
          </div>
          <button onclick="openModal('modal-subscribe')" class="w-full mt-6 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition">Подключить</button>
        </div>

        <!-- Plan 2 (Featured) -->
        <div class="bg-gradient-to-b from-slate-900 via-slate-900 to-emerald-950/20 border-2 border-emerald-500/50 p-6 rounded-2xl flex flex-col justify-between shadow-xl relative">
          <span class="absolute -top-3 right-6 text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500 text-slate-950 uppercase">Хит продаж</span>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono uppercase tracking-wider text-emerald-400 font-bold">Профессиональный</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">plan-pro</span>
            </div>
            <div>
              <p class="text-3xl font-extrabold text-white mono-num">4 500 ₽ <span class="text-xs font-normal text-slate-400">/ месяц</span></p>
              <p class="text-xs text-slate-400 mt-1">Оптимально для растущего бизнеса</p>
            </div>
            <ul class="text-xs text-slate-300 space-y-2.5 pt-4 border-t border-slate-800">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> 500 включенных вызовов API</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> 6.00 ₽ / вызов сверх лимита</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> Smart Dunning защита</li>
            </ul>
          </div>
          <button onclick="openModal('modal-subscribe')" class="w-full mt-6 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow transition">Подключить</button>
        </div>

        <!-- Plan 3 (Trial) -->
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between shadow-sm hover:border-slate-700 transition">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">Корпоративный</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">plan-trial</span>
            </div>
            <div>
              <p class="text-3xl font-extrabold text-white mono-num">12 000 ₽ <span class="text-xs font-normal text-slate-400">/ месяц</span></p>
              <p class="text-xs text-emerald-400 mt-1 font-semibold">14 дней бесплатный пробный период</p>
            </div>
            <ul class="text-xs text-slate-300 space-y-2.5 pt-4 border-t border-slate-800">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> 2000 включенных вызовов API</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> 4.00 ₽ / вызов сверх лимита</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> Выделенный Circuit Breaker</li>
            </ul>
          </div>
          <button onclick="openModal('modal-subscribe')" class="w-full mt-6 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition">Начать триал</button>
        </div>
      </div>
    </div>

  </div>

  <!-- ================= SLIDE-OVER DRAWER (ENTITY INSPECTOR) ================= -->
  <div id="inspector-drawer" class="fixed inset-y-0 right-0 w-full max-w-md bg-slate-925 border-l border-slate-800 shadow-2xl z-50 transform translate-x-full drawer-transition flex flex-col justify-between">
    <div>
      <div class="p-5 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h3 id="drawer-title" class="text-sm font-bold text-white">Инспектор сущности</h3>
          <p id="drawer-subtitle" class="text-xs text-slate-400 mt-0.5 font-mono">#ID</p>
        </div>
        <button onclick="closeDrawer()" class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <div class="p-6 space-y-5 text-xs text-slate-300 overflow-y-auto max-h-[calc(100vh-140px)] custom-scrollbar" id="drawer-content">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <div class="p-4 border-t border-slate-800 bg-slate-950 flex justify-end gap-3" id="drawer-footer">
      <button onclick="closeDrawer()" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition">Закрыть</button>
    </div>
  </div>

  <!-- ================= MODALS ================= -->

  <!-- Modal: Create Subscription -->
  <div id="modal-subscribe" class="fixed inset-0 modal-backdrop z-50 hidden flex items-center justify-center p-4">
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
          <input type="text" id="sub-input-customer" value="cust-client-201" class="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono focus:border-emerald-500 focus:outline-none">
        </div>
        <div>
          <label class="block text-slate-300 font-medium mb-1">Тарифный план</label>
          <select id="sub-input-plan" class="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 focus:border-emerald-500 focus:outline-none">
            <option value="plan-basic">Стартовый тариф (1500 ₽/мес, 100 ед. квоты)</option>
            <option value="plan-pro" selected>Профессиональный (4500 ₽/мес, 500 ед. квоты)</option>
            <option value="plan-trial">Корпоративный Триал (14 дней бесплатно)</option>
          </select>
        </div>
        <div>
          <label class="block text-slate-300 font-medium mb-1">Ключ идемпотентности (Idempotency Key)</label>
          <input type="text" id="sub-input-idemp" value="tx-order-001" class="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono text-[11px] focus:border-emerald-500 focus:outline-none">
          <p class="text-[10px] text-slate-500 mt-1">Гарантирует защиту от повторного списания средств при сбоях сети.</p>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
        <button onclick="closeModal('modal-subscribe')" class="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs font-medium">Отмена</button>
        <button onclick="submitSubscription()" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold shadow">Оформить</button>
      </div>
    </div>
  </div>

  <!-- Modal: Plan Upgrade with Proration -->
  <div id="modal-proration" class="fixed inset-0 modal-backdrop z-50 hidden flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl p-6 shadow-2xl space-y-5">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 class="text-base font-bold text-white">Смена тарифного плана</h3>
          <p class="text-xs text-slate-400">Пропорциональный перерасчет неизрасходованных дней (Proration)</p>
        </div>
        <button onclick="closeModal('modal-proration')" class="text-slate-400 hover:text-white">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <div class="space-y-4 text-xs">
        <div>
          <label class="block text-slate-300 font-medium mb-1">Выберите целевую подписку</label>
          <select id="proration-sub-select" onchange="updateProrationPreview()" class="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 focus:border-emerald-500 focus:outline-none font-mono">
            <!-- Populated dynamically -->
          </select>
        </div>

        <div>
          <label class="block text-slate-300 font-medium mb-1">Новый тарифный план</label>
          <select id="proration-plan-select" onchange="updateProrationPreview()" class="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 focus:border-emerald-500 focus:outline-none">
            <option value="plan-pro">Профессиональный (4 500.00 ₽)</option>
            <option value="plan-basic">Стартовый (1 500.00 ₽)</option>
            <option value="plan-trial">Корпоративный (12 000.00 ₽)</option>
          </select>
        </div>

        <!-- Tremor Interactive Proration Math Breakdown Card -->
        <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2.5">
          <div class="flex items-center justify-between text-slate-400">
            <span>Неизрасходованный кредит старого тарифа:</span>
            <span class="font-mono text-emerald-400 font-semibold" id="proration-credit-val">- 750.00 ₽</span>
          </div>
          <div class="flex items-center justify-between text-slate-400">
            <span>Стоимость нового тарифа на остаток периода:</span>
            <span class="font-mono text-slate-200" id="proration-new-cost">+ 2 250.00 ₽</span>
          </div>
          <div class="pt-2 border-t border-slate-800 flex items-center justify-between text-white font-bold text-sm">
            <span>Итого к доплате прямо сейчас:</span>
            <span class="font-mono text-emerald-400 text-base" id="proration-net-due">1 500.00 ₽</span>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
        <button onclick="closeModal('modal-proration')" class="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs font-medium">Отмена</button>
        <button onclick="submitPlanChange()" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold shadow">Подтвердить перерасчет</button>
      </div>
    </div>
  </div>

  <!-- Modal: Shadcn Command Palette (Ctrl + K) -->
  <div id="modal-command" class="fixed inset-0 modal-backdrop z-50 hidden flex items-start justify-center pt-20 p-4" onclick="handleCommandBackdrop(event)">
    <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden space-y-2" onclick="event.stopPropagation()">
      <div class="p-3 border-b border-slate-800 flex items-center gap-3">
        <i data-lucide="search" class="w-4 h-4 text-emerald-400 ml-2"></i>
        <input type="text" id="command-search-input" placeholder="Поиск окон, действий или клиентов..." class="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none font-sans" oninput="filterCommandList(this.value)">
        <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">ESC</span>
      </div>
      <div class="p-2 space-y-1 max-h-80 overflow-y-auto custom-scrollbar" id="command-list">
        <button onclick="openWindowTab('overview'); closeCommandPalette();" class="w-full text-left px-3 py-2 rounded-xl text-slate-200 hover:bg-slate-800 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2.5"><i data-lucide="layout-dashboard" class="w-4 h-4 text-emerald-400"></i> Сводный обзор (Overview)</span>
          <span class="text-[10px] font-mono text-slate-500">Окно 1</span>
        </button>
        <button onclick="openWindowTab('subscriptions'); closeCommandPalette();" class="w-full text-left px-3 py-2 rounded-xl text-slate-200 hover:bg-slate-800 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2.5"><i data-lucide="credit-card" class="w-4 h-4 text-teal-400"></i> Договоры подписок</span>
          <span class="text-[10px] font-mono text-slate-500">Окно 2</span>
        </button>
        <button onclick="openWindowTab('resilience'); closeCommandPalette();" class="w-full text-left px-3 py-2 rounded-xl text-slate-200 hover:bg-slate-800 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2.5"><i data-lucide="activity" class="w-4 h-4 text-rose-400"></i> Отказоустойчивость & Circuit Breaker</span>
          <span class="text-[10px] font-mono text-slate-500">Окно 4</span>
        </button>
        <button onclick="toggleSplitView(); closeCommandPalette();" class="w-full text-left px-3 py-2 rounded-xl text-slate-200 hover:bg-slate-800 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2.5"><i data-lucide="columns-2" class="w-4 h-4 text-amber-400"></i> Переключить режим Сплит-экрана</span>
          <span class="text-[10px] font-mono text-slate-500">View</span>
        </button>
        <button onclick="tripCircuitBreaker(); closeCommandPalette();" class="w-full text-left px-3 py-2 rounded-xl text-slate-200 hover:bg-slate-800 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2.5"><i data-lucide="zap-off" class="w-4 h-4 text-rose-400"></i> Имитировать сбой банка (504 Timeout)</span>
          <span class="text-[10px] font-mono text-rose-400">Chaos</span>
        </button>
        <button onclick="resetCircuitBreaker(); closeCommandPalette();" class="w-full text-left px-3 py-2 rounded-xl text-slate-200 hover:bg-slate-800 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2.5"><i data-lucide="shield-check" class="w-4 h-4 text-emerald-400"></i> Восстановить работу шлюза</span>
          <span class="text-[10px] font-mono text-emerald-400">Reset</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Toast Notification Hub -->
  <div id="toast" class="fixed bottom-6 right-6 z-50 transform translate-y-24 opacity-0 transition-all duration-300 pointer-events-none px-4 py-3 rounded-2xl bg-slate-900 border border-slate-700 text-white text-xs flex items-center gap-3 shadow-2xl">
    <i data-lucide="info" class="w-4 h-4 text-emerald-400 shrink-0" id="toast-icon"></i>
    <span id="toast-msg">Уведомление</span>
  </div>

  <!-- ================= CLIENT JAVASCRIPT WORKSPACE LOGIC ================= -->
  <script>
    // State Machine
    const state = {{
      openTabs: ['overview', 'subscriptions', 'resilience'],
      activeTab: '{initial_window}',
      splitView: false,
      secondaryTab: 'resilience',
      data: {{
        stats: null,
        subs: [],
        invoices: [],
        outbox: [],
        usage: [],
      }}
    }};

    // Window Titles & Metadata Map
    const WINDOW_CONFIG = {{
      'overview': {{ title: 'Сводный обзор системы', icon: 'layout-dashboard' }},
      'subscriptions': {{ title: 'Реестр договоров подписок', icon: 'credit-card' }},
      'invoices': {{ title: 'Финансовые счета и проводки', icon: 'receipt' }},
      'resilience': {{ title: 'Отказоустойчивость & Circuit Breaker', icon: 'activity' }},
      'usage': {{ title: 'Учет потребления и квот API', icon: 'gauge' }},
      'outbox': {{ title: 'Transactional Outbox Stream', icon: 'send' }},
      'plans': {{ title: 'Конструктор тарифных планов', icon: 'layers' }},
    }};

    // Chart.js Instances
    let chartRevenue = null;
    let chartStatus = null;

    // --- TAB MANAGEMENT (MULTI-WINDOW) ---
    function renderTabs() {{
      const container = document.getElementById('window-tabs-container');
      container.innerHTML = '';

      state.openTabs.forEach(tabId => {{
        const cfg = WINDOW_CONFIG[tabId] || {{ title: tabId, icon: 'square' }};
        const isActive = (state.activeTab === tabId);

        const tabBtn = document.createElement('div');
        tabBtn.className = `flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium cursor-pointer transition select-none ${{
          isActive 
            ? 'bg-slate-850 text-white border border-emerald-500/40 shadow-sm' 
            : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-900'
        }}`;
        tabBtn.onclick = () => selectWindowTab(tabId);

        tabBtn.innerHTML = `
          <i data-lucide="${{cfg.icon}}" class="w-3.5 h-3.5 ${{isActive ? 'text-emerald-400' : 'text-slate-400'}}"></i>
          <span>${{cfg.title.split(' ')[0]}}</span>
          ${{state.openTabs.length > 1 ? `
            <button onclick="closeWindowTab(event, '${{tabId}}')" class="p-0.5 rounded hover:bg-slate-700 text-slate-400 hover:text-white ml-1">
              <i data-lucide="x" class="w-3 h-3"></i>
            </button>
          ` : ''}}
        `;
        container.appendChild(tabBtn);
      }});

      lucide.createIcons();
    }}

    function openWindowTab(tabId) {{
      if (!state.openTabs.includes(tabId)) {{
        state.openTabs.push(tabId);
      }}
      selectWindowTab(tabId);
    }}

    function closeWindowTab(event, tabId) {{
      event.stopPropagation();
      if (state.openTabs.length <= 1) return;

      const idx = state.openTabs.indexOf(tabId);
      state.openTabs = state.openTabs.filter(t => t !== tabId);

      if (state.activeTab === tabId) {{
        const newActive = state.openTabs[Math.max(0, idx - 1)];
        selectWindowTab(newActive);
      }} else {{
        renderTabs();
      }}
    }}

    function selectWindowTab(tabId) {{
      state.activeTab = tabId;
      document.getElementById('window-title').innerText = WINDOW_CONFIG[tabId]?.title || tabId;
      
      // Update sidebar nav active style
      document.querySelectorAll('[id^="sidebar-nav-"]').forEach(btn => {{
        btn.classList.remove('bg-slate-850', 'text-white', 'border-emerald-500/30');
        btn.classList.add('text-slate-400');
      }});
      const activeNav = document.getElementById(`sidebar-nav-${{tabId}}`);
      if (activeNav) {{
        activeNav.classList.add('bg-slate-850', 'text-white', 'border-emerald-500/30');
        activeNav.classList.remove('text-slate-400');
      }}

      renderTabs();
      renderWorkspace();
    }}

    // --- SPLIT-VIEW MANAGEMENT (DUAL WINDOWS) ---
    function toggleSplitView() {{
      state.splitView = !state.splitView;
      const statusBadge = document.getElementById('badge-split-status');
      const toggleBtn = document.getElementById('btn-split-toggle');

      if (state.splitView) {{
        statusBadge.innerText = 'Вкл';
        statusBadge.className = 'text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold';
        toggleBtn.classList.add('border-emerald-500/40', 'bg-slate-850');
        showToast('Сплит-экран включен: 2 окна параллельно');
      }} else {{
        statusBadge.innerText = 'Выкл';
        statusBadge.className = 'text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700';
        toggleBtn.classList.remove('border-emerald-500/40', 'bg-slate-850');
        showToast('Сплит-экран выключен');
      }}
      renderWorkspace();
    }}

    function changeSecondaryWindow(targetTab) {{
      state.secondaryTab = targetTab;
      renderWorkspace();
    }}

    function renderWorkspace() {{
      const singleContainer = document.getElementById('single-window-viewport');
      const splitContainer = document.getElementById('split-window-viewport');
      const primarySlot = document.getElementById('primary-window-slot');
      const splitLeftSlot = document.getElementById('split-left-slot');
      const splitRightSlot = document.getElementById('split-right-slot');

      const leftTpl = document.getElementById(`template-${{state.activeTab}}`);
      const rightTpl = document.getElementById(`template-${{state.secondaryTab}}`);

      if (!state.splitView) {{
        singleContainer.classList.remove('hidden');
        splitContainer.classList.add('hidden');
        if (leftTpl) {{
          primarySlot.innerHTML = leftTpl.innerHTML;
        }}
      }} else {{
        singleContainer.classList.add('hidden');
        splitContainer.classList.remove('hidden');

        document.getElementById('split-left-title').innerText = WINDOW_CONFIG[state.activeTab]?.title || state.activeTab;
        document.getElementById('split-secondary-selector').value = state.secondaryTab;

        if (leftTpl) splitLeftSlot.innerHTML = leftTpl.innerHTML;
        if (rightTpl) splitRightSlot.innerHTML = rightTpl.innerHTML;
      }}

      lucide.createIcons();
      initTremorTracker();
      if (state.activeTab === 'overview' || (state.splitView && state.secondaryTab === 'overview')) {{
        initCharts();
      }}
      repopulateDataDOM();
    }}

    // --- TREMOR TRACKER INITIALIZATION (40 BLOCKS) ---
    function initTremorTracker() {{
      const bar = document.getElementById('tremor-tracker-bar');
      if (!bar) return;
      bar.innerHTML = '';

      const isBreakerOpen = state.data.stats?.circuit_breaker?.state === 'OPEN';

      for (let i = 0; i < 40; i++) {{
        const block = document.createElement('div');
        block.className = 'h-5 rounded-sm tracker-block cursor-pointer';

        if (isBreakerOpen && i >= 35) {{
          block.classList.add('bg-rose-500');
          block.title = `Блок #${{i+1}}: 504 Gateway Timeout (Circuit Breaker OPEN)`;
        }} else if (i === 18 || i === 29) {{
          block.classList.add('bg-amber-400');
          block.title = `Блок #${{i+1}}: Smart Dunning Retry (Задержка 120мс)`;
        }} else {{
          block.classList.add('bg-emerald-500');
          block.title = `Блок #${{i+1}}: 200 OK (Задержка ${{Math.floor(25 + Math.random() * 20)}}мс)`;
        }}
        bar.appendChild(block);
      }}
    }}

    // --- CHARTS INITIALIZATION (FINTECH STYLE) ---
    function initCharts() {{
      const revCanvas = document.getElementById('chart-revenue-mrr');
      const donutCanvas = document.getElementById('chart-status-donut');

      if (revCanvas) {{
        if (chartRevenue) chartRevenue.destroy();
        const ctxRev = revCanvas.getContext('2d');
        const gradient = ctxRev.createLinearGradient(0, 0, 0, 240);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

        chartRevenue = new Chart(ctxRev, {{
          type: 'line',
          data: {{
            labels: ['Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт (Факт)'],
            datasets: [{{
              label: 'MRR (₽)',
              data: [1500, 3000, 4500, 9000, 10500, parseFloat(state.data.stats?.total_revenue || 6000)],
              borderColor: '#10b981',
              backgroundColor: gradient,
              borderWidth: 2.5,
              tension: 0.35,
              fill: true,
              pointBackgroundColor: '#10b981',
              pointRadius: 4,
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
              x: {{ grid: {{ color: '#1e293b' }}, ticks: {{ color: '#94a3b8', font: {{ family: 'JetBrains Mono', size: 10 }} }} }},
              y: {{ grid: {{ color: '#1e293b' }}, ticks: {{ color: '#94a3b8', font: {{ family: 'JetBrains Mono', size: 10 }} }} }}
            }}
          }}
        }});
      }}

      if (donutCanvas) {{
        if (chartStatus) chartStatus.destroy();
        const ctxDonut = donutCanvas.getContext('2d');
        chartStatus = new Chart(ctxDonut, {{
          type: 'doughnut',
          data: {{
            labels: ['Active', 'Past Due', 'Canceled'],
            datasets: [{{
              data: [
                state.data.subs.filter(s => s.status === 'ACTIVE').length || 1,
                state.data.subs.filter(s => s.status === 'PAST_DUE').length || 0,
                state.data.subs.filter(s => s.status === 'CANCELED').length || 0
              ],
              backgroundColor: ['#10b981', '#f59e0b', '#64748b'],
              borderColor: '#0b0f19',
              borderWidth: 3,
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            cutout: '72%'
          }}
        }});
      }}
    }}

    // --- REAL-TIME DATA REFRESH ---
    async function refreshData() {{
      try {{
        const [statsRes, subsRes, invsRes, outboxRes, usageRes] = await Promise.all([
          fetch('/api/v1/system/stats'),
          fetch('/api/v1/system/subscriptions'),
          fetch('/api/v1/system/invoices'),
          fetch('/api/v1/system/outbox'),
          fetch('/api/v1/system/usage'),
        ]);

        state.data.stats = await statsRes.json();
        state.data.subs = await subsRes.json();
        state.data.invoices = await invsRes.json();
        state.data.outbox = await outboxRes.json();
        state.data.usage = await usageRes.json();

        updateHeaderStatus();
        repopulateDataDOM();
      }} catch (err) {{
        console.error('Data sync error:', err);
      }}
    }}

    function updateHeaderStatus() {{
      const cb = state.data.stats?.circuit_breaker;
      if (!cb) return;

      const statePill = document.getElementById('header-cb-state');
      const dot = document.getElementById('header-cb-dot');
      const card = document.getElementById('header-cb-card');

      statePill.innerText = cb.state;

      if (cb.state === 'OPEN') {{
        statePill.className = 'font-bold font-mono text-rose-400';
        dot.className = 'w-2.5 h-2.5 rounded-full bg-rose-400 animate-ping';
        card.className = 'flex items-center gap-2 px-3 py-1.5 rounded-xl border border-rose-500/40 bg-rose-950/40 text-xs shadow-lg glow-rose';
      }} else if (cb.state === 'HALF_OPEN') {{
        statePill.className = 'font-bold font-mono text-amber-400';
        dot.className = 'w-2.5 h-2.5 rounded-full bg-amber-400';
        card.className = 'flex items-center gap-2 px-3 py-1.5 rounded-xl border border-amber-500/40 bg-amber-950/40 text-xs glow-amber';
      }} else {{
        statePill.className = 'font-bold font-mono text-emerald-400';
        dot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-400';
        card.className = 'flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-900 text-xs shadow-sm';
      }}

      // Update Subscriptions Badge in sidebar
      const badgeSubs = document.getElementById('nav-badge-subs');
      if (badgeSubs) badgeSubs.innerText = state.data.subs.length;

      const badgeInvs = document.getElementById('nav-badge-invs');
      if (badgeInvs) badgeInvs.innerText = state.data.invoices.length;
    }}

    function repopulateDataDOM() {{
      const {{ stats, subs, invoices, outbox, usage }} = state.data;
      if (!stats) return;

      // Update KPI Cards
      const kpiRev = document.getElementById('kpi-revenue');
      if (kpiRev) kpiRev.innerText = `${{Number(stats.total_revenue).toLocaleString('ru-RU', {{ minimumFractionDigits: 2 }})}} ₽`;

      const kpiSubs = document.getElementById('kpi-subscriptions');
      if (kpiSubs) kpiSubs.innerText = subs.length;

      const kpiInvs = document.getElementById('kpi-invoices');
      if (kpiInvs) kpiInvs.innerText = invoices.length;

      // Update Donut numbers
      const dActive = document.getElementById('donut-active-cnt');
      if (dActive) dActive.innerText = subs.filter(s => s.status === 'ACTIVE').length;
      const dPastDue = document.getElementById('donut-pastdue-cnt');
      if (dPastDue) dPastDue.innerText = subs.filter(s => s.status === 'PAST_DUE').length;
      const dCancel = document.getElementById('donut-canceled-cnt');
      if (dCancel) dCancel.innerText = subs.filter(s => s.status === 'CANCELED').length;

      // Tremor BarList: Top Clients
      const barlist = document.getElementById('tremor-barlist-container');
      if (barlist) {{
        barlist.innerHTML = subs.map(s => `
          <div class="space-y-1">
            <div class="flex items-center justify-between text-xs">
              <span class="font-mono text-slate-200 font-medium">${{s.customer_id}}</span>
              <span class="font-mono font-bold text-emerald-400">${{s.plan_name}}</span>
            </div>
            <div class="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
              <div class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full" style="width: ${{s.status === 'ACTIVE' ? '85%' : '40%'}}"></div>
            </div>
          </div>
        `).join('') || '<p class="text-xs text-slate-500">Нет данных о клиентах</p>';
      }}

      // Repopulate Subscriptions Table
      const subsBody = document.getElementById('subs-table-body');
      if (subsBody) {{
        if (subs.length === 0) {{
          subsBody.innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-slate-500">Договоров подписок не найдено. Нажмите "Оформить договор"</td></tr>';
        }} else {{
          subsBody.innerHTML = subs.map(s => `
            <tr class="hover:bg-slate-850/60 transition">
              <td class="px-5 py-3 font-mono font-medium text-white flex items-center gap-2">
                <div class="w-6 h-6 rounded-md bg-teal-500/10 text-teal-400 flex items-center justify-center text-[10px]">#</div>
                <span>${{s.customer_id}}</span>
              </td>
              <td class="px-5 py-3">${{s.plan_name}}</td>
              <td class="px-5 py-3">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${{
                  s.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                  s.status === 'PAST_DUE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                  s.status === 'TRIALING' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' :
                  'bg-slate-800 text-slate-400'
                }}">${{s.status}}</span>
              </td>
              <td class="px-5 py-3 font-mono text-slate-400">${{s.current_period_end.substring(0, 10)}}</td>
              <td class="px-5 py-3 font-mono ${{s.retry_count > 0 ? 'text-amber-400 font-bold' : 'text-slate-500'}}">${{s.retry_count}}</td>
              <td class="px-5 py-3 text-right">
                <button onclick="inspectEntity('subscription', '${{s.id}}')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium transition">
                  Инспектор
                </button>
              </td>
            </tr>
          `).join('');
        }}
      }}

      // Repopulate Invoices Table
      const invBody = document.getElementById('invoices-table-body');
      if (invBody) {{
        if (invoices.length === 0) {{
          invBody.innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-slate-500 font-sans">Счета отсутствуют</td></tr>';
        }} else {{
          invBody.innerHTML = invoices.map(inv => `
            <tr class="hover:bg-slate-850/60 transition">
              <td class="px-5 py-3 font-mono text-slate-400">${{inv.id.substring(0, 13)}}...</td>
              <td class="px-5 py-3 font-medium text-white">${{inv.customer_id}}</td>
              <td class="px-5 py-3">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${{
                  inv.status === 'PAID' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                  inv.status === 'FAILED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                  'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }}">${{inv.status}}</span>
              </td>
              <td class="px-5 py-3 font-bold text-white font-mono">${{inv.total_amount}} ${{inv.currency}}</td>
              <td class="px-5 py-3 text-slate-400 font-sans truncate max-w-xs">${{inv.items_summary}}</td>
              <td class="px-5 py-3 text-right text-slate-500">${{inv.created_at.substring(0, 10)}}</td>
            </tr>
          `).join('');
        }}
      }}

      // Repopulate Outbox Table
      const outboxBody = document.getElementById('outbox-table-body');
      if (outboxBody) {{
        if (outbox.length === 0) {{
          outboxBody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Журнал Transactional Outbox пуст</td></tr>';
        }} else {{
          outboxBody.innerHTML = outbox.map(e => `
            <tr class="hover:bg-slate-850/60 transition">
              <td class="px-5 py-3 text-slate-400">${{e.event_id.substring(0, 12)}}...</td>
              <td class="px-5 py-3 font-semibold text-emerald-300 font-mono">${{e.event_type}}</td>
              <td class="px-5 py-3 text-slate-300">${{e.tenant_id}}</td>
              <td class="px-5 py-3 text-slate-400">${{e.occurred_at.substring(0, 19).replace('T', ' ')}}</td>
              <td class="px-5 py-3 text-right">
                <span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px]">COMMITTED</span>
              </td>
            </tr>
          `).join('');
        }}
      }}

      // Repopulate Usage & Quotas Window
      const quotasGrid = document.getElementById('usage-quotas-grid');
      if (quotasGrid) {{
        quotasGrid.innerHTML = subs.map(s => {{
          const isBasic = s.plan_id.includes('basic');
          const limit = isBasic ? 100 : 500;
          const currentUsage = isBasic ? 65 : 380;
          const pct = Math.min(100, Math.round((currentUsage / limit) * 100));

          return `
            <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-3">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="text-xs font-bold text-white font-mono">${{s.customer_id}}</h4>
                  <p class="text-[10px] text-slate-400">${{s.plan_name}} (Лимит: ${{limit}} вызовов)</p>
                </div>
                <span class="text-xs font-mono font-bold ${{pct > 80 ? 'text-amber-400' : 'text-emerald-400'}}">${{currentUsage}} / ${{limit}} ед.</span>
              </div>
              <div class="w-full h-3 rounded-full bg-slate-950 p-0.5 border border-slate-800">
                <div class="h-full rounded-full ${{pct > 80 ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-gradient-to-r from-emerald-500 to-teal-400'}}" style="width: ${{pct}}%"></div>
              </div>
              <div class="flex items-center justify-between text-[10px] font-mono text-slate-500">
                <span>Использование квоты: ${{pct}}%</span>
                <span>Статус: ${{pct >= 100 ? 'Перерасход (Overage)' : 'В пределах тарифа'}}</span>
              </div>
            </div>
          `;
        }}).join('');
      }}

      const usageTableBody = document.getElementById('usage-table-body');
      if (usageTableBody) {{
        if (usage.length === 0) {{
          usageTableBody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-slate-500 font-sans">Нет записей потребления API</td></tr>';
        }} else {{
          usageTableBody.innerHTML = usage.map(u => `
            <tr class="hover:bg-slate-850/60 transition">
              <td class="px-5 py-3 text-slate-400">${{u.id.substring(0, 10)}}...</td>
              <td class="px-5 py-3 text-white font-medium">${{u.customer_id}}</td>
              <td class="px-5 py-3 text-slate-400">${{u.subscription_id.substring(0, 12)}}...</td>
              <td class="px-5 py-3 font-bold text-cyan-400">+${{u.units}} API units</td>
              <td class="px-5 py-3 text-right text-slate-500">${{u.recorded_at.substring(0, 19).replace('T', ' ')}}</td>
            </tr>
          `).join('');
        }}
      }}

      // Repopulate Resilience State Card in Window 4
      const resCard = document.getElementById('resilience-state-card');
      const resText = document.getElementById('resilience-state-text');
      const resFail = document.getElementById('resilience-failure-count');
      const resCallout = document.getElementById('resilience-callout');

      if (resCard && resText && stats.circuit_breaker) {{
        const cb = stats.circuit_breaker;
        resText.innerText = cb.state;
        resFail.innerText = `${{cb.failure_count}} / ${{cb.threshold}} сбоев`;

        if (cb.state === 'OPEN') {{
          resText.className = 'text-2xl font-black font-mono text-rose-400';
          resCard.className = 'flex flex-col items-center justify-center p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 min-w-[200px] glow-rose';
          if (resCallout) {{
            resCallout.className = 'p-4 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-xs text-rose-300 flex items-start gap-3';
            resCallout.innerHTML = `
              <i data-lucide="alert-octagon" class="w-5 h-5 text-rose-400 shrink-0 mt-0.5"></i>
              <div>
                <span class="font-bold block">Предохранитель РАЗОМКНУТ (OPEN)!</span>
                <span class="text-slate-300 text-[11px]">Платежный шлюз банка в даунтайме. Запросы блокируются на входе для предотвращения зависания сервиса. Запущен таймер восстановления.</span>
              </div>
            `;
            lucide.createIcons();
          }}
        }} else {{
          resText.className = 'text-2xl font-black font-mono text-emerald-400';
          resCard.className = 'flex flex-col items-center justify-center p-4 rounded-xl bg-slate-950 border border-slate-800 min-w-[200px]';
        }}
      }}

      // Repopulate Proration modal select
      const proSelect = document.getElementById('proration-sub-select');
      if (proSelect && subs.length > 0 && proSelect.options.length === 0) {{
        proSelect.innerHTML = subs.map(s => `<option value="${{s.id}}">${{s.customer_id}} (${{s.plan_name}})</option>`).join('');
        updateProrationPreview();
      }}
    }}

    // --- ACTIONS & API CALLS ---
    async function tripCircuitBreaker() {{
      const res = await fetch('/api/v1/system/circuit-breaker/trip', {{ method: 'POST' }});
      if (res.ok) {{
        showToast('Circuit Breaker переведен в OPEN (Банк эмулирует 504 Timeout)!', true);
        refreshData();
      }}
    }}

    async function resetCircuitBreaker() {{
      const res = await fetch('/api/v1/system/circuit-breaker/reset', {{ method: 'POST' }});
      if (res.ok) {{
        showToast('Circuit Breaker сброшен в CLOSED (Связь с банком восстановлена)');
        refreshData();
      }}
    }}

    async function submitSubscription() {{
      const customer = document.getElementById('sub-input-customer').value;
      const plan = document.getElementById('sub-input-plan').value;
      const idemp = document.getElementById('sub-input-idemp').value;

      const res = await fetch('/api/v1/subscriptions', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          tenant_id: 'tenant-demo',
          customer_id: customer,
          plan_id: plan,
          payment_method_id: 'card-live-token',
          idempotency_key: idemp
        }})
      }});

      if (res.ok) {{
        showToast(`Подписка для ${{customer}} успешно создана!`);
        closeModal('modal-subscribe');
        refreshData();
      }} else {{
        showToast('Ошибка при оформлении договора', true);
      }}
    }}

    async function submitPlanChange() {{
      const subId = document.getElementById('proration-sub-select').value;
      const newPlan = document.getElementById('proration-plan-select').value;

      const res = await fetch(`/api/v1/subscriptions/${{subId}}/change-plan`, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          new_plan_id: newPlan,
          idempotency_key: 'proration-tx-' + Date.now()
        }})
      }});

      if (res.ok) {{
        showToast('Тариф успешно изменен с точным перерасчетом (Proration)!');
        closeModal('modal-proration');
        refreshData();
      }} else {{
        showToast('Ошибка при перерасчете тарифа', true);
      }}
    }}

    async function quickRecordUsage() {{
      const subs = state.data.subs;
      if (!subs || subs.length === 0) {{
        showToast('Сначала создайте подписку', true);
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

    function updateProrationPreview() {{
      const planVal = document.getElementById('proration-plan-select')?.value;
      const creditEl = document.getElementById('proration-credit-val');
      const costEl = document.getElementById('proration-new-cost');
      const netEl = document.getElementById('proration-net-due');

      if (planVal === 'plan-pro') {{
        creditEl.innerText = '- 750.00 ₽';
        costEl.innerText = '+ 2 250.00 ₽';
        netEl.innerText = '1 500.00 ₽';
      }} else if (planVal === 'plan-trial') {{
        creditEl.innerText = '- 750.00 ₽';
        costEl.innerText = '+ 6 000.00 ₽';
        netEl.innerText = '5 250.00 ₽';
      }} else {{
        creditEl.innerText = '- 2 250.00 ₽';
        costEl.innerText = '+ 750.00 ₽';
        netEl.innerText = '0.00 ₽';
      }}
    }}

    // --- DRAWER INSPECTOR ---
    function inspectEntity(type, id) {{
      const drawer = document.getElementById('inspector-drawer');
      const title = document.getElementById('drawer-title');
      const sub = document.getElementById('drawer-subtitle');
      const content = document.getElementById('drawer-content');

      const item = state.data.subs.find(s => s.id === id) || state.data.invoices.find(i => i.id === id);
      if (!item) return;

      title.innerText = type === 'subscription' ? 'Договор подписки' : 'Инвойс начисления';
      sub.innerText = `#${{id}}`;

      content.innerHTML = `
        <div class="space-y-4 font-mono text-xs">
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="text-slate-500 text-[10px]">КЛИЕНТ:</span>
            <p class="text-emerald-400 font-bold">${{item.customer_id}}</p>
          </div>
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="text-slate-500 text-[10px]">СТАТУС ДОМЕННОЙ МОДЕЛИ:</span>
            <p class="text-white font-bold">${{item.status}}</p>
          </div>
          <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <span class="text-slate-500 text-[10px]">СЫРОЙ СЛЕПОК (JSON DTO):</span>
            <pre class="text-[11px] text-slate-300 overflow-x-auto p-2 bg-slate-900 rounded-lg custom-scrollbar">${{JSON.stringify(item, null, 2)}}</pre>
          </div>
        </div>
      `;
      drawer.classList.remove('translate-x-full');
    }}

    function closeDrawer() {{
      document.getElementById('inspector-drawer').classList.add('translate-x-full');
    }}

    // --- MODALS & COMMAND PALETTE ---
    function openModal(id) {{
      document.getElementById(id).classList.remove('hidden');
    }}

    function closeModal(id) {{
      document.getElementById(id).classList.add('hidden');
    }}

    function openCommandPalette() {{
      document.getElementById('modal-command').classList.remove('hidden');
      document.getElementById('command-search-input').focus();
    }}

    function closeCommandPalette() {{
      document.getElementById('modal-command').classList.add('hidden');
    }}

    function handleCommandBackdrop(e) {{
      closeCommandPalette();
    }}

    function toggleNewWindowMenu() {{
      const el = document.getElementById('dropdown-new-window');
      el.classList.toggle('hidden');
    }}

    function toggleMobileSidebar() {{
      document.querySelector('aside').classList.toggle('hidden');
    }}

    function showToast(msg, isError = false) {{
      const t = document.getElementById('toast');
      const text = document.getElementById('toast-msg');
      const icon = document.getElementById('toast-icon');

      text.innerText = msg;
      icon.className = isError ? 'w-4 h-4 text-rose-400 shrink-0' : 'w-4 h-4 text-emerald-400 shrink-0';
      t.className = isError 
        ? 'fixed bottom-6 right-6 z-50 transition-all duration-300 px-4 py-3 rounded-2xl bg-slate-900 border border-rose-500/50 text-white text-xs flex items-center gap-3 shadow-2xl'
        : 'fixed bottom-6 right-6 z-50 transition-all duration-300 px-4 py-3 rounded-2xl bg-slate-900 border border-emerald-500/50 text-white text-xs flex items-center gap-3 shadow-2xl';

      t.classList.remove('translate-y-24', 'opacity-0', 'pointer-events-none');
      setTimeout(() => {{
        t.classList.add('translate-y-24', 'opacity-0', 'pointer-events-none');
      }}, 3200);
    }}

    // Keyboard Shortcuts (Ctrl+K, ESC)
    window.addEventListener('keydown', (e) => {{
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
        e.preventDefault();
        openCommandPalette();
      }}
      if (e.key === 'Escape') {{
        closeCommandPalette();
        closeDrawer();
        document.querySelectorAll('[id^="modal-"]').forEach(m => m.classList.add('hidden'));
      }}
    }});

    // Bootstrapping
    window.addEventListener('DOMContentLoaded', () => {{
      renderTabs();
      renderWorkspace();
      refreshData();
      setInterval(refreshData, 3500);
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


@router.get("/dashboard/usage", response_class=HTMLResponse)
def get_dashboard_usage() -> HTMLResponse:
    """Renders the dedicated Usage & Quotas metering window."""
    return HTMLResponse(content=build_dashboard_html("usage"))
