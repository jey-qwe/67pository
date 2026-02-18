# Memory Seeding Guide

## Overview

The `seed.py` script populates Trinity Context Core with initial context cards about your identity, tech stack, architecture, and coding rules.

## Context Cards Included

### 1. **Identity**
- **Content**: Пользователь: Архитектор (Underdog), 15 лет, из Семея. Цель: Фукуока и глобальная экспансия через AI.
- **Tags**: identity, user, goals, fukuoka, ai-expansion
- **Importance**: 10/10

### 2. **Tech Stack**
- **Content**: Технический стек: Python (FastAPI), Rust (для скорости), Qdrant (память), Gemini Pro (мозг). IDE: Antigravity.
- **Tags**: stack, python, rust, qdrant, gemini, antigravity
- **Importance**: 9/10

### 3. **Trinity Architecture**
- **Content**: Архитектура системы: Haq AI (Судья/Истина), Liar's Requiem (Память/Контекст), Mahoraga (Адаптация/Код).
- **Tags**: architecture, trinity, haq, liars-requiem, mahoraga
- **Importance**: 10/10

### 4. **Coding Rules**
- **Content**: Правила кодинга: Clean Architecture, SOLID, никаких костылей без пометки TODO, приоритет скорости.
- **Tags**: coding-rules, clean-architecture, solid, speed
- **Importance**: 9/10

### 5. **Mission Statement**
- **Content**: Миссия Trinity: Создать самую быструю и умную AI-систему для автономной разработки. От Семея до мира.
- **Tags**: mission, vision, autonomous-ai, speed
- **Importance**: 10/10

### 6. **Development Philosophy**
- **Content**: Философия: Скорость важнее идеальности. Итерация важнее планирования. Действие важнее размышлений. Ship fast, iterate faster.
- **Tags**: philosophy, mindset, speed, iteration
- **Importance**: 8/10

## Usage

### Prerequisites
1. **Install httpx** (if not already installed):
   ```bash
   pip install httpx
   ```

2. **Start the FastAPI server**:
   ```bash
   python src/main.py
   ```
   Server should be running on http://127.0.0.1:8000

3. **(Optional) Start Qdrant with Docker** for full functionality:
   ```bash
   docker-compose up -d
   ```

### Running the Seed Script

From project root:

```bash
python src/scripts/seed.py
```

### Expected Output

```
============================================================
Trinity Context Core - Memory Seeding
============================================================

Загрузка 6 контекстных карт...

[SUCCESS] Загружено: Identity
[SUCCESS] Загружено: Tech Stack
[SUCCESS] Загружено: Trinity Architecture
[SUCCESS] Загружено: Coding Rules
[SUCCESS] Загружено: Mission Statement
[SUCCESS] Загружено: Development Philosophy

[COMPLETE] Загружено 6/6 карт

============================================================
ПРОВЕРКА: Поиск в памяти
============================================================

Запрос: 'Куда мы идем?'

[SUCCESS] Найдено 3 релевантных карт:

1. Пользователь: Архитектор (Underdog), 15 лет, из Семея. Цель: Фукуока и глобальная экспансия через ...
   Теги: ['identity', 'user', 'goals', 'fukuoka', 'ai-expansion']
   Важность: 10/10

2. Миссия Trinity: Создать самую быструю и умную AI-систему для автономной разработки. От Семея до мир...
   Теги: ['mission', 'vision', 'autonomous-ai', 'speed']
   Важность: 10/10

3. Философия: Скорость важнее идеальности. Итерация важнее планирования. Действие важнее размышлений. ...
   Теги: ['philosophy', 'mindset', 'speed', 'iteration']
   Важность: 8/10

============================================================
Seeding завершен!
============================================================
```

## Verification

The script automatically performs a search with query **"Куда мы идем?"** (Where are we going?) to verify that the system understands your goals and mission.

## Customization

To add more context cards, edit `src/scripts/seed.py` and add entries to the `CONTEXT_CARDS` list:

```python
{
    "name": "Card Name",
    "content": "Your content here",
    "tags": ["tag1", "tag2"],
    "source": "user",  # or "system"
    "importance": 8    # 1-10
}
```

## Troubleshooting

### Error: Connection refused
**Problem**: FastAPI server is not running

**Solution**:
```bash
python src/main.py
```

### Error: Search returns no results
**Problem**: Docker Qdrant not running (in-memory mode limitations)

**Solution**:
```bash
docker-compose up -d
python src/scripts/seed.py
```

### Cards added but search verification fails
**Problem**: In-memory Qdrant doesn't support search

**Solution**: This is expected. Start Docker Qdrant for full search functionality.

## API Endpoints Used

- **POST** `/api/v1/memory/add` - Adds each context card
- **POST** `/api/v1/memory/search` - Verifies seeding with search

## Next Steps

After seeding:
1. Test search queries via API or Swagger UI (`http://localhost:8000/docs`)
2. Add more domain-specific context cards
3. Query the system about your goals, stack, or architecture
4. Build agents that leverage this context for decision-making
