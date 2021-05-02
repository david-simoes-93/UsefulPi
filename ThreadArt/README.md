# ThreadArt

Make some beautiful threaded paintings which you can then build in your own home.

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Some nice abstract art with few hooks

    python generate.py gray.jpg --hooks 45 --lines 1000

Or a more decent portrait

    python generate.py example.jpg --weighted example_weighted.jpg
    python generate.py churchill.jpg --weighted churchill_weighted.jpg --lines 4000 --light_penalty 0.1 --wheel_p 2500
    python generate.py joker.jpg --dual_weighted joker_wpos.jpg joker_wneg.jpg

Feel free to experiment

    python generate.py -h

