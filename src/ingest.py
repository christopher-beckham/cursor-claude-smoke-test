from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Row:
    id: str
    name: str
    value: float


def load_csv(path: Path) -> list[Row]:
    rows = []
    with path.open(newline="") as f:
        for record in csv.DictReader(f):
            rows.append(Row(
                id=record["id"],
                name=record["name"],
                value=float(record["value"]),
            ))
    return rows


def write_csv(rows: list[Row], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "value"])
        writer.writeheader()
        for row in rows:
            writer.writerow({"id": row.id, "name": row.name, "value": row.value})


def run(data_dir: Path) -> None:
    input_dir = data_dir / "input"
    output_dir = data_dir / "output"

    csv_files = list(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")

    for src in csv_files:
        logger.info("Processing %s", src.name)
        rows = load_csv(src)
        dest = output_dir / src.name
        write_csv(rows, dest)
        logger.info("Wrote %d rows to %s", len(rows), dest)


if __name__ == "__main__":
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    data_dir = Path(os.environ["DATA_DIR"])
    run(data_dir)
