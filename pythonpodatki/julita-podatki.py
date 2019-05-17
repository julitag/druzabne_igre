print ("1")
import requests
import bs4
import re
## navodila za nastavitev https://likegeeks.com/python-web-scraping/
from selenium import webdriver
import csv as csv
import os

browser = webdriver.Chrome("pythonpodatki/chromedriver.exe")

## naslovi iger
titles = []
## atributi iger
mintime = []
maxtime = []
minplayers = []
maxplayers = []
release = []
age = []
genre = []
## ustvarjalci
artists = []
designers = []
publisher = []

## dodatki
dodatki_ime = []
dodatki_url = []
dodatki_letnica = []

## range(n) za top n * 100 iger
for i in range(1):
    req = requests.get("https://boardgamegeek.com/browse/boardgame/page/%s" % str(i+1))
    soup = bs4.BeautifulSoup(req.text, "html.parser")

    ## naslov in leto izdaje za naslednjih 100 iger
    collection = soup.select(".collection_objectname") ## select class .
    for i in collection:
        title = []
        title.extend(i.stripped_strings)
        titles.append(title[0])
        release.append(int(re.search(r'\d+', title[1]).group()))

    titles = titles[0:10]

    ## podtabele, zacetna in nato po ena za vsako izmed 100 iger
    table = soup.find(lambda tag: tag.name == "table" and tag.has_attr("id") and tag["id"] == "collectionitems")
    rows = table.find_all(lambda tag: tag.name == "tr")

    ## seznam web page koncnic iger
    games = []
    for row in rows[1::]:
        a = row.find("a", href = True)
        games.append(a["href"])

    # končnice, imena in letnice dodatkov iger
    for game in games[0:10]:
        browser.get("https://boardgamegeek.com" + game + "/expansions")
        s = bs4.BeautifulSoup(browser.page_source, "html.parser")
        collection = s.find_all("div", class_ = "summary-item-title summary-item-title-separated")
        
        expan_ime = []
        expan_letnice = []

        for i in collection:
            ime = []
            ime.extend(i.stripped_strings)
            expan_ime.append(ime[0])
            expan_letnice.append(int(re.search(r'\d+', ime[1]).group()))

        dodatki_ime.append(expan_ime)
        dodatki_letnica.append(expan_letnice)

        ## seznam web page koncnic dodatkov
        for row in collection:
            a = row.find("a", href = True)
            dodatki_url.append(a["href"])

    for game in games[0:10]+dodatki_url:
        ## web page trenutne igre, ki se ga ustvari na webdriverju
        browser.get("https://boardgamegeek.com" + game)
        s = bs4.BeautifulSoup(browser.page_source, "html.parser")
        primary = s.find_all("div", class_ = "gameplay-item-primary")

        # min & max stevilo igralcev, if zanka za primer ko imamo tocno doloceno stevilo igralcev
        minimum = primary[0].find('span', {'ng-if': 'min > 0'})
        if minimum != None:
            minplayers.append(int(minimum.text))
        else:
            minplayers.append(None)

        maksimum = primary[0].find('span', {'ng-if': 'max>0 && min != max'})
        if maksimum != None:
            maxplayers.append(int(re.search(r'\d+', maksimum.text).group()))
        elif minimum != None:
            maxplayers.append(int(minimum.text))
        else:
            mayplayers.append(None)

        # min & max dolzina igranja, if zanka za primer ko se igra tocno dolocen cas
        minimum = primary[1].find('span', {'ng-if': 'min > 0'})
        if minimum != None:
            mintime.append(int(minimum.text))
        else:
            minimum = []
            mintime.append(None) # če ni podatka o trajanju igre

        maksimum = primary[1].find('span', {'ng-if': 'max>0 && min != max'})
        if maksimum != None:
            maxtime.append(int(re.search(r'\d+', maksimum.text).group()))
        elif minimum != None:
            maxtime.append(int(minimum.text))
        else:
            mintime.append(None) ## gloomheaven: solo scenario ma tle probleme - čeprau prje je delalo
        
        ## starost, if zanka za primer ko starost ni podana
        if re.search(r'\d+', primary[2].text) != None:
            age.append(int(re.search(r'\d+', primary[2].text).group()))
        else:
            age.append(None)

        primary = s.find_all(class_="feature-description")
        ## žanr
        g = primary[1].find_all("a", href=re.compile("category"))
        names = []
        for name in g:
            names.append(name["title"])
        genre.append(names)

        primary = s.find_all(class_="credits")
        ## designerji
        des = primary[1].find_all("a", href=re.compile("designer"))
        names = []
        for name in des:
            names.append(name["title"])
        designers.append(names)

        ## artisti
        art = primary[1].find_all("a", href=re.compile("artist"))
        names = []
        for name in art:
            names.append(name["title"])
        artists.append(names)

        ## založba
        pub = primary[1].find_all("a", href=re.compile("publisher"))
        publisher.append(pub[0].text)



## To show proper characters in excel you have to open new excel file and import data from games.csv using utf-8 encoding.
n = len(titles)
with open('pythonpodatki/igre.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Igra", "Min. st. igralcev", "Max. st. igralcev", "Min cas", "Max. cas", "Leto izdaje", "Min. starost"])
    for i in range(len(titles)):
        wr.writerow([titles[i], minplayers[i], maxplayers[i], mintime[i], maxtime[i], release[i], age[i]])
    for i in range(len(dodatki_ime)):
        wr.writerow([dodatki_ime[i], minplayers[n+i], maxplayers[n+i], mintime[n+i], maxtime[n+i], release[n+i], age[n+i]])

with open('pythonpodatki/ustvarjalci.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Game", "Designers", "Artists", "Publisher"])
    for i in range(len(titles)):
        wr.writerow([titles[i], designers[i], artists[i], publisher[i]])
    for i in range(len(dodatki_ime)):
        wr.writerow([dodatki_ime[i], designers[n+i], artists[n+i], publisher[n+i]])

with open('pythonpodatki/zvrst.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Game", "Zvrst"])
    for i in range(len(titles)):
       wr.writerow([titles[i], genre[i]])
    for i in range(len(dodatki_ime)):
       wr.writerow([dodatki_ime[i], genre[n+i]])

with open('pythonpodatki/dodatki.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Game", "Dodatek"])
    for i in range(len(titles)):
       wr.writerow([titles[i], dodatki_ime[i]])
