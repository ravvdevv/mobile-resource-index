# Game Asset Hosting

This project can download versioned ZIP archives from a host controlled by the project owner. Only publish assets you are authorized to redistribute.

## Expected archive names

- `anim.zip`
- `audio.zip`
- `data.zip`
- `fonts.zip`
- `models.zip`
- `SAMP.zip`
- `texdb.zip`
- `nodes.zip`
- `sets.zip`

The launcher stores the remote `nodes.zip` archive locally under the `ext` name. Preserve this mapping unless the extraction code is changed too.

## Rebuild archives locally

Place your authorized source archive at the project root as `files.zip`, then run:

```bash
python scripts/recover_game_archives.py
```

Generated archives and `SHA256SUMS.txt` are written to `recovered-zips/`. These large local files are gitignored and should not be committed to the source repository.

## Publish and connect a host

1. Choose a hosting account and repository where you are permitted to distribute the files.
2. Upload the nine ZIP archives and `SHA256SUMS.txt` as versioned release assets.
3. Verify every asset URL returns the expected archive, not a 404 or HTML error page.
4. Update `ZIP_URLS` in the launcher's `Config.java` to the verified direct download URLs.
5. Keep the URL order aligned with `ZIP_NAMES`; the `ext` entry must point to `nodes.zip`.
6. Add download checksum verification before extraction and test a clean install on Android.

Do not update the launcher with placeholder URLs. A release tag or URL is not real until the host confirms that the asset exists.
