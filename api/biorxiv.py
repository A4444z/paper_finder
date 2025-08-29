# paper_finder/api/biorxiv.py

import json
from datetime import datetime, timedelta
from . import BaseAPI
import asyncio
import aiohttp

# In-memory cache to store recent search results
BIORXIV_CACHE = {}
CACHE_EXPIRATION = timedelta(minutes=10)  # Cache results for 10 minutes

class BioRxivAPI(BaseAPI):
    """
    bioRxiv API interface, optimized with asynchronous requests for performance.
    """

    def __init__(self, base_url):
        super().__init__(base_url)

    async def fetch_page(self, session, url):
        """Asynchronously fetches data from a single page URL."""
        try:
            # Set a generous timeout for the request
            timeout = aiohttp.ClientTimeout(total=45)
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            print(f"Request timed out: {url}")
            return None
        except aiohttp.ClientError as e:
            print(f"Request failed for page: {url}, Error: {type(e).__name__}")
            return None

    async def search_async(self, query, max_results=20, **kwargs):
        """
        Concurrently fetches all pages using aiohttp, then filters the complete results.
        """
        # 1. Check cache for recent results
        cache_key = f"{query.lower().strip()}"
        if cache_key in BIORXIV_CACHE:
            timestamp, cached_results = BIORXIV_CACHE[cache_key]
            if datetime.now() - timestamp < CACHE_EXPIRATION:
                print(f"Returning cached results for '{query}'.")
                return cached_results

        # 2. Configure search parameters
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        num_pages_to_fetch = 50  # Fetch 50 pages concurrently as requested
        results_per_page = 100   # The API serves 100 results per call

        print(f"Starting concurrent search on bioRxiv for '{query}' across {num_pages_to_fetch} pages...")

        # 3. Create all concurrent request tasks
        async with aiohttp.ClientSession() as session:
            tasks = []
            for page_num in range(num_pages_to_fetch):
                # The 'cursor' is the starting record number (offset)
                cursor = page_num * results_per_page
                url = f"{self.base_url}/details/biorxiv/{start_date}/{end_date}/{cursor}"
                tasks.append(self.fetch_page(session, url))
            
            # 4. Execute all tasks and wait for them to complete
            all_page_data = await asyncio.gather(*tasks)

        # 5. --- CRITICAL CHANGE ---
        # First, consolidate ALL results from ALL pages into a single list.
        all_papers = []
        for page_data in all_page_data:
            if page_data and 'collection' in page_data:
                all_papers.extend(page_data['collection'])
        
        print(f"All pages fetched. Total articles downloaded: {len(all_papers)}. Now filtering...")

        # 6. Now, filter the consolidated list for the keyword.
        filtered_papers = []
        seen_dois = set()
        search_query_lower = query.lower()
        
        for item in all_papers:
            doi = item.get('doi')
            if doi and doi not in seen_dois:
                title = item.get('title', '').lower()
                abstract = item.get('abstract', '').lower()
                
                if search_query_lower in title or search_query_lower in abstract:
                    filtered_papers.append(item)
                    seen_dois.add(doi)
            
            # Stop filtering only when we have enough results
            if len(filtered_papers) >= max_results:
                break
        
        print(f"Search complete. Found {len(filtered_papers)} matching article(s) for '{query}'.")
        
        # 7. Parse and cache the final list of results
        final_results = self._parse_response(filtered_papers)
        BIORXIV_CACHE[cache_key] = (datetime.now(), final_results)
        
        return final_results

    def search(self, query, max_results=20, **kwargs):
        """Synchronous wrapper to call the async search from the Flask app."""
        return asyncio.run(self.search_async(query, max_results, **kwargs))

    def _parse_response(self, collection):
        """Parses the raw API response into a structured format."""
        results = []
        for item in collection:
            authors_raw = item.get('authors', '')
            if isinstance(authors_raw, list):
                author_names = [author.get('name', '') for author in authors_raw if 'name' in author]
            else:
                author_names = [name.strip() for name in authors_raw.split(';')]

            paper = {
                'id': item.get('doi', '').replace('10.1101/', ''),
                'title': item.get('title', 'No Title Available'),
                'abstract': item.get('abstract', ''),
                'authors': author_names,
                'doi': item.get('doi', ''),
                'pub_date': item.get('date', ''),
                'journal': 'bioRxiv',
                'source': 'biorxiv',
                'url': f"https://www.biorxiv.org/content/{item.get('doi', '')}"
            }
            results.append(paper)
        return results