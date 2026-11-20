// The ending's sound: one short beep each time the logo hops (when the item is saved, and twice on the closing screen).
// Usage: node audio.mjs <out.wav> [ingredients]     Timings come from page/timing.json, the same file the animation reads;
// pass "ingredients" for the variant whose closing screen comes later.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const base = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), "page/timing.json"), "utf8"));
const T = process.argv[3] === "ingredients" ? { ...base, ...base.ingredients } : base;
const SR = 48000, N = Math.round(SR * T.end);
const L = new Float32Array(N), R = new Float32Array(N);
const hz = (midi) => 440 * Math.pow(2, (midi - 69) / 12);
const env = (t, attack, tau) => Math.min(1, t / attack) * Math.exp(-t / tau);
function blip(at, midi, gain, pan = 0) {
  const start = Math.round(at * SR), gl = Math.cos((pan + 1) * Math.PI / 4), gr = Math.sin((pan + 1) * Math.PI / 4);
  for (let i = 0; i < 0.2 * SR && start + i < N; i++) {
    const t = i / SR, v = gain * env(t, 0.003, 0.045) * Math.sin(2 * Math.PI * hz(midi) * t * (1 + 0.04 * Math.exp(-t / 0.02)));
    L[start + i] += v * gl; R[start + i] += v * gr;
  }
}
blip(T.swap + 0.6, 72, 0.5);                                   // the logo lands beside the saved item
blip(T.out + 0.62, 72, 0.5); blip(T.out + 0.98, 79, 0.32, 0.1); // closing screen: take-off and landing

const pcm = Buffer.alloc(44 + N * 4);
pcm.write("RIFF", 0); pcm.writeUInt32LE(36 + N * 4, 4); pcm.write("WAVEfmt ", 8); pcm.writeUInt32LE(16, 16); pcm.writeUInt16LE(1, 20);
pcm.writeUInt16LE(2, 22); pcm.writeUInt32LE(SR, 24); pcm.writeUInt32LE(SR * 4, 28); pcm.writeUInt16LE(4, 32); pcm.writeUInt16LE(16, 34);
pcm.write("data", 36); pcm.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { pcm.writeInt16LE(Math.round(Math.tanh(L[i]) * 32767), 44 + i * 4); pcm.writeInt16LE(Math.round(Math.tanh(R[i]) * 32767), 46 + i * 4); }
writeFileSync(process.argv[2], pcm);
