from flask import Flask, request, jsonify
from flask_cors import CORS
import copy
import time


app = Flask(__name__)
CORS(app)


def bubble_sort(arr):
    a = copy.copy(arr)
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def merge_sort(arr):
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    return _merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))


def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    return result + left[i:] + right[j:]


RUNS = 7


def time_sort(fn, arr):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        fn(arr)
        times.append(time.perf_counter() - start)
    times.sort()
    trimmed = times[1:-1] if len(times) > 2 else times
    return sum(trimmed) / len(trimmed) * 1000


def build_insight(results, n):
    bubble_time = results["bubble"]["time_ms"]
    merge_time = results["merge"]["time_ms"]

    if abs(bubble_time - merge_time) / max(bubble_time, merge_time) * 100 < 12:
        return (
            f"Both algorithms are close on this random input. With n={n}, Merge Sort still keeps its O(n log n) structure while Bubble Sort does O(n²) work."
        )

    if merge_time < bubble_time:
        return (
            f"Merge Sort wins ({merge_time:.3f} ms vs {bubble_time:.3f} ms). "
            "It divides the array in half each time, while Bubble Sort keeps scanning the list repeatedly."
        )

    return (
        f"Bubble Sort wins ({bubble_time:.3f} ms vs {merge_time:.3f} ms). "
        "That would be unusual, because Bubble Sort normally loses on anything but very tiny arrays."
    )


ALGO_META = {
    "bubble": ("Bubble Sort", "O(n²)", bubble_sort),
    "merge": ("Merge Sort", "O(n log n)", merge_sort),
}


@app.route("/sort", methods=["POST"])
def sort():
    data = request.get_json() or {}
    nums = data.get("numbers", [])
    algorithms = [key for key in data.get("algorithms", ["bubble", "merge"]) if key in ALGO_META]

    if not nums:
        return jsonify({"error": "No numbers provided"}), 400

    if not algorithms:
        algorithms = ["bubble", "merge"]

    n = len(nums)
    results = {}
    sorted_output = None

    for key in algorithms:
        name, complexity, fn = ALGO_META[key]
        ms = time_sort(fn, nums)
        if sorted_output is None:
            sorted_output = fn(nums)
        results[key] = {"name": name, "complexity": complexity, "time_ms": ms}

    winner = min(results, key=lambda key: results[key]["time_ms"])
    insight = build_insight(results, n)

    return jsonify(
        {
            "input_size": n,
            "sorted": sorted_output,
            "results": results,
            "winner": winner,
            "insight": insight,
        }
    )








if __name__ == "__main__":
    app.run(port=5050, debug=True)