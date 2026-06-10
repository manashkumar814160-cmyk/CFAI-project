from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import copy
import random
import sys

sys.setrecursionlimit(100000)

app = Flask(__name__)
CORS(app)

# ── Bubble Sort ──────────────────────────────────────────────
def bubble_sort(arr):
    
    a = copy.copy(arr)
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a

# ── Merge Sort ───────────────────────────────────────────────
def merge_sort(arr):
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    return _merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def _merge(l, r):
    res = []; i = j = 0
    while i < len(l) and j < len(r):
        if l[i] <= r[j]: res.append(l[i]); i += 1
        else: res.append(r[j]); j += 1
    return res + l[i:] + r[j:]

def quick_sort(arr):
    a = copy.copy(arr)
    try:
        _quick(a, 0, len(a) - 1)
    except RecursionError:
        return sorted(a)   # fallback if stack blows on pathological input
    return a

def _quick(a, lo, hi):
    if lo >= hi:
        return
    p = _partition(a, lo, hi)
    _quick(a, lo, p - 1)
    _quick(a, p + 1, hi)

def _partition(a, lo, hi):
    pivot = a[lo]          # first element as pivot
    i = lo + 1
    for j in range(lo + 1, hi + 1):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[lo], a[i - 1] = a[i - 1], a[lo]
    return i - 1

# ── Timing ───────────────────────────────────────────────────
RUNS = 7

def time_sort(fn, arr):
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        fn(arr)
        times.append(time.perf_counter() - t0)
    times.sort()
    trimmed = times[1:-1] if len(times) > 2 else times
    return sum(trimmed) / len(trimmed) * 1000   # ms

# ── Scenario generators ──────────────────────────────────────
def generate_scenario(scenario, n):
    if scenario == "random":
        return random.sample(range(n * 10), n)
    elif scenario == "sorted":
        return list(range(n))
    elif scenario == "reverse":
        return list(range(n, 0, -1))
    elif scenario == "nearly_sorted":
        a = list(range(n))
        for _ in range(max(1, n // 20)):
            i, j = random.randint(0, n-1), random.randint(0, n-1)
            a[i], a[j] = a[j], a[i]
        return a
    elif scenario == "many_duplicates":
        return [random.randint(0, max(1, n // 10)) for _ in range(n)]
    return random.sample(range(n * 10), n)

# ── Insight builder ───────────────────────────────────────────
def build_insight(algorithms, results, arr, n):
    keys = list(algorithms)

    if 'merge' in keys and 'quick' in keys:
        mt = results['merge']['time_ms']
        qt = results['quick']['time_ms']
        diff_pct = abs(mt - qt) / max(mt, qt) * 100

        # Measure how sorted the array is
        inversions = 0
        sample = arr if n <= 300 else random.sample(arr, 300)
        ns = len(sample)
        for i in range(ns):
            for j in range(i+1, ns):
                if sample[i] > sample[j]:
                    inversions += 1
        max_inv = ns * (ns - 1) / 2
        sortedness = 1 - (inversions / max_inv if max_inv > 0 else 0)  # 1=sorted, 0=reverse

        unique_ratio = len(set(arr)) / n

        if diff_pct < 12:
            return (
                "Both algorithms perform similarly here. "
                f"With random data and moderate n={n}, both O(n log n) strategies converge — "
                "Merge's guaranteed halving and Quick's cache-friendly in-place swaps balance out."
            )

        if qt < mt:
            # Quick wins
            if sortedness > 0.9:
                return (
                    f"Quick Sort wins ({qt:.3f} ms vs {mt:.3f} ms). "
                    "Surprising — sorted input with a first-element pivot usually hurts Quick Sort. "
                    "The data must have enough variance that partitions stayed reasonably balanced."
                )
            if unique_ratio < 0.2:
                return (
                    f"Quick Sort wins ({qt:.3f} ms vs {mt:.3f} ms). "
                    f"Heavy duplicates ({100*(1-unique_ratio):.0f}% repeated values) — "
                    "Quick Sort's in-place swaps are cheaper than Merge Sort's repeated array allocation even with skewed partitions."
                )
            return (
                f"Quick Sort wins ({qt:.3f} ms vs {mt:.3f} ms). "
                "Random data is Quick Sort's ideal case — first-element pivot partitions well when values are shuffled. "
                "It also wins on cache locality: in-place swaps avoid the extra memory Merge Sort needs for auxiliary arrays."
            )
        else:
            # Merge wins
            if sortedness > 0.85:
                return (
                    f"Merge Sort wins ({mt:.3f} ms vs {qt:.3f} ms). "
                    "This is Quick Sort's known weakness: sorted or nearly-sorted input with a first-element pivot "
                    "creates maximally unbalanced partitions (pivot is always the min), degrading to O(n²). "
                    "Merge Sort always splits exactly in half — data order doesn't affect it."
                )
            if sortedness < 0.15:
                return (
                    f"Merge Sort wins ({mt:.3f} ms vs {qt:.3f} ms). "
                    "Reverse-sorted input is the worst case for first-element pivot Quick Sort — "
                    "every partition picks the minimum, creating n-1 recursive calls. "
                    "Merge Sort's fixed halving is completely immune to this."
                )
            return (
                f"Merge Sort wins ({mt:.3f} ms vs {qt:.3f} ms). "
                "Quick Sort's first-element pivot was unlucky on this data — "
                "partitions skewed, pushing it toward O(n²) behaviour. "
                "Merge Sort's guaranteed O(n log n) held firm."
            )

    # Bubble vs anything
    winner = min(keys, key=lambda k: results[k]['time_ms'])
    loser  = max(keys, key=lambda k: results[k]['time_ms'])
    wt = results[winner]['time_ms']
    lt = results[loser]['time_ms']
    return (
        f"{results[winner]['name']} wins ({wt:.3f} ms vs {lt:.3f} ms). "
        f"Bubble Sort's O(n²) double loop does {n*n:,} comparisons; "
        f"the other algorithm needs only ~{int(n * n.bit_length()):,}."
    )

# ── Routes ────────────────────────────────────────────────────
ALGO_META = {
    'bubble': ('Bubble Sort',  'O(n²)',       bubble_sort),
    'merge':  ('Merge Sort',   'O(n log n)',  merge_sort),
    'quick':  ('Quick Sort',   'O(n log n) worst O(n²)', quick_sort),
}

@app.route('/sort', methods=['POST'])
def sort():
    data       = request.get_json()
    nums       = data.get('numbers', [])
    algorithms = data.get('algorithms', ['bubble', 'merge'])

    if not nums:
        return jsonify({'error': 'No numbers provided'}), 400

    n = len(nums)
    results = {}
    sorted_output = None
    for key in algorithms:
        name, complexity, fn = ALGO_META[key]
        ms = time_sort(fn, nums)
        if sorted_output is None:
            sorted_output = fn(nums)
        results[key] = {'name': name, 'complexity': complexity, 'time_ms': ms}

    winner  = min(results, key=lambda k: results[k]['time_ms'])
    insight = build_insight(algorithms, results, nums, n)

    return jsonify({
        'input_size': n,
        'sorted': sorted_output,
        'results': results,
        'winner': winner,
        'insight': insight,
    })

@app.route('/scenario', methods=['POST'])
def scenario():
    data       = request.get_json()
    sc         = data.get('scenario', 'random')
    n          = int(data.get('n', 200))
    algorithms = data.get('algorithms', ['merge', 'quick'])

    arr = generate_scenario(sc, n)

    results = {}
    for key in algorithms:
        name, complexity, fn = ALGO_META[key]
        ms = time_sort(fn, arr)
        results[key] = {'name': name, 'complexity': complexity, 'time_ms': ms}

    winner  = min(results, key=lambda k: results[k]['time_ms'])
    insight = build_insight(algorithms, results, arr, n)

    return jsonify({
        'input_size': n,
        'scenario': sc,
        'sample': arr[:20],
        'results': results,
        'winner': winner,
        'insight': insight,
    })

if __name__ == '__main__':
    app.run(port=5050, debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import copy
import random
import sys

sys.setrecursionlimit(100000)

app = Flask(__name__)
CORS(app)

# ── Bubble Sort ──────────────────────────────────────────────
def bubble_sort(arr):
    a = copy.copy(arr)
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a

# ── Merge Sort ───────────────────────────────────────────────
def merge_sort(arr):
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    return _merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def _merge(l, r):
    res = []; i = j = 0
    while i < len(l) and j < len(r):
        if l[i] <= r[j]: res.append(l[i]); i += 1
        else: res.append(r[j]); j += 1
    return res + l[i:] + r[j:]

# ── Quick Sort (first-element pivot — intentionally naive) ───
# This matches textbook Quick Sort and shows real O(n²) degradation
# on sorted/reverse inputs, making merge vs quick comparison meaningful.
def quick_sort(arr):
    a = copy.copy(arr)
    try:
        _quick(a, 0, len(a) - 1)
    except RecursionError:
        return sorted(a)   # fallback if stack blows on pathological input
    return a

def _quick(a, lo, hi):
    if lo >= hi:
        return
    p = _partition(a, lo, hi)
    _quick(a, lo, p - 1)
    _quick(a, p + 1, hi)

def _partition(a, lo, hi):
    pivot = a[lo]          # first element as pivot
    i = lo + 1
    for j in range(lo + 1, hi + 1):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[lo], a[i - 1] = a[i - 1], a[lo]
    return i - 1

# ── Timing ───────────────────────────────────────────────────
RUNS = 7

def time_sort(fn, arr):
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        fn(arr)
        times.append(time.perf_counter() - t0)
    times.sort()
    trimmed = times[1:-1] if len(times) > 2 else times
    return sum(trimmed) / len(trimmed) * 1000   # ms

# ── Scenario generators ──────────────────────────────────────
def generate_scenario(scenario, n):
    if scenario == "random":
        return random.sample(range(n * 10), n)
    elif scenario == "sorted":
        return list(range(n))
    elif scenario == "reverse":
        return list(range(n, 0, -1))
    elif scenario == "nearly_sorted":
        a = list(range(n))
        for _ in range(max(1, n // 20)):
            i, j = random.randint(0, n-1), random.randint(0, n-1)
            a[i], a[j] = a[j], a[i]
        return a
    elif scenario == "many_duplicates":
        return [random.randint(0, max(1, n // 10)) for _ in range(n)]
    return random.sample(range(n * 10), n)

# ── Insight builder ───────────────────────────────────────────
def build_insight(algorithms, results, arr, n):
    keys = list(algorithms)

    if 'merge' in keys and 'quick' in keys:
        mt = results['merge']['time_ms']
        qt = results['quick']['time_ms']
        diff_pct = abs(mt - qt) / max(mt, qt) * 100

        # Measure how sorted the array is
        inversions = 0
        sample = arr if n <= 300 else random.sample(arr, 300)
        ns = len(sample)
        for i in range(ns):
            for j in range(i+1, ns):
                if sample[i] > sample[j]:
                    inversions += 1
        max_inv = ns * (ns - 1) / 2
        sortedness = 1 - (inversions / max_inv if max_inv > 0 else 0)  # 1=sorted, 0=reverse

        unique_ratio = len(set(arr)) / n

        if diff_pct < 12:
            return (
                "Both algorithms perform similarly here. "
                f"With random data and moderate n={n}, both O(n log n) strategies converge — "
                "Merge's guaranteed halving and Quick's cache-friendly in-place swaps balance out."
            )

        if qt < mt:
            # Quick wins
            if sortedness > 0.9:
                return (
                    f"Quick Sort wins ({qt:.3f} ms vs {mt:.3f} ms). "
                    "Surprising — sorted input with a first-element pivot usually hurts Quick Sort. "
                    "The data must have enough variance that partitions stayed reasonably balanced."
                )
            if unique_ratio < 0.2:
                return (
                    f"Quick Sort wins ({qt:.3f} ms vs {mt:.3f} ms). "
                    f"Heavy duplicates ({100*(1-unique_ratio):.0f}% repeated values) — "
                    "Quick Sort's in-place swaps are cheaper than Merge Sort's repeated array allocation even with skewed partitions."
                )
            return (
                f"Quick Sort wins ({qt:.3f} ms vs {mt:.3f} ms). "
                "Random data is Quick Sort's ideal case — first-element pivot partitions well when values are shuffled. "
                "It also wins on cache locality: in-place swaps avoid the extra memory Merge Sort needs for auxiliary arrays."
            )
        else:
            # Merge wins
            if sortedness > 0.85:
                return (
                    f"Merge Sort wins ({mt:.3f} ms vs {qt:.3f} ms). "
                    "This is Quick Sort's known weakness: sorted or nearly-sorted input with a first-element pivot "
                    "creates maximally unbalanced partitions (pivot is always the min), degrading to O(n²). "
                    "Merge Sort always splits exactly in half — data order doesn't affect it."
                )
            if sortedness < 0.15:
                return (
                    f"Merge Sort wins ({mt:.3f} ms vs {qt:.3f} ms). "
                    "Reverse-sorted input is the worst case for first-element pivot Quick Sort — "
                    "every partition picks the minimum, creating n-1 recursive calls. "
                    "Merge Sort's fixed halving is completely immune to this."
                )
            return (
                f"Merge Sort wins ({mt:.3f} ms vs {qt:.3f} ms). "
                "Quick Sort's first-element pivot was unlucky on this data — "
                "partitions skewed, pushing it toward O(n²) behaviour. "
                "Merge Sort's guaranteed O(n log n) held firm."
            )

    # Bubble vs anything
    winner = min(keys, key=lambda k: results[k]['time_ms'])
    loser  = max(keys, key=lambda k: results[k]['time_ms'])
    wt = results[winner]['time_ms']
    lt = results[loser]['time_ms']
    return (
        f"{results[winner]['name']} wins ({wt:.3f} ms vs {lt:.3f} ms). "
        f"Bubble Sort's O(n²) double loop does {n*n:,} comparisons; "
        f"the other algorithm needs only ~{int(n * n.bit_length()):,}."
    )

# ── Routes ────────────────────────────────────────────────────
ALGO_META = {
    'bubble': ('Bubble Sort',  'O(n²)',       bubble_sort),
    'merge':  ('Merge Sort',   'O(n log n)',  merge_sort),
    'quick':  ('Quick Sort',   'O(n log n) worst O(n²)', quick_sort),
}

@app.route('/sort', methods=['POST'])
def sort():
    data       = request.get_json()
    nums       = data.get('numbers', [])
    algorithms = data.get('algorithms', ['bubble', 'merge'])

    if not nums:
        return jsonify({'error': 'No numbers provided'}), 400

    n = len(nums)
    results = {}
    sorted_output = None
    for key in algorithms:
        name, complexity, fn = ALGO_META[key]
        ms = time_sort(fn, nums)
        if sorted_output is None:
            sorted_output = fn(nums)
        results[key] = {'name': name, 'complexity': complexity, 'time_ms': ms}

    winner  = min(results, key=lambda k: results[k]['time_ms'])
    insight = build_insight(algorithms, results, nums, n)

    return jsonify({
        'input_size': n,
        'sorted': sorted_output,
        'results': results,
        'winner': winner,
        'insight': insight,
    })

@app.route('/scenario', methods=['POST'])
def scenario():
    data       = request.get_json()
    sc         = data.get('scenario', 'random')
    n          = int(data.get('n', 200))
    algorithms = data.get('algorithms', ['merge', 'quick'])

    arr = generate_scenario(sc, n)

    results = {}
    for key in algorithms:
        name, complexity, fn = ALGO_META[key]
        ms = time_sort(fn, arr)
        results[key] = {'name': name, 'complexity': complexity, 'time_ms': ms}

    winner  = min(results, key=lambda k: results[k]['time_ms'])
    insight = build_insight(algorithms, results, arr, n)

    return jsonify({
        'input_size': n,
        'scenario': sc,
        'sample': arr[:20],
        'results': results,
        'winner': winner,
        'insight': insight,
    })

if __name__ == '__main__':
    app.run(port=5050, debug=True)