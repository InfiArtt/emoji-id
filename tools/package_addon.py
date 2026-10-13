# -*- coding: UTF-8 -*-
"""Package the Emoji ID add-on into a .nvda-addon archive."""

import os
import zipfile
from pathlib import Path


def package():
    root = Path(__file__).resolve().parent.parent
    addon_dir = root / "addon"
    output_zip = root / "emojiID-1.0.0.nvda-addon"

    if output_zip.exists():
        output_zip.unlink()

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for current_root, dirs, files in os.walk(addon_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__" and not d.endswith(".egg-info")]
            for file in sorted(files):
                if file.endswith(".pyc") or file.endswith(".pyo"):
                    continue
                file_path = Path(current_root) / file
                arcname = file_path.relative_to(addon_dir).as_posix()
                z.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\nSuccessfully built: {output_zip} ({output_zip.stat().st_size:,} bytes)")


if __name__ == "__main__":
    package()
