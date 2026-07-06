# LTX-2.3 Prompt Writing Reference

Distilled from the DrawThings LTX-2 guide (https://wiki.drawthings.ai/wiki/LTX-2) and the
LTX-2 team's own prompting guide (https://ltx.io/blog/prompting-guide-for-ltx-2).

**How to use this file.** Read it in full before writing any prompt. Part 2 reproduces the
LTX-2 team's guidance **verbatim** — those are the golden rules and the output must obey
them. `ltx2-official-examples.md` holds all 11 verbatim example prompts; pattern-match your
writing against those real examples rather than inventing a house style. The pre-save
checklist at the end is your gate before saving any scene.

---

# Part 1 — Golden rules

- **One clip = one prompt = one continuous shot.** LTX-2.3 renders a single short shot
  (typically ~5 s / 121 frames at 24 fps). Never pack a whole plot into one prompt.
- **One flowing paragraph, present tense, 4–8 sentences, under 200 words.** A cohesive
  scene the model reads start-to-finish — not a bullet list, not a filled-in checklist.
- **Imagine the shot, then describe what you see — don't transcribe the prose.** Picture
  how *this beat would actually play on screen*: where the camera sits, how it moves, how
  the subject moves through the frame, how the light and air look. Write *that* down. A
  prompt that paraphrases narration ("she stepped out and did not look back") gives the
  model a sentence; a prompt that describes an imagined shot ("the camera cranes up with
  her as she strides toward the lens, then holds as she passes and recedes down the lane")
  gives it a film.
- **Author from the camera, and chain it.** The lens is the protagonist. Give the camera
  2–4 distinct moves within the single shot, each triggered by an action beat, ending on a
  defined framing (see Part 3). A prompt is **not** `<one camera label> + narrative`.
- **LTX-2.3 generates video AND audio in one pass.** Every prompt must describe sound, or
  the model invents generic filler.
- **Show, don't tell.** Never write a bare internal-state label ("sad", "angry",
  "nervous"); render it as posture, gesture, and expression.
- **Write the whole prompt in the source novel's language** (Chinese novel → Chinese
  prompt, Japanese → Japanese), dialogue included. See Part 5.

---

# Part 2 — Official LTX-2 guidance (verbatim from ltx.io)

Everything in the blockquotes below is copied verbatim from
https://ltx.io/blog/prompting-guide-for-ltx-2. The **Apply** notes are this skill's
guidance for using each rule on novels.

## Key Aspects to Include

> - **Establish the shot.** Use cinematography terms that match your preferred film genre.
>   Include aspects like scale or specific category characteristics to further refine the
>   style you're looking for.
> - **Set the scene.** Describe lighting conditions, color palette, surface textures, and
>   atmosphere to shape the mood.
> - **Describe the action.** Write the core action as a natural sequence, flowing from
>   beginning to end.
> - **Define your character(s).** Include age, hairstyle, clothing, and distinguishing
>   details. Express emotions through physical cues.
> - **Identify camera movement(s).** Specify when the view should shift and how. Including
>   how subjects or objects appear after the camera motion gives the model a better idea
>   of how to finish the motion.
> - **Describe the audio.** Use clear descriptions for ambient sounds, music, audio, and
>   speech. For dialogue, place the text between quotation marks and (if required) mention
>   the language and accent you would like the character to have.

**Apply:** Open with a cinematography term (vary it per scene). Pull character details
from the cast sheet so they stay identical across clips. "Specify **when** the view should
shift and **how**" is the mandate for camera chaining (Part 3): tie each move to a beat and
name how the subject looks after it. Put dialogue in quotes, in the novel's language.

## For Best Results

> - Keep your prompt in a single flowing paragraph to give the model a cohesive scene to
>   work with.
> - Use present tense verbs to describe movement and action.
> - Match your detail to the shot scale. Closeups need more precise detail than wide shots.
> - When describing camera movement, focus on the camera's relationship to the subject.
> - You should expect to write 4 to 8 descriptive sentences to cover all the key aspects
>   of the prompt.
> - Don't be afraid to iterate! LTX-2 is designed for fast experimentation, so refining
>   your prompt is part of the workflow.

**Apply:** Describe the camera's motion **relative to the subject** — subject moving toward
camera / across the frame / away into the distance — not abstract pans. Give close-ups more
facial and gesture detail; keep wide shots simpler. Because iteration is expected, the
skill saves each scene mapped back to its chapter so a human can regenerate a weak shot
alone.

## Additional Helpful Terms

> This is not an exhaustive list. Use it to give you some examples of how to craft the
> result you're looking for.
>
> **Categories**
> - **Animation:** stop-motion, 2D/3D animation, claymation, hand-drawn
> - **Stylized:** comic book, cyberpunk, 8-bit pixel, surreal, minimalist, painterly,
>   illustrated
> - **Cinematic:** period drama, film noir, fantasy, epic space opera, thriller, modern
>   romance, experimental film, arthouse, documentary

**Apply:** Name a Category marker early when it fits the novel's genre (`period drama`,
`film noir`, `fantasy`, `thriller`, `documentary`) — the model locks style from the first
words. Keep the same style marker across a chapter's scenes for visual consistency.

## Visual Details

> - **Lighting conditions:** flickering candles, neon glow, natural sunlight, dramatic
>   shadows
> - **Textures:** rough stone, smooth metal, worn fabric, glossy surfaces
> - **Color palette:** vibrant, muted, monochromatic, high contrast
> - **Atmospheric elements:** fog, rain, dust, particles, smoke

**Apply:** Anchor mood with concrete lighting, palette, texture, and atmosphere rather than
vague words. Favor the atmospheric effects LTX-2 handles well (fog, mist, golden hour, rain,
reflections). Keep lighting logic consistent within a shot (see What to Avoid).

## Sound and Voice

> - **Setting:** Ambient coffeeshop noises, dripping rain and wind blowing, forest ambience
>   with birds singing
> - **Dialogue style:** Energetic announcer, resonant voice with gravitas, distorted
>   radio-style, robotic monotone, childlike curiosity
> - **Volume:** quiet whisper, mutters, shouts, screams

**Apply:** Every prompt needs layered sound (Part 4). Attribute dialogue delivery with these
volume/style words (`barely a whisper`, `mutters`, `shouts over the wind`) so the spoken
line lands with the right energy. Weave sound into prose or a bracket group — never an
`Audio:` label.

## Technical Style Markers

> - **Camera language:** follows, tracks, pans across, circles around, tilts upward, pushes
>   in, pulls back, overhead view, handheld movement, over-the-shoulder, wide establishing
>   shot, static frame
> - **Film characteristics:** jittery stop-motion, pixelated edges, lens flares, film grain
> - **Scale indicators:** expansive, epic, intimate, claustrophobic
> - **Pacing and temporal effects:** slow motion, time-lapse, rapid cuts, lingering shot,
>   continuous shot, freeze-frame, fade-in, fade-out, seamless transition, dynamic
>   movement, sudden stop
> - **Specific visual effects (if relevant):** particle systems, motion blur, depth of
>   field

**Apply:** Draw camera verbs from this list, and vary them across scenes so a chapter feels
edited, not cloned. Use scale words (`intimate`, `claustrophobic`, `epic`) to match the
beat's emotion. Reach for temporal effects (`slow motion`, `sudden stop`, `freeze-frame`)
to punctuate a climactic moment.

## What Works Well with LTX-2

> - **Cinematic compositions:** Wide, medium, and close-up shots with thoughtful lighting,
>   shallow depth of field, and natural motion.
> - **Emotive human moments:** LTX-2 excels at single-subject emotional expressions, subtle
>   gestures, and facial nuance.
> - **Atmosphere & setting:** Weather effects like fog, mist, golden hour light, soft
>   shadows, rain, reflections, and ambient textures all help ground the scene.
> - **Clean, readable camera language:** Clear directions like "slow dolly in," "handheld
>   tracking," or "over-the-shoulder" improve consistency.
> - **Stylized aesthetics:** Painterly, noir, analog film look, fashion editorial,
>   pixelated animation, or surreal art styles work especially well when named early in
>   the prompt.
> - **Lighting and mood control:** Backlighting, color palettes, soft rim light, flickering
>   lamps — these anchor tone better than generic mood words.
> - **Voice:** Characters can talk and sing in various languages.

**Apply:** Lean into what the model is good at. Prefer **single-subject** scenes built
around one character's emotional beat and facial nuance — that is LTX-2's sweet spot, and it
maps naturally onto splitting a busy chapter into focused one-character clips. Name any
style/look early. Multilingual voice support is why native-language dialogue works.

## What to Avoid with LTX-2

> - **Internal states:** Avoid emotional labels like "sad" or "confused" without describing
>   visual cues. Use posture, gesture, and facial expression instead.
> - **Text and logos:** LTX-2 does not currently generate readable or consistent text.
>   Avoid signage, brand names, or printed material.
> - **Complex physics or chaotic motion:** Non-linear or fast-twisting motion (e.g.,
>   jumping, juggling) can lead to artifacts or glitches. However, dancing can work well.
> - **Scene complexity overload:** Too many characters, layered actions, or excessive
>   objects reduce clarity and model accuracy.
> - **Inconsistent lighting logic:** Avoid mixing conflicting light sources (e.g., "a warm
>   sunset with cold fluorescent glow") unless clearly motivated.
> - **Over complicated prompts:** The more actions/characters/instructions you add, the
>   higher the chance some of them won't be seen in the output. Begin with simple things
>   and layer on additional instructions as you iterate.

**Apply — these are the rules drafts most often break:**
- Convert every stated emotion in the novel into a visible cue (`jaw tight`,
  `shoulders hunched`, `eyes darting`) — never leave the bare label.
- No on-screen text, signage, logos, or brand names; also list them in the negative prompt.
- One subject + one primary action per clip. If a chapter beat has a crowd or several
  simultaneous actions, split it into separate scenes instead of overloading one.
- Avoid chaotic/non-linear physics (jumping, juggling, fast twisting); prefer smooth,
  motivated motion.
- One motivated lighting scheme per shot.

---

# Part 3 — Camera authoring

## Positive-prompt element order

Arrange the paragraph roughly in this order for best adherence:

1. **Main action** — the primary event, framed as what the camera catches.
2. **Gestures & nuance** — specific physical movements, subtle character details.
3. **Appearance** — subjects/objects in literal, concrete terms (from the cast sheet).
4. **Environment** — setting, background, atmosphere (dense fog, neon-lit alley).
5. **Camera work — the spine of the shot** (chained; see below).
6. **Lighting & color** — technical film terms (golden hour, cool blue moonlight).
7. **Scene shifts** — any sudden change of action, weather, or time within the shot.
8. **Audio & dialogue** — quoted lines + woven/bracketed sound (Part 4).

## Vary your opening — don't fall into a formula

The most common failure is opening **every** prompt with the same template (e.g.
"Cinematic medium shot, slow dolly-in…"). That flattens every scene into one look. The
official examples open in five different ways — choose the one that fits *this* beat:

- **Action-first:** "An action packed, cinematic shot of a monster truck driving fast
  towards the camera…"
- **Location/mood-first, then camera:** "A warm sunny backyard. The camera starts in a
  tight cinematic close-up of a woman and a man in their 30s…"
- **Slug line / unusual vantage:** "INT. OVEN – DAY. Static camera from inside the oven,
  looking outward through the slightly fogged glass door…"
- **Subject-first:** "The young african american woman wearing a futuristic transparent
  visor… she is soldering a robotic arm."
- **"The camera opens…":** "The camera opens in a calm, sunlit frog yoga studio…"

## Chain the camera (camera A → change → camera B → …)

A strong LTX-2 prompt is a *chain* of camera beats, each paired with an action beat,
flowing continuously:

```
<camera A> + <action A>  →  <camera changes to B> + <action B>  →  <camera settles to C> + <end framing>
```

How the model's own examples are built:

- **Monster truck** = *(A)* locked lens, truck drives fast toward camera → *(B)* as it
  passes, camera **pans left** to follow → *(C)* **handheld**, tracks it into the distance
  → *(D)* truck drifts, turns, drives back **until seen in extreme close-up**.
- **Robot** = *(A)* camera **dollies back**, holding a medium shot of the slow walk → *(B)*
  it starts running, camera **keeps dollying back until** a second blue robot appears in an
  **over-the-shoulder** shot.
- **"We need to run"** = *(A)* camera **zooms in on his mouth** as he whispers → *(B)* he
  screams "NOW!", camera **zooms back out** → *(C)* he turns and runs, camera **tracks**
  handheld → *(D)* camera **cranes up** to show him run into the distance.

**Motivate each move and name its end framing.** A move should *do* something: reveal a new
subject (pan right to reveal the grandfather), change the relationship (dolly back until a
second figure enters over-the-shoulder), or land an emotional beat (push in on her
tear-streaked face). Use the subject's action as the hinge ("as she turns, the camera arcs
around her"; "the plank cracks and the lens whips up to her face"). Match the shot *type* to
the beat: a lonely departure → high wide crane; dread → claustrophobic push-in; a reveal →
slow pan or rack focus.

**Shot-type & move vocabulary (don't reuse the same one every time):** extreme wide /
establishing, wide, full, medium, medium close-up, close-up, extreme close-up, insert/detail,
two-shot, over-the-shoulder, POV, low-angle, high-angle, overhead/top-down, worm's-eye,
Dutch/canted angle; slow dolly in, dolly out / pull-back reveal, crane up/down, tracking /
following, lateral track, arc / orbit, whip pan, tilt up/down, rack focus, handheld follow,
locked-off static from an unusual vantage, snap zoom.

---

# Part 4 — Audio

Include 3–5 sound elements per prompt, layered (this three-layer model is a **planning
tool** — never write the layer names into the prompt):

- **Ambient / background** — establishes place: `wind rustling, distant traffic, café ambiance`.
- **Action / foreground** — syncs to visible motion: `footsteps on gravel, door creaking`.
- **Accent / punctuation** — marks a key beat: `glass shattering, sudden gasp, impact thud`.

Rule of thumb: 1 ambient + 2 action + 1 accent. Sequence with timing words ("begins with…",
"suddenly…", "then fades to…") and control distance/volume with `distant, faint, muffled,
crisp, booming, echoing`.

**Format sound the way the official examples do:** fold it into the flowing sentences, or
drop a `[sound, sound, sound]` bracket group inside the paragraph (in CJK prompts use a
`【…】` group). Do **not** append a mechanical `Audio:` / `音效：` / `音効：` heading, and do
**not** write layer names ("as ambient", "as accent") into the prompt.

- ✗ templated: `…cold blue twilight. Audio: wind over rooftops, boots creaking, a dog bark as accent.`
- ✓ woven: `…cold blue twilight as [wind moans over empty rooftops, her boots creak on frost, a lone dog barks far off].`

### Mood → audio cheat sheet

| Mood | Audio elements |
| --- | --- |
| Tension/suspense | ominous low drone, labored breathing, unsettling silence, distant footsteps |
| Joy/uplifting | bright birdsong, laughter echoing, cheerful chatter, light footsteps |
| Melancholy | mournful wind, rain against window, distant church bells, soft sighs |
| Action/intensity | rapid footsteps, impactful collisions, whooshing motion, rising intensity |

---

# Part 5 — Dialogue & transcripts (making characters speak)

LTX-2.3 generates spoken audio and lip-sync in the same pass as the video. The "transcript"
for a clip is simply the spoken line **written verbatim, in quotation marks, inside the
prompt** — there is no separate transcript input. If a line isn't in the prompt, the model
won't say it. **Give most scenes a spoken line** — talking characters make far more engaging
video. Source words in priority order: real dialogue in the prose → implied/reported speech
→ a short faithful muttered line for a character who is alone. Leave a scene silent only when
there's no character on screen or a line would break the moment.

- **Introduce the speech act, then quote the line, with delivery attribution:**
  `The old man turns to the camera and says, voice cracking, "You came back."` Prefer a
  natural complete line over a clipped single word.
- **One speaker per clip.** LTX-2.3 handles a single speaker cleanly; two people talking
  over each other desyncs. Split a back-and-forth into separate clips.
- **Fit the line to the clip.** ~2–3 words/second (English) or ~5 characters/second
  (Chinese/Japanese). A 6-second clip holds ~12–18 English words or ~30 CJK characters.
  Longer lines get cut off or drift out of sync — trim the line or lengthen the clip.
- **Keep everything in the story's language.** Write the *whole prompt* — action, camera,
  lighting, audio, and dialogue — in the source novel's language. LTX-2.3 supports
  multilingual voice, so matching the source keeps the spoken voice and cultural detail
  consistent. Native-language is the default; an English rewrite of a single weak prompt is
  only a fallback.
- **Add a tonal cue** beside the line (`voice trembling`, `barely a whisper`, `shouting
  over the wind`) and, if useful, reinforce with an accent sound (a gasp before, a sob
  after).

Example (embedded dialogue, woven audio): `Cinematic tight close-up: a weary old fisherman
lowers his lantern and turns to the young woman, his eyes wet, and says in a cracked
whisper, "You came back." Slow push-in, warm lantern glow against black night, [waves lap on
wet rock, wind sighs, a soft catch of breath just before he speaks].`

The skill also records dialogue as structured data (`speaker` + `line`) to emit a
`transcript.txt` per chapter and to check each line is embedded and fits its clip — but the
model itself only ever reads the quoted line inside the prompt.

---

# Part 6 — Negative prompts

Keep them short and content-specific. Long generic keyword dumps degrade quality. A
reasonable default:

`text overlay, subtitles, watermark, warped hands, extra fingers, static frozen frame, blurry`

Add scene-specific exclusions only when a shot needs them (e.g. `no modern cars` for a
period scene). Write the negative prompt in a form the tooling expects; the examples ship
localized negatives per language.

---

# Part 7 — Recommended generation parameters (for metadata reference)

These are the LTX-2.3 defaults from the model authors' code/docs (`Lightricks/LTX-2`
`constants.py`, `docs.ltx.video`). The skill only writes prompts, but record accurate
params in metadata so a human regenerating a clip has correct starting values.

| Parameter | Full / dev model | HQ two-stage | Distilled model |
| --- | --- | --- | --- |
| Sampling steps | **30** | 15 | 8 (+4 stage-2) |
| Video CFG (`cfg_scale`) | **3.0** | 3.0 | **1.0** (CFG off) |
| Audio CFG | **7.0** | 7.0 | 1.0 |
| Modality scale (A/V sync) | 3.0 | 3.0 | — |
| Negative prompt | used | used | **ignored** (CFG=1) |

**Video geometry (all variants):**

| Parameter | Value |
| --- | --- |
| Default output | **121 frames @ 24 fps ≈ 5 s** (ComfyUI template: 1280×720, 25 fps) |
| Frame-count rule | **must be 8·k + 1** (…, 25, 33, 41, 97, 121, 241) |
| Dimension rule | multiples of **32** (one-stage) / **64** (two-stage) |
| Clip duration | 5 s default; up to ~10 s locally, up to 20 s via API (1080p, fast) |
| Resolution | best under 720p locally; up to native 4K / 50 fps on data-center GPUs |
| Audio | joint single-pass, stereo, generated even if unprompted |

> **Match prompt density to duration.** LTX-2.3's authors note that a short prompt on a
> long clip makes the model "rush through the described action," and that longer, more
> descriptive prompts consistently outperform short ones on 2.3. For an ~5 s clip, 4–8
> sentences is right; for 8–10 s, add proportionally more concrete beats.

---

# Part 8 — Worked examples

**Woven-audio single beat:**

> A lone hiker stops mid-stride and slowly turns to look back over her shoulder, her breath
> fogging in the cold. She wears a worn red parka and a heavy backpack, boots caked in mud.
> Behind her a narrow trail winds into a dense autumn pine forest wrapped in low evening
> mist. Medium tracking shot from behind, easing into a slow push-in on her face.
> Golden-hour light rakes low through the trees, warm on one cheek, deep blue shadow on the
> other. [crunching footsteps on dry leaves, wind whispering through pine branches, distant
> owl hooting], then a sharp [twig snaps] as she freezes.

**Camera-driven, imagine-the-shot (verbatim monster-truck example):**

> An action packed, cinematic shot of a monster truck driving fast towards the camera, the
> truck passes the cameras it pans left to follow the trucks reckless drive. dust and motion
> blur is around the truck, hand held feel to the camera as it tries to track its ride into
> the distance. the truck then drifts and turns around, then drives back towards the camera
> until seen in extreme close up.

Applied to a novel beat like *"she left the cottage and did not look back"*, don't write "she
steps out and does not look back". Picture the shot and direct it: *"the camera opens tight
on her hands lacing her boots, cranes up with her as she strides through the doorway straight
toward the lens, then eases back and holds as she passes and recedes down the grey lane
without a glance back."* Same beat, authored as a shot.

For all 11 verbatim examples and a grounded structural breakdown, see
`ltx2-official-examples.md`.

---

# Part 9 — Pre-save checklist

Before saving each scene, re-read the prompt against every item:

**Structure & form**
1. One flowing paragraph, present tense, 4–8 sentences, under 200 words.
2. Opening establishes the shot with a cinematography term (+ Category marker if it fits);
   opening style **varies** across the chapter's scenes.
3. Action reads as one natural beginning-to-end sequence.

**Camera**
4. Camera is **chained** — 2–4 distinct moves, each triggered by an action beat, each
   naming where it ends; movement described relative to the subject.
5. Detail matches shot scale (close-ups more precise than wide shots).

**Subject & emotion**
6. Characters defined concretely (age, hair, clothing, distinguishing details) from the
   cast sheet, identical across clips.
7. Emotion shown via posture/gesture/expression only — **no bare internal-state labels.**

**Scene & light**
8. Concrete lighting, palette, texture, atmosphere set the mood.
9. One consistent, motivated lighting scheme.

**Audio & dialogue**
10. 3–5 layered sounds woven into prose or a `[…]` / `【…】` group — no `Audio:` label, no
    layer names.
11. Dialogue in quotes, embedded inline, with delivery attribution; one spoken line per
    scene where possible; fits the clip's time budget; in the novel's language.

**Keep it clean**
12. No on-screen text, signage, logos, or brand names.
13. One subject + one primary action per clip; no crowding or layered simultaneous actions.
14. No chaotic/non-linear physics; smooth, motivated motion only.
