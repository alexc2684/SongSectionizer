import socket
import json
import requests
import re
import sys
from bs4 import BeautifulSoup
from argparse import ArgumentParser

CLIENT_TOKEN = "FAlLLpDDvipZuMDOBM07qRkDgw_kQs3_l3KYJuMsXCE3EJIE77MdWC8FP2x2ieCO"
URL = "http://api.genius.com"
HEADERS = {"Authorization": "Bearer " + CLIENT_TOKEN, "User-Agent": "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)"}

def readData(name):
    data = []

    print("Reading in lyric URLs")
    with open(name, 'r') as f:
        for line in f.readlines():
            index = line.find('\n')
            if index != -1:
                line = line[:index]
            data.append(line)
    return data

def writeData(X, y, filename):
    try:
        with open(filename, 'w') as f:
            for data, label in zip(X, y):
                line = data + ',' + label + '\n'
                f.write(line)
        print("Finished writing data")
        return True
    except:
        return False

def getRequest(url, headers):
    return requests.request(url=url, headers=headers, method="GET")

def getLyrics(url, headers):
    req = getRequest(url, headers)
    html = BeautifulSoup(req.text, "html.parser")
    [h.extract() for h in html('script')]
    lyrics = html.find("div", class_="lyrics").get_text()

    #signify where to split lines
    lyrics = lyrics.replace("\n\n", "@@@")
    lyrics = lyrics.replace("\n", "@@@")
    lyrics = lyrics.split('@@@')

    #remove empty chars at beginning and end
    lyrics = lyrics[1:len(lyrics)-1]
    return lyrics

def checkClass(lyric):
    sample = lyric.lower()
    if sample.find('verse') != -1:
        return 0
    elif sample.find('chorus') != -1:
        return 1
    else:
        return 2

def splitLyrics(lyrics):
    data = []
    labels = []

    currLyrics = ''
    currClass = -1
    for line in lyrics:
        if line.find('[') != -1:
            if currClass != -1:
                data.append(currLyrics)
                labels.append(currClass)
            currLyrics = ''
            currClass = checkClass(line)
        else:
            currLyrics += line + ' '

    return data, labels

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-d', dest='data')
    args = parser.parse_args()

    songs = readData(args.data)

    X = []
    y = []
    for song in songs:
        lyrics = getLyrics(song, HEADERS)
        data, label = splitLyrics(lyrics)
        X += data
        y += label

    writeData(X, y, 'lyricData.txt')
