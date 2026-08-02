"""Calibrate cheap structural features against heuristic cover costs."""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import re
import math
import statistics
import sys
import time


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("proxy_v2_cost_eval", HERE / "proxy_v2_cost_eval.py")
assert SPEC and SPEC.loader
model = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = model
SPEC.loader.exec_module(model)


def structural_features(targets: tuple[int, ...], active_hidden: int) -> dict[str, float]:
    weights = Counter(target.bit_count() for target in targets)
    forced_pairs = {target for target in targets if target.bit_count() == 2}
    pairs: Counter[int] = Counter()
    triples: Counter[int] = Counter()
    forced_hits = 0
    width = model.VISIBLE + active_hidden
    for target in targets:
        bits = [bit for bit in range(width) if (target >> bit) & 1]
        if len(bits) >= 3:
            forced_hits += sum(pair & target == pair for pair in forced_pairs)
        for i in range(len(bits)):
            for j in range(i + 1, len(bits)):
                pair = (1 << bits[i]) | (1 << bits[j])
                pairs[pair] += 1
                for k in range(j + 1, len(bits)):
                    triples[pair | (1 << bits[k])] += 1
    standalone = {2: 1, 3: 2, 4: 3, 5: 6, 6: 7, 7: 10, 8: 13, 9: 16}
    values: dict[str, float] = {
        "active_hidden": active_hidden,
        "targets": len(targets),
        "standalone_units": sum(standalone[weight] * count for weight, count in weights.items()),
        "forced_hits": forced_hits,
        "pair_incidence": sum(pairs.values()),
        "pair_unique": len(pairs),
        "pair_repeat": sum(count - 1 for count in pairs.values()),
        "pair_repeat_cap3": sum(min(count - 1, 3) for count in pairs.values()),
        "pair_ge2": sum(count >= 2 for count in pairs.values()),
        "pair_ge3": sum(count >= 3 for count in pairs.values()),
        "triple_incidence": sum(triples.values()),
        "triple_unique": len(triples),
        "triple_repeat": sum(count - 1 for count in triples.values()),
        "triple_repeat_cap2": sum(min(count - 1, 2) for count in triples.values()),
        "triple_ge2": sum(count >= 2 for count in triples.values()),
    }
    values.update({f"w{weight}": weights[weight] for weight in range(2, 10)})
    return values


def candidates(root: Path):
    seen: set[tuple[str, str]] = set()
    for filename in glob.glob(str(root / ".research" / "**" / "*.log"), recursive=True):
        for line in open(filename, encoding="utf-8", errors="ignore"):
            match = re.search(r"\bX=([0-9a-fA-F,]+)\s+D=([0-9a-fA-F,]+)", line)
            if not match:
                continue
            raw_x, raw_d = match.groups()
            if len(raw_x.split(",")) != 32 or len(raw_d.split(",")) != 10:
                continue
            key = raw_x, raw_d
            if key in seen:
                continue
            seen.add(key)
            yield Path(filename).relative_to(root).as_posix(), raw_x, raw_d


def ranks(values: list[float]) -> list[int]:
    result = [0] * len(values)
    for rank, index in enumerate(sorted(range(len(values)), key=lambda index: (values[index], index))):
        result[index] = rank
    return result


def correlation(left: list[float], right: list[float]) -> float:
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((a - left_mean) ** 2 for a in left) * sum((b - right_mean) ** 2 for b in right)
    )
    return numerator / denominator if denominator else 0.0


def metrics(actual: list[float], predicted: list[float]) -> dict[str, float]:
    error = [predicted[index] - actual[index] for index in range(len(actual))]
    return {
        "mae_units": statistics.fmean(abs(value) for value in error),
        "rmse_units": math.sqrt(statistics.fmean(value * value for value in error)),
        "maximum_absolute_error_units": max(abs(value) for value in error),
        "pearson": correlation(actual, predicted),
        "spearman": correlation(ranks(actual), ranks(predicted)),
    }


def solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    augmented = [row.copy() + [value] for row, value in zip(matrix, vector)]
    size = len(vector)
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("singular calibration matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = augmented[row][column]
            if multiplier:
                augmented[row] = [
                    augmented[row][index] - multiplier * augmented[column][index]
                    for index in range(size + 1)
                ]
    return [augmented[index][-1] for index in range(size)]


def fit_ridge(x_train: list[list[float]], y_train: list[float], ridge: float) -> tuple[list[float], list[float], list[float]]:
    columns = len(x_train[0])
    mean = [statistics.fmean(row[column] for row in x_train) for column in range(columns)]
    scale = [
        math.sqrt(statistics.fmean((row[column] - mean[column]) ** 2 for row in x_train))
        for column in range(columns)
    ]
    scale = [value if value >= 1e-9 else 1.0 for value in scale]
    design = [
        [1.0] + [(row[column] - mean[column]) / scale[column] for column in range(columns)]
        for row in x_train
    ]
    size = columns + 1
    normal = [[0.0] * size for _ in range(size)]
    rhs = [0.0] * size
    for row, target in zip(design, y_train):
        for left in range(size):
            rhs[left] += row[left] * target
            for right in range(size):
                normal[left][right] += row[left] * row[right]
    for index in range(1, size):
        normal[index][index] += ridge
    coefficients = solve_linear(normal, rhs)
    return coefficients, mean, scale


def predict_ridge(
    x: list[list[float]], coefficients: list[float], mean: list[float], scale: list[float]
) -> list[float]:
    return [
        coefficients[0]
        + sum(
            ((row[column] - mean[column]) / scale[column]) * coefficients[column + 1]
            for column in range(len(row))
        )
        for row in x
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    parser.add_argument("--restarts", type=int, default=12)
    parser.add_argument("--pair-top-k", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    records = []
    for source, raw_x, raw_d in candidates(args.root.resolve()):
        x_rows = model.parse_hex_list(raw_x, 32)
        d_rows = model.parse_hex_list(raw_d, 10)
        targets, active_hidden = model.build_targets(x_rows, d_rows)
        if not targets or max(target.bit_count() for target in targets) > 9:
            continue
        options = [model.make_options(target, 32 + active_hidden) for target in targets]
        digest = hashlib.sha256((raw_x + "|" + raw_d).encode()).hexdigest()
        cover = model.solve_cover(options, args.restarts, args.seed ^ int(digest[:8], 16), args.pair_top_k)
        features = structural_features(targets, active_hidden)
        records.append(
            {
                "id": digest[:16],
                "source": source,
                "features": features,
                "cover_logic_units": cover.units,
                "fixed_gate": (32 + active_hidden) * 5 + 38,
            }
        )

    # Hash split is stable if more log points are later added.
    train = [record for record in records if int(record["id"][-2:], 16) % 5]
    test = [record for record in records if not int(record["id"][-2:], 16) % 5]
    feature_sets = {
        "weights_only": ["standalone_units", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9"],
        "pair_structural": [
            "standalone_units", "forced_hits", "pair_repeat", "pair_ge2", "pair_ge3",
            "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9",
        ],
        "pair_triple_structural": [
            "standalone_units", "forced_hits", "pair_repeat", "pair_ge2", "pair_ge3",
            "triple_repeat", "triple_ge2", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9",
        ],
    }
    fits = {}
    for fit_name, names in feature_sets.items():
        x_train = [[record["features"][name] for name in names] for record in train]
        y_train = [float(record["cover_logic_units"]) for record in train]
        x_test = [[record["features"][name] for name in names] for record in test]
        y_test = [float(record["cover_logic_units"]) for record in test]
        coefficients, mean, scale = fit_ridge(x_train, y_train, ridge=8.0)
        fits[fit_name] = {
            "features": names,
            "intercept_normalized": float(coefficients[0]),
            "coefficients_normalized": coefficients[1:],
            "mean": mean,
            "scale": scale,
            "train": metrics(y_train, predict_ridge(x_train, coefficients, mean, scale)),
            "test": metrics(y_test, predict_ridge(x_test, coefficients, mean, scale)),
        }

    actual = [float(record["cover_logic_units"]) for record in records]
    standalone = [record["features"]["standalone_units"] for record in records]
    result = {
        "schema": 1,
        "label": {
            "kind": "multi-start coordinate-descent cover upper bound",
            "restarts": args.restarts,
            "pair_top_k": args.pair_top_k,
        },
        "records": len(records),
        "train_records": len(train),
        "test_records": len(test),
        "seconds": time.perf_counter() - started,
        "baseline_standalone": metrics(actual, standalone),
        "fits": fits,
        "points": records,
    }
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "points"}, indent=2))


if __name__ == "__main__":
    main()
