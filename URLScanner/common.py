# External / System
from threading import Lock

# List of URL found (always use wrapped by g_mMutex)
g_tabstrUrlsFound: list[str] = []

# List of URL analysed (always use wrapped by g_mMutex)
g_tabstrUrlsAnalysed: list[str] = []

# Mutex (to protect g_tabstrUrlsFound and g_tabstrUrlsAnalysed)
g_mMutex: Lock = Lock()

# Root URL
g_strRootUrl: str= ""