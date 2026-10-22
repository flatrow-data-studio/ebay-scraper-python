"""eBay price tracker: the price drops, rises and new listings since the previous run.

Runs the same search in price-monitoring mode. The Actor keeps the last price
of every listing in a key-value store of your Apify account, so this script
can run from cron on any machine. The first run records the reference; later
runs return only the new listings and the price changes, appended to a CSV
history.

    export APIFY_TOKEN="<your-apify-token>"
    python monitor_prices.py "wireless earbuds" --store ebay-earbuds-daily
"""

from scrape import COLUMNS, build_input, make_parser, run_actor, write_csv

MONITOR_COLUMNS = ["changeType", "previousPrice", "priceDelta", "priceDeltaPercent"]


def main():
    parser = make_parser("eBay price tracker: new listings and price changes since the previous run.")
    parser.add_argument("--store", default="ebay-price-monitor",
                        help="key-value store of your Apify account that keeps the previous prices "
                             "(one name per schedule)")
    parser.add_argument("--history", default="ebay_price_changes.csv",
                        help="CSV file the changes are appended to (default ebay_price_changes.csv)")
    args = parser.parse_args()

    run_input = build_input(args)
    run_input["monitorPrices"] = True
    run_input["onlyChanges"] = True
    run_input["monitorStoreName"] = args.store
    rows = run_actor(run_input, args.max_charge)

    if not rows:
        print("Nothing moved since the previous run.")
        return
    write_csv(rows, args.history, COLUMNS + MONITOR_COLUMNS, append=True)

    changed = [row for row in rows if row["changeType"] == "price_changed"]
    new = len(rows) - len(changed)
    print(f"Price changes: {len(changed)}, new listings: {new} (appended to {args.history})")
    for row in sorted(changed, key=lambda row: row["priceDeltaPercent"] or 0):
        print(f'{row["previousPrice"]} -> {row["price"]} {row["currency"]} '
              f'({row["priceDeltaPercent"]} %)  {row["title"][:80]}  {row["url"]}')


if __name__ == "__main__":
    main()
