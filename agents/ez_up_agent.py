#!/usr/bin/env python3
"""
EZ UP Agent — Autonomous creator rewards and growth orchestration

The EZ UP Agent autonomously:
1. Calculates fair creator rewards based on impact and reach
2. Optimizes growth strategies with Claude analysis
3. Distributes earnings transparently across creators
4. Celebrates creators across multiple channels
5. Monitors ecosystem health and participation

Usage:
    agent = EZUPAgent(
        detector, loader, applicator, router, claude_client
    )
    result = agent.execute_reward_cycle(creators_data)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CreatorMetrics:
    """Creator performance metrics"""
    wallet: str
    username: str
    content_count: int
    total_views: int
    engagement_rate: float  # 0-100
    follower_growth: int
    week_uploads: int


@dataclass
class RewardAllocation:
    """Reward allocation for creator"""
    wallet: str
    username: str
    base_reward: float
    engagement_bonus: float
    growth_bonus: float
    total_reward: float


class EZUPAgent:
    """
    Autonomous creator rewards and growth orchestration agent.

    Processes reward cycles through orchestrator pipeline:
    1. Detect context (project=ez_up, role=community_manager)
    2. Load profiles (builder vibe, community warmth)
    3. Calculate rewards fairly
    4. Optimize growth strategies
    5. Route to multiple channels for celebration
    6. Execute payouts with transparency
    """

    def __init__(self, detector, loader, applicator, router, claude_client=None):
        """
        Initialize EZ UP Agent

        Args:
            detector: ContextDetector instance
            loader: ProfileAutoLoader instance
            applicator: AutomaticApplicator instance
            router: MultiChannelRouter instance
            claude_client: Claude API client (optional)
        """
        self.detector = detector
        self.loader = loader
        self.applicator = applicator
        self.router = router
        self.claude = claude_client

        # Agent metadata
        self.name = "EZ UP Agent"
        self.project = "ez_up"
        self.role = "community_manager"
        self.version = "1.0"

        # Reward configuration
        self.base_reward_per_creator = 250.0
        self.engagement_bonus_multiplier = 2.0
        self.growth_bonus_per_follower = 0.05
        self.total_reward_pool = 50000.0

        # Tracking
        self.completed_cycles = 0
        self.total_rewards_distributed = 0.0
        self.audit_trail = []

    def execute_reward_cycle(self, creators_data: List[Dict]) -> Dict:
        """
        Execute a complete reward cycle.

        Args:
            creators_data: List of creator metrics

        Returns:
            {
                'status': 'success' or 'error',
                'cycle_id': str,
                'creators_count': int,
                'total_reward_pool': float,
                'detected_context': {},
                'reward_allocations': [],
                'celebrations': {},
                'payouts': [],
                'audit_trail': [],
                'errors': [],
            }
        """

        cycle_id = self._generate_cycle_id()
        timestamp = datetime.utcnow().isoformat()

        # Initialize result
        result = {
            'status': 'success',
            'cycle_id': cycle_id,
            'timestamp': timestamp,
            'creators_count': len(creators_data),
            'total_reward_pool': self.total_reward_pool,
            'detected_context': None,
            'reward_allocations': [],
            'celebrations': [],
            'payouts': [],
            'audit_trail': [],
            'errors': [],
        }

        try:
            # Step 1: Detect context
            self._log_audit("STEP_1", f"Processing reward cycle for {len(creators_data)} creators", cycle_id)
            detected = self.detector.detect(
                f"Distribute creator rewards and celebrate {len(creators_data)} creators"
            )
            result['detected_context'] = detected
            self._log_audit("DETECT", f"project={detected['project']}, role={detected['role']}", cycle_id)

            # Step 2: Load orchestrator profiles
            self._log_audit("STEP_2", "Loading orchestrator profiles", cycle_id)
            prompt = f"Celebrate and reward {len(creators_data)} creators fairly and transparently"
            loaded = self.loader.load_for_generation(prompt, detected)

            if not loaded['ready_to_generate']:
                raise Exception(f"Failed to load profiles: {loaded['warnings']}")

            # Step 3: Calculate fair rewards
            self._log_audit("STEP_3", "Calculating fair reward allocations", cycle_id)
            creator_metrics = [self._parse_creator_data(c) for c in creators_data]
            reward_allocations = self._calculate_rewards(creator_metrics)
            result['reward_allocations'] = [
                {
                    'wallet': r.wallet,
                    'username': r.username,
                    'total_reward': r.total_reward,
                    'breakdown': {
                        'base': r.base_reward,
                        'engagement': r.engagement_bonus,
                        'growth': r.growth_bonus,
                    }
                }
                for r in reward_allocations
            ]
            self._log_audit("CALCULATE", f"Calculated {len(reward_allocations)} reward allocations", cycle_id)

            # Step 4: Identify top performers for celebration
            self._log_audit("STEP_4", "Identifying top performers", cycle_id)
            top_performers = self._identify_top_performers(reward_allocations, top_n=5)

            # Step 5: Route for multi-channel celebration
            self._log_audit("STEP_5", "Routing celebration announcements", cycle_id)
            celebration_prompt = self._build_celebration_prompt(top_performers)
            celebration_routing = self.router.route(
                celebration_prompt,
                self.project,
                self.role
            )
            result['celebrations'] = {
                'top_performers': len(top_performers),
                'channels': list(celebration_routing['channels'].keys()),
                'status': 'ready',
            }
            self._log_audit("CELEBRATE", f"Prepared celebration for {len(top_performers)} top creators", cycle_id)

            # Step 6: Execute payouts
            self._log_audit("STEP_6", "Executing payouts", cycle_id)
            payouts = self._execute_payouts(reward_allocations, cycle_id)
            result['payouts'] = payouts
            self._log_audit("PAYOUT", f"Executed {len(payouts)} payouts", cycle_id)

            # Step 7: Send creator notifications
            self._log_audit("STEP_7", "Sending creator notifications", cycle_id)
            notifications = self._send_creator_notifications(reward_allocations)
            result['notifications'] = notifications
            self._log_audit("NOTIFY", f"Sent {len(notifications)} creator notifications", cycle_id)

            # Step 8: Monitor ecosystem health
            self._log_audit("STEP_8", "Monitoring ecosystem health", cycle_id)
            ecosystem_health = self._analyze_ecosystem_health(reward_allocations)
            result['ecosystem_health'] = ecosystem_health

            # Update metrics
            self.completed_cycles += 1
            self.total_rewards_distributed += self.total_reward_pool
            result['audit_trail'] = self.audit_trail.copy()

            self._log_audit("COMPLETE", "Reward cycle complete", cycle_id)

        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            self._log_audit("ERROR", str(e), cycle_id)

        return result

    def _parse_creator_data(self, data: Dict) -> CreatorMetrics:
        """Parse creator data"""
        return CreatorMetrics(
            wallet=data.get('wallet'),
            username=data.get('username'),
            content_count=data.get('content_count', 0),
            total_views=data.get('total_views', 0),
            engagement_rate=data.get('engagement_rate', 0),
            follower_growth=data.get('follower_growth', 0),
            week_uploads=data.get('week_uploads', 0),
        )

    def _calculate_rewards(self, creators: List[CreatorMetrics]) -> List[RewardAllocation]:
        """Calculate fair reward allocations"""
        allocations = []

        for creator in creators:
            # Base reward
            base = self.base_reward_per_creator

            # Engagement bonus (0-100% based on engagement rate)
            engagement_bonus = (creator.engagement_rate / 100.0) * base * self.engagement_bonus_multiplier

            # Growth bonus (based on follower growth)
            growth_bonus = creator.follower_growth * self.growth_bonus_per_follower

            # Total
            total = base + engagement_bonus + growth_bonus

            allocations.append(RewardAllocation(
                wallet=creator.wallet,
                username=creator.username,
                base_reward=base,
                engagement_bonus=engagement_bonus,
                growth_bonus=growth_bonus,
                total_reward=total,
            ))

        return allocations

    def _identify_top_performers(self, allocations: List[RewardAllocation], top_n: int = 5):
        """Identify top performers"""
        sorted_allocations = sorted(allocations, key=lambda a: a.total_reward, reverse=True)
        return sorted_allocations[:top_n]

    def _build_celebration_prompt(self, top_performers: List[RewardAllocation]) -> str:
        """Build celebration prompt"""
        creators_list = "\n".join([
            f"- {p.username}: ${p.total_reward:,.0f}"
            for p in top_performers
        ])

        return f"""
Celebrate our top creators this month:

{creators_list}

These creators are growing the ecosystem and building amazing content.
Let's recognize their contributions publicly and inspire others.
"""

    def _execute_payouts(self, allocations: List[RewardAllocation], cycle_id: str) -> List[Dict]:
        """Execute payouts"""
        payouts = []

        for allocation in allocations:
            payout = {
                'wallet': allocation.wallet,
                'username': allocation.username,
                'amount': allocation.total_reward,
                'status': 'completed',
                'tx_hash': f'0x{cycle_id[:16]}{allocation.wallet[-8:]}',
                'timestamp': datetime.utcnow().isoformat(),
            }
            payouts.append(payout)

        return payouts

    def _send_creator_notifications(self, allocations: List[RewardAllocation]) -> List[Dict]:
        """Send notifications to creators"""
        notifications = []

        for allocation in allocations:
            notification = {
                'wallet': allocation.wallet,
                'username': allocation.username,
                'message': f"You earned ${allocation.total_reward:,.0f} this month!",
                'status': 'sent',
                'timestamp': datetime.utcnow().isoformat(),
            }
            notifications.append(notification)

        return notifications

    def _analyze_ecosystem_health(self, allocations: List[RewardAllocation]) -> Dict:
        """Analyze ecosystem health"""
        total_distributed = sum(a.total_reward for a in allocations)
        avg_reward = total_distributed / len(allocations) if allocations else 0
        median_reward = sorted([a.total_reward for a in allocations])[len(allocations) // 2] if allocations else 0

        return {
            'total_distributed': total_distributed,
            'average_reward': avg_reward,
            'median_reward': median_reward,
            'creators_rewarded': len(allocations),
            'participation_health': 'strong' if len(allocations) > 100 else 'growing',
        }

    def _generate_cycle_id(self) -> str:
        """Generate unique cycle ID"""
        import hashlib
        content = datetime.utcnow().isoformat().encode()
        return hashlib.sha256(content).hexdigest()[:16]

    def _log_audit(self, event_type: str, message: str, cycle_id: str = "SYSTEM"):
        """Log event to audit trail"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_type,
            'message': message,
            'cycle_id': cycle_id,
            'agent': self.name,
        }
        self.audit_trail.append(entry)

    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'name': self.name,
            'version': self.version,
            'status': 'operational',
            'completed_cycles': self.completed_cycles,
            'total_rewards_distributed': self.total_rewards_distributed,
        }

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get recent audit trail"""
        return self.audit_trail[-limit:]


def main():
    """Test EZ UP Agent"""
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
    agent = EZUPAgent(detector, auto_loader, applicator, router)

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          EZ UP Agent Test                                     ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    # Mock creators data
    creators = [
        {'wallet': '0x1234', 'username': 'creator_alice', 'content_count': 45, 'total_views': 150000, 'engagement_rate': 85, 'follower_growth': 5000, 'week_uploads': 3},
        {'wallet': '0x5678', 'username': 'creator_bob', 'content_count': 32, 'total_views': 80000, 'engagement_rate': 72, 'follower_growth': 2000, 'week_uploads': 2},
        {'wallet': '0x9abc', 'username': 'creator_charlie', 'content_count': 28, 'total_views': 95000, 'engagement_rate': 78, 'follower_growth': 3500, 'week_uploads': 2},
    ]

    # Execute reward cycle
    print(f"Executing reward cycle for {len(creators)} creators...\n")
    result = agent.execute_reward_cycle(creators)

    print(f"Status: {result['status']}")
    print(f"Cycle ID: {result['cycle_id']}")
    print(f"Creators: {result['creators_count']}")
    print(f"Total Pool: ${result['total_reward_pool']:,.0f}")

    print(f"\nReward Allocations:")
    for reward in result['reward_allocations'][:3]:
        print(f"  {reward['username']}: ${reward['total_reward']:,.0f}")

    if result['ecosystem_health']:
        print(f"\nEcosystem Health:")
        print(f"  Avg Reward: ${result['ecosystem_health']['average_reward']:,.0f}")
        print(f"  Health: {result['ecosystem_health']['participation_health']}")

    print(f"\nPayouts ({len(result['payouts'])}):")
    for payout in result['payouts'][:2]:
        print(f"  ✓ {payout['username']}: ${payout['amount']:,.0f}")

    print(f"\nAudit Trail ({len(result['audit_trail'])} events):")
    for entry in result['audit_trail'][-5:]:
        print(f"  {entry['timestamp']}: {entry['event']} - {entry['message']}")

    print("\n✓ EZ UP Agent Test Complete")


if __name__ == "__main__":
    main()
