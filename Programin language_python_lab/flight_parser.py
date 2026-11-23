import argparse
import json
import logging
import os
import sys
from datetime import datetime

from vaildator import load_airports
from csv_loader import parse_files
from query import run_queries

STUDENT_ID = "241RDB123"
FIRST_NAME = "Janis"
LAST_NAME = "Berzins"

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Flight Schedule Parser and Query Runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", metavar="FILE", help="Parse a single CSV file")
    group.add_argument("-d", metavar="FOLDER", help="Parse every CSV file in the folder")
    group.add_argument("-j", metavar="FILE", help="Load existing JSON database")

    parser.add_argument("-a", metavar="FILE", help="Airport list file")
    parser.add_argument("-o", metavar="FILE", default="db.json", help="Output path for JSON database")
    parser.add_argument("-q", metavar="FILE", help="Run queries from JSON file")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="Folder for query response file")

    args = parser.parse_args(argv)

    if (args.i or args.d) and not args.a:
        parser.error("-a is required with -i and -d")
    if args.j and "-o" in sys.argv:
        parser.error("-o cannot be used with -j")

    db = []
    log_handler = None
    logger = logging.getLogger("flight_parser")

    try:
        if args.i or args.d:
            if not os.path.exists(args.a):
                print(f"Error: Airport file {args.a} does not exist.", file=sys.stderr)
                return 1

            airports = load_airports(args.a)

            paths = []
            if args.i:
                if not os.path.exists(args.i):
                    print(f"Error: CSV file {args.i} does not exist.", file=sys.stderr)
                    return 1
                paths = [args.i]
            else:
                if not os.path.isdir(args.d):
                    print(f"Error: Folder {args.d} does not exist.", file=sys.stderr)
                    return 1
                csv_files = sorted([f for f in os.listdir(args.d) if f.endswith(".csv")])
                if not csv_files:
                    print(f"Error: No .csv files found in {args.d}.", file=sys.stderr)
                    return 1
                paths = [os.path.join(args.d, f) for f in csv_files]

            valid_records, error_messages = parse_files(paths, airports)
            db = valid_records

            os.makedirs(os.path.dirname(os.path.abspath(args.o)), exist_ok=True)
            with open(args.o, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)

            db_dir = os.path.dirname(os.path.abspath(args.o))
            log_path = os.path.join(db_dir, "errors.log")

            logger.setLevel(logging.INFO)
            log_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            log_handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(log_handler)

            for err_msg in error_messages:
                logger.warning(err_msg)

        elif args.j:
            if not os.path.exists(args.j):
                print(f"Error: Database JSON file {args.j} does not exist.", file=sys.stderr)
                return 1
            with open(args.j, "r", encoding="utf-8") as f:
                try:
                    db = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON in {args.j}", file=sys.stderr)
                    return 1
            if not isinstance(db, list):
                print(f"Error: JSON database must be an array.", file=sys.stderr)
                return 1

        if args.q:
            if not os.path.exists(args.q):
                print(f"Error: Query file {args.q} does not exist.", file=sys.stderr)
                return 1
            with open(args.q, "r", encoding="utf-8") as f:
                try:
                    queries = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON in {args.q}", file=sys.stderr)
                    return 1

            query_results = run_queries(db, queries)

            now_str = datetime.now().strftime("%Y%m%d_%H%M")
            resp_filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{now_str}.json"
            resp_path = os.path.join(args.r, resp_filename)
            os.makedirs(os.path.abspath(args.r), exist_ok=True)

            with open(resp_path, "w", encoding="utf-8") as f:
                json.dump(query_results, f, indent=2)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        if log_handler is not None:
            logger.removeHandler(log_handler)
            log_handler.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())