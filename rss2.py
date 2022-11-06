import feedparser
from re import sub

def ReadNews():
    try:
        NewsFeed = feedparser.parse("https://www.tagesschau.de/xml/rss2_https/")
        #NewsText = NewsFeed.entries[0].title+": "+NewsFeed.entries[0].content[1].value # alt
        NewsText = NewsFeed.entries[0].title+": "+NewsFeed.entries[0].description
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' ','§':'Paragraph'}
        for char in chars:
            NewsText = NewsText.replace(char,chars[char])
    except:
        NewsText = "Keine Tagesschau News ???"
    return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', ' ', NewsText)

NewsText = ReadNews();
print(NewsText);