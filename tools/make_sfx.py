"""Generates the game's sound effects and music as WAV files, using only the Python standard library.

Everything here is synthesized from scratch (sine/square waves and noise), so the sounds are ours
and need no CREDITS.md entry. Run: python tools/make_sfx.py <output folder>
"""
import math
import os
import random
import struct
import sys
import wave

RATE = 44100
random.seed(7)


def write(path, samples):
    peak = max(1e-9, max(abs(s) for s in samples))
    scale = 0.85 / peak if peak > 0.85 else 1.0
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s * scale)) * 32767)) for s in samples))


def env(i, n, attack=0.005, release=None):
    t = i / RATE
    a = min(1.0, t / attack) if attack > 0 else 1.0
    r = 1.0 - i / n if release is None else max(0.0, 1.0 - max(0, i - (n - release * RATE)) / (release * RATE))
    return a * r


def tone(freq_fn, dur, wave_fn=math.sin, vol=1.0, attack=0.005, decay_pow=1.0):
    n = int(dur * RATE)
    out, phase = [], 0.0
    for i in range(n):
        phase += 2 * math.pi * freq_fn(i / n) / RATE
        out.append(wave_fn(phase) * vol * env(i, n, attack) ** decay_pow)
    return out


def square(p):
    return 1.0 if math.sin(p) >= 0 else -1.0


def tri(p):
    return 2 / math.pi * math.asin(math.sin(p))


def noise(dur, vol=1.0, lowpass=0.2, decay_pow=1.0):
    n = int(dur * RATE)
    out, y = [], 0.0
    for i in range(n):
        y += lowpass * (random.uniform(-1, 1) - y)
        out.append(y * vol * env(i, n, 0.002) ** decay_pow)
    return out


def mix(*tracks):
    n = max(len(t) for t in tracks)
    return [sum(t[i] for t in tracks if i < len(t)) for i in range(n)]


def seq(*parts):
    out = []
    for p in parts:
        out += p
    return out


def silence(dur):
    return [0.0] * int(dur * RATE)


def note(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def make_all(folder):
    os.makedirs(folder, exist_ok=True)
    # quick rising "boing" for each hop
    write(os.path.join(folder, "SFX_Hop.wav"),
          tone(lambda x: 380 + 520 * x, 0.11, lambda p: 0.7 * math.sin(p) + 0.3 * tri(p), 0.8, decay_pow=1.5))
    # soft thump on landing
    write(os.path.join(folder, "SFX_Land.wav"),
          mix(tone(lambda x: 140 - 60 * x, 0.08, math.sin, 0.9, decay_pow=2.0), noise(0.05, 0.25, 0.1, 2.0)))
    # car squash: crunchy noise + descending squeak
    write(os.path.join(folder, "SFX_Squash.wav"),
          mix(noise(0.35, 1.0, 0.35, 1.5), tone(lambda x: 900 - 700 * x, 0.3, square, 0.25, decay_pow=1.2)))
    # splash: filtered noise burst with a bubbly wobble
    splash = noise(0.6, 1.0, 0.08, 1.3)
    bubbles = tone(lambda x: 300 + 200 * math.sin(x * 40), 0.5, math.sin, 0.25, decay_pow=2.0)
    write(os.path.join(folder, "SFX_Splash.wav"), mix(splash, bubbles))
    # goal reached: bright rising arpeggio
    arp = seq(*[tone(lambda x, f=note(n): f, 0.09, lambda p: 0.6 * square(p) + 0.4 * math.sin(p), 0.35, decay_pow=0.8)
                for n in (72, 76, 79, 84)])
    write(os.path.join(folder, "SFX_Goal.wav"), mix(arp, silence(0.1) + tone(lambda x: note(88), 0.35, math.sin, 0.3)))
    # game over: sad descending notes
    write(os.path.join(folder, "SFX_GameOver.wav"),
          seq(*[tone(lambda x, f=note(n): f * (1 - 0.03 * x), 0.28, tri, 0.6, decay_pow=0.7) for n in (67, 63, 60, 55)]))
    # win: short fanfare
    fan = seq(*[tone(lambda x, f=note(n): f, d, lambda p: 0.5 * square(p) + 0.5 * tri(p), 0.4, decay_pow=0.6)
                for n, d in ((67, 0.12), (67, 0.12), (67, 0.12), (72, 0.5))])
    write(os.path.join(folder, "SFX_Win.wav"), fan)
    # dusk chime when the sky changes
    chime = mix(*[silence(0.12 * k) + tone(lambda x, f=note(n): f, 1.2, math.sin, 0.3, decay_pow=2.5)
                  for k, n in enumerate((76, 72, 69, 64))])
    write(os.path.join(folder, "SFX_Dusk.wav"), chime)
    # car horn (two-tone)
    write(os.path.join(folder, "SFX_Honk.wav"),
          mix(tone(lambda x: 400, 0.25, square, 0.3, decay_pow=0.3), tone(lambda x: 500, 0.25, square, 0.3, decay_pow=0.3)))
    # looping music: 16 bars at 120 bpm. A section (bouncy pentatonic tune), then a B section an octave
    # lower that climbs back up, over bass, soft chord pads, kick, snare and hats
    beat = 0.25
    melody = [72, 74, 76, 79, 76, 74, 72, 69, 72, 74, 76, 79, 81, 79, 76, 74,
              76, 79, 81, 84, 81, 79, 76, 74, 72, 74, 76, 74, 72, 69, 67, 69,
              69, 72, 74, 72, 69, 67, 64, 67, 69, 72, 74, 76, 74, 72, 69, 67,
              72, 76, 79, 76, 81, 79, 76, 79, 84, 81, 79, 76, 74, 76, 79, 72]
    bass = [48, 48, 55, 55, 45, 45, 52, 52, 41, 41, 48, 48, 43, 43, 50, 50,
            45, 45, 52, 52, 41, 41, 48, 48, 43, 43, 50, 50, 43, 43, 48, 48]
    lead = lambda p: 0.5 * square(p) + 0.5 * tri(p)
    mel = seq(*[tone(lambda x, f=note(n): f, beat, lead, 0.16, decay_pow=1.2) for n in melody])
    bas = seq(*[tone(lambda x, f=note(n): f, beat * 2, tri, 0.35, attack=0.01, decay_pow=0.5) for n in bass])
    pads = seq(*[mix(tone(lambda x, f=note(n + 24): f, beat * 2, math.sin, 0.07, attack=0.08, decay_pow=0.4),
                     tone(lambda x, f=note(n + 31): f, beat * 2, math.sin, 0.05, attack=0.08, decay_pow=0.4))
                 for n in bass])
    kick = tone(lambda x: 150 - 105 * x, 0.12, math.sin, 0.55, attack=0.001, decay_pow=2.0)
    snare = mix(noise(0.12, 0.3, 0.6, 2.0), tone(lambda x: 190, 0.08, tri, 0.12, decay_pow=2.0))
    step = int(beat * RATE)
    drums = silence(beat * len(melody))
    for i in range(len(melody)):
        hits = [noise(0.04, 0.1, 0.9, 3.0)]
        if i % 2 == 0:
            hits.append(kick)
        if i % 4 == 2:
            hits.append(snare)
        for hit in hits:
            for j, s in enumerate(hit):
                if i * step + j < len(drums):
                    drums[i * step + j] += s
    write(os.path.join(folder, "SFX_Music.wav"), mix(mel, bas, pads, drums))
    # daytime ambience loop: soft wind plus scattered bird chirps
    loop = 8.0
    wind = [0.5 * s for s in noise(loop, 0.25, 0.01, 0.0)]
    birds = silence(loop)
    for _ in range(14):
        start = int(random.uniform(0, loop - 0.6) * RATE)
        base = random.uniform(2200, 3800)
        chirp = seq(*[tone(lambda x, b=base: b * (1 + 0.25 * math.sin(x * math.pi)), random.uniform(0.04, 0.09),
                           math.sin, 0.25, decay_pow=1.5) + silence(0.03) for _ in range(random.randint(2, 4))])
        for i, s in enumerate(chirp):
            if start + i < len(birds):
                birds[start + i] += s
    write(os.path.join(folder, "SFX_AmbienceDay.wav"), mix(wind, birds))
    # night ambience loop: pulsing cricket trills over a low hum
    loop = 6.0
    crickets = silence(loop)
    for _ in range(9):
        start = int(random.uniform(0, loop - 0.8) * RATE)
        f = random.uniform(4200, 5200)
        trill = []
        for _ in range(random.randint(3, 6)):
            trill += tone(lambda x, f=f: f, 0.025, math.sin, 0.18, decay_pow=0.5) + silence(0.02)
        for i, s in enumerate(trill):
            if start + i < len(crickets):
                crickets[start + i] += s
    hum = [0.4 * s for s in noise(loop, 0.15, 0.005, 0.0)]
    write(os.path.join(folder, "SFX_AmbienceNight.wav"), mix(crickets, hum))
    make_extras(folder)


def make_extras(folder):
    """Sounds added for the full-game update: clock tick, level-up jingle, bonus fly chime."""
    # clock tick for the last seconds of the crossing timer: a short woody click
    write(os.path.join(folder, "SFX_Tick.wav"),
          mix(tone(lambda x: 1800 - 600 * x, 0.04, math.sin, 0.6, attack=0.001, decay_pow=3.0), noise(0.02, 0.2, 0.7, 3.0)))
    # level up: quick rising major arpeggio ending on a held chord
    run_up = seq(*[tone(lambda x, f=note(n): f, 0.07, lambda p: 0.5 * square(p) + 0.5 * tri(p), 0.35, decay_pow=0.8)
                   for n in (60, 64, 67, 72, 76, 79)])
    held = mix(*[tone(lambda x, f=note(n): f, 0.6, tri, 0.25, decay_pow=1.5) for n in (72, 76, 79, 84)])
    write(os.path.join(folder, "SFX_LevelUp.wav"), seq(run_up, held))
    # bonus fly: a buzzy wing flutter that resolves into two sparkly pings
    buzz = tone(lambda x: 220 + 30 * math.sin(x * 60), 0.18, square, 0.15, decay_pow=1.0)
    pings = seq(tone(lambda x: note(91), 0.09, math.sin, 0.4, decay_pow=1.5),
                tone(lambda x: note(96), 0.3, math.sin, 0.4, decay_pow=2.0))
    write(os.path.join(folder, "SFX_FlyBonus.wav"), seq(buzz, pings))
    make_endless(folder)


def make_endless(folder):
    """Sounds for endless mode: railway crossing bell, train horn, and a chime for entering a new landscape."""
    # crossing bell: four bright metallic dings (two detuned partials each)
    ding = mix(tone(lambda x: 1320, 0.22, math.sin, 0.4, attack=0.001, decay_pow=2.5),
               tone(lambda x: 1760 * 1.01, 0.22, math.sin, 0.25, attack=0.001, decay_pow=3.0))
    write(os.path.join(folder, "SFX_TrainBell.wav"), seq(*[ding + silence(0.06) for _ in range(4)]))
    # train horn: a low chord of buzzy tones that swells and fades, plus rumbling noise
    chord = mix(*[tone(lambda x, f=f: f * (1 - 0.02 * x), 1.1, lambda p: 0.6 * square(p) + 0.4 * tri(p), 0.18,
                       attack=0.08, decay_pow=0.6) for f in (185.0, 233.0, 277.0)])
    write(os.path.join(folder, "SFX_TrainHorn.wav"), mix(chord, noise(1.3, 0.35, 0.03, 0.8)))
    # new landscape: soft rising four-note chime
    write(os.path.join(folder, "SFX_NewArea.wav"),
          mix(*[silence(0.1 * k) + tone(lambda x, f=note(n): f, 0.9, math.sin, 0.3, decay_pow=2.0)
                for k, n in enumerate((67, 71, 74, 79))]))


def make_jumpcut(folder):
    """Jump Cut's own sounds. Beat 1's quick time event: the world drops into bullet time, the
    player has to hit Freeze Frame, and the last five seconds of the freeze are counted down the
    way a film set counts down to "Action" - a 1 kHz pop per second, then the clapper.

    Synthesized here from sine/square/noise like everything else in this file, so they are ours
    and need no CREDITS.md entry.

        python tools/make_sfx.py <folder> jumpcut
    """
    # SFX_CountdownBeep - the Academy leader's 1 kHz "pop", one per remaining second.
    # Deliberately dry and short so five of them in a row read as a countdown, not as music.
    write(os.path.join(folder, "SFX_CountdownBeep.wav"),
          tone(lambda x: 1000.0, 0.11, math.sin, 0.55, attack=0.001, decay_pow=2.2))

    # SFX_CountdownAction - time is up and the world moves again. A clapperboard crack
    # (short bright noise burst) followed by a rising two-tone, so it reads as "go", not "fail".
    clap = noise(0.07, 0.75, lowpass=0.9, decay_pow=4.0)
    call = seq(tone(lambda x: 1245.0, 0.10, math.sin, 0.42, attack=0.001, decay_pow=2.0),
               tone(lambda x: 1660.0, 0.34, math.sin, 0.42, attack=0.002, decay_pow=1.6))
    write(os.path.join(folder, "SFX_CountdownAction.wav"), seq(clap, call))

    # SFX_BulletTime - the explosion drops the world into slow motion. A tone bending DOWN a
    # fifth plus a noise swell: the standard "everything just slowed" cue, falling rather than
    # rising so it cannot be mistaken for the countdown's pops.
    swoop = mix(tone(lambda x: 880.0 * (1.0 - 0.42 * x), 0.75, math.sin, 0.30, attack=0.004, decay_pow=1.2),
                tone(lambda x: 586.0 * (1.0 - 0.42 * x), 0.75, tri, 0.18, attack=0.004, decay_pow=1.2))
    write(os.path.join(folder, "SFX_BulletTime.wav"), mix(swoop, noise(0.8, 0.22, 0.05, 1.4)))


def _delay(dur, track):
    return silence(dur) + track


def _thud(freq, dur, vol=0.9, drop=0.55):
    """A body hit: a sine that falls in pitch fast, the way a kick drum does."""
    return tone(lambda x: freq * (1.0 - drop * min(1.0, x * 3.0)), dur, math.sin, vol, attack=0.001, decay_pow=2.4)


def _swell(dur, vol, lowpass):
    """Air moving past: noise that rises and falls with no hard start, so it never reads as a hit."""
    n = int(dur * RATE)
    air = noise(dur, 1.0, lowpass=lowpass, decay_pow=0.0)
    return [air[i] * math.sin(math.pi * i / n) ** 2 * vol for i in range(n)]


def make_jumpcut_fight(folder):
    """Every sound beats 1 to 3 were missing (issue #43): the fight, the crash, the powers, the screens.

    Same rules as make_jumpcut(): sine, square, triangle and noise only, so they are ours and need no
    CREDITS.md entry. Each name is the Unreal asset name the builder assigns to a Blueprint variable.

        python tools/make_sfx.py <folder> jumpcut
    """
    def w(name, samples):
        write(os.path.join(folder, name + ".wav"), samples)

    # --- the fight -------------------------------------------------------------------------------
    # SFX_PunchWhoosh - air moving, no contact.
    w("SFX_PunchWhoosh", _swell(0.16, 0.6, 0.35))

    # SFX_PunchHit1/2/3 - the combo. Each is a click (bright noise) on a falling thud. The third is
    # the finisher: lower, longer, with a second body under it, so the ear hears the combo end.
    w("SFX_PunchHit1", mix(noise(0.05, 0.8, 0.85, 3.0), _thud(190.0, 0.13, 0.9)))
    w("SFX_PunchHit2", mix(noise(0.05, 0.8, 0.80, 3.0), _thud(165.0, 0.14, 0.95)))
    w("SFX_PunchHit3", mix(noise(0.09, 1.0, 0.70, 2.4), _thud(120.0, 0.30, 1.0), _thud(62.0, 0.42, 0.8, 0.4),
                           _delay(0.03, noise(0.25, 0.35, 0.10, 2.0))))

    # SFX_PlayerHit - the player takes one. Duller than his own punches and with a short falling
    # square "ugh", so it is never confused with a hit he landed.
    w("SFX_PlayerHit", mix(noise(0.06, 0.6, 0.45, 3.0), _thud(140.0, 0.18, 0.9),
                           tone(lambda x: 300.0 * (1.0 - 0.45 * x), 0.16, square, 0.10, attack=0.002, decay_pow=1.5)))
    # SFX_GoonHit - a goon takes one: lighter and higher than the punch that caused it.
    w("SFX_GoonHit", mix(noise(0.04, 0.5, 0.6, 3.0), _thud(230.0, 0.10, 0.6)))
    # SFX_GoonDown - body to pavement: a low thud, then a softer second one as he settles.
    w("SFX_GoonDown", mix(_thud(95.0, 0.28, 1.0, 0.5), noise(0.12, 0.5, 0.25, 2.5),
                          _delay(0.19, mix(_thud(75.0, 0.22, 0.55, 0.4), noise(0.10, 0.25, 0.2, 2.5)))))

    # SFX_CleaverSwing - a blade, so the whoosh carries a thin falling whistle the fists do not have.
    w("SFX_CleaverSwing", mix(_swell(0.26, 0.55, 0.55),
                              tone(lambda x: 2600.0 * (1.0 - 0.5 * x), 0.26, math.sin, 0.12, attack=0.05, decay_pow=1.5)))
    # SFX_BossDown - the boss falls. The goon's fall, twice the size, plus the cleaver ringing on
    # the ground a beat later (two high sines that are not in tune with each other).
    ring = mix(tone(lambda x: 1870.0, 0.9, math.sin, 0.16, attack=0.001, decay_pow=2.5),
               tone(lambda x: 2495.0, 0.7, math.sin, 0.10, attack=0.001, decay_pow=2.5),
               noise(0.03, 0.4, 0.9, 3.0))
    w("SFX_BossDown", mix(_thud(70.0, 0.55, 1.0, 0.45), _thud(48.0, 0.7, 0.8, 0.3), noise(0.3, 0.6, 0.15, 2.0),
                          _delay(0.42, ring)))

    # --- beat 1: the crash and the explosion -------------------------------------------------------
    # SFX_CarCrash - the car comes through the cafe wall: an engine rising for a third of a second,
    # the impact, then glass - a spray of very short high sine pings at random times.
    engine = tone(lambda x: 70.0 + 110.0 * x, 0.34, square, 0.16, attack=0.05, decay_pow=0.0)
    engine = [engine[i] * (i / len(engine)) for i in range(len(engine))]
    impact = mix(noise(0.5, 1.0, 0.5, 2.0), _thud(80.0, 0.5, 1.0, 0.5), noise(0.9, 0.5, 0.06, 1.5))
    glass = []
    for _k in range(26):
        f = random.uniform(2400.0, 6200.0)
        glass.append(_delay(0.05 + random.uniform(0.0, 0.75) ** 1.5,
                            tone(lambda x, f=f: f, random.uniform(0.03, 0.09), math.sin, random.uniform(0.05, 0.16),
                                 attack=0.001, decay_pow=2.0)))
    w("SFX_CarCrash", seq(engine, mix(impact, *glass)))

    # SFX_Explosion - the blast that starts the quick time event. A crack, a very low boom that
    # keeps falling, and a long dull noise tail. No high tail: SFX_BulletTime plays over the end of it.
    w("SFX_Explosion", mix(noise(0.08, 1.0, 0.95, 3.0),
                           tone(lambda x: 85.0 * (1.0 - 0.6 * x), 1.3, math.sin, 1.0, attack=0.002, decay_pow=1.6),
                           tone(lambda x: 43.0 * (1.0 - 0.4 * x), 1.5, tri, 0.7, attack=0.004, decay_pow=1.4),
                           noise(1.5, 0.75, 0.07, 1.8), _delay(0.02, noise(0.5, 0.5, 0.3, 2.0))))

    # --- the powers ---------------------------------------------------------------------------------
    # SFX_PowerFreezeFrame - taking the first power from the driver. Cold: a pure rising fifth with
    # a shimmer two octaves up, pale like the power's cyan. Ends on a held note, as if it stopped.
    w("SFX_PowerFreezeFrame", mix(
        seq(tone(lambda x: note(69), 0.16, math.sin, 0.35, decay_pow=0.6),
            tone(lambda x: note(76), 0.16, math.sin, 0.35, decay_pow=0.6),
            tone(lambda x: note(81), 0.95, math.sin, 0.40, decay_pow=1.6)),
        _delay(0.32, tone(lambda x: note(93) * (1.0 + 0.004 * math.sin(40.0 * x)), 0.95, math.sin, 0.10, decay_pow=1.8)),
        _delay(0.32, tone(lambda x: note(88), 0.95, tri, 0.08, decay_pow=1.8))))
    # SFX_FreezeFrameOn - pressing E. The world stops: a hard low click and a tone that is cut
    # dead rather than fading (decay_pow 0 = no fade), because time did not slow down, it stopped.
    w("SFX_FreezeFrameOn", seq(mix(noise(0.03, 0.9, 0.9, 2.0), _thud(110.0, 0.09, 0.8)),
                               mix(tone(lambda x: note(81), 0.22, math.sin, 0.30, attack=0.002, decay_pow=0.0),
                                   tone(lambda x: note(88), 0.22, tri, 0.14, attack=0.002, decay_pow=0.0))))

    # SFX_PowerSplice - taking the second power from the boss. Splice is the cut, so it is two
    # halves that do not join smoothly: a phrase, a tape-splice click, the same phrase a tritone up.
    def half(base):
        return seq(tone(lambda x: note(base), 0.11, square, 0.16, decay_pow=0.5),
                   tone(lambda x: note(base + 7), 0.11, square, 0.16, decay_pow=0.5),
                   tone(lambda x: note(base + 12), 0.20, square, 0.16, decay_pow=1.2))
    w("SFX_PowerSplice", seq(half(62), noise(0.02, 0.8, 0.95, 2.0), half(68),
                             tone(lambda x: note(80), 0.6, math.sin, 0.30, decay_pow=1.8)))
    # SFX_SpliceBlink - the blink itself (Left Shift). Very short: a rising zip that is CUT, a
    # click, and a falling zip on the other side - leave, cut, arrive. 0.2 s, because it is spammed.
    w("SFX_SpliceBlink", seq(tone(lambda x: 500.0 + 2600.0 * x * x, 0.07, tri, 0.38, attack=0.001, decay_pow=0.0),
                             noise(0.012, 0.9, 0.95, 1.0),
                             tone(lambda x: 3100.0 - 2300.0 * x, 0.11, tri, 0.34, attack=0.001, decay_pow=1.4)))

    # --- the level ----------------------------------------------------------------------------------
    # SFX_Checkpoint - a film slate: the clap, then two soft confirming notes.
    w("SFX_Checkpoint", seq(noise(0.05, 0.7, 0.9, 4.0),
                            tone(lambda x: note(79), 0.10, math.sin, 0.30, decay_pow=1.0),
                            tone(lambda x: note(84), 0.32, math.sin, 0.30, decay_pow=1.6)))
    # SFX_GateOpen - a heavy roller gate: a low rattling square that climbs slowly, ending in a clunk.
    n = int(0.9 * RATE)
    rattle = tone(lambda x: 38.0 + 22.0 * x, 0.9, square, 0.22, attack=0.03, decay_pow=0.0)
    grit = noise(0.9, 0.45, 0.3, 0.0)
    w("SFX_GateOpen", seq([(rattle[i] + grit[i] * (0.5 + 0.5 * math.sin(2 * math.pi * 14.0 * i / RATE))) *
                           min(1.0, 4.0 * (1.0 - i / n)) for i in range(n)],
                          mix(_thud(90.0, 0.25, 1.0), noise(0.06, 0.7, 0.6, 3.0))))

    # --- the screens --------------------------------------------------------------------------------
    def chord(notes, dur, vol):
        return mix(*[tone(lambda x, f=note(k): f, dur, tri, vol, attack=0.01, decay_pow=1.5) for k in notes])

    def run(notes, dur):
        return seq(*[tone(lambda x, f=note(k): f, dur, tri, 0.30, decay_pow=0.6) for k in notes])

    # SFX_TitleSting - the title card. A rising run into an open fifth: A with no third at the end,
    # so it sounds like a question the game has yet to answer.
    w("SFX_TitleSting", seq(run((57, 60, 64, 69), 0.09),
                            mix(chord((45, 57, 64, 69), 1.6, 0.22),
                                tone(lambda x: note(81), 1.6, math.sin, 0.12, decay_pow=2.0))))
    # SFX_WinSting - major, rising, resolved.
    w("SFX_WinSting", seq(run((60, 64, 67), 0.10),
                          mix(chord((48, 60, 64, 67, 72), 1.4, 0.2),
                              tone(lambda x: note(84), 1.4, math.sin, 0.12, decay_pow=2.0))))
    # SFX_LoseSting - three falling notes into a low minor chord, like a reel running down.
    w("SFX_LoseSting", seq(run((67, 63, 60), 0.16),
                           mix(chord((36, 48, 51, 55), 1.5, 0.22),
                               tone(lambda x: note(48) * (1.0 - 0.06 * x), 1.5, square, 0.05, decay_pow=1.5))))


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "sfx"
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    os.makedirs(folder, exist_ok=True)
    if which == "jumpcut":
        make_jumpcut(folder)
        make_jumpcut_fight(folder)
    else:
        make_all(folder)
        make_jumpcut(folder)
        make_jumpcut_fight(folder)
