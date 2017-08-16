    def print_graph(self, links_per_video, only_mature_videos=True):
        input_links_counts = self.count_recommendation_links()
        graph = {}
        nodes = []
        links = []
        for video_id in self._video_infos:
            video = self._video_infos[video_id]
            if video['likes'] < MATURITY_THRESHOLD:
                popularity = -1
            else:
                popularity = video['likes'] / float(video['likes'] + video['dislikes'] + 1)

            if self.video_is_mature(video):
                nodes.append({'id': video_id, 'size': input_links_counts.get(video_id, 0), 'popularity': popularity, 'type': 'circle', 'likes': video['likes'], 'dislikes': video['dislikes'], 'views': video['views'], 'depth': video['depth']})
                link = 0
            for reco in self._video_infos[video_id]['recommendations']:
                if reco in self._video_infos:
                    if self.video_is_mature(self._video_infos[video_id]) and self.video_is_mature(self._video_infos[reco]):
                        links.append({'source': video_id, 'target': reco, 'value': 1})
                        link += 1
                    if link >= links_per_video:
                        break
                    graph['nodes'] = nodes
                    graph['links'] = links
        with open('./graph-' + self._name + '.json', 'w') as fp:
            json.dump(graph, fp)
            date = time.strftime('%Y-%m-%d')
        with open('./graph-' + self._name + '-' + date + '.json', 'w') as fp:
            json.dump(graph, fp)
            print ('Wrote graph as: ' + './graph-' + self._name + '-' + date + '.json')
