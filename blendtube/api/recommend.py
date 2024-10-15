from youtubesearchpython import VideosSearch

def recommendURLs(urls: list) -> list:
    return_lst = []
    
    for url in urls:
        videosSearch = VideosSearch(url, limit=2)
        results = videosSearch.result()['result']
        
        search_result_urls = []
        
        for result in results:
            search_result_urls.append(result['link'])
        
        return_lst.append(search_result_urls)
    
    return return_lst