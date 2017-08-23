import os
import sys
# Add parent dir to PYTHONPATH
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src"
sys.path.append(src_path)

import unittest
import youtube_watch_page

print_dbg = True #False

class TestYoutubeWatchPage(unittest.TestCase):

    def test_gets_data_having_closed_captions(self):
        vid = 'Surdizmf_dw'
        p = youtube_watch_page.YoutubeWatchPage(vid)
        
        self.assertEqual('White Power (Watch to the end!)', p.title())
        self.assertGreater(p.views(), 1071330)
        self.assertGreater(p.likes(), 7950)
        self.assertGreater(p.dislikes(), 6410)
        self.assertTrue('white knights' in p.transcript())
        self.assertIsNotNone(p.dict())
        
        if print_dbg:
            print "dict " + str( p.dict())
            print "Views " + str( p.views())
            print "likes " + str( p.likes())
            print "dislikes " + str( p.dislikes())
            print "recommended " + str( p.recommended())
            print "title " + str( p.title()) # 
            print "trans url " + str( p.transcript_url()) 
            print "transcript " + str( p.transcript())
            print "dict " + str( p.dict())
        
    def test_gets_data_having_no_closed_captions(self):
        vid = 'gDl01PngkMo'
        p = youtube_watch_page.YoutubeWatchPage(vid)
        
        self.assertEqual('White Pride Worldwide', p.title())
        self.assertGreater(p.views(), 30800)
        self.assertGreater(p.likes(), 400)
        self.assertGreater(p.dislikes(), 60)
        self.assertEqual(p.transcript(), None)
        self.assertIsNotNone(p.dict())
        
        if print_dbg:
            print "dict " + str( p.dict())
            print "Views " + str( p.views())
            print "likes " + str( p.likes())
            print "dislikes " + str( p.dislikes())
            print "recommended " + str( p.recommended())
            print "title " + str( p.title()) # 
            print "trans url " + str( p.transcript_url()) 
            print "transcript " + str( p.transcript())
            print "dict " + str( p.dict())

if __name__ == '__main__':
    unittest.main()
