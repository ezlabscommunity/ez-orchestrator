#!/usr/bin/env python3
"""
Governance Engine for EZ Orchestrator

The safety and approval layer that prevents runaway agents.

Features:
- Approval gates (human review required)
- Safety checks (tone, compliance, appropriateness)
- Role-based permissions (RBAC)
- Channel restrictions (limit where agents post)
- Audit logging (complete tracking)
- Review queues (pending actions)
- Escalation paths (what to do if rejected)

This is the institutional control layer.

Usage:
    governance = GovernanceEngine(config)
    review = governance.submit_for_review(action, metadata)
    result = governance.approve(review_id, approver)
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions requiring governance"""
    POST_DISCORD = "post_discord"
    POST_X = "post_x"
    EXECUTE_SWAP = "execute_swap"
    EXECUTE_PAYOUT = "execute_payout"
    MODIFY_PROFILE = "modify_profile"


class ApprovalStatus(Enum):
    """Status of an approval"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class RiskLevel(Enum):
    """Risk assessment of action"""
    LOW = "low"              # Auto-approve possible
    MEDIUM = "medium"        # Requires single approver
    HIGH = "high"            # Requires multiple approvers
    CRITICAL = "critical"    # Requires executive approval


class Role(Enum):
    """Governance roles"""
    OPERATOR = "operator"        # Can submit actions
    REVIEWER = "reviewer"        # Can approve low/medium
    MANAGER = "manager"          # Can approve high
    EXECUTIVE = "executive"      # Can approve critical
    ADMIN = "admin"              # Can do anything


class SafetyChecker:
    """Performs safety checks on proposed actions"""

    def __init__(self):
        self.tone_rules = {
            'discord': ['professional', 'engaging', 'on-brand'],
            'x': ['concise', 'engaging', 'professional'],
        }

        self.forbidden_phrases = [
            'buy now', 'guaranteed', 'financial advice',
            'moon', 'lambo', 'pump',
        ]

        self.max_frequency = {
            'discord': {'per_hour': 3, 'per_day': 20},
            'x': {'per_hour': 5, 'per_day': 30},
        }

    def check_safety(self, action: Dict) -> Dict:
        """
        Perform comprehensive safety check

        Args:
            action: {
                'type': ActionType,
                'channel': str,
                'content': str,
                'agent': str,
                'timestamp': str,
            }

        Returns:
            {
                'safe': bool,
                'risk_level': RiskLevel,
                'checks': {
                    'tone': bool,
                    'compliance': bool,
                    'frequency': bool,
                    'content_policy': bool,
                },
                'issues': [str],
            }
        """

        issues = []
        checks = {}

        # Check 1: Tone
        checks['tone'] = self._check_tone(action)
        if not checks['tone']:
            issues.append("Tone check failed")

        # Check 2: Forbidden phrases
        checks['compliance'] = self._check_forbidden_phrases(action)
        if not checks['compliance']:
            issues.append("Contains forbidden phrases")

        # Check 3: Content policy
        checks['content_policy'] = self._check_content_policy(action)
        if not checks['content_policy']:
            issues.append("Violates content policy")

        # Check 4: Frequency (mock - would track in real system)
        checks['frequency'] = self._check_frequency(action)
        if not checks['frequency']:
            issues.append("Exceeds posting frequency limits")

        # Determine risk level
        issue_count = len(issues)
        if issue_count == 0:
            risk_level = RiskLevel.LOW
        elif issue_count == 1:
            risk_level = RiskLevel.MEDIUM
        elif issue_count <= 3:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        return {
            'safe': len(issues) == 0,
            'risk_level': risk_level.value,
            'checks': checks,
            'issues': issues,
        }

    def _check_tone(self, action: Dict) -> bool:
        """Check tone appropriateness"""
        # In production: Use AI to check tone
        # For now: Simple heuristic
        content = action.get('content', '').lower()
        return not any(word in content for word in ['!!', '???', 'URGENT'])

    def _check_forbidden_phrases(self, action: Dict) -> bool:
        """Check for forbidden phrases"""
        content = action.get('content', '').lower()
        return not any(phrase in content for phrase in self.forbidden_phrases)

    def _check_content_policy(self, action: Dict) -> bool:
        """Check content policy compliance"""
        # In production: Check against policy database
        # For now: Basic checks
        content = action.get('content', '')
        return len(content) > 10 and len(content) < 5000

    def _check_frequency(self, action: Dict) -> bool:
        """Check posting frequency limits"""
        # In production: Query database for recent posts
        # For now: Always pass
        return True


class ApprovalQueue:
    """Manages pending approvals"""

    def __init__(self):
        self.pending = {}  # review_id → approval record
        self.history = []  # All approvals (approved/rejected)

    def submit_for_review(self,
                         action: Dict,
                         risk_level: str,
                         submitter: str) -> Dict:
        """
        Submit action for review

        Args:
            action: Action details
            risk_level: low|medium|high|critical
            submitter: Who submitted

        Returns:
            {
                'review_id': str,
                'status': 'pending',
                'required_approvals': int,
                'submitted_at': str,
            }
        """

        review_id = self._generate_review_id()

        # Determine required approvers
        required_count = {
            'low': 0,      # Auto-approve
            'medium': 1,   # 1 reviewer
            'high': 2,     # 2 reviewers
            'critical': 3, # 3+ executives
        }.get(risk_level, 1)

        record = {
            'review_id': review_id,
            'action': action,
            'risk_level': risk_level,
            'submitter': submitter,
            'status': ApprovalStatus.PENDING.value if required_count > 0 else ApprovalStatus.APPROVED.value,
            'required_approvals': required_count,
            'approvals': [],
            'rejections': [],
            'submitted_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        }

        if required_count == 0:
            # Auto-approve low risk
            record['status'] = ApprovalStatus.APPROVED.value
            record['approved_at'] = datetime.utcnow().isoformat()
            record['approved_by'] = 'system'
            logger.info(f"Auto-approved low-risk action: {review_id}")

        self.pending[review_id] = record
        logger.info(f"Submitted for review: {review_id} (risk: {risk_level})")

        return {
            'review_id': review_id,
            'status': record['status'],
            'required_approvals': required_count,
            'submitted_at': record['submitted_at'],
        }

    def approve(self, review_id: str, approver: str, role: Role) -> Dict:
        """
        Approve a pending action

        Args:
            review_id: ID of review
            approver: Who is approving
            role: Role of approver (must have permission)

        Returns:
            {'status': 'approved' or 'error', 'message': str}
        """

        if review_id not in self.pending:
            return {'status': 'error', 'message': 'Review not found'}

        record = self.pending[review_id]

        # Check if already decided
        if record['status'] != ApprovalStatus.PENDING.value:
            return {
                'status': 'error',
                'message': f"Already {record['status']}"
            }

        # Check role permission
        if not self._can_approve(role, record['risk_level']):
            return {
                'status': 'error',
                'message': f"{role.value} cannot approve {record['risk_level']} risk actions"
            }

        # Add approval
        record['approvals'].append({
            'approver': approver,
            'role': role.value,
            'approved_at': datetime.utcnow().isoformat(),
        })

        # Check if enough approvals
        if len(record['approvals']) >= record['required_approvals']:
            record['status'] = ApprovalStatus.APPROVED.value
            record['approved_at'] = datetime.utcnow().isoformat()
            logger.info(f"Approved: {review_id}")
            return {'status': 'approved', 'message': 'Action approved'}

        return {
            'status': 'pending',
            'message': f"Approval recorded ({len(record['approvals'])}/{record['required_approvals']})"
        }

    def reject(self, review_id: str, rejecter: str, reason: str) -> Dict:
        """
        Reject a pending action

        Args:
            review_id: ID of review
            rejecter: Who is rejecting
            reason: Why rejected

        Returns:
            {'status': 'rejected', 'message': str}
        """

        if review_id not in self.pending:
            return {'status': 'error', 'message': 'Review not found'}

        record = self.pending[review_id]
        record['status'] = ApprovalStatus.REJECTED.value
        record['rejected_at'] = datetime.utcnow().isoformat()
        record['rejected_by'] = rejecter
        record['rejection_reason'] = reason

        logger.warning(f"Rejected: {review_id} - {reason}")

        return {
            'status': 'rejected',
            'message': f'Action rejected: {reason}'
        }

    def get_pending(self, role: Role) -> List[Dict]:
        """Get pending reviews for a role"""
        relevant = []

        for review_id, record in self.pending.items():
            if record['status'] != ApprovalStatus.PENDING.value:
                continue

            if self._can_approve(role, record['risk_level']):
                relevant.append({
                    'review_id': review_id,
                    'action': record['action'],
                    'risk_level': record['risk_level'],
                    'submitted_at': record['submitted_at'],
                    'approvals_so_far': len(record['approvals']),
                    'required_approvals': record['required_approvals'],
                })

        return relevant

    def _can_approve(self, role: Role, risk_level: str) -> bool:
        """Check if role can approve risk level"""
        permissions = {
            Role.REVIEWER: ['low', 'medium'],
            Role.MANAGER: ['low', 'medium', 'high'],
            Role.EXECUTIVE: ['low', 'medium', 'high', 'critical'],
            Role.ADMIN: ['low', 'medium', 'high', 'critical'],
        }

        return risk_level in permissions.get(role, [])

    def _generate_review_id(self) -> str:
        """Generate unique review ID"""
        import hashlib
        content = datetime.utcnow().isoformat().encode()
        return hashlib.sha256(content).hexdigest()[:16]


class GovernanceEngine:
    """Main governance orchestrator"""

    def __init__(self):
        self.safety_checker = SafetyChecker()
        self.approval_queue = ApprovalQueue()
        self.audit_log = []

    def submit_action(self,
                      action: Dict,
                      submitter: str,
                      submitter_role: Role) -> Dict:
        """
        Submit action for governance review

        Args:
            action: Action to take
            submitter: Who submitted
            submitter_role: Role of submitter

        Returns:
            {
                'status': 'approved' or 'pending',
                'review_id': str,
                'safety_check': {...},
                'next_steps': str,
            }
        """

        # Step 1: Safety check
        safety = self.safety_checker.check_safety(action)

        # Step 2: Submit for approval
        approval = self.approval_queue.submit_for_review(
            action,
            safety['risk_level'],
            submitter
        )

        # Step 3: Log
        self._log_audit({
            'event': 'action_submitted',
            'review_id': approval['review_id'],
            'action_type': action.get('type'),
            'submitter': submitter,
            'risk_level': safety['risk_level'],
            'safety_issues': safety['issues'],
        })

        # Determine next steps
        if approval['status'] == ApprovalStatus.APPROVED.value:
            next_steps = "Ready to execute immediately"
        else:
            next_steps = f"Awaiting {approval['required_approvals']} approvals"

        return {
            'status': approval['status'],
            'review_id': approval['review_id'],
            'safety_check': safety,
            'required_approvals': approval['required_approvals'],
            'next_steps': next_steps,
        }

    def get_pending_for_approver(self, approver: str, role: Role) -> Dict:
        """Get pending items for approver"""
        pending = self.approval_queue.get_pending(role)

        return {
            'approver': approver,
            'role': role.value,
            'pending_count': len(pending),
            'pending_items': pending,
        }

    def approve_action(self, review_id: str, approver: str, role: Role) -> Dict:
        """Approve pending action"""
        result = self.approval_queue.approve(review_id, approver, role)

        self._log_audit({
            'event': 'action_approved',
            'review_id': review_id,
            'approver': approver,
            'approver_role': role.value,
        })

        return result

    def reject_action(self, review_id: str, rejecter: str, reason: str) -> Dict:
        """Reject pending action"""
        result = self.approval_queue.reject(review_id, rejecter, reason)

        self._log_audit({
            'event': 'action_rejected',
            'review_id': review_id,
            'rejecter': rejecter,
            'reason': reason,
        })

        return result

    def _log_audit(self, entry: Dict):
        """Log to audit trail"""
        entry['timestamp'] = datetime.utcnow().isoformat()
        self.audit_log.append(entry)

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get audit trail"""
        return self.audit_log[-limit:]


def main():
    """Test governance engine"""
    print("\n" + "="*70)
    print("PHASE 9: GOVERNANCE ENGINE TEST")
    print("="*70 + "\n")

    # Initialize
    governance = GovernanceEngine()

    # Test action 1: Low risk (should auto-approve)
    print("Test 1: Low-risk Discord message")
    action1 = {
        'type': 'post_discord',
        'channel': 'news',
        'content': 'Bitcoin reaches new all-time high',
        'agent': 'ez_feed',
    }

    result1 = governance.submit_action(action1, 'operator1', Role.OPERATOR)
    print(f"  Status: {result1['status']}")
    print(f"  Review ID: {result1['review_id']}")
    print(f"  Risk Level: {result1['safety_check']['risk_level']}")
    print(f"  Next Steps: {result1['next_steps']}\n")

    # Test action 2: Medium risk (needs 1 approval)
    print("Test 2: Medium-risk X post with questionable tone")
    action2 = {
        'type': 'post_x',
        'channel': 'x',
        'content': 'URGENT!!! Bitcoin going to the moon!!!',
        'agent': 'ez_feed',
    }

    result2 = governance.submit_action(action2, 'operator2', Role.OPERATOR)
    print(f"  Status: {result2['status']}")
    print(f"  Review ID: {result2['review_id']}")
    print(f"  Risk Level: {result2['safety_check']['risk_level']}")
    print(f"  Issues: {result2['safety_check']['issues']}")
    print(f"  Required Approvals: {result2['required_approvals']}\n")

    # Get pending for reviewer
    print("Test 3: Check pending approvals for reviewer")
    pending = governance.get_pending_for_approver('reviewer1', Role.REVIEWER)
    print(f"  Pending for: {pending['role']}")
    print(f"  Count: {pending['pending_count']}")
    if pending['pending_items']:
        for item in pending['pending_items']:
            print(f"    - {item['review_id']}: {item['action'].get('type')}\n")

    # Approve action
    print("Test 4: Approve action")
    approval = governance.approve_action(result2['review_id'], 'reviewer1', Role.REVIEWER)
    print(f"  Result: {approval['status']}")
    print(f"  Message: {approval['message']}\n")

    # Audit trail
    print("Test 5: Audit trail")
    audit = governance.get_audit_log(limit=5)
    print(f"  Total entries: {len(audit)}")
    for entry in audit:
        print(f"    {entry['timestamp']}: {entry['event']}")

    print("\n✓ Governance Engine Test Complete")


if __name__ == "__main__":
    main()
