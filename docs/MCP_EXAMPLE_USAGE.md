# MCP Server Usage Examples

## Running the MCP Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python mcp/server.py

# Expected output:
# === EZ Orchestrator MCP Server ===
# 
# ✓ ProfileLoader initialized
# ✓ Profiles: ./profiles
# ✓ Schemas: ./schemas
# 
#   projects: 9 profiles
#   roles: 6 profiles
#   vibes: 7 profiles
#   channels: 9 profiles
# 
# ✓ MCP Server Ready
# ✓ Available tools:
#     - get_project
#     - get_role
#     - get_vibe
#     - get_channel
#     - get_context
#     - list_profiles
```

---

## Example 1: Get Full Context

**Claude Query:**
```
Use get_context to retrieve the orchestration context for EZ Chain + Core Engineer
```

**Tool Call:**
```python
server.call_tool("get_context", project="ez_chain", role="core_engineer")
```

**Response:**
```json
{
  "success": true,
  "context": {
    "project": {
      "name": "EZ Chain",
      "description": "Proof-of-Active-Human blockchain infrastructure...",
      "category": "infrastructure",
      "pillars": [
        "Proof-of-Active-Human consensus mechanism",
        "Human-verifiable validation",
        "Decentralized infrastructure",
        "Developer-first tooling"
      ],
      "default_vibe": "prestige",
      "secondary_vibes": ["builder", "research"],
      "status": "active",
      "channels": ["github", "discord", "website", "internal_docs"],
      "audience": "Protocol developers, node operators, cryptography researchers...",
      "metadata": {
        "token": "EZC",
        "mainnet": true,
        "testnet": true,
        "audit_status": "pending",
        "security_contact": "security@ezchain.ai"
      }
    },
    "role": {
      "name": "Core Engineer",
      "description": "Senior technical leader responsible for architecture...",
      "authority_level": "strategic",
      "required_context": [
        "Technical architecture and design patterns",
        "Project roadmap and milestones",
        "Team capacity and availability",
        "Security considerations and threat model",
        "Regulatory and compliance requirements"
      ],
      "vibe_affinity": ["prestige", "builder", "research"],
      "preferred_channels": ["github", "discord", "internal_docs"],
      "communication_style": {
        "formality_level": "professional",
        "response_time": "24 hours (critical: 4 hours)",
        "escalation_triggers": [
          "Critical security issues",
          "Timeline impacts > 1 week",
          "Architecture-level conflicts",
          "Cross-project dependencies"
        ]
      },
      "interaction_rules": [
        "Always provide technical rationale with data and tradeoffs",
        "Use deterministic reasoning; explain decision criteria explicitly",
        "Include context: what problem are we solving, what constraints apply",
        "Decisions should be verifiable and auditable",
        "Prefer options with analysis over top-line recommendations"
      ],
      "metadata": {
        "seniority": "senior",
        "team": "core",
        "on_call": true
      }
    },
    "vibe": {
      "name": "Prestige",
      "description": "Professional, authoritative tone emphasizing quality...",
      "tone_characteristics": {
        "formality": "high",
        "professionalism": "executive",
        "accessibility": "expert-to-expert",
        "energy": "measured and deliberate"
      },
      "language_guidelines": [
        "Use precise, industry-standard terminology",
        "Avoid colloquialisms and informal language",
        "Emphasize data, evidence, and verifiable facts",
        "Explain complexity without oversimplifying",
        "Lead with expertise and credibility signals"
      ],
      "do_list": [
        "✓ Include data, metrics, and specific examples",
        "✓ Explain tradeoffs and constraints explicitly",
        "✓ Use active voice and clear subject attribution",
        "✓ Reference standards, best practices, and established patterns",
        "✓ Validate with deterministic reasoning"
      ],
      "dont_list": [
        "✗ Marketing language or hyperbole",
        "✗ Assumptions without supporting evidence",
        "✗ Vague recommendations without context",
        "✗ Dismissive tone toward questions or alternatives",
        "✗ Jargon without explanation"
      ]
    },
    "channels": {
      "github": {
        "name": "GitHub",
        "description": "Code review, technical discussion...",
        "constraints": {
          "format": "Markdown + code blocks + links",
          "character_limit": null,
          "media": "Code snippets, diffs, diagrams..."
        },
        "best_practices": [
          "Use issue templates for consistency",
          "Link related issues and PRs (fixes #123)",
          "Include reproducible steps for bugs",
          "Use code blocks with language identifier",
          "Request reviewers explicitly for PRs"
        ],
        "formatting_rules": {
          "headers": "# Title (H1 for issue titles, H2+ for sections)",
          "code": "Use triple backticks with language: ```rust code ```",
          "emphasis": "**bold** for important terms, `code` for identifiers",
          "lists": "- bullets for features, 1. numbers for steps",
          "links": "[Display Text](URL) — always descriptive anchor text"
        }
      },
      "discord": {
        "name": "Discord",
        "description": "Real-time chat, community, voice...",
        "constraints": {
          "format": "Markdown, threads, reactions, embeds",
          "character_limit": 2000
        }
        // ... more channel details
      }
      // ... other channels
    }
  }
}
```

---

## Example 2: List Available Projects

**Claude Query:**
```
What projects are available?
```

**Tool Call:**
```python
server.call_tool("list_profiles", type="projects")
```

**Response:**
```json
{
  "success": true,
  "profiles": [
    "ez_chain",
    "zendex",
    "ez_path",
    "ez_up",
    "ezverse",
    "ojet3d",
    "ez_secure",
    "crypto_news_org",
    "tech_news_studio"
  ]
}
```

---

## Example 3: Get a Specific Channel Profile

**Claude Query:**
```
How should I format content for X (Twitter)?
```

**Tool Call:**
```python
server.call_tool("get_channel", name="x")
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "name": "X",
    "description": "Public social media platform for announcements...",
    "constraints": {
      "format": "Plain text + links + media",
      "character_limit": 280,
      "media": "Images (1200x675), videos, GIFs, polls"
    },
    "tone_guidelines": {
      "formality": "medium-casual",
      "primary_vibe": "builder",
      "temperature": "energetic, authentic, accessible"
    },
    "best_practices": [
      "Start threads with a hook or compelling statement",
      "Use relevant hashtags (#crypto, #web3, #ethereum, #ezlabs)",
      "Pin important announcements (1 per profile)",
      "Engage with replies and retweets",
      "Use visuals for engagement (images, videos)",
      "Post at optimal times (weekday mornings/evenings UTC)",
      "Keep language simple and punchy (280 chars is tight)",
      "Avoid jargon without explanation"
    ],
    "do_list": [
      "✓ Lead with news or compelling statement",
      "✓ Use threads for deeper dives (max 5-7 tweets)",
      "✓ Include visuals (images, charts, videos)",
      "✓ Link to detailed resources (docs, GitHub)",
      "✓ Engage with community replies"
    ],
    "dont_list": [
      "✗ Hype without substance ('moon', 'lambo', 'to the moon')",
      "✗ Over-explain (280 chars is tight, link to docs)",
      "✗ Spam hashtags or mentions",
      "✗ Delete tweets (archive instead)"
    ]
  }
}
```

---

## Example 4: Claude Uses Context to Shape Output

**Setup:**
```
You are the EZ Labs orchestrator.

When generating content, follow these steps:
1. Get the target project context
2. Get the target role profile
3. Get the target channel formatting rules
4. Apply the vibe guidelines
5. Shape output accordingly
```

**Claude Prompt:**
```
Write a GitHub PR description for EZ Path's x402 router optimization.
The author is a Core Engineer, we're shipping a 40% performance improvement.
```

**Claude Process:**
1. `get_context("ez_path", "core_engineer")`
2. Extract vibe: prestige
3. Extract channel: github
4. Apply formatting rules: Markdown, code blocks, links
5. Apply interaction rules: data-driven, tradeoffs, verification
6. Generate output

**Claude Output:**
```markdown
# perf: optimize x402 router for 40% throughput improvement

## Problem
The current routing loop has suboptimal cache locality,
causing 60% of CPU time in the hot path.

## Solution
Refactored the router to:
- Improve memory access patterns (cache locality)
- Reduce allocations in critical path
- Parallelize venue evaluation where possible

## Performance Impact
- Throughput: 40% improvement (1000 TPS → 1400 TPS)
- Latency: <2% regression (acceptable tradeoff)
- Memory: 15% reduction under load

## Testing
- Benchmark suite: 100 runs average
- Production simulation: 10M routes tested
- A/B: 0.5% difference (within margin)

## Tradeoffs
The refactor increases code complexity slightly but the
performance gains justify the maintenance cost.

Refs: #234
```

---

## Example 5: List All Available Roles

**Claude Query:**
```
What roles are available in the organization?
```

**Tool Call:**
```python
server.call_tool("list_profiles", type="roles")
```

**Response:**
```json
{
  "success": true,
  "profiles": [
    "core_engineer",
    "founder",
    "community_manager",
    "ai_builder",
    "creative_technologist",
    "security_partner"
  ]
}
```

---

## Example 6: Error Handling

**Claude Query:**
```
Get context for a project that doesn't exist
```

**Tool Call:**
```python
server.call_tool("get_context", project="nonexistent", role="core_engineer")
```

**Response:**
```json
{
  "error": "Context not found for project='nonexistent', role='core_engineer'"
}
```

**Claude Should:**
1. Recognize the error
2. List available projects: `list_profiles("projects")`
3. Ask user to clarify which project they meant
4. Retry with correct project name

---

## Integration Workflow

```
┌─────────────┐
│ Claude      │ "Write a GitHub PR for EZ Chain"
│ Query       │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Claude decides to use tools:         │
│ 1. get_context("ez_chain", "core_engineer")
│ 2. get_vibe("prestige")
│ 3. get_channel("github")
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ MCP Server returns:                  │
│ - Full project + role context        │
│ - Vibe tone guidelines               │
│ - Channel formatting rules           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Claude shapes output:                │
│ - Use Markdown + code blocks         │
│ - Professional, authoritative tone   │
│ - Data-driven arguments              │
│ - Verifiable decision criteria       │
└──────┬───────────────────────────────┘
       │
       ▼
┌─────────────┐
│ Output: PR  │ Shaped by project + role + vibe + channel
│ Description │ Deterministic, verifiable, consistent
└─────────────┘
```

---

## Performance Notes

- All queries are **O(1)** lookups (dictionary-based)
- Profiles are loaded once at server startup
- No network latency (local filesystem)
- Recommended: Cache full context if calling multiple tools
- Optimal: Use `get_context()` for complete info (single query)

---

## Testing the MCP Server

```bash
# Test 1: Start the server
python mcp/server.py
# Should show all 31 profiles loaded

# Test 2: Verify profiles are accessible
cd /tmp/ez-orchestrator
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from orchestrator.loader import ProfileLoader

loader = ProfileLoader('./profiles', './schemas')
print("Projects:", loader.list_profiles('projects'))
print("Roles:", loader.list_profiles('roles'))
print("Vibes:", loader.list_profiles('vibes'))
print("Channels:", loader.list_profiles('channels'))

# Test context
context = loader.get_context('ez_chain', 'core_engineer')
print("\nContext keys:", list(context.keys()))
print("Channels available:", len(context['channels']))
EOF
```

---

**MCP Integration Ready** ✓
