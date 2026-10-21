# Mobile Resource Index

Recovery and integrity tooling for the RavMP Mobile Android resource archive workflow.

> **Distribution note:** This repository contains tooling and documentation only. Game archives are not included. Publish or host proprietary assets only when you have the legal rights to redistribute them.

## Recover archive packages

1. Place an authorized source archive named `files.zip` in the repository root.
2. Run:

```bash
python scripts/recover_game_archives.py
```

The script validates the source ZIP, rebuilds the expected resource packages under `recovered-zips/`, checks each output archive, and writes SHA-256 hashes to `recovered-zips/SHA256SUMS.txt`. The source archive is not modified.

## Expected package names

`anim.zip`, `audio.zip`, `data.zip`, `fonts.zip`, `models.zip`, `SAMP.zip`, `texdb.zip`, `nodes.zip`, and `sets.zip`.

**Important mapping:** the launcher downloads `nodes.zip` for its local `ext` slot. Keep this mapping aligned with the launcher configuration and extraction logic.

See [docs/asset-hosting.md](docs/asset-hosting.md) for host setup and integration checks.

## Scope

This repository is for recovery, packaging, and integrity checks. Generated ZIPs, source archives, and other large/proprietary game data are intentionally excluded from version control.
