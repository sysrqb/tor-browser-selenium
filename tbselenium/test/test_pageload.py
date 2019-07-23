import unittest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.test import TBB_PATH
from tbselenium.common import CHECK_TPO_URL, LAUNCH_NEW_TBB_TOR
from tbselenium.utils import disable_js


import time
import csv
import random
import json
import os


"""
Test adapted from
https://github.com/onkeltom/browser_pageloadspeed/blob/ad3c962a0bee43beeeb1e8da46f21238b795f935/ff_loadtest.py

See for more details:
https://hacks.mozilla.org/2017/11/comparing-browser-page-load-time-an-introduction-to-methodology/
"""

class PageLoadTest(unittest.TestCase):

    def test_pageload(self):
        # define unique results file for this run
        ts = int(time.time())
        filename = "perftimings_firefox_" + str(ts) + ".csv"

        # open list of urls for testing. Find the current path for the file
        # (we don't care if it's absolute, relative, or a link - we only care
        # it works)
        path = os.path.dirname(__file__)
        with open(path + '/' + 'test_data/news.txt', 'r') as url_file:
            test_urls = url_file.readlines()

        # TODO This does not work, can it or do we need another measurement vector?
        #script = """
        #const { BrowserLoader } = ChromeUtils.import(
        #  "resource://devtools/client/shared/browser-loader.js", {});
        #const require = window.windowRequire = BrowserLoader({
        #  baseURI: "resource://devtools/client/netmonitor/",
        #  window,
        #}).require;

        #let har = gBrowser.devtools.network.getHAR();
        #"""

        # do 10 runs
        for x in range(0,10):
            # Currently, |privacy.resistFingerprinting| must be false so
            # |window.performance.timing| returns useful values.
            #
            # TODO This doesn't work. Pref must be set in the Firefox user
            # profile before running the test.
            #prefs={'privacy.resistFingerprinting': False,}

            # TODO Add support for using the bundled tor instead of relying on a local service
            # or using stem.
            #tor_cfg=LAUNCH_NEW_TBB_TOR
            #with TBDriverFixture(TBB_PATH, tor_cfg=tor_cfg, pref_dict=prefs) as driver:

            with TBDriverFixture(TBB_PATH) as driver:
                # set page load time out to 60 seconds
                driver.set_page_load_timeout(60)
                
                # randomly shuffle list of urls to avoid order bias in testing
                random.shuffle(test_urls)
            
                for i, url in enumerate(test_urls):
                    url = url[:-1]
                                
                    try:
                        # request url from list
                        driver.get(url)
                        
                        # pull window.performance.timing after loading the page and add information about url and number of run
                        perf_timing = None
                        #with driver.context(FirefoxDriver.CHROME_CONTEXT):
                        #    perf_timings = driver.execute_script("return window.performance.timing")
                        #    perf_timings['url'] = str(url)
                        #    perf_timings['run'] = str(x)

                        perf_timings = driver.execute_script("return window.performance.timing")
                        perf_timings['url'] = str(url)
                        perf_timings['run'] = str(x)
                        
                        # write perf_timings to results csv file
                        if os.path.exists(filename):
                            #append_write = 'a' # append if already exists
                            with open(filename, 'a') as results_file:
                                csvwriter = csv.writer(results_file)
                                csvwriter.writerow(perf_timings.values())
                        else:
                            #append_write = 'w' # make a new file if not
                            with open(filename, 'w') as results_file:
                                csvwriter = csv.writer(results_file)
                                csvwriter.writerow(perf_timings.keys())
                                csvwriter.writerow(perf_timings.values())
            
            
                    except: # what to do in case that an exception is thrown (which happens usually upon page load timeout)
            
                        # also pull data and store it to the results file
                        perf_timings = driver.execute_script("return window.performance.timing")
                        perf_timings['url'] = str(url)
                        perf_timings['run'] = str(x)
                        
                        if os.path.exists(filename):
                            #append_write = 'a' # append if already exists
                            with open(filename, 'a') as results_file:
                                csvwriter = csv.writer(results_file)
                                csvwriter.writerow(perf_timings.values())
                        else:
                            #append_write = 'w' # make a new file if not
                            with open(filename, 'w') as results_file:
                                csvwriter = csv.writer(results_file)
                                csvwriter.writerow(perf_timings.keys())
                                csvwriter.writerow(perf_timings.values())
            
                        continue
            			  
                driver.quit()

if __name__ == "__main__":
    unittest.main()
