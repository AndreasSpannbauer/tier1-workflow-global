#!/usr/bin/env python3
"""
Contract Validation Template

PURPOSE: Validate that code implementation matches specification contracts

CUSTOMIZE THIS FILE for your project:
- Update CONTRACT_TYPES to match your contract format (OpenAPI, GraphQL, gRPC, etc.)
- Update file paths to match your project structure
- Update validation logic to match your contract validation needs

EXAMPLES:
- API endpoints match OpenAPI/Swagger spec
- Database models match schema definitions
- Frontend types match backend API contracts
- gRPC services match .proto files
- GraphQL resolvers match schema

This is a TEMPLATE - adapt it to your project's needs.
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Any
import re
import json

# ==============================================================================
# CUSTOMIZE THESE FOR YOUR PROJECT
# ==============================================================================

# Define contract file locations
CONTRACT_FILES = {
    "openapi": Path("api/openapi.yaml"),  # OpenAPI/Swagger spec
    "openapi_json": Path("api/openapi.json"),  # OpenAPI JSON format
    "graphql": Path("schema/schema.graphql"),  # GraphQL schema
    "proto": Path("proto/"),  # gRPC proto files directory
}

# Define source code locations
SOURCE_DIR = Path("src")
API_DIR = SOURCE_DIR / "api"
MODELS_DIR = SOURCE_DIR / "models"

# Contract validation settings
ENABLE_OPENAPI_VALIDATION = True
ENABLE_GRAPHQL_VALIDATION = False
ENABLE_PROTO_VALIDATION = False
ENABLE_MODEL_VALIDATION = False

# ==============================================================================
# VALIDATION LOGIC (customize as needed)
# ==============================================================================


def load_openapi_spec() -> Dict[str, Any] | None:
    """Load OpenAPI specification from YAML or JSON."""
    # Try YAML first
    yaml_path = CONTRACT_FILES.get("openapi")
    if yaml_path and yaml_path.exists():
        try:
            import yaml

            return yaml.safe_load(yaml_path.read_text())
        except ImportError:
            print("⚠️  PyYAML not installed - cannot parse OpenAPI YAML")
            print("   Install: pip install pyyaml")
        except Exception as e:
            print(f"⚠️  Failed to parse OpenAPI YAML: {e}")

    # Try JSON
    json_path = CONTRACT_FILES.get("openapi_json")
    if json_path and json_path.exists():
        try:
            return json.loads(json_path.read_text())
        except Exception as e:
            print(f"⚠️  Failed to parse OpenAPI JSON: {e}")

    return None


def extract_api_endpoints_from_code() -> Set[str]:
    """
    Extract API endpoints from source code.

    Customize this for your framework:
    - Flask: @app.route()
    - FastAPI: @app.get(), @app.post(), etc.
    - Django: urlpatterns
    - Express: app.get(), app.post(), etc.
    """
    endpoints = set()

    if not API_DIR.exists():
        return endpoints

    for file_path in API_DIR.rglob("*.py"):
        content = file_path.read_text()

        # Flask pattern: @app.route('/path')
        flask_routes = re.findall(r'@app\.route\(["\']([^"\']+)["\']', content)
        endpoints.update(flask_routes)

        # FastAPI pattern: @app.get('/path'), @app.post('/path'), etc.
        fastapi_routes = re.findall(
            r'@app\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']', content
        )
        endpoints.update(fastapi_routes)

    return endpoints


def validate_openapi_contracts() -> List[Dict[str, str]]:
    """Validate that API endpoints match OpenAPI spec."""
    violations = []

    spec = load_openapi_spec()
    if not spec:
        print("ℹ️  No OpenAPI spec found - skipping OpenAPI validation")
        return violations

    # Extract endpoints from spec
    spec_endpoints = set(spec.get("paths", {}).keys())

    # Extract endpoints from code
    code_endpoints = extract_api_endpoints_from_code()

    # Check for mismatches
    missing_in_code = spec_endpoints - code_endpoints
    missing_in_spec = code_endpoints - spec_endpoints

    if missing_in_code:
        violations.append(
            {
                "type": "openapi",
                "issue": "Endpoints defined in spec but not implemented in code",
                "endpoints": list(missing_in_code),
            }
        )

    if missing_in_spec:
        violations.append(
            {
                "type": "openapi",
                "issue": "Endpoints implemented in code but not defined in spec",
                "endpoints": list(missing_in_spec),
            }
        )

    return violations


def validate_graphql_contracts() -> List[Dict[str, str]]:
    """
    Validate GraphQL schema matches resolvers.

    Customize this for your GraphQL framework:
    - Apollo Server
    - Graphene (Python)
    - Ariadne
    - Strawberry
    """
    violations = []

    schema_path = CONTRACT_FILES.get("graphql")
    if not schema_path or not schema_path.exists():
        print("ℹ️  No GraphQL schema found - skipping GraphQL validation")
        return violations

    # TODO: Implement GraphQL schema validation
    # This is a placeholder - customize for your GraphQL setup

    # Example checks:
    # - All schema types have resolvers
    # - All resolvers match schema types
    # - Query/Mutation fields are implemented

    return violations


def validate_proto_contracts() -> List[Dict[str, str]]:
    """
    Validate gRPC proto definitions match service implementations.

    Customize this for your gRPC setup.
    """
    violations = []

    proto_dir = CONTRACT_FILES.get("proto")
    if not proto_dir or not proto_dir.exists():
        print("ℹ️  No proto directory found - skipping gRPC validation")
        return violations

    # TODO: Implement proto validation
    # This is a placeholder - customize for your gRPC setup

    # Example checks:
    # - All proto services have implementations
    # - All proto messages are used
    # - Service methods match proto definitions

    return violations


def validate_model_contracts() -> List[Dict[str, str]]:
    """
    Validate database models match schema definitions.

    Customize this for your ORM:
    - SQLAlchemy
    - Django ORM
    - Prisma
    - TypeORM
    """
    violations = []

    if not MODELS_DIR.exists():
        print("ℹ️  No models directory found - skipping model validation")
        return violations

    # TODO: Implement model validation
    # This is a placeholder - customize for your ORM

    # Example checks:
    # - Model fields match database schema
    # - Required fields are not nullable
    # - Relationships are defined correctly

    return violations


def print_violations(violations: List[Dict[str, Any]]) -> None:
    """Print violations in a readable format."""
    if not violations:
        return

    print("\n❌ Contract violations detected:\n")
    for i, v in enumerate(violations, 1):
        print(f"{i}. Type: {v['type']}")
        print(f"   Issue: {v['issue']}")
        if "endpoints" in v and v["endpoints"]:
            print(f"   Endpoints:")
            for endpoint in v["endpoints"][:5]:
                print(f"     - {endpoint}")
            if len(v["endpoints"]) > 5:
                print(f"     ... and {len(v['endpoints']) - 5} more")
        print()


def main() -> int:
    """Run contract validation."""
    print("🔍 Running contract validation...\n")

    all_violations = []

    # Run enabled validations
    if ENABLE_OPENAPI_VALIDATION:
        print("Checking OpenAPI contracts...")
        openapi_violations = validate_openapi_contracts()
        all_violations.extend(openapi_violations)

    if ENABLE_GRAPHQL_VALIDATION:
        print("Checking GraphQL contracts...")
        graphql_violations = validate_graphql_contracts()
        all_violations.extend(graphql_violations)

    if ENABLE_PROTO_VALIDATION:
        print("Checking gRPC proto contracts...")
        proto_violations = validate_proto_contracts()
        all_violations.extend(proto_violations)

    if ENABLE_MODEL_VALIDATION:
        print("Checking model contracts...")
        model_violations = validate_model_contracts()
        all_violations.extend(model_violations)

    # Print results
    if all_violations:
        print_violations(all_violations)
        print(f"Total violations: {len(all_violations)}")
        print(
            "\nℹ️  Fix these violations or update validation rules in validate_contracts.py"
        )
        return 1
    else:
        print("✅ Contract validation passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
