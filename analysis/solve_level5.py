import hashlib
import itertools
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable

import cv2
import numpy as np
from ecdsa import SECP256k1, SigningKey

TARGET_ADDRESS = "1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7"
TICK_ADJUSTMENTS: Dict[int, int] = {39: 17, 52: 6}  # zero-based indices for rectangles 40 and 53


@dataclass
class RectangleMetrics:
    index: int
    row: int
    col: int
    outer_area: float
    inner_area: float
    shell_area: float
    bbox: Tuple[int, int, int, int]


def load_rectangles(image_path: str) -> List[RectangleMetrics]:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    _, binary = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        raise RuntimeError("No contours detected")

    grouped: Dict[int, List[RectangleMetrics]] = {}

    for idx, cnt in enumerate(contours):
        parent = hierarchy[0][idx][3]
        if parent == -1:
            continue

        outer_cnt = contours[parent]
        inner_cnt = cnt
        outer_area = cv2.contourArea(outer_cnt)
        inner_area = cv2.contourArea(inner_cnt)
        shell_area = outer_area - inner_area

        x, y, w, h = cv2.boundingRect(outer_cnt)
        cx, cy = x + w / 2, y + h / 2
        row_key = round(cy / 10) * 10

        metrics = RectangleMetrics(
            index=-1,
            row=-1,
            col=-1,
            outer_area=outer_area,
            inner_area=inner_area,
            shell_area=shell_area,
            bbox=(x, y, w, h),
        )

        grouped.setdefault(row_key, []).append((cx, metrics))

    valid_rows = sorted(key for key, items in grouped.items() if len(items) == 8)
    if len(valid_rows) != 8:
        raise RuntimeError(f"Expected 8 valid rows, found {len(valid_rows)}: {valid_rows}")

    rectangles: List[RectangleMetrics] = []
    for row_idx, row_key in enumerate(valid_rows):
        entries = sorted(grouped[row_key], key=lambda item: item[0])
        for col_idx, (_, metrics) in enumerate(entries):
            metrics.index = row_idx * 8 + col_idx
            metrics.row = row_idx
            metrics.col = col_idx
            rectangles.append(metrics)

    rectangles.sort(key=lambda m: m.index)
    if len(rectangles) != 64:
        raise RuntimeError(f"Expected 64 rectangles, got {len(rectangles)}")

    return rectangles


def apply_tick_adjustments(values: np.ndarray, mode: str) -> np.ndarray:
    adjusted = values.astype(float).copy()
    for idx, amount in TICK_ADJUSTMENTS.items():
        if idx < 0 or idx >= len(adjusted):
            continue
        if mode == "add":
            adjusted[idx] += amount
        elif mode == "subtract":
            adjusted[idx] -= amount
        elif mode == "multiply":
            adjusted[idx] *= amount
        elif mode == "none":
            pass
        else:
            raise ValueError(f"Unsupported adjustment mode: {mode}")
    return adjusted


def pairing_orders() -> Dict[str, List[Tuple[int, int]]]:
    idx = np.arange(64).reshape(8, 8)

    orders: Dict[str, List[int]] = {}
    orders["row_major"] = idx.flatten(order="C").tolist()
    orders["column_major"] = idx.flatten(order="F").tolist()

    snake_rows = []
    for r in range(8):
        row = idx[r]
        snake_rows.extend(row[::-1] if r % 2 else row)
    orders["snake_rows"] = snake_rows

    snake_cols = []
    for c in range(8):
        col = idx[:, c]
        snake_cols.extend(col[::-1] if c % 2 else col)
    orders["snake_cols"] = snake_cols

    pairings: Dict[str, List[Tuple[int, int]]] = {}
    for name, order in orders.items():
        if len(order) != 64:
            raise ValueError(f"Order {name} has incorrect length {len(order)}")
        pairs = [(order[i], order[i + 1]) for i in range(0, 64, 2)]
        pairings[name] = pairs

    return pairings


def combine_pairs(values: np.ndarray, pairs: Iterable[Tuple[int, int]]) -> np.ndarray:
    return np.array([values[a] + values[b] for a, b in pairs], dtype=float)


def transform_bytes(raw: np.ndarray) -> Dict[str, List[int]]:
    results: Dict[str, List[int]] = {}

    # Mod 256 of raw values
    results["mod256"] = [int(v) % 256 for v in raw]

    max_val = float(np.max(raw))
    if max_val > 0:
        res = np.clip(np.round(raw / max_val * 255), 0, 255)
        results["scale_to_max"] = res.astype(int).tolist()

    min_val = float(np.min(raw))
    spread = max_val - min_val
    if spread > 0:
        res = np.clip(np.round((raw - min_val) / spread * 255), 0, 255)
        results["minmax_norm"] = res.astype(int).tolist()

    # Small affine transforms modulo 256 (inspired by mini-puzzle digits)
    affine_params = list(itertools.product([1, 3, 5, 7, 9, 11, 13, 15, 255], [0, 16, 32, 48, 64, 77, 96]))
    for a, b in affine_params:
        transformed = [(a * int(v) + b) % 256 for v in raw]
        results[f"affine_{a}_{b}"] = transformed

    return results


def privkey_to_address(priv_bytes: bytes, compressed: bool) -> str:
    sk = SigningKey.from_string(priv_bytes, curve=SECP256k1)
    vk = sk.verifying_key

    if compressed:
        prefix = b"02" if vk.to_string()[-1] % 2 == 0 else b"03"
        pubkey = bytes.fromhex(prefix.decode()) + vk.to_string()[:32]
    else:
        pubkey = b"\x04" + vk.to_string()

    sha = hashlib.sha256(pubkey).digest()
    ripe = hashlib.new("ripemd160", sha).digest()
    payload = b"\x00" + ripe
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    address_bytes = payload + checksum
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    value = int.from_bytes(address_bytes, "big")
    encoded = ""
    while value > 0:
        value, rem = divmod(value, 58)
        encoded = alphabet[rem] + encoded

    # handle leading zeros
    padding = 0
    for byte in address_bytes:
        if byte == 0:
            padding += 1
        else:
            break
    return "1" * padding + encoded


def contains_byte77(values: List[int]) -> bool:
    return any(v == 0x77 for v in values)


def search_candidates(image_path: str) -> List[Dict[str, str]]:
    rectangles = load_rectangles(image_path)

    area_sources = {
        "outer": np.array([r.outer_area for r in rectangles], dtype=float),
        "inner": np.array([r.inner_area for r in rectangles], dtype=float),
        "shell": np.array([r.shell_area for r in rectangles], dtype=float),
    }

    tick_modes = ["none", "add", "subtract", "multiply"]
    pairings = pairing_orders()

    candidates: List[Dict[str, str]] = []

    for area_name, base_values in area_sources.items():
        for tick_mode in tick_modes:
            try:
                adjusted_values = apply_tick_adjustments(base_values, tick_mode)
            except ValueError:
                continue

            for pair_name, pairs in pairings.items():
                pair_sums = combine_pairs(adjusted_values, pairs)
                transformed_sets = transform_bytes(pair_sums)

                for transform_name, byte_values in transformed_sets.items():
                    if len(byte_values) != 32:
                        continue
                    if not contains_byte77(byte_values):
                        continue

                    priv_bytes = bytes(byte_values)

                    for compressed in (True, False):
                        address = privkey_to_address(priv_bytes, compressed=compressed)
                        if address == TARGET_ADDRESS:
                            candidates.append({
                                "area": area_name,
                                "tick": tick_mode,
                                "pairing": pair_name,
                                "transform": transform_name,
                                "format": "compressed" if compressed else "uncompressed",
                                "hex_key": priv_bytes.hex(),
                                "address": address,
                            })
    return candidates


def main():
    import json

    image_path = "crypto5fix.png"
    candidates = search_candidates(image_path)
    output = {
        "found": len(candidates),
        "candidates": candidates,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

