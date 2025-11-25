"""
GCP Services Collector
Collects all available services from Google Cloud Platform
"""

from google.cloud import billing_v1
from google.oauth2 import service_account
import json
from typing import List, Dict
import os

class GCPServicesCollector:
    def __init__(self):
        """Initialize the GCP Billing client"""
        credentials_path = "/home/divya/.gcloud/credentials.json"
        print(f"Using credentials path: {credentials_path}")
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = billing_v1.CloudCatalogClient(credentials=credentials)
        else:
            self.client = billing_v1.CloudCatalogClient()

    def get_all_services(self) -> List[Dict]:
        """Fetch all GCP services from Cloud Catalog API"""
        print("Fetching all GCP services...")

        all_services = []

        try:
            # List all services
            request = billing_v1.ListServicesRequest()
            page_result = self.client.list_services(request=request)

            for service in page_result:
                service_data = {
                    'name': service.name,
                    'service_id': service.service_id,
                    'display_name': service.display_name,
                    'business_entity_name': service.business_entity_name
                }
                all_services.append(service_data)

            print(f"\n✅ Total services found: {len(all_services)}")

        except Exception as e:
            print(f"❌ Error fetching services: {str(e)}")

        return all_services

    def save_to_file(self, services: List[Dict], filename: str = '../data/GCP/raw/gcp_services.json'):
        """Save services data to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                'total_services': len(services),
                'services': services
            }, f, indent=4)
        print(f"✅ Saved to {filename}")


def main():
    print("="*60)
    print("GCP Services Collector")
    print("="*60)
    print("This script fetches all available services from GCP\n")

    collector = GCPServicesCollector()
    services = collector.get_all_services()

    if services:
        collector.save_to_file(services)
    else:
        print("\n❌ No services found. Check your GCP credentials and API access.")


if __name__ == "__main__":
    main()