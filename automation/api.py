from curl_cffi import requests
import time

def get_posts():
    url = "https://jsonplaceholder.typicode.com/posts"
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                impersonate="chrome",
                timeout=10
            )
            print("API Status:", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                print("Posts received:", len(data))
                return data[:10]
            else:
                print(f"API failed (status {response.status_code}), attempt {attempt+1}/{max_retries}")
                
        except Exception as e:
            print(f"API attempt {attempt+1}/{max_retries} ERROR: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(1)
    
    print("All API retries failed. Using fallback posts.")
    # Simple fallback dummy posts
    fallback_posts = [
        {"id": 1, "title": "Fallback Post 1", "body": "This is fallback content when API fails."},
        {"id": 2, "title": "Fallback Post 2", "body": "Automation continues gracefully."},
    ]
    return fallback_posts

