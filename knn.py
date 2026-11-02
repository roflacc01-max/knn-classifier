import math
import json
import csv
from collections import Counter

DATA_FILE = "data.json"
CSV_FILE = "data.csv"


def read_point(prompt):
    """
    Запрашивает координаты точки, возвращает кортеж (x, y).
    """
    while True:
        try:
            x = float(input(f"{prompt} по оси x: "))
            y = float(input(f"{prompt} по оси y: "))
            return (x, y)
        except ValueError:
            print("Ошибка: введите числовое значение.")


def collect_points():
    """
    Диалог ввода обучающих точек.
    Возвращает словарь структуры (1).
    """
    data = {}

    while True:
        print("\nВведите координаты точки:")
        point = read_point("Введите координату точки")
        label = input("Введите метку класса объекта: ").strip()

        if label not in data:
            data[label] = []
        data[label].append(point)

        while True:
            cont = input("Добавить ещё одну точку? (y — да, любой другой символ — нет): ").strip().lower()
            if cont == 'y':
                break
            else:
                if len(data) < 2:
                    print("Ошибка: необходимо ввести не менее двух различных меток классов.")
                    break
                if any(len(points) < 3 for points in data.values()):
                    print("Ошибка: для каждой метки необходимо ввести не менее трёх точек.")
                    break
                return data
        if cont != 'y':
            return data


def read_k(total):
    """
    Запрашивает k, проверяя условие 1 <= k <= total.
    """
    while True:
        try:
            k = int(input(f"Введите количество ближайших соседей k (1..{total}): "))
            if 1 <= k <= total:
                return k
            else:
                print(f"Ошибка: k должно быть в диапазоне от 1 до {total}.")
        except ValueError:
            print("Ошибка: введите целое число.")


def distance(p1, p2):
    """
    Евклидово расстояние между двумя кортежами координат.
    Для сравнения используем квадрат расстояния (без извлечения корня).
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def neighbours(data, point, k):
    """
    k ближайших соседей: список [(квадрат_расстояния, метка, координаты), ...],
    отсортированный по возрастанию расстояния.
    """
    distances = []
    for label, points in data.items():
        for p in points:
            dist = distance(point, p)
            distances.append((dist, label, p))

    distances.sort(key=lambda x: x[0])
    return distances[:k]


def predict(data, point, k):
    """
    Предсказанная метка класса для точки point.
    """
    nearest = neighbours(data, point, k)

    votes = Counter()
    for dist, label, p in nearest:
        votes[label] += 1

    max_votes = max(votes.values())
    candidates = [label for label, count in votes.items() if count == max_votes]

    if len(candidates) > 1:
        min_dist = float('inf')
        winner = candidates[0]
        for dist, label, p in nearest:
            if label in candidates and dist < min_dist:
                min_dist = dist
                winner = label
        return winner
    else:
        return candidates[0]


# --- ФУНКЦИИ СОХРАНЕНИЯ И ЗАГРУЗКИ (Этап 3) ---

def save_data(data, path):
    """Сохраняет выборку в JSON-файл."""
    plain = {label: [list(p) for p in points]
             for label, points in data.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plain, f, ensure_ascii=False)


def load_data(path):
    """Читает выборку из файла; None, если файла нет или он повреждён."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return {label: [tuple(p) for p in points]
            for label, points in raw.items()}


# --- ФУНКЦИЯ ЭКСПОРТА В CSV (Вариант 6) ---

def export_to_csv(data, path):
    """Сохраняет выборку в CSV: по строке на точку — x, y, метка."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "label"])  # заголовок
        for label, points in data.items():
            for x, y in points:
                writer.writerow([x, y, label])


def main():
    """
    Точка входа: ввод данных, классификация, вывод результата.
    """
    print("=== Сбор обучающей выборки ===")

    # Пытаемся загрузить сохраненную выборку
    data = load_data(DATA_FILE)
    if data is not None:
        total = sum(len(p) for p in data.values())
        answer = input(f"Найдена сохранённая выборка ({total} точек). Использовать? (y/n): ")
        if answer.strip().lower() != "y":
            data = None

    # Если выборки нет, вводим вручную и сохраняем
    if data is None:
        data = collect_points()
        save_data(data, DATA_FILE)

    # Экспортируем в CSV (Индивидуальное задание)
    export_to_csv(data, CSV_FILE)

    total = sum(len(p) for p in data.values())
    print(f"\nВведено {total} точек, метки классов: {', '.join(sorted(set(data)))}")
    print(f"Выборка экспортирована в {CSV_FILE}")

    print("\n=== Классификация неизвестной точки ===")
    point = read_point("Введите координаты точки неизвестного класса")

    k = read_k(total)

    nearest = neighbours(data, point, k)

    print(f"\nБлижайшие соседи точки ({point[0]:.1f}, {point[1]:.1f}):")
    for dist_sq, label, p in nearest:
        print(f"({p[0]:.1f}, {p[1]:.1f})  расстояние {math.sqrt(dist_sq):.2f}  метка {label}")

    votes = Counter()
    for dist_sq, label, p in nearest:
        votes[label] += 1

    votes_str = ', '.join([f"{label} – {count}" for label, count in votes.items()])
    print(f"\nГолоса: {votes_str}")

    result = predict(data, point, k)
    print(f"Предсказанная метка класса: {result}")


if __name__ == '__main__':
    main()