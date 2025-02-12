import requests
import json
import time
import sys
from typing import Optional, Union, List

class Crawl4AiTester:
    def __init__(self, base_url: str = "http://[url]", api_token: str = "[token]"): #Change the url to match your URL
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def submit_and_wait(self, request_data: dict, timeout: int = 300) -> dict:
        # Submit crawl job with authorization header
        response = requests.post(
            f"{self.base_url}/crawl", 
            json=request_data,
            headers=self.headers
        )
        task_id = response.json()["task_id"]
        print(f"Task ID: {task_id}")

        # Poll for result with authorization header
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task {task_id} timeout")
            result = requests.get(
                f"{self.base_url}/task/{task_id}",
                headers=self.headers
            )
            status = result.json()
            if status["status"] == "completed":
                return status
            time.sleep(2)

    def crawl(self, 
              urls: Union[str, List[str]], 
              extraction_type: str = "basic",
              extraction_params: Optional[dict] = None,
              priority: int = 10,
              ttl: int = 3600) -> dict:
        
        request = {
            "urls": urls,
            "extraction_config": {
                "type": extraction_type,
                "params": extraction_params or {}
            },
            "priority": priority,
            "ttl": ttl
        }
        
        result = self.submit_and_wait(request)
        return result

def display_result(result: dict):
    """Display the crawled content in a structured way"""
    print("\n=== Crawl Result ===")
    print(f"Status: {result['status']}")
    
    if 'result' in result:
        if 'markdown' in result['result']:
            print("\n=== Content (Markdown) ===")
            print(result['result']['markdown'][:1000] + "...\n")  # Show first 1000 chars
        
        if 'text' in result['result']:
            print("\n=== Content (Text) ===")
            print(result['result']['text'][:1000] + "...\n")
            
        if 'html' in result['result']:
            print("\n=== Content (HTML) ===")
            print(result['result']['html'][:1000] + "...\n")
            
        # Save complete result to file
        with open('crawl_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\nComplete result saved to 'crawl_result.json'")

def test_deployment():
    tester = Crawl4AiTester(api_token="test123")
    
    # Let user choose extraction method
    print("\nAvailable extraction methods:")
    print("1. basic - Simple HTML to text extraction")
    print("2. llm - LLM-based extraction")
    print("3. cosine - Cosine similarity based extraction")
    print("4. json_css - CSS selector based extraction")
    
    method = input("\nChoose extraction method (1-4): ")
    extraction_types = {
        "1": "basic",
        "2": "llm",
        "3": "cosine",
        "4": "json_css"
    }
    
    # Get URL(s)
    urls = input("\nEnter URL(s) to crawl (comma-separated for multiple): ")
    urls = [url.strip() for url in urls.split(",")] if "," in urls else urls
    
    # Get priority
    priority = int(input("\nEnter priority (1-10): ") or "10")
    
    # Additional params for specific methods
    extraction_params = {}
    if method == "4":  # json_css
        selectors = input("\nEnter CSS selectors (comma-separated): ")
        extraction_params["selectors"] = [s.strip() for s in selectors.split(",")]
    
    result = tester.crawl(
        urls=urls,
        extraction_type=extraction_types[method],
        extraction_params=extraction_params,
        priority=priority
    )
    
    display_result(result)

if __name__ == "__main__":
    test_deployment()
