# Games Indexer

A neat little UI to use in conjunction with IGDB.com. Convert your CSVs from there and add/remove games at your leisure.

    pip install -r reqs.txt
    python igdb.py --csv some_games_list.csv
    python igdb.py

For specific games,

    python igdb.py --list some_games_list.csv --add 123
    python igdb.py --list some_games_list.csv --remove 123
