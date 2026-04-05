"""
Regenerate the rendered Title 18 filing artifacts from the shared override context.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

from formal_logic.title18_filing_index import write_title18_filing_index
from formal_logic.title18_final_packet import write_title18_final_packets
from formal_logic.title18_rendered_filings import write_rendered_title18_filings
from formal_logic.title18_service_packet import write_title18_service_packet


def regenerate_title18_packets(merged_order_track: str = "hacc") -> Dict[str, Path]:
    outputs: Dict[str, Path] = {}
    outputs.update({f"rendered_{key}": value for key, value in write_rendered_title18_filings(merged_order_track=merged_order_track).items()})
    outputs.update({f"service_{key}": value for key, value in write_title18_service_packet().items()})
    outputs.update({f"index_{key}": value for key, value in write_title18_filing_index(merged_order_track=merged_order_track).items()})
    outputs.update({f"final_{key}": value for key, value in write_title18_final_packets().items()})
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate Title 18 filing artifacts")
    parser.add_argument("--merged-order-track", choices=["hacc", "quantum"], default="hacc")
    args = parser.parse_args()
    outputs = regenerate_title18_packets(merged_order_track=args.merged_order_track)
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())