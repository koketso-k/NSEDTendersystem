import statistics

class AnalyticsService:
    """Handles analytics and reporting for tender data."""

    def average_bid_price(self, bid_prices: list) -> float:
        """Calculate the average bid price."""
        return statistics.mean(bid_prices) if bid_prices else 0

    def highest_bid(self, bid_prices: list) -> float:
        """Find the highest bid value."""
        return max(bid_prices) if bid_prices else 0

    def lowest_bid(self, bid_prices: list) -> float:
        """Find the lowest bid value."""
        return min(bid_prices) if bid_prices else 0
