# Braacket Utilties

Braacket doesn't have an API, so, if you want to access the data, you have to scrape it. This is a collection of utilities to help you do that.

## Most Improved (`most-improved.py`)

This script will get the most improved players in a given season, which is determined by the difference in their current rating points and their rating points at the beginning of the season.

You can use it like so:

```bash
py .\most-improved.py https://braacket.com/league/MSVS/ranking/61481DD2-6EF1-40F8-82A7-6EF1769AE8DE?rows=200
```

This will output the most improved to a `.txt` file, like: `most-improved-20240827173029.txt`.

If you'd like to sort the list, you can also run the script like so:

```bash
py .\most-improved.py most-improved-20240827173029.txt
```

This will output the sorted list to a `.txt` file, like: `most-improved-20240827175959-sorted`.

