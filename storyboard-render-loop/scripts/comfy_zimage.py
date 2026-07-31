#!/usr/bin/env python3
"""Generate a single image with a ComfyUI Z-Image Turbo workflow.

Stdlib only (urllib) — no pip install needed.

The script takes an API-format ComfyUI workflow (either the bundled default
template or one you exported yourself via ComfyUI's "Workflow -> Export (API)"),
patches the prompt / seed / steps / size / filename, submits it to the ComfyUI
HTTP API, waits for the render to finish, downloads the resulting image(s) and
writes the first one to --out.

It is deliberately robust about *where* to patch things:

  * positive / negative text  -> resolved by following the sampler's
    `positive` / `negative` links to the CLIPTextEncode node, with a
    `_meta.title` / class_type fallback.
  * seed                       -> `seed` or `noise_seed` on the sampler /
    RandomNoise node.
  * steps                      -> `steps` on the sampler / BasicScheduler.
  * cfg                        -> `cfg` / `guidance` on the sampler (optional).
  * width / height             -> the Empty*LatentImage node.
  * filename_prefix            -> the SaveImage node.

So it works with the standard Z-Image Turbo template *and* with most custom
workflows without hand-editing JSON. If auto-detection misses something, tag
the node in ComfyUI with a `_meta.title` from the list below and it will be
found by title.

Result is printed to stdout as one JSON line:
  {"status":"ok","prompt_id":"...","seed":123,"images":["...png"],"out":"..."}
  {"status":"error","error":"...","prompt_id":"..."}

Exit code is 0 on success, 1 on any failure (so callers can branch on it).
"""

import argparse
import json
import os
import random
import sys
import time
import uuid
import urllib.request
import urllib.parse
import urllib.error

SAMPLER_TYPES = {
    "KSampler", "KSamplerAdvanced", "SamplerCustom", "SamplerCustomAdvanced",
}
LATENT_TYPES = {
    "EmptyLatentImage", "EmptySD3LatentImage", "EmptyLatentImageAdvanced",
}
# _meta.title tags you can set in ComfyUI to force-target a node.
TITLE_POSITIVE = {"POSITIVE_PROMPT", "POSITIVE", "PROMPT"}
TITLE_NEGATIVE = {"NEGATIVE_PROMPT", "NEGATIVE"}
TITLE_LATENT = {"LATENT_IMAGE", "LATENT", "EMPTY_LATENT"}
TITLE_SAMPLER = {"SAMPLER", "KSAMPLER"}
TITLE_SAVE = {"SAVE", "SAVE_IMAGE", "OUTPUT"}


def _title(node):
    return (node.get("_meta", {}) or {}).get("title", "") or ""


def _by_title(wf, titles):
    for nid, node in wf.items():
        if _title(node).strip().upper() in titles:
            return nid, node
    return None, None


def _set_if_present(inputs, candidates, value):
    for key in candidates:
        if key in inputs and not isinstance(inputs[key], list):
            inputs[key] = value
            return True
    return False


def _resolve_text_node(wf, ref, _depth=0):
    """Follow a conditioning link back to a node that has a `text` widget."""
    if not isinstance(ref, list) or _depth > 6:
        return None
    node = wf.get(str(ref[0]))
    if not node:
        return None
    ins = node.get("inputs", {})
    if "text" in ins and not isinstance(ins["text"], list):
        return node
    # Chained conditioning nodes (ConditioningZeroOut, ConditioningCombine...)
    for key in ("conditioning", "conditioning_1", "positive", "negative"):
        if isinstance(ins.get(key), list):
            found = _resolve_text_node(wf, ins[key], _depth + 1)
            if found is not None:
                return found
    return None


def patch_workflow(wf, *, prompt, negative, seed, steps, cfg, width, height,
                   filename_prefix):
    report = {}

    samplers = [(nid, n) for nid, n in wf.items()
                if n.get("class_type") in SAMPLER_TYPES]
    if not samplers:
        nid, node = _by_title(wf, TITLE_SAMPLER)
        if node:
            samplers = [(nid, node)]

    # --- positive / negative text ---
    pos_node = neg_node = None
    for _, n in samplers:
        ins = n.get("inputs", {})
        if pos_node is None and isinstance(ins.get("positive"), list):
            pos_node = _resolve_text_node(wf, ins["positive"])
        if neg_node is None and isinstance(ins.get("negative"), list):
            neg_node = _resolve_text_node(wf, ins["negative"])

    if pos_node is None:
        _, pos_node = _by_title(wf, TITLE_POSITIVE)
    if neg_node is None:
        _, neg_node = _by_title(wf, TITLE_NEGATIVE)

    if pos_node is not None and "text" in pos_node.get("inputs", {}):
        pos_node["inputs"]["text"] = prompt
        report["positive"] = True
    else:
        report["positive"] = False

    if negative is not None and neg_node is not None \
            and "text" in neg_node.get("inputs", {}) \
            and neg_node is not pos_node:
        neg_node["inputs"]["text"] = negative
        report["negative"] = True
    else:
        report["negative"] = bool(negative) is False

    # --- seed / steps / cfg ---
    seed_set = steps_set = cfg_set = False
    for _, n in samplers:
        ins = n.setdefault("inputs", {})
        if not seed_set:
            seed_set = _set_if_present(ins, ("seed", "noise_seed"), seed)
        if not steps_set:
            steps_set = _set_if_present(ins, ("steps",), steps)
        if cfg is not None and not cfg_set:
            cfg_set = _set_if_present(ins, ("cfg", "guidance"), cfg)

    # Fallbacks for SamplerCustomAdvanced-style graphs.
    if not seed_set:
        for _, n in wf.items():
            if _set_if_present(n.get("inputs", {}), ("noise_seed", "seed"), seed):
                seed_set = True
                break
    if not steps_set:
        for _, n in wf.items():
            ct = n.get("class_type", "")
            if ct in ("BasicScheduler", "SamplerCustomAdvanced") or "Scheduler" in ct:
                if _set_if_present(n.get("inputs", {}), ("steps",), steps):
                    steps_set = True
                    break
    report["seed"] = seed_set
    report["steps"] = steps_set
    report["cfg"] = cfg_set if cfg is not None else None

    # --- width / height on latent ---
    wh_set = False
    latents = [(nid, n) for nid, n in wf.items()
               if n.get("class_type") in LATENT_TYPES]
    if not latents:
        nid, node = _by_title(wf, TITLE_LATENT)
        if node:
            latents = [(nid, node)]
    for _, n in latents:
        ins = n.setdefault("inputs", {})
        w = _set_if_present(ins, ("width",), width)
        h = _set_if_present(ins, ("height",), height)
        wh_set = wh_set or (w and h)
    report["size"] = wh_set

    # --- filename prefix on SaveImage ---
    prefix_set = False
    if filename_prefix:
        saves = [(nid, n) for nid, n in wf.items()
                 if n.get("class_type") == "SaveImage"]
        if not saves:
            nid, node = _by_title(wf, TITLE_SAVE)
            if node:
                saves = [(nid, node)]
        for _, n in saves:
            if _set_if_present(n.setdefault("inputs", {}),
                               ("filename_prefix",), filename_prefix):
                prefix_set = True
    report["filename_prefix"] = prefix_set

    return report


def _http_json(url, payload=None, timeout=30):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_bytes(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def submit(host, workflow, client_id, timeout):
    return _http_json(f"{host}/prompt",
                      {"prompt": workflow, "client_id": client_id},
                      timeout=timeout)


def wait_for_history(host, prompt_id, timeout, poll=1.5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            hist = _http_json(f"{host}/history/{prompt_id}", timeout=30)
        except urllib.error.URLError:
            time.sleep(poll)
            continue
        entry = hist.get(prompt_id)
        if entry:
            status = entry.get("status", {})
            if status.get("completed") or status.get("status_str") == "success":
                return entry
            if status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI reported error: {json.dumps(status)[:500]}")
            # completed flag can lag; if outputs already present, accept.
            if entry.get("outputs"):
                return entry
        time.sleep(poll)
    raise TimeoutError(f"Render did not finish within {timeout}s")


def collect_images(entry):
    images = []
    for node_out in entry.get("outputs", {}).values():
        for img in node_out.get("images", []):
            if img.get("type") == "output":
                images.append(img)
    return images


def download_image(host, img, dest_path):
    q = urllib.parse.urlencode({
        "filename": img["filename"],
        "subfolder": img.get("subfolder", ""),
        "type": img.get("type", "output"),
    })
    data = _http_bytes(f"{host}/view?{q}", timeout=120)
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)


def main():
    # Result lines carry Chinese; force UTF-8 stdout so Windows cp1252 consoles
    # (and pipes) don't choke when callers read the JSON.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Render one Z-Image Turbo image via ComfyUI")
    ap.add_argument("--prompt", required=True, help="positive prompt text")
    ap.add_argument("--negative", default="",
                    help="negative prompt (ignored by Z-Image Turbo; kept for compatibility)")
    ap.add_argument("--out", required=True, help="output image path (.png)")
    ap.add_argument("--host", default=os.environ.get("COMFYUI_HOST", "http://127.0.0.1:8188"),
                    help="ComfyUI base URL (env COMFYUI_HOST)")
    ap.add_argument("--workflow",
                    default=os.path.join(os.path.dirname(__file__), "zimage_workflow.api.json"),
                    help="API-format workflow JSON (export via ComfyUI 'Export (API)')")
    ap.add_argument("--seed", type=int, default=None, help="fixed seed (default: random)")
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--cfg", type=float, default=None,
                    help="CFG; Z-Image Turbo uses ~1.0. Leave unset to keep workflow value")
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--filename-prefix", default="storyboard")
    ap.add_argument("--timeout", type=int, default=240, help="render timeout seconds")
    ap.add_argument("--dry-run", action="store_true",
                    help="patch + print workflow, do not submit")
    args = ap.parse_args()

    seed = args.seed if args.seed is not None else random.randint(0, 2**31 - 1)

    def fail(msg, prompt_id=None):
        print(json.dumps({"status": "error", "error": msg,
                          "prompt_id": prompt_id, "seed": seed}, ensure_ascii=False))
        sys.exit(1)

    try:
        with open(args.workflow, "r", encoding="utf-8") as f:
            wf = json.load(f)
    except Exception as e:  # noqa: BLE001
        fail(f"cannot read workflow {args.workflow}: {e}")

    if "nodes" in wf and "prompt" not in wf:
        fail("workflow looks like a UI export (has 'nodes'). Re-export using "
             "ComfyUI 'Workflow -> Export (API)' to get the API format.")

    report = patch_workflow(
        wf, prompt=args.prompt, negative=(args.negative or None), seed=seed,
        steps=args.steps, cfg=args.cfg, width=args.width, height=args.height,
        filename_prefix=args.filename_prefix)

    if not report.get("positive"):
        fail("could not locate a positive prompt node to patch. Tag it with "
             "_meta.title 'POSITIVE_PROMPT' in ComfyUI, or check the workflow.")

    if args.dry_run:
        print(json.dumps({"status": "dry-run", "patch_report": report,
                          "seed": seed, "workflow": wf}, ensure_ascii=False))
        return

    client_id = str(uuid.uuid4())
    try:
        resp = submit(args.host, wf, client_id, timeout=60)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:800]
        fail(f"POST /prompt failed ({e.code}): {body}")
    except urllib.error.URLError as e:
        fail(f"cannot reach ComfyUI at {args.host}: {e}")

    prompt_id = resp.get("prompt_id")
    if not prompt_id:
        fail(f"no prompt_id in response: {json.dumps(resp)[:400]}")

    try:
        entry = wait_for_history(args.host, prompt_id, timeout=args.timeout)
    except Exception as e:  # noqa: BLE001
        fail(str(e), prompt_id=prompt_id)

    images = collect_images(entry)
    if not images:
        fail("render finished but produced no output images", prompt_id=prompt_id)

    saved = []
    try:
        download_image(args.host, images[0], args.out)
        saved.append(args.out)
        # Save any extra images alongside --out.
        base, ext = os.path.splitext(args.out)
        for i, img in enumerate(images[1:], start=1):
            extra = f"{base}_{i}{ext}"
            download_image(args.host, img, extra)
            saved.append(extra)
    except Exception as e:  # noqa: BLE001
        fail(f"failed downloading image: {e}", prompt_id=prompt_id)

    print(json.dumps({"status": "ok", "prompt_id": prompt_id, "seed": seed,
                      "images": saved, "out": args.out,
                      "patch_report": report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
