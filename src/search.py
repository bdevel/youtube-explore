
class Search():
    def __init__(self, search_phrase, language):
        self._search_phrase = search_phrase
        self._language = language


    
    def follow_recommendations(self, search_phrase, search_results, branching, depth):
        search_results = self._get_search_results(search_phrase, search_results)
        print ('Search results ' + repr(search_results))

        all_recos = []
        for video in search_results:
            all_recos.extend(self.get_n_recommendations(video, branching, depth))
            print ('\n\n\nNext search: ')
            all_recos.extend(search_results)
        return all_recos



    def _get_search_results(self, search_phrase, max_results, top_rated=False):
            assert max_results < 20, 'max_results was not implemented to be > 20'

        if self._verbose:
            print ('Searching for {}'.format(search_phrase))

        # Trying to get results from cache
        if search_phrase in self._search_infos and len(self._search_infos[search_phrase]) >= max_results:
            return self._search_infos[search_phrase][0:max_results]

        # Escaping search terms for youtube
        escaped_search_phrase = urllib2.quote(search_phrase.encode('utf-8'))

        # We only want search results that are videos, filtered by viewcoung.
        #  This is achieved by using the youtube URI parameter: sp=CAMSAhAB
        if self._alltime:
            filter = "CAMSAhAB"
        else:
            if top_rated:
                filter = "CAE%253D"
            else:
                filter = "EgIQAQ%253D%253D"

        url = "https://www.youtube.com/results?sp=" + filter + "&q=" + escaped_search_phrase
        if self._gl:
            url = url + '&gl=' + self._gl

        print ('Searching URL: ' + url)

        headers = {}
        if self._language:
            headers["Accept-Language"] = self._language
            url_request = urllib2.Request(url, headers=headers)
            html = urllib2.urlopen(url_request)
            soup = BeautifulSoup(html, "lxml")

        videos = []
        for item_section in soup.findAll('div', {'class': 'yt-lockup-dismissable'}):
            video = item_section.contents[0].contents[0]['href'].split('=')[1]
            videos.append(video)

        self._search_infos[search_phrase] = videos
        return videos[0:max_results]

