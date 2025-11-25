import boto3
import json

client = boto3.client('pricing', region_name='us-east-1')

# Create a paginator for describe_services
paginator = client.get_paginator('describe_services')

# Iterate through all pages
all_services = []
for page in paginator.paginate():
    all_services.extend(page['Services'])


# Print all service codes
print(f"Total services: {len(all_services)}\n")

service_codes = [service['ServiceCode'] for service in all_services]
print("All service codes:")
print(service_codes)

# Save all services to a JSON file
with open('../data/AWS/raw/aws_services.json', 'w') as f:
    json.dump(all_services, f, indent=4)
