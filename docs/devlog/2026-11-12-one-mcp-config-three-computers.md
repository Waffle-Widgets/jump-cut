# 2026-11-12 — One MCP config, three computers

- **What we asked for:** "are you able to control UE and Blender with MCP like the Claude desktop app can?", then
  "usually we can just use the /mcp command to connect", "how do we restart all of the chats for this project in that
  directory?", "what if the path is different per computer we are working on?", and finally "I'm fine with either fix
  as long as it works on all of our machines".
- **What happened:** The honest answer to the first question was "yes, but not in this chat" — the session had started
  in `Documents`, and MCP servers are read from config when a session starts, so neither server was loaded. `/mcp`
  doesn't rescue that: it lists and re-authenticates servers a session *already* loaded, it can't attach a new one.
  Digging into why led to the real bug. Our committed `.mcp.json` hardcoded `C:\blender_mcp\mcp`, so on Justin's Mac
  that server could never start — and our own `CLAUDE.md` already said "never put a Mac path in the shared
  `.mcp.json`... no `C:\` paths in anything shared". We were breaking our own rule, in the file the rule was about.
- **What we learned:** the fix is a split, not a clever path. Shared `.mcp.json` now holds only `unreal`, because
  `127.0.0.1:8000` means "this machine's editor" on every OS. Blender's server needs a real folder, and folders differ
  per computer, so each machine registers it at **user scope** via a new `tools/setup_mcp.ps1` / `setup_mcp.sh`.
  Three things we got for free or nearly lost:
  - We nearly shipped `${BLENDER_MCP_DIR:-C:/blender_mcp/mcp}` in the committed file instead. The CLI's headless auth
    on this PC is expired, so we could not actually prove the `:-default` half expands at launch — `claude mcp list`
    printed it back as a bare `${BLENDER_MCP_DIR}` either way. An unverified mechanism that fails silently is the
    worst thing to put in a jam repo, so we used the one we could test end to end.
  - User scope also fixed the thing we started with: servers now load in **whatever folder a chat opens in**, so a
    chat that lands in `Documents` still gets Unreal. `claude mcp list` from `Documents`: both ✔ Connected.
  - `uvx blender-mcp` looks like a tidy path-free install and is a trap. The `blender-mcp` name on PyPI belongs to a
    different, third-party project; ours is Blender's own at `projects.blender.org/lab/blender_mcp.git`.
- Two PowerShell traps, both found by running the script rather than reading it: PowerShell 5.1 **swallows a bare
  `--`**, so `claude mcp add blender -s user -- uv ...` fails with `unknown option '--directory'` and the `--` has to
  be quoted; and `claude mcp remove` writes to stderr when the server isn't there, which under
  `$ErrorActionPreference = 'Stop'` is fatal and kills an idempotent remove-then-add.
- One more thing worth saying plainly: `blender: ✔ Connected` only means the bridge process started. Blender itself
  wasn't running and nothing was listening on 9876, so any Blender tool call would have connected and then failed.
  A green tick is not a working tool.
- `tools/bootstrap/new_jam_repo.ps1` was generating the broken `.mcp.json` too, so it was fixed in the same pass —
  otherwise the next repo we make brings the bug back.
