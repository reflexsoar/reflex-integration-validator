import os
import argparse
import glob
import json

from loguru import logger
from pydantic import ValidationError

from reflex_integration_validator.schema import validate_integration

def load_manifests(manifest_pattern, manifest_dir, recursive=False):
    """
    Loads the manifests from the manifest directory based on the glob pattern
    :param manifest_pattern: The glob pattern to match
    :param manifest_dir: The directory to load the manifests from
    :return: A list of manifests
    """
    manifests = []

    if recursive:
        manifest_pattern = f"**/{manifest_pattern}"

    for filename in glob.glob(os.path.join(manifest_dir, manifest_pattern), recursive=recursive):
        with open(filename) as f:
            manifest = json.load(f)
            manifests.append({filename: manifest})
   
    return manifests

# Define arguments to load a specific manifest file from the manifests folder
parser = argparse.ArgumentParser(description='Checks a manifest against the Integration schema')
parser.add_argument('--manifest', type=str, default='*.json', help='The manifest file to load')
parser.add_argument('--manifest-dir', type=str, default='manifests', help='The directory to load the manifest from')
parser.add_argument('--recursive', action='store_true', help='Recursively load manifests from the manifest directory')
def main():

    args = parser.parse_args()

    # args.manifest must end in .json
    if not args.manifest.endswith('.json'):
        logger.error(f"Manifest file {args.manifest} must end in .json")
        exit(1)

    # Load the manifests based on the glob pattern
    logger.info(f"Loading manifests from {args.manifest_dir} {'recursively' if args.recursive else ''}")
    manifests = load_manifests(args.manifest, args.manifest_dir, args.recursive)

    for manifest in manifests:
        for filename, manifest_json in manifest.items():
            logger.info(f"Validating {filename}")

            try:
                integration = validate_integration(manifest_json)
            except ValidationError as e:
                logger.error(f"Validation failed for {filename}")
                print(e)
                exit(1)
            
            logger.success(f"Validation passed for {filename}")
                
if __name__ == "__main__":
    main()