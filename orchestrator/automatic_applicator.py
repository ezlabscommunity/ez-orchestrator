#!/usr/bin/env python3
"""
Automatic Applicator for EZ Orchestrator

Pre-applies orchestration context to prompts so Claude doesn't have to.

Builds enhanced system messages that embed:
- Vibe tone instructions
- Channel formatting rules
- Best practices
- Role expectations
- Example patterns

Usage:
    applicator = AutomaticApplicator()
    enhanced_prompt = applicator.build_enhanced_prompt(
        user_input, detected_context, loaded_profiles
    )
    # Pass enhanced_prompt to Claude
"""

from typing import Dict


class AutomaticApplicator:
    """
    Automatically applies orchestration context to prompts.

    Takes the loaded context from ProfileAutoLoader and builds an enhanced
    system message that embeds all the guidance Claude needs.
    """

    def __init__(self):
        """Initialize the applicator"""
        pass

    def build_enhanced_prompt(self,
                            user_input: str,
                            detected_context: Dict,
                            loaded_profiles: Dict) -> Dict:
        """
        Build an enhanced prompt with all context pre-applied.

        Args:
            user_input: User's original request
            detected_context: Output from ContextDetector
            loaded_profiles: Output from ProfileAutoLoader.load_for_generation()

        Returns:
            {
                'system_message': str,  # Enhanced system prompt
                'user_message': str,    # User input (unchanged)
                'context_applied': {
                    'vibe': str,
                    'channel': str,
                    'role': str,
                    'project': str,
                },
                'instructions_included': [str],
            }
        """

        orchestration = loaded_profiles['orchestration_context']

        # Extract profiles
        project_profile = orchestration['project']
        role_profile = orchestration['role']
        vibe_profile = orchestration['vibe']
        channel_name = detected_context.get('channel')
        channel_profile = orchestration['channels'].get(channel_name)

        # Build system message sections
        sections = []

        # 1. Identity and purpose
        sections.append(self._build_identity_section(project_profile, role_profile))

        # 2. Vibe/tone instructions
        if vibe_profile:
            sections.append(self._build_vibe_section(vibe_profile))

        # 3. Channel-specific instructions
        if channel_profile:
            sections.append(self._build_channel_section(channel_profile, channel_name))

        # 4. Role expectations
        if role_profile:
            sections.append(self._build_role_section(role_profile))

        # 5. Best practices
        if vibe_profile and channel_profile:
            sections.append(self._build_best_practices_section(vibe_profile, channel_profile))

        # 6. Examples
        if vibe_profile:
            sections.append(self._build_examples_section(vibe_profile))

        # 7. Critical rules
        sections.append(self._build_critical_rules_section(
            vibe_profile, channel_profile, role_profile
        ))

        # Combine sections
        system_message = "\n".join(filter(None, sections))

        # Build context summary
        context_applied = {
            'project': project_profile.get('name') if project_profile else None,
            'role': role_profile.get('name') if role_profile else None,
            'vibe': vibe_profile.get('name') if vibe_profile else None,
            'channel': channel_name,
        }

        instructions_included = [
            s.split('\n')[0] for s in sections if s and s.startswith('#')
        ]

        return {
            'system_message': system_message,
            'user_message': user_input,
            'context_applied': context_applied,
            'instructions_included': instructions_included,
        }

    def _build_identity_section(self, project: Dict, role: Dict) -> str:
        """Build identity and purpose section"""
        if not (project and role):
            return ""

        return f"""# Context & Purpose

You are working within the EZ Labs ecosystem.

**Project:** {project.get('name')} ({project.get('category')})
- Purpose: {project.get('description')}
- Audience: {project.get('audience')}

**Your Role:** {role.get('name')}
- Authority Level: {role.get('authority_level')}
- Purpose: {role.get('description')}

Your outputs are shaped by this context."""

    def _build_vibe_section(self, vibe: Dict) -> str:
        """Build vibe/tone section"""
        if not vibe:
            return ""

        characteristics = vibe.get('tone_characteristics', {})

        return f"""# Tone & Voice ({vibe.get('name')} Vibe)

Adopt this tone for all outputs:
- Formality Level: {characteristics.get('formality')}
- Professionalism: {characteristics.get('professionalism')}
- Accessibility: {characteristics.get('accessibility')}
- Energy: {characteristics.get('energy')}

**Language Guidelines:**
{self._format_list(vibe.get('language_guidelines', []))}"""

    def _build_channel_section(self, channel: Dict, channel_name: str) -> str:
        """Build channel-specific instructions"""
        if not channel:
            return ""

        constraints = channel.get('constraints', {})

        return f"""# Channel: {channel.get('name')}

**Constraints:**
- Format: {constraints.get('format')}
- Character Limit: {constraints.get('character_limit') or 'Unlimited'}
- Media: {constraints.get('media')}

**Formatting Rules:**
{self._format_dict(channel.get('formatting_rules', {}))}

**Best Practices:**
{self._format_list(channel.get('best_practices', []))}"""

    def _build_role_section(self, role: Dict) -> str:
        """Build role expectations section"""
        if not role:
            return ""

        return f"""# Role Expectations ({role.get('name')})

**Responsibilities:**
{self._format_list(role.get('responsibilities', []))}

**Interaction Rules:**
{self._format_list(role.get('interaction_rules', []))}

**Required Context:**
{self._format_list(role.get('required_context', []))}"""

    def _build_best_practices_section(self, vibe: Dict, channel: Dict) -> str:
        """Build combined best practices section"""
        do_list = vibe.get('do_list', [])
        dont_list = vibe.get('dont_list', [])

        return f"""# Best Practices

**Do:**
{self._format_list(do_list)}

**Don't:**
{self._format_list(dont_list)}"""

    def _build_examples_section(self, vibe: Dict) -> str:
        """Build examples section"""
        examples = vibe.get('example_opening', [])

        if not examples:
            return ""

        return f"""# Example Patterns

**Opening Approaches:**
{self._format_list(examples)}

Use these patterns as inspiration for your opening."""

    def _build_critical_rules_section(self, vibe: Dict, channel: Dict, role: Dict) -> str:
        """Build critical rules section"""
        rules = []

        # Vibe rules
        if vibe:
            dont_list = vibe.get('dont_list', [])
            for rule in dont_list:
                rules.append(f"AVOID: {rule}")

        # Channel rules
        if channel:
            constraints = channel.get('constraints', {})
            if constraints.get('character_limit'):
                rules.append(f"CONSTRAINT: Maximum {constraints['character_limit']} characters")

        # Role rules
        if role:
            authority = role.get('authority_level')
            if authority == 'strategic':
                rules.append("RULE: Include tradeoff analysis and verification criteria")

        if not rules:
            return ""

        return f"""# Critical Rules (Must Follow)

{chr(10).join(rules)}"""

    def _format_list(self, items: list) -> str:
        """Format list items for readability"""
        if not items:
            return "(none)"
        return "\n".join(f"- {item}" for item in items)

    def _format_dict(self, d: dict) -> str:
        """Format dictionary for readability"""
        if not d:
            return "(none)"
        return "\n".join(f"- {k}: {v}" for k, v in d.items())


def main():
    """Test the automatic applicator"""
    import sys
    sys.path.insert(0, '.')

    from orchestrator.loader import ProfileLoader
    from orchestrator.context_detector import ContextDetector
    from orchestrator.profile_auto_loader import ProfileAutoLoader

    # Initialize
    profile_loader = ProfileLoader('./profiles', './schemas')
    detector = ContextDetector(profile_loader)
    auto_loader = ProfileAutoLoader(profile_loader)
    applicator = AutomaticApplicator()

    # Test input
    user_input = "Write a GitHub PR for EZ Chain's consensus refactor that improves throughput by 40%"

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          Automatic Applicator Test Results                    ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    # Step 1: Detect
    print("Step 1: Detect Context")
    detected = detector.detect(user_input)
    print(f"Detected: {detected['project']} / {detected['role']} / {detected['channel']}\n")

    # Step 2: Load
    print("Step 2: Load Profiles")
    loaded = auto_loader.load_for_generation(user_input, detected)
    print(f"Loaded: ready_to_generate = {loaded['ready_to_generate']}\n")

    # Step 3: Apply
    print("Step 3: Build Enhanced Prompt")
    enhanced = applicator.build_enhanced_prompt(user_input, detected, loaded)

    print("Enhanced System Message:")
    print("─" * 64)
    print(enhanced['system_message'])
    print("─" * 64)

    print(f"\nContext Applied: {enhanced['context_applied']}")
    print(f"Instructions Included: {enhanced['instructions_included']}")

    print("\n✓ Automatic Applicator Test Complete")


if __name__ == "__main__":
    main()
