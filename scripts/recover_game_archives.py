#!/usr/bin/env python3
"""Rebuild RavMP Mobile's nine expected ZIP packages from a recovered Android files.zip.

Run from the repository root:
    python scripts/recover_game_archives.py

The source archive is read-only. Outputs go to recovered-zips/ and are intentionally
not committed. Review the manifest before privately hosting any recovered assets.
"""
from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "files.zip"
OUTPUT = ROOT / "recovered-zips"

DIRECTORY_PACKAGES = ("anim", "audio", "data", "fonts", "models", "SAMP", "texdb")
ROOT_RUNTIME_RE = re.compile(
    r"^(?:NODES\d+\.DAT|ROADBLOX\.DAT|spath0\.dat|stream\.ini|tracks\d*\.dat|train\d*\.dat)$",
    re.IGNORECASE,
)
SET_FILES = {"gta_sa.set", "gtasatelem.set"}
# These are device/user state or logs, not distributable base-game assets.
EXCLUDED_SAMP_FILES = {"SAMP/favorites.json", "SAMP/settings.ini", "SAMP/svlog.txt"}
EXCLUDED_MEMBERS = {
    "anim/anim.img.temp",  # interrupted-download/temp copy, not the final game asset
    "audio/CONFIG/AudioEventHistory.txt",  # runtime history log
}
EXCLUDED_ROOT_FILES = {"avatar.jpg", "samp_log.txt"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if not SOURCE.is_file():
        print(f"Missing source archive: {SOURCE}", file=sys.stderr)
        return 1

    OUTPUT.mkdir(parents=True, exist_ok=True)
    # `nodes.zip` is the remote filename configured for the local `ext.zip` slot.
    # Remove the old intermediate name if this script was run before that mapping was fixed.
    stale_ext_archive = OUTPUT / "ext.zip"
    if stale_ext_archive.exists():
        stale_ext_archive.unlink()

    packages: dict[str, list[str]] = {name: [] for name in (*DIRECTORY_PACKAGES, "nodes", "sets")}

    with zipfile.ZipFile(SOURCE, "r") as source:
        bad_member = source.testzip()
        if bad_member:
            print(f"Source archive is corrupt at: {bad_member}", file=sys.stderr)
            return 2

        for info in source.infolist():
            if info.is_dir() or not info.filename.startswith("files/"):
                continue
            relative = info.filename[len("files/"):]
            if not relative or "__MACOSX" in relative or ".DS_Store" in relative:
                continue
            first, separator, _ = relative.partition("/")

            if relative in EXCLUDED_MEMBERS:
                continue
            if first in DIRECTORY_PACKAGES:
                if first == "SAMP" and relative in EXCLUDED_SAMP_FILES:
                    continue
                packages[first].append(info.filename)
            elif not separator and relative.lower() not in {x.lower() for x in EXCLUDED_ROOT_FILES}:
                if ROOT_RUNTIME_RE.fullmatch(relative):
                    packages["nodes"].append(info.filename)
                elif relative in SET_FILES:
                    packages["sets"].append(info.filename)

        empty = [name for name, members in packages.items() if not members]
        if empty:
            print("Refusing to create incomplete packages; no source members found for: " + ", ".join(empty), file=sys.stderr)
            return 3

        results: list[tuple[str, int, int, str]] = []
        for name, members in packages.items():
            destination = OUTPUT / f"{name}.zip"
            with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as target:
                for member in sorted(members):
                    # Strip only the recovered archive's outer "files/" directory so
                    # extraction lands in the exact paths the Android launcher expects.
                    entry_name = member[len("files/"):]
                    target.writestr(entry_name, source.read(member))
            with zipfile.ZipFile(destination, "r") as check:
                bad_member = check.testzip()
                if bad_member:
                    print(f"Generated archive is corrupt: {destination.name}:{bad_member}", file=sys.stderr)
                    return 4
                count = len(check.infolist())
                uncompressed = sum(i.file_size for i in check.infolist() if not i.is_dir())
            results.append((destination.name, count, uncompressed, sha256(destination)))

    manifest = OUTPUT / "SHA256SUMS.txt"
    manifest.write_text("\n".join(f"{digest}  {name}" for name, _, _, digest in results) + "\n", encoding="utf-8")
    print(f"Recovered archives from: {SOURCE.name}")
    print(f"Output directory: {OUTPUT}")
    print("\nArchive          Entries   Uncompressed bytes   SHA-256")
    for name, count, size, digest in results:
        print(f"{name:<16} {count:>7} {size:>21,}   {digest}")
    print("\nExcluded personal/runtime state and temporary files: avatar.jpg, samp_log.txt, SAMP/favorites.json, SAMP/settings.ini, SAMP/svlog.txt, anim/anim.img.temp, audio/CONFIG/AudioEventHistory.txt, CLEO/, MonetLoader/, mods/, download/.")
    print("Mapping note: nodes.zip is the remote filename for the launcher's local ext.zip slot.")
    print("Note: generated ZIPs are for recovery/testing. Do not publicly redistribute proprietary game assets without the rights to do so.")
    print(f"Manifest: {manifest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
