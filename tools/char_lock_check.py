"""Check that no prompt describes a locked character by hand.

The character lock (docs/character-locks.json) only works if every prompt uses the {CafeWalker} token
instead of writing him out in prose. The moment one prompt says "a dark green apron" in its own words,
that picture is free to drift - which is exactly how the title card, the "to be continued" card and the
itch.io cover ended up with three different aprons on the same man (Fri Nov 13).

So this fails the moment a prompt in docs/prompts.md or docs/prompts-gemini.md uses a locked character's
own distinctive words without the token.

    python tools/char_lock_check.py            # check, exit 1 on a finding
    python tools/char_lock_check.py --list     # print the lock instead

It is a text check, not an image check. It cannot tell you the picture came out right - only that the
words sent to the model came from one place. Looking at the picture is still your job.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCKS = os.path.join(ROOT, 'docs', 'character-locks.json')
DOCS = ['docs/prompts.md', 'docs/prompts-gemini.md']

# Words that belong to a locked character. Seeing one in a prompt that did not use the token means
# somebody is describing him by hand again. Keep these specific: "green" alone would fire on a tree.
TELLS = {
    'CafeWalker': ['dark green apron', 'green bib apron', 'green cloth apron', 'green canvas apron',
                   'khaki brown shirt', 'khaki brown long-sleeve', 'cream shirt', 'barista',
                   'coffee shop worker',
                   # the director costume form, added Sat Nov 14 - a costume is still him
                   'charcoal grey bomber jacket', 'grey bomber jacket', 'film director'],
    'CafeCoworker': ['teal apron', 'teal canvas apron', 'white short-sleeve shirt', 'high ponytail'],
    'CrashDriver': ['brown leather jacket', 'leather jacket'],
}


def prompts(path):
    """Yield (code, line_no, text) for every '> ' prompt line under a '### CODE' heading."""
    code = None
    for i, l in enumerate(open(path, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,4} ([A-Z0-9][A-Z0-9-]*)\b', l)
        if m: code = m.group(1)
        elif l.startswith('> ') and code: yield code, i, l[2:]


def main():
    lock = {k: v for k, v in json.load(open(LOCKS, encoding='utf-8')).items() if not k.startswith('_')}
    if '--list' in sys.argv:
        for n, c in lock.items():
            print('%s  (%s)' % (n, c['role']))
            for inv in c.get('invariants', []): print('    - ' + inv)
        return 0

    bad = []
    for rel in DOCS:
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(path): continue
        # gather each code's whole prompt so a token on line 1 covers a tell on line 5
        whole, where = {}, {}
        for code, i, text in prompts(path):
            whole[code] = whole.get(code, '') + ' ' + text
            where.setdefault(code, i)
        for code, text in whole.items():
            low = text.lower()
            used = set(re.findall(r'\{([A-Za-z][A-Za-z0-9_]*)(?::\w+)?\}', text))
            for name, tells in TELLS.items():
                if name in used: continue
                if code in lock[name].get('sheet_prompts', []): continue   # the lock's own source
                for t in tells:
                    if t in low:
                        bad.append('%s:%d  %s says "%s" but does not use {%s}' % (rel, where[code], code, t, name))
                        break

    missing = [n for n, c in lock.items()
               if not os.path.exists(os.path.join(ROOT, c['sheet'].replace('/', os.sep)))]
    for n in missing: bad.append('lock: %s names a sheet that is not on disk (%s)' % (n, lock[n]['sheet']))

    if bad:
        print('character lock: %d problem(s)' % len(bad))
        for b in bad: print('  ' + b)
        print('\nFix by replacing the hand-written description with the token, e.g. {CafeWalker} or'
              '\n{CafeWalker:short} when the character is small in the frame. See docs/character-locks.json.')
        return 1
    print('character lock: ok - %d characters, every prompt that mentions one uses its token' % len(lock))
    return 0


if __name__ == '__main__':
    sys.exit(main())
