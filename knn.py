import math
from collections import Counter


def read_point(prompt):
    while True:
        try:
            x = float(input(f"{prompt} по оси x: "))
            y = float(input(f"{prompt} по оси y: "))
            return (x, y)
        except ValueError:
            print("Ошибка: введите числовое значение.")


def collect_points():
    data = {}

    while True:
        print("\nВведите координаты точки:")
        point = read_point("Введите координату точки")
        label = input("Введите метку класса объекта: ").strip()

        if label not in data:
            data[label] = []
        data[label].append(point)
        if len(data) >= 2:
            all_points_count = sum(len(points) for points in data.values())
            if all_points_count >= 6 and all(len(points) >= 3 for points in data.values()):
                pass

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
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def neighbours(data, point, k):
    distances = []
    for label, points in data.items():
        for p in points:
            dist = distance(point, p)
            distances.append((dist, label, p))
    distances.sort(key=lambda x: x[0])
    return distances[:k]


def predict(data, point, k):
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


def main():
    print("Сбор выборки")
    data = collect_points()

    total_points = sum(len(points) for points in data.values())
    labels = set(data.keys())
    print(f"\nВведено {total_points} точек, метки классов: {', '.join(sorted(labels))}")

    print("\nКлассификация неизвестной точки")
    point = read_point("Введите координаты точки неизвестного класса")

    k = read_k(total_points)

    nearest = neighbours(data, point, k)

    print(f"\nБлижайшие соседи точки ({point[0]:.1f}, {point[1]:.1f}):")
    for dist, label, p in nearest:
        print(f"({p[0]:.1f}, {p[1]:.1f})  расстояние {math.sqrt(dist):.2f}  метка {label}")

    votes = Counter()
    for dist, label, p in nearest:
        votes[label] += 1

    votes_str = ', '.join([f"{label} – {count}" for label, count in votes.items()])
    print(f"\nГолоса: {votes_str}")

    result = predict(data, point, k)
    print(f"Предсказанная метка класса: {result}")


if __name__ == '__main__':
    main()