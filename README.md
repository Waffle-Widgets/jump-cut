# Jump Cut — 2026 Epic AI MegaJam entry

Our entry for the 2026 Epic AI MegaJam (Nov 12–15). Made by our team with Unreal Engine 5.8,
Claude Code (through Epic's Unreal MCP) and Gemini.

This repo was created on 2026-11-12 by `tools/bootstrap/new_jam_repo.ps1`, which copies only tools, scripts,
agent settings and docs from our practice repo, plus Unreal's own Third Person Blueprint template.
All gameplay, levels and art in this repo were made during the jam; the Git history shows when.
What we *did* prepare before the jam is declared, file by file, in [`docs/PREJAM.md`](docs/PREJAM.md) —
jam rule §7h allows it, and the itch.io page asks us to say what it is.

**Our Glass Box devlog is [`docs/devlog/`](docs/devlog/README.md)** (one file per entry): what we asked the AI agents for, what they
actually did, and everything that broke on the way.

## New to the team? Start here

1. [`docs/HOW_WE_WORK.md`](docs/HOW_WE_WORK.md): how we work, in five minutes (roles per computer, the playtest loop).
2. [`docs/SETUP_TEAMMATE.md`](docs/SETUP_TEAMMATE.md): set up your Windows PC or Mac.
3. [`docs/PLAYTEST.md`](docs/PLAYTEST.md): how to get test builds and report problems.

Almost everything is done by asking Claude in a chat opened on this repo folder.

## Where things are

| Path | What it is |
| --- | --- |
| `JumpCut/` | The Unreal project (open `JumpCut.uproject` in UE 5.8) |
| `docs/HOW_WE_WORK.md` | How the team works: start here |
| `docs/TEAM.md` | Who's on the team, what each computer does, who owns what |
| `docs/PLAYTEST.md` | Test builds and reporting problems as GitHub issues |
| `docs/PITCH.md` | The game we're making |
| `docs/ROADMAP.md` | What's open, the cut list, what we decided |
| `docs/PLAN.md` | Team plan and schedule |
| `docs/RULES.md` | The official jam rules we follow |
| `docs/PREJAM.md` | What we made **before** the jam, declared file by file (rule §7h) |
| `docs/devlog/` | Our devlog (Glass Box), one file per entry |
| `CREDITS.md` | Every asset we didn't make ourselves |
| `CLAUDE.md` / `GEMINI.md` | Standing instructions for our AI agents — pre-jam, declared in `docs/PREJAM.md` |
| `tools/`, `Art/Blender/*.py` | Scripts, mostly prepared before the jam (sound generator, AI 3D model cleanup, rigging, walk cycles) — declared in `docs/PREJAM.md`, which also says which ones were written *during* the jam |
