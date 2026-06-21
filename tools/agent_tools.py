#!/usr/bin/env python3
"""
Agent Action Tools for EZ Orchestrator

Real tools that agents can use to execute actions.
These are exposed via MCP protocol to Claude.

Tools:
- publish_to_discord: Send message to Discord
- publish_to_x: Post tweet to X
- commit_to_github: Push code to GitHub
- execute_swap: Execute DeFi swap
- execute_payout: Send token payments

All tools require approval before execution.

Usage:
    tools = AgentTools(governance, distributors)
    result = tools.publish_to_discord(review_id, message)
"""

from typing import Dict, Optional, List
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class AgentTools:
    """
    Real action tools for agents.

    All tools follow the pattern:
    1. Tool called with action details
    2. Tool gets approval review_id from governance
    3. Tool verifies action is approved
    4. Tool executes if approved
    5. Tool returns result with tracking
    """

    def __init__(self, governance, distributors: Dict):
        """
        Initialize tools

        Args:
            governance: GovernanceEngine instance
            distributors: Dict of channel distributors
                {
                    'discord': DiscordDistributor,
                    'x': XDistributor,
                }
        """
        self.governance = governance
        self.distributors = distributors
        self.execution_log = []

    def publish_to_discord(self,
                          review_id: str,
                          title: str,
                          content: str,
                          channel: str = "announcements") -> Dict:
        """
        Execute approved Discord publication

        Args:
            review_id: Governance review ID
            title: Message title
            content: Message content
            channel: Discord channel

        Returns:
            {
                'status': 'executed' or 'failed',
                'message_id': str,
                'review_id': str,
                'timestamp': str,
            }
        """

        logger.info(f"Tool: publish_to_discord (review: {review_id})")

        # Verify approval
        if not self._verify_approved(review_id):
            return {
                'status': 'rejected',
                'error': 'Action not approved',
                'review_id': review_id,
            }

        try:
            # Execute via distributor
            if 'discord' not in self.distributors:
                raise Exception("Discord distributor not configured")

            distributor = self.distributors['discord']
            result = distributor.send_message(title, content)

            # Log execution
            self._log_execution({
                'tool': 'publish_to_discord',
                'review_id': review_id,
                'result': result,
                'status': 'success',
            })

            return {
                'status': 'executed',
                'message_id': result.get('message_id'),
                'review_id': review_id,
                'timestamp': datetime.utcnow().isoformat(),
                'channel': channel,
            }

        except Exception as e:
            logger.error(f"Discord publish failed: {e}")
            self._log_execution({
                'tool': 'publish_to_discord',
                'review_id': review_id,
                'error': str(e),
                'status': 'failed',
            })
            return {
                'status': 'failed',
                'error': str(e),
                'review_id': review_id,
            }

    def publish_to_x(self,
                     review_id: str,
                     content: str,
                     hashtags: List[str] = None) -> Dict:
        """
        Execute approved X (Twitter) publication

        Args:
            review_id: Governance review ID
            content: Tweet content (max 280 chars)
            hashtags: List of hashtags

        Returns:
            {
                'status': 'executed' or 'failed',
                'tweet_id': str,
                'review_id': str,
                'timestamp': str,
            }
        """

        logger.info(f"Tool: publish_to_x (review: {review_id})")

        # Verify approval
        if not self._verify_approved(review_id):
            return {
                'status': 'rejected',
                'error': 'Action not approved',
                'review_id': review_id,
            }

        try:
            # Execute via distributor
            if 'x' not in self.distributors:
                raise Exception("X distributor not configured")

            distributor = self.distributors['x']
            result = distributor.post_tweet(content, hashtags or [])

            # Log execution
            self._log_execution({
                'tool': 'publish_to_x',
                'review_id': review_id,
                'result': result,
                'status': 'success',
            })

            return {
                'status': 'executed',
                'tweet_id': result.get('tweet_id'),
                'review_id': review_id,
                'timestamp': datetime.utcnow().isoformat(),
                'content': content[:100],
            }

        except Exception as e:
            logger.error(f"X publish failed: {e}")
            self._log_execution({
                'tool': 'publish_to_x',
                'review_id': review_id,
                'error': str(e),
                'status': 'failed',
            })
            return {
                'status': 'failed',
                'error': str(e),
                'review_id': review_id,
            }

    def commit_to_github(self,
                         review_id: str,
                         repo: str,
                         branch: str,
                         commit_message: str,
                         files: Dict[str, str]) -> Dict:
        """
        Execute approved GitHub commit

        Args:
            review_id: Governance review ID
            repo: Repository name
            branch: Branch to commit to
            commit_message: Commit message
            files: Dict of filename → content

        Returns:
            {
                'status': 'executed' or 'failed',
                'commit_hash': str,
                'review_id': str,
            }
        """

        logger.info(f"Tool: commit_to_github (review: {review_id})")

        # Verify approval
        if not self._verify_approved(review_id):
            return {
                'status': 'rejected',
                'error': 'Action not approved',
                'review_id': review_id,
            }

        try:
            # In production: Use PyGithub to commit
            # For now: Mock commit
            commit_hash = self._generate_hash(commit_message)

            logger.info(f"Committed to {repo}/{branch}: {commit_hash}")

            self._log_execution({
                'tool': 'commit_to_github',
                'review_id': review_id,
                'repo': repo,
                'branch': branch,
                'files': list(files.keys()),
                'status': 'success',
            })

            return {
                'status': 'executed',
                'commit_hash': commit_hash,
                'review_id': review_id,
                'timestamp': datetime.utcnow().isoformat(),
                'repo': repo,
                'branch': branch,
                'files_updated': len(files),
            }

        except Exception as e:
            logger.error(f"GitHub commit failed: {e}")
            self._log_execution({
                'tool': 'commit_to_github',
                'review_id': review_id,
                'error': str(e),
                'status': 'failed',
            })
            return {
                'status': 'failed',
                'error': str(e),
                'review_id': review_id,
            }

    def execute_swap(self,
                     review_id: str,
                     amount_in: float,
                     token_in: str,
                     token_out: str,
                     slippage_tolerance: int = 50) -> Dict:
        """
        Execute approved DeFi swap

        Args:
            review_id: Governance review ID
            amount_in: Amount to swap
            token_in: Input token
            token_out: Output token
            slippage_tolerance: Max slippage in bps

        Returns:
            {
                'status': 'executed' or 'failed',
                'tx_hash': str,
                'amount_out': float,
                'review_id': str,
            }
        """

        logger.info(f"Tool: execute_swap (review: {review_id})")

        # Verify approval (CRITICAL - requires high level approval)
        if not self._verify_approved(review_id, min_risk_level='high'):
            return {
                'status': 'rejected',
                'error': 'Action not approved (requires high-level approval)',
                'review_id': review_id,
            }

        try:
            # In production: Use x402 meta-router
            # For now: Mock execution
            amount_out = amount_in * 0.995  # Mock 0.5% slippage
            tx_hash = self._generate_hash(f"{amount_in}{token_in}{token_out}")

            logger.info(f"Swap executed: {amount_in} {token_in} → {amount_out} {token_out}")

            self._log_execution({
                'tool': 'execute_swap',
                'review_id': review_id,
                'amount_in': amount_in,
                'token_in': token_in,
                'token_out': token_out,
                'amount_out': amount_out,
                'status': 'success',
            })

            return {
                'status': 'executed',
                'tx_hash': tx_hash,
                'amount_out': amount_out,
                'slippage': 50,
                'review_id': review_id,
                'timestamp': datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Swap execution failed: {e}")
            self._log_execution({
                'tool': 'execute_swap',
                'review_id': review_id,
                'error': str(e),
                'status': 'failed',
            })
            return {
                'status': 'failed',
                'error': str(e),
                'review_id': review_id,
            }

    def execute_payout(self,
                       review_id: str,
                       recipients: List[Dict],
                       token: str = "EZ",
                       total_amount: float = 0) -> Dict:
        """
        Execute approved token payout

        Args:
            review_id: Governance review ID
            recipients: List of {wallet, amount}
            token: Token to pay (default EZ)
            total_amount: Total amount being paid

        Returns:
            {
                'status': 'executed' or 'failed',
                'payouts': int,
                'total_amount': float,
                'review_id': str,
            }
        """

        logger.info(f"Tool: execute_payout (review: {review_id})")

        # Verify approval (CRITICAL - requires executive approval)
        if not self._verify_approved(review_id, min_risk_level='critical'):
            return {
                'status': 'rejected',
                'error': 'Action not approved (requires executive approval)',
                'review_id': review_id,
            }

        try:
            # In production: Send tokens via blockchain
            # For now: Mock execution
            successful_payouts = len(recipients)

            logger.info(f"Payouts executed: {successful_payouts} recipients")

            self._log_execution({
                'tool': 'execute_payout',
                'review_id': review_id,
                'payouts': successful_payouts,
                'token': token,
                'total_amount': total_amount,
                'status': 'success',
            })

            return {
                'status': 'executed',
                'payouts': successful_payouts,
                'total_amount': total_amount,
                'token': token,
                'review_id': review_id,
                'timestamp': datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Payout execution failed: {e}")
            self._log_execution({
                'tool': 'execute_payout',
                'review_id': review_id,
                'error': str(e),
                'status': 'failed',
            })
            return {
                'status': 'failed',
                'error': str(e),
                'review_id': review_id,
            }

    def _verify_approved(self, review_id: str, min_risk_level: str = 'low') -> bool:
        """
        Verify action is approved before execution

        Args:
            review_id: Review ID
            min_risk_level: Minimum approval level needed

        Returns:
            True if approved, False otherwise
        """

        # In production: Query governance system
        # For testing: Always return True if review_id provided
        return bool(review_id)

    def _log_execution(self, entry: Dict):
        """Log tool execution"""
        entry['timestamp'] = datetime.utcnow().isoformat()
        self.execution_log.append(entry)

    def _generate_hash(self, content: str) -> str:
        """Generate hash for mock results"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_execution_log(self, limit: int = 20) -> List[Dict]:
        """Get recent executions"""
        return self.execution_log[-limit:]


def main():
    """Test agent tools"""
    print("\n" + "="*70)
    print("PHASE 10: AGENT TOOLS TEST")
    print("="*70 + "\n")

    # Mock governance and distributors
    class MockGovernance:
        pass

    class MockDistributor:
        def send_message(self, title, content):
            return {'message_id': f'msg_{datetime.utcnow().timestamp()}'}

        def post_tweet(self, content, hashtags):
            return {'tweet_id': f'tweet_{datetime.utcnow().timestamp()}'}

    governance = MockGovernance()
    distributors = {
        'discord': MockDistributor(),
        'x': MockDistributor(),
    }

    # Create tools
    tools = AgentTools(governance, distributors)

    print("Testing Agent Tools:\n")

    # Test 1: Discord publish
    print("1. publish_to_discord")
    result = tools.publish_to_discord(
        "review_001",
        "Breaking: New DeFi Protocol",
        "Introducing the next generation of liquidity routing..."
    )
    print(f"   Status: {result['status']}")
    print(f"   Message ID: {result.get('message_id')}\n")

    # Test 2: X publish
    print("2. publish_to_x")
    result = tools.publish_to_x(
        "review_002",
        "New DeFi protocol launches with institutional-grade features",
        hashtags=['DeFi', 'crypto']
    )
    print(f"   Status: {result['status']}")
    print(f"   Tweet ID: {result.get('tweet_id')}\n")

    # Test 3: GitHub commit
    print("3. commit_to_github")
    result = tools.commit_to_github(
        "review_003",
        "ez-orchestrator",
        "main",
        "Phase 10: Add agent tools",
        {'tools.py': 'code here', 'README.md': 'docs here'}
    )
    print(f"   Status: {result['status']}")
    print(f"   Commit: {result.get('commit_hash')}\n")

    # Test 4: Execute swap
    print("4. execute_swap")
    result = tools.execute_swap(
        "review_004",
        1000000,
        "USDC",
        "ETH"
    )
    print(f"   Status: {result['status']}")
    print(f"   Amount Out: {result.get('amount_out')}\n")

    # Test 5: Execute payout
    print("5. execute_payout")
    recipients = [
        {'wallet': '0x123...', 'amount': 1000},
        {'wallet': '0x456...', 'amount': 500},
    ]
    result = tools.execute_payout(
        "review_005",
        recipients,
        token="EZ",
        total_amount=1500
    )
    print(f"   Status: {result['status']}")
    print(f"   Payouts: {result.get('payouts')}\n")

    # Show execution log
    print("Execution Log:")
    log = tools.get_execution_log()
    for entry in log:
        print(f"  {entry['timestamp']}: {entry['tool']}")

    print("\n✓ Agent Tools Test Complete")


if __name__ == "__main__":
    main()
