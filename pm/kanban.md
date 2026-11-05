---
kanban-plugin: basic
---

## Бэклог (Backlog)

- [ ] Интеграция с реальным банковским шлюзом через адаптер T-Bank / Сбербанк [sp: 8] #backend #integrations
- [ ] Механизм автоматической выгрузки фискальных чеков (54-ФЗ) [sp: 5] #billing #compliance
- [ ] Поддержка динамических мультивалютных курсов через ЦБ РФ API [sp: 3] #domain #currency
- [ ] Дашборд метрик на Grafana: MRR, Churn Rate, LTV, Gateway Latency [sp: 8] #devops #observability
- [ ] Реализация распределенного кэширования политик доступа через Redis [sp: 5] #perf #redis

## Спринт 3: Персистентность и отказоустойчивость (Sprint 3)

- [ ] Перенос хранилища из InMemory в SQLAlchemy 2.0 (SQLite / PostgreSQL) [sp: 8] #backend #db
- [ ] Паттерн Unit of Work для атомарности финансовых транзакций [sp: 5] #architecture #patterns
- [ ] Реализация паттерна Circuit Breaker для изоляции сбоев платежного шлюза [sp: 5] #resilience #patterns
- [ ] Transactional Outbox для надежной публикации доменных событий [sp: 8] #resilience #events
- [ ] Интерактивный CLI симулятор пиковых нагрузок и сбоев банка [sp: 5] #demo #cli
- [ ] Dockerfile и docker-compose манифесты для локального запуска [sp: 3] #devops #docker

## В работе (In Progress)

- [ ] Реализация SQLAlchemy моделей и маппинга сущностей [sp: 5] #backend #db
- [ ] Circuit Breaker: состояния Closed, Open, Half-Open с таймаутом восстановления [sp: 5] #resilience

## Ревью и тестирование (Review / QA)

- [ ] Валидация идемпотентности повторных списаний в REST API [sp: 3] #qa #tests
- [ ] Тестирование математической корректности перерасчета (Proration) при переходе между тарифами [sp: 5] #domain #math

## Выполнено (Done)

- [x] Анализ аналогов (Stripe, Chargebee, Paddle) и ценности продукта [sp: 8] #pm #research
- [x] Составление каталога User Stories с критериями приемки [sp: 5] #pm #docs
- [x] Спецификация функциональных и нефункциональных требований (FR/NFR) [sp: 8] #architecture #docs
- [x] Диаграмма Ганта и план спринтов на семестр [sp: 5] #pm #planning
- [x] Проектирование слоя Domain (сущности, value objects, инварианты) [sp: 13] #domain #clean-architecture
- [x] Прикладной слой: сценарии оформления подписки, триала и смены тарифа [sp: 8] #usecases
- [x] Фоновый цикл регулярного биллинга и учет метрик перерасхода (Usage-based) [sp: 8] #billing
- [x] Эмулятор шлюза с эмуляцией сбоев и идемпотентности [sp: 5] #resilience
- [x] Полноценный REST API на FastAPI со Swagger документацией [sp: 8] #api #fastapi
- [x] Набор модульных и интеграционных тестов с нулевыми внешними зависимостями [sp: 5] #tests
