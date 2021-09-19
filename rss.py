import feedparser
from re import sub

def ShowText(TextOut):
        # Replace special characters, whch are not available in font
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'ue','ß':'ss','–':'-',' ':' ','<br':'','/>':'','C<br':'C'}
        for char in chars:
            TextOut = TextOut.replace(char,chars[char])
        return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', '', TextOut) 

#NewsFeed = feedparser.parse("https://www.tagesschau.de/xml/rss2_https/")
#NewsFeed = feedparser.parse("https://www.ntg24.de/rssfeed_aktien.xml")
#NewsFeed = feedparser.parse("https://www.wetter.com/wetter_rss/wetter.xml")
#NewsText = NewsFeed.entries[0].title+": "+NewsFeed.entries[0].content[1].value
#print(NewsFeed.entries[1].title)
#print(NewsFeed['feed']['title'])
#print(NewsFeed.entries[1].content[0])
print(ShowText('Hallo & - . % ? =(liebe Freunde) :'))
#print(NewsFeed.entries[0].content[1].value)