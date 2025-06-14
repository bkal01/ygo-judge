import argparse
import sys

from pathlib import Path

# Ensure src is on path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from src.store.vector_store import VectorStore


def main():
    parser = argparse.ArgumentParser(description="Populate Chroma vector database.")
    parser.add_argument(
        "--rules",
        action="store_true",
        help="Populate the rules collection.",
    )
    parser.add_argument(
        "--qa",
        action="store_true",
        help="Populate the official_qa collection.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Populate all collections.",
    )
    args = parser.parse_args()

    if not (args.rules or args.qa or args.all):
        parser.error("Specify at least one of --rules, --qa, or --all")

    store = VectorStore()

    if args.rules or args.all:
        print("Populating rules collection…", flush=True)
        store.populate_rules_collection()
        print("Done populating rules collection.")

    if args.qa or args.all:
        print("Populating official_qa collection…", flush=True)
        store.populate_official_qa_collection()
        print("Done populating official_qa collection.")


if __name__ == "__main__":
    main() 