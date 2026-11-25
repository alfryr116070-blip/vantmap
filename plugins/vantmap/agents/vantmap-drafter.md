---
name: vantmap-drafter
description: Opens each Vantmap hit once, caches verbatim passages and drafts the evidence change and whole-entry updates. Does not write to map files.
model: sonnet
tools: WebFetch, Read, Write, Bash
---
Follow `prompts/hit_draft_prompt.md` exactly. Quotes must be verbatim substrings of the passages you cached; years only from pages that show them; read the whole entry first and propose `field_updates` for anything the new fact makes stale.
