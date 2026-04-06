#!/usr/bin/env python3
"""Run a real gym-sokoban environment probe and persist a compact report.

This is intentionally separate from ``sokoban_layout_experiments.py``.
That script is a custom apartment-layout simulator with Sokoban-style
constraints. This probe uses an actual Sokoban engine from ``gym-sokoban``.
"""

from __future__ import annotations

import argparse
import json
import random
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


CELL_LABELS = {
    0: "#",  # wall
    1: " ",  # floor
    2: ".",  # target
    3: "*",  # box on target
    4: "$",  # box off target
    5: "@",  # player
}


def _ascii_room(room_state) -> str:
    rows: List[str] = []
    for row in room_state:
        rows.append("".join(CELL_LABELS.get(int(cell), "?") for cell in row))
    return "\n".join(rows)


def _board_counts(room_state) -> Dict[str, int]:
    counts = {"walls": 0, "floor": 0, "targets": 0, "boxes_on_target": 0, "boxes": 0, "player": 0}
    for row in room_state:
        for cell in row:
            value = int(cell)
            if value == 0:
                counts["walls"] += 1
            elif value == 1:
                counts["floor"] += 1
            elif value == 2:
                counts["targets"] += 1
            elif value == 3:
                counts["boxes_on_target"] += 1
            elif value == 4:
                counts["boxes"] += 1
            elif value == 5:
                counts["player"] += 1
    return counts


def run_probe(env_id: str, steps: int, seed: int) -> Dict[str, object]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import gym
        import gym_sokoban  # noqa: F401
        from gym_sokoban.envs.sokoban_env import ACTION_LOOKUP

    random.seed(seed)

    env = gym.make(env_id)
    if hasattr(env, "seed"):
        try:
            env.seed(seed)
        except Exception:
            pass

    observation = env.reset()
    base = env.unwrapped

    rollout: List[Dict[str, object]] = []
    total_reward = 0.0
    done = False

    for step_index in range(steps):
        action = env.action_space.sample()
        out = env.step(action)
        observation, reward, done, info = out
        total_reward += float(reward)
        rollout.append(
            {
                "step": step_index + 1,
                "action": int(action),
                "action_name": ACTION_LOOKUP[int(action)],
                "reward": float(reward),
                "done": bool(done),
                "moved_player": bool(info.get("action.moved_player", False)),
                "moved_box": bool(info.get("action.moved_box", False)),
                "board_ascii": _ascii_room(base.room_state),
            }
        )
        if done:
            break

    tiny = env.render(mode="tiny_rgb_array")
    payload: Dict[str, object] = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "engine": {
            "name": "gym-sokoban",
            "source": "https://github.com/mpSchrader/gym-sokoban",
            "envId": env_id,
        },
        "seed": seed,
        "initialState": {
            "observationShape": list(observation.shape),
            "tinyRenderShape": list(tiny.shape),
            "boardCounts": _board_counts(base.room_state),
            "boardAscii": _ascii_room(base.room_state),
        },
        "actionLookup": {str(k): v for k, v in ACTION_LOOKUP.items()},
        "rollout": rollout,
        "summary": {
            "stepsExecuted": len(rollout),
            "totalReward": total_reward,
            "terminated": bool(done),
            "allBoxesOnTarget": bool(base._check_if_all_boxes_on_target()),
        },
        "comparisonNote": (
            "This artifact is generated from an actual Sokoban environment. "
            "It should be treated separately from sokoban_layout_experiments.py, "
            "which is a custom apartment-layout simulator with Sokoban-style constraints."
        ),
    }
    return payload


def write_outputs(payload: Dict[str, object], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "gym_sokoban_probe.json"
    md_path = out_dir / "gym_sokoban_probe.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Gym Sokoban Probe",
        "",
        f"Generated: {payload['generatedAt']}",
        "",
        f"- Engine: {payload['engine']['name']}",
        f"- Source: {payload['engine']['source']}",
        f"- Environment: {payload['engine']['envId']}",
        f"- Seed: {payload['seed']}",
        f"- Steps executed: {payload['summary']['stepsExecuted']}",
        f"- Total reward: {payload['summary']['totalReward']}",
        f"- Terminated: {'yes' if payload['summary']['terminated'] else 'no'}",
        f"- All boxes on target: {'yes' if payload['summary']['allBoxesOnTarget'] else 'no'}",
        "",
        "## Initial Board",
        "",
        "```text",
        payload["initialState"]["boardAscii"],
        "```",
        "",
        "## Action Lookup",
        "",
    ]

    for action_id, name in payload["actionLookup"].items():
        lines.append(f"- {action_id}: {name}")

    lines.extend(["", "## Rollout", ""])
    for step in payload["rollout"]:
        lines.append(f"### Step {step['step']}")
        lines.append(f"- Action: {step['action']} ({step['action_name']})")
        lines.append(f"- Reward: {step['reward']}")
        lines.append(f"- Moved player: {'yes' if step['moved_player'] else 'no'}")
        lines.append(f"- Moved box: {'yes' if step['moved_box'] else 'no'}")
        lines.append("")
        lines.append("```text")
        lines.append(step["board_ascii"])
        lines.append("```")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real gym-sokoban environment probe.")
    parser.add_argument("--env-id", default="Sokoban-small-v0")
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    payload = run_probe(args.env_id, args.steps, args.seed)
    print(json.dumps(payload, indent=2))

    if args.write:
        out_dir = Path(__file__).resolve().parent.parent / "outputs"
        write_outputs(payload, out_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
