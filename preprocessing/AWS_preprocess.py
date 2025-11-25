"""
AWS Pricing Data Transformer
Transforms AWS pricing JSON files into standardized CloudService format
"""

import json
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

# Import the standardized schema (assume it's in the same directory)
from standard_cloud_service import CloudService, TechnicalSpecs, PricingInfo, ServiceCategory


class AWSDataTransformer:
    """Transform AWS pricing data into standardized format"""

    def __init__(self, data_dir: str = "./data/AWS"):
        self.data_dir = data_dir
        self.services = []

        # Service type mappings
        self.service_type_map = {
            'ec2': ServiceCategory.COMPUTE.value,
            'rds': ServiceCategory.DATABASE.value,
            'lambda': ServiceCategory.SERVERLESS.value,
            'eks': ServiceCategory.KUBERNETES.value,
            'ecs': ServiceCategory.CONTAINER.value,
            's3': ServiceCategory.STORAGE.value
        }

        # Region name mappings
        self.region_map = {
            'US East (N. Virginia)': 'us-east-1',
            'US East (Ohio)': 'us-east-2',
            'US West (N. California)': 'us-west-1',
            'US West (Oregon)': 'us-west-2',
            'Canada (Central)': 'ca-central-1',
            'Canada West (Calgary)': 'ca-west-1',
            'EU (Ireland)': 'eu-west-1',
            'EU (Frankfurt)': 'eu-central-1',
            'EU (London)': 'eu-west-2',
            'EU (Paris)': 'eu-west-3',
            'EU (Stockholm)': 'eu-north-1',
            'Asia Pacific (Tokyo)': 'ap-northeast-1',
            'Asia Pacific (Seoul)': 'ap-northeast-2',
            'Asia Pacific (Singapore)': 'ap-southeast-1',
            'Asia Pacific (Sydney)': 'ap-southeast-2',
            'Asia Pacific (Mumbai)': 'ap-south-1',
            'South America (São Paulo)': 'sa-east-1',
            'China (Beijing)': 'cn-north-1',
            'China (Ningxia)': 'cn-northwest-1'
        }

    def transform_all_services(self, output_file: str = "aws_standardized_services.json"):
        """Transform all AWS service files"""
        print("="*80)
        print("AWS DATA TRANSFORMATION")
        print("="*80)

        # Process each service type
        self.transform_ec2()
        self.transform_lambda()
        self.transform_rds()
        self.transform_eks()
        self.transform_ecs()
        self.transform_s3()

        # Save to file
        self.save_services(output_file)

        # Print summary
        self.print_summary()

    def transform_ec2(self):
        """Transform EC2 pricing data"""
        print("\n Processing EC2...")
        file_path = self._find_file_by_pattern("ec2_pricing_*.json")
        if not file_path:
            print("    EC2 file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data:
            service = self._transform_ec2_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"   Processed {count} EC2 instances")

    def transform_lambda(self):
        """Transform Lambda pricing data"""
        print("\n Processing Lambda...")
        file_path = self._find_file_by_pattern("lambda_pricing_*.json")
        if not file_path:
            print("    Lambda file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data:
            service = self._transform_lambda_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"   Processed {count} Lambda pricing entries")

    def transform_rds(self):
        """Transform RDS pricing data"""
        print("\n️  Processing RDS...")

        # Find all RDS files
        rds_files = [f for f in os.listdir(self.data_dir) if f.startswith('rds_') and f.endswith('.json')]

        total_count = 0
        for rds_file in rds_files:
            file_path = os.path.join(self.data_dir, rds_file)
            with open(file_path, 'r') as f:
                data = json.load(f)

            count = 0
            for item in data:
                service = self._transform_rds_item(item)
                if service:
                    self.services.append(service)
                    count += 1

            total_count += count

        print(f"   Processed {total_count} RDS instances across {len(rds_files)} files")

    def transform_eks(self):
        """Transform EKS pricing data"""
        print("\n  Processing EKS...")
        file_path = self._find_file_by_pattern("eks_pricing_*.json")
        if not file_path:
            print("    EKS file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data:
            service = self._transform_eks_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"   Processed {count} EKS pricing entries")

    def transform_ecs(self):
        """Transform ECS pricing data"""
        print("\n Processing ECS...")
        file_path = self._find_file_by_pattern("ecs_pricing_*.json")
        if not file_path:
            print("    ECS file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data:
            service = self._transform_ecs_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"   Processed {count} ECS pricing entries")

    def transform_s3(self):
        """Transform S3 pricing data"""
        print("\n Processing S3...")
        file_path = self._find_file_by_pattern("s3_pricing_*.json")
        if not file_path:
            print("    S3 file not found")
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        count = 0
        for item in data:
            service = self._transform_s3_item(item)
            if service:
                self.services.append(service)
                count += 1

        print(f"   Processed {count} S3 pricing entries")

    def _transform_ec2_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single EC2 item"""
        try:
            product = item.get('product', {})
            attributes = product.get('attributes', {})
            sku = product.get('sku', '')

            # Extract instance type
            instance_type = attributes.get('instanceType', '')
            if not instance_type:
                return None

            # Extract specs
            vcpu = self._parse_float(attributes.get('vcpu', '0'))
            memory_str = attributes.get('memory', '0 GiB')
            memory_gb = self._parse_memory(memory_str)

            # Extract region
            location = attributes.get('location', '')
            region = self.region_map.get(location, location.lower().replace(' ', '-'))

            # Extract pricing
            pricing_list = self._extract_pricing(item, region)

            # Create description
            description = self._create_ec2_description(attributes, instance_type)

            # Create specs
            specs = TechnicalSpecs(
                vcpu=vcpu,
                memory_gb=memory_gb,
                storage_type=attributes.get('storage', 'EBS-optimized'),
                network_performance=attributes.get('networkPerformance', ''),
                architecture=self._map_architecture(attributes.get('physicalProcessor', '')),
                operating_system=attributes.get('operatingSystem', 'Linux')
            )

            # Determine features
            features = self._extract_ec2_features(attributes)

            # Create service
            service = CloudService(
                service_id=f"aws_ec2_{instance_type}_{region}_{sku}",
                provider="aws",
                service_name=f"EC2 {instance_type}",
                service_type="ec2",
                category=self.service_type_map['ec2'],
                description=description,
                short_description=f"EC2 {instance_type}: {vcpu} vCPU, {memory_gb} GB RAM",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],  # Would need to aggregate across regions
                features=features,
                use_cases=["Web servers", "Application servers", "Batch processing", "Development"],
                tags=["compute", "vm", "ec2", instance_type.lower()],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            print(f"      Error processing EC2 item: {str(e)}")
            return None

    def _transform_lambda_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single Lambda item"""
        try:
            product = item.get('product', {})
            attributes = product.get('attributes', {})
            sku = product.get('sku', '')

            # Extract location
            location = attributes.get('location', '')
            region = self.region_map.get(location, attributes.get('regionCode', 'unknown'))

            # Extract pricing
            pricing_list = self._extract_pricing(item, region)
            if not pricing_list:
                return None

            # Determine if ARM or x86
            group = attributes.get('group', '')
            is_arm = 'ARM' in group or 'ARM' in attributes.get('usagetype', '')
            arch = "ARM64" if is_arm else "x86_64"

            # Create description
            group_desc = attributes.get('groupDescription', '')
            description = f"AWS Lambda serverless compute. {group_desc}"

            # Create specs
            specs = TechnicalSpecs(
                memory_gb=10.0,  # Lambda max memory
                architecture=arch
            )

            # Features
            features = [
                "Event-driven execution",
                "Automatic scaling",
                "Pay per invocation",
                "Integrated with AWS services",
                f"{arch} architecture"
            ]

            if is_arm:
                features.append("Better price-performance with Graviton2")

            # Create service
            service = CloudService(
                service_id=f"aws_lambda_{arch}_{region}_{sku}",
                provider="aws",
                service_name=f"AWS Lambda ({arch})",
                service_type="lambda",
                category=self.service_type_map['lambda'],
                description=description,
                short_description=f"Serverless compute with {arch}",
                specs=specs,
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
                tags=["serverless", "lambda", "compute", arch.lower()],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            print(f"      Error processing Lambda item: {str(e)}")
            return None

    def _transform_rds_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single RDS item"""
        try:
            product = item.get('product', {})
            attributes = product.get('attributes', {})
            sku = product.get('sku', '')

            # Extract instance class
            instance_class = attributes.get('instanceType', '')
            if not instance_class:
                return None

            # Extract database engine
            db_engine = attributes.get('databaseEngine', 'Unknown')
            deployment = attributes.get('deploymentOption', 'Single-AZ')

            # Extract specs
            vcpu = self._parse_float(attributes.get('vcpu', '0'))
            memory_str = attributes.get('memory', '0 GiB')
            memory_gb = self._parse_memory(memory_str)

            # Extract region
            location = attributes.get('location', '')
            region = self.region_map.get(location, location.lower().replace(' ', '-'))

            # Extract pricing
            pricing_list = self._extract_pricing(item, region)

            # Create description
            description = f"Amazon RDS {db_engine} database instance. {deployment} deployment for {'high availability' if 'Multi' in deployment else 'cost-effective operation'}."

            # Create specs
            specs = TechnicalSpecs(
                vcpu=vcpu,
                memory_gb=memory_gb,
                storage_type=attributes.get('storageMedia', 'SSD'),
                database_engine=db_engine,
                architecture=self._map_architecture(attributes.get('physicalProcessor', ''))
            )

            # Features
            features = [
                f"{db_engine} engine",
                f"{deployment} deployment",
                "Automated backups",
                "Point-in-time recovery",
                "Automated software patching"
            ]

            if 'Multi' in deployment:
                features.extend(["Automatic failover", "High availability"])

            # Create service
            service = CloudService(
                service_id=f"aws_rds_{db_engine}_{instance_class}_{deployment}_{region}_{sku}",
                provider="aws",
                service_name=f"RDS {db_engine} {instance_class} ({deployment})",
                service_type="rds",
                category=self.service_type_map['rds'],
                description=description,
                short_description=f"RDS {db_engine}: {vcpu} vCPU, {memory_gb} GB RAM",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Web applications",
                    "E-commerce platforms",
                    "Mobile applications",
                    "Enterprise applications"
                ],
                tags=["database", "rds", db_engine.lower(), "managed"],
                supports_auto_scaling=True,
                supports_multi_az=('Multi' in deployment),
                supports_encryption=True,
                raw_sku=sku,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            print(f"      Error processing RDS item: {str(e)}")
            return None

    def _transform_eks_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single EKS item"""
        try:
            product = item.get('product', {})
            attributes = product.get('attributes', {})
            sku = product.get('sku', '')

            # Extract region
            location = attributes.get('location', '')
            region = self.region_map.get(location, attributes.get('regionCode', 'unknown'))

            # Extract pricing
            pricing_list = self._extract_pricing(item, region)
            if not pricing_list:
                return None

            # Create description
            description = "Amazon Elastic Kubernetes Service (EKS) - Managed Kubernetes service. Run containerized applications using Kubernetes without managing control plane."

            # Create specs (EKS is a managed service, limited direct specs)
            specs = TechnicalSpecs()

            # Features
            features = [
                "Managed Kubernetes control plane",
                "Automatic version updates",
                "Integrated with AWS services",
                "Multi-AZ deployment",
                "Built-in security"
            ]

            # Create service
            service = CloudService(
                service_id=f"aws_eks_{region}_{sku}",
                provider="aws",
                service_name="Amazon EKS",
                service_type="eks",
                category=self.service_type_map['eks'],
                description=description,
                short_description="Managed Kubernetes service",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Microservices",
                    "Container orchestration",
                    "Hybrid applications",
                    "Batch processing"
                ],
                tags=["kubernetes", "containers", "eks", "orchestration"],
                supports_auto_scaling=True,
                supports_multi_az=True,
                supports_encryption=True,
                raw_sku=sku,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            print(f"      Error processing EKS item: {str(e)}")
            return None

    def _transform_ecs_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single ECS item"""
        try:
            product = item.get('product', {})
            attributes = product.get('attributes', {})
            sku = product.get('sku', '')

            # Extract region
            location = attributes.get('location', '')
            region = self.region_map.get(location, attributes.get('regionCode', 'unknown'))

            # Extract pricing
            pricing_list = self._extract_pricing(item, region)
            if not pricing_list:
                return None

            # Determine if Fargate or EC2
            usage_type = attributes.get('usagetype', '')
            is_fargate = 'Fargate' in attributes.get('group', '') or 'Fargate' in usage_type

            # Create description
            if is_fargate:
                description = "AWS Fargate for ECS - Serverless compute for containers. Run containers without managing servers."
            else:
                description = "Amazon ECS - Container orchestration service. Run Docker containers on EC2 instances."

            # Create specs
            specs = TechnicalSpecs()

            # Features
            features = [
                "Docker container support",
                "Task definitions",
                "Service auto-scaling",
                "Integrated with AWS services"
            ]

            if is_fargate:
                features.extend(["Serverless", "No server management"])
            else:
                features.append("EC2 instance based")

            # Create service
            service_name = "AWS Fargate" if is_fargate else "Amazon ECS"
            service = CloudService(
                service_id=f"aws_ecs_{'fargate' if is_fargate else 'ec2'}_{region}_{sku}",
                provider="aws",
                service_name=service_name,
                service_type="ecs",
                category=self.service_type_map['ecs'],
                description=description,
                short_description="Container orchestration service",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Microservices",
                    "Batch processing",
                    "Web applications",
                    "CI/CD pipelines"
                ],
                tags=["containers", "ecs", "docker", "fargate" if is_fargate else "ec2"],
                supports_auto_scaling=True,
                supports_encryption=True,
                raw_sku=sku,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            print(f"      Error processing ECS item: {str(e)}")
            return None

    def _transform_s3_item(self, item: Dict) -> Optional[CloudService]:
        """Transform single S3 item"""
        try:
            product = item.get('product', {})
            attributes = product.get('attributes', {})
            sku = product.get('sku', '')

            # Extract storage class
            storage_class = attributes.get('storageClass', 'Standard')

            # Extract region
            location = attributes.get('location', '')
            region = self.region_map.get(location, attributes.get('regionCode', 'unknown'))

            # Extract pricing
            pricing_list = self._extract_pricing(item, region)
            if not pricing_list:
                return None

            # Create description
            description = f"Amazon S3 {storage_class} storage class. {self._get_s3_class_description(storage_class)}"

            # Create specs
            specs = TechnicalSpecs(
                storage_type="Object Storage"
            )

            # Features based on storage class
            features = self._get_s3_features(storage_class)

            # Create service
            service = CloudService(
                service_id=f"aws_s3_{storage_class}_{region}_{sku}",
                provider="aws",
                service_name=f"Amazon S3 ({storage_class})",
                service_type="s3",
                category=self.service_type_map['s3'],
                description=description,
                short_description=f"Object storage - {storage_class} class",
                specs=specs,
                pricing=pricing_list,
                region=region,
                available_regions=[region],
                features=features,
                use_cases=[
                    "Data lakes",
                    "Backup and restore",
                    "Static website hosting",
                    "Content distribution"
                ],
                tags=["storage", "s3", "object-storage", storage_class.lower()],
                supports_encryption=True,
                raw_sku=sku,
                last_updated=datetime.now().isoformat()
            )

            return service

        except Exception as e:
            print(f"       Error processing S3 item: {str(e)}")
            return None

    # Helper methods

    def _find_file_by_pattern(self, pattern: str) -> Optional[str]:
        """Find file matching pattern"""
        import glob
        files = glob.glob(os.path.join(self.data_dir, pattern))
        return files[0] if files else None

    def _extract_pricing(self, item: Dict, region: str) -> List[PricingInfo]:
        """Extract pricing information from AWS item"""
        pricing_list = []

        try:
            terms = item.get('terms', {})
            on_demand = terms.get('OnDemand', {})

            for term_key, term_data in on_demand.items():
                price_dimensions = term_data.get('priceDimensions', {})

                for dimension_key, dimension in price_dimensions.items():
                    price_per_unit = dimension.get('pricePerUnit', {})
                    usd_price = float(price_per_unit.get('USD', '0'))
                    cny_price = float(price_per_unit.get('CNY', '0'))

                    # Convert CNY to USD if needed (approximate rate)
                    if cny_price > 0 and usd_price == 0:
                        usd_price = cny_price / 7.0  # Approximate conversion

                    if usd_price > 0:
                        pricing_info = PricingInfo(
                            price_per_unit=usd_price,
                            currency="USD",
                            unit=dimension.get('unit', ''),
                            pricing_model="on_demand",
                            region=region,
                            free_tier_included=False
                        )
                        pricing_list.append(pricing_info)

        except Exception as e:
            pass

        return pricing_list

    def _parse_float(self, value: str) -> float:
        """Parse float from string"""
        try:
            return float(value)
        except:
            return 0.0

    def _parse_memory(self, memory_str: str) -> float:
        """Parse memory string to GB"""
        try:
            # Examples: "8 GiB", "16 GB", "1,024 GiB"
            memory_str = memory_str.replace(',', '').upper()
            if 'GIB' in memory_str or 'GB' in memory_str:
                return float(re.search(r'([\d.]+)', memory_str).group(1))
            elif 'TIB' in memory_str or 'TB' in memory_str:
                return float(re.search(r'([\d.]+)', memory_str).group(1)) * 1024
            return 0.0
        except:
            return 0.0

    def _map_architecture(self, processor: str) -> str:
        """Map processor to architecture"""
        processor_lower = processor.lower()
        if 'graviton' in processor_lower or 'arm' in processor_lower:
            return "ARM64"
        elif 'amd' in processor_lower or 'intel' in processor_lower:
            return "x86_64"
        return "x86_64"

    def _create_ec2_description(self, attributes: Dict, instance_type: str) -> str:
        """Create description for EC2 instance"""
        family = attributes.get('instanceFamily', '')
        processor = attributes.get('physicalProcessor', '')
        network = attributes.get('networkPerformance', '')

        desc = f"Amazon EC2 {instance_type} instance. "
        if family:
            desc += f"Part of {family} family. "
        if processor:
            desc += f"Powered by {processor}. "
        if network:
            desc += f"Network performance: {network}."

        return desc

    def _extract_ec2_features(self, attributes: Dict) -> List[str]:
        """Extract features from EC2 attributes"""
        features = ["On-demand scaling", "Multiple instance types"]

        if attributes.get('enhancedNetworkingSupported') == 'Yes':
            features.append("Enhanced networking")
        if attributes.get('dedicatedEbsThroughput'):
            features.append("EBS optimized")
        if 'Graviton' in attributes.get('physicalProcessor', ''):
            features.append("ARM-based Graviton processor")

        return features

    def _get_s3_class_description(self, storage_class: str) -> str:
        """Get description for S3 storage class"""
        descriptions = {
            'Standard': 'Frequently accessed data with low latency and high throughput',
            'Intelligent-Tiering': 'Automatic cost savings by moving data between access tiers',
            'Standard-IA': 'Infrequently accessed data with rapid access when needed',
            'One Zone-IA': 'Lower-cost option for infrequently accessed data in single AZ',
            'Glacier': 'Long-term archive with retrieval times from minutes to hours',
            'Glacier Deep Archive': 'Lowest cost storage for long-term retention',
        }
        return descriptions.get(storage_class, 'Object storage')

    def _get_s3_features(self, storage_class: str) -> List[str]:
        """Get features for S3 storage class"""
        base_features = [
            "99.999999999% durability",
            "Versioning",
            "Lifecycle policies",
            "Encryption at rest"
        ]

        class_features = {
            'Standard': ["Low latency", "High throughput", "Frequent access optimized"],
            'Intelligent-Tiering': ["Automatic tiering", "Cost optimization", "No retrieval fees"],
            'Standard-IA': ["Lower cost", "Rapid access", "Infrequent access optimized"],
            'Glacier': ["Archive storage", "Configurable retrieval times", "Lowest cost for archival"],
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
                'provider': 'aws',
                'extraction_date': datetime.now().isoformat(),
                'total_services': len(self.services)
            },
            'services': services_output
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"   Saved {len(self.services)} services")

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
    transformer = AWSDataTransformer(data_dir="../data/AWS")

    # Transform all services
    transformer.transform_all_services(output_file="aws_standardized_services.json")

    print("\n Transformation complete!")
    print("Output file: aws_standardized_services.json")


if __name__ == "__main__":
    main()