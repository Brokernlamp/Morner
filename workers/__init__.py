# workers/__init__.py

from .google_maps import scrape as scrape_maps
from .justdial import scrape as scrape_jd
from .indiamart import scrape as scrape_im

# This allows you to call workers.scrape_maps() 
# instead of workers.google_maps.scrape()