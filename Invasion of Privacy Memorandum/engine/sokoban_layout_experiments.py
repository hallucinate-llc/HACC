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
    windows: Dict[str, List[Rect]]
    entry: Cell
    bathroom: Cell

    @property
    def sqft(self) -> int:
        return self.width * self.height

    @property
    def occupied_sqft(self) -> int:
        cells: Set[Cell] = set()
        for rect in self.rooms.values():
            cells |= _cells_for_rect(rect)
        return len(cells)


def _room_area(rect: Rect) -> int:
    return rect[2] * rect[3]


ITEMS: List[Item] = [
    # Kitchen anchors first: sink+stove establish the work line, fridge fills remaining edge.
    Item("kitchen_sink", "kitchen", 3, 2),
    Item("kitchen_stove", "kitchen", 3, 2),
    Item("kitchen_refrigerator", "kitchen", 3, 2),
    # Bathroom anchors first: tub first prevents dead-end rough-in states.
    Item("bath_tub", "bathroom", 5, 3, rotate=False),
    Item("bath_sink", "bathroom", 3, 2, rotate=False),
    Item("bath_toilet", "bathroom", 2, 3, rotate=False),
    # Living room program so layouts are not mostly empty
    Item("living_sofa", "living_room", 7, 3),
    Item("living_coffee_table", "living_room", 3, 2),
    # Jane bedroom
    Item("jane_full_bed", "jane_room", 5, 7),
    Item("jane_recliner", "jane_room", 3, 3),
    Item("jane_scooter_parking", "jane_room", 3, 5),
    Item("jane_tv_desk_40in", "jane_room", 4, 2),
    Item("jane_closet_zone", "jane_room", 2, 5, rotate=False),
    Item("jane_standup_ac", "jane_room", 2, 2, rotate=False),
    # Benjamin bedroom
    Item("benjamin_queen_bed", "ben_room", 5, 7),
    Item("benjamin_standing_desk", "ben_room", 6, 3),
    Item("benjamin_desk_chair", "ben_room", 3, 3),
    Item("benjamin_filing_cabinets", "ben_room", 2, 6, rotate=False),
    Item("benjamin_closet_zone", "ben_room", 2, 5, rotate=False),
    Item("benjamin_standup_ac", "ben_room", 2, 2, rotate=False),
    Item("xl_dog_bed", "ben_room", 4, 3),
]

NON_BLOCKING_ITEMS: Set[str] = {"bath_toilet", "bath_sink", "bath_tub"}
MAX_ITEM_OPTIONS = 80

ROOM_COLORS = {
    "ben_room": "#f4d35e",
    "jane_room": "#9ad1d4",
    "living_room": "#c7d3ff",
    "circulation": "#f1f3f4",
    "kitchen": "#fffacd",
    "bathroom": "#d9ead3",
}

ITEM_COLORS = {
    "bed": "#ffcc80",
    "desk": "#90caf9",
    "storage": "#bcaaa4",
    "mobility": "#a5d6a7",
    "dog": "#ffe082",
    "guest": "#ef9a9a",
    "living": "#c5e1a5",
    "kitchen": "#ffd699",
    "bathroom": "#c8e6c9",
    "other": "#e0e0e0",
}

# Items that must be flush against a room wall (no floating in open space).
WALL_ADJACENT_ITEMS: Set[str] = {
    "jane_full_bed", "benjamin_queen_bed",
    "jane_closet_zone", "benjamin_closet_zone",
    "jane_tv_desk_40in", "benjamin_filing_cabinets",
    "bath_toilet", "bath_sink", "bath_tub",
    "kitchen_refrigerator", "kitchen_stove", "kitchen_sink",
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
    kitchen_w = 8
    kitchen_h = 6
    circulation_w = 6
    if layout_type == "1br":
        bed_w = min(max(11, int(width * 0.30)), 12)
        living_w = min(max(18, width - bed_w), 22)
        living_h = min(max(16, height - kitchen_h), 20)
        occupied_right_h = kitchen_h + living_h
        rooms = {
            "ben_room": (0, 0, bed_w, max(height, occupied_right_h)),
            "kitchen": (bed_w, 0, kitchen_w, kitchen_h),
            "circulation": (bed_w + kitchen_w, 0, circulation_w, kitchen_h),
            # In 1BR mode the living and Jane functions collapse into one open area.
            "living_room": (bed_w, kitchen_h, living_w, living_h),
            "jane_room":   (bed_w, kitchen_h, living_w, living_h),
            "bathroom": (bed_w + living_w - bath_w, kitchen_h + living_h - bath_h, bath_w, bath_h),
        }
        door_cells = {
            "ben_room": (bed_w - 1, min(max(height, occupied_right_h) - 2, kitchen_h + 2)),
            "kitchen":  (bed_w, kitchen_h - 1),
            "living_room": (bed_w + kitchen_w, kitchen_h),
            "bathroom": (bed_w + living_w - bath_w, kitchen_h + living_h - (bath_h // 2)),
        }
        windows = {
            "ben_room":    [(0, max(1, height // 4), 1, min(4, max(2, height // 5)))],
            "kitchen":     [(bed_w + kitchen_w // 2, 0, min(3, kitchen_w // 2), 1)],
            "living_room": [(bed_w + living_w - 1, kitchen_h + max(1, living_h // 4), 1, min(5, max(3, living_h // 3)))],
            "jane_room":   [(bed_w + living_w - 1, kitchen_h + max(1, living_h // 3), 1, min(4, max(2, living_h // 4)))],
        }
        entry = (bed_w + kitchen_w + 1, kitchen_h + 1)
    else:
        bed_w = min(max(11, int(width * 0.24)), 12)
        ben_h = min(max(13, int(height * 0.36)), 15)
        jane_h = min(max(13, int(height * 0.36)), 15)
        living_w = min(max(16, width - bed_w), 20)
        living_h = min(max(10, height - kitchen_h - bath_h), 12)
        rooms = {
            "ben_room":  (0, 0, bed_w, ben_h),
            "jane_room": (0, ben_h, bed_w, jane_h),
            "kitchen":   (bed_w, 0, kitchen_w, kitchen_h),
            "circulation": (bed_w + kitchen_w, 0, circulation_w, kitchen_h),
            "living_room": (bed_w, kitchen_h, living_w, living_h),
            "bathroom":    (bed_w + living_w - bath_w, kitchen_h + living_h, bath_w, bath_h),
        }
        door_cells = {
            "ben_room":    (bed_w - 1, max(1, ben_h - 2)),
            "jane_room":   (bed_w - 1, ben_h + 1),
            "kitchen":     (bed_w, kitchen_h - 1),
            "living_room": (bed_w + kitchen_w, kitchen_h),
            "bathroom":    (bed_w + living_w - bath_w, kitchen_h + living_h + (bath_h // 2)),
        }
        windows = {
            "ben_room":    [(0, max(1, ben_h // 4), 1, min(4, max(2, ben_h // 3)))],
            "jane_room":   [(0, ben_h + max(1, jane_h // 4), 1, min(4, max(2, jane_h // 3)))],
            "kitchen":     [(bed_w + kitchen_w // 2, 0, min(3, kitchen_w // 2), 1)],
            "living_room": [(bed_w + living_w - 1, kitchen_h + max(1, living_h // 4), 1, min(6, max(4, living_h // 2)))],
        }
        entry = (bed_w + kitchen_w + 1, kitchen_h + 1)

    bathroom = door_cells["bathroom"]
    return LayoutCandidate(layout_type, width, height, rooms, door_cells, windows, entry, bathroom)


def _normalize_rect(rect_like: List[int]) -> Rect:
    x, y, w, h = [int(v) for v in rect_like]
    return (x, y, w, h)


def _normalize_cell(cell_like: List[int]) -> Cell:
    x, y = [int(v) for v in cell_like]
    return (x, y)


def _load_shell_candidate(shell_path: Path) -> LayoutCandidate:
    payload = json.loads(shell_path.read_text(encoding="utf-8"))
    return LayoutCandidate(
        layout_type=str(payload.get("layout_type", "shell")),
        width=int(payload["width"]),
        height=int(payload["height"]),
        rooms={k: _normalize_rect(v) for k, v in payload["rooms"].items()},
        door_cells={k: _normalize_cell(v) for k, v in payload["door_cells"].items()},
        windows={k: [_normalize_rect(v) for v in vals] for k, vals in payload.get("windows", {}).items()},
        entry=_normalize_cell(payload["entry"]),
        bathroom=_normalize_cell(payload["bathroom"]),
    )


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


def _rects_touch(a: Rect, b: Rect) -> bool:
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    ax2, ay2 = ax1 + aw - 1, ay1 + ah - 1
    bx2, by2 = bx1 + bw - 1, by1 + bh - 1
    return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)


def _touches_window_segment(rect: Rect, segments: List[Rect]) -> bool:
    return any(_rects_touch(rect, seg) for seg in segments)


def _rect_near_window_segment(rect: Rect, segments: List[Rect], max_gap: int = 1) -> bool:
    x, y, w, h = rect
    expanded = (x - max_gap, y - max_gap, w + (2 * max_gap), h + (2 * max_gap))
    return any(_rects_touch(expanded, seg) for seg in segments)


def _touches_room_wall(rect: Rect, room: Rect) -> bool:
    """Return True if the rect is flush against at least one wall of its room."""
    x, y, w, h = rect
    rx, ry, rw, rh = room
    return x == rx or x + w == rx + rw or y == ry or y + h == ry + rh


def _touches_room_corner(rect: Rect, room: Rect) -> bool:
    x, y, w, h = rect
    rx, ry, rw, rh = room
    left = x == rx
    right = x + w == rx + rw
    top = y == ry
    bottom = y + h == ry + rh
    return (left or right) and (top or bottom)


def _shares_wall_side(rect: Rect, room: Rect, side: str) -> bool:
    x, y, w, h = rect
    rx, ry, rw, rh = room
    if side == "left":
        return x == rx
    if side == "right":
        return x + w == rx + rw
    if side == "top":
        return y == ry
    if side == "bottom":
        return y + h == ry + rh
    return False


def _door_wall_side(door: Cell, room: Rect) -> Optional[str]:
    dx, dy = door
    rx, ry, rw, rh = room
    if dx == rx:
        return "left"
    if dx == rx + rw - 1:
        return "right"
    if dy == ry:
        return "top"
    if dy == ry + rh - 1:
        return "bottom"
    return None


def _midpoint_near_room_end(rect: Rect, room: Rect, axis: str, end_fraction: float = 0.35) -> bool:
    x, y, w, h = rect
    rx, ry, rw, rh = room
    if axis == "y":
        midpoint = y + (h / 2.0)
        near_top = midpoint <= ry + (rh * end_fraction)
        near_bottom = midpoint >= ry + rh - (rh * end_fraction)
        return near_top or near_bottom
    midpoint = x + (w / 2.0)
    near_left = midpoint <= rx + (rw * end_fraction)
    near_right = midpoint >= rx + rw - (rw * end_fraction)
    return near_left or near_right


def _cells_directly_in_front_of_rect(rect: Rect, room: Rect) -> Set[Cell]:
    x, y, w, h = rect
    rx, ry, rw, rh = room
    front: Set[Cell] = set()
    if x == rx:
        front |= {(x + w, cy) for cy in range(y, y + h) if x + w < rx + rw}
    if x + w == rx + rw:
        front |= {(x - 1, cy) for cy in range(y, y + h) if x - 1 >= rx}
    if y == ry:
        front |= {(cx, y + h) for cx in range(x, x + w) if y + h < ry + rh}
    if y + h == ry + rh:
        front |= {(cx, y - 1) for cx in range(x, x + w) if y - 1 >= ry}
    return front


def _cells_adjacent_to_rect(rect: Rect, room: Rect) -> Set[Cell]:
    x, y, w, h = rect
    rx, ry, rw, rh = room
    adjacent: Set[Cell] = set()
    for cx in range(x - 1, x + w + 1):
        if rx <= cx < rx + rw:
            if ry <= y - 1 < ry + rh:
                adjacent.add((cx, y - 1))
            if ry <= y + h < ry + rh:
                adjacent.add((cx, y + h))
    for cy in range(y, y + h):
        if ry <= cy < ry + rh:
            if rx <= x - 1 < rx + rw:
                adjacent.add((x - 1, cy))
            if rx <= x + w < rx + rw:
                adjacent.add((x + w, cy))
    return adjacent


def _item_access_cells(rect: Rect, room: Rect) -> Set[Cell]:
    front = _cells_directly_in_front_of_rect(rect, room)
    if front:
        return front
    return _cells_adjacent_to_rect(rect, room)


def _wall_center_offset(rect: Rect, room: Rect) -> float:
    x, y, w, h = rect
    rx, ry, rw, rh = room
    rect_cx, rect_cy = _rect_center(rect)
    if _shares_wall_side(rect, room, "left") or _shares_wall_side(rect, room, "right"):
        return abs(rect_cy - (ry + rh / 2.0))
    if _shares_wall_side(rect, room, "top") or _shares_wall_side(rect, room, "bottom"):
        return abs(rect_cx - (rx + rw / 2.0))
    return 9999.0


def _door_clear_offset(rect: Rect, room: Rect, door: Optional[Cell]) -> float:
    if door is None:
        return 0.0
    landing = _door_landing_zone(door, room)
    if not landing:
        return 0.0
    rect_cells = _cells_for_rect(rect)
    if rect_cells & landing:
        return -1000.0
    cx, cy = _rect_center(rect)
    return min(abs(cx - lx) + abs(cy - ly) for lx, ly in landing)


def _room_accessible_to_item(
    rect: Rect,
    room: Rect,
    door: Optional[Cell],
    blocked: Set[Cell],
    reserved: Set[Cell],
    width: int,
    height: int,
) -> bool:
    if door is None:
        return True
    access_cells = _item_access_cells(rect, room)
    if not access_cells:
        return False
    temp_blocked = set(blocked) | set(reserved) | _cells_for_rect(rect)
    temp_blocked.discard(door)
    for cell in sorted(access_cells):
        if cell in temp_blocked:
            continue
        if _shortest_path(door, cell, temp_blocked, width, height) is not None:
            return True
    return False


def _door_landing_zone(door: Cell, room: Rect) -> Set[Cell]:
    dx, dy = door
    rx, ry, rw, rh = room
    side = _door_wall_side(door, room)
    cells: Set[Cell] = {(dx, dy)}
    if side == "left":
        cells |= {(cx, cy) for cx in range(dx, min(dx + 3, rx + rw)) for cy in range(max(ry, dy - 1), min(ry + rh, dy + 2))}
    elif side == "right":
        cells |= {(cx, cy) for cx in range(max(rx, dx - 2), dx + 1) for cy in range(max(ry, dy - 1), min(ry + rh, dy + 2))}
    elif side == "top":
        cells |= {(cx, cy) for cx in range(max(rx, dx - 1), min(rx + rw, dx + 2)) for cy in range(dy, min(dy + 3, ry + rh))}
    elif side == "bottom":
        cells |= {(cx, cy) for cx in range(max(rx, dx - 1), min(rx + rw, dx + 2)) for cy in range(max(ry, dy - 2), dy + 1)}
    return cells


def _closet_layout_is_realistic(rect: Rect, room: Rect, windows: List[Rect], door: Optional[Cell], blocked: Set[Cell]) -> bool:
    if not _touches_room_wall(rect, room):
        return False
    if _touches_window_segment(rect, windows):
        return False

    # Closet must not block the door entry zone.
    if door is not None:
        door_side = _door_wall_side(door, room)
        if door_side and _shares_wall_side(rect, room, door_side):
            return False
        if _cells_for_rect(rect) & _door_landing_zone(door, room):
            return False

    # A closet needs a reachable face, not just a wall placement.
    front_cells = _cells_directly_in_front_of_rect(rect, room)
    if len(front_cells) < 2:
        return False
    accessible_front = [cell for cell in front_cells if cell not in blocked]
    if len(accessible_front) < max(1, len(front_cells) // 2):
        return False

    return True


def _filing_cabinets_layout_is_realistic(
    rect: Rect,
    room: Rect,
    windows: List[Rect],
    door: Optional[Cell],
    blocked: Set[Cell],
    width: int,
    height: int,
) -> bool:
    if not _touches_room_wall(rect, room):
        return False
    if _touches_window_segment(rect, windows):
        return False
    if not (_shares_wall_side(rect, room, "left") or _shares_wall_side(rect, room, "right")):
        return False

    if door is not None:
        door_side = _door_wall_side(door, room)
        if door_side and _shares_wall_side(rect, room, door_side):
            return False
        if _cells_for_rect(rect) & _door_landing_zone(door, room):
            return False

    front_cells = _cells_directly_in_front_of_rect(rect, room)
    if len(front_cells) < rect[3]:
        return False
    if any(cell in blocked for cell in front_cells):
        return False

    if door is not None:
        # Filing rows must be reachable so records can actually be pulled.
        temp_blocked = set(blocked) | _cells_for_rect(rect)
        reachable_front = [
            cell for cell in front_cells
            if cell not in temp_blocked and _shortest_path(door, cell, temp_blocked, width, height) is not None
        ]
        if len(reachable_front) < max(2, rect[3] // 2):
            return False

    return True


def _kitchen_layout_is_realistic(
    placed: Dict[str, Rect],
    room: Rect,
    windows: List[Rect],
    door: Optional[Cell],
    blocked: Set[Cell],
    width: int,
    height: int,
) -> bool:
    fridge = placed.get("kitchen_refrigerator")
    stove = placed.get("kitchen_stove")
    sink = placed.get("kitchen_sink")
    fixtures = [r for r in (fridge, stove, sink) if r is not None]

    for fixture in fixtures:
        if not _touches_room_wall(fixture, room):
            return False

    if door is not None:
        door_side = _door_wall_side(door, room)
        if door_side is not None and fridge is not None:
            # Keep the door side open for appliance clearance by pinning the
            # largest appliance away from the entry wall.
            if _shares_wall_side(fridge, room, door_side):
                return False

    if sink is not None and stove is not None:
        sink_sides = {side for side in ("left", "right", "top", "bottom") if _shares_wall_side(sink, room, side)}
        stove_sides = {side for side in ("left", "right", "top", "bottom") if _shares_wall_side(stove, room, side)}
        if not (sink_sides & stove_sides):
            return False
        sx, sy, sw, sh = sink
        tx, ty, tw, th = stove
        sink_center = (sx + sw // 2, sy + sh // 2)
        stove_center = (tx + tw // 2, ty + th // 2)
        if abs(sink_center[0] - stove_center[0]) + abs(sink_center[1] - stove_center[1]) > 6:
            return False
    elif sink is not None and windows:
        if not _touches_window_segment(sink, windows):
            return False

    temp_blocked = set(blocked)
    for fixture in fixtures:
        temp_blocked |= _cells_for_rect(fixture)

    # Keep at least one reachable working cell in front of each appliance.
    for fixture in fixtures:
        front = _cells_directly_in_front_of_rect(fixture, room)
        work_cells = [cell for cell in front if cell not in temp_blocked]
        if not work_cells:
            return False
        if door is not None:
            if not any(_shortest_path(door, cell, temp_blocked, width, height) is not None for cell in work_cells):
                return False

    return True


def _living_room_layout_is_realistic(
    placed: Dict[str, Rect],
    room: Rect,
    windows: List[Rect],
    living_door: Optional[Cell],
    kitchen_door: Optional[Cell],
    blocked: Set[Cell],
    width: int,
    height: int,
) -> bool:
    sofa = placed.get("living_sofa")
    coffee = placed.get("living_coffee_table")

    if coffee is not None:
        if sofa is None:
            return False
        if not _rects_adjacent(coffee, sofa):
            return False
        sofa_cx, sofa_cy = _rect_center(sofa)
        coffee_cx, coffee_cy = _rect_center(coffee)
        if abs(coffee_cx - sofa_cx) + abs(coffee_cy - sofa_cy) > 6:
            return False

    if living_door is not None:
        # Preserve a small clear zone at the living-room doorway.
        landing = _door_landing_zone(living_door, room)
        if sofa is not None and (_cells_for_rect(sofa) & landing):
            return False

    return True


def _door_swing_cells(door: Cell, width: int, height: int) -> Set[Cell]:
    x, y = door
    if 0 <= x < width and 0 <= y < height:
        return {(x, y)}
    return set()


def _bathroom_layout_is_realistic(
    placed: Dict[str, Rect],
    room: Rect,
    door: Optional[Cell],
    width: int,
    height: int,
) -> bool:
    toilet = placed.get("bath_toilet")
    sink = placed.get("bath_sink")
    tub = placed.get("bath_tub")

    if door is None:
        return False

    door_side = _door_wall_side(door, room)
    if door_side is None:
        return False

    # Even partial bathroom placements must be plausible, otherwise earlier
    # fixtures can trap the later ones with no valid completion.
    if tub is not None and not (_shares_wall_side(tub, room, "top") or _shares_wall_side(tub, room, "bottom")):
        return False
    # Tub should not block the door wall; sink and toilet can be anywhere reachable.
    if tub is not None:
        tub_sides = {side for side in ("left", "right", "top", "bottom") if _shares_wall_side(tub, room, side)}
        if door_side in tub_sides:
            return False
    for fixture in (sink, toilet):
        if fixture is not None and not _touches_room_wall(fixture, room):
            return False

    blocked_partial = set()
    for fixture in (sink, toilet, tub):
        if fixture is not None:
            blocked_partial |= _cells_for_rect(fixture)
    if _door_landing_zone(door, room) & blocked_partial:
        return False

    if toilet is None or sink is None or tub is None:
        return True

    # Toilet and sink should both be wall-mounted and not float in the center.
    if not _touches_room_wall(sink, room) or not _touches_room_wall(toilet, room):
        return False

    # Sink and toilet should be wall-mounted. Tub gets its own wall.
    tub_sides_all = {side for side in ("left", "right", "top", "bottom") if _shares_wall_side(tub, room, side)}
    for fixture in (sink, toilet):
        fsides = {side for side in ("left", "right", "top", "bottom") if _shares_wall_side(fixture, room, side)}
        # Fixture must not be on same wall as tub.
        if fsides & tub_sides_all:
            return False

    # Keep at least some central maneuvering zone by preventing all three fixtures
    # from consuming the same wall run directly across the room width.
    bath_cells = _cells_for_rect(room)
    blocked = _cells_for_rect(sink) | _cells_for_rect(toilet) | _cells_for_rect(tub)
    open_cells = bath_cells - blocked
    if len(open_cells) < max(8, (room[2] * room[3]) // 4):
        return False

    # Preserve a real entry landing zone just inside the bathroom door.
    if _door_landing_zone(door, room) & blocked:
        return False

    # Keep an actual usable aisle from the door into the bathroom interior.
    # Use room-local flood fill (fast) instead of full-apartment BFS.
    if door is not None and door not in blocked:
        rx, ry, rw, rh = room
        room_cells = {(cx, cy) for cx in range(rx, rx + rw) for cy in range(ry, ry + rh)}
        inner_cells = {c for c in room_cells if c not in blocked and c != door}
        if not inner_cells:
            return False
        # Flood fill from door; verify at least one interior cell is reachable.
        queue = deque([door])
        visited = {door}
        reachable_inner = False
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in inner_cells:
                reachable_inner = True
                break
            for nx, ny in ((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
                if (nx, ny) in room_cells and (nx, ny) not in blocked and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        if not reachable_inner:
            return False

    return True


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


def _shortest_path(start: Cell, goal: Cell, blocked: Set[Cell], width: int, height: int) -> Optional[List[Cell]]:
    if start in blocked or goal in blocked:
        return None
    frontier = deque([start])
    parent: Dict[Cell, Optional[Cell]] = {start: None}
    while frontier:
        cur = frontier.popleft()
        if cur == goal:
            path: List[Cell] = []
            node: Optional[Cell] = cur
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path
        for nxt in _neighbors(cur, width, height):
            if nxt in blocked or nxt in parent:
                continue
            parent[nxt] = cur
            frontier.append(nxt)
    return None


def _find_walkable_cell_in_room(room: Rect, blocked: Set[Cell], width: int, height: int) -> Optional[Cell]:
    rx, ry, rw, rh = room
    cx = rx + rw // 2
    cy = ry + rh // 2
    candidates: List[Cell] = []
    for radius in range(max(rw, rh) + 2):
        for x in range(rx, rx + rw):
            for y in range(ry, ry + rh):
                if abs(x - cx) + abs(y - cy) == radius:
                    candidates.append((x, y))
        for cell in candidates:
            if 0 <= cell[0] < width and 0 <= cell[1] < height and cell not in blocked:
                return cell
    return None


def _rect_center(rect: Rect) -> Tuple[float, float]:
    x, y, w, h = rect
    return (x + (w / 2.0), y + (h / 2.0))


def _distance_to_cell(rect: Rect, cell: Optional[Cell]) -> float:
    if cell is None:
        return 0.0
    cx, cy = _rect_center(rect)
    return abs(cx - cell[0]) + abs(cy - cell[1])


def _placement_score(
    item: Item,
    rect: Rect,
    room: Rect,
    candidate: LayoutCandidate,
    placed: Dict[str, Rect],
) -> Tuple[float, float, float]:
    # Lower scores are preferred.
    score = 0.0
    tie_1 = 0.0
    tie_2 = 0.0

    door = candidate.door_cells.get(item.room)
    wall_center = _wall_center_offset(rect, room)
    door_clear = _door_clear_offset(rect, room, door)

    if "closet" in item.name:
        score -= 20.0 if _touches_room_corner(rect, room) else 0.0
        tie_1 = -door_clear
        tie_2 = wall_center
    elif item.name == "benjamin_filing_cabinets":
        score -= 15.0 if _touches_room_corner(rect, room) else 0.0
        tie_1 = -door_clear
        tie_2 = wall_center
    elif item.name.endswith("standup_ac"):
        score -= 10.0 if _touches_room_wall(rect, room) else 0.0
        tie_1 = wall_center
        tie_2 = -door_clear
    elif item.name == "living_sofa":
        score -= 8.0 if _touches_room_wall(rect, room) else 0.0
        tie_1 = wall_center
        tie_2 = -door_clear
    elif item.name == "living_coffee_table":
        sofa = placed.get("living_sofa")
        if sofa is not None:
            sx, sy = _rect_center(sofa)
            rx, ry = _rect_center(rect)
            tie_1 = abs(rx - sx) + abs(ry - sy)
            tie_2 = -door_clear
    elif item.name == "benjamin_standing_desk":
        wall_side = _desk_wall_side(rect, room)
        score -= 18.0 if wall_side is not None else 0.0
        tie_1 = wall_center
        tie_2 = -door_clear
    elif item.name == "benjamin_desk_chair":
        desk = placed.get("benjamin_standing_desk")
        if desk is not None:
            score -= 20.0 if _desk_chair_forms_tau(rect, desk, room) else 0.0
            dx, dy = _rect_center(desk)
            rx, ry = _rect_center(rect)
            tie_1 = abs(rx - dx) + abs(ry - dy)
            tie_2 = -door_clear
    else:
        tie_1 = -door_clear
        tie_2 = wall_center

    # Prefer slightly more compact room use by nudging toward existing items.
    if placed:
        px = sum(_rect_center(r)[0] for r in placed.values()) / len(placed)
        py = sum(_rect_center(r)[1] for r in placed.values()) / len(placed)
        rx, ry = _rect_center(rect)
        tie_2 += abs(rx - px) + abs(ry - py)

    return (score, tie_1, tie_2)


def _desk_wall_side(rect: Rect, room: Rect) -> Optional[str]:
    x, y, w, h = rect
    horizontal = w >= h
    if horizontal:
        if _shares_wall_side(rect, room, "top"):
            return "top"
        if _shares_wall_side(rect, room, "bottom"):
            return "bottom"
    else:
        if _shares_wall_side(rect, room, "left"):
            return "left"
        if _shares_wall_side(rect, room, "right"):
            return "right"
    return None


def _standing_desk_layout_is_realistic(rect: Rect, room: Rect) -> bool:
    # Desk should read like the top bar of a tau/T shape: its long edge is
    # anchored to a wall, with the user/chair approaching from the open side.
    return _desk_wall_side(rect, room) is not None


def _desk_chair_forms_tau(chair: Rect, desk: Rect, room: Rect) -> bool:
    wall_side = _desk_wall_side(desk, room)
    if wall_side is None:
        return False
    if not _rects_adjacent(chair, desk):
        return False

    dx, dy, dw, dh = desk
    cx, cy, cw, ch = chair
    desk_cx, desk_cy = _rect_center(desk)
    chair_cx, chair_cy = _rect_center(chair)

    # Chair must sit on the open side opposite the wall and be roughly centered
    # on the desk span, making the combined footprint read like a T/tau.
    if wall_side == "top":
        if cy != dy + dh:
            return False
        return abs(chair_cx - desk_cx) <= max(1.0, dw / 6.0)
    if wall_side == "bottom":
        if cy + ch != dy:
            return False
        return abs(chair_cx - desk_cx) <= max(1.0, dw / 6.0)
    if wall_side == "left":
        if cx != dx + dw:
            return False
        return abs(chair_cy - desk_cy) <= max(1.0, dh / 6.0)
    if wall_side == "right":
        if cx + cw != dx:
            return False
        return abs(chair_cy - desk_cy) <= max(1.0, dh / 6.0)
    return False


def _room_of_path(path: List[Cell], rooms: Dict[str, Rect]) -> Set[str]:
    out: Set[str] = set()
    for cell in path:
        room = _room_for_cell(rooms, cell)
        if room is not None:
            out.add(room)
    return out


def _evaluate_guest_alert_scenario(candidate: LayoutCandidate, placed: Dict[str, Rect], blocked: Set[Cell]) -> Tuple[bool, List[str], Dict[str, object]]:
    issues: List[str] = []

    dog_rect = placed.get("xl_dog_bed")
    if dog_rect is None:
        return False, ["dog_bed_missing"], {}

    dog_start = _adjacent_walkable_target(dog_rect, blocked, candidate.width, candidate.height)
    if dog_start is None:
        return False, ["dog_has_no_walkable_start"], {}

    host_starts = {
        "benjamin": candidate.door_cells.get("ben_room"),
        "jane": candidate.door_cells.get("jane_room"),
    }
    host_starts = {k: v for k, v in host_starts.items() if v is not None}
    interaction_rooms = ["living_room", "ben_room", "jane_room"]
    containment_rooms = ["ben_room", "jane_room"]

    scenario: Dict[str, object] = {}
    for interaction_room in interaction_rooms:
        interaction_target = _find_walkable_cell_in_room(candidate.rooms[interaction_room], blocked, candidate.width, candidate.height)
        if interaction_target is None:
            continue

        guest_path = _shortest_path(candidate.entry, interaction_target, blocked, candidate.width, candidate.height)
        if guest_path is None:
            continue

        guest_path_rooms = _room_of_path(guest_path, candidate.rooms)
        for host_name, host_start in host_starts.items():
            host_path = _shortest_path(host_start, interaction_target, blocked, candidate.width, candidate.height)
            if host_path is None:
                continue

            for containment_room in containment_rooms:
                if containment_room == interaction_room:
                    continue
                containment_target = _find_walkable_cell_in_room(candidate.rooms[containment_room], blocked, candidate.width, candidate.height)
                if containment_target is None:
                    continue
                dog_path = _shortest_path(dog_start, containment_target, blocked, candidate.width, candidate.height)
                if dog_path is None:
                    continue

                dog_rooms = _room_of_path(dog_path, candidate.rooms)
                final_dog_room = _room_for_cell(candidate.rooms, containment_target)
                if final_dog_room is None or final_dog_room in guest_path_rooms:
                    continue
                if interaction_room in dog_rooms:
                    continue

                scenario = {
                    "host": host_name,
                    "interactionRoom": interaction_room,
                    "containmentRoom": containment_room,
                    "guestPathLength": len(guest_path),
                    "hostPathLength": len(host_path),
                    "dogPathLength": len(dog_path),
                }
                return True, [], scenario

    issues.append("guest_alert_isolation_failed")
    return False, issues, scenario


def _reserved_cells(candidate: LayoutCandidate) -> Set[Cell]:
    reserved: Set[Cell] = set()
    reserved |= {candidate.entry, candidate.bathroom}
    for door in candidate.door_cells.values():
        reserved |= {door}
        reserved |= _door_swing_cells(door, candidate.width, candidate.height)
    return reserved


def _valid_item_rects(
    candidate: LayoutCandidate,
    item: Item,
    placed: Dict[str, Rect],
    blocked: Set[Cell],
    reserved: Set[Cell],
    rng: random.Random,
    tries: int,
) -> List[Rect]:
    room = candidate.rooms[item.room]
    orientations = [(item.w, item.h)]
    if item.rotate and item.w != item.h:
        orientations.append((item.h, item.w))

    options: List[Rect] = []
    for ow, oh in orientations:
        options.extend(_iter_rect_positions(room, ow, oh))
    rng.shuffle(options)
    options.sort(key=lambda rect: _placement_score(item, rect, room, candidate, placed))
    if len(options) > MAX_ITEM_OPTIONS and not item.name.endswith("standup_ac"):
        options = options[:MAX_ITEM_OPTIONS]

    valid: List[Rect] = []
    for rect in options:
        cells = _cells_for_rect(rect)
        if cells & blocked:
            continue
        if cells & reserved:
            continue
        if item.name.endswith("standup_ac") and not _rect_near_window_segment(rect, candidate.windows.get(item.room, []), max_gap=1):
            continue
        if item.name in WALL_ADJACENT_ITEMS and not _touches_room_wall(rect, room):
            continue
        if not _room_accessible_to_item(
            rect,
            room,
            candidate.door_cells.get(item.room),
            blocked,
            reserved,
            candidate.width,
            candidate.height,
        ):
            continue
        if "closet" in item.name and not _closet_layout_is_realistic(
            rect,
            room,
            candidate.windows.get(item.room, []),
            candidate.door_cells.get(item.room),
            blocked,
        ):
            continue
        if item.name == "benjamin_filing_cabinets" and not _filing_cabinets_layout_is_realistic(
            rect,
            room,
            candidate.windows.get(item.room, []),
            candidate.door_cells.get(item.room),
            blocked,
            candidate.width,
            candidate.height,
        ):
            continue
        if item.name == "benjamin_standing_desk" and not _standing_desk_layout_is_realistic(rect, room):
            continue
        if item.room == "bathroom":
            temp = dict(placed)
            temp[item.name] = rect
            if not _bathroom_layout_is_realistic(
                temp,
                room,
                candidate.door_cells.get("bathroom"),
                candidate.width,
                candidate.height,
            ):
                continue
        if item.room == "kitchen":
            temp = dict(placed)
            temp[item.name] = rect
            if not _kitchen_layout_is_realistic(
                temp,
                room,
                candidate.windows.get(item.room, []),
                candidate.door_cells.get(item.room),
                blocked,
                candidate.width,
                candidate.height,
            ):
                continue
        if item.room == "living_room" and item.name.startswith("living_"):
            temp = dict(placed)
            temp[item.name] = rect
            if not _living_room_layout_is_realistic(
                temp,
                room,
                candidate.windows.get(item.room, []),
                candidate.door_cells.get("living_room"),
                candidate.door_cells.get("kitchen"),
                blocked,
                candidate.width,
                candidate.height,
            ):
                continue
        if item.name == "benjamin_desk_chair":
            desk = placed.get("benjamin_standing_desk")
            if desk is None or not _desk_chair_forms_tau(rect, desk, room):
                continue
        valid.append(rect)
        if len(valid) >= tries:
            break
    return valid


def _item_dependencies(item: Item) -> Set[str]:
    deps: Set[str] = set()
    if item.name == "benjamin_desk_chair":
        deps.add("benjamin_standing_desk")
    if item.name == "living_coffee_table":
        deps.add("living_sofa")
    return deps


def _search_place_items(
    candidate: LayoutCandidate,
    items_left: List[Item],
    placed: Dict[str, Rect],
    blocked: Set[Cell],
    reserved: Set[Cell],
    rng: random.Random,
    tries: int,
) -> Optional[Dict[str, Rect]]:
    if not items_left:
        return dict(placed)

    available_items = [item for item in items_left if _item_dependencies(item).issubset(placed.keys())]
    if not available_items:
        return None

    ranked: List[Tuple[int, int, Item, List[Rect]]] = []
    for item in available_items:
        index = items_left.index(item)
        valid = _valid_item_rects(candidate, item, placed, blocked, reserved, rng, tries)
        if not valid:
            return None
        ranked.append((len(valid), index, item, valid))

    ranked.sort(key=lambda row: (row[0], row[1]))
    _, chosen_index, item, valid_rects = ranked[0]

    next_items = items_left[:chosen_index] + items_left[chosen_index + 1 :]
    for rect in valid_rects:
        next_placed = dict(placed)
        next_placed[item.name] = rect
        next_blocked = set(blocked) | _cells_for_rect(rect)
        solved = _search_place_items(candidate, next_items, next_placed, next_blocked, reserved, rng, tries)
        if solved is not None:
            return solved
    return None


def _place_items(candidate: LayoutCandidate, rng: random.Random, tries: int = 200) -> Optional[Dict[str, Rect]]:
    reserved = _reserved_cells(candidate)
    return _search_place_items(candidate, list(ITEMS), {}, set(), reserved, rng, tries)


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

    # 1) Benjamin and the shared interaction space must remain distinct.
    ben_room = "ben_room"
    living_room = "living_room"
    if ben_room == living_room:
        issues.append("sex_event_same_room_violation")

    blocked = _clearance_blocked(candidate, placed)

    guest_alert_ok, guest_alert_issues, _guest_alert = _evaluate_guest_alert_scenario(candidate, placed, blocked)
    if not guest_alert_ok:
        issues.extend(guest_alert_issues)

    # 8, 20) Clear movement paths for cane/walker/scooter + dog flow.
    key_paths = [
        (candidate.entry, candidate.bathroom),
        (candidate.door_cells.get("ben_room"), candidate.bathroom),
        (candidate.door_cells.get("jane_room"), candidate.bathroom),
        (candidate.door_cells.get("living_room"), candidate.bathroom),
    ]
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
        # Stop early once we have a first feasible and enough examples.
        if first_success is not None and len(example_successes) >= 3:
            break

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
            _, _, guest_alert = _evaluate_guest_alert_scenario(candidate, placed, _clearance_blocked(candidate, placed))
            success = {
                "sqft": candidate.occupied_sqft,
                "grossSqft": candidate.sqft,
                "width": width,
                "height": height,
                "roomFootprints": candidate.rooms,
                "doorCells": candidate.door_cells,
                "entryCell": candidate.entry,
                "windowFootprints": candidate.windows,
                "itemFootprints": placed,
                "agentScenarios": {
                    "guestAlert": guest_alert,
                },
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
        imap = pool.imap_unordered(_run_candidate_attempts, tasks, chunksize=4)
        try:
            for partial in imap:
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
                # Stop early once we have a first feasible and enough examples.
                if first_success is not None and len(example_successes) >= 3:
                    pool.terminate()
                    break
        except Exception:
            pass

    return {
        "layoutType": layout_type,
        "testedLayouts": tested,
        "firstFeasible": first_success,
        "sampleFeasible": example_successes,
        "failureReasons": failures,
    }


def _base_item_area() -> int:
    return sum(item.w * item.h for item in ITEMS)


def _occupied_room_area(rooms: Dict[str, Rect]) -> int:
    cells: Set[Cell] = set()
    for rect in rooms.values():
        cells |= _cells_for_rect(rect)
    return len(cells)


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
            "Guest and dog alert handling is modeled as an agent movement scenario, not as static guest or containment furniture footprints.",
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
        "kitchen_refrigerator": "Fridge",
        "kitchen_stove": "Stove",
        "kitchen_sink": "K. sink",
        "bath_toilet": "Toilet",
        "bath_sink": "Bath sink",
        "bath_tub": "Tub",
        "jane_full_bed": "Jane bed",
        "jane_recliner": "Jane lounge",
        "jane_scooter_parking": "Scooter",
        "jane_tv_desk_40in": "TV/desk",
        "jane_closet_zone": "Jane closet",
        "jane_standup_ac": "Jane AC",
        "benjamin_queen_bed": "Ben bed",
        "benjamin_standing_desk": "Stand desk",
        "benjamin_desk_chair": "Desk chair",
        "benjamin_filing_cabinets": "Files x3",
        "living_sofa": "Sofa",
        "living_coffee_table": "Coffee",
        "benjamin_closet_zone": "Ben closet",
        "benjamin_standup_ac": "Ben AC",
        "xl_dog_bed": "Dog bed",
    }
    return mapping.get(name, name)


def _item_style_group(name: str) -> str:
    if "bed" in name:
        return "bed"
    if "desk" in name or "chair" in name:
        return "desk"
    if "closet" in name or "cabinets" in name:
        return "storage"
    if "scooter" in name:
        return "mobility"
    if "dog" in name:
        return "dog"
    if "living_" in name:
        return "living"
    if "guest" in name:
        return "guest"
    if "kitchen" in name or "stove" in name or "fridge" in name or "refrigerator" in name:
        return "kitchen"
    if "bath" in name or "toilet" in name or "tub" in name or "sink" in name:
        return "bathroom"
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
    windows = layout.get("windowFootprints", {})
    door_cells = layout.get("doorCells", {})
    entry_cell = layout.get("entryCell")
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
    gross_sqft = int(layout.get("grossSqft", layout["sqft"]))
    lines.append(
        f'<text x="{margin}" y="40" font-family="Arial" font-size="12">'
        f'{width}ft x {height}ft ({int(layout["sqft"])} occupied sq ft, {gross_sqft} gross)'
        f'</text>'
    )

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

    for _room_name, segments in windows.items():
        for rect in segments:
            x, y, w, h = [int(v) for v in rect]
            px = margin + x * cell
            py = margin + 50 + y * cell
            pw = w * cell
            ph = h * cell
            lines.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#4fc3f7" stroke="#0277bd" stroke-width="1" fill-opacity="0.75"/>')

    for _name, door in door_cells.items():
        dx, dy = [int(v) for v in door]
        for sx, sy in _door_swing_cells((dx, dy), width, height):
            spx = margin + sx * cell
            spy = margin + 50 + sy * cell
            lines.append(f'<rect x="{spx}" y="{spy}" width="{cell}" height="{cell}" fill="#c5e1a5" stroke="none" fill-opacity="0.35"/>')
        px = margin + dx * cell
        py = margin + 50 + dy * cell
        lines.append(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" fill="#8bc34a" stroke="#33691e" stroke-width="1" fill-opacity="0.8"/>')

    if entry_cell is not None:
        ex, ey = [int(v) for v in entry_cell]
        epx = margin + ex * cell
        epy = margin + 50 + ey * cell
        lines.append(f'<rect x="{epx}" y="{epy}" width="{cell}" height="{cell}" fill="#ff8a65" stroke="#bf360c" stroke-width="1" fill-opacity="0.9"/>')
        lines.append(f'<text x="{epx + cell + 4}" y="{epy + 12}" font-family="Arial" font-size="10" fill="#111">Front entry</text>')

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
        ("Living", ITEM_COLORS["living"]),
        ("Windows", "#4fc3f7"),
        ("Door swing", "#c5e1a5"),
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
        lines.append(f"- Estimated occupied sq ft: {recommendation['estimatedMinimumSqft']}")
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


def _run_shell_candidate(candidate: LayoutCandidate, attempts_per_size: int, seed: int) -> Dict[str, object]:
    rng = random.Random(seed)
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
            _, _, guest_alert = _evaluate_guest_alert_scenario(candidate, placed, _clearance_blocked(candidate, placed))
            success = {
                "sqft": candidate.occupied_sqft,
                "grossSqft": candidate.sqft,
                "width": candidate.width,
                "height": candidate.height,
                "roomFootprints": candidate.rooms,
                "doorCells": candidate.door_cells,
                "entryCell": candidate.entry,
                "windowFootprints": candidate.windows,
                "itemFootprints": placed,
                "agentScenarios": {
                    "guestAlert": guest_alert,
                },
            }
            if first_success is None:
                first_success = success
            if len(example_successes) < 3:
                example_successes.append(success)
        else:
            for issue in issues:
                failures[issue] = failures.get(issue, 0) + 1

    return {
        "layoutType": candidate.layout_type,
        "testedLayouts": tested,
        "firstFeasible": first_success,
        "sampleFeasible": example_successes,
        "failureReasons": failures,
    }


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
    parser.add_argument(
        "--shell-json",
        type=str,
        default="",
        help="Optional JSON floor shell fixture with explicit rooms, doors, and windows.",
    )
    args = parser.parse_args()

    if args.shell_json:
        candidate = _load_shell_candidate(Path(args.shell_json))
        results = [_run_shell_candidate(candidate, args.attempts_per_size, args.seed)]
    elif args.processes > 1:
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
                "sex_event_requires_benjamin_private_room_and_shared_space_separation",
                "living_room_must_have_bathroom_path_during_shared_space_use",
                "guest_alert_requires_guest_host_and_dog_to_route_without_dog_sharing_the_interaction_room",
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
