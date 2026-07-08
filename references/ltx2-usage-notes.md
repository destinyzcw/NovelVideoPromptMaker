# LTX-2.3 Usage Notes (deep-research findings)

Practical usage guidance for LTX-2 / LTX-2.3 gathered from primary sources (Lightricks
GitHub/HuggingFace/docs, the arXiv paper, the ltx.io guides) and corroborated community
practitioners (ComfyUI/KJNodes GitHub issues, CivitAI workflow authors, nemovideo.com,
aistudynow.com, stable-diffusion-art.com, HuggingFace forum). Each item is tagged
**[official]** (from Lightricks/authors) or **[community]** (field-tested third parties;
treat single-source community tips as provisional).

This skill only writes **text prompts** — it does not run the model. The "Model & runtime
facts" section is for accurate metadata and for understanding *why* the prompt rules exist;
the "Prompt-writing rules" section is what most affects our output and is mirrored into
`ltx2-prompt-guide.md`.

---

## 1. Model & runtime facts (for metadata / context)

**Versions** [official]: The current open release is **LTX-2.3 (22B)**; it supersedes the
original LTX-2 (19B). API variants are `ltx-2-3-fast` and `ltx-2-3-pro` (the older
`ltx-2-fast`/`ltx-2-pro` were deprecated). "LTXV-2" is community shorthand, not an official
name.

**Architecture** [official, arXiv 2601.03233]: Joint **single-pass** audio+video diffusion.
Asymmetric dual-stream transformer (~14B video + ~5B audio) linked by bidirectional
cross-attention; sub-frame A/V alignment. Audio is **always** generated (stereo; 16 kHz VAE
internal, 24 kHz+ vocoder out) — it cannot be suppressed in the open-source pipeline, which
is why every prompt must describe sound or the model fills the void (often "elevator muzak").

**Geometry** [official, `constants.py` / HF card]:
- Default output **121 frames @ 24 fps ≈ 5 s** (ComfyUI beginner template uses 1280×720,
  25 fps, 5 s).
- Frame count **must be 8·k + 1** (…, 25, 33, 41, 97, 121, 241). Non-conforming counts
  behave unpredictably.
- Dimensions must be multiples of **32** (one-stage) / **64** (two-stage). Best results
  locally at **≤ 720p**; native **4K / 50 fps / up to 20 s** is API/data-center territory.

**Parameters** [official, `constants.py`]:
- Full/dev model: **30 steps**, video **CFG 3.0**, audio **CFG 7.0**, modality_scale 3.0.
- HQ two-stage: 15 steps. Distilled: **8 (+4) steps, CFG 1.0** — CFG=1 means the **negative
  prompt is ignored** on the distilled model.
- There is an official **default negative prompt** (a long quality/consistency list) in
  `constants.py`; the ComfyUI template default is just `pc game, console game, video game,
  cartoon, childish, ugly`.

**Prompt enhancement** [official]: All pipelines support `enhance_prompt` (a Gemma-3 text
encoder rewrites/expands the prompt). The enhancer's own system prompts (see §2) reveal how
Lightricks wants prompts phrased.

**Modes** [official]: T2V, I2V (first-frame), keyframe / first-last-frame interpolation,
multi-keyframe, V2V (IC-LoRA), A2V, retake/inpaint window, video extend (Pro), **LipDub**
(dialogue replacement), HDR, text-to-audio.

**Documented limitations** [official]: unreliable on-screen text/logos; chaotic/non-linear
motion (jumping, juggling) glitches (dancing is fine); too many characters/objects reduces
accuracy; conflicting lighting confuses it; abstract emotion labels underperform physical
cues; "prompt following is heavily influenced by prompting-style"; audio without speech is
lower quality.

---

## 2. Prompt-writing rules (these change how we author prompts)

### 2.1 Restrained, concrete language — drop empty intensifiers [official]
The Lightricks prompt-enhancer system prompts explicitly strip hype: use `red dress` not
`vibrant red`, `soft overhead light` not `blinding light`, `subtle freckles` not `striking
freckles`; "avoid dramatic terms, use mild, natural, understated phrasing." Empty adjectives
(`epic, dynamic, cinematic, vivid, stunning`) don't carry action — **named, concrete
motion and appearance do.** (Consistent with our "show don't tell" and "named motion over
adjectives" rules. Note the ltx.io examples still open with a light `cinematic` style cue —
a *single* early style marker is fine; it's the pile-up of intensifiers to avoid.)

### 2.2 Visual and audio only — no other senses [official]
"NO smell, taste, or tactile sensations." Describe only what the camera sees and the mic
hears. Don't write "the salt air stings her skin" — show the wind and spray instead.

### 2.3 Action carries the shot; use present-progressive verbs [official]
"Strong prompts say what changes on screen." Lead with concrete verbs (walking, pouring,
turning, lifting, revealing, drifting) as a natural beginning-to-end sequence. A sparse
prompt makes the model "lazy" → static or drifting output.

### 2.4 Match prompt density to clip length [official — new in 2.3]
Longer, more descriptive prompts consistently outperform short ones on 2.3; a short prompt
on a long clip makes the model **rush** the action. ~5 s → 4–8 sentences; 8–10 s → add
proportionally more concrete beats. But don't over-constrain with numbers ("exactly 3 birds
at 45°") or contradictions ("still peaceful lake with crashing waves") — natural language,
no conflicts.

### 2.5 Block the scene like a director [community ★★★]
LTX-2.3 respects spatial layout: state left/right, foreground/background, facing
toward/away, and distance between subjects. "Two people talking" → "the taller man stands
on the left, hands in pockets; the woman on the right holding a bicycle; houses blurred
behind." Scene **direction**, not vague description.

### 2.6 Camera: motivate every move; don't fight the model [official + community]
- The enhancer system prompt says **don't invent camera motion unless it's narratively
  needed** — i.e. every camera move should *do* something (reveal, reframe, land a beat),
  never gratuitous. This is compatible with our chained-camera style **as long as each move
  is motivated by the action**; it's a caution against random move-stacking, not against
  camera authoring (the ltx.io monster-truck example is heavy, motivated choreography).
- **Don't stack mutually exclusive cues** ("handheld AND smooth gimbal") → jitter.
- Plain **"static camera" / "camera not moving" text is unreliable** [community, multiple
  reports] — the reliable fix is a camera-control IC-LoRA (out of scope for prompt text).
  If a locked frame is wanted, "tripod locked, no camera movement" is the best text attempt.
- Describe movement **relative to the subject**, and name the subject's end-state so the
  model knows how to finish the move.

### 2.7 Audio woven through the action, aligned to tempo [official]
"Describe the complete soundscape throughout the prompt alongside the actions — NOT at the
end. Align audio intensity with action tempo." Thread each sound into the sentence for the
beat it accompanies. **A trailing catch-all bracket group at the very end of the prompt is a
confirmed failure mode** — the model largely ignores it, so ambient audio parked in a final
`[…]` / `【…】` (e.g. a closing `【山风…、脚步、鸦啼、呼吸】`) never reaches the video (observed
in the field on LTX-2.3). A short inline bracket group *beside its own beat* mid-paragraph is
fine; the anti-pattern is collecting the whole soundscape at the end. Never an `Audio:` label;
never layer names.

### 2.7b Character consistency: verbatim anchors + DrawThings I2V carry [official + community]
Two reliable levers hold a character's look across independent clips. (1) **Restate the
canonical appearance verbatim** — reuse the exact cast-sheet anchor phrases (same words, same
order) in every T2V prompt the character appears in; paraphrasing or thinning the description
(e.g. "the same young man" with the hair/clothing dropped) leaves those traits for the model
to re-invent, and hair/build/clothing drift shot to shot (a confirmed field failure). (2)
**Chain continuous runs image-to-video**: DrawThings can start a clip from the previous
clip's *last frame* natively (its "use last frame" I2V), inheriting the look pixel-for-pixel
— on those carried clips the text anchors can be light. Note DrawThings supports T2V and I2V
only; First-Frame-Last-Frame (FFLF) and S2V are not exposed there, so the skill relies on the
last-frame I2V carry-over rather than extracting frames itself.

### 2.8 Dialogue: segment long lines with acting directions between them [official — 2.3]
For speaking characters, break a long line into short phrases separated by acting/delivery
beats, e.g.: `...speaks in a slow, sad voice, "I remember after you kids came along..." He
pauses and looks aside, then continues, "your mom..." His eyes widen. He finishes, voice
cracking, "...said something I never understood."` Put speech in quotes; give a volume/tone
reference (whisper, mutter, shout); state language/accent when useful. Keep the total within
the clip's time budget (~2–3 EN words/s, ~5 CJK chars/s).

### 2.9 Keep dialogue clean of stray music [official + community]
Because audio is generated holistically, "musical-looking" scenes (café, party) tend to add
background music that bleeds over speech. In the prompt, explicitly anchor the acoustic:
"crisp close-mic speech with quiet room tone, no background music." (Negative prompts do
**not** reliably remove it — use a positive acoustic instruction.)

### 2.10 Language & lip-sync caveat for CJK [official, important for this skill]
Standard T2V "characters can talk and sing in various languages," so native-language
dialogue is correct. **But** the dedicated LipDub lip-sync path is validated only for
**English, French, Spanish, German, Russian** — Chinese/Japanese lip-sync fidelity is not
guaranteed. Practical mitigation for CJK novels: keep spoken lines **short and clearly
delivered**, favor close-up framing for talking beats (better mouth detail), and for
critical dialogue an audio-first workflow (generate/verify speech, then audio-to-video) is
the most reliable route.

---

## 3. Failure-mode → fix cheat sheet (mostly runtime, [community])

| Symptom | Fix |
| --- | --- |
| Static / no motion (esp. I2V) | Prompt the *action/changes*, not the still image; longer, action-first prompt; ensure text encoder loaded; for I2V slightly blur/compress the input frame |
| Subject morphs/melts mid-clip | Shorten the clip (≤~24–32 frames) and stitch; lock a seed; +2 steps |
| Crunchy edges / halo / flicker | Lower CFG first (not steps); full model lives ~CFG 3, community draft base ~4.5–6.5 |
| Flat / washed look | Add concrete lighting ("golden-hour side-light"), don't raise CFG |
| Camera move ignored | Text camera control is weak; make moves specific + motivated, or use IC-LoRA |
| Random background music over speech | Positive acoustic instruction ("quiet room tone, no music"); audio-first for critical VO |
| Black/green frames | Setup issue — mismatched model/adapter/dtype, not the prompt |

**Seed strategy** [community]: lock a seed once the motion "feel" is good; if a clip
mutates, try seeds ~20 apart — LTX seems to settle within small seed neighborhoods.

**Iterate** [official]: LTX-2 is built for fast experimentation; regenerating a weak shot
with a tweaked prompt is expected — which is exactly why this skill maps every scene back to
its chapter so a single clip can be re-run in isolation.

---

## 4. Source index

Official: `github.com/Lightricks/LTX-2` (incl. `constants.py`, pipeline READMEs,
`ComfyUI-LTXVideo` `system_prompts/gemma_*`), `huggingface.co/Lightricks/LTX-2.3`,
`docs.ltx.video`, `ltx.io/blog/prompting-guide-for-ltx-2` and the LTX-2.3 prompt guide,
arXiv `2601.03233`, `wiki.drawthings.ai/wiki/LTX-2`.
Community: ComfyUI-LTXVideo & KJNodes GitHub issues (#7, #203, #489), CivitAI LTXV workflow
articles, `nemovideo.com`, `aistudynow.com`, `stable-diffusion-art.com/ltx-video`,
HuggingFace forum thread on LTX-2.3 dialogs, GeekatplayStudio LTX-2.3 LipSync repo.
