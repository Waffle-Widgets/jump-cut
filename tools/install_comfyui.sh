#!/usr/bin/env bash
# Install ComfyUI + the Qwen-Image models that tools/gen_images.py expects, on this machine.
#
# Written for GameStation (RTX 5090 / Blackwell -> cu128 wheels). M Station already has this
# set up; this gives the second machine the same image pipeline so the art stays consistent.
#
# IDEMPOTENT AND RESUMABLE on purpose: the Remote Peer re-runs it from the top if the machine
# restarts mid-download. Every step checks for its own output and skips if it is already there,
# and huggingface_hub resumes partial files.
set -u

COMFY="/c/Users/thecl/ComfyUI"
COMFY_WIN='C:\Users\thecl\ComfyUI'
PY313="/c/Program Files/WindowsApps/PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0/python3.13.exe"
VPY="$COMFY/venv/Scripts/python.exe"

say() { echo "[$(date '+%H:%M:%S')] $*"; }

# ---------------------------------------------------------------- 1. the repo
if [ ! -d "$COMFY/.git" ]; then
  say "cloning ComfyUI into $COMFY"
  git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$COMFY" || exit 1
else
  say "ComfyUI already cloned, skipping"
fi

# ---------------------------------------------------------------- 2. the venv
if [ ! -f "$VPY" ]; then
  say "creating venv with Python 3.13"
  "$PY313" -m venv "$COMFY/venv" || exit 1
else
  say "venv already exists, skipping"
fi
"$VPY" -m pip install --upgrade pip -q

# ------------------------------------------------- 3. torch for Blackwell (sm_120)
if ! "$VPY" -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
  say "installing torch (cu128 - required for the 5090; cu124 wheels have no sm_120 kernels)"
  "$VPY" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 || exit 1
else
  say "torch with CUDA already present, skipping"
fi

say "installing ComfyUI requirements"
"$VPY" -m pip install -r "$COMFY/requirements.txt" || exit 1
"$VPY" -m pip install -q huggingface_hub || exit 1

# ---------------------------------------------------------------- 4. the models
# Exact filenames are dictated by tools/gen_images.py - do not rename them.
mkdir -p "$COMFY/models/diffusion_models" "$COMFY/models/text_encoders" "$COMFY/models/vae"

say "fetching Qwen-Image models (~45 GB total, resumable)"
"$VPY" - <<'PYEOF'
import os, sys
from huggingface_hub import HfApi, hf_hub_download

COMFY = r"C:\Users\thecl\ComfyUI"
api = HfApi()

# (exact filename gen_images.py asks for, which ComfyUI folder it belongs in, required?)
WANT = [
    ("qwen_image_2512_fp8_e4m3fn.safetensors",     "diffusion_models", True),
    ("qwen_2.5_vl_7b_fp8_scaled.safetensors",      "text_encoders",    True),
    ("qwen_image_vae.safetensors",                 "vae",              True),
    ("qwen_image_edit_2511_fp8mixed.safetensors",  "diffusion_models", False),  # only used with --ref
]
# Comfy-Org's repackaged single-file releases - the ones ComfyUI's own docs point at.
REPOS = [
    "Comfy-Org/Qwen-Image_ComfyUI",
    "Comfy-Org/Qwen-Image-Edit_ComfyUI",
]

# Build one index of every file in those repos, matched on basename so a repo
# reshuffling its split_files/ layout doesn't break this.
index = {}
for repo in REPOS:
    try:
        for path in api.list_repo_files(repo):
            index.setdefault(os.path.basename(path), []).append((repo, path))
    except Exception as e:
        print(f"  ! could not list {repo}: {e}")

failed_required = []
for name, folder, required in WANT:
    dest_dir = os.path.join(COMFY, "models", folder)
    dest = os.path.join(dest_dir, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 1_000_000:
        print(f"  = {name} already present ({os.path.getsize(dest)/2**30:.1f} GB), skipping")
        continue
    hits = index.get(name)
    if not hits:
        print(f"  ! {name} not found in any known repo")
        if required:
            failed_required.append(name)
        continue
    repo, path = hits[0]
    print(f"  > {name}  <-  {repo}/{path}")
    try:
        got = hf_hub_download(repo_id=repo, filename=path, local_dir=dest_dir)
        # flatten: gen_images.py wants the file directly in the folder, not under split_files/
        if os.path.abspath(got) != os.path.abspath(dest):
            os.replace(got, dest)
        print(f"  + {name} done ({os.path.getsize(dest)/2**30:.1f} GB)")
    except Exception as e:
        print(f"  ! {name} failed: {e}")
        if required:
            failed_required.append(name)

if failed_required:
    print("MISSING REQUIRED: " + ", ".join(failed_required))
    sys.exit(2)
print("all required models present")
PYEOF
MODEL_RC=$?
if [ "$MODEL_RC" != "0" ]; then
  say "model download incomplete (rc=$MODEL_RC) - re-running this job will resume"
  exit "$MODEL_RC"
fi

# ---------------------------------------------------------------- 5. prove it runs
say "starting ComfyUI to verify"
"$VPY" "$COMFY/main.py" --listen 127.0.0.1 --port 8188 >"$COMFY/comfy.log" 2>&1 &
CPID=$!
for i in $(seq 1 120); do
  sleep 2
  if curl -s --max-time 3 http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
    say "ComfyUI is up on 127.0.0.1:8188"
    curl -s http://127.0.0.1:8188/system_stats
    echo
    kill "$CPID" 2>/dev/null
    say "DONE - tools/gen_images.py can now run on this machine"
    exit 0
  fi
done
kill "$CPID" 2>/dev/null
say "ComfyUI did not come up - see $COMFY/comfy.log"
exit 1
