# ez-orchestrator
EZ Orchestrator is a unique digital network and community ecosystem.
ez-orchestrator/
├── profiles/               # Extended runtime configurations
│   ├── projects/           # Project-specific contexts (e.g., EZ Path, ZENDEX)
│   ├── channels/           # Formatting & rules per platform (e.g., X, Discord)
│   ├── roles/              # Persona boundaries (e.g., founder, core_engineer)
│   └── vibes/              # Behavioral tones (e.g., prestige, builder)
├── schemas/                # Strict validation files for profile enforcement
│   ├── project.schema.yaml
│   ├── channel.schema.yaml
│   ├── role.schema.yaml
│   └── vibe.schema.yaml
├── orchestrator/           # Core execution logic
│   ├── context_detector.py # Infers active context from user input
│   ├── profile_loader.py   # YAML to JSON parser & compiler
│   ├── tool_router.py      # Directs tasks to downstream MCP tools
│   ├── execution_engine.py # Coordinates state and model context
│   └── audit_logger.py     # Tracks agent behaviors and decisions
├── mcp/                    # Model Context Protocol layer
│   ├── manifest.json       # MCP Host config mapping tools to servers
│   └── tools/              # Actionable tool schemas
│       ├── publish_x.json
│       ├── publish_discord.json
│       └── commit_github.json
└── docs/                   # Full system architecture documentation
    ├── PROFILE_SYSTEM.md
    └── ORCHESTRATOR_FLOW.md
    
    name: "Profile Identifier"
description: "High-level purpose statement"
keywords: ["tag1", "tag2"]
tone: "Specific stylistic rules"
allowed_topics: []
forbidden_topics: []
disclaimers: "Required legal or brand boilerplate"
formatting_rules: "Platform/role constraints (e.g., length, formatting)"
example_phrases: []
vibe_defaults: []
channel_defaults: []

[ GitHub (YAML Profiles) ]
           │
           ▼
[ Orchestrator Engine ] ──► (Parses YAML → JSON at Runtime)
           │
           ▼
[ MCP Server Layer ] ────► Exposes "get_profile" Tool
           │
           ▼
[ AI Agent Context ] ────► Generates Deterministic & Context-Aware Output
