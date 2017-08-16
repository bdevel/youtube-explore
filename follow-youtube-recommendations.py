__author__ = 'Guillaume Chaslot'

"""
    This scripts starts from a search query on youtube and:
        1) gets the N first search results
        2) follows the first M recommendations
        3) repeats step (2) P times
        4) stores the results in a json file
"""


import os
import sys
src_path = os.path.dirname(os.path.abspath(__file__)) + "/src"
sys.path.append(src_path)

import urllib2
import re
import json
import sys
import argparse
import time
import youtube_watch_page

from bs4 import BeautifulSoup


RECOMMENDATIONS_PER_VIDEO = 1
RESULTS_PER_SEARCH = 1

# NUMBER OF MIN LIKES ON A VIDEO TO CONSIDER IT
MATURITY_THRESHOLD = 5

class YoutubeFollower():
    def __init__(self, verbose=False, name='', alltime=True, gl=None, language=None):
        # Name
        self._name = name
        self._alltime = alltime
        self._verbose = verbose

        # Dict video_id to {'likes': ,
        #                   'dislikes': ,
        #                   'views': ,
        #                   'recommendations': []}
        self._video_infos = {} # self.try_to_load_video_infos()

        # Dict search terms to [video_ids]
        self._search_infos = {}
        self._gl = gl
        self._language = language

        print ('Location = ' + repr(self._gl) + ' Language = ' + repr(self._language))


    def get_video_details(self, video_id):
        # Pull from cache or download new copy
        if video_id in self._video_infos:
            return self._video_infos[video_id]
        else:
            page = youtube_watch_page.YoutubeWatchPage(video_id)
            data = page.dict()
            self._video_infos[video_id] = data
            return data
        
    def get_recommendations(self, video_id, nb_recos_wanted, depth):
        data = self.get_video_details(video_id)
        data['depth'] = depth
        print (repr(data['title'] + ' ' + str(data['views']) + ' views , depth: ' + str(data['depth'])))
        #print (repr(data['recommendations']))

        return data['recommendations']

    def get_n_recommendations(self, seed, branching, depth):
        if depth is 0:
            return [seed]
        current_video = seed
        all_recos = [seed]
        for video in self.get_recommendations(current_video, branching, depth):
            all_recos.extend(self.get_n_recommendations(video, branching, depth - 1))
        return all_recos
    
    # tsr 1
    def follow_from_search(self, search_term, search_results, branching, depth):
        search.results(search_term, search_results, branching, depth) 
        all_recos = self.compute_all_recommendations_from_search(search_term, search_results, branching, depth)
        counts = self.count(all_recos)
        print ('\n\n\nSearch term = ' + search_term + '\n')
        print ('counts: ' + repr(counts))
        sorted_videos = sorted(counts, key=counts.get, reverse=True)
        return sorted_videos, counts



    def count(self, iterator):
        counts = {}
        for video in iterator:
            counts[video] = counts.get(video, 0) + 1
        return counts
    def save_video_infos(self, keyword):
        print ('Wrote file:')
        date = time.strftime('%Y%m%d')
        with open('data/video-infos-' + keyword + '-' + date + '.json', 'w') as fp:
            json.dump(self._video_infos, fp)

    def try_to_load_video_infos(self):
        try:
            with open('data/video-infos-' + self._name + '.json', 'r') as fp:
                return json.load(fp)
        except Exception as e:
            print ('Failed to load from graph ' + repr(e))
            return {}

    def count_recommendation_links(self):
        counts = {}
        for video_id in self._video_infos:
            for reco in self._video_infos[video_id]['recommendations']:
                counts[reco] = counts.get(reco, 0) + 1
        return counts

    def video_is_mature(self, video):
        return int(video['likes']) > MATURITY_THRESHOLD


    def get_top_rated(self, search_terms):
        top_rated_videos = self.get_search_results(self, search_terms, 20, top_rated=True)
        for video_id in top_rated_videos:
            if video_id not in self._video_infos:
                self.get_recommendations(video_id, 20, 0)
        return top_rated_videos

    def print_videos(self, videos, counts, max_length):
        idx = 1
        for video in videos[:max_length]:
            try:
                current_title = self._video_infos[video]['title']
                print (str(idx) + ') Recommended ' + str(counts[video]) + ' times: '
                    ' https://www.youtube.com/watch?v=' + video + ' , Title: ' + repr(current_title))
                if idx % 20 == 0:
                    print ('')
                idx += 1
            except KeyError:
                pass

    def get_top_videos(self, videos, counts, max_length_count):
        video_infos = []
        for video in videos:
            try:
                video_infos.append(self._video_infos[video])
                video_infos[-1]['recommendations'] = counts[video]
            except KeyError:
                pass

        # Computing the average recommendations of the video:
        # The average is computing only on the top videos, so it is an underestimation of the actual average.
        if video_infos is []:
            return []
        sum_recos = 0
        for video in video_infos:
            sum_recos += video['recommendations']
        avg = sum_recos / float(len(video_infos))
        for video in video_infos:
            video['mult'] = video['recommendations'] / avg
        return video_infos[:max_length_count]

# tsr 0    
def compare_keywords(query, search_results, branching, depth, name, gl, language):
    total_results = search_results * branching * depth
    print "Total of " + str(total_results) + " videos will be processed."

    
    date = time.strftime('%Y-%m-%d')
    file_name = 'results/' + name + '-' + date + '.json'
    print ('Running, will save the resulting json to:' + file_name)
    top_videos = {}
    for keyword in query.split(','):
        yf = YoutubeFollower(verbose=True, name=keyword, alltime=False, gl=gl, language=language)
        top_recommended, counts = yf.follow_from_search(keyword,
                          search_results=search_results,
                          branching=branching,
                          depth=depth)
        top_videos[keyword] = yf.get_top_videos(top_recommended, counts, 150)
        yf.print_videos(top_recommended, counts, 50)
        yf.save_video_infos(name + '-' + keyword)

    with open(file_name, 'w') as fp:
        json.dump(top_videos, fp)

def main():
    global parser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', help='The start search query')
    parser.add_argument('--name', help='Name given to the file')
    parser.add_argument('--searches', default='5', type=int, help='The number of search results to start the exploration')
    parser.add_argument('--branch', default='3', type=int, help='The branching factor of the exploration')
    parser.add_argument('--depth', default='5', type=int, help='The depth of the exploration')
    parser.add_argument('--alltime', default=False, type=bool, help='If we get search results ordered by highest number of views')
    parser.add_argument('--gl', help='Location passed to YouTube e.g. US, FR, GB, DE...')
    parser.add_argument('--language', help='Languaged passed to HTML header, en, fr, en-US, ...')
    # Not yet implemented
    # parser.add_argument('--makehtml', default=False, type=bool,
    #     help='If true, writes a .html page with the name which compare most recommended videos and top rated ones.')

    args = parser.parse_args()
    compare_keywords(args.query, args.searches, args.branch, args.depth, args.name, args.gl, args.language)

    return 0

if __name__ == "__main__":
    sys.exit(main())
