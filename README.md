# Multi-Tenant Billing and Subscription Platform (Subscription Engine)

Проект по дисциплине «Проектная практика» (ПП).  
Архитектурно строгое решение для мультитенантной тарификации, управления жизненным циклом подписок и учета потребляемых ресурсов, спроектированное по канонам **Clean Architecture (Чистая архитектура)** с доказательством масштабирования и отказоустойчивости.

---

## 📚 Проектная документация и артефакты управления (PM)

### Документы требований и исследования:
1. [**Первичное исследование и обоснование ценности (Value Discovery)**](file:///C:/Users/Oliver/_Personal/_University/_PP/docs/01_research_and_value.md)
   * Анализ существующих решений (Stripe Billing, Chargebee, Paddle).
   * Обоснование ценности продукта для независимого корпоративного контура.
   * Каталог пользовательских историй (User Stories) с критериями приемки.
2. [**Спецификация требований и вилка сложности (FR / NFR / Scope)**](file:///C:/Users/Oliver/_Personal/_University/_PP/docs/02_requirements_and_scope.md)
   * Функциональные требования: изоляция арендаторов, тарифные сетки, жизненный цикл, идемпотентность, учет потребления.
   * Нефункциональные требования: отказоустойчивость, финансовая целостность ($RPO = 0$), задержки $< 200$ мс, append-only журнал.
   * Границы проекта: что входит в реализацию, а что осознанно исключено.
3. [**Календарный график разработки и диаграмма Ганта**](file:///C:/Users/Oliver/_Personal/_University/_PP/docs/03_project_schedule_gantt.md)
   * Разбивка на 6 спринтов (по 2 недели).
   * Оценка в Story Points и критерии готовности (Definition of Done).

### Менеджерские артефакты (Obsidian & Agile):
* [**Канбан-доска проекта (Obsidian Kanban)**](file:///C:/Users/Oliver/_Personal/_University/_PP/pm/kanban.md) — доска задач с декомпозицией по спринтам, сторипоинтами и тегами (`#backend`, `#resilience`, `#pm`, `#qa`).
* [**Отчет по Спринту 1**](file:///C:/Users/Oliver/_Personal/_University/_PP/pm/sprints/sprint_01_report.md) — ресерч, спецификация требований, согласование рамок.
* [**Отчет по Спринту 2**](file:///C:/Users/Oliver/_Personal/_University/_PP/pm/sprints/sprint_02_report.md) — доменное ядро, Clean Architecture, REST API, Proration.
* [**Заметки встреч с заказчиком**](file:///C:/Users/Oliver/_Personal/_University/_PP/pm/meetings/2026-09-18_client_sync.md) — фидбек Камиля Раисовича по вилке сложности и защите Спринта 1.

---

## 🏛️ Архитектура системы (Clean Architecture)

Структура исходного кода строго разделена по слоям независимости:

```
src/billing/
├── domain/                  # Ядро предметной области (чистый Python, без внешних фреймворков и ORM)
│   ├── exceptions.py        # Исключения предметной области
│   ├── value_objects.py     # Value Objects: Money, Currency, IdempotencyKey, BillingPeriod, ProrationResult
│   ├── events.py            # Доменные события (SubscriptionActivated, PaymentFailed, PlanUpgraded)
│   └── entities.py          # Сущности: Tenant, Plan, Subscription, Invoice, UsageRecord
├── application/             # Прикладной слой (сценарии использования и абстрактные порты)
│   ├── ports/               # Абстрактные интерфейсы
│   │   ├── repositories.py  # ITenantRepository, IPlanRepository, ISubscriptionRepository, IInvoiceRepository, IUsageRepository
│   │   ├── payment_gateway.py # IPaymentGateway (контракт шлюза оплаты с признаком is_transient)
│   │   ├── outbox.py        # IOutboxRepository (контракт Transactional Outbox)
│   │   └── clock.py         # IClock (детерминированное управление временем)
│   └── use_cases/           # Интеракторы бизнес-процессов
│       ├── subscribe_customer.py # Оформление подписки (триал / немедленная оплата + идемпотентность)
│       ├── change_plan.py   # Смена тарифа с математическим перерасчетом (Proration)
│       ├── record_usage.py  # Потоковая регистрация потребления ресурсов
│       └── run_billing_cycle.py # Фоновый биллинг, перерасход квот и обработка сбоев
├── infrastructure/          # Адаптеры внешних систем
│   ├── persistence/
│   │   ├── in_memory_repositories.py # Быстрые In-Memory хранилища для тестов
│   │   └── sql/             # SQLAlchemy 2.0 (SQLite / PostgreSQL)
│   │       ├── models.py    # Реляционные схемы таблиц
│   │       ├── database.py  # Подключение к БД и инициализация
│   │       ├── unit_of_work.py # Паттерн Unit of Work для атомарности транзакций
│   │       └── repositories.py # SQLAlchemy реализации репозиториев
│   ├── resilience/          # Паттерны отказоустойчивости
│   │   ├── circuit_breaker.py # Circuit Breaker (Closed, Open, Half-Open) для изоляции падений банков
│   │   └── dunning.py       # Smart Dunning с экспоненциальным бэкоффом и случайным джиттером
│   └── gateways/            # Эмуляторы шлюзов со сценариями сбоев, таймаутов и проверкой идемпотентности
└── presentation/            # Слой представления
    ├── api/                 # FastAPI REST API, Pydantic схемы, контроллеры
    └── cli/                 # Интерактивный терминальный демонстратор и симулятор хаоса (Chaos Runner)
```

---

## ⚡ Паттерны надежности и доказательство NFR

1. **Идемпотентность**: повторные сетевые вызовы с одинаковым `Idempotency-Key` возвращают исходный результат без повторного списания средств.
2. **Circuit Breaker**: при серии сетевых сбоев платежного шлюза (например, 504 Gateway Timeout) система мгновенно размыкает цепь (`OPEN`), предотвращая каскадные падения и лавину запросов к банку, а затем плавно восстанавливается через `HALF_OPEN`.
3. **Transactional Outbox**: доменные события сохраняются в таблицу `outbox_messages` внутри той же транзакции, что и счета, гарантируя доставку сообщений во внешние шины (Zero Data Loss).
4. **Unit of Work**: атомарный коммит финансовых записей с автоматическим откатом (`rollback`) при любых непредвиденных ошибках.

---

## 🚀 Запуск и интерактивная демонстрация

### 1. Запуск интерактивного симулятора хаоса (CLI Demo Runner):
Демонстрирует весь семестровый объем возможностей за 10 секунд (подписка, перерасчет тарифа, падение шлюза, срабатывание предохранителя, восстановление и итоговая финансовая ведомость):
```powershell
$env:PYTHONPATH="src"
python src/billing/presentation/cli/demo_runner.py
```

### 2. Запуск REST API сервера:
```powershell
$env:PYTHONPATH="src"
uvicorn billing.presentation.api.main:app --reload --port 8000
```
Интерактивная спецификация Swagger UI: `http://localhost:8000/docs`

### 3. Запуск полного набора тестов:
```powershell
$env:PYTHONPATH="src"
python -m pytest tests -v
```

---

## 🐳 Развертывание в Docker

Запуск сервиса в связке с PostgreSQL 16:
```powershell
docker-compose up --build
```
