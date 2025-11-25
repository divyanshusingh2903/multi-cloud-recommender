import boto3
import json
from datetime import datetime
from typing import List, Dict

class AWSPricingExtractor:
    def __init__(self, region='us-east-1'):
        self.client = boto3.client('pricing', region_name=region)

    def get_ec2_pricing(self) -> List[Dict]:
        """Get all EC2 instance pricing data"""
        print("Fetching EC2 pricing data...")

        filters = [
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Compute Instance'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'}
        ]

        return self._get_all_pricing_data('AmazonEC2', filters)

    def get_rds_pricing(self, engine: str, deployment: str) -> List[Dict]:
        """Get RDS database pricing data for specific engine and deployment"""
        print(f"Fetching RDS pricing data for {engine} ({deployment})...")

        filters = [
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Database Instance'},
            {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': engine},
            {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': deployment}
        ]

        return self._get_all_pricing_data('AmazonRDS', filters)

    def get_lambda_pricing(self) -> List[Dict]:
        """Get all Lambda pricing data"""
        print("Fetching Lambda pricing data...")

        filters = []
        return self._get_all_pricing_data('AWSLambda', filters)

    def get_eks_pricing(self) -> List[Dict]:
        """Get all EKS pricing data"""
        print("Fetching EKS pricing data...")

        filters = []
        return self._get_all_pricing_data('AmazonEKS', filters)

    def get_ecs_pricing(self) -> List[Dict]:
        """Get all ECS/Fargate pricing data"""
        print("Fetching ECS/Fargate pricing data...")

        filters = []
        return self._get_all_pricing_data('AmazonECS', filters)

    def get_s3_pricing(self) -> List[Dict]:
        """Get all S3 pricing data"""
        print("Fetching S3 pricing data...")

        filters = [

        ]

        return self._get_all_pricing_data('AmazonS3', filters)

    def _get_all_pricing_data(self, service_code: str, filters: List[Dict]) -> List[Dict]:
        """Fetch ALL pricing data with pagination"""
        all_products = []
        next_token = None
        page_count = 0

        try:
            while True:
                page_count += 1
                params = {
                    'ServiceCode': service_code,
                    'Filters': filters,
                    'MaxResults': 100
                }

                if next_token:
                    params['NextToken'] = next_token

                response = self.client.get_products(**params)

                # Parse price list items
                for price_item in response.get('PriceList', []):
                    product_data = json.loads(price_item)
                    all_products.append(product_data)

                next_token = response.get('NextToken')

                print(f"  Page {page_count}: {len(all_products)} items so far...")

                if not next_token:
                    break

        except Exception as e:
            print(f"Error fetching pricing data: {str(e)}")

        print(f"  ✅ Complete! Total items: {len(all_products)}")
        return all_products

    # ============================================================
    # EXTRACT ALL SERVICES AND SAVE SEPARATELY
    # ============================================================
    def extract_all_services(self, output_dir: str = '.'):
        """Extract pricing data for all services into separate JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        summary = {
            'timestamp': timestamp,
            'extraction_date': datetime.now().isoformat(),
            'services': {}
        }

        def save_to_file(service_name, data):
            file_path = f"{output_dir}/{service_name}_pricing_{timestamp}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  ✅ Saved {service_name} data → {file_path}")
            return file_path

        # EC2
        print("\n" + "="*60)
        print("EXTRACTING EC2 DATA")
        print("="*60)
        ec2_data = self.get_ec2_pricing()
        summary['services']['ec2'] = {'count': len(ec2_data)}
        save_to_file('ec2', ec2_data)

        # RDS
        print("\n" + "="*60)
        print("EXTRACTING RDS DATA")
        print("="*60)
        rds_engines = ['MySQL', 'PostgreSQL', 'MariaDB', 'Oracle', 'SQL Server', 'Aurora MySQL', 'Aurora PostgreSQL']
        deployment_options = ['Single-AZ', 'Multi-AZ']
        rds_summary = {}
        for engine in rds_engines:
            rds_summary[engine] = {}
            for deployment in deployment_options:
                rds_data = self.get_rds_pricing(engine, deployment)
                rds_summary[engine][deployment] = len(rds_data)
                save_to_file(f"rds_{engine.replace(' ', '_')}_{deployment}", rds_data)
        summary['services']['rds'] = rds_summary

        # Lambda
        print("\n" + "="*60)
        print("EXTRACTING LAMBDA DATA")
        print("="*60)
        lambda_data = self.get_lambda_pricing()
        summary['services']['lambda'] = {'count': len(lambda_data)}
        save_to_file('lambda', lambda_data)

        # EKS
        print("\n" + "="*60)
        print("EXTRACTING EKS DATA")
        print("="*60)
        eks_data = self.get_eks_pricing()
        summary['services']['eks'] = {'count': len(eks_data)}
        save_to_file('eks', eks_data)

        # ECS
        print("\n" + "="*60)
        print("EXTRACTING ECS DATA")
        print("="*60)
        ecs_data = self.get_ecs_pricing()
        summary['services']['ecs'] = {'count': len(ecs_data)}
        save_to_file('ecs', ecs_data)

        # S3
        print("\n" + "="*60)
        print("EXTRACTING S3 DATA")
        print("="*60)
        s3_data = self.get_s3_pricing()
        summary['services']['s3'] = {'count': len(s3_data)}
        save_to_file('s3', s3_data)

        # Save summary
        summary_file = f"{output_dir}/aws_pricing_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n" + "="*60)
        print("ALL DATA EXTRACTION COMPLETE!")
        print("="*60)
        print(f"Summary saved → {summary_file}")
        return summary


def main():
    print("AWS Pricing Data Extractor")
    print("="*60)
    print("This script extracts ALL pricing data from AWS (EC2, RDS, Lambda, EKS, ECS, S3)")
    print("Each service will be saved into its own JSON file.")
    print("="*60 + "\n")

    extractor = AWSPricingExtractor(region='us-east-1')
    extractor.extract_all_services(output_dir='../data/AWS/raw')


if __name__ == "__main__":
    main()

