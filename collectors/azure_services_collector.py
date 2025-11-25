"""
Azure Services Collector
Collects all available services from Microsoft Azure
"""

import requests
import json
from typing import List, Dict
import time


class AzureServicesCollector:
    """
    Collects Azure service information using the Azure Retail Prices API
    """

    def __init__(self):
        """Initialize the Azure Retail Prices API client"""
        self.base_url = "https://prices.azure.com/api/retail/prices"
        print("Azure Services Collector initialized")
        print("Using Azure Retail Prices API (no authentication required)")

    def get_all_services(self) -> List[Dict]:
        """
        Fetch all unique Azure services from the Retail Prices API

        Returns:
            List of unique service dictionaries
        """
        print("\nFetching all Azure services...")

        all_services = {}  # Use dict to deduplicate by serviceName
        next_page_link = self.base_url
        page_count = 0

        try:
            # We'll fetch multiple pages to get a comprehensive list
            # The API returns paginated results
            while next_page_link and page_count < 20:  # Limit to 20 pages for service discovery
                page_count += 1
                print(f"  Fetching page {page_count}...")

                response = requests.get(next_page_link, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Extract unique services from this page
                items = data.get('Items', [])
                for item in items:
                    service_name = item.get('serviceName', 'Unknown')
                    service_id = item.get('serviceId', '')
                    service_family = item.get('serviceFamily', '')
                    product_name = item.get('productName', '')

                    # Use serviceName as key to deduplicate
                    if service_name not in all_services:
                        all_services[service_name] = {
                            'service_name': service_name,
                            'service_id': service_id,
                            'service_family': service_family,
                            'example_product': product_name
                        }

                # Get next page link
                next_page_link = data.get('NextPageLink')

                # Small delay to avoid rate limiting
                time.sleep(0.5)

            print(f"\nTotal unique services found: {len(all_services)}")

            # Convert to list and sort
            services_list = sorted(all_services.values(), key=lambda x: x['service_name'])

            return services_list

        except Exception as e:
            print(f"Error fetching services: {str(e)}")
            return []

    def save_to_file(self, services: List[Dict], filename: str = 'azure_services.json'):
        """Save services data to JSON file"""
        output = {
            'total_services': len(services),
            'collection_method': 'Azure Retail Prices API',
            'note': 'Services extracted from pricing data',
            'services': services
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=4)

        print(f"Saved to {filename}")


def main():
    print("="*60)
    print("Azure Services Collector")
    print("="*60)
    print("This script fetches all available services from Microsoft Azure\n")

    print("Note: Azure uses the Retail Prices API which is public")
    print("No authentication is required\n")

    collector = AzureServicesCollector()

    # Collect all services
    services = collector.get_all_services()

    if services:
        collector.save_to_file(services)

        print("\n" + "="*60)
        print("Sample Services:")
        print("="*60)
        for service in services[:20]:
            print(f"  • {service['service_name']}")
            if service['service_family']:
                print(f"    Family: {service['service_family']}")

        if len(services) > 20:
            print(f"  ... and {len(services) - 20} more services")
    else:
        print("\n No services found. Check your internet connection.")


if __name__ == "__main__":
    main()