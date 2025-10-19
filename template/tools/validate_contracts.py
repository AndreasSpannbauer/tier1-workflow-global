#!/usr/bin/env python3
"""
API Contract Validation Script

MIT License - Copy and customize for your project

USAGE:
    python validate_contracts.py [--contracts-dir DIR] [--json] [--verbose]

CUSTOMIZATION:
    1. Edit CONTRACT_RULES to match your API standards
    2. Implement custom validators in validate_* functions
    3. Update schema validation logic for your contract format
    4. Add project-specific naming conventions

EXAMPLE CONTRACT (contracts/users_api.yaml):
    version: "1.0"
    endpoint: /api/v1/users
    methods:
      GET:
        request:
          query_params:
            - name: page
              type: integer
              required: false
        response:
          status: 200
          schema:
            type: object
            properties:
              users:
                type: array
                items:
                  type: object
                  properties:
                    id: {type: string}
                    name: {type: string}
      POST:
        request:
          body:
            type: object
            required: [name, email]
            properties:
              name: {type: string}
              email: {type: string, format: email}
        response:
          status: 201
          schema:
            type: object
            properties:
              id: {type: string}
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Optional YAML support (graceful fallback)
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Optional colorized output (graceful fallback)
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = ""
    class Style:
        RESET_ALL = BRIGHT = ""
    HAS_COLOR = False


@dataclass
class Violation:
    """Contract violation"""
    severity: str  # 'error' or 'warning'
    rule: str
    message: str
    contract_file: Optional[Path] = None
    field: Optional[str] = None

    def __str__(self) -> str:
        prefix = f"{Fore.RED}ERROR" if self.severity == 'error' else f"{Fore.YELLOW}WARNING"
        location = f" in {self.contract_file}" if self.contract_file else ""
        field_info = f" (field: {self.field})" if self.field else ""
        return f"{prefix}{Style.RESET_ALL}: [{self.rule}] {self.message}{location}{field_info}"


@dataclass
class ValidationResult:
    """Validation result container"""
    violations: List[Violation] = field(default_factory=list)
    contracts_scanned: int = 0

    @property
    def errors(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == 'error']

    @property
    def warnings(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == 'warning']

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


# DEFAULT CONTRACT RULES - Customize for your project
CONTRACT_RULES = {
    "endpoint_patterns": {
        # Enforce REST naming conventions
        "must_start_with": "/api/",
        "version_pattern": r"^/api/v\d+/",
        "no_trailing_slash": True,
        "lowercase_only": True,
    },
    "required_fields": [
        # Fields that must be present in every contract
        "version",
        "endpoint",
        "methods",
    ],
    "http_methods": [
        # Allowed HTTP methods
        "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"
    ],
    "response_status_codes": {
        # Valid status codes per method
        "GET": [200, 404],
        "POST": [201, 400, 409],
        "PUT": [200, 404],
        "PATCH": [200, 404],
        "DELETE": [204, 404],
    },
    "schema_validation": {
        # JSON Schema requirements
        "require_type": True,
        "require_properties_for_objects": True,
        "forbid_additional_properties": False,
    },
    "backward_compatibility": {
        # Breaking change detection
        "check_removed_fields": True,
        "check_type_changes": True,
        "check_required_additions": True,
    },
}


class ContractValidator:
    """Main validation engine"""

    def __init__(
        self,
        contracts_dir: Path,
        rules: Dict[str, Any],
        baseline_dir: Optional[Path] = None,
        verbose: bool = False
    ):
        self.contracts_dir = contracts_dir.resolve()
        self.rules = rules
        self.baseline_dir = baseline_dir
        self.verbose = verbose
        self.result = ValidationResult()

    def log(self, message: str) -> None:
        """Verbose logging"""
        if self.verbose:
            print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")

    def validate(self) -> ValidationResult:
        """Run all validation checks"""
        self.log(f"Scanning contracts in {self.contracts_dir}")

        if not self.contracts_dir.exists():
            self.result.violations.append(Violation(
                severity='error',
                rule='missing_directory',
                message=f"Contracts directory does not exist: {self.contracts_dir}"
            ))
            return self.result

        # Find contract files
        contract_files = list(self.contracts_dir.glob("**/*.yaml")) + \
                        list(self.contracts_dir.glob("**/*.yml")) + \
                        list(self.contracts_dir.glob("**/*.json"))

        self.result.contracts_scanned = len(contract_files)

        if not contract_files:
            self.result.violations.append(Violation(
                severity='warning',
                rule='no_contracts',
                message=f"No contract files found in {self.contracts_dir}"
            ))
            return self.result

        # Validate each contract
        for contract_file in contract_files:
            self._validate_contract_file(contract_file)

        return self.result

    def _load_contract(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load contract from YAML or JSON file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            if file_path.suffix in ['.yaml', '.yml']:
                if not HAS_YAML:
                    self.result.violations.append(Violation(
                        severity='error',
                        rule='missing_dependency',
                        message="PyYAML not installed (pip install pyyaml)",
                        contract_file=file_path
                    ))
                    return None
                return yaml.safe_load(content)
            elif file_path.suffix == '.json':
                return json.loads(content)
            else:
                self.result.violations.append(Violation(
                    severity='error',
                    rule='invalid_format',
                    message=f"Unsupported file format: {file_path.suffix}",
                    contract_file=file_path
                ))
                return None

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            self.result.violations.append(Violation(
                severity='error',
                rule='parse_error',
                message=f"Failed to parse contract: {e}",
                contract_file=file_path
            ))
            return None

    def _validate_contract_file(self, file_path: Path) -> None:
        """Validate a single contract file"""
        self.log(f"Validating {file_path.name}")

        contract = self._load_contract(file_path)
        if not contract:
            return

        # Check required fields
        self._validate_required_fields(contract, file_path)

        # Validate endpoint naming
        if 'endpoint' in contract:
            self._validate_endpoint_naming(contract['endpoint'], file_path)

        # Validate HTTP methods
        if 'methods' in contract:
            self._validate_methods(contract['methods'], file_path)

        # Validate schemas
        if 'methods' in contract:
            for method, spec in contract['methods'].items():
                self._validate_method_spec(method, spec, file_path)

        # Check backward compatibility
        if self.baseline_dir:
            self._validate_backward_compatibility(contract, file_path)

    def _validate_required_fields(self, contract: Dict[str, Any], file_path: Path) -> None:
        """Check required fields are present"""
        required = self.rules.get("required_fields", [])

        for field in required:
            if field not in contract:
                self.result.violations.append(Violation(
                    severity='error',
                    rule='missing_required_field',
                    message=f"Missing required field: {field}",
                    contract_file=file_path,
                    field=field
                ))

    def _validate_endpoint_naming(self, endpoint: str, file_path: Path) -> None:
        """Validate endpoint follows naming conventions"""
        patterns = self.rules.get("endpoint_patterns", {})

        # Must start with prefix
        if prefix := patterns.get("must_start_with"):
            if not endpoint.startswith(prefix):
                self.result.violations.append(Violation(
                    severity='error',
                    rule='endpoint_naming',
                    message=f"Endpoint must start with '{prefix}': {endpoint}",
                    contract_file=file_path
                ))

        # Version pattern
        if version_pattern := patterns.get("version_pattern"):
            if not re.match(version_pattern, endpoint):
                self.result.violations.append(Violation(
                    severity='warning',
                    rule='endpoint_versioning',
                    message=f"Endpoint should match version pattern '{version_pattern}': {endpoint}",
                    contract_file=file_path
                ))

        # No trailing slash
        if patterns.get("no_trailing_slash") and endpoint.endswith('/'):
            self.result.violations.append(Violation(
                severity='warning',
                rule='endpoint_naming',
                message=f"Endpoint should not have trailing slash: {endpoint}",
                contract_file=file_path
            ))

        # Lowercase only
        if patterns.get("lowercase_only") and endpoint != endpoint.lower():
            self.result.violations.append(Violation(
                severity='warning',
                rule='endpoint_naming',
                message=f"Endpoint should be lowercase: {endpoint}",
                contract_file=file_path
            ))

    def _validate_methods(self, methods: Dict[str, Any], file_path: Path) -> None:
        """Validate HTTP methods"""
        allowed_methods = self.rules.get("http_methods", [])

        for method in methods:
            if method not in allowed_methods:
                self.result.violations.append(Violation(
                    severity='error',
                    rule='invalid_http_method',
                    message=f"Invalid HTTP method: {method}",
                    contract_file=file_path
                ))

    def _validate_method_spec(
        self,
        method: str,
        spec: Dict[str, Any],
        file_path: Path
    ) -> None:
        """Validate method specification"""
        # Check response status codes
        if 'response' in spec and 'status' in spec['response']:
            status = spec['response']['status']
            valid_statuses = self.rules.get("response_status_codes", {}).get(method, [])

            if valid_statuses and status not in valid_statuses:
                self.result.violations.append(Violation(
                    severity='warning',
                    rule='response_status',
                    message=f"Unusual status code for {method}: {status}",
                    contract_file=file_path
                ))

        # Validate request schema
        if 'request' in spec and 'body' in spec['request']:
            self._validate_schema(spec['request']['body'], f"{method}.request.body", file_path)

        # Validate response schema
        if 'response' in spec and 'schema' in spec['response']:
            self._validate_schema(spec['response']['schema'], f"{method}.response.schema", file_path)

    def _validate_schema(
        self,
        schema: Dict[str, Any],
        path: str,
        file_path: Path
    ) -> None:
        """Validate JSON Schema structure"""
        schema_rules = self.rules.get("schema_validation", {})

        # Require type field
        if schema_rules.get("require_type") and 'type' not in schema:
            self.result.violations.append(Violation(
                severity='error',
                rule='schema_validation',
                message=f"Schema missing 'type' field",
                contract_file=file_path,
                field=path
            ))

        # Require properties for objects
        if schema_rules.get("require_properties_for_objects"):
            if schema.get('type') == 'object' and 'properties' not in schema:
                self.result.violations.append(Violation(
                    severity='warning',
                    rule='schema_validation',
                    message=f"Object schema should define 'properties'",
                    contract_file=file_path,
                    field=path
                ))

        # Recursively validate nested schemas
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                if isinstance(prop_schema, dict):
                    self._validate_schema(prop_schema, f"{path}.{prop_name}", file_path)

        if 'items' in schema and isinstance(schema['items'], dict):
            self._validate_schema(schema['items'], f"{path}.items", file_path)

    def _validate_backward_compatibility(
        self,
        contract: Dict[str, Any],
        file_path: Path
    ) -> None:
        """Check for breaking changes against baseline"""
        if not self.baseline_dir:
            return

        baseline_file = self.baseline_dir / file_path.relative_to(self.contracts_dir)
        if not baseline_file.exists():
            self.log(f"No baseline contract found for {file_path.name} (new contract)")
            return

        baseline = self._load_contract(baseline_file)
        if not baseline:
            return

        compat_rules = self.rules.get("backward_compatibility", {})

        # Check removed fields
        if compat_rules.get("check_removed_fields"):
            self._check_removed_fields(baseline, contract, file_path)

        # Check type changes
        if compat_rules.get("check_type_changes"):
            self._check_type_changes(baseline, contract, file_path)

        # Check new required fields
        if compat_rules.get("check_required_additions"):
            self._check_required_additions(baseline, contract, file_path)

    def _check_removed_fields(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any],
        file_path: Path
    ) -> None:
        """Detect removed fields (breaking change)"""
        def get_fields(obj: Any, prefix: str = "") -> Set[str]:
            fields = set()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    field_path = f"{prefix}.{key}" if prefix else key
                    fields.add(field_path)
                    fields.update(get_fields(value, field_path))
            return fields

        baseline_fields = get_fields(baseline)
        current_fields = get_fields(current)
        removed = baseline_fields - current_fields

        for field in removed:
            self.result.violations.append(Violation(
                severity='error',
                rule='breaking_change',
                message=f"Removed field (breaking change): {field}",
                contract_file=file_path,
                field=field
            ))

    def _check_type_changes(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any],
        file_path: Path
    ) -> None:
        """Detect type changes (breaking change)"""
        def compare_types(base_obj: Any, curr_obj: Any, prefix: str = "") -> None:
            if isinstance(base_obj, dict) and isinstance(curr_obj, dict):
                for key in base_obj:
                    if key in curr_obj:
                        field_path = f"{prefix}.{key}" if prefix else key

                        # Check schema type changes
                        if key == 'type':
                            if base_obj[key] != curr_obj[key]:
                                self.result.violations.append(Violation(
                                    severity='error',
                                    rule='breaking_change',
                                    message=f"Type changed from {base_obj[key]} to {curr_obj[key]}",
                                    contract_file=file_path,
                                    field=prefix
                                ))
                        else:
                            compare_types(base_obj[key], curr_obj[key], field_path)

        compare_types(baseline, current)

    def _check_required_additions(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any],
        file_path: Path
    ) -> None:
        """Detect new required fields (breaking change)"""
        def compare_required(base_obj: Any, curr_obj: Any, prefix: str = "") -> None:
            if isinstance(base_obj, dict) and isinstance(curr_obj, dict):
                # Check 'required' arrays
                if 'required' in curr_obj:
                    baseline_required = set(base_obj.get('required', []))
                    current_required = set(curr_obj['required'])
                    new_required = current_required - baseline_required

                    for field in new_required:
                        self.result.violations.append(Violation(
                            severity='error',
                            rule='breaking_change',
                            message=f"New required field (breaking change): {field}",
                            contract_file=file_path,
                            field=prefix
                        ))

                # Recurse into nested objects
                for key in base_obj:
                    if key in curr_obj and isinstance(base_obj[key], dict):
                        field_path = f"{prefix}.{key}" if prefix else key
                        compare_required(base_obj[key], curr_obj[key], field_path)

        compare_required(baseline, current)


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate API contracts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=Path("contracts"),
        help="Directory containing contract files (default: ./contracts)"
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        help="Baseline contracts directory for backward compatibility check"
    )
    parser.add_argument(
        "--json",
        action='store_true',
        help="Output results as JSON"
    )
    parser.add_argument(
        "--verbose",
        action='store_true',
        help="Verbose output"
    )

    args = parser.parse_args()

    # Run validation
    validator = ContractValidator(
        args.contracts_dir,
        CONTRACT_RULES,
        baseline_dir=args.baseline_dir,
        verbose=args.verbose
    )
    result = validator.validate()

    # Output results
    if args.json:
        output = {
            "passed": result.passed,
            "contracts_scanned": result.contracts_scanned,
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "violations": [
                {
                    "severity": v.severity,
                    "rule": v.rule,
                    "message": v.message,
                    "contract": str(v.contract_file) if v.contract_file else None,
                    "field": v.field
                }
                for v in result.violations
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"\n{Fore.CYAN}Contract Validation{Style.RESET_ALL}")
        print(f"Contracts scanned: {result.contracts_scanned}")
        print(f"Errors: {Fore.RED if result.errors else Fore.GREEN}{len(result.errors)}{Style.RESET_ALL}")
        print(f"Warnings: {Fore.YELLOW if result.warnings else Fore.GREEN}{len(result.warnings)}{Style.RESET_ALL}")

        if result.violations:
            print(f"\n{Style.BRIGHT}Violations:{Style.RESET_ALL}")
            for violation in result.violations:
                print(f"  {violation}")

        if result.passed:
            print(f"\n{Fore.GREEN}✓ Contract validation passed{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ Contract validation failed{Style.RESET_ALL}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
