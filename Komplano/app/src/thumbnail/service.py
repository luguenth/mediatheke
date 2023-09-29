from bs4 import BeautifulSoup
import requests

def fetch_thumbnail(url) -> str:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        meta_tags = soup.find_all('meta')
        
        for meta_tag in meta_tags:
            if meta_tag.get('property') == 'og:image' or meta_tag.get('name') == 'twitter:image':
                thumbnail_url = meta_tag.get('content')
                
                if thumbnail_url.startswith('/'):
                    return f"{url.split('/')[0]}//{url.split('/')[2]}{thumbnail_url}"
                
                return thumbnail_url  # Return as soon as you find the thumbnail
        
        return ""
    
    except Exception as e:
        print(f"Something went wrong: {e}")
        return "An error occurred while fetching the thumbnail"
    
