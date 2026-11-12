# Reference-picture prompts

Prompts for `tools/gen_images.py`, which draws them on M Station's graphics card (ComfyUI + Qwen-Image, nothing
goes online). Run one by its code:

    python tools/gen_images.py MC-APOSE --takes 3 --size 1024x1536

Takes land in `Art/Refs/gen/CODE-N.png`, which git ignores. Copy the one we pick to `Art/Refs/<name>_apose.png`
and commit that, so the picture a 3D model was made from is in the repo next to the model.

**What the A-pose prompts are for.** They are the input picture for Meshy (image-to-3D), so they follow
`CLAUDE.md`: full body, plain white background, A-pose with clear gaps between the arms and the body. A pose with
the arms against the torso gives a 3D model with the arms fused to the chest.

**The look.** Cel-shaded anime, because that is the only style with a tested path in this repo (the cel-shader
demo on `mendezm87/anime-look` and the `CafeWalker` model). `ROADMAP.md` still lists the art style under
"Still to decide" — these are drawn in the leading candidate, not in a chosen one.

**Rules note.** No trademarks or logos, nothing above 13+ (`docs/RULES.md`). For the mob boss that means an
invented crest or none at all, never a real family crest, and a clean blade — no blood.

---

### MC-APOSE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a young
> adult man standing straight in an A-pose, arms angled down and away from his sides with clear empty space between
> each arm and his torso, palms open, legs apart, facing the viewer, short messy black hair, calm tired face, a
> cream long-sleeve shirt with the sleeves pushed up, a dark green canvas apron tied at the waist, charcoal work
> trousers, scuffed grey sneakers, a folded cloth hanging from the apron tie, flat plain white background, even
> front lighting, no ground shadow

### BOSS1-APOSE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a lean
> man in his forties standing straight in an A-pose, arms angled down and away from his sides with clear empty
> space between each arm and his torso, legs apart, facing the viewer, a cracked open-face motorcycle helmet pushed
> back on his head, frosted goggles resting on the brim, a battered brown leather racing jacket with pale frost
> creeping across one shoulder, a torn dark scarf, worn leather driving gloves, dark trousers, heavy boots, flat
> plain white background, even front lighting, no ground shadow

### BOSS2-APOSE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a broad
> heavyset older man standing straight in an A-pose, arms angled down and away from his sides with clear empty
> space between each arm and his torso, legs apart, facing the viewer, slicked back grey hair, a hard scarred
> face, a sharply tailored charcoal double-breasted suit worn open over a deep magenta shirt with no tie, a plain
> geometric diamond pin on the lapel, stylised wave tattoos on the backs of his hands, holding a heavy clean
> steel cleaver point down in his right hand, flat plain white background, even front lighting, no ground shadow

### BOSS2-NOBLADE
> anime character reference sheet, cel shaded with hard-edged shadows and clean dark line art, full body, a broad
> heavyset older man standing straight in an A-pose, both arms angled down and well away from his sides with a wide
> empty gap between each arm and his torso, both hands empty and open with the fingers spread, legs apart, facing
> the viewer, slicked back grey hair, a hard scarred face, a sharply tailored charcoal double-breasted suit worn
> open over a deep magenta shirt, a plain geometric diamond pin on the lapel, stylised wave tattoos on the backs
> of his hands, flat plain white background, even front lighting, no ground shadow

### CLEAVER-PROP
> a single heavy steel meat cleaver lying flat and seen straight from the side, filling the frame, clean polished
> blade with a dark wooden handle and three rivets, one round hole near the top corner of the blade, cel shaded
> with hard-edged shadows and a clean dark outline, flat plain white background, even lighting, no ground shadow,
> nothing else in the picture
