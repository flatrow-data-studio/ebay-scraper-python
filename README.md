# eBay scraper in Python: listing prices, condition and sold counts

> This repository calls a paid Apify Actor built by Flatrow Data Studio (the author). Links to apify.com carry the author's affiliate code: the author may earn a commission if you sign up to Apify through them, at no extra cost to you.

A small eBay scraper in Python. `scrape.py` searches eBay for one or more keywords and saves **one row per listing** to CSV: price and currency, strike-through price and discount, condition, buying format (Buy It Now or auction), shipping cost or free shipping, ships-from country, units sold, rating, sponsored flag and position in the results, on ebay.com, ebay.co.uk, ebay.de, ebay.fr, ebay.it, ebay.es, ebay.nl, ebay.ca or ebay.com.au. `monitor_prices.py` turns the same search into an **eBay price tracker** that returns only the price drops, price rises and new listings since its previous run.

Both scripts run the [eBay Listings Scraper & Price Tracker](https://apify.com/myth84/ebay-search-scraper?fpr=pnpkfc) on Apify through the official `apify-client` package: the Actor runs in Apify's cloud and returns clean rows, so there is no browser, HTML parsing or proxy to maintain on your side. No login, no cookies, and **no personal data**: seller pseudonyms, feedback scores, store names, buyers and bidders are never collected.

## Use cases

- **Resale research**: the asking prices of a used iPhone, a vintage watch or a games console, with condition and units sold.
- **Sourcing**: the cheapest new items with Buy It Now and free shipping, from your own country.
- **Price alerts**: a daily cron job that prints the listings whose price went down.
- **Competitor price monitoring** across eBay marketplaces, ready for pandas or Excel.

## Installation

You need Python 3.11 or later and a free [Apify account](https://apify.com/?fpr=pnpkfc) (the free plan includes monthly credit).

```bash
git clone https://github.com/flatrow-data-studio/ebay-scraper-python.git
cd ebay-scraper-python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export APIFY_TOKEN="<your-apify-token>"   # Apify Console > Settings > API & Integrations
```

## Run it

```bash
# 60 "wireless earbuds" listings on ebay.com
python scrape.py "wireless earbuds" --max-results 60

# Brand-new laptop stands with Buy It Now, cheapest first (price plus shipping)
python scrape.py "laptop stand" --condition new --buying-format buy-it-now --sort price-asc
```

The script writes `ebay_listings.csv` (change it with `--output`) and prints the five cheapest listings. Other options: several keywords in one run (`"iphone 13" "iphone 14"`), `--marketplace` (`US`, `UK`, `DE`, `FR`, `IT`, `ES`, `NL`, `CA`, `AU`), `--price-max`, `--exclude case` to leave out listings with a word (repeatable), and `--max-charge 0.50` to stop a run once it has cost 50 cents; `python scrape.py --help` lists them all.

## Track prices every day

```bash
python monitor_prices.py "wireless earbuds" --store ebay-earbuds-daily
```

The first run records the price of every listing as the reference (they all come back as `new`). From the second run on, only the new listings and the listings whose price changed are returned, with `previousPrice`, `priceDelta` and `priceDeltaPercent`; they are printed and appended to `ebay_price_changes.csv`. The reference lives in a key-value store of your Apify account (`--store`, `ebay-price-monitor` by default; use one name per schedule), so the script can run from cron on any machine:

```bash
0 7 * * * cd /path/to/ebay-scraper-python && .venv/bin/python monitor_prices.py "wireless earbuds" --store ebay-earbuds-daily >> tracker.log 2>&1
```

Keep the same keywords, marketplace, sort and filters from run to run: changing them starts a new reference.

## Sample output

One real row from a "wireless earbuds" search on ebay.com, key columns only:

```json
{
  "platformProductId": "157236783307",
  "title": "Bluetooth Wireless Earbuds Headset Headphones Compatible with iPhone and Samsung",
  "currency": "USD",
  "price": 17.99,
  "soldCount": 866,
  "shippingFree": true,
  "shipsFrom": "US",
  "attributes": {
    "condition": "new",
    "conditionText": "Brand New",
    "listingFormat": "buy-it-now",
    "leafCategoryId": "80077"
  },
  "isSponsored": true,
  "searchRank": 1
}
```

## Columns

`scrape.py` writes these columns:

| Column | Meaning |
|---|---|
| `platformProductId` | eBay item number |
| `title` | Listing title |
| `currency` | Currency of the prices |
| `price` | Price as displayed (Buy It Now price or current bid), shipping excluded |
| `originalPrice` | Strike-through or list price |
| `discountPercent` | Discount against `originalPrice` |
| `soldCount` | Units sold |
| `shippingFree` | Free shipping |
| `shippingCost` | Shipping cost |
| `shipsFrom` | Ships-from country |
| `rating` | Product rating out of 5 |
| `reviewCount` | Number of product ratings |
| `isSponsored` | Sponsored result |
| `searchQuery` | The keywords that found the listing |
| `searchRank` | Position in the results |
| `url` | Listing link |
| `condition` | Normalized condition (`new`, `used`...), from the `attributes` column |
| `conditionText` | Condition as eBay displays it, from the `attributes` column |
| `listingFormat` | `buy-it-now` or `auction`, from the `attributes` column |

The dataset of each run has more columns (image, delivery estimate, marketplace...): add their names to `COLUMNS` in `scrape.py`, or keys of `attributes` to `ATTRIBUTES`. The full list is on the [Actor page](https://apify.com/myth84/ebay-search-scraper?fpr=pnpkfc).

## Pricing

The Actor is pay-per-event: from $2.50 per 1,000 listings on Apify's Free plan, lower on paid plans, with compute and proxies included. Apify's free monthly credit of $5 covers about 1,999 listings. You pay per listing saved and nothing else; `--max-results` caps every keyword of a run, and in price-tracking mode only the new and changed listings are saved and charged.

## FAQ

**Do I need to write a scraper or run a browser?** No. The Actor runs in Apify's cloud and is kept up to date when eBay changes its pages; your script receives JSON rows.

**Can I paste an eBay search URL with my filters?** Yes: the Actor also takes `startUrls`, search URLs copied from your browser. Put them in `run_input` in place of `searchQueries` in `build_input`; the [Actor page](https://apify.com/myth84/ebay-search-scraper?fpr=pnpkfc) documents every input field.

**Is there personal data in the output?** No. eBay search results name sellers; this Actor does not. Rows contain listing facts only. Use the data for analysis, respect eBay's terms and the law of your country, and do not republish listings.

## Related

Other Python examples by Flatrow Data Studio, all with a CSV export and a price tracker:

- [amazon-scraper-python](https://github.com/flatrow-data-studio/amazon-scraper-python): Amazon product prices, ratings and price drops.
- [aliexpress-scraper-python](https://github.com/flatrow-data-studio/aliexpress-scraper-python): AliExpress product prices, units sold and shipping.
- [airbnb-scraper-python](https://github.com/flatrow-data-studio/airbnb-scraper-python): Airbnb listings, nightly and total prices, ratings and availability.
- [booking-scraper-python](https://github.com/flatrow-data-studio/booking-scraper-python): Booking.com hotel prices, taxes, review scores and stars.
- [google-hotels-scraper-python](https://github.com/flatrow-data-studio/google-hotels-scraper-python): Google Hotels prices, with every booking site's rate.

## License

MIT, see [LICENSE](LICENSE). eBay is a trademark of its owner; this project is not affiliated with eBay.
