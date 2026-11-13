# 2026-11-12 — Jump Cut opens on the Mac (Justins-Mac-mini)

- **What we asked for:** get the Mac hooked up to Unreal and load the game as it stands; then check we had
  followed the setup guide.
- **Prompt(s) we gave the agent:** "Can we get hooked up to unreal and load up what we have so far for the jump cut
  repo. That's our game for the contest." and "There should have been a .md for getting set up. Did we follow it?"
- **What happened:**
  - The repo was on an old branch; Claude switched it to `playtest` (this Mac is a tester) and pulled the LFS files.
  - Unreal 5.8.4 is installed in `~/Epic Games/UE_5.8`, not `/Users/Shared/Epic Games` as
    `docs/SETUP_TEAMMATE.md` says (that folder held only an empty launcher stub).
  - **First launch failed:** the editor quit after 5 seconds with "missing Metal Toolchain". Xcode 27.2 was there,
    but not its Metal shader compiler. `xcodebuild -downloadComponent MetalToolchain` (839 MB, from Apple) fixed it.
    The setup guide says a Mac doesn't need Xcode; for UE 5.8 on this Mac it needed this part of it.
  - Second launch: editor up in about 2.5 minutes, `Lvl_JumpCut` loaded with 41 actors, 0 errors and 1 warning
    (`M_Boss` lacks the skeletal-mesh usage flag; the builder re-saves it). Play mode reached the title screen with
    no runtime errors. Nothing was saved.
  - The chat had started before the editor, so its Unreal tools never loaded; Claude talked to the MCP at
    `127.0.0.1:8000/mcp` with plain `curl` JSON-RPC instead.
  - **We hadn't followed the setup guide.** Checked step by step afterwards: `lfs.locksverify` was off (now on) and
    `tools/setup_mcp.sh` had never been run for this repo. Running it as the guide says gave "permission denied":
    the script was committed without its executable bit. Ran it with `bash`, then fixed the bit in Git.
- **What we learned:**
  - On a Mac, install Xcode's Metal Toolchain before the first open.
  - Shell scripts need their executable bit in Git (`git update-index --chmod=+x`), or every Mac trips on them.
  - Follow the setup guide first; it would have caught the missing MCP setup before anything else.
- **Media:** ![Jump Cut's title screen in Play mode on the Mac](../media/2026-11-12-mac-first-open-title.png)
