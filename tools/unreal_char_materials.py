"""Put every character on M_AnimeChar, so the cel look treats them all the same way.

Run through the editor console box:  py <repo>/tools/unreal_char_materials.py [measure|fix]
Writes JumpCut/Saved/jcpy/char_materials.txt

WHY. Six character skeletal meshes are in the project. Three of them (CrashDriver,
CleaverBoss, and the player via MI_CafeWalker) are on MI_* instances whose parent is
M_AnimeChar - our own character material, a straight BaseColor-from-texture feed that
the MI_AnimeLook post-process then bands. The other three - SK_StreetGoon,
SK_CafeCoworker and the Meshy SK_CafeWalker - are still on the material Interchange
invented for them at FBX import time, sitting inside their own import folder. That is
why the goons render as flat untextured silhouettes while the player beside them is
correctly textured: their committed texture is fine and nothing is sampling it.

WHERE THE FIX GOES. On the SkeletalMesh ASSET's material slot, not on an actor's
override_materials. The goons are SPAWNED AT RUNTIME by BP_GoonSpawner, so there is no
placed actor to override - CrashDriver and CleaverBoss get away with actor overrides
only because they are hand-placed. Setting the asset slot covers every instance,
placed or spawned.
"""
import os, sys, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'char_materials.txt')
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
ANIME_CHAR = '/Game/Game/Materials/M_AnimeChar'
MAT_DIR = '/Game/Game/Materials'

# mesh -> (instance name, base colour texture). The texture is the one committed beside
# the mesh in its own import folder, so a remade character brings its own.
PLAN = [
    ('/Game/Game/Imported/StreetGoon/Meshy/SK_StreetGoon',
     'MI_StreetGoon', '/Game/Game/Imported/StreetGoon/Meshy/T_StreetGoon_BaseColor'),
    ('/Game/Game/Imported/CafeCoworker/SK/SK_CafeCoworker',
     'MI_CafeCoworker', '/Game/Game/Imported/CafeCoworker/Tex/T_CafeCoworker_BaseColor'),
    ('/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker',
     'MI_CafeWalker_Meshy', '/Game/Game/Imported/CafeWalker/Meshy/T_CafeWalker_BaseColor'),
]


def flush():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def describe(path):
    a = unreal.load_asset(path)
    if a is None:
        return 'MISSING'
    if isinstance(a, unreal.MaterialInstanceConstant):
        p = a.get_editor_property('parent')
        return 'MI parent=%s' % (p.get_path_name() if p else None)
    return type(a).__name__


def measure():
    P('=== every character skeletal mesh, slot by slot ===')
    for folder in ['/Game/Game/Imported']:
        for p in sorted(eal.list_assets(folder, recursive=True, include_folder=False)):
            a = unreal.load_asset(p)
            if not isinstance(a, unreal.SkeletalMesh):
                continue
            P('  %s' % p)
            for i, m in enumerate(a.get_editor_property('materials')):
                mi = m.get_editor_property('material_interface')
                mp = mi.get_path_name().split('.')[0] if mi else None
                P('    slot %d  %-22s -> %-58s  %s' % (
                    i, str(m.get_editor_property('material_slot_name')), mp,
                    describe(mp) if mp else ''))


def fix():
    changed = []
    for mesh_path, mi_name, tex_path in PLAN:
        mesh = unreal.load_asset(mesh_path)
        if mesh is None:
            P('SKIP  mesh missing: %s' % mesh_path)
            continue
        tex = unreal.load_asset(tex_path)
        if tex is None:
            P('SKIP  texture missing: %s' % tex_path)
            continue
        mi_path = '%s/%s' % (MAT_DIR, mi_name)
        mi = unreal.load_asset(mi_path)
        if mi is None:
            at = unreal.AssetToolsHelpers.get_asset_tools()
            mi = at.create_asset(mi_name, MAT_DIR, unreal.MaterialInstanceConstant,
                                 unreal.MaterialInstanceConstantFactoryNew())
            P('CREATED %s' % mi_path)
        parent = unreal.load_asset(ANIME_CHAR)
        mel.set_material_instance_parent(mi, parent)
        mel.set_material_instance_texture_parameter_value(mi, 'Tex', tex)
        changed.append(mi)
        P('SET     %s  parent=M_AnimeChar  Tex=%s' % (mi_path, tex_path))

        mats = mesh.get_editor_property('materials')
        newmats = []
        for m in mats:
            nm = unreal.SkeletalMaterial()
            nm.set_editor_property('material_interface', mi)
            nm.set_editor_property('material_slot_name', m.get_editor_property('material_slot_name'))
            try:
                nm.set_editor_property('uv_channel_data', m.get_editor_property('uv_channel_data'))
            except Exception:
                pass
            newmats.append(nm)
        mesh.set_editor_property('materials', newmats)
        changed.append(mesh)
        P('ASSIGNED %s  slot(s) -> %s' % (mesh_path, mi_name))

    pkgs = []
    for a in changed:
        pk = a.get_outermost()
        if pk not in pkgs:
            pkgs.append(pk)
    # LFS read-only trap: a committed .uasset cannot be written until the flag is cleared.
    for pk in pkgs:
        fn = unreal.SystemLibrary.get_system_path(pk) or ''
        if fn and os.path.exists(fn) and not os.access(fn, os.W_OK):
            P('READONLY (needs attrib -r / lfs unlock): %s' % fn)
    ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
    P('SAVED %d packages ok=%s' % (len(pkgs), ok))
    for pk in pkgs:
        P('   %s' % pk.get_name())


BP_OVERRIDES = [
    # Blueprint, component, the MI its mesh should wear (None = clear the override and
    # let the mesh asset's own slot decide)
    ('/Game/Game/Blueprints/BP_Goon.BP_Goon_C', 'CharacterMesh0', '/Game/Game/Materials/MI_StreetGoon'),
]


def goon_override():
    """BP_Goon's CharacterMesh0 carries override_materials = [M_Goon] - a flat colour
    material left over from the grey-box build. An override beats the mesh asset's own
    slot, so the goon's correct 2048 texture is bound, sampled by correct UVs, and then
    thrown away. The player has no override, which is why he looks right beside them."""
    pkgs = []
    for cls_path, comp_name, mi_path in BP_OVERRIDES:
        cls = unreal.load_object(None, cls_path)
        cdo = unreal.get_default_object(cls)
        for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
            if c.get_name() != comp_name:
                continue
            was = [m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]
            mi = unreal.load_asset(mi_path) if mi_path else None
            c.set_editor_property('override_materials', [mi] if mi else [])
            now = [m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]
            P('BP %s.%s override_materials %s -> %s' % (cls_path.rsplit('/', 1)[-1], comp_name, was, now))
            pk = cls.get_outermost()
            if pk not in pkgs:
                pkgs.append(pk)
    if pkgs:
        ok = unreal.EditorLoadingAndSavingUtils.save_packages(pkgs, False)
        P('SAVED blueprint packages %s ok=%s' % ([p.get_name() for p in pkgs], ok))


def report_placeholders():
    P('')
    P('=== the placeholder colour materials from the grey-box build ===')
    for n in ('M_Goon', 'M_Boss', 'M_PropRed', 'M_PropBlue', 'M_GreyWall', 'M_GreyFloor'):
        a = unreal.load_asset('%s/%s' % (MAT_DIR, n))
        if a is None:
            continue
        try:
            c = a.get_base_color()
        except Exception:
            c = None
        P('  %-12s expressions=%d  %s' % (n, mel.get_num_material_expressions(a), c))


mode = sys.argv[1] if len(sys.argv) > 1 else 'measure'
try:
    P('MODE %s' % mode)
    if mode == 'fix':
        fix()
        goon_override()
        P('')
    report_placeholders()
    measure()
except Exception:
    P('EXCEPTION')
    P(traceback.format_exc())
flush()
