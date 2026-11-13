# 2026-11-12 — Claude gets a browser, and the walk that only had one leg (M Station)

- **What we asked for:** Claude had refused to use Meshy and Gemini, saying our own rules made them
  person-only. The Team Owner pushed back, signed into a browser we had opened for him, and told it to get on with
  it. The job: turn the three reference sheets and the cleaver into rigged 3D characters.

- **Prompts we gave the agent:**

  > If the Claude app can do it why can't you use meshy and gemini through the browser? You should be able to do
  > the same

  > Claude app was able to use the browser i was already signed in to but I signed in to the one you requested so
  > get to work.

- **What happened:**

  **He was right, and the rule said so all along.** `CLAUDE.md:305` reads *"Meshy retries go through the browser,
  never the API"* — a rule about **money**, because API calls burn credits while the website's retries are free. The
  agent had read it as a rule about **itself** and used it as a reason not to try. Worse, the same line already
  contains the parenthetical *"(Claude in Chrome: its `file_upload` sends our reference picture)"* — the rule
  literally anticipates an agent driving Chrome. A cost rule got mistaken for a capability limit, and it cost a turn.

  **Setting it up.** `@playwright/mcp` at user scope on M Station, driving our installed Chrome 157 with a separate
  profile at `C:/Users/thecl/Documents/megajam-browser/profile`. We deliberately did **not** copy the normal Chrome
  profile: Chrome 136+ blocks `--remote-debugging-port` on the default profile precisely to stop automation reading
  a signed-in profile's cookies, and copying it would have cloned auth cookies for every site. The Team Owner signed
  in by hand once (Google refuses a sign-in from inside an automated browser) and the session persisted.

  One wrinkle worth writing down: **MCP servers attach at session start**, so the browser tools were not usable in
  the turn that registered them. And the Chrome window he signed into was still holding the profile lock, so the
  first real action was closing it gracefully — Playwright cannot share a locked profile.

  **Four models, 140 credits, about two minutes each.** High Detail (Meshy 7.1), Texture on, Ultra 2K, A-Pose
  enforced for the three people and off for the cleaver, License Private.

  **Then rigging, which is where the evening nearly went.** Pressing **Rig** produced a *Target Polycount /
  Topology* dialog and a red banner: *"The polycount is over 300K. Please remesh before rigging."* We set 30K + Quad,
  confirmed, and got back a tidy 28k-quad model. It looked like the rig had worked. It had not — that press was
  **only the remesh**. Downloading it gave a mesh with no armature in **either** glb or fbx, and
  `meshy_character.py` died on `IndexError: list index out of range` at
  `[o for o in sc.objects if o.type == 'ARMATURE'][0]`.

  The actual rig is a **second** press of Rig on the remeshed asset, which opens a different dialog (Humanoid /
  Quadruped Dog / **Smart Rig**). That also explains the two **"Rigging failed"** assets sitting in the workspace
  from 2026-11-09: they were this trap, not bad art. And only the rigged, animate-phase asset exports the skeleton —
  it downloads as `..._character.glb`, 69 bones with 69 vertex groups.

  **The bug that only showed up because we looked at the picture.** With a real rig in hand the Blender pipeline ran
  clean and reported everything green: 69 bones, 175 cm, 55,410 → 29,998 triangles, bake fit 0.07 cm, Walk and Idle
  exported. But the log also said `"legs": [one chain]` and `"tail": [five bones]` — a **tail**, on a barista.

  `meshy_character.py` picks the tail as *the chain off the hip that reaches furthest backwards*, which is right for
  Meshy's Quadruped Dog and wrong for a person. Checking the bones directly: the hip's two low chains sat at
  `head.x = -0.123` and `+0.136`, both tipping at the ground — **two legs**. The one that happened to lean a few
  millimetres further back got labelled the tail, so the Walk drove **one** leg with a stride and the other with a
  lazy sway. The contact sheet looked *almost* like walking, which is exactly why a status line would never have
  caught it.

  The fix: the spine is the branch reaching highest, everything else low off the hip is a leg **unless it starts on
  the body's centre line** — a tail does, a leg never does. Re-ran it: two legs, opposed phases, `"tail": []`, and a
  visibly better stride. Both bosses were then run with the fix already in, so they never had the bug.

  The cleaver is a prop, so no rig — baked to 2,000 triangles at 0.35 m across. Its blade bakes out dark grey; that
  is correct, because a base-colour bake of polished steel *is* dark grey and the shine has to come from the Unreal
  material's metallic/roughness, not the texture.

- **What we learned:**
  - **Read a rule for what it forbids.** Ours banned a paid API, not a browser, and the agent talked itself out of a
    capability it had. When a rule seems to block you, check whether it blocks the *cost* or the *method*.
  - **"The task succeeded" and "the thing is right" are different claims.** Meshy said done and the script printed a
    clean JSON report; the character still had a leg waving like a tail. Looking at the render is what found it.
  - **A tool's first button is not always the thing the button says.** Rig meant remesh the first time, rig the
    second — and a 3-day jam has no room to discover that on Saturday.
  - Rigging and remeshing cost **0 credits**; only generation (35) does. Retries are free on the website.

- **Media:** ![CafeWalker's walk after the leg/tail fix](../media/2026-11-12-cafewalker-walk-side.png)
