# ThreadArt

Make some beautiful threaded paintings which you can then build in your own home.

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Some nice abstract art with few hooks

    python generate.py gray.jpg --hooks 45 --lines 2500

Or a more decent portrait

    python generate.py example.jpg --hooks 180 --lines 2500 --weighted example_weighted.jpg

