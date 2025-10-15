import requests

class ETenderService:
    """Handles interaction with the external South African eTender API."""

    BASE_URL = "https://ocds-api.etenders.gov.za/api/v1/"

    def search_tenders(self, query: str):
        """Search for tenders based on a query string."""
        response = requests.get(f"{self.BASE_URL}/search", params={"q": query})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching tenders: {response.status_code}")

    def get_tender_details(self, tender_id: str):
        """Fetch detailed information for a specific tender."""
        response = requests.get(f"{self.BASE_URL}/tenders/{tender_id}")
        return response.json() if response.status_code == 200 else None
