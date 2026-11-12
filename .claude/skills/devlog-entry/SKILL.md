---
name: devlog-entry
description: Write the Glass Box devlog entry as a new file in docs/devlog/ for a change the user tested, with a screenshot, and commit it together with the change. Use after every tested change, and whenever something broke or a setup problem was solved.
---

# Devlog entry (Glass Box prize)

The Glass Box prize is for the best devlog showing *how* we built the game, so the honest parts (failures, retries,
dead ends) are worth the most. Write one entry per tested change without being asked.

## Steps
1. **Only after the user confirmed it works** in Play mode (or confirmed a non-game change is fine).
2. Save all assets in the editor. If Unreal is open, capture a picture (`playtest-capture` skill) into
   `docs/media/<short-name>.png`.
3. Add a **new file** `docs/devlog/YYYY-MM-DD-what-happened.md` (naming rules: `docs/devlog/README.md`). Never
   append to another entry or to `docs/DEVLOG.md`. Use the template:

```
# YYYY-MM-DD — short title (which PC, if it matters)
- **What we asked for:** in plain words
- **Prompt(s) we gave the agent:** the user's actual words, quoted
- **What happened:**
  - what was built, where it lives in the Content Browser or repo
  - every failure, wrong guess, retry and what fixed it
- **What we learned:** one or two lessons someone else could use
- **Media:** ![what it shows](../media/<file>.png)
```

4. Plain language: the readers are judges and beginners, not engineers. Say what the player sees.
5. If the lesson changes how we should work, also suggest adding it to `CLAUDE.md` (or the matching skill).
6. Commit the change and the entry together: `git pull --rebase` first, a short plain message, no `.uasset` from a
   PC that doesn't own Unreal. Tell the user what was committed.
