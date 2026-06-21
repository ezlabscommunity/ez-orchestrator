# Phase 5: Orchestrator Logic — Automatic Context-Aware Orchestration

## Objective

Build the **Orchestrator Logic Layer** that automatically detects context and applies profiles WITHOUT requiring explicit requests.

After Phase 5, the system will be **fully autonomous**.

---

## What is Orchestrator Logic?

The layer that answers: "Given a user input, what context should I detect, what profiles should I load, and how should I apply them?"

```
User Input (e.g., "Write a GitHub PR for EZ Chain")
    ↓
Orchestrator Logic Layer
    ├─ Context Detector: "project=ez_chain, role=core_engineer, channel=github"
    ├─ Profile Loader: "get_context('ez_chain', 'core_engineer')"
    ├─ Vibe Applier: "Apply prestige tone"
    ├─ Channel Applier: "Apply GitHub formatting (Markdown, code blocks)"
    └─ Output Formatter: "Generate Markdown PR"
    ↓
Claude (with applied context)
    ↓
Profile-Shaped Output
```

---

## Phase 5 Architecture

### 5a: Context Detector
**Goal:** Auto-identify project, role, and channel from user input

**Input:** "Write a GitHub PR for EZ Chain's consensus refactor"

**Output:**
```json
{
  "project": "ez_chain",
  "role": "core_engineer",
  "channel": "github",
  "confidence": 0.95,
  "reasoning": "Keywords: 'GitHub' → channel, 'EZ Chain' → project, 'refactor' → core_engineer"
}
```

**Methods:**
- Keyword matching (GitHub → github, Discord → discord)
- Project name matching (EZ Chain → ez_chain)
- Role inference from task type (refactor → core_engineer, announcement → community_manager)
- Channel inference from platform mentions

### 5b: Profile Auto-Loader
**Goal:** Load profiles automatically after context detection

**Input:** Context detection output (project, role, channel)

**Output:** Full orchestration context ready to apply

**Process:**
1. Take detected: project, role, channel
2. Call: `get_context(project, role)`
3. Load: channel profile for each channel
4. Return: Complete profiles ready to apply

### 5c: Automatic Applicator
**Goal:** Apply tone, formatting, and best practices without Claude doing it manually

**Input:** User input + detected context + loaded profiles

**Output:** Claude system message with profiles pre-loaded and pre-applied

**What it applies:**
- Vibe tone (prestige → formal, builder → energetic)
- Channel formatting (GitHub → Markdown, X → 280 chars)
- Best practices (GitHub → linked issues, Discord → threads)
- Role expectations (strategic → data-driven, operational → action-focused)
- Example patterns (from profile examples)

### 5d: Multi-Channel Router
**Goal:** Route single input to multiple channels with appropriate adaptation

**Input:** "Announce mainnet launch"

**Output:**
```
GitHub (issue): Technical announcement with specs
Discord (thread): Community announcement with emoji
X (thread): 280-char hook + threads
Website (blog): Long-form announcement
```

Each adapted for its channel, same core message, perfect format per platform.

---

## Phase 5 Implementation Plan

### 5a: Build Context Detector

**File:** `orchestrator/context_detector.py`

```python
class ContextDetector:
    """Detect project, role, channel from user input"""
    
    def detect(self, input_text: str) -> dict:
        """
        Analyze input and return detected context
        
        Returns:
        {
            "project": "ez_chain",
            "role": "core_engineer", 
            "channel": "github",
            "confidence": 0.95,
            "reasoning": "..."
        }
        """
        pass
    
    def _detect_project(self, text: str) -> tuple:
        """Detect project from text"""
        pass
    
    def _detect_role(self, text: str, project: str) -> tuple:
        """Detect role from text and project context"""
        pass
    
    def _detect_channel(self, text: str) -> tuple:
        """Detect channel from text"""
        pass
```

**Detection Methods:**
- Exact matching: "GitHub" → "github"
- Fuzzy matching: "GH" → "github"
- Project keywords: "EZ Chain" → "ez_chain"
- Role inference: "refactor" → "core_engineer"
- Channel mentions: "post on X" → "x"

### 5b: Build Profile Auto-Loader

**File:** `orchestrator/profile_loader.py` (extend existing)

```python
class ProfileAutoLoader:
    """Load profiles based on detected context"""
    
    def load(self, detected_context: dict) -> dict:
        """Load full profiles based on detected context"""
        project = detected_context['project']
        role = detected_context['role']
        channels = detected_context.get('channels', [project_channels])
        
        # Load all profiles
        context = self.loader.get_context(project, role)
        
        # Add detected context
        context['detected'] = detected_context
        
        return context
```

### 5c: Build Automatic Applicator

**File:** `orchestrator/automatic_applicator.py`

```python
class AutomaticApplicator:
    """Apply profiles automatically to generation"""
    
    def build_enhanced_prompt(self, 
                            user_input: str,
                            detected_context: dict,
                            loaded_profiles: dict) -> str:
        """
        Build enhanced prompt with profiles pre-loaded
        
        Returns: System message + user message with context applied
        """
        
        # Extract relevant profiles
        vibe = loaded_profiles['vibe']
        channel = loaded_profiles['channels'].get(detected_context['channel'])
        role = loaded_profiles['role']
        
        # Build enhanced prompt
        enhanced = f"""
        {self._vibe_instructions(vibe)}
        {self._channel_instructions(channel)}
        {self._role_instructions(role)}
        
        User Request: {user_input}
        """
        
        return enhanced
    
    def _vibe_instructions(self, vibe: dict) -> str:
        """Generate vibe-specific instructions"""
        pass
    
    def _channel_instructions(self, channel: dict) -> str:
        """Generate channel-specific instructions"""
        pass
    
    def _role_instructions(self, role: dict) -> str:
        """Generate role-specific instructions"""
        pass
```

### 5d: Build Multi-Channel Router

**File:** `orchestrator/multi_channel_router.py`

```python
class MultiChannelRouter:
    """Route content to multiple channels"""
    
    def route(self, input_text: str, project: str, role: str) -> dict:
        """
        Take single input and route to multiple channels
        
        Returns:
        {
            "github": {...},
            "discord": {...},
            "x": {...},
            "website": {...}
        }
        """
        
        # Get project channels
        context = self.loader.get_context(project, role)
        project_channels = context['project'].get('channels', [])
        
        outputs = {}
        for channel in project_channels:
            # Generate for each channel with its own formatting
            channel_output = self._generate_for_channel(
                input_text, 
                project, 
                role, 
                channel,
                context['channels'][channel]
            )
            outputs[channel] = channel_output
        
        return outputs
    
    def _generate_for_channel(self, text, project, role, channel, channel_profile):
        """Generate output for specific channel"""
        pass
```

---

## Phase 5 Workflow

### Before Phase 5 (Manual)
```
User: "Write a GitHub PR for EZ Chain"
Claude: "Let me use get_context('ez_chain', 'core_engineer')..."
Claude: "Applying prestige tone..."
Claude: "Using Markdown format..."
Claude: Generates PR manually applying all rules
```

### After Phase 5 (Automatic)
```
User: "Write a GitHub PR for EZ Chain"
Orchestrator: "Detected project=ez_chain, role=core_engineer, channel=github"
Orchestrator: "Loaded context, applying prestige tone + GitHub formatting"
Claude: Receives enhanced prompt with all context pre-loaded
Claude: Generates PR with context automatically applied
```

---

## Phase 5 Success Criteria

- [ ] Context detector works (project, role, channel)
- [ ] Accuracy: >90% detection rate
- [ ] Auto-loader loads all profiles correctly
- [ ] Applicator pre-applies context to prompts
- [ ] Multi-channel router generates for all channels
- [ ] Outputs are consistently shaped by detected context
- [ ] Single input → multiple channel outputs work
- [ ] Full automation (Claude doesn't manually apply rules)

---

## Key Components

### 1. Context Detection (5a)
**Inputs:** User text  
**Outputs:** project, role, channel, confidence  
**Methods:** Keyword matching, fuzzy matching, inference  
**Success:** 90%+ accuracy  

### 2. Profile Loading (5b)
**Inputs:** Detected context  
**Outputs:** Full orchestration context  
**Methods:** Use existing ProfileLoader + auto-expand  
**Success:** All profiles loaded correctly  

### 3. Auto Application (5c)
**Inputs:** User input + context + profiles  
**Outputs:** Enhanced prompt with context pre-applied  
**Methods:** Build system message from profiles  
**Success:** Claude generates without manual application  

### 4. Multi-Channel Routing (5d)
**Inputs:** Single user request + project + role  
**Outputs:** Multiple channel-specific outputs  
**Methods:** Detect all channels for project, generate per channel  
**Success:** Outputs are perfectly adapted per channel  

---

## Example: Phase 5 in Action

**User Input:**
```
"Announce the ZENDEX institutional trading launch on all channels"
```

**Phase 5 Process:**

1. **Detect Context:**
   ```
   project: zendex
   role: founder (inferred from "launch" + CEO context)
   channels: [github, discord, x, website, telegram]
   confidence: 0.92
   ```

2. **Load Profiles:**
   ```
   get_context("zendex", "founder")
   → Returns: project + role + vibe + all 5 channels
   ```

3. **Apply Automatically:**
   ```
   Prestige vibe + founder role
   → "Professional, authoritative tone, strategic messaging"
   ```

4. **Route to Channels:**
   ```
   GitHub → Technical announcement (Markdown)
   Discord → Community announcement (emoji, threads)
   X → 280-char hook + threads
   Website → Blog post (long-form)
   Telegram → Alert message (concise)
   ```

**Output:**
```
github/announcement.md:
  # ZENDEX Institutional Trading Live
  Technical specs, performance metrics...

discord/announcement.md:
  🚀 ZENDEX Institutional Trading
  Premium UX, ZK privacy, live now...

x/thread.md:
  ZENDEX: Institutional-grade trading live.
  Tweet 2: ZK privacy enabled...
  Tweet 3: Premium UX...

website/blog.md:
  ZENDEX Institutional Trading Launch
  Long-form narrative, market position...

telegram/alert.md:
  ZENDEX live. Premium institutional trading.
  https://zendex.io
```

All from a single input, automatically routed and adapted.

---

## Timeline

| Task | Time | Status |
|------|------|--------|
| 5a: Context Detector | 2 hours | → Next |
| 5b: Profile Loader | 1 hour | → Next |
| 5c: Auto Applicator | 2 hours | → Next |
| 5d: Multi-Router | 2 hours | → Next |
| Testing | 2 hours | → Next |
| **Total** | **9 hours** | **Estimated** |

---

## Next Steps

1. Build Phase 5a: Context Detector
2. Build Phase 5b: Profile Auto-Loader
3. Build Phase 5c: Automatic Applicator
4. Build Phase 5d: Multi-Channel Router
5. Test end-to-end automation
6. Verify all success criteria

---

**Phase 5: Where the orchestrator becomes fully autonomous.** 🤖

---

## Status: PHASE 5 PLANNING COMPLETE

Ready to implement Phase 5a: Context Detector

**Next:** Start building context detection engine
