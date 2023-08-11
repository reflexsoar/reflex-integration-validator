import os
import argparse
import glob
import json

from loguru import logger
from pydantic import ValidationError

from reflex_integration_validator.manifest import validate_integration

def load_manifests(manifest_pattern, manifest_dir):
    """
    Loads the manifests from the manifest directory based on the glob pattern
    :param manifest_pattern: The glob pattern to match
    :param manifest_dir: The directory to load the manifests from
    :return: A list of manifests
    """
    manifests = []
    for filename in glob.glob(os.path.join(manifest_dir, manifest_pattern)):
        with open(filename) as f:
            manifests.append({filename: json.load(f)})
    return manifests

# Define arguments to load a specific manifest file from the manifests folder
parser = argparse.ArgumentParser(description='Checks a manifest against the Integration schema')
parser.add_argument('--manifest', type=str, default='*.json', help='The manifest file to load')
parser.add_argument('--manifest-dir', type=str, default='manifests', help='The directory to load the manifest from')
def main():

    args = parser.parse_args()

    # args.manifest must end in .json
    if not args.manifest.endswith('.json'):
        logger.error(f"Manifest file {args.manifest} must end in .json")
        exit(1)

    # Load the manifests based on the glob pattern
    logger.info(f"Loading manifests from {args.manifest_dir} with pattern {args.manifest}")
    manifests = load_manifests(args.manifest, args.manifest_dir)

    for manifest in manifests:
        for filename, manifest_json in manifest.items():
            logger.info(f"Validating {filename}")

            try:
                integration = validate_integration(manifest_json)
            except ValidationError as e:
                logger.error(f"Validation failed for {filename}")
                print(e)
                
if __name__ == "__main__":
    main()