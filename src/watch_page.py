
import re
from bs4 import BeautifulSoup

# TODO:
#   load more suggestions
#  duration?
# thumb can get later easy via id

import download

class WatchPage():
    def __init__(self, video_id):
        self._video_id = video_id
        
        self._html = download.get_and_cache('video-' + video_id + '.html', self.url())
        self._soup = BeautifulSoup(self._html, "lxml")

    def video_id(self):
        return self._video_id
    
    def url(self):
        return "https://www.youtube.com/watch?v=" + self._video_id

    def title(self):
        title = ''
        for eow_title in self._soup.findAll('span', {'id': 'eow-title'}):
            title = eow_title.text.strip()

        if title == '':
            print ('WARNING: title not found')
        return title

    def description(self):
        # <meta itemprop="channelId" content="UCxCwI4zOtmeafBTTwvlmHjw">
        dom = self._soup.select('#watch-description-text')
        if len(dom) == 0:
            return None
        else:
            return dom[0].get_text()
    
    def published(self):
        dom = self._soup.select('meta[itemprop="datePublished"]')
        if len(dom) == 0:
            return None
        else:
            return dom[0]["content"]
    
    def channel(self):
        # <meta itemprop="channelId" content="UCxCwI4zOtmeafBTTwvlmHjw">
        dom = self._soup.select('meta[itemprop="channelId"]')
        if len(dom) == 0:
            return None
        else:
            return dom[0]["content"]
    
    def views(self):
        for watch_count in self._soup.findAll('div', {'class': 'watch-view-count'}):
            try:
                return self.clean_count(watch_count.contents[0])
            except IndexError:
                return None
            
    def likes(self):
        for like_count in self._soup.findAll('button', {'class': 'like-button-renderer-like-button'}):
            try:
                return self.clean_count(like_count.contents[0].text)
            except IndexError:
                return None
            
    def dislikes(self):
        for like_count in self._soup.findAll('button', {'class': 'like-button-renderer-dislike-button'}):
            try:
                return self.clean_count(like_count.contents[0].text)
            except IndexError:
                return None

    # must be same interface as Search
    def recommended(self):
        # Recommendations
        recos = []
        for link in self._soup.select('#watch7-sidebar-contents a.content-link'):
            if "/watch" in link["href"]:
                vid = link["href"].replace('/watch?v=', '') # TODO, change to regex match
                recos.append(vid)
                
        if len(recos) == 0:
            print ('Could not get a recommendation because of malformed content')
        return recos
            
    def dict(self):
        return {'id': self.video_id(),
                'published': self.published(),
                'title': self.title(),
                'description': self.description(),
                'channel': self.channel(),
                'views': self.views(),
                'likes': self.likes(),
                'dislikes': self.dislikes(),
                'recommendations': self.recommended(),
                'transcript': self.transcript()}
    
    # TODO add paragraphs to text.
    def transcript(self):
        url = self.transcript_url()
        if url ==  None:
            return None
        src = download.get_and_cache('video-' + self.video_id() + '-transcript.xml', url)
        text = ''
        for t in BeautifulSoup(src, "lxml").select('text'):
            text = text + " " + t.get_text()
        #text = xml.get_text() # doesn't strip font tags
        
        text = re.sub('</?font[^>]*>', ' ', text)# strip font tags (soup doesn't replace with a space, conjoining words)
        text = re.sub('\[[^\]]+\]', ' ', text) # remove annotations such as [Music]
        text =  BeautifulSoup(text, "lxml").get_text() # unscape html entities such as &#39;
        text = re.sub('\s+', ' ', text) # change multispaces to single
        return text
        
                
    def transcript_url(self):
        # {\"captionTracks\":[{\"baseUrl\":\"https:\/\/www.youtube.com\/api\/timedtext?v=Surdizmf_dw\\u0026expire=1502844203\\u0026signature=28A6505915769B42A0557191C4476C5A92127E90.559655AFCC6462B7543BEFF373D4F2C7220B2993\\u0026sparams=asr_langs%2Ccaps%2Cv%2Cexpire\\u0026key=yttt1\\u0026asr_langs=ko%2Cde%2Cen%2Cfr%2Cja%2Cru%2Ces%2Cpt%2Cit%2Cnl\\u0026hl=en_US\\u0026caps=asr\\u0026kind=asr\\u0026lang=en\",
        prefix = 'https:\/\/www.youtube.com\/api\/timedtext'.replace('\\', '\\\\').replace('/', '\/')
        #print prefix
        #m = re.search('https:\?/\?/www.youtube.com\?/api\?/timedtext[^"]+', self._html)
        m = re.search("(" + prefix + '[^\"]+)\\\\\",', self._html)
        if m == None:
            return None
        else:
            return m.group(1).replace('\/', '/').replace('\\\u0026', '&')
            
    
    def clean_count(self, text_count):
        # Ignore non ascii
        ascii_count = text_count.encode('ascii', 'ignore')
        # Ignore non numbers
        p = re.compile('[\d,]+')
        return int(p.findall(ascii_count)[0].replace(',', ''))

    
