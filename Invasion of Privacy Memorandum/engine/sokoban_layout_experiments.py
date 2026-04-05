#!/usr/bin/env python3
"""Run Sokoban-style apartment layout experiments for 1BR and 2BR units.

The script uses a coarse 1-foot grid and randomized placement to estimate the
minimum square footage needed to satisfy furniture, circulation, and scenario
constraints.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import random
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


Cell = Tuple[int, int]
Rect = Tuple[int, int, int, int]


@dataclass(frozen=True)
class Item:
    name: str
    room: str
    w: int
    h: int
    rotate: bool = True


@dataclass
class LayoutCandidate:
    layout_type: str
    width: int
    height: int
    rooms: Dict[str, Rect]
    door_cells: Dict[str, Cell]
    entry: Cell
    bathroom: Cell

    @property
    def sqft(self) -> int:
        return self.width * self.height


ITEMS: List[Item] = [
    # Jane
    Item("jane_full_bed", "jane_room", 5, 7),
    Item("jane_recliner", "jane_room", 3, 3),
    Item("jane_scooter_parking", "jane_room", 3, 5),
    Item("jane_tv_desk_40in", "jane_room", 4, 2),
    Item("jane_closet_zone", "jane_room", 2, 6, rotate=False),
    Item("jane_standup_ac", "jane_room", 2, 2, rotate=False),
    # Benjamin
    Item("benjamin_queen_bed", "ben_room", 5, 7),
    Item("benjamin_standing_desk", "ben_room", 6, 3),
    Item("benjamin_desk_bike_treadmill", "ben_room", 6, 4),
    Item("benjamin_filing_cabinets", "ben_room", 4, 2),
    Item("benjamin_closet_zone", "ben_room", 2, 6, rotate=False),
    Item("benjamin_standup_ac", "ben_room", 2, 2, rotate=False),
    Item("xl_dog_bed", "ben_room", 4, 3),
    # Shared
    Item("guest_worker_temp_zone", "living_room", 6, 6),
    Item("dog_alert_containment_zone", "living_room", 5, 5),
    Item("bathroom_fixture_zone", "bathroom", 5, 8, rotate=False),
]

NON_BLOCKING_ITEMS = {"bathroom_fixture_zone"}

ROOM_COLORS = {
    "ben_room": "#f4d35e",
    "jane_room": "#9ad1d4",
    "mother_room": "#f7a399",
    "living_room": "#c7d3ff",
    "bathroom": "#d9ead3",
}

ITEM_COLORS = {
    "bed": "#ffcc80",
    "desk": "#90caf9",
    "storage": "#bcaaa4",
    "mobility": "#a5d6a7",
    "dog": "#ffe082",
    "guest": "#ef9a9a",
    "other": "#e0e0e0",
}


def _cells_for_rect(rect: Rect) -> Set[Cell]:
    x, y, w, h = rect
    return {(cx, cy) for cx in range(x, x + w) for cy in range(y, y + h)}


def _room_for_cell(rooms: Dict[str, Rect], cell: Cell) -> Optional[str]:
    x, y = cell
    for room_name, (rx, ry, rw, rh) in rooms.items():
        if rx <= x < rx + rw and ry <= y < ry + rh:
            return room_name
    return None


def _build_candidate(layout_type: str, width: int, height: int) -> LayoutCandidate:
    bath_w = 8
    bath_h = 8
    if layout_type == "1br":
        bed_w = max(11, int(width * 0.34))
        living_w = width - bed_w
        rooms = {
            "ben_room": (0, 0, bed_w, height),
            "living_room": (bed_w, 0, living_w, height),
            "bathroom": (living_w - bath_w + bed_w, height - bath_h, bath_w, bath_h),
            # In one-bedroom mode, Jane and mother are both forced into living space.
            "jane_room": (bed_w, 0, living_w, height),
            "mother_room": (bed_w, 0, living_w, height),
        }
        door_cells = {
            "ben_room": (bed_w - 1, max(1, height // 2)),
            "living_room": (bed_w, max(1, height // 2)),
            "bathroom": (bed_w + living_w - bath_w, height - (bath_h // 2)),
        }
        entry = (bed_w + 1, 1)
    else:
        bed_w = max(10, int(width * 0.28))
        bed_h = max(10, int(height * 0.48))
        rooms = {
            "ben_room": (0, 0, bed_w, bed_h),
            "jane_room": (0, bed_h, bed_w, height - bed_h),
            # Mother uses living-room partition/privacy zone in 2BR simulations.
            "mother_room": (bed_w, 0, width - bed_w, height),
            "living_room": (bed_w, 0, width - bed_w, height),
            "bathroom": (width - bath_w, height - bath_h, bath_w, bath_h),
        }
        door_cells = {
            "ben_room": (bed_w - 1, max(1, bed_h // 2)),
            "jane_room": (bed_w - 1, bed_h + max(1, (height - bed_h) // 2)),
            "living_room": (bed_w, max(1, height // 2)),
            "bathroom": (width - bath_w, height - (bath_h // 2)),
        }
        entry = (bed_w + 1, 1)

    bathroom = door_cells["bathroom"]
    return LayoutCandidate(layout_type, width, height, rooms, door_cells, entry, bathroom)


def _rect_inside_room(rect: Rect, room: Rect) -> bool:
    x, y, w, h = rect
    rx, ry, rw, rh = room
    return rx <= x and ry <= y and x + w <= rx + rw and y + h <= ry + rh


def _iter_rect_positions(room: Rect, w: int, h: int) -> Iterable[Rect]:
    rx, ry, rw, rh = room
    for x in range(rx, rx + rw - w + 1):
        for y in range(ry, ry + rh - h + 1):
            yield (x, y, w, h)


def _neighbors(cell: Cell, width: int, height: int) -> Iterable[Cell]:
    x, y = cell
    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        if 0 <= nx < width and 0 <= ny < height:
            yield (nx, ny)


def _l_path(a: Cell, b: Cell) -> Set[Cell]:
    cells: Set[Cell] = set()
    ax, ay = a
    bx, by = b
    step_x = 1 if bx >= ax else -1
    for x in range(ax, bx + step_x, step_x):
        cells.add((x, ay))
    step_y = 1 if by >= ay else -1
    for y in range(ay, by + step_y, step_y):
        cells.add((bx, y))
    return cells


def _inflate(cells: Set[Cell], width: int, height: int, margin: int = 1) -> Set[Cell]:
    out: Set[Cell] = set()
    for x, y in cells:
        for dx in range(-margin, margin + 1):
            for dy in range(-margin, margin + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    out.add((nx, ny))
    return out


def _is_reachable(start: Cell, goal: Cell, blocked: Set[Cell], width: int, height: int) -> bool:
    if start in blocked or goal in blocked:
        return False
    frontier = deque([start])
    seen = {start}
    while frontier:
        cur = frontier.popleft()
        if cur == goal:
            return True
        for nxt in _neighbors(cur, width, height):
            if nxt in blocked or nxt in seen:
                continue
            seen.add(nxt)
            frontier.append(nxt)
    return False


def _adjacent_walkable_target(rect: Rect, blocked: Set[Cell], width: int, height: int) -> Optional[Cell]:
    x, y, w, h = rect
    ring: List[Cell] = []
    for cx in range(x - 1, x + w + 1):
        ring.append((cx, y - 1))
        ring.append((cx, y + h))
    for cy in range(y, y + h):
        ring.append((x - 1, cy))
        ring.append((x + w, cy))
    for cell in ring:
        cx, cy = cell
        if not (0 <= cx < width and 0 <= cy < height):
            continue
        if cell in blocked:
            continue
        return cell
    return None


def _place_items(candidate: LayoutCandidate, rng: random.Random, tries: int = 200) -> Optional[Dict[str, Rect]]:
    placed: Dict[str, Rect] = {}
    blocked: Set[Cell] = set()

    reserved: Set[Cell] = set()
    reserved |= _inflate({candidate.entry, candidate.bathroom}, candidate.width, candidate.height, margin=1)
    for door in candidate.door_cells.values():
        reserved |= _inflate({door}, candidate.width, candidate.height, margin=1)
    reserved |= _inflate(_l_path(candidate.entry, candidate.bathroom), candidate.width, candidate.height, margin=1)
    for key in ("ben_room", "jane_room"):
        door = candidate.door_cells.get(key)
        if door is not None:
            reserved |= _inflate(_l_path(door, candidate.bathroom), candidate.width, candidate.height, margin=0)

    for item in ITEMS:
        room = candidate.rooms[item.room]
        orientations = [(item.w, item.h)]
        if item.rotate and item.w != item.h:
            orientations.append((item.h, item.w))

        options: List[Rect] = []
        for ow, oh in orientations:
            options.extend(_iter_rect_positions(room, ow, oh))
        rng.shuffle(options)

        chosen = None
        for rect in options[:tries]:
            cells = _cells_for_rect(rect)
            if cells & blocked:
                continue
            if cells & reserved:
                continue
            # Dog containment should be away from entry and guests.
            if item.name == "dog_alert_containment_zone":
                cx = rect[0] + rect[2] // 2
                cy = rect[1] + rect[3] // 2
                if abs(cx - candidate.entry[0]) + abs(cy - candidate.entry[1]) < 7:
                    continue
            # Desk bike/treadmill must be adjacent to standing desk.
            if item.name == "benjamin_desk_bike_treadmill":
                desk = placed.get("benjamin_standing_desk")
                if desk is None:
                    continue
                if not _rects_adjacent(rect, desk):
                    continue
            chosen = rect
            break

        if chosen is None:
            return None
        placed[item.name] = chosen
        blocked |= _cells_for_rect(chosen)

    return placed


def _rects_adjacent(a: Rect, b: Rect) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    a_left, a_right = ax, ax + aw - 1
    a_top, a_bot = ay, ay + ah - 1
    b_left, b_right = bx, bx + bw - 1
    b_top, b_bot = by, by + bh - 1

    horizontal_touch = (a_right + 1 == b_left or b_right + 1 == a_left) and not (a_bot < b_top or b_bot < a_top)
    vertical_touch = (a_bot + 1 == b_top or b_bot + 1 == a_top) and not (a_right < b_left or b_right < a_left)
    return horizontal_touch or vertical_touch


def _clearance_blocked(candidate: LayoutCandidate, placed: Dict[str, Rect]) -> Set[Cell]:
    blocked: Set[Cell] = set()
    for name, rect in placed.items():
        if name in NON_BLOCKING_ITEMS:
            continue
        blocked |= _cells_for_rect(rect)
    return blocked


def _evaluate_rules(candidate: LayoutCandidate, placed: Dict[str, Rect]) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    rooms = candidate.rooms

    # 1) Benjamin and mother cannot be in same room during sex event.
    ben_room = "ben_room"
    mother_room = "mother_room"
    if ben_room == mother_room:
        issues.append("sex_event_same_room_violation")

    # 4) Jane should not share room with mother during dog alert.
    if rooms["jane_room"] == rooms["mother_room"]:
        issues.append("dog_alert_jane_mother_privacy_violation")

    blocked = _clearance_blocked(candidate, placed)

    # 2) Mother cannot be trapped in her room during sex event.
    mother_rect = candidate.rooms["mother_room"]
    mother_start = (mother_rect[0] + 1, mother_rect[1] + 1)
    if not _is_reachable(mother_start, candidate.bathroom, blocked, candidate.width, candidate.height):
        issues.append("mother_trapped_no_bathroom_path")

    # 3) During guest/worker door activity, dog must be separable from entry.
    dog_rect = placed["dog_alert_containment_zone"]
    dog_center = (dog_rect[0] + dog_rect[2] // 2, dog_rect[1] + dog_rect[3] // 2)
    if abs(dog_center[0] - candidate.entry[0]) + abs(dog_center[1] - candidate.entry[1]) < 7:
        issues.append("dog_not_separated_from_entry")

    guest_rect = placed["guest_worker_temp_zone"]
    guest_center = (guest_rect[0] + guest_rect[2] // 2, guest_rect[1] + guest_rect[3] // 2)
    guest_access_target = _adjacent_walkable_target(guest_rect, blocked, candidate.width, candidate.height)
    if guest_access_target is None:
        issues.append("guest_zone_inaccessible")

    # Same room is acceptable when there is enough distance to separate dog from the door/guest stream.
    if abs(dog_center[0] - guest_center[0]) + abs(dog_center[1] - guest_center[1]) < 8:
        issues.append("dog_and_guest_same_zone")

    # 8, 20) Clear movement paths for cane/walker/scooter + dog flow.
    key_paths = [
        (candidate.entry, candidate.bathroom),
        (candidate.door_cells.get("ben_room"), candidate.bathroom),
        (candidate.door_cells.get("jane_room"), candidate.bathroom),
    ]
    if guest_access_target is not None:
        key_paths.append((candidate.entry, guest_access_target))
    for start, goal in key_paths:
        if start is None:
            continue
        if not _is_reachable(start, goal, blocked, candidate.width, candidate.height):
            issues.append("circulation_path_blocked")
            break

    return (len(issues) == 0), issues


def _run_layout_type(layout_type: str, attempts_per_size: int, seed: int) -> Dict[str, object]:
    if layout_type == "1br":
        candidates = [(w, h) for w in range(28, 45) for h in range(26, 42)]
    else:
        candidates = [(w, h) for w in range(36, 63) for h in range(30, 49)]
    candidates.sort(key=lambda pair: pair[0] * pair[1])

    tested = 0
    failures: Dict[str, int] = {}
    first_success: Optional[Dict[str, object]] = None
    example_successes: List[Dict[str, object]] = []

    for idx, (width, height) in enumerate(candidates):
        partial = _run_candidate_attempts((layout_type, width, height, attempts_per_size, seed + (idx * 9973)))
        tested += int(partial["testedLayouts"])
        for reason, count in partial["failureReasons"].items():
            failures[reason] = failures.get(reason, 0) + int(count)
        partial_first = partial.get("firstFeasible")
        if partial_first is not None:
            if first_success is None or int(partial_first["sqft"]) < int(first_success["sqft"]):
                first_success = partial_first
        for success in partial["sampleFeasible"]:
            if len(example_successes) >= 3:
                break
            example_successes.append(success)

    return {
        "layoutType": layout_type,
        "testedLayouts": tested,
        "firstFeasible": first_success,
        "sampleFeasible": example_successes,
        "failureReasons": failures,
    }


def _run_candidate_attempts(task: Tuple[str, int, int, int, int]) -> Dict[str, object]:
    layout_type, width, height, attempts_per_size, seed = task
    rng = random.Random(seed)
    candidate = _build_candidate(layout_type, width, height)

    tested = 0
    failures: Dict[str, int] = {}
    first_success: Optional[Dict[str, object]] = None
    example_successes: List[Dict[str, object]] = []

    for _ in range(attempts_per_size):
        tested += 1
        placed = _place_items(candidate, rng)
        if placed is None:
            failures["placement_failed"] = failures.get("placement_failed", 0) + 1
            continue
        ok, issues = _evaluate_rules(candidate, placed)
        if ok:
            success = {
                "sqft": candidate.sqft,
                "width": width,
                "height": height,
                "roomFootprints": candidate.rooms,
                "itemFootprints": placed,
            }
            if first_success is None:
                first_success = success
            if len(example_successes) < 3:
                example_successes.append(success)
        else:
            for issue in issues:
                failures[issue] = failures.get(issue, 0) + 1

    return {
        "layoutType": layout_type,
        "width": width,
        "height": height,
        "testedLayouts": tested,
        "firstFeasible": first_success,
        "sampleFeasible": example_successes,
        "failureReasons": failures,
    }


def _run_layout_type_parallel(layout_type: str, attempts_per_size: int, seed: int, processes: int) -> Dict[str, object]:
    if layout_type == "1br":
        candidates = [(w, h) for w in range(28, 45) for h in range(26, 42)]
    else:
        candidates = [(w, h) for w in range(36, 63) for h in range(30, 49)]
    candidates.sort(key=lambda pair: pair[0] * pair[1])

    tasks = [
        (layout_type, width, height, attempts_per_size, seed + (idx * 9973))
        for idx, (width, height) in enumerate(candidates)
    ]

    tested = 0
    failures: Dict[str, int] = {}
    first_success: Optional[Dict[str, object]] = None
    example_successes: List[Dict[str, object]] = []

    with multiprocessing.Pool(processes=processes) as pool:
        for partial in pool.imap_unordered(_run_candidate_attempts, tasks, chunksize=8):
            tested += int(partial["testedLayouts"])
            for reason, count in partial["failureReasons"].items():
                failures[reason] = failures.get(reason, 0) + int(count)
            partial_first = partial.get("firstFeasible")
            if partial_first is not None:
                if first_success is None or int(partial_first["sqft"]) < int(first_success["sqft"]):
                    first_success = partial_first
            for success in partial["sampleFeasible"]:
                if len(example_successes) >= 3:
                    break
                example_successes.append(success)

    return {
        "layoutType": layout_type,
        "testedLayouts": tested,
        "firstFeasible": first_success,
        "sampleFeasible": example_successes,
        "failureReasons": failures,
    }


def _base_item_area() -> int:
    return sum(item.w * item.h for item in ITEMS)


def _estimate_space_summary(results: List[Dict[str, object]]) -> Dict[str, object]:
    furniture_area = _base_item_area()
    circulation_multiplier = 1.55
    baseline_needed = int(round(furniture_area * circulation_multiplier))

    summary: Dict[str, object] = {
        "furnitureFootprintSqft": furniture_area,
        "circulationAdjustedBaselineSqft": baseline_needed,
        "notes": [
            "Baseline multiplies furniture footprint by a circulation factor for cane/walker/scooter movement.",
            "Feasibility checks also enforce privacy and alert-state exclusion rules.",
        ],
        "layoutRecommendations": {},
    }

    for item in results:
        first = item.get("firstFeasible")
        if first is None:
            summary["layoutRecommendations"][item["layoutType"]] = {
                "feasible": False,
                "estimatedMinimumSqft": None,
                "recommendation": "No feasible layout found under current exclusion rules and object set.",
            }
            continue
        sqft = int(first["sqft"])
        summary["layoutRecommendations"][item["layoutType"]] = {
            "feasible": True,
            "estimatedMinimumSqft": sqft,
            "recommendation": "Feasible in simulation; treat as a lower bound and add 10-15% safety margin for real-world walls, doors, and turning radii.",
        }
    return summary


def _item_label(name: str) -> str:
    mapping = {
        "jane_full_bed": "Jane bed",
        "jane_recliner": "Jane recliner",
        "jane_scooter_parking": "Scooter",
        "jane_tv_desk_40in": "TV desk",
        "jane_closet_zone": "Jane closet",
        "jane_standup_ac": "Jane AC",
        "benjamin_queen_bed": "Ben bed",
        "benjamin_standing_desk": "Stand desk",
        "benjamin_desk_bike_treadmill": "Bike+tread",
        "benjamin_filing_cabinets": "Files",
        "benjamin_closet_zone": "Ben closet",
        "benjamin_standup_ac": "Ben AC",
        "xl_dog_bed": "Dog bed",
        "guest_worker_temp_zone": "Guest zone",
        "dog_alert_containment_zone": "Dog alert",
        "bathroom_fixture_zone": "Bath fix",
    }
    return mapping.get(name, name)


def _item_style_group(name: str) -> str:
    if "bed" in name:
        return "bed"
    if "desk" in name or "treadmill" in name or "bike" in name:
        return "desk"
    if "closet" in name or "cabinets" in name:
        return "storage"
    if "scooter" in name:
        return "mobility"
    if "dog" in name:
        return "dog"
    if "guest" in name:
        return "guest"
    return "other"


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _render_layout_svg(layout: Dict[str, object], title: str, out_path: Path) -> None:
    width = int(layout["width"])
    height = int(layout["height"])
    rooms = layout["roomFootprints"]
    items = layout["itemFootprints"]

    cell = 18
    margin = 24
    legend_w = 280
    canvas_w = margin * 2 + width * cell + legend_w
    canvas_h = margin * 2 + height * cell + 80

    lines: List[str] = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">')
    lines.append('<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>')
    lines.append(f'<text x="{margin}" y="20" font-family="Arial" font-size="16" font-weight="bold">{_xml_escape(title)}</text>')
    lines.append(f'<text x="{margin}" y="40" font-family="Arial" font-size="12">{width}ft x {height}ft ({int(layout["sqft"])} sq ft)</text>')

    # Rooms
    for room_name, rect in rooms.items():
        x, y, w, h = [int(v) for v in rect]
        px = margin + x * cell
        py = margin + 50 + y * cell
        pw = w * cell
        ph = h * cell
        color = ROOM_COLORS.get(room_name, "#eeeeee")
        lines.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{color}" stroke="#4a4a4a" stroke-width="1" fill-opacity="0.35"/>')
        lines.append(
            f'<text x="{px + 4}" y="{py + 14}" font-family="Arial" font-size="11" fill="#222">{_xml_escape(room_name)}</text>'
        )

    # Items
    for item_name, rect in items.items():
        x, y, w, h = [int(v) for v in rect]
        px = margin + x * cell
        py = margin + 50 + y * cell
        pw = w * cell
        ph = h * cell
        style_group = _item_style_group(item_name)
        fill = ITEM_COLORS.get(style_group, ITEM_COLORS["other"])
        lines.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{fill}" stroke="#333" stroke-width="1"/>')
        label = _item_label(item_name)
        if pw >= 36 and ph >= 16:
            lines.append(
                f'<text x="{px + 3}" y="{py + 12}" font-family="Arial" font-size="10" fill="#111">{_xml_escape(label)}</text>'
            )

    # Boundary
    lines.append(
        f'<rect x="{margin}" y="{margin + 50}" width="{width * cell}" height="{height * cell}" fill="none" stroke="#111" stroke-width="2"/>'
    )

    # Legend
    lx = margin + width * cell + 24
    ly = margin + 60
    lines.append(f'<text x="{lx}" y="{ly - 18}" font-family="Arial" font-size="13" font-weight="bold">Legend</text>')
    legend_rows = [
        ("Beds", ITEM_COLORS["bed"]),
        ("Desk / Exercise", ITEM_COLORS["desk"]),
        ("Storage", ITEM_COLORS["storage"]),
        ("Mobility", ITEM_COLORS["mobility"]),
        ("Dog", ITEM_COLORS["dog"]),
        ("Guest / Worker", ITEM_COLORS["guest"]),
    ]
    for idx, (label, color) in enumerate(legend_rows):
        y = ly + idx * 22
        lines.append(f'<rect x="{lx}" y="{y}" width="16" height="16" fill="{color}" stroke="#444"/>')
        lines.append(f'<text x="{lx + 24}" y="{y + 12}" font-family="Arial" font-size="11">{_xml_escape(label)}</text>')

    lines.append('</svg>')
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _write_diagrams(payload: Dict[str, object], out_dir: Path) -> List[str]:
    diagrams_dir = out_dir / "sokoban_diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    created: List[str] = []
    md_lines = [
        "# Sokoban Layout Diagrams",
        "",
        "These diagrams visualize feasible layouts discovered in the experiment run.",
        "",
    ]

    for result in payload["results"]:
        layout_type = result["layoutType"]
        md_lines.append(f"## {layout_type.upper()}")
        first = result.get("firstFeasible")
        if first is None:
            md_lines.append("No feasible layout found.")
            md_lines.append("")
            continue

        first_name = f"{layout_type}_first_feasible.svg"
        first_path = diagrams_dir / first_name
        _render_layout_svg(first, f"{layout_type.upper()} first feasible layout", first_path)
        created.append(f"sokoban_diagrams/{first_name}")
        md_lines.append(f"### First feasible layout")
        md_lines.append(f"![{layout_type} first feasible](sokoban_diagrams/{first_name})")
        md_lines.append("")

        for idx, sample in enumerate(result.get("sampleFeasible", []), start=1):
            sample_name = f"{layout_type}_sample_{idx}.svg"
            sample_path = diagrams_dir / sample_name
            _render_layout_svg(sample, f"{layout_type.upper()} sample #{idx}", sample_path)
            created.append(f"sokoban_diagrams/{sample_name}")
            md_lines.append(f"### Sample {idx}")
            md_lines.append(f"![{layout_type} sample {idx}](sokoban_diagrams/{sample_name})")
            md_lines.append("")

    md_path = out_dir / "sokoban_layout_diagrams.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    created.append("sokoban_layout_diagrams.md")
    return created


def _write_outputs(payload: Dict[str, object], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "sokoban_layout_experiments.json"
    md_path = out_dir / "sokoban_layout_experiments.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Sokoban Layout Experiment Report",
        "",
        f"Generated: {payload['generatedAt']}",
        "",
        "## Estimated Space Summary",
        f"- Furniture footprint (sq ft): {payload['spaceSummary']['furnitureFootprintSqft']}",
        f"- Circulation-adjusted baseline (sq ft): {payload['spaceSummary']['circulationAdjustedBaselineSqft']}",
        "",
    ]
    for layout_type, recommendation in payload["spaceSummary"]["layoutRecommendations"].items():
        lines.append(f"### {layout_type.upper()}")
        lines.append(f"- Feasible: {'yes' if recommendation['feasible'] else 'no'}")
        lines.append(f"- Estimated minimum sq ft: {recommendation['estimatedMinimumSqft']}")
        lines.append(f"- Recommendation: {recommendation['recommendation']}")
        lines.append("")

    lines.append("## Rule Failure Signals")
    for result in payload["results"]:
        lines.append(f"### {result['layoutType'].upper()}")
        if not result["failureReasons"]:
            lines.append("- No failures recorded.")
        else:
            for reason, count in sorted(result["failureReasons"].items(), key=lambda kv: (-kv[1], kv[0])):
                lines.append(f"- {reason}: {count}")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Sokoban-style apartment layout experiments.")
    parser.add_argument("--attempts-per-size", type=int, default=140)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--processes",
        type=int,
        default=max(1, (multiprocessing.cpu_count() or 2) - 1),
        help="Worker process count for parallel candidate sweeps (set to 1 for serial mode).",
    )
    parser.add_argument("--write", action="store_true", help="Write JSON/Markdown outputs under outputs/.")
    parser.add_argument(
        "--write-diagrams",
        action="store_true",
        help="Write SVG layout diagrams and a diagram markdown index under outputs/.",
    )
    args = parser.parse_args()

    if args.processes > 1:
        results = [
            _run_layout_type_parallel("1br", args.attempts_per_size, args.seed, args.processes),
            _run_layout_type_parallel("2br", args.attempts_per_size, args.seed + 1, args.processes),
        ]
    else:
        results = [
            _run_layout_type("1br", args.attempts_per_size, args.seed),
            _run_layout_type("2br", args.attempts_per_size, args.seed + 1),
        ]
    summary = _estimate_space_summary(results)
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "assumptions": {
            "gridCellFeet": 1,
            "walkwayTargetFeet": 3,
            "bathroomCount": 1,
            "processes": args.processes,
            "ruleSet": [
                "sex_event_requires_benjamin_and_mother_in_different_rooms",
                "mother_must_have_bathroom_path_during_sex_event",
                "dog_alert_requires_dog_separated_from_entry_and_guest_zone",
                "dog_alert_requires_jane_and_mother_room_separation",
                "mobility_requires_clear_paths_for_cane_walker_and_scooter",
            ],
        },
        "spaceSummary": summary,
        "results": results,
    }

    print(json.dumps(payload, indent=2))

    if args.write:
        root = Path(__file__).resolve().parent.parent
        out_dir = root / "outputs"
        _write_outputs(payload, out_dir)
        if args.write_diagrams:
            payload["diagramArtifacts"] = _write_diagrams(payload, out_dir)
            # Persist diagram artifact references back into JSON output.
            (out_dir / "sokoban_layout_experiments.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(json.dumps(payload, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
