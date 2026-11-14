"""Point BP_Player's body at the remade SK_CafeWalkerV2 mesh.

Run headless:
    UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="<repo>/tools/unreal_player_body_v2.py [measure|swap]"
or through the editor console box:
    py <repo>/tools/unreal_player_body_v2.py [measure|swap]

Writes JumpCut/Saved/jcpy/player_body_v2.txt. `measure` touches nothing.

WHY THIS IS A ONE-PROPERTY CHANGE AND NOT A RETARGET.
SK_CafeWalkerV2 is the remade Meshy body RESKINNED onto the EXISTING 69-bone
SK_CafeWalker_Skeleton (issue #96), so every clip, montage and anim blueprint we own
still applies to it. BP_Player's name table references SK_CafeWalker, ABP_Unarmed_CWM and
five AM_CafeWalker_* montages; only the first of those has to move. Nothing is retargeted,
nothing is re-authored.

THE CHECKS, because "set the property" is not evidence:
  * the two meshes' skeletons are the same OBJECT, not merely the same path;
  * the component's anim_class is unchanged by the swap (that is the whole bet);
  * override_materials stays empty, so the mesh asset's own slot decides the look -
    an override is exactly what made the goons render flat (PR #105);
  * the V2 slot resolves to an MI whose parent is M_AnimeChar, by object identity;
  * the component's relative transform is unchanged, so he does not sink or float;
  * after `swap`, run `measure` again in a FRESH process - that is the only read that
    proves what reached disk rather than what is in this process's memory.
"""
import os
import sys
import traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), 'jcpy', 'player_body_v2.txt')

BP_CLASS = '/Game/Game/Blueprints/BP_Player.BP_Player_C'
COMP = 'CharacterMesh0'
V1 = '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker'
V2 = '/Game/Game/Imported/CafeWalkerV2/SK_CafeWalkerV2'
SKEL = '/Game/Game/Imported/CafeWalker/Meshy/SK_CafeWalker_Skeleton'
ANIME_CHAR = '/Game/Game/Materials/M_AnimeChar'

log = []


def say(s):
    log.append(str(s))
    unreal.log('[player-v2] %s' % s)


def flush():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')


def path_of(o):
    return o.get_path_name() if o else None


def probe(o, name):
    """get_editor_property that reports rather than raising, so one missing property
    does not take the whole measurement down."""
    try:
        return o.get_editor_property(name)
    except Exception as e:
        return 'ERR(%s)' % e


def describe_mesh(tag, path):
    m = unreal.load_asset(path)
    if m is None:
        say('%s MISSING %s' % (tag, path))
        return None
    skel = probe(m, 'skeleton')
    phys = probe(m, 'physics_asset')
    say('%s %s' % (tag, path))
    say('    skeleton      %s' % path_of(skel) if hasattr(skel, 'get_path_name') else '    skeleton      %s' % skel)
    say('    physics_asset %s' % (path_of(phys) if hasattr(phys, 'get_path_name') else phys))
    mats = probe(m, 'materials')
    if isinstance(mats, str):
        say('    materials     %s' % mats)
    else:
        for i, s in enumerate(mats):
            mi = s.get_editor_property('material_interface')
            slot = s.get_editor_property('material_slot_name')
            parent = None
            if isinstance(mi, unreal.MaterialInstance):
                parent = path_of(mi.get_editor_property('parent'))
            say('    slot[%d] %-16s %s   parent=%s' % (i, slot, path_of(mi), parent))
    try:
        b = m.get_bounds()
        o, e = b.origin, b.box_extent
        say('    bounds origin (%.2f, %.2f, %.2f) extent (%.2f, %.2f, %.2f)' % (o.x, o.y, o.z, e.x, e.y, e.z))
        say('    height %.2f cm   feet at z %.2f   head at z %.2f'
            % (e.z * 2.0, o.z - e.z, o.z + e.z))
    except Exception as e:
        say('    bounds        ERR(%s)' % e)
    return m


def get_comp():
    cls = unreal.load_object(None, BP_CLASS)
    if cls is None:
        say('REFUSING: could not load %s' % BP_CLASS)
        return None, None, None
    cdo = unreal.get_default_object(cls)
    for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
        if c.get_name() == COMP:
            return cls, cdo, c
    say('REFUSING: no component named %s on %s' % (COMP, BP_CLASS))
    say('    components present: %s'
        % [c.get_name() for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent)])
    return cls, cdo, None


def describe_comp(c, tag):
    mesh = probe(c, 'skeletal_mesh_asset')
    anim = probe(c, 'anim_class')
    ovr = probe(c, 'override_materials')
    loc = probe(c, 'relative_location')
    rot = probe(c, 'relative_rotation')
    scl = probe(c, 'relative_scale3d')
    say('%s BP_Player.%s' % (tag, COMP))
    say('    skeletal_mesh_asset %s' % (path_of(mesh) if hasattr(mesh, 'get_path_name') else mesh))
    if hasattr(mesh, 'get_path_name'):
        sk = probe(mesh, 'skeleton')
        say('      its skeleton      %s' % (path_of(sk) if hasattr(sk, 'get_path_name') else sk))
    say('    anim_class          %s' % (path_of(anim) if hasattr(anim, 'get_path_name') else anim))
    say('    override_materials  %s'
        % ([path_of(m) for m in ovr] if not isinstance(ovr, str) else ovr))
    for nm, v in (('relative_location', loc), ('relative_rotation', rot), ('relative_scale3d', scl)):
        try:
            say('    %-19s %s' % (nm, v))
        except Exception:
            say('    %-19s ?' % nm)
    return {'mesh': mesh, 'anim': anim, 'ovr': ovr, 'loc': loc, 'rot': rot, 'scl': scl}


def measure():
    say('=== the two bodies ===')
    m1 = describe_mesh('V1', V1)
    m2 = describe_mesh('V2', V2)
    skel = unreal.load_asset(SKEL)
    if m1 is not None and m2 is not None:
        s1 = probe(m1, 'skeleton')
        s2 = probe(m2, 'skeleton')
        same = (s1 is s2) and (s1 is skel)
        say('SKELETON IDENTITY: V1 is V2 is %s -> %s' % (SKEL.rsplit('/', 1)[-1], same))
        if not same:
            say('  V1 skeleton %s' % path_of(s1) if hasattr(s1, 'get_path_name') else s1)
            say('  V2 skeleton %s' % path_of(s2) if hasattr(s2, 'get_path_name') else s2)
    say('')
    say('=== BP_Player as it stands ===')
    cls, cdo, c = get_comp()
    if c is None:
        return None
    return describe_comp(c, 'NOW')


def swap():
    before = measure()
    if before is None:
        return
    say('')
    cls, cdo, c = get_comp()
    v2 = unreal.load_asset(V2)
    if v2 is None:
        say('REFUSING: %s is missing' % V2)
        return
    s2 = probe(v2, 'skeleton')
    if s2 is not unreal.load_asset(SKEL):
        say('REFUSING: V2 is not on %s - swapping would break every clip' % SKEL)
        return
    if c.get_editor_property('skeletal_mesh_asset') is v2:
        say('ALREADY on V2 - nothing to do')
        return

    say('=== setting skeletal_mesh_asset -> %s ===' % V2)
    try:
        c.set_editor_property('skeletal_mesh_asset', v2)
    except Exception as e:
        say('set_editor_property failed (%s); trying set_skeletal_mesh_asset' % e)
        c.set_skeletal_mesh_asset(v2)

    after = describe_comp(c, 'AFTER')

    ok = True
    if after['mesh'] is not v2:
        say('FAIL: the property did not take'); ok = False
    if path_of(after['anim']) != path_of(before['anim']):
        say('FAIL: anim_class changed %s -> %s'
            % (path_of(before['anim']), path_of(after['anim']))); ok = False
    if not isinstance(after['ovr'], str) and len(after['ovr']) != 0:
        say('FAIL: override_materials is not empty - the mesh slot will be ignored'); ok = False
    for nm in ('loc', 'rot', 'scl'):
        if str(before[nm]) != str(after[nm]):
            say('FAIL: %s changed %s -> %s' % (nm, before[nm], after[nm])); ok = False
    mats = probe(v2, 'materials')
    if not isinstance(mats, str):
        for s in mats:
            mi = s.get_editor_property('material_interface')
            if not isinstance(mi, unreal.MaterialInstance):
                say('FAIL: slot %s is not a material instance (%s)'
                    % (s.get_editor_property('material_slot_name'), path_of(mi))); ok = False
            elif mi.get_editor_property('parent') is not unreal.load_asset(ANIME_CHAR):
                say('FAIL: slot %s parent is %s, not M_AnimeChar'
                    % (s.get_editor_property('material_slot_name'),
                       path_of(mi.get_editor_property('parent')))); ok = False
    if not ok:
        say('NOT SAVING - a check failed above')
        return

    pkg = cls.get_outermost()
    saved = unreal.EditorLoadingAndSavingUtils.save_packages([pkg], False)
    say('SAVED %s ok=%s' % (pkg.get_name(), saved))
    say('Now run this script again with `measure` in a FRESH process - that is the only')
    say('read that proves what reached disk.')


mode = sys.argv[1] if len(sys.argv) > 1 else 'measure'
try:
    say('MODE %s' % mode)
    if mode == 'swap':
        swap()
    else:
        measure()
except Exception:
    say('EXCEPTION')
    say(traceback.format_exc())
flush()
