#!/usr/bin/env python3
"""
Profile Auto-Loader for EZ Orchestrator

Automatically loads profiles based on detected context.

Usage:
    loader = ProfileLoader(...)
    auto_loader = ProfileAutoLoader(loader)
    context = auto_loader.load_for_context(detected_context)
"""

from typing import Dict, Optional


class ProfileAutoLoader:
    """
    Automatically loads orchestration profiles based on detected context.

    Takes the output of ContextDetector and loads the full orchestration
    context (project + role + vibe + channels) ready for application.
    """

    def __init__(self, profile_loader):
        """Initialize with the ProfileLoader"""
        self.loader = profile_loader

    def load_for_context(self, detected_context: Dict) -> Dict:
        """
        Load full orchestration context based on detected context.

        Args:
            detected_context: Output from ContextDetector.detect()
                {
                    'project': str,
                    'role': str,
                    'channel': str,
                    'confidence': float,
                    'all_channels': list,
                    ...
                }

        Returns:
            {
                'detected': detected_context,  # Original detection result
                'project': {...},               # Full project profile
                'role': {...},                  # Full role profile
                'vibe': {...},                  # Full vibe profile
                'channels': {                   # Channel profiles for project
                    'github': {...},
                    'discord': {...},
                    ...
                },
                'is_valid': bool,               # All detected items exist?
                'missing': [str],               # Any missing profiles?
                'load_errors': [str],           # Any load errors?
            }
        """

        project = detected_context.get('project')
        role = detected_context.get('role')
        channel = detected_context.get('channel')
        all_channels = detected_context.get('all_channels', [])

        # Load each profile
        result = {
            'detected': detected_context,
            'project': None,
            'role': None,
            'vibe': None,
            'channels': {},
            'is_valid': True,
            'missing': [],
            'load_errors': [],
        }

        # Load project
        if project:
            project_profile = self.loader.get_project(project)
            if project_profile:
                result['project'] = project_profile.data
            else:
                result['is_valid'] = False
                result['missing'].append(f"project:{project}")
                result['load_errors'].append(f"Project '{project}' not found")
        else:
            result['is_valid'] = False
            result['missing'].append("project:None")

        # Load role
        if role:
            role_profile = self.loader.get_role(role)
            if role_profile:
                result['role'] = role_profile.data
            else:
                result['is_valid'] = False
                result['missing'].append(f"role:{role}")
                result['load_errors'].append(f"Role '{role}' not found")
        else:
            result['is_valid'] = False
            result['missing'].append("role:None")

        # Load vibe (from project or role context)
        if result['project']:
            default_vibe = result['project'].get('default_vibe')
            if default_vibe:
                vibe_profile = self.loader.get_vibe(default_vibe)
                if vibe_profile:
                    result['vibe'] = vibe_profile.data
                else:
                    result['load_errors'].append(f"Vibe '{default_vibe}' not found")

        # Load channels (for all channels in project)
        if all_channels:
            for ch in all_channels:
                channel_profile = self.loader.get_channel(ch)
                if channel_profile:
                    result['channels'][ch] = channel_profile.data
                else:
                    result['load_errors'].append(f"Channel '{ch}' not found")

        # Additional channel if detected
        if channel and channel not in result['channels']:
            channel_profile = self.loader.get_channel(channel)
            if channel_profile:
                result['channels'][channel] = channel_profile.data

        return result

    def load_for_generation(self, user_input: str, detected_context: Dict) -> Dict:
        """
        Load full context for generation (convenience method).

        This is what Claude would call: loads everything needed to generate
        context-aware output.

        Args:
            user_input: The user's original request
            detected_context: Output from ContextDetector.detect()

        Returns:
            {
                'user_input': str,
                'detected_context': Dict,
                'orchestration_context': Dict,  # Full loaded context
                'ready_to_generate': bool,
                'warnings': [str],
            }
        """

        loaded_context = self.load_for_context(detected_context)

        warnings = []

        # Warn if confidence is low
        if detected_context.get('confidence', 0) < 0.7:
            warnings.append(f"Low confidence detection ({detected_context['confidence']})")

        # Warn if any profiles missing
        if loaded_context['load_errors']:
            warnings.extend(loaded_context['load_errors'])

        # Check if we have the essentials
        ready_to_generate = (
            loaded_context['project'] is not None and
            loaded_context['role'] is not None and
            loaded_context['vibe'] is not None
        )

        return {
            'user_input': user_input,
            'detected_context': detected_context,
            'orchestration_context': loaded_context,
            'ready_to_generate': ready_to_generate,
            'warnings': warnings,
        }


def main():
    """Test the profile auto-loader"""
    import sys
    sys.path.insert(0, '.')

    from orchestrator.loader import ProfileLoader
    from orchestrator.context_detector import ContextDetector

    # Initialize
    profile_loader = ProfileLoader('./profiles', './schemas')
    detector = ContextDetector(profile_loader)
    auto_loader = ProfileAutoLoader(profile_loader)

    # Test input
    user_input = "Write a GitHub PR for EZ Chain's consensus refactor"

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          Profile Auto-Loader Test Results                     ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    # Step 1: Detect context
    print("Step 1: Detect Context")
    print(f"Input: {user_input}\n")
    detected = detector.detect(user_input)
    print(f"Detected:")
    print(f"  Project: {detected['project']}")
    print(f"  Role: {detected['role']}")
    print(f"  Channel: {detected['channel']}")
    print(f"  Confidence: {detected['confidence']}\n")

    # Step 2: Load profiles
    print("Step 2: Load Profiles")
    loaded = auto_loader.load_for_generation(user_input, detected)

    print(f"Loaded:")
    print(f"  Project: {loaded['orchestration_context']['project'].get('name')}")
    print(f"  Role: {loaded['orchestration_context']['role'].get('name')}")
    print(f"  Vibe: {loaded['orchestration_context']['vibe'].get('name')}")
    print(f"  Channels: {list(loaded['orchestration_context']['channels'].keys())}")
    print(f"  Ready to Generate: {loaded['ready_to_generate']}")

    if loaded['warnings']:
        print(f"  Warnings: {loaded['warnings']}")

    print("\n✓ Auto-Loader Test Complete")


if __name__ == "__main__":
    main()
