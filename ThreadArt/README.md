# ThreadArt

Make some beautiful threaded paintings which you can then build in your own home.

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Some nice abstract art with few hooks

    python generate.py gray.jpg --hooks 45 --max_lines
    
![image](https://user-images.githubusercontent.com/9117323/122535251-47aac380-d01b-11eb-990d-94e92164c4fe.png)


Or a more decent portrait

    python generate.py example.jpg --weighted example_weighted.jpg
    
![image](https://user-images.githubusercontent.com/9117323/122534310-4fb63380-d01a-11eb-9245-36172742f730.png)
    
    python generate.py churchill.jpg --weighted churchill_weighted.jpg --lines 4000 --light_penalty 0.1 --line_w 0.4

![image](https://user-images.githubusercontent.com/9117323/122534373-5b095f00-d01a-11eb-92a1-54e1ebe723a3.png)

    python generate.py joker.jpg --dual_weighted joker_wpos.jpg joker_wneg.jpg
    
![image](https://user-images.githubusercontent.com/9117323/122534401-6066a980-d01a-11eb-9a0d-2524ce88340e.png)

    python generate.py che.png --dual_weighted che_wpos.jpg che_wneg.jpg --line_w 0.5 --hooks 180
    
![image](https://user-images.githubusercontent.com/9117323/122535287-4f6a6800-d01b-11eb-9dd0-699a0fc56e35.png)

Feel free to experiment

    python generate.py -h

I also usually run some grid search to find the best parameters. Edit `grid_search.py` and run it for about an hour.
