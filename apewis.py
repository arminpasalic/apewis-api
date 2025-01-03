import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

@dataclass
class StockMention:
    rank: int
    ticker: str
    name: str
    mentions: int
    upvotes: int
    rank_24h_ago: Optional[int]
    mentions_24h_ago: Optional[int]

class ApeWisdomAPI:
    BASE_URL = "https://apewisdom.io/api/v1.0"
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0

    def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()

    def get_mentions(self, filter_type: str = "all-stocks", page: int = 1) -> Dict:
        self._rate_limit_wait()
        url = f"{self.BASE_URL}/filter/{filter_type}/page/{page}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def _safe_int_convert(self, value) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def get_all_mentions(self, filter_type: str = "all-stocks") -> List[StockMention]:
        all_mentions = []
        page = 1
        
        while True:
            data = self.get_mentions(filter_type, page)
            
            mentions = [
                StockMention(
                    rank=result["rank"],
                    ticker=result["ticker"],
                    name=result["name"],
                    mentions=self._safe_int_convert(result["mentions"]) or 0,
                    upvotes=self._safe_int_convert(result["upvotes"]) or 0,
                    rank_24h_ago=self._safe_int_convert(result["rank_24h_ago"]),
                    mentions_24h_ago=self._safe_int_convert(result["mentions_24h_ago"])
                )
                for result in data["results"]
            ]
            
            all_mentions.extend(mentions)
            
            if page >= data["pages"]:
                break
                
            page += 1
            
        return all_mentions

def main():
    api = ApeWisdomAPI(rate_limit=1.0)
    
    page_data = api.get_mentions("all-stocks", page=1)
    print(f"First page results: {len(page_data['results'])} mentions")
    
    all_mentions = api.get_all_mentions("all-stocks")
    print(f"\nTotal mentions collected: {len(all_mentions)}")
    
    print("\nTop 5 mentioned stocks:")
    for mention in sorted(all_mentions, key=lambda x: x.mentions, reverse=True)[:5]:
        print(f"{mention.ticker}: {mention.mentions} mentions, {mention.upvotes} upvotes")

if __name__ == "__main__":
    main()