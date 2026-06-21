# Phase 4b: Execution Guide — Claude MCP Integration

## Status: READY TO EXECUTE

All configuration and documentation is ready. Follow these steps to integrate Claude with the EZ Orchestrator MCP server.

---

## Prerequisites

✓ MCP server running: `python3 mcp/server.py`
✓ All 31 profiles loaded
✓ Claude Code or Claude API available
✓ MCP configuration ready (`.mcp/mcp.json`)
✓ System prompt ready (`CLAUDE_SYSTEM_PROMPT.md`)

---

## Execution Steps

### Step 1: Start the MCP Server

**Terminal 1:**
```bash
cd ez-orchestrator
python3 mcp/server.py
```

**Expected Output:**
```
=== EZ Orchestrator MCP Server ===

✓ ProfileLoader initialized
✓ Projects: 9, Roles: 6, Vibes: 7, Channels: 9
✓ MCP Server Ready
✓ Available tools:
    - get_project
    - get_role
    - get_vibe
    - get_channel
    - get_context
    - list_profiles
```

### Step 2: Load Claude with MCP Tools

**Option A: Claude Code CLI**

Configure MCP in `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "ez-orchestrator": {
      "command": "python3",
      "args": ["/path/to/ez-orchestrator/mcp/server.py"],
      "env": {
        "MCP_PROFILE_PATH": "/path/to/ez-orchestrator/profiles",
        "MCP_SCHEMA_PATH": "/path/to/ez-orchestrator/schemas"
      }
    }
  }
}
```

Restart Claude Code to load the MCP tools.

**Option B: Claude API**

Use the system prompt from `CLAUDE_SYSTEM_PROMPT.md` in your API calls.

**Option C: Claude Web (claude.ai)**

Load the system prompt in your custom instructions.

### Step 3: Verify MCP Tools Are Available

**Prompt Claude:**
```
List the MCP tools you have available.
```

**Expected Response:**
```
I have access to the following MCP tools:
- get_project(name)
- get_role(name)
- get_vibe(name)
- get_channel(name)
- get_context(project, role)
- list_profiles(type)

Ready to use them.
```

### Step 4: Test Context Loading

**Prompt Claude:**
```
Use get_context to load the orchestration context for EZ Chain + Core Engineer.
```

**Expected Response:**
```
Calling: get_context(project="ez_chain", role="core_engineer")

Context Retrieved:
- Project: EZ Chain
- Role: Core Engineer
- Vibe: Prestige
- Channels: 9 (github, discord, x, ...)

The context includes:
- Project category: infrastructure
- Role authority: strategic
- Vibe formality: high
- Channel formats: Markdown for GitHub, 280 chars for X, etc.
```

### Step 5: Test Profile Application

**Prompt Claude:**
```
Write a GitHub PR description for EZ Chain's consensus validation refactor.
The refactor improves throughput by 40%.

First, use get_context("ez_chain", "core_engineer") to load the profile.
Then, apply the formatting rules and vibe guidance.
Finally, generate the PR.
```

**Expected Response:**

Claude should:
1. Call `get_context("ez_chain", "core_engineer")`
2. Show what it loaded (prestige vibe, GitHub channel)
3. Generate Markdown PR with:
   - Professional, data-driven language
   - Clear problem/solution/testing sections
   - Linked issues
   - Tradeoff analysis
   - Verification checkmarks

**Output should look like:**
```markdown
# refactor: optimize consensus validation for 40% throughput

## Problem
Current validation loop has suboptimal cache locality, 
causing 40% of CPU time in the hot path.

## Solution
Refactored to:
- Improve memory access patterns (cache locality)
- Reduce allocations in critical path
- Parallelize venue evaluation

## Performance Impact
- Throughput: 40% improvement (1000 TPS → 1400 TPS)
- Latency: <2% regression (acceptable tradeoff)
- Memory: 15% reduction under load

## Testing
- Benchmark suite: 100 runs, consistent results
- Stress test: 10M routes, zero failures
- A/B: 0.5% difference (within margin)

Fixes #456
```

### Step 6: Test Multiple Channels

**Prompt Claude:**
```
Using get_context("ez_up", "community_manager"), 
write a Discord announcement for the creator rewards launch.
```

**Expected Response:**

Claude should generate Discord-specific content:
- Use threads and emoji
- Energetic, builder vibe
- Casual-professional tone
- Clear CTAs
- Community-focused

### Step 7: Test Channel Diversity

**Prompt Claude:**
```
I need content for three channels, same project and role:
- Project: tech_news_studio
- Role: ai_builder

Generate content for:
1. GitHub (technical discussion)
2. Beehiiv (newsletter)
3. X (social media)

Use get_context and adapt for each channel.
```

**Expected Response:**

Claude should generate three versions, each shaped by:
- Same vibe (prestige + research)
- Different channel formatting (Markdown, email, 280 chars)
- Different tone application (technical, narrative, punchy)

---

## Verification Checklist

- [ ] MCP server running without errors
- [ ] All 6 tools available in Claude
- [ ] `get_context` returns full profile
- [ ] Claude shows what profiles it loaded
- [ ] Outputs follow channel formatting rules
- [ ] Outputs follow vibe tone guidance
- [ ] Multiple projects/roles work
- [ ] Multiple channels work
- [ ] Claude explains which rules it's applying
- [ ] Outputs are deterministic (same input = same output)

---

## Expected Outcomes

**After Phase 4b:**

✓ Claude is profile-aware
✓ Claude is vibe-aware
✓ Claude is channel-aware
✓ Claude generates context-shaped outputs
✓ Outputs are deterministic and verifiable
✓ Team consistency is enforced by profiles

---

## Troubleshooting

### Tools Not Available
- Verify MCP server is running
- Check MCP configuration
- Restart Claude to reload MCP

### Context Not Loading
- Ensure profile names are correct (case-sensitive)
- Verify profiles exist: `ls profiles/projects/ez_chain.yaml`
- Test directly: `python3 mcp/server.py` and check example output

### Outputs Not Shaped by Profiles
- Verify Claude called `get_context`
- Check that vibe/channel were in the response
- Ensure system prompt includes profile application instructions
- Review do/dont lists from profiles

### Performance Issues
- All tool calls are <50ms (very fast)
- Server runs in-memory (no network latency)
- Should be instant for Claude integration

---

## Success Criteria

**Phase 4b is successful when:**

1. Claude can call all 6 orchestrator tools
2. `get_context` returns full orchestration context
3. Claude applies vibe tone to outputs
4. Claude applies channel formatting to outputs
5. Claude follows best practices from profiles
6. Outputs are deterministic (repeatable)
7. Outputs are verifiable (show applied rules)
8. Multiple channels/roles/projects work
9. Documentation is complete

---

## Next: Phase 5

Once Phase 4b is verified, move to Phase 5:

**Phase 5: Orchestrator Logic**

Build the automatic layer:
- Context detection (identify project/role/channel from input)
- Auto-profile loading
- Automatic tone application
- Multi-channel routing

---

## Resources

- **MCP Integration Guide:** `docs/PHASE_4B_CLAUDE_INTEGRATION.md`
- **System Prompt:** `CLAUDE_SYSTEM_PROMPT.md`
- **Real Examples:** `docs/PHASE_4B_CLAUDE_INTEGRATION.md` (Examples section)
- **MCP Server:** `mcp/server.py`
- **Profiles:** `profiles/` (all 31 profiles)

---

## Timeline

- Setup: 15 minutes
- Testing: 30 minutes
- Verification: 30 minutes
- **Total: ~1 hour**

---

**Phase 4b is ready to execute. Claude will become profile-aware within 1 hour.** 🚀
