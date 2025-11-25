"""
GCP Pricing Data Transformer
Transforms GCP pricing JSON files into standardized CloudService format
"""

import json
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

# Import the standardized schema
from standard_cloud_service import CloudService, TechnicalSpecs, PricingInfo, ServiceCategory


class GCPDataTransformer:
    """Transform GCP pricing data into standardized format"""

    def __init__(self, data_dir: str = "./data/GCP"):
        self.data_dir = data_dir
        self.services = []

        # Service type mappings
        self.service_type_map = {
            'compute': ServiceCategory.COMPUTE.value,
            'cloud_sql': ServiceCategory.DATABASE.value,
            'functions': ServiceCategory.SERVERLESS.value,
            'gke': ServiceCategory.KUBERNETES.value,
            'cloud_run': ServiceCategory.CONTAINER.value,
            'storage': ServiceCategory.STORAGE.value,
            'spanner': ServiceCategory.DATABASE.value,
            'firestore': ServiceCategory.DATABASE.value,
            'bigtable': ServiceCategory.DATABASE.value,
            'memorystore': ServiceCategory.DATABASE.value,
            'app_engine': ServiceCategory.SERVERLESS.value
        }

        # GCP region code to readable region mapping
        self.region_map = {
            'us-central1': 'Iowa',
            'us-east1': 'South Carolina',
            'us-east4': 'Northern Virginia',
            'us-west1': 'Oregon',
            'us-west2': 'Los Angeles',
            'us-west3': 'Salt Lake City',
            'us-west4': 'Las Vegas',
            'northamerica-northeast1': 'Montreal',
            'northamerica-northeast2': 'Toronto',
            'southamerica-east1': 'São Paulo',
            'europe-west1': 'Belgium',
            'europe-west2': 'London',
            'europe-west3': 'Frankfurt',
            'europe-west4': 'Netherlands',
            'europe-west6': 'Zurich',
            'europe-central2': 'Warsaw',
            'europe-north1': 'Finland',
            'asia-east1': 'Taiwan',
            'asia-east2': 'Hong Kong',
            'asia-northeast1': 'Tokyo',
            'asia-northeast2': 'Osaka',
            'asia-northeast3': 'Seoul',
            'asia-south1': 'Mumbai',
            'asia-southeast1': 'Singapore',
            'asia-southeast2': 'Jakarta',
            'australia-southeast1': 'Sydney',
            'australia-southeast2': 'Melbourne'
        }

    def transform_all_services(self, output_file: str = "gcp_standardized_services.json"):
        """Transform all GCP service files"""
        print("="*80)
        print("GCP DATA TRANSFORMATION")
        print("="*80)

        # Process each service type
        self.transform_compute()
        self.transform_cloud_sql()
        self.transform_functions()
        self.transform_gke()
        self.transform_cloud_run()
        self.transform_storage()
        self.transform_spanner()
        self.transform_firestore()
        self.transform_bigtable()
        self.transform_memorystore()
        self.transform_app_engine()

        # Save to file
        self.save_services(output_file)

        # Print summary
        self.print_summary()

    def transform_compute(self):
        """Transform Compute Engine pricing data"""
        print("\n  Processing Compute Engine...")
        file_path = self._find_file_by_pattern("gcp_compute_pricing_*.json")
        if not file_path:
            print("     Compute Engine file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_compute_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Compute Engine SKUs")

    def transform_cloud_sql(self):
        """Transform Cloud SQL pricing data"""
        print("\n️  Processing Cloud SQL...")
        file_path = self._find_file_by_pattern("gcp_cloud_sql_pricing_*.json")
        if not file_path:
            print("     Cloud SQL file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_cloud_sql_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Cloud SQL SKUs")

    def transform_functions(self):
        """Transform Cloud Functions pricing data"""
        print("\n Processing Cloud Functions...")
        file_path = self._find_file_by_pattern("gcp_functions_pricing_*.json")
        if not file_path:
            print("     Cloud Functions file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_functions_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Cloud Functions SKUs")

    def transform_gke(self):
        """Transform GKE pricing data"""
        print("\n  Processing Google Kubernetes Engine...")
        file_path = self._find_file_by_pattern("gcp_gke_pricing_*.json")
        if not file_path:
            print("     GKE file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_gke_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} GKE SKUs")

    def transform_cloud_run(self):
        """Transform Cloud Run pricing data"""
        print("\n Processing Cloud Run...")
        file_path = self._find_file_by_pattern("gcp_cloud_run_pricing_*.json")
        if not file_path:
            print("     Cloud Run file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_cloud_run_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Cloud Run SKUs")

    def transform_storage(self):
        """Transform Cloud Storage pricing data"""
        print("\n Processing Cloud Storage...")
        file_path = self._find_file_by_pattern("gcp_storage_pricing_*.json")
        if not file_path:
            print("     Cloud Storage file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_storage_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Cloud Storage SKUs")

    def transform_spanner(self):
        """Transform Cloud Spanner pricing data"""
        print("\n Processing Cloud Spanner...")
        file_path = self._find_file_by_pattern("gcp_spanner_pricing_*.json")
        if not file_path:
            print("     Cloud Spanner file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_spanner_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Cloud Spanner SKUs")

    def transform_firestore(self):
        """Transform Firestore pricing data"""
        print("\n Processing Firestore...")
        file_path = self._find_file_by_pattern("gcp_firestore_pricing_*.json")
        if not file_path:
            print("     Firestore file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_firestore_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Firestore SKUs")

    def transform_bigtable(self):
        """Transform Cloud Bigtable pricing data"""
        print("\n Processing Cloud Bigtable...")
        file_path = self._find_file_by_pattern("gcp_bigtable_pricing_*.json")
        if not file_path:
            print("     Cloud Bigtable file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_bigtable_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} Cloud Bigtable SKUs")

    def transform_memorystore(self):
        """Transform Memorystore pricing data"""
        print("\n Processing Memorystore...")
        file_path = self._find_file_by_pattern("gcp_memorystore_pricing_*.json")
        if not file_path:
            print("     Memorystore file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_memorystore_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"   Processed {count} Memorystore SKUs")

    def transform_app_engine(self):
        """Transform App Engine pricing data"""
        print("\n Processing App Engine...")
        file_path = self._find_file_by_pattern("gcp_app_engine_pricing_*.json")
        if not file_path:
            print("     App Engine file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for sku in data.get('skus', []):
            service = self._transform_app_engine_sku(sku)
            if service:
                self.services.append(service)
                count += 1

        print(f"    Processed {count} App Engine SKUs")

    # Transform individual SKUs

    def _transform_compute_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Compute Engine SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')
            category = sku.get('category', {})

            # Only process CPU and RAM components for standard instances
            resource_group = category.get('resource_group', '')
            usage_type = category.get('usage_type', 'OnDemand')

            # Skip if not CPU or RAM
            if resource_group not in ['CPU', 'RAM']:
                return None

            # Skip sole tenancy and other specialized offerings for now
            if any(x in description for x in ['Sole Tenancy', 'Commitment v1', 'Accelerator']):
                return None

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Parse instance family and details from description
            instance_info = self._parse_compute_instance_info(description)
            if not instance_info:
                return None

            instance_family = instance_info['family']
            instance_type = instance_info['type']
            is_spot = instance_info['is_spot']

            # Determine pricing model
            pricing_model = "spot" if is_spot else "on_demand"
            if "Commit" in usage_type:
                pricing_model = "reserved"

            # Create service ID with component type
            service_id = f"gcp_compute_{instance_family}_{resource_group.lower()}_{region}_{sku_id}"

            # Create specs based on component type
            specs = TechnicalSpecs()
            if resource_group == 'CPU':
                specs.vcpu = 1.0  # Per core pricing
            elif resource_group == 'RAM':
                specs.memory_gb = 1.0  # Per GB pricing

            # Determine architecture
            if instance_family in ['n2d', 't2d']:
                specs.architecture = "AMD EPYC"
            elif instance_family in ['t2a']:
                specs.architecture = "ARM64"
            else:
                specs.architecture = "x86_64"

            # Create description
            component_name = "vCPU" if resource_group == 'CPU' else "GB RAM"
            pricing_desc = "Spot" if is_spot else "On-Demand"
            if pricing_model == "reserved":
                pricing_desc = "Committed Use"

            full_description = f"Google Compute Engine {instance_family.upper()} {instance_type} {component_name} ({pricing_desc}). {description}"

            # Features
            features = [
                f"{instance_family.upper()} machine family",
                f"{pricing_desc} pricing",
                "Live migration" if not is_spot else "No live migration (Spot)",
                "Custom machine types available"
            ]

            if is_spot:
                features.append("Up to 91% discount vs on-demand")

            if instance_family == 'e2':
                features.extend(["Cost-optimized", "Shared-core available"])
            elif instance_family in ['n2', 'n2d']:
                features.extend(["General purpose", "Balanced performance"])
            elif instance_family in ['c2', 'c2d', 'c3']:
                features.extend(["Compute-optimized", "High performance"])
            elif instance_family in ['m1', 'm2', 'm3']:
                features.extend(["Memory-optimized", "High memory-to-CPU ratio"])
            elif instance_family == 't2a':
                features.extend(["ARM-based", "Cost-effective"])

            # Use cases based on family
            use_cases = self._get_compute_use_cases(instance_family)

            # Create service
            service = CloudService(
                service_id=service_id,
                provider="gcp",
                service_name=f"Compute Engine {instance_family.upper()} {instance_type} ({component_name})",
                service_type="compute",
                category=self.service_type_map['compute'],
                description=full_description,
                short_description=f"GCE {instance_family.upper()}: {component_name} ({pricing_desc})",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=use_cases,
                tags=["compute", "vm", "gce", instance_family.lower(), pricing_model],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_cloud_sql_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Cloud SQL SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')
            category = sku.get('category', {})

            # Focus on instance-related SKUs
            resource_group = category.get('resource_group', '')
            if 'Instance' not in resource_group and 'CPU' not in resource_group and 'RAM' not in resource_group:
                return None

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Parse database engine and instance type
            db_engine = self._parse_db_engine(description)
            instance_type = self._parse_sql_instance_type(description)

            # Extract specs
            specs = self._extract_sql_specs(description)
            specs.database_engine = db_engine

            # Create description
            full_description = f"Google Cloud SQL {db_engine} managed database instance. {description}"

            # Features
            features = [
                f"{db_engine} engine",
                "Automated backups",
                "Point-in-time recovery",
                "Automatic replication",
                "Automated patching",
                "High availability configuration"
            ]

            # Create service
            service = CloudService(
                service_id=f"gcp_cloudsql_{db_engine}_{instance_type}_{region}_{sku_id}",
                provider="gcp",
                service_name=f"Cloud SQL {db_engine} {instance_type}",
                service_type="cloud_sql",
                category=self.service_type_map['cloud_sql'],
                description=full_description,
                short_description=f"Cloud SQL {db_engine}: {specs.vcpu or 'variable'} vCPU, {specs.memory_gb or 'variable'} GB RAM",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Web applications",
                    "E-commerce platforms",
                    "Mobile applications",
                    "Enterprise applications"
                ],
                tags=["database", "cloud-sql", db_engine.lower(), "managed"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_functions_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Cloud Functions SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')
            category = sku.get('category', {})

            # Focus on compute-related SKUs
            resource_group = category.get('resource_group', '')
            if resource_group not in ['Compute', 'Functions']:
                return None

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Determine generation
            generation = "2nd Gen" if "2nd gen" in description.lower() else "1st Gen"

            # Create description
            full_description = f"Google Cloud Functions {generation} - Serverless function execution. {description}"

            # Create specs
            specs = TechnicalSpecs(
                memory_gb=8.0,  # Max memory for Cloud Functions
                architecture="x86_64"
            )

            # Features
            features = [
                "Event-driven execution",
                "Automatic scaling",
                "Pay per invocation",
                "Integrated with Google Cloud services",
                f"{generation} runtime"
            ]

            if generation == "2nd Gen":
                features.extend([
                    "Longer request timeout (60 minutes)",
                    "Larger instances",
                    "CloudEvents support"
                ])

            # Create service
            service = CloudService(
                service_id=f"gcp_functions_{generation.replace(' ', '_')}_{region}_{sku_id}",
                provider="gcp",
                service_name=f"Cloud Functions ({generation})",
                service_type="functions",
                category=self.service_type_map['functions'],
                description=full_description,
                short_description=f"Serverless functions {generation}",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "API backends",
                    "Data processing",
                    "Real-time file processing",
                    "IoT backends",
                    "Webhooks"
                ],
                tags=["serverless", "functions", "compute", generation.lower()],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_gke_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single GKE SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Create description
            full_description = f"Google Kubernetes Engine - Managed Kubernetes service. {description}"

            # Create specs
            specs = TechnicalSpecs()

            # Features
            features = [
                "Managed Kubernetes control plane",
                "Automatic upgrades",
                "Integrated with Google Cloud services",
                "Multi-zone clusters",
                "Workload identity",
                "Binary authorization"
            ]

            # Create service
            service = CloudService(
                service_id=f"gcp_gke_{region}_{sku_id}",
                provider="gcp",
                service_name="Google Kubernetes Engine",
                service_type="gke",
                category=self.service_type_map['gke'],
                description=full_description,
                short_description="Managed Kubernetes service",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Microservices",
                    "Container orchestration",
                    "Hybrid applications",
                    "Batch processing"
                ],
                tags=["kubernetes", "containers", "gke", "orchestration"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_cloud_run_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Cloud Run SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')
            category = sku.get('category', {})

            # Focus on compute resources
            resource_group = category.get('resource_group', '')
            if resource_group not in ['Compute', 'Cloud Run']:
                return None

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Create description
            full_description = f"Google Cloud Run - Serverless container platform. {description}"

            # Create specs
            specs = TechnicalSpecs(
                memory_gb=32.0,  # Max memory for Cloud Run
                vcpu=8.0  # Max vCPUs
            )

            # Features
            features = [
                "Serverless container execution",
                "Automatic scaling to zero",
                "Pay per use",
                "HTTPS endpoints",
                "WebSocket support",
                "gRPC support",
                "Direct VPC access"
            ]

            # Create service
            service = CloudService(
                service_id=f"gcp_cloud_run_{region}_{sku_id}",
                provider="gcp",
                service_name="Cloud Run",
                service_type="cloud_run",
                category=self.service_type_map['cloud_run'],
                description=full_description,
                short_description="Serverless container platform",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Microservices",
                    "Web applications",
                    "APIs",
                    "Batch jobs"
                ],
                tags=["serverless", "containers", "cloud-run"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_storage_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Cloud Storage SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')
            category = sku.get('category', {})

            # Focus on storage SKUs
            resource_group = category.get('resource_group', '')
            if 'Storage' not in resource_group:
                return None

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Parse storage class
            storage_class = self._parse_storage_class(description)

            # Create description
            full_description = f"Google Cloud Storage {storage_class} class. {self._get_storage_class_description(storage_class)}"

            # Create specs
            specs = TechnicalSpecs(
                storage_type="Object Storage"
            )

            # Features
            features = self._get_storage_features(storage_class)

            # Create service
            service = CloudService(
                service_id=f"gcp_storage_{storage_class}_{region}_{sku_id}",
                provider="gcp",
                service_name=f"Cloud Storage ({storage_class})",
                service_type="storage",
                category=self.service_type_map['storage'],
                description=full_description,
                short_description=f"Object storage - {storage_class} class",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Data lakes",
                    "Backup and restore",
                    "Content distribution",
                    "Archive storage"
                ],
                tags=["storage", "gcs", "object-storage", storage_class.lower()],
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_spanner_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Cloud Spanner SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Create description
            full_description = f"Google Cloud Spanner - Horizontally scalable, strongly consistent, relational database. {description}"

            # Create specs
            specs = TechnicalSpecs(
                database_engine="Spanner",
                storage_type="Distributed"
            )

            # Features
            features = [
                "Horizontal scalability",
                "Strong consistency",
                "High availability (99.999%)",
                "Automatic replication",
                "ACID transactions",
                "SQL support"
            ]

            # Create service
            service = CloudService(
                service_id=f"gcp_spanner_{region}_{sku_id}",
                provider="gcp",
                service_name="Cloud Spanner",
                service_type="spanner",
                category=self.service_type_map['spanner'],
                description=full_description,
                short_description="Globally distributed relational database",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Global applications",
                    "Financial services",
                    "E-commerce",
                    "Gaming"
                ],
                tags=["database", "spanner", "distributed", "sql"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_firestore_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Firestore SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Determine if free tier
            has_free_tier = "with free tier" in description.lower()

            # Create description
            full_description = f"Google Cloud Firestore - NoSQL document database. {description}"

            # Create specs
            specs = TechnicalSpecs(
                database_engine="Firestore",
                storage_type="NoSQL Document"
            )

            # Features
            features = [
                "Real-time synchronization",
                "Offline support",
                "Automatic scaling",
                "ACID transactions",
                "Mobile and web SDKs"
            ]

            if has_free_tier:
                features.append("Free tier available")

            # Create service
            service = CloudService(
                service_id=f"gcp_firestore_{region}_{sku_id}",
                provider="gcp",
                service_name="Cloud Firestore",
                service_type="firestore",
                category=self.service_type_map['firestore'],
                description=full_description,
                short_description="NoSQL document database",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Mobile applications",
                    "Web applications",
                    "Real-time apps",
                    "Gaming"
                ],
                tags=["database", "firestore", "nosql", "document"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_bigtable_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Cloud Bigtable SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Create description
            full_description = f"Google Cloud Bigtable - NoSQL wide-column database. {description}"

            # Create specs
            specs = TechnicalSpecs(
                database_engine="Bigtable",
                storage_type="NoSQL Wide-column"
            )

            # Features
            features = [
                "Low latency",
                "High throughput",
                "Automatic replication",
                "HBase compatible",
                "Linear scalability"
            ]

            # Create service
            service = CloudService(
                service_id=f"gcp_bigtable_{region}_{sku_id}",
                provider="gcp",
                service_name="Cloud Bigtable",
                service_type="bigtable",
                category=self.service_type_map['bigtable'],
                description=full_description,
                short_description="NoSQL wide-column database",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Time-series data",
                    "IoT data",
                    "Financial data",
                    "Analytics"
                ],
                tags=["database", "bigtable", "nosql", "wide-column"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_memorystore_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single Memorystore SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Determine engine
            engine = "Redis" if "redis" in description.lower() else "Memcached"

            # Create description
            full_description = f"Google Cloud Memorystore for {engine} - Managed in-memory data store. {description}"

            # Create specs
            specs = TechnicalSpecs(
                database_engine=f"Memorystore {engine}",
                storage_type="In-memory"
            )

            # Features
            features = [
                f"Managed {engine}",
                "High availability",
                "Automatic failover",
                "Monitoring and alerting",
                "VPC peering"
            ]

            # Create service
            service = CloudService(
                service_id=f"gcp_memorystore_{engine}_{region}_{sku_id}",
                provider="gcp",
                service_name=f"Memorystore for {engine}",
                service_type="memorystore",
                category=self.service_type_map['memorystore'],
                description=full_description,
                short_description=f"Managed {engine} service",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Caching",
                    "Session management",
                    "Pub/Sub",
                    "Leaderboards"
                ],
                tags=["database", "memorystore", engine.lower(), "cache"],
                supports_auto_scaling=False,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=sku_id,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            return None

    def _transform_app_engine_sku(self, sku: Dict) -> Optional[CloudService]:
        """Transform single App Engine SKU"""
        try:
            description = sku.get('description', '')
            sku_id = sku.get('sku_id', '')

            # Extract region
            regions = sku.get('service_regions', ['global'])
            region = regions[0] if regions else 'global'

            # Extract pricing
            pricing_list = self._extract_gcp_pricing(sku, region)
            if not pricing_list:
                return None

            # Determine environment
            environment = "Flexible" if "flexible" in description.lower() else "Standard"

            # Create description
            full_description = f"Google App Engine {environment} - Platform as a Service. {description}"

            # Create specs
            specs = TechnicalSpecs()

            # Features
            features = [
                f"{environment} environment",
                "Automatic scaling",
                "Built-in services",
                "Traffic splitting",
                "Version management"
            ]

            if environment == "Standard":
                features.extend(["Fast startup", "Free tier available"])
            else:
                features.extend(["Custom runtime", "SSH access"])

            # Create service
            service = CloudService(
                service_id=f"gcp_app_engine_{environment}_{region}_{sku_id}",
                provider="gcp",
                service_name=f"App Engine ({environment})",
                service_type="app_engine",
                category=self.service_type_map['app_engine'],
                description=full_description,
                short_description=f"PaaS {environment} environment",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=regions,
                features=features,
                use_cases=[
                    "Web applications",
                    "Mobile backends",
                    "RESTful APIs",
                    "IoT applications"
                ],
                tags=["paas", "app-engine", environment.lower()],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku_id,
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

    def _extract_gcp_pricing(self, sku: Dict, region: str) -> List[PricingInfo]:
        """Extract pricing information from GCP SKU"""
        pricing_list = []

        try:
            pricing_info_list = sku.get('pricing_info', [])

            for pricing_info in pricing_info_list:
                pricing_expr = pricing_info.get('pricing_expression', {})
                tiered_rates = pricing_expr.get('tiered_rates', [])
                unit = pricing_expr.get('usage_unit', '')

                # Get the first non-zero tier
                for tier in tiered_rates:
                    unit_price = tier.get('unit_price', {})
                    units = int(unit_price.get('units', '0'))
                    nanos = int(unit_price.get('nanos', 0))

                    # Convert to USD
                    price_usd = units + (nanos / 1e9)

                    if price_usd > 0:
                        # Check for free tier
                        start_usage = tier.get('start_usage_amount', 0)
                        has_free_tier = start_usage > 0 and len(tiered_rates) > 1

                        pricing_info_obj = PricingInfo(
                            price_per_unit=price_usd,
                            currency="USD",
                            unit=unit,
                            pricing_model="on_demand",
                            region=region,
                            free_tier_included=has_free_tier
                        )
                        pricing_list.append(pricing_info_obj)
                        break  # Only take first non-zero tier

        except Exception as e:
            pass

        return pricing_list

    def _parse_machine_type(self, description: str) -> Optional[str]:
        """Parse machine type from description"""
        # Common patterns: "n1-standard-1", "n2-standard-4", "e2-medium"
        pattern = r'(n1|n2|n2d|e2|c2|m1|m2)[-\s](standard|highmem|highcpu|micro|small|medium|large|xlarge)[-\s]?\d*'
        match = re.search(pattern, description.lower())
        if match:
            return match.group(0).replace(' ', '-')
        return None

    def _parse_compute_instance_info(self, description: str) -> Optional[Dict]:
        """Parse instance family and type from description"""
        desc_lower = description.lower()

        # Determine if Spot/Preemptible
        is_spot = 'spot' in desc_lower or 'preemptible' in desc_lower

        # Parse instance family
        families = ['n1', 'n2', 'n2d', 'e2', 'c2', 'c2d', 'c3', 'm1', 'm2', 'm3', 't2d', 't2a']
        instance_family = None
        for family in families:
            if family in desc_lower:
                instance_family = family
                break

        if not instance_family:
            return None

        # Parse instance type (standard, custom, highmem, highcpu, etc.)
        instance_type = 'standard'
        if 'custom' in desc_lower:
            instance_type = 'custom'
        elif 'highmem' in desc_lower:
            instance_type = 'highmem'
        elif 'highcpu' in desc_lower:
            instance_type = 'highcpu'
        elif 'micro' in desc_lower or 'small' in desc_lower or 'medium' in desc_lower:
            instance_type = 'shared-core'

        return {
            'family': instance_family,
            'type': instance_type,
            'is_spot': is_spot
        }

    def _get_compute_use_cases(self, instance_family: str) -> List[str]:
        """Get use cases based on instance family"""
        use_cases_map = {
            'e2': ["Web servers", "Development", "Small databases", "Microservices"],
            'n1': ["General purpose workloads", "Web servers", "Application servers"],
            'n2': ["General purpose workloads", "Medium-large databases", "Application servers"],
            'n2d': ["General purpose workloads", "Cost-optimized compute", "Gaming servers"],
            'c2': ["Compute-intensive workloads", "HPC", "Gaming servers", "Ad serving"],
            'c2d': ["Compute-intensive workloads", "Electronic design automation", "Gaming"],
            'c3': ["Compute-intensive workloads", "HPC", "High-performance databases"],
            'm1': ["Large in-memory databases", "SAP HANA", "In-memory analytics"],
            'm2': ["Large in-memory databases", "SAP HANA", "In-memory analytics"],
            'm3': ["Large in-memory databases", "SAP HANA", "In-memory analytics"],
            't2d': ["Scale-out workloads", "Web serving", "Containerized applications"],
            't2a': ["Scale-out workloads", "Web serving", "Microservices", "Cost-optimized"]
        }
        return use_cases_map.get(instance_family, ["General purpose workloads", "Web servers"])

    def _extract_compute_specs(self, description: str, machine_type: str) -> TechnicalSpecs:
        """Extract compute specs from description"""
        specs = TechnicalSpecs()

        # Parse vCPU
        vcpu_pattern = r'(\d+)\s*vCPU'
        vcpu_match = re.search(vcpu_pattern, description, re.IGNORECASE)
        if vcpu_match:
            specs.vcpu = float(vcpu_match.group(1))

        # Parse memory
        mem_pattern = r'(\d+(?:\.\d+)?)\s*GB'
        mem_match = re.search(mem_pattern, description, re.IGNORECASE)
        if mem_match:
            specs.memory_gb = float(mem_match.group(1))

        # Determine architecture
        if 'n2d' in machine_type.lower():
            specs.architecture = "AMD EPYC"
        else:
            specs.architecture = "x86_64"

        return specs

    def _parse_db_engine(self, description: str) -> str:
        """Parse database engine from description"""
        desc_lower = description.lower()
        if 'mysql' in desc_lower:
            return 'MySQL'
        elif 'postgresql' in desc_lower or 'postgres' in desc_lower:
            return 'PostgreSQL'
        elif 'sql server' in desc_lower:
            return 'SQL Server'
        else:
            return 'Unknown'

    def _parse_sql_instance_type(self, description: str) -> str:
        """Parse SQL instance type from description"""
        # Common patterns: db-n1-standard-1, db-custom-4-15360
        pattern = r'db-[\w-]+'
        match = re.search(pattern, description.lower())
        if match:
            return match.group(0)
        return 'standard'

    def _extract_sql_specs(self, description: str) -> TechnicalSpecs:
        """Extract SQL specs from description"""
        specs = TechnicalSpecs()

        # Parse vCPU
        vcpu_pattern = r'(\d+)\s*vCPU'
        vcpu_match = re.search(vcpu_pattern, description, re.IGNORECASE)
        if vcpu_match:
            specs.vcpu = float(vcpu_match.group(1))

        # Parse memory
        mem_pattern = r'(\d+(?:\.\d+)?)\s*GB'
        mem_match = re.search(mem_pattern, description, re.IGNORECASE)
        if mem_match:
            specs.memory_gb = float(mem_match.group(1))

        return specs

    def _parse_storage_class(self, description: str) -> str:
        """Parse storage class from description"""
        desc_lower = description.lower()
        if 'standard' in desc_lower:
            return 'Standard'
        elif 'nearline' in desc_lower:
            return 'Nearline'
        elif 'coldline' in desc_lower:
            return 'Coldline'
        elif 'archive' in desc_lower:
            return 'Archive'
        else:
            return 'Standard'

    def _get_storage_class_description(self, storage_class: str) -> str:
        """Get description for storage class"""
        descriptions = {
            'Standard': 'Best for frequently accessed data with low latency',
            'Nearline': 'Low-cost storage for data accessed less than once a month',
            'Coldline': 'Very low-cost storage for data accessed less than once a quarter',
            'Archive': 'Lowest-cost storage for data accessed less than once a year'
        }
        return descriptions.get(storage_class, 'Object storage')

    def _get_storage_features(self, storage_class: str) -> List[str]:
        """Get features for storage class"""
        base_features = [
            "11 9's durability",
            "Versioning",
            "Lifecycle management",
            "Encryption at rest",
            "Global accessibility"
        ]

        class_features = {
            'Standard': ["Low latency", "High throughput", "No retrieval cost"],
            'Nearline': ["30-day minimum storage", "Lower storage cost", "Retrieval fees apply"],
            'Coldline': ["90-day minimum storage", "Very low storage cost", "Higher retrieval fees"],
            'Archive': ["365-day minimum storage", "Lowest storage cost", "Highest retrieval fees"]
        }

        return base_features + class_features.get(storage_class, [])

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
                'provider': 'gcp',
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
            print(f"  {service_type.upper()}: {count} services")

        print(f"\n  TOTAL: {len(self.services)} services")
        print("="*80)


def main():
    """Main execution"""
    # Create transformer
    transformer = GCPDataTransformer(data_dir="../data/GCP")

    # Transform all services
    transformer.transform_all_services(output_file="gcp_standardized_services.json")

    print("\n Transformation complete!")
    print(" Output file: gcp_standardized_services.json")


if __name__ == "__main__":
    main()