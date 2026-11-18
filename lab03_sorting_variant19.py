#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЛР №3. Простые сортировки и QuickSort.
БВТ2506, Шибасов Роман Дмитриевич, вариант 19.
Запуск: python lab03_sorting_variant19.py
"""

from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path
from typing import Callable, Any

VARIANT = 19
SEED = 30 + VARIANT

# Размеры соответствуют стартовой заготовке КИМ-03.
SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
OUTPUT_DIR = Path("lab03_results")


def bubble_sort(a: list, key: Callable[[Any], Any] | None = None) -> tuple[list, int, int]:
    """Пузырьковая сортировка: возвращает (результат, сравнения, обмены)."""
    if key is None:
        key = lambda value: value
    result = list(a)
    comparisons = swaps = 0

    for end in range(len(result) - 1, 0, -1):
        changed = False
        for j in range(end):
            comparisons += 1
            if key(result[j]) > key(result[j + 1]):
                result[j], result[j + 1] = result[j + 1], result[j]
                swaps += 1
                changed = True
        if not changed:
            break

    return result, comparisons, swaps


def insertion_sort(a: list, key: Callable[[Any], Any] | None = None) -> tuple[list, int, int]:
    """Сортировка вставками; перемещения — сдвиги и запись вставляемого элемента."""
    if key is None:
        key = lambda value: value
    result = list(a)
    comparisons = moves = 0

    for i in range(1, len(result)):
        value = result[i]
        j = i - 1

        while j >= 0:
            comparisons += 1
            if key(result[j]) > key(value):
                result[j + 1] = result[j]
                moves += 1
                j -= 1
            else:
                break

        result[j + 1] = value
        if j + 1 != i:
            moves += 1

    return result, comparisons, moves


def selection_sort(a: list, key: Callable[[Any], Any] | None = None) -> tuple[list, int, int]:
    """Сортировка выбором; обмены считаются только при разных индексах."""
    if key is None:
        key = lambda value: value
    result = list(a)
    comparisons = swaps = 0
    n = len(result)

    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            comparisons += 1
            if key(result[j]) < key(result[min_index]):
                min_index = j

        if min_index != i:
            result[i], result[min_index] = result[min_index], result[i]
            swaps += 1

    return result, comparisons, swaps


def quick_sort(a: list, rng: random.Random | None = None,
               key: Callable[[Any], Any] | None = None) -> list:
    """
    Итеративный QuickSort с рандомизированным pivot и трёхчастным разбиением.
    key позволяет демонстрировать сортировку пар по первому элементу.
    """
    if rng is None:
        rng = random.Random()
    if key is None:
        key = lambda value: value

    result = list(a)
    if len(result) < 2:
        return result

    stack = [(0, len(result) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue

        pivot_index = rng.randrange(lo, hi + 1)
        pivot_value = key(result[pivot_index])

        # Dutch National Flag: [lo, lt) < pivot, [lt, i) == pivot,
        # (gt, hi] > pivot.
        lt, i, gt = lo, lo, hi
        while i <= gt:
            current = key(result[i])
            if current < pivot_value:
                result[lt], result[i] = result[i], result[lt]
                lt += 1
                i += 1
            elif current > pivot_value:
                result[i], result[gt] = result[gt], result[i]
                gt -= 1
            else:
                i += 1

        # Сначала обрабатываем меньшую часть, чтобы ограничить глубину стека.
        left = (lo, lt - 1)
        right = (gt + 1, hi)
        left_size = left[1] - left[0]
        right_size = right[1] - right[0]
        if left_size > right_size:
            if left[0] < left[1]:
                stack.append(left)
            if right[0] < right[1]:
                stack.append(right)
        else:
            if right[0] < right[1]:
                stack.append(right)
            if left[0] < left[1]:
                stack.append(left)

    return result


ALGORITHMS = {
    "Пузырьком": lambda data: bubble_sort(data)[0],
    "Вставками": lambda data: insertion_sort(data)[0],
    "Выбором": lambda data: selection_sort(data)[0],
    "QuickSort": lambda data: quick_sort(data, random.Random(SEED)),
}


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три воспроизводимых класса входных данных."""
    rng = random.Random(seed + n)
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "Упорядоченный": sorted(data),
        "Случайный": data,
        "Обратный": sorted(data, reverse=True),
    }


def is_sorted(data: list) -> bool:
    return all(data[i] <= data[i + 1] for i in range(len(data) - 1))


def verify_algorithm(name: str, function: Callable[[list], list]) -> None:
    """Граничные случаи и 300 сравнений с эталонной sorted()."""
    boundary = [
        [], [7], [2, 1], [5, 5, 5, 5],
        [1, 2, 3, 4, 5], [5, 4, 3, 2, 1],
        [-3, 0, -3, 8, 2, 0],
    ]
    for data in boundary:
        result = function(list(data))
        if not isinstance(result, list):
            raise AssertionError(f"{name}: результат не является списком")
        if not is_sorted(result):
            raise AssertionError(f"{name}: результат не отсортирован: {data} -> {result}")
        if sorted(result) != sorted(data):
            raise AssertionError(f"{name}: изменился набор элементов")

    rng = random.Random(2026)
    for _ in range(300):
        data = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        result = function(list(data))
        if result != sorted(data):
            raise AssertionError(f"{name}: ошибка на входе {data}")

    print(f"[OK] {name}: граничные случаи и 300 случайных тестов")


def stability_demo() -> dict[str, bool]:
    """Проверяет сохранение порядка меток у элементов с одинаковым ключом."""
    sample = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (3, "e")]
    expected = {
        key: [label for value, label in sample if value == key]
        for key in sorted({value for value, _ in sample})
    }

    results = {
        "Пузырьком": bubble_sort(sample, key=lambda pair: pair[0])[0],
        "Вставками": insertion_sort(sample, key=lambda pair: pair[0])[0],
        "Выбором": selection_sort(sample, key=lambda pair: pair[0])[0],
        "QuickSort": quick_sort(sample, random.Random(SEED), key=lambda pair: pair[0]),
    }

    stable = {}
    print("\nДемонстрация стабильности (сортировка по ключу):")
    for name, result in results.items():
        order = {
            key: [label for value, label in result if value == key]
            for key in sorted({value for value, _ in sample})
        }
        stable[name] = order == expected
        print(f"  {name:12}: {result} -> {'стабильная' if stable[name] else 'нестабильная'}")
    return stable


def benchmark(function: Callable[[list], list], data: list) -> float:
    """Прогрев + медиана пяти запусков на отдельных копиях данных."""
    function(list(data))  # прогрев не включается в замер
    times = []
    for _ in range(REPEATS):
        sample = list(data)
        start = time.perf_counter()
        function(sample)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def save_counter_table() -> None:
    path = OUTPUT_DIR / "operation_counters.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Алгоритм", "Класс входа", "Размер", "Сравнения", "Обмены/перемещения"])
        for class_name, data in make_inputs(500, SEED).items():
            for name, sorter in (
                ("Пузырьком", bubble_sort),
                ("Вставками", insertion_sort),
                ("Выбором", selection_sort),
            ):
                _, comparisons, moves = sorter(data)
                writer.writerow([name, class_name, len(data), comparisons, moves])
    print(f"\nТаблица счётчиков: {path}")


def run_benchmarks() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    rows = []

    plans = [
        ("Пузырьком", bubble_sort, SIZES_QUADRATIC),
        ("Вставками", insertion_sort, SIZES_QUADRATIC),
        ("Выбором", selection_sort, SIZES_QUADRATIC),
        ("QuickSort", lambda data: quick_sort(data, random.Random(SEED)), SIZES_QUICK),
    ]

    print("\nЗамеры времени (медиана, секунд):")
    for name, sorter, sizes in plans:
        print(f"\n{name}:")
        for n in sizes:
            inputs = make_inputs(n, SEED)
            for class_name, data in inputs.items():
                elapsed = benchmark(sorter, data)
                rows.append([name, class_name, n, elapsed])
                print(f"  n={n:>6}, {class_name:<15}: {elapsed:.6f}")

    csv_path = OUTPUT_DIR / "benchmark_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Алгоритм", "Класс входа", "Размер", "Медиана времени, с"])
        writer.writerows(rows)
    print(f"\nТаблица замеров: {csv_path}")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib не установлен. Установите: python -m pip install matplotlib")
        return

    # Отдельный log-log график для каждой пары «алгоритм — класс входа».
    for algorithm in dict.fromkeys(row[0] for row in rows):
        for class_name in dict.fromkeys(row[1] for row in rows):
            selected = [row for row in rows if row[0] == algorithm and row[1] == class_name]
            selected.sort(key=lambda row: row[2])
            x = [row[2] for row in selected]
            y = [row[3] for row in selected]

            plt.figure(figsize=(7, 5))
            plt.loglog(x, y, marker="o", label="Измеренное время")
            plt.title(f"{algorithm}: {class_name.lower()} вход")
            plt.xlabel("Размер массива n (логарифмическая шкала)")
            plt.ylabel("Время, секунды (логарифмическая шкала)")
            plt.grid(True, which="both", linestyle=":")
            plt.legend()
            safe_algorithm = algorithm.lower().replace(" ", "_")
            safe_class = class_name.lower().replace(" ", "_")
            image_path = OUTPUT_DIR / f"{safe_algorithm}_{safe_class}.png"
            plt.tight_layout()
            plt.savefig(image_path, dpi=150)
            plt.close()

    print(f"Графики сохранены в каталоге: {OUTPUT_DIR}")


def main() -> None:
    random.seed(SEED)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("ЛР №3 — простые сортировки и QuickSort")
    print("БВТ2506 | Шибасов Роман Дмитриевич | вариант 19")
    print(f"Seed = 30 + {VARIANT} = {SEED}")

    for name, function in ALGORITHMS.items():
        verify_algorithm(name, function)

    # Для сортировки выбором число сравнений всегда n*(n-1)/2.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    if comparisons != 10:
        raise AssertionError("Неверный счётчик сравнений сортировки выбором")
    print("[OK] Счётчик Selection Sort: n*(n-1)/2")

    stability_demo()
    save_counter_table()
    run_benchmarks()
    print("\nРабота завершена. Проверьте CSV и PNG в lab03_results.")


if __name__ == "__main__":
    main()
