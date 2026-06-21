#!/usr/bin/env python3
"""
Context Detector for EZ Orchestrator

Automatically detects project, role, and channel from user input.

Usage:
    detector = ContextDetector(loader)
    context = detector.detect("Write a GitHub PR for EZ Chain")
    # Returns: {project: "ez_chain", role: "core_engineer", channel: "github", ...}
"""

import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher


class ContextDetector:
    """
    Detects orchestration context (project, role, channel) from user input.

    Provides intelligent inference of:
    - Which EZ Labs project is referenced
    - Which role should handle the task
    - Which communication channel is targeted
    """

    def __init__(self, loader):
        """Initialize with ProfileLoader for accessing profile names"""
        self.loader = loader
        self.projects = loader.list_profiles('projects')
        self.roles = loader.list_profiles('roles')
        self.channels = loader.list_profiles('channels')
        self._build_detection_maps()

    def _build_detection_maps(self):
        """Build keyword maps for efficient detection"""
        # Project keywords (project name → keywords)
        self.project_keywords = {
            'ez_chain': ['ez chain', 'chain', 'consensus', 'validator', 'proof of human'],
            'zendex': ['zendex', 'trading', 'dex', 'privacy', 'institutional'],
            'ez_path': ['ez path', 'router', 'liquidity', 'venue', 'routing'],
            'ez_up': ['ez up', 'creator', 'rewards', 'growth', 'distribution'],
            'ezverse': ['ezverse', 'world', 'identity', 'metaverse', 'progression'],
            'ojet3d': ['ojet3d', '3d', 'asset', 'avatar', 'motion'],
            'ez_secure': ['ez secure', 'security', 'audit', 'vulnerability'],
            'crypto_news_org': ['crypto news', 'news', 'aggregator', 'publishing'],
            'tech_news_studio': ['tech news', 'news studio', 'ai news', 'production'],
        }

        # Channel keywords (channel name → keywords)
        self.channel_keywords = {
            'github': ['github', 'pr', 'pull request', 'issue', 'code review', 'commit'],
            'discord': ['discord', 'chat', 'community', 'thread', 'announcement'],
            'x': ['x', 'twitter', 'tweet', 'post', 'social media', '280'],
            'website': ['website', 'blog', 'post', 'web', 'page', 'landing'],
            'internal_docs': ['docs', 'document', 'internal', 'decision', 'rfc'],
            'telegram': ['telegram', 'alert', 'notification', 'quick'],
            'beehiv': ['newsletter', 'email', 'beehiiv', 'subscribe'],
            'youtube': ['youtube', 'video', 'tutorial', 'talk', 'presentation'],
            'tiktok': ['tiktok', 'short video', 'viral', 'trending'],
        }

        # Role inference patterns (keyword → role)
        self.role_patterns = {
            'core_engineer': [
                r'refactor', r'architecture', r'protocol', r'consensus',
                r'validation', r'technical', r'code', r'implementation',
                r'optimize', r'performance', r'throughput'
            ],
            'community_manager': [
                r'announce', r'community', r'engagement', r'discussion',
                r'welcome', r'support', r'help', r'ask'
            ],
            'founder': [
                r'launch', r'announce', r'strategy', r'vision',
                r'executive', r'decision', r'direction'
            ],
            'ai_builder': [
                r'agent', r'ai', r'model', r'training', r'ml',
                r'orchestrat', r'workflow', r'automation'
            ],
            'creative_technologist': [
                r'design', r'visual', r'3d', r'motion', r'ui', r'ux',
                r'brand', r'creative'
            ],
            'security_partner': [
                r'security', r'vulnerability', r'audit', r'exploit',
                r'threat', r'risk'
            ],
        }

    def detect(self, input_text: str) -> Dict:
        """
        Detect orchestration context from user input.

        Args:
            input_text: User's request or description

        Returns:
            {
                'project': str or None,
                'role': str or None,
                'channel': str or None,
                'confidence': float (0-1),
                'reasoning': str,
                'all_channels': list (channels for detected project)
            }
        """

        # Detect each component
        project, project_conf, project_reason = self._detect_project(input_text)
        role, role_conf, role_reason = self._detect_role(input_text, project)
        channel, channel_conf, channel_reason = self._detect_channel(input_text)

        # Get all channels for the project if detected
        all_channels = []
        if project:
            project_profile = self.loader.get_project(project)
            if project_profile:
                all_channels = project_profile.get('channels', [])

        # Calculate overall confidence
        confidences = [c for c in [project_conf, role_conf, channel_conf] if c is not None]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Build reasoning
        reasoning = f"{project_reason}; {role_reason}; {channel_reason}"

        return {
            'project': project,
            'role': role,
            'channel': channel,
            'confidence': round(overall_confidence, 2),
            'reasoning': reasoning,
            'project_confidence': project_conf,
            'role_confidence': role_conf,
            'channel_confidence': channel_conf,
            'all_channels': all_channels,
        }

    def _detect_project(self, text: str) -> Tuple[Optional[str], Optional[float], str]:
        """Detect project from text"""
        text_lower = text.lower()

        # Try exact keyword matches first
        for project, keywords in self.project_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return project, 0.95, f"Found project keyword: '{keyword}' → {project}"

        # Try fuzzy matching against project names
        best_match = None
        best_score = 0.7  # Minimum threshold

        for project in self.projects:
            score = self._fuzzy_match(project.replace('_', ' '), text_lower)
            if score > best_score:
                best_match = project
                best_score = score

        if best_match:
            return best_match, best_score, f"Fuzzy matched project: {best_match} (score: {best_score:.2f})"

        return None, 0.0, "No project detected"

    def _detect_role(self, text: str, project: Optional[str]) -> Tuple[Optional[str], Optional[float], str]:
        """Detect role from text and project context"""
        text_lower = text.lower()

        # Use project context to infer role
        if project:
            # Get typical roles for this project
            project_profile = self.loader.get_project(project)
            if project_profile:
                # Infer role based on project type
                category = project_profile.get('category', '')

                if category == 'infrastructure':
                    if any(word in text_lower for word in ['refactor', 'optimize', 'protocol', 'validation']):
                        return 'core_engineer', 0.9, "Project is infrastructure + task suggests core_engineer"

                elif category == 'trading':
                    if any(word in text_lower for word in ['institutional', 'feature']):
                        return 'founder', 0.85, "Trading project + leadership context → founder"

                elif category == 'creative':
                    if any(word in text_lower for word in ['design', 'visual', '3d', 'motion']):
                        return 'creative_technologist', 0.85, "Creative project + design keywords"
                    elif any(word in text_lower for word in ['announce', 'community']):
                        return 'community_manager', 0.80, "Creative project + community keywords"

                elif category == 'content':
                    if any(word in text_lower for word in ['ai', 'agent', 'orchestrat']):
                        return 'ai_builder', 0.85, "Content project + AI keywords"
                    elif any(word in text_lower for word in ['announce', 'write']):
                        return 'community_manager', 0.80, "Content project + community task"

        # Try pattern matching on role patterns
        best_role = None
        best_score = 0.0

        for role, patterns in self.role_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, text_lower)) / len(patterns)
            if score > best_score:
                best_role = role
                best_score = score

        if best_score > 0.5:
            return best_role, best_score, f"Pattern matched role: {best_role} (score: {best_score:.2f})"

        # Default to core_engineer if no match
        return 'core_engineer', 0.5, "Default to core_engineer (no strong match)"

    def _detect_channel(self, text: str) -> Tuple[Optional[str], Optional[float], str]:
        """Detect communication channel from text"""
        text_lower = text.lower()

        # Try keyword matches
        for channel, keywords in self.channel_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    confidence = 0.95 if len(keyword) > 3 else 0.85
                    return channel, confidence, f"Found channel keyword: '{keyword}' → {channel}"

        # Try fuzzy matching
        best_match = None
        best_score = 0.7

        for channel in self.channels:
            score = self._fuzzy_match(channel.replace('_', ' '), text_lower)
            if score > best_score:
                best_match = channel
                best_score = score

        if best_match:
            return best_match, best_score, f"Fuzzy matched channel: {best_match}"

        return None, 0.0, "No channel detected"

    def _fuzzy_match(self, target: str, text: str) -> float:
        """Calculate fuzzy match score (0-1)"""
        # Simple ratio-based matching
        words = text.split()
        for word in words:
            ratio = SequenceMatcher(None, target.lower(), word.lower()).ratio()
            if ratio > 0.7:
                return ratio

        # Check if target is substring
        if target.lower() in text:
            return 0.9

        return 0.0


def main():
    """Test the context detector"""
    import sys
    sys.path.insert(0, '.')

    from orchestrator.loader import ProfileLoader

    # Initialize detector
    loader = ProfileLoader('./profiles', './schemas')
    detector = ContextDetector(loader)

    # Test inputs
    test_inputs = [
        "Write a GitHub PR for EZ Chain's consensus refactor",
        "Announce creator rewards launch on Discord",
        "Tweet about ZENDEX institutional features",
        "Write a blog post about AI infrastructure",
        "Create a newsletter about tech trends",
    ]

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║            Context Detector Test Results                      ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    for user_input in test_inputs:
        context = detector.detect(user_input)

        print(f"Input: {user_input}")
        print(f"Detected:")
        print(f"  Project: {context['project']} (confidence: {context['project_confidence']})")
        print(f"  Role: {context['role']} (confidence: {context['role_confidence']})")
        print(f"  Channel: {context['channel']} (confidence: {context['channel_confidence']})")
        print(f"  Overall Confidence: {context['confidence']}")
        print(f"  Reasoning: {context['reasoning']}")
        if context['all_channels']:
            print(f"  Project Channels: {', '.join(context['all_channels'])}")
        print()


if __name__ == "__main__":
    main()
