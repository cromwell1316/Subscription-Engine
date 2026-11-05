# Multi-Tenant Billing and Subscription Platform (Subscription Engine)

Проект по дисциплине «Проектная практика» (ПП).  
Архитектурно строгое решение для мультитенантной тарификации, управления жизненным циклом подписок и учета потребляемых ресурсов, спроектированное по канонам **Clean Architecture (Чистая архитектура)**.

---

## 📚 Проектная документация (Этапы 1–3)

1. [Первичное исследование и обоснование ценности (Value & Market Research)](file:///C:/Users/Oliver/_Personal/_University/_PP/docs/01_research_and_value.md)
   * Анализ существующих решений (Stripe Billing, Chargebee, Paddle).
   * Обоснование ценности для независимых контуров.
   * Каталог пользовательских историй (User Stories) с критериями приемки.
2. [Спецификация требований и вилка сложности (FR / NFR / Scope)](file:///C:/Users/Oliver/_Personal/_University/_PP/docs/02_requirements_and_scope.md)
   * Функциональные требования: изоляция арендаторов, тарифные сетки, жизненный цикл, идемпотентность, учет потребления.
   * Нефункциональные требования: отказоустойчивость, RTO/RPO, задержки, неизменяемый журнал начислений.
   * Границы проекта: что входит в реализацию, а что осознанно исключено.
3. [Календарный график разработки и диаграмма Ганта](file:///C:/Users/Oliver/_Personal/_University/_PP/docs/03_project_schedule_gantt.md)
   * Разбивка на 6 спринтов (по 2 недели).
   * Оценка в Story Points и критерии готовности (Definition of Done).

---

## 🏛️ Архитектура системы (Clean Architecture)

Структура исходного кода строго разделена по слоям независимости:

```
src/billing/
├── domain/                  # Ядро предметной области (чистый Python, без фреймворков и БД)
│   ├── exceptions.py        # Исключения предметной области
│   ├── value_objects.py     # Value Objects: Money, Currency, IdempotencyKey, BillingPeriod, ProrationResult
│   └── entities.py          # Сущности: Tenant, Plan, Subscription, Invoice, UsageRecord
├── application/             # Прикладной слой (сценарии использования и порты)
│   ├── ports/               # Абстрактные контракты (интерфейсы)
│   │   ├── repositories.py  # ITenantRepository, IPlanRepository, ISubscriptionRepository, IInvoiceRepository, IUsageRepository
│   │   ├── payment_gateway.py # IPaymentGateway (контракт шлюза оплаты)
│   │   └── clock.py         # IClock (интерфейс времени для детерминированного тестирования)
│   └── use_cases/           # Интеракторы бизнес-процессов
│       ├── subscribe_customer.py # Оформление подписки (триал / немедленная оплата + идемпотентность)
│       ├── change_plan.py   # Смена тарифа с пропорциональным перерасчетом (Proration)
│       ├── record_usage.py  # Регистрация потребления ресурсов
│       └── run_billing_cycle.py # Фоновый цикл биллинга, перерасход квот и обработка сбоев
└── infrastructure/          # Адаптеры внешних систем
    ├── persistence/         # Репозитории хранения данных (InMemory / SQL)
    └── gateways/            # Эмуляторы шлюзов со сценариями сбоев, таймаутов и проверкой идемпотентности
└── presentation/            # Слой представления (API интерфейс)
    └── api/                 # FastAPI приложение, Pydantic схемы, маршрутизаторы
```

---

## 🌐 Запуск REST API сервера

```powershell
$env:PYTHONPATH="src"
uvicorn billing.presentation.api.main:app --reload --port 8000
```

Интерактивная документация Swagger UI доступна по адресу:  
`http://localhost:8000/docs`

---

## 🚀 Запуск тестирования

Модульные и интеграционные тесты API выполняются через `pytest`:

```powershell
$env:PYTHONPATH="src"
python -m pytest tests -v
```
