#!/usr/bin/env bash

LOCK_DIR="${HARNESS_ROOT}/.session-lock"
LOCK_INFO="${HARNESS_ROOT}/.session-lock.info"

lock_is_stale() {
  if [ ! -f "$LOCK_INFO" ]; then
    return 0
  fi
  local pid
  pid="$(awk -F': ' '$1=="pid"{print $2}' "$LOCK_INFO" 2>/dev/null || true)"
  if [ -z "$pid" ]; then
    return 0
  fi
  if kill -0 "$pid" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

clear_stale_lock() {
  if [ -d "$LOCK_DIR" ] && lock_is_stale; then
    rm -rf "$LOCK_DIR"
    rm -f "$LOCK_INFO"
  fi
}

acquire_lock() {
  clear_stale_lock
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    cat >"$LOCK_INFO" <<EOF
pid: $$
started_at: $(timestamp_now)
cwd: $(pwd)
command: ${0:-unknown}
EOF
    return 0
  fi
  printf 'Harness lock is already held.\n' >&2
  if [ -f "$LOCK_INFO" ]; then
    cat "$LOCK_INFO" >&2
  fi
  return 11
}

release_lock() {
  if [ -f "$LOCK_INFO" ]; then
    local pid
    pid="$(awk -F': ' '$1=="pid"{print $2}' "$LOCK_INFO" 2>/dev/null || true)"
    if [ "$pid" = "$$" ]; then
      rm -rf "$LOCK_DIR"
      rm -f "$LOCK_INFO"
    fi
  fi
}

show_lock_info() {
  if [ -f "$LOCK_INFO" ]; then
    cat "$LOCK_INFO"
  else
    printf 'No active harness lock.\n'
  fi
}
