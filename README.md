
# _Get Steam Games_
### API scraper to download a list of all Steam games
![image](https://user-images.githubusercontent.com/108484798/189700949-62bc7141-3893-474a-8729-c65bbba0999b.png)

## Features
* Catch every single game in Steam DB
* Continue fetching where you stopped
* Updates the list with new games every restart

## How to use
Clone or download the repository
```sh
https://github.com/PatrickDegner/GetSteamGames.git
```

Install the dependencies or use the pipfile
```sh
pip install requests
```
Startup the app
```sh
getgames.py
```
After startup you will see the progressbar "running". 

![image](https://user-images.githubusercontent.com/108484798/189707076-ab7611c5-3208-4887-a96a-aa4dec0f2269.png)


## How it works:

-- On first start "GetSteamGames" app will download a list of all titles in Steam DB.

-- This list will be used to call every game after another (1,5 seconds).

-- Every non game(dlc,app,others) or not released game will be put into another json file.

-- On real game the game infos will be stored into a json

-- If you want to redownload the full list, just delete applist.json

-- If you want to recheck not released games you can also delete not_released.json


## What infos to get?

| what | to | get? |
| ------ | ------ | ------ |
| appid | name | free or not |
| release_date | price | currency |
| required_age | dlc_count | reviews |
| detailed_description | dev_notes | main_image |
| short_description | platform | recommendations |
| about_the_game | metacritic_score | developers |
| achievements_count | metacritic_url | categories |
| genres | publishers |  |

## Other Infos

* Steam only allows 1 call every 1,5 seconds.
* Whole download will take multiple days.
* Update will be faster after first big fetch
