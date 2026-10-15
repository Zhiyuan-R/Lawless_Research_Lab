#!/usr/bin/env bash
# harvey_lab/setup.sh — prepare a local Harvey LAB (Legal Agent Benchmark) environment.
#
# Idempotent. Steps:
#   1. Clone harveyai/harvey-labs at a pinned ref into harvey_lab/vendor/harvey-labs
#      (~4 GB: the 2,010 task matter files live in the repo).
#   2. uv sync the harness (lab_core) and its provider SDKs.
#   3. Install pandoc >= 3.5 on the host (the grader converts .docx with it).
#   4. Install podman and provide the lab-sandbox:latest image: pull the upstream
#      image from ghcr.io, else build harvey_lab/sandbox/Dockerfile.ubuntu.
#
# Env overrides:
#   HARVEY_LABS_REF   git tag/commit to pin (default: v1.2.0)
#   SKIP_SANDBOX=1    skip step 4 (e.g. to only browse tasks)

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$HERE/vendor/harvey-labs"
REF="${HARVEY_LABS_REF:-v1.2.0}"
REPO_URL="https://github.com/harveyai/harvey-labs.git"

log() { printf "\033[1;34m[harvey-lab]\033[0m %s\n" "$*"; }

# 1. Pinned checkout
if [[ ! -d "$VENDOR/.git" ]]; then
    log "cloning $REPO_URL@$REF (large: ~4 GB of task documents)"
    mkdir -p "$(dirname "$VENDOR")"
    git clone --depth 1 --branch "$REF" "$REPO_URL" "$VENDOR"
else
    current="$(git -C "$VENDOR" describe --tags --exact-match 2>/dev/null || git -C "$VENDOR" rev-parse --short HEAD)"
    if [[ "$current" != "$REF" ]]; then
        log "switching checkout $current -> $REF"
        git -C "$VENDOR" fetch --depth 1 origin "refs/tags/$REF:refs/tags/$REF" 2>/dev/null \
            || git -C "$VENDOR" fetch --depth 1 origin "$REF"
        git -C "$VENDOR" checkout -q "$REF" 2>/dev/null || git -C "$VENDOR" checkout -q FETCH_HEAD
    fi
fi
log "harvey-labs at $(git -C "$VENDOR" rev-parse --short HEAD) ($REF)"

# 2. Python deps
command -v uv >/dev/null || { log "installing uv"; curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
(cd "$VENDOR" && uv sync --all-extras)

# 3. pandoc >= 3.5 for grading .docx deliverables
pandoc_ok() {
    command -v pandoc >/dev/null || return 1
    local v; v="$(pandoc --version | head -1 | awk '{print $2}')"
    [[ "$(printf '%s\n3.5\n' "$v" | sort -V | head -1)" == "3.5" ]]
}
if ! pandoc_ok; then
    log "installing pinned pandoc"
    sudo_cmd=""; [[ $EUID -ne 0 ]] && sudo_cmd="sudo"
    $sudo_cmd sh "$VENDOR/lab_core/sandbox/install_pandoc.sh"
    hash -r
fi
log "$(pandoc --version | head -1)"

[[ "${SKIP_SANDBOX:-0}" == "1" ]] && { log "SKIP_SANDBOX=1, done"; exit 0; }

# 4. podman + sandbox image
if ! command -v podman >/dev/null; then
    log "installing podman"
    if command -v apt-get >/dev/null; then
        sudo_cmd=""; [[ $EUID -ne 0 ]] && sudo_cmd="sudo"
        $sudo_cmd apt-get update -qq && $sudo_cmd apt-get install -y -qq podman
    elif command -v brew >/dev/null; then
        brew install podman && (podman machine init || true) && podman machine start || true
    else
        echo "Install podman manually: https://podman.io/docs/installation" >&2; exit 1
    fi
fi

if podman image inspect lab-sandbox:latest >/dev/null 2>&1; then
    log "sandbox image lab-sandbox:latest present"
elif podman pull -q ghcr.io/harveyai/lab-sandbox:latest >/dev/null 2>&1; then
    podman tag ghcr.io/harveyai/lab-sandbox:latest lab-sandbox:latest
    log "pulled upstream sandbox image"
else
    log "ghcr.io pull failed; building fallback image from sandbox/Dockerfile.ubuntu"
    ctx="$(mktemp -d)"
    trap 'rm -rf "$ctx"' EXIT
    cp "$HERE/sandbox/Dockerfile.ubuntu" "$ctx/Dockerfile"
    cp "$VENDOR/lab_core/sandbox/install_pandoc.sh" "$ctx/"
    cp "$VENDOR/lab_core/sandbox/parsers/parse_doc.py" "$ctx/"
    # Trust a TLS-intercepting egress proxy's CA during the build, if one is configured.
    ca="${PROXY_CA_BUNDLE:-/root/.ccr/ca-bundle.crt}"
    if [[ -r "$ca" ]]; then cp "$ca" "$ctx/proxy-ca.crt"; else : > "$ctx/proxy-ca.crt"; fi
    build_args=()
    for v in HTTPS_PROXY https_proxy; do
        [[ -n "${!v:-}" ]] && build_args+=(--build-arg "$v=${!v}")
    done
    podman build --network=host "${build_args[@]}" -t lab-sandbox:latest "$ctx"
fi

log "ready. Next: add API keys to $VENDOR/.env, then run harvey_lab/run_smoke_test.sh"
