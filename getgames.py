import requests
import time
import json
import shutil
import os
import re
import sys


# Sleep timer set to 1.6 because the steam api only accepts requests every 1,5 seconds
sleeptime = 1.6


# Removing items from applist when exists in skip or not_released list
def remove_duplicates():
    with open('applist.json', 'r', encoding='utf-8') as f:
        applist = json.load(f)

    with open('skiplist.json', 'r', encoding='utf-8') as d:
        skiplist = json.load(d)

    with open('not_released.json', 'r', encoding='utf-8') as e:
        not_released = json.load(e)

    list_diff = list(set(applist) - set(skiplist) - set(not_released))

    with open('list_diff.json', 'w', encoding='utf-8') as test:
        json.dump(list_diff, test, indent=4)


# Progressbar
def progress(count, total, status='', bar_len=60):
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 2)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    fmt = '[%s] %s%s ...%s done' % (bar, percents, '%', status)
    print('\b' * len(fmt), end='')
    sys.stdout.write(fmt)
    sys.stdout.flush()


# Convert Steam string price to a number. Original (5,29 €)
def price_to_number(price):
    try:
        price = price.replace(',', '.')
        return round(float(re.findall('([0-9]+[,.]+[0-9]+)', price)[0]), 2)
    except IndexError:
        return float(price[0])
    except:
        print("Price Error")


# Clean the text with replace and regexp. Many games have html code or links in description
def clean_text(text):
    text = text.replace('\n\r', ' ')
    text = text.replace('\r\n', ' ')
    text = text.replace('\r \n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace("’", '')
    text = text.replace("™", '')
    text = text.replace("–", '-')
    text = text.replace("…", '')
    text = text.replace('&quot;', "'")
    text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', text, flags=re.MULTILINE)
    text = re.sub('<[^<]+?>', ' ', text)
    text = re.sub(' +', ' ', text)
    text = text.lstrip(' ')
    return text


# Getting the full Steam app list
def create_app_list():
    print('Requesting steam game list')
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2')
    if response:
        time.sleep(sleeptime)
        data = response.json()['applist']['apps']
        app_list = [str(i["appid"]) for i in data]
        with open('applist.json', 'w', encoding='utf-8') as f:
            json.dump(app_list, f, indent=4, ensure_ascii=False)
    else:
        print("An error occurred... Waiting 10 seconds for retry")
        time.sleep(10)
        create_app_list()


# Function to save and append the json files
def save_json(data, filename):
    items = []
    if not os.path.isfile(filename):
        items.append(data)
        with open(filename, mode='w', encoding='utf-8') as f:
            f.write(json.dumps(items, indent=4, ensure_ascii=False))
    else:
        with open(filename, mode='r', encoding='utf-8') as file:
            insert = json.load(file)
        if data in insert:
            pass
        else:
            insert.append(data)
            with open(filename, mode='w', encoding='utf-8') as f:
                f.write(json.dumps(insert, indent=4, ensure_ascii=False))


# Parsing through the request and getting only wanted infos
def create_game_json(app):
    gamelist = {}
    gamelist['appid'] = app['data']['steam_appid']
    gamelist['name'] = app['data']['name'].strip()
    gamelist['release_date'] = app['data']['release_date']['date']
    if app['data']['is_free'] == True or 'price_overview' not in app['data']:
        gamelist['price'] = 0.0
        gamelist['currency'] = 'EUR'
    else:
        gamelist['price'] = price_to_number(app['data']['price_overview']['final_formatted'])
        gamelist['currency'] = app['data']['price_overview']['currency']
    gamelist['required_age'] = int(str(app['data']['required_age']).replace('+', '')) if 'required_age' in app['data'] else 0
    gamelist['dlc_count'] = len(app['data']['dlc']) if 'dlc' in app['data'] else 0

    gamelist['detailed_description'] = clean_text(app['data']['detailed_description'].strip()) if 'detailed_description' in app['data'] else ''
    gamelist['about_the_game'] = clean_text(app['data']['about_the_game'].strip()) if 'about_the_game' in app['data'] else ''
    gamelist['short_description'] = clean_text(app['data']['short_description'].strip()) if 'short_description' in app['data'] else ''
    gamelist['reviews'] = clean_text(app['data']['reviews']) if 'reviews' in app['data'] else ''
    gamelist['notes'] = clean_text(app['data']['content_descriptors']['notes'].strip()) if 'content_descriptors' in app['data'] and app['data']['content_descriptors']['notes'] is not None else ''

    gamelist['header_image'] = app['data']['header_image'].strip() if 'header_image' in app['data'] else ''
    gamelist['windows'] = True if app['data']['platforms']['windows'] else False
    gamelist['mac'] = True if app['data']['platforms']['mac'] else False
    gamelist['linux'] = True if app['data']['platforms']['linux'] else False
    gamelist['metacritic_score'] = int(app['data']['metacritic']['score']) if 'metacritic' in app['data'] else 0
    gamelist['metacritic_url'] = app['data']['metacritic']['url'] if 'metacritic' in app['data'] else ''
    gamelist['achievements'] = int(app['data']['achievements']['total']) if 'achievements' in app['data'] else 0
    gamelist['recommendations'] = app['data']['recommendations']['total'] if 'recommendations' in app['data'] else 0
    gamelist['developers'] = []
    if 'developers' in app['data']:
        for developer in app['data']['developers']:
            gamelist['developers'].append(developer.strip())
    gamelist['publishers'] = []
    if 'publishers' in app['data']:
        for publisher in app['data']['publishers']:
            gamelist['publishers'].append(publisher.strip())
    gamelist['categories'] = []
    if 'categories' in app['data']:
        for category in app['data']['categories']:
            gamelist['categories'].append(category['description'])
    gamelist['genres'] = []
    if 'genres' in app['data']:
        for genre in app['data']['genres']:
            gamelist['genres'].append(genre['description'])
    save_json(gamelist, 'gamelist.json')
    # print(gamelist)


'''
Scraper. Fetching game infos and splitting into skip and not released list.
Checking if game already exists in game app or not released list.
'''
def get_game_info():
    counter = 0
    print("GetSteamGames app started...")
    print("Scanning files for starting point...")
    remove_duplicates()
    with open('list_diff.json', 'r', encoding='utf-8') as f:
        counter += (read_json('skiplist.json') + read_json('not_released.json'))
        for i in json.load(f):
            if os.path.isfile('gamelist.bak') == False or os.path.getsize("gamelist.bak") < os.path.getsize("gamelist.json"):
                shutil.copyfile("gamelist.json", "gamelist.bak")
            appid = i
            if appid in get_list('skiplist.json'):
                counter += 1
            elif appid in get_gamelist_apps():
                counter += 1
            elif appid in get_list('not_released.json'):
                counter += 1
            if appid not in get_list('skiplist.json') and appid not in get_gamelist_apps() and appid not in get_list('not_released.json'):
                response = requests.get(f'https://store.steampowered.com/api/appdetails?l=english&appids={appid}')
                data = response.json()
                app = data[f'{appid}']
                counter += 1
                time.sleep(sleeptime)
                if app['success'] == False:
                    # print(f"putting {appid} into skiplist because of non success")
                    save_json(appid, 'skiplist.json')
                elif app['data']['type'] != 'game':
                    # print(f"putting {appid} into skiplist because its no full game")
                    save_json(appid, 'skiplist.json')
                elif app['data']['release_date']['coming_soon'] == True:
                    # print(f"putting {appid} into not_released.json because not released")
                    save_json(appid, 'not_released.json')
                elif 'developers' in app['data'] and len(app['data']['developers']) == 0:
                    # print(f"putting {appid} into skiplist because no developer")
                    save_json(appid, 'skiplist.json')
                else:
                    # print(f"writing new game {appid} to gamelist.json")
                    create_game_json(app)
                progress(counter, read_json('applist.json'))


# loading the appid's from gamelist.json
def get_gamelist_apps():
    gamelist = []
    with open('gamelist.json', 'r', encoding='utf-8') as file:
        items = json.load(file)
        for i in items:
            gamelist.append(str(i['appid']))
        return gamelist


# loading the appid's from file
def get_list(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        items = json.load(file)
        return items


# Check length of the json files
def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return len(file.readlines())


# Starting area
if __name__ == '__main__':
    try:
        if not os.path.isfile('applist.json'):
            create_app_list()
            get_game_info()
        elif not os.path.isfile('gamelist.json'):
            with open('gamelist.json', 'w', encoding='utf-8') as f:
                f.write('[{"appid": 1}]')
            get_game_info()
        elif not os.path.isfile('not_released.json'):
            with open('not_released.json', 'w', encoding='utf-8') as f:
                f.write('["1"]')
            get_game_info()
        else:
            get_game_info()
    except FileNotFoundError:
        print("File not found. Creating...")
        time.sleep(2)
        if not os.path.isfile('not_released.json'):
            with open('not_released.json', 'w', encoding='utf-8') as f:
                f.write('["2"]')
            get_game_info()
        else:
            get_game_info()
    # except (KeyboardInterrupt, SystemExit):
    #     get_game_info()
    else:
        print("Completed")
