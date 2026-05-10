"""
Env Guard - Prevent execve E2BIG by capping cocoon's persistent envp.

Cocoon's StateManager merges every variable from each block's
'export -p' into a persistent dictionary that is then re-passed as
envp to every subsequent subprocess. With Yocto workflows that source
oe-init-build-env and run bitbake-layers, this dictionary grows
without bound and eventually exceeds the kernel's ARG_MAX, causing
subprocess.Popen's execve to fail with [Errno 7] Argument list too
long.

This module centralises the three guards that prevent that:
  1. A denylist of known-noisy bitbake/oe internals.
  2. A per-variable byte cap (MAX_VAR_BYTES, well below MAX_ARG_STRLEN).
  3. A total env-size budget (MAX_ENV_BYTES, enforced after each merge).
"""

from typing import Dict, Set

from .colors import Colors


# Per-variable cap. 32 KiB is well below MAX_ARG_STRLEN (~128 KiB).
MAX_VAR_BYTES = 32 * 1024

# Total envp budget. Linux ARG_MAX is ~2 MiB and must also fit argv;
# 1 MiB leaves comfortable headroom.
MAX_ENV_BYTES = 1 * 1024 * 1024

# Bitbake / OE internals that legitimately get re-exported on every
# block but must NEVER be carried across cocoon blocks. Keeping them
# is what causes envp to grow without bound.
DENYLISTED_PREFIXES = (
    'BB_ORIGENV',
    'BB_HASHCONFIG',
    'BB_INVALIDCONF',
    'BB_BASEHASH',
    'BB_TASKHASH',
    'BB_SETSCENE',
    'BB_RUNTASK',
    'BB_CURRENT',
    'BBPATH_EXTRA',
    'BB_RUNFMT',
)

DENYLISTED_EXACT = {
    '_',                       # bash internal, useless to persist
    'OLDPWD',                  # tracked separately
    'SHLVL',                   # bash maintains this
    'PIPESTATUS',
}

# Baseline vars that must never be evicted by the size-budget enforcer.
BASELINE_KEYS = {
    'PATH', 'HOME', 'USER', 'LOGNAME', 'SHELL', 'TERM',
    'LANG', 'LC_ALL', 'PWD', 'TMPDIR',
}


def is_denylisted_env_var(name: str) -> bool:
    """Return True if `name` is a bitbake/oe internal that must not
    be persisted across cocoon blocks."""
    if name in DENYLISTED_EXACT:
        return True
    for prefix in DENYLISTED_PREFIXES:
        if name.startswith(prefix):
            return True
    return False


def is_oversized_value(value: str) -> bool:
    """Return True if `value` exceeds the per-variable byte cap."""
    return len(value.encode('utf-8', errors='replace')) > MAX_VAR_BYTES


def warn_oversized(var_name: str, value: str, already_warned: Set[str]):
    """Emit a one-time warning that `var_name` was dropped for being
    larger than MAX_VAR_BYTES. Mutates `already_warned` to suppress
    repeat warnings for the same var."""
    if var_name in already_warned:
        return
    print(Colors.colorize(
        f"  [env_guard] dropping oversized env var "
        f"{var_name} ({len(value)} bytes > {MAX_VAR_BYTES})",
        Colors.YELLOW,
    ))
    already_warned.add(var_name)


def total_env_size(env: Dict[str, str]) -> int:
    """Approximate envp size: sum of len("KEY=VALUE\\0") for every entry."""
    return sum(len(k) + len(v) + 2 for k, v in env.items())


def enforce_env_size_budget(env: Dict[str, str]):
    """If `env` exceeds MAX_ENV_BYTES, drop the largest non-baseline keys
    until back under budget. Mutates `env` in place."""
    size = total_env_size(env)
    if size <= MAX_ENV_BYTES:
        return

    candidates = sorted(
        (
            (k, len(k) + len(env[k]) + 2)
            for k in env
            if k not in BASELINE_KEYS
        ),
        key=lambda kv: kv[1],
        reverse=True,
    )

    for key, ksz in candidates:
        if size <= MAX_ENV_BYTES:
            break
        print(Colors.colorize(
            f"  [env_guard] env-budget exceeded, dropping "
            f"{key} ({ksz} bytes)",
            Colors.YELLOW,
        ))
        env.pop(key, None)
        size -= ksz
