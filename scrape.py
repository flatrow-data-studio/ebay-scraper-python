"""eBay scraper in Python: listing prices, condition and sold counts to CSV.

Runs the eBay Listings Scraper (an Apify Actor) for one or more keywords on an
eBay marketplace and saves one row per listing to a CSV file.

    export APIFY_TOKEN="<your-apify-token>"
    python scrape.py "wireless earbuds" --max-results 60
    python scrape.py "laptop stand" --condition new --buying-format buy-it-now --sort price-asc
"""

import argparse
import csv
import json
import os
import sys
from decimal import Decimal

from apify_client import ApifyClient

ACTOR = "myth84/ebay-search-scraper"

# Columns written to the CSV. Every row of the dataset has more (see the README).
COLUMNS = [
    "platformProductId",
    "title",
    "currency",
    "price",
    "originalPrice",
    "discountPercent",
    "soldCount",
    "shippingFree",
    "shippingCost",
    "shipsFrom",
    "rating",
    "reviewCount",
    "isSponsored",
    "searchQuery",
    "searchRank",
    "url",
]

# Keys of the attributes column, written as columns of their own.
ATTRIBUTES = ["condition", "conditionText", "listingFormat"]


def make_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("keywords", nargs="+", help='searches as typed on eBay, e.g. "wireless earbuds"')
    parser.add_argument("--marketplace", default="US", choices=["US", "UK", "DE", "FR", "IT", "ES", "NL", "CA", "AU"],
                        help="ebay.com (US), ebay.co.uk (UK), ebay.de (DE)... (default US)")
    parser.add_argument("--sort", default="best-match", choices=["best-match", "price-asc"],
                        help="eBay's best match, or price plus shipping, lowest first")
    parser.add_argument("--condition", default="any", choices=["any", "new", "used"])
    parser.add_argument("--buying-format", default="all", choices=["all", "buy-it-now", "auction"])
    parser.add_argument("--price-max", type=float, help="maximum price, in the marketplace currency")
    parser.add_argument("--exclude", action="append", help="word the listings must not contain (repeatable)")
    parser.add_argument("--max-results", type=int, default=50,
                        help="listings per keyword (default 50); you pay per listing saved")
    parser.add_argument("--max-charge", type=Decimal, help="stop the run once it has cost this many USD")
    return parser


def build_input(args):
    run_input = {
        "searchQueries": args.keywords,
        "marketplace": args.marketplace,
        "sortBy": args.sort,
        "condition": args.condition,
        "buyingFormat": args.buying_format,
        "maxResults": args.max_results,
    }
    if args.price_max is not None:
        run_input["priceMax"] = args.price_max
    if args.exclude:
        run_input["excludeWords"] = args.exclude
    return run_input


def run_actor(run_input, max_charge=None):
    """Runs the Actor, waits for it to finish and returns the rows of its dataset."""
    if not os.environ.get("APIFY_TOKEN"):
        sys.exit("Set APIFY_TOKEN first: Apify Console > Settings > API & Integrations.")
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR).call(run_input=run_input, max_total_charge_usd=max_charge)
    if run is None:
        sys.exit("The run could not be started.")
    status = getattr(run.status, "value", run.status)  # SUCCEEDED, FAILED, TIMED-OUT...
    if status != "SUCCEEDED":
        sys.exit(f"The run ended as {status}: open its log in Apify Console.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def cell(value):
    """Lists and objects as JSON text, so that every CSV row has the same columns."""
    return json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value


def write_csv(rows, path, columns=COLUMNS, append=False):
    new_file = not (append and os.path.exists(path))
    with open(path, "a" if append else "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(columns + ATTRIBUTES)
        for row in rows:
            attributes = row.get("attributes") or {}
            writer.writerow([cell(row.get(column)) for column in columns]
                            + [cell(attributes.get(key)) for key in ATTRIBUTES])


def main():
    parser = make_parser("Scrape eBay listing prices, condition and units sold to CSV.")
    parser.add_argument("--output", default="ebay_listings.csv", help="CSV file (default ebay_listings.csv)")
    args = parser.parse_args()

    rows = run_actor(build_input(args), args.max_charge)
    write_csv(rows, args.output)
    print(f"{len(rows)} listings saved to {args.output}")

    priced = sorted((row for row in rows if row.get("price") is not None), key=lambda row: row["price"])
    for row in priced[:5]:
        condition = (row.get("attributes") or {}).get("conditionText") or "-"
        print(f'{row["price"]:>9} {row["currency"]}  {condition:<12}  {row.get("soldCount") or 0:>5} sold  '
              f'{row["title"][:70]}')


if __name__ == "__main__":
    main()
