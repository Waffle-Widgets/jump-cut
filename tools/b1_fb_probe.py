"""Read-only probe for the Nov 14 feedback pass on beat 1. Writes Saved/jcpy/b1_fb_probe.txt."""
import unreal, os, json

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
L = []
def say(s): L.append(str(s))

try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    say('world=%s  pie=%s' % (ues.get_editor_world().get_name(), ues.get_game_world() is not None))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # ---------- 1. the sequence ----------
    seq = None if True else unreal.load_asset('/Game/Game/Cinematics/LS_Beat1_Opening')
    say('\n=== LS_Beat1_Opening ===')
    if seq:
        dr = seq.get_display_rate()
        tr = seq.get_tick_resolution()
        say('display_rate=%s/%s tick_res=%s/%s playback=%s..%s' % (
            dr.numerator, dr.denominator, tr.numerator, tr.denominator,
            seq.get_playback_start(), seq.get_playback_end()))
        fps = float(dr.numerator) / float(dr.denominator)
        for b in seq.get_bindings():
            say('\n  BINDING %-28s id=%s  spawnable=%s' % (b.get_name(), b.get_id(), b.get_object_template() is not None))
            tmpl = b.get_object_template()
            if tmpl:
                say('    template class=%s' % tmpl.get_class().get_name())
            for t in b.get_tracks():
              try:
                say('    TRACK %s' % t.get_class().get_name())
                try:
                    say('      prop=%s' % t.get_property_name())
                except Exception:
                    pass
                for s in t.get_sections():
                    try:
                        sf, ef = s.get_start_frame(), s.get_end_frame()
                        say('      SECTION %s  range %s..%s (%.2fs..%.2fs)' % (
                            s.get_class().get_name(), sf, ef, sf / fps, ef / fps))
                    except Exception as e:
                        say('      SECTION %s  (no frame range: %s)' % (s.get_class().get_name(), e))
                    try:
                        for ch in s.get_all_channels():
                            ks = ch.get_keys()
                            if not ks:
                                continue
                            rows = []
                            for k in ks:
                                t0 = k.get_time()
                                fr = t0.frame_number.value if hasattr(t0, 'frame_number') else t0
                                try:
                                    v = k.get_value()
                                except Exception:
                                    v = '?'
                                rows.append('%s=%s' % (fr, round(v, 2) if isinstance(v, float) else v))
                            say('        CH %-24s %s' % (ch.get_name(), ' '.join(rows)))
                    except Exception as e:
                        say('        (channels: %s)' % e)
              except Exception as e:
                say('    (track failed: %s)' % e)
        say('\n  master tracks:')
        for t in seq.get_tracks():
            say('    %s' % t.get_class().get_name())
            for s in t.get_sections():
                say('      %s %s..%s' % (s.get_class().get_name(), s.get_start_frame(), s.get_end_frame()))
    else:
        say('  (skipped this pass)')

    # ---------- 2. blueprint defaults ----------
    def dump_bp(path):
        say('\n=== %s ===' % path)
        bp = unreal.load_asset(path)
        if bp is None:
            say('  MISSING'); return
        cls = bp.generated_class()
        cdo = unreal.get_default_object(cls)
        try:
            parent = bp.get_editor_property('parent_class')
            base = set(dir(unreal.get_default_object(parent)))
        except Exception as e:
            say('  (no parent: %s)' % e); base = set()
        own = sorted(n for n in dir(cdo) if not n.startswith('_') and n not in base)
        for n in own:
            try:
                v = cdo.get_editor_property(n)
            except Exception:
                continue
            if callable(v):
                continue
            say('  %-34s = %s' % (n, v))
        say('  (%d own properties)' % len(own))

    dump_bp('/Game/Game/Blueprints/BP_OpeningDirector')
    dump_bp('/Game/Game/Blueprints/BP_Coworker')

    # ---------- 3. the level actors that matter ----------
    say('\n=== level actors: markers, beacon, wreck, driver, fire ===')
    want = ('marker', 'beacon', 'crash', 'driver', 'fire', 'blast', 'wreck', 'car', 'patch', 'coworker', 'director', 'sequence')
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        cls = a.get_class().get_name()
        if not any(w in lab.lower() for w in want) and not any(w in cls.lower() for w in want):
            continue
        mesh = ''
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            m = c.get_editor_property('static_mesh')
            mesh += ' mesh=%s' % (m.get_name() if m else None)
        say('  %-26s %-28s loc=%s scale=%s hidden=%s tags=%s%s' % (
            lab, cls, a.get_actor_location(), a.get_actor_scale3d(),
            a.get_editor_property('hidden'), [str(t) for t in a.get_editor_property('tags')], mesh))

    # ---------- 4. HUD widget ----------
    say('\n=== WBP_HUD tree ===')
    w = unreal.load_asset('/Game/Game/UI/WBP_HUD')
    if w:
        try:
            tree = w.get_editor_property('widget_tree')
            root = tree.get_editor_property('root_widget')
            def walk(x, d=0):
                if x is None: return
                say('  %s%s (%s)' % ('  ' * d, x.get_name(), x.get_class().get_name()))
                try:
                    for c in x.get_all_children():
                        walk(c, d + 1)
                except Exception:
                    pass
            walk(root)
        except Exception as e:
            say('  %s' % e)
    else:
        say('  MISSING')
except Exception as e:
    import traceback
    say('FAILED: %s' % e); say(traceback.format_exc())

open(os.path.join(OUT, 'b1_fb_probe.txt'), 'w').write('\n'.join(L))
print('\n'.join(L[:5]))
print('WROTE %s' % os.path.join(OUT, 'b1_fb_probe.txt'))
