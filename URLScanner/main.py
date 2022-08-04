# External / System
import sys
import logging
import time
import concurrent.futures
import validators
import tempfile
import os
from threading import Thread
# Locals
from common import *
from utils import *

if __name__ == "__main__":

    # Basic testing
    if len(sys.argv)<2:
        print("Usage: main.py [--debug] URLToScan")
        exit(-1)

    # Debug or Info + URL
    if len(sys.argv)==3 and sys.argv[1]=="--debug":
        strLevel=logging.DEBUG
        strTargetedUrl=sys.argv[2]
    else:
        strLevel=logging.INFO
        strTargetedUrl=sys.argv[1]
    
    # Root URL Cleaned
    while strTargetedUrl.endswith('/')!=False:
        strTargetedUrl=strTargetedUrl[:-1]

    if not validators.url(strTargetedUrl):
        print("<"+strTargetedUrl+"> is not a valid URL")
        exit(-1)

    # Logging
    strURLDomain=GetDomainFromUrl(strTargetedUrl)
    strLogName="links_from_"+strURLDomain+".log"
    strTmpDir=tempfile.gettempdir()
    strLogPath=strTmpDir+'\\'+strLogName
    strLogFormat="%(asctime)s: %(message)s"
    if os.path.exists(strLogName):
        os.remove(strLogName)
    logging.basicConfig(filename=strLogPath,
                        filemode='w',
                        format=strLogFormat,
                        level=strLevel,
                        datefmt="%H:%M:%S")

    print('Logging is available at <'+strLogPath+'>')

    # We make RootURL global so it can be used by other functions
    strRootUrl=GetRootUrl(strTargetedUrl)
    SetRootUrl(strRootUrl)

    # Analysing...
    g_tabstrUrlsFound.append(strTargetedUrl);
    ceWorkers=64
    tabstrUrls=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=ceWorkers) as executor:
        while True:
            g_mMutex.acquire()
            ceURLsLeft=len(g_tabstrUrlsFound)
            logging.info("URLs (found=%d, analysed=%d)", ceURLsLeft, len(g_tabstrUrlsAnalysed))
            if ceURLsLeft==0:
                g_mMutex.release()
                exit(-1)
            else:
                # Analysing a maximum of ceWorkers URL simultaneously
                i=0
                tabstrUrls.clear()
                while (i<ceWorkers) and (i<ceURLsLeft):
                    strUrl=g_tabstrUrlsFound.pop(0) 
                    if not strUrl in g_tabstrUrlsAnalysed:
                        tabstrUrls.append(strUrl)
                        i+=1
                    ceURLsLeft-=1
            g_mMutex.release()

            if i>0:
                futures=[executor.submit(FindUrlsFromRootUrl, strUrl) for strUrl in tabstrUrls]
                logging.debug("Waiting for %d tasks to complete...", i)
                concurrent.futures.wait(futures)