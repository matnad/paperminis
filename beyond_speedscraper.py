# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 12:35:04 2018

@author: Matthias N.
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import asyncio
import concurrent.futures
import json, codecs

async def speedcrawl(pages):
    
    data = []
    for p in range(1,pages+1):
        data.append ({'page': p})
    
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(pages,100)) as executor:

        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor, 
                requests.get, 
                'https://www.dndbeyond.com/monsters',
                d
            )
            for d in data
        ]
        for response in await asyncio.gather(*futures):
            pass
    return [f.result() for f in futures]




ua = UserAgent()
header = {'User-Agent':str(ua.chrome)}
url = 'https://www.dndbeyond.com/monsters'
htmlContent = requests.get(url, headers=header)
soup = BeautifulSoup(htmlContent.text, "html.parser")

uldiv = soup.find_all("a", class_="b-pagination-item")
pages = int(uldiv[-1].text)

print('{} pages found.'.format(pages))

loop = asyncio.get_event_loop()   
r = loop.run_until_complete(speedcrawl(pages))

monster_type_url_dict = {'aberration': 'https://i.imgur.com/qI39ipJ.jpg',
                          'beast': 'https://i.imgur.com/GrjN1HL.jpg',
                          'celestial': 'https://i.imgur.com/EHaX5Pz.jpg',
                          'construct': 'https://i.imgur.com/me0a3la.jpg',
                          'dragon': 'https://i.imgur.com/92iC5ga.jpg',
                          'elemental': 'https://i.imgur.com/egeiuFf.jpg',
                          'fey': 'https://i.imgur.com/hhSXx7Y.jpg',
                          'fiend': 'https://i.imgur.com/OWTsHDl.jpg',
                          'giant': 'https://i.imgur.com/lh3eZGN.jpg',
                          'humanoid': 'https://i.imgur.com/ZSH9ikY.jpg',
                          'monstrosity': 'https://i.imgur.com/5iY8KhJ.jpg',
                          'ooze': 'https://i.imgur.com/WDHbliU.jpg',
                          'plant': 'https://i.imgur.com/FqEpGiQ.jpg',
                          'undead': 'https://i.imgur.com/MwdXPAX.jpg'}

monsters = {}
for p in r:
    soup = BeautifulSoup(p.text, "html.parser")
    infos = soup.find_all('div', class_='info')
    #css_links = [link["href"] for link in soup.findAll("link") if "stylesheet" in link.get("rel", [])]
    
    for info in infos:
        divs = info.find_all('div')
        for d in divs:
            c = d.get('class')
            if 'monster-icon' in c:
                a = d.find('a')
                if a == None:
                    creature_type = d.find('div').get('class')[1]
                    img_url = monster_type_url_dict[creature_type]
                else: 
                    img_url = a.get('href')
            elif 'monster-challenge' in c:
                cr = d.find('span').text
            elif 'monster-name' in c:
                name = d.find('a').text
                source = d.find('span', class_="source").text
            elif 'monster-type' in c:
                monster_type = d.find('span').text
            elif 'monster-size' in c:
                size = d.find('span').text
            elif 'monster-alignment' in c:
                alignment = d.find('span').text
                
        #monsters[name] =  {'name': name, 'source': source, 'type': monster_type, 'size': size, 'alignment': alignment, 'CR': cr, 'img_url': img_url}
        monsters[name] =  {'name': name,'size': size,'img_url': img_url}


with open('monsters.json', 'wb') as f:
    json.dump(monsters, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4, sort_keys=True)









