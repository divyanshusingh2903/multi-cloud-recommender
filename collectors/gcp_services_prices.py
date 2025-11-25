"""
GCP Pricing Data Extractor
Extracts pricing data for VMs, Databases, Storage, Functions, Container Services, and Kubernetes
"""

# Load environment variables from .env file (for IDE compatibility)
from dotenv import load_dotenv
load_dotenv()

from google.cloud import billing_v1
from google.oauth2 import service_account
import json
from datetime import datetime
from typing import List, Dict

class GCPPricingExtractor:
    def __init__(self):
        """Initialize the GCP Cloud Catalog client"""
        credentials_path = "/home/divya/.gcloud/credentials.json"
        print(f"Using credentials path: {credentials_path}")
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = billing_v1.CloudCatalogClient(credentials=credentials)
        else:
            self.client = billing_v1.CloudCatalogClient()

        # Service IDs mapping (these are GCP's official service IDs)
        self.service_ids = {
            'compute': '6F81-5844-456A',
            'cloud_sql': '9662-B51E-5089',
            'storage': '95FF-2EF5-5EA1',  
            'functions': '29E7-DA93-CA13',
            'run': '152E-C115-5142',
            'gke': 'CCD8-9BF1-090E',
            'spanner': 'CC63-0873-48FD',
            'firestore': 'EE2C-7FAC-5E08',
            'bigtable': 'C3BE-24A5-0975',
            'memorystore': 'A2B5-E0F1-B0F3',
            'app_engine': 'F17B-412E-CB64',
        }

    def get_service_skus(self, service_id: str, service_name: str) -> List[Dict]:
        """Get all SKUs (pricing items) for a specific service"""
        print(f"\nFetching {service_name} pricing data...")
        all_skus = []

        try:
            service_path = f"services/{service_id}"
            request = billing_v1.ListSkusRequest(parent=service_path)
            page_result = self.client.list_skus(request=request)

            page_count = 0
            for sku in page_result:
                page_count += 1

                # Extract pricing information
                sku_data = {
                    'name': sku.name,
                    'sku_id': sku.sku_id,
                    'description': sku.description,
                    'category': {
                        'service_display_name': sku.category.service_display_name,
                        'resource_family': sku.category.resource_family,
                        'resource_group': sku.category.resource_group,
                        'usage_type': sku.category.usage_type
                    },
                    'service_regions': list(sku.service_regions),
                    'pricing_info': []
                }

                # Extract pricing tiers
                for pricing_info in sku.pricing_info:
                    pricing_data = {
                        'summary': pricing_info.summary,
                        'currency_conversion_rate': pricing_info.currency_conversion_rate,
                        'effective_time': pricing_info.effective_time.isoformat() if pricing_info.effective_time else None,
                        'pricing_expression': {
                            'usage_unit': pricing_info.pricing_expression.usage_unit,
                            'display_quantity': pricing_info.pricing_expression.display_quantity,
                            'usage_unit_description': pricing_info.pricing_expression.usage_unit_description,
                            'tiered_rates': []
                        }
                    }

                    # Extract tiered rates
                    for tier in pricing_info.pricing_expression.tiered_rates:
                        tier_data = {
                            'start_usage_amount': tier.start_usage_amount,
                            'unit_price': {
                                'currency_code': tier.unit_price.currency_code,
                                'units': str(tier.unit_price.units),
                                'nanos': tier.unit_price.nanos
                            }
                        }
                        pricing_data['pricing_expression']['tiered_rates'].append(tier_data)

                    sku_data['pricing_info'].append(pricing_data)

                all_skus.append(sku_data)

                if page_count % 50 == 0:
                    print(f"  Processed {page_count} SKUs...")

            print(f"  ✅ Complete! Total SKUs: {len(all_skus)}")

        except Exception as e:
            print(f"  ❌ Error fetching {service_name} pricing: {str(e)}")

        return all_skus

    def get_compute_pricing(self) -> List[Dict]:
        """Get Compute Engine (VM) pricing"""
        return self.get_service_skus(
            self.service_ids['compute'],
            'Compute Engine (VMs)'
        )

    def get_cloud_sql_pricing(self) -> List[Dict]:
        """Get Cloud SQL (Database) pricing"""
        return self.get_service_skus(
            self.service_ids['cloud_sql'],
            'Cloud SQL (Databases)'
        )

    def get_storage_pricing(self) -> List[Dict]:
        """Get Cloud Storage pricing"""
        return self.get_service_skus(
            self.service_ids['storage'],
            'Cloud Storage'
        )

    def get_functions_pricing(self) -> List[Dict]:
        """Get Cloud Functions pricing"""
        return self.get_service_skus(
            self.service_ids['functions'],
            'Cloud Functions'
        )

    def get_cloud_run_pricing(self) -> List[Dict]:
        """Get Cloud Run (Container Service) pricing"""
        return self.get_service_skus(
            self.service_ids['run'],
            'Cloud Run (Container Service)'
        )

    def get_gke_pricing(self) -> List[Dict]:
        """Get Google Kubernetes Engine pricing"""
        return self.get_service_skus(
            self.service_ids['gke'],
            'Google Kubernetes Engine (GKE)'
        )

    def get_spanner_pricing(self) -> List[Dict]:
        """Get Cloud Spanner pricing"""
        return self.get_service_skus(
            self.service_ids['spanner'],
            'Cloud Spanner'
        )

    def get_firestore_pricing(self) -> List[Dict]:
        """Get Firestore pricing"""
        return self.get_service_skus(
            self.service_ids['firestore'],
            'Firestore (NoSQL)'
        )

    def get_bigtable_pricing(self) -> List[Dict]:
        """Get Cloud Bigtable pricing"""
        return self.get_service_skus(
            self.service_ids['bigtable'],
            'Cloud Bigtable (NoSQL)'
        )

    def get_memorystore_pricing(self) -> List[Dict]:
        """Get Memorystore (Redis/Memcached) pricing"""
        return self.get_service_skus(
            self.service_ids['memorystore'],
            'Memorystore (Redis/Memcached)'
        )

    def get_app_engine_pricing(self) -> List[Dict]:
        """Get App Engine pricing"""
        return self.get_service_skus(
            self.service_ids['app_engine'],
            'App Engine'
        )

    def save_to_file(self, service_name: str, data: List[Dict], output_dir: str = '.'):
        """Save pricing data to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/gcp_{service_name}_pricing_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'service': service_name,
                'extraction_date': datetime.now().isoformat(),
                'total_skus': len(data),
                'skus': data
            }, f, indent=2)

        print(f"  ✅ Saved {service_name} → {filename}")
        return filename

    def extract_all_services(self, output_dir: str = '.'):
        """Extract pricing data for all services"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        summary = {
            'timestamp': timestamp,
            'extraction_date': datetime.now().isoformat(),
            'services': {}
        }

        print("\n" + "="*60)
        print("GCP PRICING DATA EXTRACTION")
        print("="*60)

        # Define services to extract
        services = [
            # Core Compute & Containers
            ('compute', self.get_compute_pricing, 'Compute Engine (VMs)'),
            ('gke', self.get_gke_pricing, 'Google Kubernetes Engine'),
            ('cloud_run', self.get_cloud_run_pricing, 'Cloud Run (Containers)'),
            ('app_engine', self.get_app_engine_pricing, 'App Engine (PaaS)'),

            # Serverless
            ('functions', self.get_functions_pricing, 'Cloud Functions'),

            # Databases
            ('cloud_sql', self.get_cloud_sql_pricing, 'Cloud SQL (Relational DB)'),
            ('spanner', self.get_spanner_pricing, 'Cloud Spanner (Distributed SQL)'),
            ('firestore', self.get_firestore_pricing, 'Firestore (NoSQL Document)'),
            ('bigtable', self.get_bigtable_pricing, 'Cloud Bigtable (NoSQL Wide-column)'),
            ('memorystore', self.get_memorystore_pricing, 'Memorystore (Redis/Memcached)'),

            # Storage
            ('storage', self.get_storage_pricing, 'Cloud Storage'),
        ]

        for service_key, fetch_func, display_name in services:
            print("\n" + "="*60)
            print(f"EXTRACTING: {display_name}")
            print("="*60)

            data = fetch_func()
            summary['services'][service_key] = {
                'display_name': display_name,
                'sku_count': len(data)
            }
            self.save_to_file(service_key, data, output_dir)

        # Save summary
        summary_file = f"{output_dir}/gcp_pricing_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n" + "="*60)
        print("ALL DATA EXTRACTION COMPLETE!")
        print("="*60)
        print(f"Summary saved → {summary_file}\n")

        # Print summary
        print("Extraction Summary:")
        print("-" * 60)
        for service_key, info in summary['services'].items():
            print(f"  {info['display_name']}: {info['sku_count']} SKUs")

        return summary


def main():
    print("="*60)
    print("GCP Pricing Data Extractor")
    print("="*60)
    print("This script extracts pricing data from Google Cloud Platform")
    print("Services included:")
    print("\nCOMPUTE & CONTAINERS:")
    print("  - Compute Engine (VMs)")
    print("  - Google Kubernetes Engine (GKE)")
    print("  - Cloud Run (Container Service)")
    print("  - App Engine (PaaS)")
    print("\nSERVERLESS:")
    print("  - Cloud Functions")
    print("\nDATABASES:")
    print("  - Cloud SQL (MySQL, PostgreSQL, SQL Server)")
    print("  - Cloud Spanner (Distributed SQL)")
    print("  - Firestore (NoSQL Document)")
    print("  - Cloud Bigtable (NoSQL Wide-column)")
    print("  - Memorystore (Redis/Memcached)")
    print("\nSTORAGE:")
    print("  - Cloud Storage")
    print("="*60 + "\n")

    print("Prerequisites:")
    print("1. Install: pip install google-cloud-billing")
    print("2. Set credentials: export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
    print("3. Enable Cloud Billing API in your GCP project")
    print("\n")

    try:
        extractor = GCPPricingExtractor()
        extractor.extract_all_services(output_dir='../data/GCP/raw')
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease ensure:")
        print("  - You have valid GCP credentials configured")
        print("  - The Cloud Billing API is enabled")
        print("  - You have the necessary permissions to access billing data")


if __name__ == "__main__":
    main()