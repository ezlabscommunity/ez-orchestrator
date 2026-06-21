#!/usr/bin/env python3
"""
Multi-Channel Router for EZ Orchestrator

Routes single user input to multiple channels with automatic adaptation.

Usage:
    router = MultiChannelRouter(detector, auto_loader, applicator)
    outputs = router.route("Announce ZENDEX launch", "zendex", "founder")

    # Returns:
    # {
    #     'github': {...},
    #     'discord': {...},
    #     'x': {...},
    #     'website': {...},
    #     ...
    # }
"""

from typing import Dict, List, Optional
from orchestrator.context_detector import ContextDetector
from orchestrator.profile_auto_loader import ProfileAutoLoader
from orchestrator.automatic_applicator import AutomaticApplicator


class MultiChannelRouter:
    """
    Routes content to multiple channels with automatic adaptation.

    Takes a single user input and the target project, then automatically:
    1. Generates version for each channel the project uses
    2. Adapts format, tone, length per channel
    3. Returns all channel-specific outputs

    This enables: "Announce X" → automatically generates for GitHub, Discord, X, etc.
    """

    def __init__(self, detector, auto_loader, applicator):
        """Initialize with orchestration components"""
        self.detector = detector
        self.auto_loader = auto_loader
        self.applicator = applicator
        self.loader = detector.loader

    def route(self, user_input: str, project: str, role: Optional[str] = None) -> Dict:
        """
        Route user input to all channels for a project.

        Args:
            user_input: The user's request (e.g., "Announce mainnet launch")
            project: Target project (e.g., "ez_chain")
            role: Optional role override. If not provided, infers from input.

        Returns:
            {
                'user_input': str,
                'project': str,
                'role': str,
                'routing_summary': str,
                'channels': {
                    'github': {...},
                    'discord': {...},
                    'x': {...},
                    ...
                },
                'total_outputs': int,
            }
        """

        # Get project profile to find all channels
        project_profile = self.loader.get_project(project)
        if not project_profile:
            return {
                'error': f"Project '{project}' not found",
                'user_input': user_input,
                'channels': {},
            }

        project_channels = project_profile.get('channels', [])

        # Infer role if not provided
        if not role:
            detected = self.detector.detect(user_input)
            role = detected.get('role') or 'community_manager'

        # Generate for each channel
        channel_outputs = {}

        for channel in project_channels:
            # Create channel-specific context
            channel_context = {
                'project': project,
                'role': role,
                'channel': channel,
                'confidence': 1.0,  # We know project and role explicitly
                'all_channels': project_channels,
            }

            # Load profiles
            loaded = self.auto_loader.load_for_generation(user_input, channel_context)

            if not loaded['ready_to_generate']:
                channel_outputs[channel] = {
                    'status': 'error',
                    'message': f"Failed to load profiles for {channel}",
                }
                continue

            # Build enhanced prompt for this channel
            enhanced = self.applicator.build_enhanced_prompt(
                user_input,
                channel_context,
                loaded
            )

            # Generate channel-specific output
            output = {
                'status': 'ready',
                'channel': channel,
                'system_message': enhanced['system_message'],
                'user_message': enhanced['user_message'],
                'context_applied': enhanced['context_applied'],
                'instructions': enhanced['instructions_included'],
                'channel_profile': self.loader.get_channel(channel).data if self.loader.get_channel(channel) else None,
            }

            channel_outputs[channel] = output

        # Build routing summary
        successful = sum(1 for o in channel_outputs.values() if o.get('status') == 'ready')
        total = len(channel_outputs)

        routing_summary = f"Routed to {successful}/{total} channels for project {project}"

        return {
            'user_input': user_input,
            'project': project,
            'role': role,
            'routing_summary': routing_summary,
            'channels': channel_outputs,
            'total_outputs': successful,
            'total_channels': total,
        }

    def route_to_specific_channels(self,
                                   user_input: str,
                                   project: str,
                                   channels: List[str],
                                   role: Optional[str] = None) -> Dict:
        """
        Route user input to specific channels (subset).

        Args:
            user_input: The user's request
            project: Target project
            channels: Specific channels to route to
            role: Optional role override

        Returns:
            Same as route(), but only for specified channels
        """

        # Get full routing
        full_routing = self.route(user_input, project, role)

        # Filter to requested channels
        filtered_outputs = {
            ch: full_routing['channels'][ch]
            for ch in channels
            if ch in full_routing['channels']
        }

        return {
            'user_input': user_input,
            'project': project,
            'role': role,
            'routing_summary': f"Routed to {len(filtered_outputs)} selected channels",
            'channels': filtered_outputs,
            'total_outputs': len(filtered_outputs),
            'total_channels': len(filtered_outputs),
        }

    def get_channel_instruction(self, channel: str, routing_result: Dict) -> str:
        """
        Get generation instruction for a specific channel.

        Can be used to guide Claude in generating for a specific channel.

        Args:
            channel: Channel name
            routing_result: Result from route()

        Returns:
            String with complete system message for that channel
        """

        if channel not in routing_result['channels']:
            return f"Channel '{channel}' not found in routing"

        channel_output = routing_result['channels'][channel]

        if channel_output.get('status') != 'ready':
            return f"Channel '{channel}' not ready: {channel_output.get('message')}"

        return channel_output['system_message']

    def summarize_routing(self, routing_result: Dict) -> str:
        """
        Get a human-readable summary of the routing.

        Args:
            routing_result: Result from route()

        Returns:
            Formatted summary string
        """

        summary = f"""
Multi-Channel Routing Summary
────────────────────────────────────────

User Input: {routing_result['user_input']}
Project: {routing_result['project']}
Role: {routing_result['role']}

Routing Status: {routing_result['routing_summary']}

Channels Generated:
"""

        for channel, output in routing_result['channels'].items():
            status = "✓" if output.get('status') == 'ready' else "✗"
            summary += f"\n  {status} {channel}"
            if output.get('status') == 'ready':
                instructions = output.get('instructions', [])
                for instruction in instructions[:2]:  # Show first 2 instructions
                    summary += f"\n      - {instruction}"

        return summary


def main():
    """Test the multi-channel router"""
    import sys
    sys.path.insert(0, '.')

    from orchestrator.loader import ProfileLoader

    # Initialize
    loader = ProfileLoader('./profiles', './schemas')
    detector = ContextDetector(loader)
    auto_loader = ProfileAutoLoader(loader)
    applicator = AutomaticApplicator()
    router = MultiChannelRouter(detector, auto_loader, applicator)

    # Test input
    user_input = "Announce mainnet launch"

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          Multi-Channel Router Test Results                    ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    # Route to all channels for ez_chain
    print("Routing: Announce mainnet launch for EZ Chain\n")
    result = router.route(user_input, "ez_chain", "founder")

    # Print summary
    print(router.summarize_routing(result))

    # Show sample channel outputs
    print("\n" + "─" * 64)
    print("\nSample Channel Instructions (GitHub):\n")
    if 'github' in result['channels'] and result['channels']['github'].get('status') == 'ready':
        github_instruction = router.get_channel_instruction('github', result)
        print(github_instruction[:500] + "...\n[truncated]")

    print("✓ Multi-Channel Router Test Complete")


if __name__ == "__main__":
    main()
