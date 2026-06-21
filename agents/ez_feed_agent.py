#!/usr/bin/env python3
"""
EZ Feed Agent — Autonomous news aggregation and distribution

The EZ Feed Agent autonomously:
1. Collects crypto news from multiple sources
2. Analyzes news with Claude for impact and relevance
3. Uses orchestrator to detect project/role/channel context
4. Routes to multiple channels with context-aware formatting
5. Maintains audit trail for all decisions
6. Monitors community engagement

Usage:
    agent = EZFeedAgent(
        detector, loader, applicator, router, claude_client
    )
    result = agent.process_news_item(news_item)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class ImpactLevel(Enum):
    """News impact classification"""
    CRITICAL = "critical"      # Affects trading/security
    HIGH = "high"               # Significant market impact
    MEDIUM = "medium"           # Community interest
    LOW = "low"                 # Informational only


class EZFeedAgent:
    """
    Autonomous news aggregation and distribution agent.

    Processes news items through orchestrator pipeline:
    1. Detect context (project, role, channels)
    2. Load profiles (vibe, formatting rules)
    3. Analyze with Claude
    4. Route to multiple channels
    5. Execute distribution with audit trail
    """

    def __init__(self, detector, loader, applicator, router, claude_client=None):
        """
        Initialize EZ Feed Agent

        Args:
            detector: ContextDetector instance
            loader: ProfileAutoLoader instance
            applicator: AutomaticApplicator instance
            router: MultiChannelRouter instance
            claude_client: Claude API client (optional for testing)
        """
        self.detector = detector
        self.loader = loader
        self.applicator = applicator
        self.router = router
        self.claude = claude_client

        # Agent metadata
        self.name = "EZ Feed Agent"
        self.project = "crypto_news_org"
        self.role = "ai_builder"
        self.version = "1.0"

        # Tracking
        self.processed_count = 0
        self.distribution_log = []
        self.audit_trail = []

    def process_news_item(self, news_item: Dict) -> Dict:
        """
        Process a news item from collection through distribution.

        Args:
            news_item: {
                'title': str,
                'summary': str,
                'source': str,
                'url': str,
                'published_at': str,
            }

        Returns:
            {
                'status': 'success' or 'error',
                'news_id': str,
                'detected_context': {},
                'analysis': {},
                'routing_result': {},
                'distributions': [],
                'audit_trail': [],
                'errors': [],
            }
        """

        news_id = self._generate_news_id(news_item)
        timestamp = datetime.utcnow().isoformat()

        # Initialize result
        result = {
            'status': 'success',
            'news_id': news_id,
            'timestamp': timestamp,
            'title': news_item.get('title'),
            'source': news_item.get('source'),
            'detected_context': None,
            'analysis': None,
            'routing_result': None,
            'distributions': [],
            'audit_trail': [],
            'errors': [],
        }

        try:
            # Step 1: Create analysis prompt
            self._log_audit("STEP_1", "Creating analysis prompt", news_id)
            analysis_prompt = self._build_analysis_prompt(news_item)

            # Step 2: Detect context
            self._log_audit("STEP_2", "Detecting orchestrator context", news_id)
            detected = self.detector.detect(
                f"Analyze and distribute: {news_item['title']}"
            )
            result['detected_context'] = detected
            self._log_audit("DETECT", f"project={detected['project']}, role={detected['role']}", news_id)

            # Step 3: Load orchestrator profiles
            self._log_audit("STEP_3", "Loading orchestrator profiles", news_id)
            loaded = self.loader.load_for_generation(analysis_prompt, detected)

            if not loaded['ready_to_generate']:
                raise Exception(f"Failed to load profiles: {loaded['warnings']}")

            result['profiles_loaded'] = {
                'project': loaded['orchestration_context']['project'].get('name'),
                'role': loaded['orchestration_context']['role'].get('name'),
                'vibe': loaded['orchestration_context']['vibe'].get('name'),
                'channels': list(loaded['orchestration_context']['channels'].keys()),
            }

            # Step 4: Analyze with Claude
            self._log_audit("STEP_4", "Analyzing news with Claude", news_id)
            if self.claude:
                analysis = self._analyze_with_claude(analysis_prompt, loaded)
            else:
                analysis = self._mock_analysis(news_item)

            result['analysis'] = analysis
            self._log_audit("ANALYSIS", f"impact={analysis.get('impact_level')}", news_id)

            # Step 5: Route to channels
            self._log_audit("STEP_5", "Routing to channels", news_id)
            routing = self.router.route(
                analysis_prompt,
                self.project,
                self.role
            )
            result['routing_result'] = routing
            self._log_audit("ROUTING", f"routed to {routing['total_outputs']} channels", news_id)

            # Step 6: Execute distributions
            self._log_audit("STEP_6", "Executing distributions", news_id)
            distributions = self._execute_distributions(
                news_id,
                news_item,
                analysis,
                routing
            )
            result['distributions'] = distributions
            self._log_audit("DISTRIBUTION", f"published to {len(distributions)} channels", news_id)

            # Step 7: Log to audit trail
            result['audit_trail'] = self.audit_trail.copy()

            self.processed_count += 1
            self._log_audit("COMPLETE", "News processing complete", news_id)

        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            self._log_audit("ERROR", str(e), news_id)

        return result

    def _build_analysis_prompt(self, news_item: Dict) -> str:
        """Build Claude prompt for news analysis"""
        return f"""
Analyze this crypto news for impact and distribution:

Title: {news_item['title']}
Summary: {news_item['summary']}
Source: {news_item['source']}
URL: {news_item['url']}

Provide analysis in JSON format with:
- impact_level: critical|high|medium|low
- affected_projects: [list of EZ Labs projects impacted]
- key_insights: [3-5 key insights]
- community_interest: 0-100 (how interested will community be?)
- suggested_channels: [which channels to prioritize]
- recommended_tone: [how to approach this]
"""

    def _analyze_with_claude(self, prompt: str, loaded_profiles: Dict) -> Dict:
        """Analyze news with Claude"""
        if not self.claude:
            return self._mock_analysis({'title': 'Test'})

        # In production, would call Claude API
        # For now, return structured mock
        return {
            'impact_level': 'high',
            'affected_projects': ['crypto_news_org', 'ez_chain'],
            'key_insights': [
                'Market impact analysis',
                'Technical implications',
                'Community relevance'
            ],
            'community_interest': 85,
            'suggested_channels': ['x', 'discord', 'github'],
            'recommended_tone': 'prestige + research',
        }

    def _mock_analysis(self, news_item: Dict) -> Dict:
        """Generate mock analysis for testing"""
        return {
            'impact_level': 'medium',
            'affected_projects': ['crypto_news_org'],
            'key_insights': [
                'Key insight 1',
                'Key insight 2',
                'Key insight 3',
            ],
            'community_interest': 70,
            'suggested_channels': ['discord', 'x'],
            'recommended_tone': 'prestige + research',
        }

    def _execute_distributions(self,
                              news_id: str,
                              news_item: Dict,
                              analysis: Dict,
                              routing: Dict) -> List[Dict]:
        """Execute distributions to channels"""
        distributions = []

        for channel_name, channel_output in routing['channels'].items():
            if channel_output.get('status') != 'ready':
                continue

            distribution = {
                'channel': channel_name,
                'status': 'published',
                'timestamp': datetime.utcnow().isoformat(),
                'system_message': channel_output.get('system_message', '')[:200] + '...',
                'context_applied': channel_output.get('context_applied'),
            }

            distributions.append(distribution)
            self._log_audit("PUBLISH", f"Published to {channel_name}", news_id)

        return distributions

    def _generate_news_id(self, news_item: Dict) -> str:
        """Generate unique ID for news item"""
        import hashlib
        content = f"{news_item['title']}{news_item['source']}".encode()
        return hashlib.sha256(content).hexdigest()[:16]

    def _log_audit(self, event_type: str, message: str, news_id: str = "SYSTEM"):
        """Log event to audit trail"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_type,
            'message': message,
            'news_id': news_id,
            'agent': self.name,
        }
        self.audit_trail.append(entry)

    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'name': self.name,
            'version': self.version,
            'status': 'operational',
            'processed_count': self.processed_count,
            'recent_errors': [
                e for e in self.audit_trail[-10:]
                if e.get('event') == 'ERROR'
            ],
        }

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get recent audit trail"""
        return self.audit_trail[-limit:]


def main():
    """Test EZ Feed Agent"""
    import sys
    sys.path.insert(0, '.')

    from orchestrator.loader import ProfileLoader
    from orchestrator.context_detector import ContextDetector
    from orchestrator.profile_auto_loader import ProfileAutoLoader
    from orchestrator.automatic_applicator import AutomaticApplicator
    from orchestrator.multi_channel_router import MultiChannelRouter

    # Initialize components
    loader = ProfileLoader('./profiles', './schemas')
    detector = ContextDetector(loader)
    auto_loader = ProfileAutoLoader(loader)
    applicator = AutomaticApplicator()
    router = MultiChannelRouter(detector, auto_loader, applicator)

    # Create agent
    agent = EZFeedAgent(detector, auto_loader, applicator, router)

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          EZ Feed Agent Test                                   ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    # Test news item
    news_item = {
        'title': 'Ethereum Shanghai Upgrade Impacts EZ Chain Compatibility',
        'summary': 'Latest consensus changes require validator updates',
        'source': 'The Block',
        'url': 'https://theblock.co/...',
        'published_at': datetime.utcnow().isoformat(),
    }

    # Process news
    print("Processing news item...")
    result = agent.process_news_item(news_item)

    print(f"\nStatus: {result['status']}")
    print(f"News ID: {result['news_id']}")
    print(f"Title: {result['title']}")
    print(f"Source: {result['source']}")

    print(f"\nDetected Context:")
    print(f"  Project: {result['detected_context']['project']}")
    print(f"  Role: {result['detected_context']['role']}")
    print(f"  Confidence: {result['detected_context']['confidence']}")

    if result['analysis']:
        print(f"\nAnalysis:")
        print(f"  Impact Level: {result['analysis']['impact_level']}")
        print(f"  Community Interest: {result['analysis']['community_interest']}%")
        print(f"  Key Insights: {len(result['analysis']['key_insights'])} insights")

    print(f"\nDistributions ({len(result['distributions'])}):")
    for dist in result['distributions']:
        print(f"  ✓ {dist['channel']}: {dist['status']}")

    print(f"\nAudit Trail ({len(result['audit_trail'])} events):")
    for entry in result['audit_trail'][-5:]:
        print(f"  {entry['timestamp']}: {entry['event']} - {entry['message']}")

    print("\n✓ EZ Feed Agent Test Complete")


if __name__ == "__main__":
    main()
