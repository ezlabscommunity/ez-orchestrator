#!/usr/bin/env python3
"""
EZ Orchestrator Profile Loader

Loads YAML profiles from disk, validates against schemas,
and provides programmatic access to orchestrator configuration.

Usage:
    loader = ProfileLoader('./profiles', './schemas')
    ez_chain = loader.get_project('ez_chain')
    core_eng = loader.get_role('core_engineer')
    prestige = loader.get_vibe('prestige')
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import yaml


@dataclass
class Profile:
    """Base profile dataclass with common operations"""
    name: str
    profile_type: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.data, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


class SchemaValidator:
    """Validates profiles against schema definitions"""

    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        self.schemas = {}
        self._load_schemas()

    def _load_schemas(self):
        """Load all schema definitions"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema directory not found: {self.schema_path}")

        for schema_file in self.schema_path.glob("*.schema.yaml"):
            schema_type = schema_file.stem.replace(".schema", "")
            with open(schema_file, "r") as f:
                self.schemas[schema_type] = yaml.safe_load(f)

    def validate(self, profile_type: str, profile_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate profile against schema.
        Returns (is_valid, error_list)
        """
        schema = self.schemas.get(profile_type)
        if not schema:
            return False, [f"No schema found for type: {profile_type}"]

        errors = []

        # Check required fields
        required = schema.get("required_fields", [])
        for field in required:
            if field not in profile_data:
                errors.append(f"Missing required field: {field}")

        # Validate field constraints
        fields_schema = schema.get("fields", {})
        for field_name, field_def in fields_schema.items():
            if field_name not in profile_data:
                continue

            value = profile_data[field_name]
            field_errors = self._validate_field(field_name, value, field_def)
            errors.extend(field_errors)

        return len(errors) == 0, errors

    def _validate_field(self, field_name: str, value: Any, field_def: Dict[str, Any]) -> List[str]:
        """Validate individual field"""
        errors = []
        field_type = field_def.get("type")

        # Type validation
        if field_type == "string":
            if not isinstance(value, str):
                errors.append(f"{field_name}: expected string, got {type(value).__name__}")
            else:
                # Length constraints
                constraints = field_def.get("constraints", {})
                if "min_length" in constraints and len(value) < constraints["min_length"]:
                    errors.append(f"{field_name}: minimum length {constraints['min_length']}")
                if "max_length" in constraints and len(value) > constraints["max_length"]:
                    errors.append(f"{field_name}: maximum length {constraints['max_length']}")

        elif field_type == "enum":
            allowed = field_def.get("allowed_values", [])
            if value not in allowed:
                errors.append(f"{field_name}: '{value}' not in {allowed}")

        elif field_type == "array":
            if not isinstance(value, list):
                errors.append(f"{field_name}: expected array, got {type(value).__name__}")
            else:
                constraints = field_def.get("constraints", {})
                if "min_items" in constraints and len(value) < constraints["min_items"]:
                    errors.append(f"{field_name}: minimum {constraints['min_items']} items")
                if "max_items" in constraints and len(value) > constraints["max_items"]:
                    errors.append(f"{field_name}: maximum {constraints['max_items']} items")

        return errors


class ProfileLoader:
    """Main orchestrator profile loader"""

    def __init__(self, profiles_dir: str = "./profiles", schemas_dir: str = "./schemas"):
        self.profiles_path = Path(profiles_dir)
        self.schemas_path = Path(schemas_dir)
        self.validator = SchemaValidator(self.schemas_path)
        self.profiles: Dict[str, Dict[str, Profile]] = {
            "projects": {},
            "roles": {},
            "channels": {},
            "vibes": {},
        }
        self._load_all_profiles()

    def _load_all_profiles(self):
        """Load all profiles from disk"""
        for profile_type in self.profiles.keys():
            profile_dir = self.profiles_path / profile_type
            if not profile_dir.exists():
                continue

            for profile_file in profile_dir.glob("*.yaml"):
                profile_name = profile_file.stem
                try:
                    with open(profile_file, "r") as f:
                        profile_data = yaml.safe_load(f)

                    # Validate against schema if applicable
                    if profile_type in ["projects", "roles"]:
                        is_valid, errors = self.validator.validate(profile_type.rstrip("s"), profile_data)
                        if not is_valid:
                            print(f"⚠️  Validation errors in {profile_type}/{profile_name}: {errors}")

                    # Create profile object
                    profile = Profile(
                        name=profile_name,
                        profile_type=profile_type,
                        data=profile_data,
                    )
                    self.profiles[profile_type][profile_name] = profile

                except Exception as e:
                    print(f"❌ Error loading {profile_type}/{profile_name}: {e}")

    def get_project(self, project_name: str) -> Optional[Profile]:
        """Get a project profile by name"""
        return self.profiles["projects"].get(project_name)

    def get_role(self, role_name: str) -> Optional[Profile]:
        """Get a role profile by name"""
        return self.profiles["roles"].get(role_name)

    def get_channel(self, channel_name: str) -> Optional[Profile]:
        """Get a channel profile by name"""
        return self.profiles["channels"].get(channel_name)

    def get_vibe(self, vibe_name: str) -> Optional[Profile]:
        """Get a vibe profile by name"""
        return self.profiles["vibes"].get(vibe_name)

    def get_profile(self, profile_type: str, profile_name: str) -> Optional[Profile]:
        """Get a profile by type and name"""
        if profile_type in self.profiles:
            return self.profiles[profile_type].get(profile_name)
        return None

    def list_profiles(self, profile_type: str) -> List[str]:
        """List all profiles of a given type"""
        if profile_type in self.profiles:
            return sorted(self.profiles[profile_type].keys())
        return []

    def list_all(self) -> Dict[str, List[str]]:
        """List all profiles by type"""
        return {ptype: sorted(profiles.keys()) for ptype, profiles in self.profiles.items()}

    def export_to_json(self, output_dir: str = "./export"):
        """Export all profiles to JSON for external consumption"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        for profile_type, profiles in self.profiles.items():
            type_dir = output_path / profile_type
            type_dir.mkdir(exist_ok=True)

            for profile_name, profile in profiles.items():
                output_file = type_dir / f"{profile_name}.json"
                with open(output_file, "w") as f:
                    f.write(profile.to_json())

        print(f"✓ Exported {sum(len(p) for p in self.profiles.values())} profiles to {output_dir}/")

    def get_context(self, project_name: str, role_name: str) -> Dict[str, Any]:
        """
        Build orchestration context for a given project + role combination.
        Used by downstream orchestrator engine and MCP server.
        """
        project = self.get_project(project_name)
        role = self.get_role(role_name)

        if not project or not role:
            return {}

        # Get vibe profiles
        project_vibe = self.get_vibe(project.get("default_vibe"))
        role_vibes = [self.get_vibe(v) for v in role.get("vibe_affinity", [])]

        context = {
            "project": project.data,
            "role": role.data,
            "vibe": project_vibe.data if project_vibe else None,
            "secondary_vibes": [v.data for v in role_vibes if v],
            "channels": {
                ch: self.get_channel(ch).data
                for ch in project.get("channels", [])
                if self.get_channel(ch)
            },
        }

        return context


def main():
    """CLI interface for testing"""
    import sys

    # Initialize loader from current directory structure
    loader = ProfileLoader("./profiles", "./schemas")

    print("=== EZ Orchestrator Profile Loader ===\n")

    # List all profiles
    print("📦 Loaded Profiles:")
    for ptype, profiles in loader.list_all().items():
        if profiles:
            print(f"  {ptype}: {', '.join(profiles)}")

    # Example: Get EZ Chain + Core Engineer context
    print("\n🔍 Example Context (ez_chain + core_engineer):")
    context = loader.get_context("ez_chain", "core_engineer")
    if context:
        print(f"  Project: {context['project'].get('name')}")
        print(f"  Role: {context['role'].get('name')}")
        print(f"  Vibe: {context['vibe'].get('name') if context['vibe'] else 'None'}")
        print(f"  Authority Level: {context['role'].get('authority_level')}")
        print(f"  Channels: {', '.join(context['channels'].keys())}")

    # Export to JSON
    print("\n📤 Exporting to JSON...")
    loader.export_to_json("./export")


if __name__ == "__main__":
    main()
