"""
Azure Pricing Data Extractor
Extracts pricing data for VMs, Databases, Storage, Functions, Container Services, and Kubernetes

Azure uses the Retail Prices API which is public and doesn't require authentication
"""

import requests
import json
from datetime import datetime
from typing import List, Dict
import time
from urllib.parse import quote


class AzurePricingExtractor:
    """Extract Azure pricing data using the Retail Prices API"""

    def __init__(self):
        """Initialize the Azure Retail Prices API client"""
        self.base_url = "https://prices.azure.com/api/retail/prices"
        print("Azure Pricing Extractor initialized")
        print("Using Azure Retail Prices API (public, no authentication required)")

    def _build_filter(self, filters: Dict[str, str]) -> str:
        """
        Build OData filter string for API query

        Args:
            filters: Dictionary of field -> value filters

        Returns:
            OData filter string
        """
        filter_parts = []
        for field, value in filters.items():
            filter_parts.append(f"{field} eq '{value}'")
        return " and ".join(filter_parts)

    def _get_all_pricing_data(self, filter_str: str, service_name: str) -> List[Dict]:
        """
        Fetch all pricing data with pagination

        Args:
            filter_str: OData filter string
            service_name: Name of service for logging

        Returns:
            List of pricing items
        """
        all_items = []
        url = f"{self.base_url}?$filter={quote(filter_str)}"
        page_count = 0

        try:
            while url and page_count < 100:  # Limit to 100 pages
                page_count += 1

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                data = response.json()
                items = data.get('Items', [])
                all_items.extend(items)

                print(f"  Page {page_count}: {len(all_items)} items so far...")

                # Get next page
                url = data.get('NextPageLink')

                # Rate limiting
                time.sleep(0.3)

            print(f"   Complete! Total items: {len(all_items)}")

        except Exception as e:
            print(f"   Error fetching {service_name}: {str(e)}")

        return all_items

    def get_virtual_machines_pricing(self) -> List[Dict]:
        """Get Virtual Machines pricing"""
        print("\n Fetching Virtual Machines pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Virtual Machines',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Virtual Machines')

    def get_sql_database_pricing(self) -> List[Dict]:
        """Get Azure SQL Database pricing"""
        print("\n Fetching Azure SQL Database pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Azure Database for MySQL',
            'priceType': 'Consumption'
        })

        mysql_data = self._get_all_pricing_data(filter_str, 'MySQL')

        # Also get PostgreSQL
        filter_str = self._build_filter({
            'serviceName': 'Azure Database for PostgreSQL',
            'priceType': 'Consumption'
        })

        postgres_data = self._get_all_pricing_data(filter_str, 'PostgreSQL')

        # Get SQL Database
        filter_str = self._build_filter({
            'serviceName': 'SQL Database',
            'priceType': 'Consumption'
        })

        sql_data = self._get_all_pricing_data(filter_str, 'SQL Database')

        # Get MariaDB
        filter_str = self._build_filter({
            'serviceName': 'Azure Database for MariaDB',
            'priceType': 'Consumption'
        })

        mariadb_data = self._get_all_pricing_data(filter_str, 'MariaDB')

        return mysql_data + postgres_data + sql_data + mariadb_data

    def get_sql_managed_instance_pricing(self) -> List[Dict]:
        """Get SQL Managed Instance pricing"""
        print("\n Fetching SQL Managed Instance pricing...")

        filter_str = self._build_filter({
            'serviceName': 'SQL Managed Instance',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'SQL Managed Instance')

    def get_synapse_analytics_pricing(self) -> List[Dict]:
        """Get Azure Synapse Analytics pricing"""
        print("\n Fetching Azure Synapse Analytics pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Azure Synapse Analytics',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Synapse Analytics')

    def get_storage_pricing(self) -> List[Dict]:
        """Get Azure Storage pricing"""
        print("\n Fetching Azure Storage pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Storage',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Storage')

    def get_functions_pricing(self) -> List[Dict]:
        """Get Azure Functions pricing"""
        print("\n Fetching Azure Functions pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Functions',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Azure Functions')

    def get_container_instances_pricing(self) -> List[Dict]:
        """Get Azure Container Instances pricing"""
        print("\n Fetching Container Instances pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Container Instances',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Container Instances')

    def get_aks_pricing(self) -> List[Dict]:
        """Get Azure Kubernetes Service pricing"""
        print("\n Fetching AKS pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Azure Kubernetes Service',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'AKS')

    def get_app_service_pricing(self) -> List[Dict]:
        """Get Azure App Service pricing"""
        print("\n Fetching App Service pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Azure App Service',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'App Service')

    def get_cosmos_db_pricing(self) -> List[Dict]:
        """Get Azure Cosmos DB pricing"""
        print("\n Fetching Cosmos DB pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Azure Cosmos DB',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Cosmos DB')

    def get_redis_cache_pricing(self) -> List[Dict]:
        """Get Azure Cache for Redis pricing"""
        print("\n Fetching Redis Cache pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Redis Cache',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Redis Cache')

    def get_logic_apps_pricing(self) -> List[Dict]:
        """Get Logic Apps pricing"""
        print("\n Fetching Logic Apps pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Logic Apps',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Logic Apps')

    def get_container_apps_pricing(self) -> List[Dict]:
        """Get Azure Container Apps pricing"""
        print("\n Fetching Azure Container Apps pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Azure Container Apps',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Container Apps')

    def get_container_registry_pricing(self) -> List[Dict]:
        """Get Container Registry pricing"""
        print("\n Fetching Container Registry pricing...")

        filter_str = self._build_filter({
            'serviceName': 'Container Registry',
            'priceType': 'Consumption'
        })

        return self._get_all_pricing_data(filter_str, 'Container Registry')

    def save_to_file(self, service_name: str, data: List[Dict], output_dir: str = '.'):
        """Save pricing data to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/azure_{service_name}_pricing_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'service': service_name,
                'extraction_date': datetime.now().isoformat(),
                'total_items': len(data),
                'items': data
            }, f, indent=2)

        print(f"   Saved {service_name} → {filename}")
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
        print("AZURE PRICING DATA EXTRACTION")
        print("="*60)

        # Define services to extract
        services = [
            # Core Compute & Containers
            ('virtual_machines', self.get_virtual_machines_pricing, 'Virtual Machines'),
            ('aks', self.get_aks_pricing, 'Azure Kubernetes Service'),
            ('container_instances', self.get_container_instances_pricing, 'Container Instances'),
            ('container_apps', self.get_container_apps_pricing, 'Azure Container Apps (Serverless)'),
            ('container_registry', self.get_container_registry_pricing, 'Container Registry'),
            ('app_service', self.get_app_service_pricing, 'App Service (PaaS)'),

            # Serverless
            ('functions', self.get_functions_pricing, 'Azure Functions'),
            ('logic_apps', self.get_logic_apps_pricing, 'Logic Apps (Serverless Workflows)'),

            # Databases
            ('sql_database', self.get_sql_database_pricing, 'SQL Databases (SQL, MySQL, PostgreSQL, MariaDB)'),
            ('sql_managed_instance', self.get_sql_managed_instance_pricing, 'SQL Managed Instance'),
            ('cosmos_db', self.get_cosmos_db_pricing, 'Cosmos DB (NoSQL)'),
            ('synapse_analytics', self.get_synapse_analytics_pricing, 'Azure Synapse Analytics (Data Warehouse)'),
            ('redis_cache', self.get_redis_cache_pricing, 'Redis Cache'),

            # Storage
            ('storage', self.get_storage_pricing, 'Azure Storage'),
        ]

        for service_key, fetch_func, display_name in services:
            print("\n" + "="*60)
            print(f"EXTRACTING: {display_name}")
            print("="*60)

            data = fetch_func()
            summary['services'][service_key] = {
                'display_name': display_name,
                'item_count': len(data)
            }
            self.save_to_file(service_key, data, output_dir)

        # Save summary
        summary_file = f"{output_dir}/azure_pricing_summary_{timestamp}.json"
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
            print(f"  {info['display_name']}: {info['item_count']} items")

        return summary


def main():
    print("="*60)
    print("Azure Pricing Data Extractor")
    print("="*60)
    print("This script extracts pricing data from Microsoft Azure")
    print("Services included:")
    print("\nCOMPUTE & CONTAINERS:")
    print("  - Virtual Machines")
    print("  - Azure Kubernetes Service (AKS)")
    print("  - Container Instances")
    print("  - Azure Container Apps (Serverless Containers)")
    print("  - Container Registry")
    print("  - App Service (PaaS)")
    print("\nSERVERLESS:")
    print("  - Azure Functions")
    print("  - Logic Apps (Serverless Workflows)")
    print("\nDATABASES:")
    print("  - Azure SQL Database")
    print("  - SQL Managed Instance")
    print("  - Azure Database for MySQL")
    print("  - Azure Database for PostgreSQL")
    print("  - Azure Database for MariaDB")
    print("  - Azure Synapse Analytics (Data Warehouse)")
    print("  - Cosmos DB (NoSQL)")
    print("  - Azure Cache for Redis")
    print("\nSTORAGE:")
    print("  - Azure Storage (Blob, Files, etc.)")
    print("="*60 + "\n")

    print("Note: Using Azure Retail Prices API (public, no authentication needed)")
    print("API Endpoint: https://prices.azure.com/api/retail/prices")
    print("\n")

    try:
        extractor = AzurePricingExtractor()
        extractor.extract_all_services(output_dir='.')
    except Exception as e:
        print(f"\n Error: {str(e)}")
        print("\nPlease ensure:")
        print("  - You have internet connectivity")
        print("  - The Azure Retail Prices API is accessible")


if __name__ == "__main__":
    main()