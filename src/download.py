
import os
import urllib2

def cache(self, cache_name, content):
    f = open(cache_file, 'w')
    f.write(content)
    f.close()
    return out

def get_and_cache(self, cache_name, url):
    cache_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/cache"
    cache_file = cache_dir + "/" + cache_name
    
    # make cache dir if not created
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if not os.path.exists(cache_file):          
      while True:
          try:
              u = urllib2.urlopen(url)
              out = u.read()
              cache(cache_name, out)
              return out
          except urllib2.URLError:
              print "Failed to download " + url
              time.sleep(1)
    else:   
        f = open(cache_file, 'r')
        out = f.read()
        f.close()
        return out
