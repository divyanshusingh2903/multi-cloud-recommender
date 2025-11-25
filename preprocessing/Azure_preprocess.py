"""
Azure Pricing Data Transformer
Transforms Azure pricing JSON files into standardized CloudService format
"""

import json
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

# Import the standardized schema (assume it's in the same directory or accessible)
from standard_cloud_service import CloudService, TechnicalSpecs, PricingInfo, ServiceCategory


class AzureDataTransformer:
    """Transform Azure pricing data into standardized format"""

    def __init__(self, data_dir: str = "./data/Azure"):
        self.data_dir = data_dir
        self.services = []

        # Service type mappings
        self.service_type_map = {
            'virtual_machines': ServiceCategory.COMPUTE.value,
            'sql_database': ServiceCategory.DATABASE.value,
            'sql_managed_instance': ServiceCategory.DATABASE.value,
            'functions': ServiceCategory.SERVERLESS.value,
            'logic_apps': ServiceCategory.SERVERLESS.value,
            'aks': ServiceCategory.KUBERNETES.value,
            'container_instances': ServiceCategory.CONTAINER.value,
            'container_apps': ServiceCategory.CONTAINER.value,
            'container_registry': ServiceCategory.CONTAINER.value,
            'app_service': ServiceCategory.SERVERLESS.value,
            'storage': ServiceCategory.STORAGE.value,
            'cosmos_db': ServiceCategory.DATABASE.value,
            'synapse_analytics': ServiceCategory.DATABASE.value,
            'redis_cache': ServiceCategory.DATABASE.value
        }

        # Azure region mapping (short name to readable)
        self.region_map = {
            'eastus': 'East US',
            'eastus2': 'East US 2',
            'westus': 'West US',
            'westus2': 'West US 2',
            'westus3': 'West US 3',
            'centralus': 'Central US',
            'northcentralus': 'North Central US',
            'southcentralus': 'South Central US',
            'westcentralus': 'West Central US',
            'canadacentral': 'Canada Central',
            'canadaeast': 'Canada East',
            'brazilsouth': 'Brazil South',
            'northeurope': 'North Europe',
            'westeurope': 'West Europe',
            'uksouth': 'UK South',
            'ukwest': 'UK West',
            'francecentral': 'France Central',
            'germanywestcentral': 'Germany West Central',
            'norwayeast': 'Norway East',
            'switzerlandnorth': 'Switzerland North',
            'swedencentral': 'Sweden Central',
            'eastasia': 'East Asia',
            'southeastasia': 'Southeast Asia',
            'japaneast': 'Japan East',
            'japanwest': 'Japan West',
            'australiaeast': 'Australia East',
            'australiasoutheast': 'Australia Southeast',
            'centralindia': 'Central India',
            'southindia': 'South India',
            'westindia': 'West India',
            'koreacentral': 'Korea Central',
            'koreasouth': 'Korea South'
        }

    def transform_all_services(self, output_file: str = "azure_standardized_services.json"):
        """Transform all Azure service files"""
        print("="*80)
        print("AZURE DATA TRANSFORMATION")
        print("="*80)

        # Process each service type
        self.transform_virtual_machines()
        self.transform_sql_database()
        self.transform_sql_managed_instance()
        self.transform_functions()
        self.transform_logic_apps()
        self.transform_aks()
        self.transform_container_instances()
        self.transform_container_apps()
        self.transform_container_registry()
        self.transform_app_service()
        self.transform_storage()
        self.transform_cosmos_db()
        self.transform_synapse_analytics()
        self.transform_redis_cache()

        # Save to file
        self.save_services(output_file)

        # Print summary
        self.print_summary()

    def transform_virtual_machines(self):
        """Transform Virtual Machines pricing data"""
        print("\n Processing Virtual Machines...")
        file_path = self._find_file_by_pattern("azure_virtual_machines_pricing_*.json")
        if not file_path:
            print("    Virtual Machines file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_vm_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Virtual Machine SKUs")

    def transform_sql_database(self):
        """Transform SQL Database pricing data"""
        print("\n Processing SQL Databases...")
        file_path = self._find_file_by_pattern("azure_sql_database_pricing_*.json")
        if not file_path:
            print("    SQL Database file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_sql_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} SQL Database SKUs")

    def transform_functions(self):
        """Transform Azure Functions pricing data"""
        print("\n Processing Azure Functions...")
        file_path = self._find_file_by_pattern("azure_functions_pricing_*.json")
        if not file_path:
            print("    Azure Functions file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_functions_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Azure Functions SKUs")

    def transform_aks(self):
        """Transform AKS pricing data"""
        print("\n Processing Azure Kubernetes Service...")
        file_path = self._find_file_by_pattern("azure_aks_pricing_*.json")
        if not file_path:
            print("    AKS file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_aks_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} AKS SKUs")

    def transform_container_instances(self):
        """Transform Container Instances pricing data"""
        print("\n Processing Container Instances...")
        file_path = self._find_file_by_pattern("azure_container_instances_pricing_*.json")
        if not file_path:
            print("    Container Instances file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_container_instances_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Container Instances SKUs")

    def transform_app_service(self):
        """Transform App Service pricing data"""
        print("\n Processing App Service...")
        file_path = self._find_file_by_pattern("azure_app_service_pricing_*.json")
        if not file_path:
            print("    App Service file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_app_service_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} App Service SKUs")

    def transform_storage(self):
        """Transform Storage pricing data"""
        print("\n Processing Azure Storage...")
        file_path = self._find_file_by_pattern("azure_storage_pricing_*.json")
        if not file_path:
            print("    Storage file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_storage_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Storage SKUs")

    def transform_cosmos_db(self):
        """Transform Cosmos DB pricing data"""
        print("\n Processing Cosmos DB...")
        file_path = self._find_file_by_pattern("azure_cosmos_db_pricing_*.json")
        if not file_path:
            print("    Cosmos DB file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_cosmos_db_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Cosmos DB SKUs")

    def transform_redis_cache(self):
        """Transform Redis Cache pricing data"""
        print("\n Processing Redis Cache...")
        file_path = self._find_file_by_pattern("azure_redis_cache_pricing_*.json")
        if not file_path:
            print("    Redis Cache file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_redis_cache_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Redis Cache SKUs")

    def transform_sql_managed_instance(self):
        """Transform SQL Managed Instance pricing data"""
        print("\n Processing SQL Managed Instance...")
        file_path = self._find_file_by_pattern("azure_sql_managed_instance_pricing_*.json")
        if not file_path:
            print("    SQL Managed Instance file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            # Reuse the SQL transform logic
            service = self._transform_sql_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} SQL Managed Instance SKUs")

    def transform_logic_apps(self):
        """Transform Logic Apps pricing data"""
        print("\n Processing Logic Apps...")
        file_path = self._find_file_by_pattern("azure_logic_apps_pricing_*.json")
        if not file_path:
            print("    Logic Apps file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_logic_apps_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Logic Apps SKUs")

    def transform_container_apps(self):
        """Transform Container Apps pricing data"""
        print("\n Processing Container Apps...")
        file_path = self._find_file_by_pattern("azure_container_apps_pricing_*.json")
        if not file_path:
            print("    Container Apps file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_container_apps_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Container Apps SKUs")

    def transform_container_registry(self):
        """Transform Container Registry pricing data"""
        print("\n Processing Container Registry...")
        file_path = self._find_file_by_pattern("azure_container_registry_pricing_*.json")
        if not file_path:
            print("    Container Registry file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_container_registry_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Container Registry SKUs")

    def transform_synapse_analytics(self):
        """Transform Synapse Analytics pricing data"""
        print("\n Processing Azure Synapse Analytics...")
        file_path = self._find_file_by_pattern("azure_synapse_analytics_pricing_*.json")
        if not file_path:
            print("    Synapse Analytics file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data.get('items', []):
            service = self._transform_synapse_analytics_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Synapse Analytics SKUs")

    # Transform individual items

    def _transform_vm_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Virtual Machine item"""
        try:
            sku_name = item.get('skuName', '')
            product_name = item.get('productName', '')
            armor_sku_name = item.get('armSkuName', '')

            # Skip non-VM items
            if not armor_sku_name or 'Spot' in product_name:
                return None

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            retail_price = float(item.get('retailPrice', 0))

            if unit_price == 0 and retail_price == 0:
                return None

            price = unit_price if unit_price > 0 else retail_price

            # Parse specs from product name
            specs = self._parse_vm_specs(product_name, armor_sku_name)

            # Create description
            description = f"Azure Virtual Machine {armor_sku_name}. {product_name}"

            # Create specs object
            tech_specs = TechnicalSpecs(
                vcpu=specs.get('vcpu'),
                memory_gb=specs.get('memory_gb'),
                architecture="x86_64"
            )

            # Features
            features = ["On-demand scaling", "Multiple VM sizes", "Windows and Linux support"]
            if 'Premium' in product_name:
                features.append("Premium SSD storage")

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=price,
                currency="USD",
                unit="hour",
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_vm_{armor_sku_name}_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name=f"Virtual Machine {armor_sku_name}",
                service_type="virtual_machines",
                category=self.service_type_map['virtual_machines'],
                description=description,
                short_description=f"Azure VM: {specs.get('vcpu', 'N/A')} vCPU, {specs.get('memory_gb', 'N/A')} GB RAM",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=["Web servers", "Application servers", "Batch processing", "Development"],
                tags=["compute", "vm", "virtual-machine", armor_sku_name.lower()],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_sql_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single SQL Database item"""
        try:
            product_name = item.get('productName', '')
            service_name = item.get('serviceName', '')
            sku_name = item.get('skuName', '')

            # Determine database engine
            engine = "SQL Server"
            if "MySQL" in service_name:
                engine = "MySQL"
            elif "PostgreSQL" in service_name:
                engine = "PostgreSQL"
            elif "MariaDB" in service_name:
                engine = "MariaDB"

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Parse specs
            specs = self._parse_db_specs(product_name, sku_name)

            # Create description
            description = f"Azure {engine} managed database. {product_name}"

            # Create specs object
            tech_specs = TechnicalSpecs(
                vcpu=specs.get('vcpu'),
                memory_gb=specs.get('memory_gb'),
                database_engine=engine,
                storage_type="SSD"
            )

            # Features
            features = [
                f"{engine} engine",
                "Automated backups",
                "Point-in-time restore",
                "High availability options",
                "Automatic patching"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Hour'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_{engine.lower().replace(' ', '_')}_{sku_name}_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name=f"Azure Database for {engine} {sku_name}",
                service_type="sql_database",
                category=self.service_type_map['sql_database'],
                description=description,
                short_description=f"Azure {engine}: {specs.get('vcpu', 'N/A')} vCPU, {specs.get('memory_gb', 'N/A')} GB RAM",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=["Web applications", "Enterprise applications", "Analytics"],
                tags=["database", engine.lower(), "managed", "sql"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_functions_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Azure Functions item"""
        try:
            product_name = item.get('productName', '')
            meter_name = item.get('meterName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Create description
            description = f"Azure Functions - Serverless compute platform. {product_name}"

            # Create specs
            tech_specs = TechnicalSpecs(
                memory_gb=1.5,  # Max memory per execution
                architecture="x86_64"
            )

            # Features
            features = [
                "Event-driven execution",
                "Automatic scaling",
                "Pay per execution",
                "Multiple language support",
                "Integrated with Azure services"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Million Executions'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=True
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_functions_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name="Azure Functions",
                service_type="functions",
                category=self.service_type_map['functions'],
                description=description,
                short_description="Serverless compute for event-driven workloads",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "API backends",
                    "Data processing",
                    "Real-time file processing",
                    "IoT backends",
                    "Scheduled tasks"
                ],
                tags=["serverless", "functions", "compute", "event-driven"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_aks_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single AKS item"""
        try:
            product_name = item.get('productName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Create description
            description = "Azure Kubernetes Service - Managed Kubernetes cluster. Simplify deployment, management, and operations of Kubernetes."

            # Create specs
            tech_specs = TechnicalSpecs()

            # Features
            features = [
                "Managed Kubernetes control plane",
                "Automatic upgrades",
                "Integrated monitoring",
                "Azure Active Directory integration",
                "Virtual network integration"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Hour'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_aks_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name="Azure Kubernetes Service (AKS)",
                service_type="aks",
                category=self.service_type_map['aks'],
                description=description,
                short_description="Managed Kubernetes service",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Microservices",
                    "Container orchestration",
                    "CI/CD pipelines",
                    "Hybrid deployments"
                ],
                tags=["kubernetes", "containers", "aks", "orchestration"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_container_instances_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Container Instances item"""
        try:
            product_name = item.get('productName', '')
            meter_name = item.get('meterName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Create description
            description = f"Azure Container Instances - Run containers without managing servers. {product_name}"

            # Parse specs from meter name
            specs = self._parse_container_specs(meter_name)

            # Create specs object
            tech_specs = TechnicalSpecs(
                vcpu=specs.get('vcpu'),
                memory_gb=specs.get('memory_gb')
            )

            # Features
            features = [
                "Fast startup times",
                "Per-second billing",
                "Hypervisor-level security",
                "Custom sizes",
                "Persistent storage"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Hour'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_container_instances_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name="Azure Container Instances",
                service_type="container_instances",
                category=self.service_type_map['container_instances'],
                description=description,
                short_description=f"Serverless containers: {specs.get('vcpu', 'N/A')} vCPU, {specs.get('memory_gb', 'N/A')} GB RAM",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Batch jobs",
                    "Task automation",
                    "Event-driven applications",
                    "Development/testing"
                ],
                tags=["containers", "serverless", "docker"],
                supports_auto_scaling=False,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_app_service_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single App Service item"""
        try:
            product_name = item.get('productName', '')
            sku_name = item.get('skuName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Create description
            description = f"Azure App Service - Platform-as-a-Service for web apps, mobile backends, and REST APIs. {product_name}"

            # Parse specs
            specs = self._parse_app_service_specs(product_name, sku_name)

            # Create specs object
            tech_specs = TechnicalSpecs(
                vcpu=specs.get('vcpu'),
                memory_gb=specs.get('memory_gb')
            )

            # Features
            features = [
                "Built-in auto-scaling",
                "Deployment slots",
                "Integrated CI/CD",
                "Custom domains and SSL",
                "Multiple language support"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Hour'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=('Free' in sku_name or 'Shared' in sku_name)
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_app_service_{sku_name}_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name=f"App Service {sku_name}",
                service_type="app_service",
                category=self.service_type_map['app_service'],
                description=description,
                short_description=f"PaaS: {specs.get('vcpu', 'N/A')} vCPU, {specs.get('memory_gb', 'N/A')} GB RAM",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Web applications",
                    "Mobile backends",
                    "REST APIs",
                    "Background jobs"
                ],
                tags=["paas", "web", "app-service"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_storage_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Storage item"""
        try:
            product_name = item.get('productName', '')
            meter_name = item.get('meterName', '')

            # Only process storage capacity items
            if 'Data Stored' not in meter_name and 'Capacity' not in meter_name:
                return None

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Determine storage type
            storage_type = "Standard"
            if "Premium" in product_name:
                storage_type = "Premium"
            elif "Cool" in meter_name:
                storage_type = "Cool"
            elif "Archive" in meter_name:
                storage_type = "Archive"

            # Create description
            description = f"Azure Storage {storage_type} tier. {self._get_storage_description(storage_type)}"

            # Create specs
            tech_specs = TechnicalSpecs(
                storage_type="Blob Storage"
            )

            # Features
            features = self._get_storage_features(storage_type)

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 GB/Month'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_storage_{storage_type}_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name=f"Azure Storage ({storage_type})",
                service_type="storage",
                category=self.service_type_map['storage'],
                description=description,
                short_description=f"Object storage - {storage_type} tier",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Data lakes",
                    "Backup and restore",
                    "Content distribution",
                    "Archive storage"
                ],
                tags=["storage", "blob", "object-storage", storage_type.lower()],
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_cosmos_db_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Cosmos DB item"""
        try:
            product_name = item.get('productName', '')
            meter_name = item.get('meterName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Create description
            description = "Azure Cosmos DB - Globally distributed, multi-model database service. Low latency and high availability."

            # Create specs
            tech_specs = TechnicalSpecs(
                database_engine="Cosmos DB",
                storage_type="NoSQL Multi-model"
            )

            # Features
            features = [
                "Global distribution",
                "Multi-model support (Document, Graph, Key-Value)",
                "Guaranteed low latency",
                "Automatic indexing",
                "Multiple consistency levels",
                "99.999% availability SLA"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '100 RUs'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_cosmos_db_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name="Azure Cosmos DB",
                service_type="cosmos_db",
                category=self.service_type_map['cosmos_db'],
                description=description,
                short_description="Globally distributed multi-model database",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Global applications",
                    "IoT and telematics",
                    "Gaming",
                    "Real-time analytics"
                ],
                tags=["database", "nosql", "cosmos-db", "distributed"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_redis_cache_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Redis Cache item"""
        try:
            product_name = item.get('productName', '')
            sku_name = item.get('skuName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Parse specs
            specs = self._parse_redis_specs(product_name, sku_name)

            # Create description
            description = f"Azure Cache for Redis - Managed Redis cache service. {product_name}"

            # Create specs object
            tech_specs = TechnicalSpecs(
                memory_gb=specs.get('memory_gb'),
                database_engine="Redis",
                storage_type="In-memory"
            )

            # Features
            features = [
                "Managed Redis",
                "High availability",
                "Data persistence",
                "Clustering support",
                "Built-in monitoring"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Hour'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_redis_{sku_name}_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name=f"Azure Cache for Redis {sku_name}",
                service_type="redis_cache",
                category=self.service_type_map['redis_cache'],
                description=description,
                short_description=f"Managed Redis: {specs.get('memory_gb', 'N/A')} GB memory",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Caching",
                    "Session management",
                    "Pub/Sub messaging",
                    "Leaderboards"
                ],
                tags=["database", "redis", "cache", "in-memory"],
                supports_auto_scaling=False,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_logic_apps_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Logic Apps item"""
        try:
            product_name = item.get('productName', '')
            meter_name = item.get('meterName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Create description
            description = f"Azure Logic Apps - Serverless workflow automation and integration. {product_name}"

            # Create specs
            tech_specs = TechnicalSpecs()

            # Features
            features = [
                "Visual workflow designer",
                "Pre-built connectors",
                "Automatic scaling",
                "Enterprise integration",
                "B2B capabilities"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Action'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_logic_apps_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name="Logic Apps",
                service_type="logic_apps",
                category=self.service_type_map['logic_apps'],
                description=description,
                short_description="Serverless workflow automation",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Workflow automation",
                    "System integration",
                    "B2B integration",
                    "Event processing"
                ],
                tags=["serverless", "workflow", "integration", "logic-apps"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_container_apps_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Container Apps item"""
        try:
            product_name = item.get('productName', '')
            meter_name = item.get('meterName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Parse specs from meter name
            specs = self._parse_container_specs(meter_name)

            # Create description
            description = f"Azure Container Apps - Serverless container platform. {product_name}"

            # Create specs object
            tech_specs = TechnicalSpecs(
                vcpu=specs.get('vcpu'),
                memory_gb=specs.get('memory_gb')
            )

            # Features
            features = [
                "Serverless containers",
                "Auto-scaling to zero",
                "HTTPS ingress",
                "Built-in load balancing",
                "Dapr integration",
                "KEDA support"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 vCPU-second'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_container_apps_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name="Azure Container Apps",
                service_type="container_apps",
                category=self.service_type_map['container_apps'],
                description=description,
                short_description=f"Serverless containers: {specs.get('vcpu', 'N/A')} vCPU, {specs.get('memory_gb', 'N/A')} GB RAM",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Microservices",
                    "APIs",
                    "Event-driven applications",
                    "Background jobs"
                ],
                tags=["containers", "serverless", "microservices"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_container_registry_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Container Registry item"""
        try:
            product_name = item.get('productName', '')
            sku_name = item.get('skuName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Determine tier from SKU
            tier = "Basic"
            if "Standard" in sku_name or "Standard" in product_name:
                tier = "Standard"
            elif "Premium" in sku_name or "Premium" in product_name:
                tier = "Premium"

            # Create description
            description = f"Azure Container Registry {tier} - Docker container registry service. {product_name}"

            # Create specs
            tech_specs = TechnicalSpecs(
                storage_type="Container Registry"
            )

            # Features
            features = [
                f"{tier} tier",
                "Docker registry",
                "Image scanning",
                "Geo-replication" if tier == "Premium" else "Single region"
            ]

            if tier == "Premium":
                features.extend(["Content trust", "Private link support"])

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '1 Day'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_container_registry_{tier}_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name=f"Container Registry ({tier})",
                service_type="container_registry",
                category=self.service_type_map['container_registry'],
                description=description,
                short_description=f"Container registry - {tier} tier",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Container image storage",
                    "CI/CD pipelines",
                    "Kubernetes deployments",
                    "Docker registries"
                ],
                tags=["containers", "registry", "docker", tier.lower()],
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_synapse_analytics_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Synapse Analytics item"""
        try:
            product_name = item.get('productName', '')
            meter_name = item.get('meterName', '')

            # Extract region
            region = item.get('armRegionName', 'unknown')
            region_display = self.region_map.get(region, region)

            # Extract pricing
            unit_price = float(item.get('unitPrice', 0))
            if unit_price == 0:
                return None

            # Create description
            description = f"Azure Synapse Analytics - Unified analytics platform combining data warehousing and big data analytics. {product_name}"

            # Create specs
            tech_specs = TechnicalSpecs(
                database_engine="Synapse",
                storage_type="Data Warehouse"
            )

            # Features
            features = [
                "Unified analytics",
                "Serverless and dedicated options",
                "Integrated with Power BI",
                "Built-in data integration",
                "Apache Spark pools",
                "SQL analytics"
            ]

            # Create pricing
            pricing_list = [PricingInfo(
                price_per_unit=unit_price,
                currency="USD",
                unit=item.get('unitOfMeasure', '100 DWU'),
                pricing_model="on_demand",
                region=region,
                free_tier_included=False
            )]

            # Create service
            service = CloudService(
                service_id=f"azure_synapse_analytics_{region}_{item.get('skuId', '')}",
                provider="azure",
                service_name="Azure Synapse Analytics",
                service_type="synapse_analytics",
                category=self.service_type_map['synapse_analytics'],
                description=description,
                short_description="Unified analytics and data warehouse",
                specs=tech_specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Data warehousing",
                    "Big data analytics",
                    "Real-time analytics",
                    "Data integration"
                ],
                tags=["database", "data-warehouse", "analytics", "synapse"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=item.get('skuId', ''),
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    # Helper methods

    def _find_file_by_pattern(self, pattern: str) -> Optional[str]:
        """Find file matching pattern"""
        import glob
        files = glob.glob(os.path.join(self.data_dir, pattern))
        return files[0] if files else None

    def _parse_vm_specs(self, product_name: str, sku_name: str) -> Dict:
        """Parse VM specs from product name"""
        specs = {}

        # Try to extract vCPU and memory from product name
        # Example: "Standard_D2s_v3" typically has patterns
        vcpu_match = re.search(r'(\d+)\s*vCPU', product_name, re.IGNORECASE)
        if vcpu_match:
            specs['vcpu'] = float(vcpu_match.group(1))

        memory_match = re.search(r'(\d+(?:\.\d+)?)\s*GiB', product_name, re.IGNORECASE)
        if memory_match:
            specs['memory_gb'] = float(memory_match.group(1))

        return specs

    def _parse_db_specs(self, product_name: str, sku_name: str) -> Dict:
        """Parse database specs from product name"""
        specs = {}

        vcpu_match = re.search(r'(\d+)\s*vCore', product_name, re.IGNORECASE)
        if vcpu_match:
            specs['vcpu'] = float(vcpu_match.group(1))

        memory_match = re.search(r'(\d+(?:\.\d+)?)\s*GB', product_name, re.IGNORECASE)
        if memory_match:
            specs['memory_gb'] = float(memory_match.group(1))

        return specs

    def _parse_container_specs(self, meter_name: str) -> Dict:
        """Parse container specs from meter name"""
        specs = {}

        vcpu_match = re.search(r'(\d+(?:\.\d+)?)\s*vCPU', meter_name, re.IGNORECASE)
        if vcpu_match:
            specs['vcpu'] = float(vcpu_match.group(1))

        memory_match = re.search(r'(\d+(?:\.\d+)?)\s*GB', meter_name, re.IGNORECASE)
        if memory_match:
            specs['memory_gb'] = float(memory_match.group(1))

        return specs

    def _parse_app_service_specs(self, product_name: str, sku_name: str) -> Dict:
        """Parse App Service specs"""
        specs = {}

        # App Service plans typically don't expose vCPU/memory directly
        # We can infer from tier names
        if 'Basic' in sku_name:
            specs['vcpu'] = 1
            specs['memory_gb'] = 1.75
        elif 'Standard' in sku_name:
            specs['vcpu'] = 1
            specs['memory_gb'] = 1.75
        elif 'Premium' in sku_name:
            specs['vcpu'] = 2
            specs['memory_gb'] = 3.5

        return specs

    def _parse_redis_specs(self, product_name: str, sku_name: str) -> Dict:
        """Parse Redis cache specs"""
        specs = {}

        # Extract cache size
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*GB', product_name, re.IGNORECASE)
        if size_match:
            specs['memory_gb'] = float(size_match.group(1))

        return specs

    def _get_storage_description(self, storage_type: str) -> str:
        """Get description for storage type"""
        descriptions = {
            'Standard': 'General-purpose storage with low cost and high durability',
            'Premium': 'High-performance storage with low latency for I/O intensive workloads',
            'Cool': 'Lower-cost tier for infrequently accessed data',
            'Archive': 'Lowest-cost tier for rarely accessed data with flexible latency'
        }
        return descriptions.get(storage_type, 'Reliable and scalable object storage')

    def _get_storage_features(self, storage_type: str) -> List[str]:
        """Get features for storage type"""
        base_features = [
            "High durability (99.999999999%)",
            "Versioning",
            "Lifecycle management",
            "Encryption at rest"
        ]

        type_features = {
            'Standard': ["Low latency", "High throughput", "Frequent access optimized"],
            'Premium': ["Ultra-low latency", "High IOPS", "SSD-backed"],
            'Cool': ["Lower storage cost", "Higher access cost", "30-day minimum"],
            'Archive': ["Lowest storage cost", "Highest access cost", "180-day minimum"]
        }

        return base_features + type_features.get(storage_type, [])

    def save_services(self, output_file: str):
        """Save transformed services to JSON file"""
        print(f"\n Saving to {output_file}...")

        services_output = []
        for service in self.services:
            services_output.append({
                'embedding_text': service.generate_embedding_text(),
                'blob': service.to_dict()
            })

        output_data = {
            'metadata': {
                'provider': 'azure',
                'extraction_date': datetime.now().isoformat(),
                'total_services': len(self.services)
            },
            'services': services_output
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"    Saved {len(self.services)} services")

    def print_summary(self):
        """Print transformation summary"""
        print("\n" + "="*80)
        print("TRANSFORMATION SUMMARY")
        print("="*80)

        # Count by service type
        type_counts = {}
        for service in self.services:
            service_type = service.service_type
            type_counts[service_type] = type_counts.get(service_type, 0) + 1

        for service_type, count in sorted(type_counts.items()):
            print(f"  {service_type.upper().replace('_', ' ')}: {count} services")

        print(f"\n  TOTAL: {len(self.services)} services")
        print("="*80)


def main():
    """Main execution"""
    # Create transformer
    transformer = AzureDataTransformer(data_dir="./data/Azure/raw")

    # Transform all services
    transformer.transform_all_services(output_file="azure_standardized_services.json")

    print("\n Transformation complete!")
    print(" Output file: azure_standardized_services.json")


if __name__ == "__main__":
    main()