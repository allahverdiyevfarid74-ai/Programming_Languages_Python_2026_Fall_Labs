import csv
import os
from vaildator import validate_row, to_record

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    valid_records = []
    error_messages = []
    seen_flights = set()

    for path in paths:
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_no, raw_line in enumerate(lines, start=1):
            if not raw_line.strip():
                continue
            if raw_line.strip().startswith("#"):
                continue
            if line_no == 1:
                continue

            reader = csv.reader([raw_line])
            try:
                row = next(reader)
            except StopIteration:
                continue

            error_code = validate_row(row, airports)
            if error_code is not None:
                free_text = raw_line.strip()
                error_messages.append(f"{filename}:{line_no}: {error_code} | {free_text}")
            else:
                record = to_record(row)
                key = (record["flight_id"], record["departure_datetime"])
                if key in seen_flights:
                    free_text = raw_line.strip()
                    error_messages.append(f"{filename}:{line_no}: DUPLICATE_FLIGHT | {free_text}")
                else:
                    seen_flights.add(key)
                    valid_records.append(record)

    return valid_records, error_messages
