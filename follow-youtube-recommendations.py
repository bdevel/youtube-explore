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
import search

from bs4 import BeautifulSoup


RECOMMENDATIONS_PER_VIDEO = 1
RESULTS_PER_SEARCH = 1

# NUMBER OF MIN LIKES ON A VIDEO TO CONSIDER IT
MATURITY_THRESHOLD = 5

# incriment the lowest index item,
# roll while item < index max_list
# Note, if you say [2,2] then the
# max the list will get to is [1,1],
# as zero counts as an item
def inc_list(lst, max_list):
    for i,m in enumerate(max_list):
        if i >= len(lst):
            break
        
        lst[i] = lst[i] + 1 # inc
        
        # reset if at limit
        if lst[i] >= max_list[i]:
            lst[i] = 0
            if i + 1 >= len(lst):
              # go to 0 of next depth,
              lst.append(0)
              if len(lst) > len(max_list):
                return None# None left
              break
            else:
                continue # inc next depth
        else:
            break
    return lst


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

        


    def get_video_details(self, video_id):
        # Pull from cache or download new copy
        if video_id in self._video_infos:
            return self._video_infos[video_id]
        else:
            page = youtube_watch_page.YoutubeWatchPage(video_id)
            data = page.dict()
            self._video_infos[video_id] = data
            return data
        
    # def get_recommendations(self, video_id, nb_recos_wanted, depth):
    #     data = self.get_video_details(video_id)
    #     data['depth'] = depth
    #     print (repr(data['title'] + ' ' + str(data['views']) + ' views , depth: ' + str(data['depth'])))
    #     #print (repr(data['recommendations']))

    #     return data['recommendations']

    # def get_n_recommendations(self, seed, branching, depth):
    #     if depth is 0:
    #         return [seed]
    #     current_video = seed
    #     all_recos = [seed]
    #     for video in self.get_recommendations(current_video, branching, depth):
    #         all_recos.extend(self.get_n_recommendations(video, branching, depth - 1))
    #     return all_recos

    # def next_path(self, path, r, b, d):
    #     # is []
    #     if len(path) == 0:
    #         path.append(0)
    #         return path
        
    #     # is [x .  . ] < max r 
    #     elif p[0] < r - 1:# still below max r
    #         p[0] = p[0] + 1 # inc first
    #         return p
        
    #     elif p[0] >= r:
    #         # 
    #         p[1] = p[1] = 0# reset
    #         if len(p) == 1:
    #             p.append(0) # go to next depth
    #             return p
    #         else:
    #             p[1] = p[1] + 1
    #             return p
    #         return p
        
    #     elif p[2] >= b:
    #         p[2] = p[2] = 0# reset
    #         if len(p) == 1:
    #             p.append(0) # go to next depth
    #             return p
    #         else:
    #             p[2] = p[2] + 1
    #             return p
    #         return p
        
    #      elif p[3] >= :
    #          p[2] = p[2] = 0# reset
    #         if len(p) == 1:
    #             p.append(0) # go to next depth
    #             return p
    #         else:
    #             p[2] = p[2] + 1
    #             return p
    #         return p
    
    def process_watch_page(self, page, path):
        data = page.dict()
        print data['title']
        # save file
        # Get channel info

    # returns a WatchPage object for the recommedation at nth recommendations
    # of successive depths.
    # Example, [0,0,0]
    #   gets first result item's, first recommendestion's, first recommendation    
    def recommended_page_at(self, page, path):
        if len(path) > 0:
            # get child since we aren't at the end yet
            nth = path[0]
            next_path = path[1:]
            
            # get page of recommendation
            recs = page.recommended()
            if nth >= len(recs):
                print "End of list. Unable to get " + str(path)
                return None
            child = WatchPage(recs[nth])
            return self.recommended_page_at(child, next_path)
        else:
            # if [] that means end of path, we win!
            return page
        
    def follow_from_search(self, search_term, search_qty, branches, depth):
        results = search.Search(search_term, self._language, self._gl)

        max_path = [search_qty]
        max_path.extend([branches] * depth) # -1 to count the search as a level
        
        path = [0]# start at first search result item
        while path != None:
            print "At: " + str(path)
            page = self.recommended_page_at(results, path)
            self.process_watch_page(page, path)
            path = inc_list(path, max_path)
        
        #rec_path = [] # first time around this is the result videos
        # while True:
        #     print "At level " + str(rec_path)
        #     for vid in video_ids:
        #         page = youtube_watch_page.YoutubeWatchPage(vid)
        #         r = page.recommendation_at(rec_path)
                
        #     if len(rec_path) == 0: # []
        #         rec_path.append(0)
                
        #     elif rec_path[0:1] == search_qty
        #         rec_path.append(0)
            
            #if rec_path != [search_results, branching, depth]:
            #    break
            
        
        # Crawl priority: To capture videos closest to the term.
        # We will build out the base first and not deep too fast.
        # So the plan is to draw one layer at a time.
        # Depth 0
        # First we load the pages for every result.
        # Depth 1
        # Next we go to the first rec from the first search result.
        # Then first rec of second result, etc.
        # Depth n
        # After n-1 rec of each result is done, do nth rec
        # search => recommend0
        #        => recommend1
        #        => recommend2
        #        => recommend0 => rec0
        #        => recommend1 => rec0
        #        => recommend2 => rec0
        #        => recommend0 => rec1
        #        => recommend1 => rec1
        #        => recommend2 => rec1
        
        # Alternative crawl
        # We want to many thin deep strands from the root
        # search => recommend0 => rec0 => rec0 => rec0
        #        => recommend1 => rec0 => rec0 => rec0
        
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
def compare_keywords(query, search_qty, branches, depth, name, gl, language):
    total_results = search_qty * branches * depth
    print "Total of " + str(total_results) + " videos will be processed."

    
    date = time.strftime('%Y-%m-%d')
    file_name = 'results/' + name + '-' + date + '.json'
    print ('Running, will save the resulting json to:' + file_name)
    top_videos = {}
    for keyword in query.split(','):
        yf = YoutubeFollower(verbose=True, name=keyword, alltime=False, gl=gl, language=language)
        top_recommended, counts = yf.follow_from_search(keyword,
                          search_qty=search_qty,
                          branches=branches,
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
