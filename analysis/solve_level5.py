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
    outer_perimeter: float
    inner_perimeter: float
    bbox: Tuple[int, int, int, int]
    center_intensity_sum: float


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
        outer_perimeter = cv2.arcLength(outer_cnt, True)
        inner_perimeter = cv2.arcLength(inner_cnt, True)

        x, y, w, h = cv2.boundingRect(outer_cnt)
        cx, cy = x + w / 2, y + h / 2
        row_key = round(cy / 10) * 10

        cx_i, cy_i = int(round(cx)), int(round(cy))
        half = 2
        y0 = max(cy_i - half, 0)
        y1 = min(cy_i + half + 1, binary.shape[0])
        x0 = max(cx_i - half, 0)
        x1 = min(cx_i + half + 1, binary.shape[1])
        patch = binary[y0:y1, x0:x1]
        center_sum = float(patch.sum() / 255)

        metrics = RectangleMetrics(
            index=-1,
            row=-1,
            col=-1,
            outer_area=outer_area,
            inner_area=inner_area,
            shell_area=shell_area,
            outer_perimeter=outer_perimeter,
            inner_perimeter=inner_perimeter,
            bbox=(x, y, w, h),
            center_intensity_sum=center_sum,
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


def apply_pair_tick_adjustments(pair_sums: np.ndarray, pairs: Iterable[Tuple[int, int]], mode: str) -> np.ndarray:
    if mode == "none":
        return pair_sums

    adjusted = pair_sums.astype(float).copy()
    for pair_idx, (a, b) in enumerate(pairs):
        delta = 0.0
        factor = 1.0
        for rect_idx, amount in TICK_ADJUSTMENTS.items():
            if rect_idx in (a, b):
                delta += amount
                factor *= amount

        if delta == 0 and factor == 1.0:
            continue

        if mode == "add":
            adjusted[pair_idx] += delta
        elif mode == "subtract":
            adjusted[pair_idx] -= delta
        elif mode == "multiply":
            adjusted[pair_idx] *= factor
        else:
            raise ValueError(f"Unsupported pair adjustment mode: {mode}")

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

    # Diagonal traversal (top-left to bottom-right)
    diagonal = []
    for s in range(0, 15):
        for r in range(8):
            c = s - r
            if 0 <= c < 8:
                diagonal.append(idx[r, c])
    orders["diagonal"] = diagonal

    diagonal_snake = []
    for s in range(0, 15):
        diag_indices = [idx[r, s - r] for r in range(8) if 0 <= s - r < 8]
        if s % 2:
            diag_indices = list(reversed(diag_indices))
        diagonal_snake.extend(diag_indices)
    orders["diagonal_snake"] = diagonal_snake

    # Spiral traversal (clockwise from top-left)
    spiral = []
    top, bottom, left, right = 0, 7, 0, 7
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            spiral.append(idx[top, c])
        top += 1
        for r in range(top, bottom + 1):
            spiral.append(idx[r, right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                spiral.append(idx[bottom, c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                spiral.append(idx[r, left])
            left += 1
    orders["spiral_cw"] = spiral

    # Gray-code traversal (3-bit Gray for rows and columns)
    gray_sequence = [0, 1, 3, 2, 6, 7, 5, 4]
    gray_order = []
    for gr in gray_sequence:
        for gc in gray_sequence:
            gray_order.append(idx[gr, gc])
    orders["gray_rowcol"] = gray_order

    pairings: Dict[str, List[Tuple[int, int]]] = {}
    rotation_offsets = {"base": [0], "ticks": [1, 39, 40, 52, 53]}

    for name, order in orders.items():
        if len(order) != 64:
            raise ValueError(f"Order {name} has incorrect length {len(order)}")

        offsets = rotation_offsets["base"] + rotation_offsets["ticks"]
        seen_pairs = set()

        for offset in offsets:
            rotated = order[offset:] + order[:offset]
            pairs = tuple((rotated[i], rotated[i + 1]) for i in range(0, 64, 2))
            if pairs in seen_pairs:
                continue
            seen_pairs.add(pairs)
            suffix = f"_rot{offset}" if offset else ""
            pairings[f"{name}{suffix}"] = list(pairs)

        # Swap tick rectangles with their immediate successors (if present)
        for tick_idx in TICK_ADJUSTMENTS.keys():
            for direction in (1, -1):
                swapped_order = order[:]
                try:
                    pos = swapped_order.index(tick_idx)
                    swap_pos = pos + direction
                    if 0 <= swap_pos < len(swapped_order):
                        swapped_order[pos], swapped_order[swap_pos] = swapped_order[swap_pos], swapped_order[pos]
                        pairs = tuple((swapped_order[i], swapped_order[i + 1]) for i in range(0, 64, 2))
                        if pairs not in seen_pairs:
                            seen_pairs.add(pairs)
                            pairings[f"{name}_swap{tick_idx}_{direction}"] = list(pairs)
                except ValueError:
                    continue

    return pairings


def combine_pairs(values: np.ndarray, pairs: Iterable[Tuple[int, int]]) -> np.ndarray:
    return np.array([values[a] + values[b] for a, b in pairs], dtype=float)


def transform_bytes(raw: np.ndarray) -> Iterable[Tuple[str, List[int]]]:
    def normalize_values(values: np.ndarray) -> np.ndarray | None:
        if not np.all(np.isfinite(values)):
            values = np.where(np.isfinite(values), values, 0.0)
        max_val = float(np.max(values))
        min_val = float(np.min(values))
        if max_val == min_val:
            return None
        scaled = np.clip(np.round((values - min_val) / (max_val - min_val) * 255), 0, 255)
        return scaled.astype(int)

    raw_int = raw.astype(np.int64)

    # Modulo variants
    mod_vals = (raw_int % 256).astype(int)
    yield "mod256", mod_vals.tolist()

    max_val = float(np.max(raw))
    min_val = float(np.min(raw))
    spread = max_val - min_val
    if max_val != 0:
        res = np.clip(np.round(raw / max_val * 255), 0, 255).astype(int)
        yield "scale_to_max", res.tolist()
    if spread > 0:
        res = np.clip(np.round((raw - min_val) / spread * 255), 0, 255).astype(int)
        yield "minmax_norm", res.tolist()

    # Non-linear normalizations
    shifted = raw - min_val if min_val < 0 else raw.copy()
    shifted = np.maximum(shifted, 0)
    if np.any(shifted > 0):
        for name, arr in (
            ("sqrt_norm", np.sqrt(shifted)),
            ("cuberoot_norm", np.cbrt(shifted)),
            ("square_norm", np.square(shifted)),
            ("log_norm", np.log1p(shifted)),
        ):
            normalized = normalize_values(arr)
            if normalized is not None:
                yield name, normalized.tolist()

    mean_val = float(np.mean(raw))
    std_val = float(np.std(raw))
    if std_val > 0:
        z = (raw - mean_val) / std_val
        for name, arr in (
            ("logistic_norm", 1.0 / (1.0 + np.exp(-z))),
            ("tanh_norm", np.tanh(z)),
        ):
            normalized = normalize_values(arr)
            if normalized is not None:
                yield name, normalized.tolist()

    if len(raw) > 1:
        ranks = np.argsort(np.argsort(raw))
        rank_scaled = np.round(ranks / (len(raw) - 1) * 255).astype(int)
        yield "rank_scaled", rank_scaled.tolist()

        hint_pattern = [0x09, 0x11, 0x18, 0x19, 0x77, 0x0C, 0x0D, 0x0A]
        hint_sbox = (hint_pattern * ((len(raw) // len(hint_pattern)) + 1))[: len(raw)]
        yield "hint_sbox_rank", [hint_sbox[r] for r in ranks]
    else:
        yield "rank_scaled", [0]
        yield "hint_sbox_rank", [0x77]

    # Expanded affine transforms modulo 256
    affine_a = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 29, 31, 47, 63, 79, 95, 111, 127, 159, 191, 223, 255]
    affine_b = list(range(0, 256, 8)) + [77, 119, 155, 203]
    for a, b in itertools.product(affine_a, affine_b):
        transformed = (a * raw_int + b) % 256
        yield f"affine_{a}_{b}", transformed.astype(int).tolist()

    xor_inputs = mod_vals
    yield "xor_55", [(val ^ 0x55) for val in xor_inputs]
    yield "xor_aa", [(val ^ 0xAA) for val in xor_inputs]
    yield "xor_77", [(val ^ 0x77) for val in xor_inputs]
    yield "negate", [(-int(val)) % 256 for val in raw]

    def reverse_byte(byte: int) -> int:
        b = byte & 0xFF
        b = ((b >> 1) & 0x55) | ((b & 0x55) << 1)
        b = ((b >> 2) & 0x33) | ((b & 0x33) << 2)
        b = ((b >> 4) & 0x0F) | ((b & 0x0F) << 4)
        return b

    yield "bit_reverse", [reverse_byte(val) for val in xor_inputs]


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

    outer_values = np.array([r.outer_area for r in rectangles], dtype=float)
    inner_values = np.array([r.inner_area for r in rectangles], dtype=float)
    shell_values = np.array([r.shell_area for r in rectangles], dtype=float)
    outer_perimeters = np.array([r.outer_perimeter for r in rectangles], dtype=float)
    inner_perimeters = np.array([r.inner_perimeter for r in rectangles], dtype=float)
    perimeter_diff = outer_perimeters - inner_perimeters
    bbox_areas = np.array([r.bbox[2] * r.bbox[3] for r in rectangles], dtype=float)
    aspect_ratios = np.array([
        (r.bbox[2] / r.bbox[3]) if r.bbox[3] != 0 else 0.0 for r in rectangles
    ], dtype=float)
    center_sums = np.array([r.center_intensity_sum for r in rectangles], dtype=float)

    row_weights = np.array([0, 9, 1, 1, 1, 8, 1, 9], dtype=float)
    col_weights = np.array([1, 1, 1, 2, 2, 1, 1, 1], dtype=float)
    row_indices = np.array([r.row for r in rectangles], dtype=int)
    col_indices = np.array([r.col for r in rectangles], dtype=int)

    row_weight_shell = shell_values * row_weights[row_indices]
    col_weight_shell = shell_values * col_weights[col_indices]
    rowcol_product_shell = shell_values * row_weights[row_indices] * col_weights[col_indices]

    shell_outer_ratio = shell_values / np.where(outer_values != 0, outer_values, 1)
    inner_outer_ratio = inner_values / np.where(outer_values != 0, outer_values, 1)
    shell_perimeter_ratio = shell_values / np.where(perimeter_diff != 0, perimeter_diff, 1)

    area_sources = {
        "outer": outer_values,
        "inner": inner_values,
        "shell": shell_values,
        "outer_perimeter": outer_perimeters,
        "perimeter_diff": perimeter_diff,
        "shell_outer_ratio": shell_outer_ratio,
        "inner_outer_ratio": inner_outer_ratio,
        "shell_perimeter_ratio": shell_perimeter_ratio,
        "bbox_area": bbox_areas,
        "aspect_ratio": aspect_ratios,
        "center_patch_sum": center_sums,
        "row_weight_shell": row_weight_shell,
        "col_weight_shell": col_weight_shell,
        "rowcol_product_shell": rowcol_product_shell,
    }

    pre_tick_modes = ["none", "add", "subtract", "multiply"]
    post_tick_modes = ["none", "add", "subtract", "multiply"]
    pairings = pairing_orders()

    candidates: List[Dict[str, str]] = []
    checked_keys: set[str] = set()

    for area_name, base_values in area_sources.items():
        for pre_tick_mode in pre_tick_modes:
            adjusted_values = apply_tick_adjustments(base_values, pre_tick_mode)

            for pair_name, pairs in pairings.items():
                pair_sums = combine_pairs(adjusted_values, pairs)

                for post_tick_mode in post_tick_modes:
                    post_pair_sums = apply_pair_tick_adjustments(pair_sums, pairs, post_tick_mode)

                    for transform_name, byte_values in transform_bytes(post_pair_sums):
                        if len(byte_values) != 32:
                            continue
                        if not contains_byte77(byte_values):
                            continue

                        priv_bytes = bytes(byte_values)
                        hex_key = priv_bytes.hex()
                        if hex_key in checked_keys:
                            continue
                        checked_keys.add(hex_key)

                        for compressed in (True, False):
                            address = privkey_to_address(priv_bytes, compressed=compressed)
                            if address == TARGET_ADDRESS:
                                candidates.append({
                                    "area": area_name,
                                    "pre_tick": pre_tick_mode,
                                    "post_tick": post_tick_mode,
                                    "pairing": pair_name,
                                    "transform": transform_name,
                                    "format": "compressed" if compressed else "uncompressed",
                                    "hex_key": hex_key,
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

