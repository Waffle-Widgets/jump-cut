# Street model reference pictures (Sun Nov 15, M Station)

Drawn in Gemini (Create image, one new chat per picture, first take kept for all five), then sent to Meshy
Image to 3D: High Detail, Meshy 7.1, Ultra 2K, texture 2K, Pose off, License Private, 35 credits each.

Every prompt is its own description followed by the same style block.

**Style block (appended to all five):**

> Drawn as a clean 3D game-asset concept render in a stylised anime background-art style: simple confident
> shapes, flat hand-painted colours with one soft shadow tone, crisp edges, no photographic noise. The WHOLE
> object is in frame with margin on every side, seen from a three-quarter front view slightly above eye level,
> centred on a plain pure white background. Soft even studio light, no cast shadow on the ground, no
> reflections, no people, no text, no lettering, no logos, no brand badges, no watermark.

**SakuraTree_ref.jpg**

> A single cherry blossom (sakura) street tree in full bloom, about four metres tall. A thick, dark brown
> gnarled trunk that leans slightly and splits at head height into four or five sturdy spreading branches. The
> canopy is big chunky rounded clumps of blossom in pale pink and deeper rose pink, with clear gaps between the
> clumps where the dark branches show through, wider than it is tall. A small square cast-iron tree grate at the
> foot of the trunk. No falling petals in the air.

**KeiVan_ref.jpg**

> A small Japanese kei delivery van, the one-box microvan kind about 3.3 metres long: tall, narrow, flat snub
> nose, sliding side door, small wheels tucked into round arches. Cream white body with a single teal band along
> the lower side, dark grey bumpers, round headlamps, roof rack with two bars. Dark tinted glass that is opaque.
> A generic invented design that is not any real make or model, with a blank grille and blank number plates.

**Hatchback_ref.jpg**

> A small boxy 1990s-style Japanese city hatchback car, three doors, about 3.6 metres long, friendly and a
> little worn. Faded tomato red paint, black plastic bumpers, square headlamps, steel wheels with plain silver
> hubcaps, a short roof aerial. Dark tinted glass that is opaque. A generic invented design that is not any real
> make or model, with a blank grille and blank number plates.

**Bicycle_ref.jpg**

> A Japanese city bicycle of the everyday "mamachari" kind, parked upright on its double kickstand. Step-through
> curved frame in mint green, a woven wire front basket, swept-back handlebars with a small bell, a wide brown
> saddle, full silver mudguards, a rear carrier rack, a chain guard, and chunky tyres with clearly drawn thick
> spokes. Seen from the side and slightly to the front so both wheels are fully visible.

**Scooter_ref.jpg**

> A small Japanese delivery scooter parked on its centre stand, about 1.8 metres long. Rounded front leg shield
> and round headlamp, flat footboard, long black seat, a square insulated delivery box on the rear carrier,
> small chunky wheels. Body in warm orange-red with a cream front panel, the delivery box plain cream with no
> markings. A generic invented design that is not any real make or model.

## The bake (one line each, from the repo root)

    blender -b --factory-startup --python Art/Blender/meshy_prop_bake.py -- Art/Meshy/_raw/<Raw>.glb <Name> <size_m> <mode> <tris>

| Name | Raw | size, mode | tris | env |
|---|---|---|---|---|
| SakuraTree | SakuraTree.glb | 4.2 height | 22000 | `PROP_PRESCALE=0.764,1.36,1 PROP_CAGE=0.012` |
| KeiVanM | KeiVan.glb | 3.3 width | 10000 | `PROP_YAW=180` |
| Hatchback | Hatchback.glb | 3.1 width | 10000 | `PROP_YAW=180` |
| BicycleM | Bicycle.glb | 1.75 width | 12000 | `PROP_YAW=180 PROP_CAGE=0.03 PROP_TEXEL=0.002` |
| ScooterM | Scooter.glb | 1.75 width | 9000 | `PROP_YAW=180 PROP_TEXEL=0.003` |

The raw downloads (20-46 MB each, 450k-1.3M triangles) are gitignored (`Art/Meshy/_raw/`); Meshy keeps them
three days.

## Second batch (2:00 PM the same day): 13 street and cafe props

Prompts: `prompts_batch2.json` in this folder (`_style` is appended to each). The style block gained "no writing
in any language, no numbers". Same Meshy settings. Three pictures here are Gemini's full-size files
(VendingMachine, StreetLamp, Planter); the other ten are the 1024-pixel copy shown on the page, because the
download button stopped working - see the devlog entry. `GasBottles` was generated and dropped.

| Name | size, mode | tris | env |
|---|---|---|---|
| VendingMachineM | 1.90 height | 8000 | `PROP_TEXEL=0.003 PROP_BACK=0.43` |
| StreetLampM | 5.96 height | 6000 | `PROP_TEXEL=0.003 PROP_ORIGIN=base PROP_ARM=180` |
| PlanterM | 1.20 width | 8000 | `PROP_TEXEL=0.003 PROP_BACK=0.25` |
| PotRowM | 1.99 width | 10000 | `PROP_TEXEL=0.002 PROP_BACK=0.262 PROP_SHIFT_X=-0.239` |
| DumpsterM | 1.62 width | 6000 | `PROP_TEXEL=0.003 PROP_BACK=0.495` |
| AFrameSignM | 0.98 height | 3000 | `PROP_TEXEL=0.001 PROP_YAW=90` |
| BenchM | 1.80 width | 8000 | `PROP_TEXEL=0.002 PROP_BACK=0.25` |
| CafeEspressoM | 0.80 width | 8000 | `PROP_TEXEL=0.001` |
| CafeRegisterM | 0.37 height | 5000 | `PROP_TEXEL=0.001` |
| CafePastryCaseM | 1.20 width | 8000 | `PROP_TEXEL=0.001` |
| CafePlantTallM | 1.31 height | 8000 | `PROP_TEXEL=0.002` |
| CafePlantSmallM | 0.22 height | 3000 | `PROP_TEXEL=0.001` |
| CafeStoolM | 0.75 height | 4000 | `PROP_TEXEL=0.001` |
