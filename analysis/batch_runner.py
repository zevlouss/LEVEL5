import argparse
import json
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from solve_level5 import (
    TARGET_ADDRESS,
    DEFAULT_PRE_TICK_MODES,
    DEFAULT_POST_TICK_MODES,
    compute_area_sources,
    load_rectangles,
    apply_tick_adjustments,
    apply_pair_tick_adjustments,
    pairing_orders,
    combine_pairs,
    transform_bytes,
    contains_byte77,
    privkey_to_address,
)


def parse_list_argument(value: str | None) -> List[str] | None:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def build_combinations(
    areas: Sequence[str],
    pre_modes: Sequence[str],
    pairings: Sequence[str],
    post_modes: Sequence[str],
) -> List[Tuple[str, str, str, str]]:
    combos: List[Tuple[str, str, str, str]] = []
    for area in areas:
        for pre in pre_modes:
            for pairing in pairings:
                for post in post_modes:
                    combos.append((area, pre, pairing, post))
    return combos


def maybe_append_jsonl(path: Path | None, entry: Dict) -> None:
    if path is None:
        return
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch explorer for Zden Level 5 combinations")
    parser.add_argument("--image", default="crypto5fix.png", help="Path to puzzle image")
    parser.add_argument("--areas", help="Comma-separated list of area metrics to include")
    parser.add_argument("--pairs", help="Comma-separated list of pairing scheme names to include")
    parser.add_argument("--pre-modes", help="Comma-separated pre-tick modes")
    parser.add_argument("--post-modes", help="Comma-separated post-tick modes")
    parser.add_argument("--start-index", type=int, default=0, help="Start index within combination list")
    parser.add_argument("--end-index", type=int, help="End index (exclusive) within combination list")
    parser.add_argument("--transform-limit", type=int, help="Maximum transforms to evaluate per combination")
    parser.add_argument("--output", help="JSONL file to append per-combination summaries")
    parser.add_argument("--matches-output", help="JSONL file to append any matches found")
    parser.add_argument("--no-dedupe", action="store_true", help="Disable global deduplication of candidate keys")
    args = parser.parse_args()

    image_path = args.image
    rectangles = load_rectangles(image_path)
    area_sources = compute_area_sources(rectangles)

    area_filter = parse_list_argument(args.areas)
    if area_filter is not None:
        missing = [name for name in area_filter if name not in area_sources]
        if missing:
            raise ValueError(f"Unknown area metrics requested: {missing}")
        selected_areas = [name for name in area_sources if name in area_filter]
    else:
        selected_areas = list(area_sources.keys())
    selected_areas.sort()

    pairings_all = pairing_orders()
    pair_filter = parse_list_argument(args.pairs)
    if pair_filter is not None:
        missing_pairs = [name for name in pair_filter if name not in pairings_all]
        if missing_pairs:
            raise ValueError(f"Unknown pairing names requested: {missing_pairs}")
        selected_pairings = [name for name in pairings_all if name in pair_filter]
    else:
        selected_pairings = list(pairings_all.keys())
    selected_pairings.sort()

    pre_modes = parse_list_argument(args.pre_modes) or DEFAULT_PRE_TICK_MODES
    post_modes = parse_list_argument(args.post_modes) or DEFAULT_POST_TICK_MODES

    combinations = build_combinations(selected_areas, pre_modes, selected_pairings, post_modes)
    if not combinations:
        raise RuntimeError("No combinations to evaluate")

    start = max(0, args.start_index)
    end = args.end_index if args.end_index is not None else len(combinations)
    end = min(end, len(combinations))
    if start >= end:
        raise ValueError("Start index must be less than end index")

    combos_slice = combinations[start:end]
    output_path = Path(args.output) if args.output else None
    matches_path = Path(args.matches_output) if args.matches_output else None

    global_seen: set[str] = set()
    dedupe_enabled = not args.no_dedupe

    total_candidates = 0
    total_transforms = 0
    matches_found: List[Dict] = []

    for offset, (area_name, pre_mode, pairing_name, post_mode) in enumerate(combos_slice, start=start):
        values = area_sources[area_name]
        pairs = pairings_all[pairing_name]

        adjusted_values = apply_tick_adjustments(values, pre_mode)
        pair_sums = combine_pairs(adjusted_values, pairs)
        post_pair_sums = apply_pair_tick_adjustments(pair_sums, pairs, post_mode)

        transforms_processed = 0
        candidates_processed = 0
        unique_keys: set[str] = set()
        combination_matches: List[Dict] = []

        for transform_name, byte_values in transform_bytes(post_pair_sums):
            transforms_processed += 1
            if args.transform_limit and transforms_processed > args.transform_limit:
                break

            if len(byte_values) != 32 or not contains_byte77(byte_values):
                continue

            priv_bytes = bytes(byte_values)
            hex_key = priv_bytes.hex()

            if dedupe_enabled:
                if hex_key in global_seen:
                    continue
                global_seen.add(hex_key)

            if hex_key in unique_keys:
                continue
            unique_keys.add(hex_key)
            candidates_processed += 1
            total_candidates += 1

            for compressed in (True, False):
                address = privkey_to_address(priv_bytes, compressed)
                if address == TARGET_ADDRESS:
                    match_entry = {
                        "combo_index": offset,
                        "area": area_name,
                        "pre_tick": pre_mode,
                        "post_tick": post_mode,
                        "pairing": pairing_name,
                        "transform": transform_name,
                        "format": "compressed" if compressed else "uncompressed",
                        "hex_key": hex_key,
                        "address": address,
                    }
                    combination_matches.append(match_entry)
                    matches_found.append(match_entry)
                    maybe_append_jsonl(matches_path, match_entry)

        total_transforms += transforms_processed

        summary = {
            "combo_index": offset,
            "area": area_name,
            "pre_tick": pre_mode,
            "post_tick": post_mode,
            "pairing": pairing_name,
            "transforms_processed": transforms_processed,
            "candidates_processed": candidates_processed,
            "unique_keys": len(unique_keys),
            "matches": len(combination_matches),
        }
        maybe_append_jsonl(output_path, summary)

        print(
            f"[{offset}] area={area_name} pre={pre_mode} pair={pairing_name} post={post_mode} "
            f"transforms={transforms_processed} candidates={candidates_processed} matches={len(combination_matches)}"
        )

    final_summary = {
        "combinations_total": len(combinations),
        "combinations_processed": len(combos_slice),
        "start_index": start,
        "end_index": end,
        "total_transforms": total_transforms,
        "total_candidates": total_candidates,
        "matches_found": len(matches_found),
    }

    if output_path:
        maybe_append_jsonl(output_path, {"summary": final_summary})

    print(json.dumps(final_summary, indent=2))


if __name__ == "__main__":
    main()
