# Система расчета рабочего времени

## Использование в коде

### Получение сервиса
```python
from core.service_locator import get_locator

loc = get_locator()
time_calc = loc.time_calculation
```

### 1. Конверсия часов в дни
```python
# Сколько рабочих дней в 40 часах?
work_days = time_calc.calculate_work_days_from_hours(40)
# Result: 5 (при 8 ч/день)
```

### 2. Конверсия дней в часы
```python
# Сколько часов в 10 рабочих днях?
work_hours = time_calc.calculate_hours_from_work_days(10)
# Result: 80 (при 8 ч/день)
```

### 3. Добавление рабочих дней к дате
```python
from datetime import date

start = date(2026, 4, 6)  # Понедельник
end = time_calc.add_work_days_to_date(start, 5)
# Result: date(2026, 4, 10) - Пятница (выходные пропущены)
```

### 4. Подсчет рабочих дней между датами
```python
from datetime import date

start = date(2026, 4, 6)
end = date(2026, 4, 10)
count = time_calc.count_work_days_between(start, end)
# Result: 5
```

### 5. Расчет конечной даты
```python
from datetime import date

start = date(2026, 4, 6)
end = time_calc.calculate_end_date(start, 10)
# Result: date(2026, 4, 17) - 10 рабочих дней
```

### 6. Проверка рабочего дня
```python
from datetime import date

check_date = date(2026, 4, 5)  # Воскресенье
is_work = time_calc.is_work_day(check_date)
# Result: False
```

## Примеры использования в сервисах

### Пример 1: Планирование задачи
```python
from datetime import date
from core.service_locator import get_locator

# При создании задачи с указанием часов
work_hours_estimated = 40
planned_start = date.today()

loc = get_locator()
work_days = loc.time_calculation.calculate_work_days_from_hours(work_hours_estimated)
planned_end = loc.time_calculation.calculate_end_date(planned_start, work_days)

# Сохранить в БД:
# duration_days_planned = work_days
# start_date_planned = planned_start
# end_date_planned = planned_end
```

### Пример 2: Проверка просрочки задачи
```python
from datetime import date
from core.service_locator import get_locator

task = get_task_from_db()  # has end_date_planned
today = date.today()

loc = get_locator()

work_days_remaining = loc.time_calculation.count_work_days_between(today, task.end_date_planned)
if work_days_remaining < 0:
    print(f"Задача просрочена на {abs(work_days_remaining)} рабочих дней")
```

### Пример 3: Расчет СРМ (как сейчас работает)
```python
# CPM scheduler уже работает с duration_days_planned
# просто убедитесь, что эта величина рассчитана или выражена в рабочих днях

duration_days_planned = 5  # 5 рабочих дней
# CPM использует эту величину для расчета ES, EF, LS, LF
```

## Ключевые моменты

1. **Все расчеты используют стандартный график**
   - Если нужно использовать другой график, передайте `schedule` параметр в методы репозитория
   
2. **Выходные всегда пропускаются**
   - При расчете дат автоматически прибавляются выходные

3. **Перерыв на обед учитывается при расчете часов**
   - При конверсии дней в часы вычитается время обеда

4. **Расчеты работают только для будущих дат**
   - Не рекомендуется использовать для исторических данных

## Интеграция с CPM

```python
# В CPMSchedulerService при инициализации задач:
for task in tasks:
    # Убедитесь, что duration_days_planned рассчитан корректно:
    if task.work_hours_planned:
        task.duration_days_planned = time_calc.calculate_work_days_from_hours(
            task.work_hours_planned
        )
```

## Тестирование

```python
import pytest
from datetime import date
from core.service_locator import get_locator

@pytest.fixture
def time_calc():
    loc = get_locator()
    return loc.time_calculation

def test_hours_to_days(time_calc):
    assert time_calc.calculate_work_days_from_hours(8) == 1
    assert time_calc.calculate_work_days_from_hours(40) == 5

def test_work_day_skip_weekends(time_calc):
    friday = date(2026, 4, 10)
    result = time_calc.add_work_days_to_date(friday, 1)
    # Should return Monday 2026-04-13, skipping weekend
    assert result == date(2026, 4, 13)

def test_is_work_day(time_calc):
    monday = date(2026, 4, 6)
    saturday = date(2026, 4, 4)
    assert time_calc.is_work_day(monday) == True
    assert time_calc.is_work_day(saturday) == False
```
