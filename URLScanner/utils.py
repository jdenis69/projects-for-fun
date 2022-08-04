# External / System
import requests
import re
import logging
import threading
# Locals
from common import *

def GetRootUrl(strUrl : str):
	indexPrefix = strUrl.find('//')
	if indexPrefix==-1:
		exit(-1)
	indexPrefix+=2
	
	indexEndOfTopDomain = strUrl.find('/', indexPrefix)
	if indexEndOfTopDomain==-1:
		setRootUrl=strUrl
	else:
		setRootUrl=strUrl[0:indexEndOfTopDomain]

	return setRootUrl

def SetRootUrl(strUrl : str):
	global g_strRootUrl

	g_strRootUrl=strUrl

def GetDomainFromUrl(strUrl : str) -> str:
	rePattern=re.compile(r'(https?://|www\.)?(www\.)?([a-z0-9-]+)(\..+)?')
	strDomain=rePattern.sub(r'\3', strUrl)
	return strDomain

def FindUrlsFromRootUrl(strTargetedUrl : str):
	global g_tabstrUrlsFound
	global g_tabstrUrlsAnalysed
	global g_mMutex
	global g_strRootUrl
	
	logging.debug("Analysing <%s>...", strTargetedUrl)

	# Sending request to get HTML content
	# We could add more HTTP Headers and other stuff to customise it
	try:
		tabstrHeaders = {
			'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
			'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
		}
		req=requests.get(strTargetedUrl, allow_redirects=True, headers=tabstrHeaders)
	except:
		logging.debug("<%s>: invalid request", strUrl)
		return

	# Could be a good idea to manage HTTP Redirect code...
	if req.status_code!=200:
		logging.debug("<%s>: HTTP Error %d", strUrl, req.status_code)
		return

	# Find all links from HTML tag (<a href=""></a>)
	strRootHTML=req.text
	rePattern=r'href=[\'"]?([^\'" >]+)'
	tabreMatches=re.findall(rePattern, strRootHTML)
	ceURLsFound=0

	# Format link to get a valid URL start with strTargetedUrl
	for strUrl in tabreMatches:
		# If URL seems to be from another website, we skip it
		if re.search(r'[^.]*\.[^.]{2,3}(?:\.[^.]{2,3})?$', strUrl):
			logging.debug("<%s> seems to came from another domain or has an extension not supported", strUrl)
			continue
		# Cleaned URL (no useless '/' etc.)
		strUrlCleaned=""
		# Clear URL ending with '/'
		while strUrl.endswith('/')!=False:
			strUrl=strUrl[:-1]
		# Is the URL already within a known url ?
		g_mMutex.acquire()
		str_match=[s for s in g_tabstrUrlsAnalysed if s.__contains__(strUrl)]
		g_mMutex.release()
		if str_match:
			logging.debug("<%s>: already analysed (2)", strUrl)
			continue

		# Concatenate strUrl starting with '/' with g_strRootUrl
		if strUrl.startswith('/')!=False:
			while strUrl.startswith('/')!=False:
				strUrl=strUrl[1:]
			strUrlCleaned=g_strRootUrl+"/"+strUrl
		# Keep URL starting with targeted URL
		elif strUrl.startswith(strTargetedUrl)!=False:
			strUrlCleaned=strUrl

		# Keep URL if not exists AND not analysed
		if strUrlCleaned!="":
			g_mMutex.acquire()
			str_match=[s for s in g_tabstrUrlsFound if s.__contains__(strUrl)]
			if str_match:
				logging.debug("<%s>: already found", strUrl)
				g_mMutex.release()
				continue
			if (not strUrlCleaned in g_tabstrUrlsFound) and (not strUrlCleaned in g_tabstrUrlsAnalysed) :
				logging.debug("<%s>: will be analyse later", strUrlCleaned)
				g_tabstrUrlsFound.append(strUrlCleaned)
				ceURLsFound+=1 
			g_mMutex.release()

	# URL Already analysed by another worker ?
	g_mMutex.acquire()
	if not strTargetedUrl in g_tabstrUrlsAnalysed:
		g_tabstrUrlsAnalysed.append(strTargetedUrl)
	else:
		logging.debug("<%s>: already analysed (1)", strTargetedUrl)
		g_mMutex.release()
		return 
	g_mMutex.release()

	# Logging
	if ceURLsFound==0:
		logging.info("<%s> has been analysed. No new URLs found", strTargetedUrl)
	else:
		logging.info("<%s> has been analysed. %d new URLs to analyse", strTargetedUrl, ceURLsFound)