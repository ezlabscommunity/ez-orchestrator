# EZ Orchestrator Profiles Guide

## Overview

Profiles are YAML-based configuration files that define how the EZ Labs orchestrator engine routes context, enforces tone, and coordinates outputs across AI agents and communication channels.

There are four profile types:
- **Projects** — Define product boundaries, categories, audiences, and default tone
- **Roles** — Define responsibilities, authority levels, and communication expectations
- **Vibes** — Define linguistic tone, formatting rules, and content structure
- **Channels** — Define platform-specific constraints, norms, and expectations

---

## Project Profiles

### Purpose
Project profiles define the organizational unit around which orchestration decisions are made. Each project declares its category, audience, channels, and preferred tone (vibe).

### Location
`profiles/projects/*.yaml`

### Schema
See `schemas/project.schema.yaml` for strict field definitions.

### Minimal Example
```yaml
name: "EZ Chain"
description: "Proof-of-Active-Human blockchain infrastructure"
category: "infrastructure"
pillars:
  - "Decentralized validation"
  - "Human-verifiable proofs"
default_vibe: "prestige"
status: "active"
channels:
  - "github"
  - "discord"
```

### When to Create a New Project Profile
- You're launching a new product or major feature area
- The product has its own team, audience, or communication strategy
- You want the orchestrator to route context differently for this project

### Key Fields Explained

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Official project name |
| `description` | Yes | 1-2 sentence description |
| `category` | Yes | Type: infrastructure, trading, creative, content, security, tooling, gaming, cultural |
| `pillars` | Yes | 2-5 core principles or values |
| `default_vibe` | Yes | Primary tone (e.g., prestige, builder, research) |
| `status` | Yes | Current state: active, beta, planning, archived |
| `channels` | Yes | List of primary communication channels |
| `secondary_vibes` | No | 0-3 alternative tones for context switches |
| `audience` | No | Target user/reader segment |
| `links` | No | GitHub, docs, website, discord URLs |
| `metadata` | No | Custom fields: token, mainnet, status, etc. |

---

## Role Profiles

### Purpose
Role profiles define expectations, authority levels, and communication preferences for human actors or AI agents operating within the EZ Labs ecosystem.

### Location
`profiles/roles/*.yaml`

### Schema
See `schemas/role.schema.yaml` for strict field definitions.

### Minimal Example
```yaml
name: "Core Engineer"
description: "Technical leader responsible for architecture and implementation"
authority_level: "strategic"
required_context:
  - "Technical architecture"
  - "Project roadmap"
vibe_affinity:
  - "prestige"
  - "builder"
```

### When to Create a New Role Profile
- You're adding a new organizational role or function
- Different people/agents have materially different communication expectations
- You want to enforce different authority levels or context requirements

### Key Fields Explained

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Role title |
| `description` | Yes | 1-2 sentence overview |
| `authority_level` | Yes | Decision tier: executive, strategic, operational, tactical, contributor |
| `required_context` | Yes | 1-5 essential pieces of information this role needs |
| `vibe_affinity` | Yes | 1-3 tones this role naturally aligns with |
| `responsibilities` | No | List of 2-8 key duties |
| `preferred_channels` | No | Channels this role typically uses |
| `communication_style` | No | Formality, response time, escalation rules |
| `interaction_rules` | No | Guidelines for working with this role |
| `skill_requirements` | No | Expected expertise areas |
| `metadata` | No | Seniority, team, typical projects, on-call status |

---

## Vibe Profiles

### Purpose
Vibe profiles define the **tone, language, formatting, and content structure** used when communicating in a particular style. Vibes are composable and can be applied across different projects, roles, and channels.

### Location
`profiles/vibes/*.yaml`

### Schema
No strict schema; vibes have a flexible, extensible structure focusing on operational guidance.

### Minimal Example
```yaml
name: "Prestige"
description: "Professional, authoritative tone for executive contexts"
tone_characteristics:
  formality: "high"
  professionalism: "executive"
language_guidelines:
  - "Use precise, industry-standard terminology"
  - "Emphasize data and verifiable facts"
do_list:
  - "✓ Include data, metrics, and examples"
  - "✓ Explain tradeoffs explicitly"
dont_list:
  - "✗ Marketing language or hyperbole"
  - "✗ Vague recommendations without context"
```

### When to Create a New Vibe
- You identify a new communication tone used consistently across projects
- You want to enforce a specific linguistic or formatting style
- You're adding a new platform with unique constraints

### Current Vibes

#### Prestige
**Use for:** Executive summaries, strategic decisions, technical deep-dives, official communications
- Formality: High
- Audience: Decision-makers, experts
- Focus: Data, evidence, tradeoffs, verification

#### Builder
**Use for:** Implementation guides, shipping updates, practical how-tos, iteration notes
- Formality: Medium
- Audience: Engineers, practitioners
- Focus: Code, examples, speed, shipping

#### Research
**Use for:** Investigations, validation, evidence-based analysis, technical papers
- Formality: Academic-professional
- Audience: Researchers, specialists
- Focus: Methodology, findings, citations, reproducibility

#### Public
**Use for:** Community, social media, marketing, general audience communication
- (To be created)

#### Cinematic
**Use for:** Creative storytelling, brand narratives, immersive content
- (To be created)

---

## Channel Profiles

### Purpose
Channel profiles define platform-specific constraints, norms, and best practices. They account for character limits, media formats, audience size, discoverability, and archival properties.

### Location
`profiles/channels/*.yaml`

### Schema
No strict schema; channels are flexible and platform-specific.

### Minimal Example
```yaml
name: "GitHub"
description: "Code hosting, issue tracking, and technical discussion"
constraints:
  format: "Markdown + code blocks"
  character_limit: null
  media: "Code, diagrams, attachments"
best_practices:
  - "Use issue descriptions for context"
  - "Link related issues and PRs"
  - "Include reproducible steps for bugs"
```

### Current Channels

- `github.yaml` — Code, PRs, issues, discussions
- `discord.yaml` — Real-time chat, community
- `x.yaml` — Twitter/X social media (character limits, engagement)
- `internal_docs.yaml` — Google Docs, shared knowledge bases
- `website.yaml` — Public-facing content, marketing
- `beehiv.yaml` — Email newsletter (long-form, narrative)
- `telegram.yaml` — Messaging, quick updates
- `youtube.yaml` — Video content, long-form video
- `tiktok.yaml` — Short-form video, viral content

---

## Using Profiles Programmatically

### Python

```python
from orchestrator.loader import ProfileLoader

# Initialize loader
loader = ProfileLoader('./profiles', './schemas')

# Get individual profiles
ez_chain = loader.get_project('ez_chain')
core_eng = loader.get_role('core_engineer')
prestige = loader.get_vibe('prestige')

# Get profile data
print(ez_chain.get('default_vibe'))  # 'prestige'
print(core_eng.get('authority_level'))  # 'strategic'

# Build orchestration context (project + role + vibes + channels)
context = loader.get_context('ez_chain', 'core_engineer')
print(context['vibe'])  # Prestige vibe profile
print(context['channels'])  # All channels ez_chain operates on
```

### List All Profiles

```python
# List all profiles by type
all_profiles = loader.list_all()
# {'projects': ['ez_chain', ...], 'roles': ['core_engineer', ...], ...}

# List specific type
projects = loader.list_profiles('projects')
```

### Export to JSON

```python
# Export all profiles to JSON for external tools
loader.export_to_json('./export')
```

---

## Profile Validation

### Run Schema Validation

```bash
python orchestrator/loader.py
```

This validates all profiles against their schemas and reports errors.

### Manual Validation

1. **Ensure required fields are present** — Check schema for `required_fields` list
2. **Validate enum values** — Check against `allowed_values` in schema
3. **Check cross-references** — Ensure referenced vibes/channels exist
4. **Test programmatically** — Load via Python loader and inspect

---

## Best Practices

### When Naming Profiles
- **Projects:** Use snake_case (e.g., `ez_chain`, `crypto_news`)
- **Roles:** Use snake_case (e.g., `core_engineer`, `community_manager`)
- **Vibes:** Use lowercase (e.g., `prestige`, `builder`, `research`)
- **Channels:** Use lowercase (e.g., `github`, `discord`, `x`)

### When Writing Descriptions
- Be concise: 1-2 sentences max
- Focus on purpose, not implementation
- Use active voice ("X enables Y" vs "X is used for Y")

### When Defining Vibe Guidelines
- **Do lists:** Start with ✓ for positive guidance
- **Don't lists:** Start with ✗ for anti-patterns
- **Examples:** Provide 2-3 concrete examples for opening/closing patterns
- **Audience:** Be explicit about who this vibe serves

### When Cross-Referencing
- Always validate the target profile exists
- Use exact names (case-sensitive)
- Document which profiles depend on which others

---

## Extending Profiles

### Adding New Fields

Profiles support arbitrary YAML, so you can add custom fields:

```yaml
name: "Custom Project"
description: "..."
custom_field: "value"
metadata:
  arbitrary_key: "arbitrary_value"
```

### Adding New Vibe

1. Create `profiles/vibes/new_vibe.yaml`
2. Include: name, description, tone_characteristics, language_guidelines, do_list, dont_list, example_opening, example_closing, audience, platforms, metadata
3. Reference in project or role `vibe_affinity` or `default_vibe`
4. Document in this guide

### Adding New Channel

1. Create `profiles/channels/new_channel.yaml`
2. Include: name, description, constraints, best_practices, format, audience
3. Reference in project `channels` list
4. Document in this guide

---

## Next Steps

1. **Fill out remaining project profiles** — Use ez_chain.yaml as template
2. **Create additional role profiles** — community_manager, ai_builder, security_partner, founder, creative_technologist
3. **Create channel profiles** — github, discord, x, internal_docs, website, beehiv, telegram, youtube, tiktok
4. **Build MCP server** — Expose profiles as tools for downstream agents
5. **Create orchestrator engine** — Use profiles to route context and enforce tone
