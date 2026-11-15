# usage: python3 tools/mus_loopfix.py <decoded.wav> <out.wav> <target RMS dBFS>   (decode an mp3 first: afconvert -f WAVE -d LEI16@44100 in.mp3 decoded.wav)
"""Make a clean loop from a decoded mp3: cut where the tail best matches the opening, blend the
first M samples from the material just past the cut, normalise to a target RMS, report the seam."""
import wave, struct, sys, math
src, dst, target_db = sys.argv[1], sys.argv[2], float(sys.argv[3])
w = wave.open(src); ch = w.getnchannels(); sr = w.getframerate(); n = w.getnframes()
a = list(struct.unpack('<%dh' % (n * ch), w.readframes(n)))
fr = lambda i: [a[i * ch + c] for c in range(ch)]
M, W = 2205, 512
best = None
for k in range(n - 8000, n - M - 1, 3):
    e = 0
    for j in range(0, W, 4):
        e += abs(a[(k + j) * ch] - a[j * ch])
    if best is None or e < best[0]:
        best = (e, k)
err, k = best
loop = a[:k * ch]
for i in range(M):
    x = i / M
    for c in range(ch):
        loop[i * ch + c] = a[(k + i) * ch + c] * (1 - x) + a[i * ch + c] * x
def jump(s):
    return max(abs(s[c] - s[-ch + c]) for c in range(ch))
steps = sorted(abs(loop[(i + 1) * ch] - loop[i * ch]) for i in range(0, k - 1, 97))
rms = math.sqrt(sum(v * v for v in loop[::7]) / len(loop[::7])) / 32767
g = 10 ** (target_db / 20) / rms
out = struct.pack('<%dh' % len(loop), *[int(max(-32767, min(32767, v * g))) for v in loop])
o = wave.open(dst, 'wb'); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr); o.writeframes(out); o.close()
print('%s: cut at %.3fs of %.3fs (match err/sample %.0f), seam jump before %d, after %d, typical step p50 %d p99 %d, gain %.3f peak %.3f'
      % (dst.split('/')[-1], k / sr, n / sr, err / (W / 4), max(abs(a[c] - a[(n - 1) * ch + c]) for c in range(ch)),
         jump(loop), steps[len(steps) // 2], steps[int(len(steps) * .99)], g, max(abs(v) for v in loop) * g / 32767))
