# Building Superposed as a Standalone Executable

The simplest tool is **PyInstaller** — it bundles Python, pygame, and your assets into a single folder (or single file) that runs without a Python install.

---

## 1. Install PyInstaller

```bash
pip install pyinstaller
```

---

## 2. Build the executable

Run this from the project root (same folder as `run.py`):

```bash
pyinstaller --onefile --windowed \
  --add-data "assets:assets" \
  --name "Superposed" \
  run.py
```

| Flag | Purpose |
|------|---------|
| `--onefile` | Pack everything into a single executable |
| `--windowed` | No terminal window on launch (macOS/Windows) |
| `--add-data "assets:assets"` | Bundle the `assets/` folder |
| `--name "Superposed"` | Sets the output filename |

The finished executable appears in `dist/Superposed` (macOS/Linux) or `dist/Superposed.exe` (Windows).

---

## 3. Platform notes

**macOS**
- PyInstaller produces a Unix binary, not a `.app` bundle by default.
- For a proper `.app`, replace `--onefile` with `--onedir` and add `--windowed`. PyInstaller will create `dist/Superposed.app`.
- If Gatekeeper blocks it: right-click → Open, or run `xattr -cr dist/Superposed.app`.

**Windows**
- Run the same command in PowerShell or CMD (change the path separator in `--add-data` to a semicolon on older PyInstaller versions: `"assets;assets"`).
- PyInstaller 6+ accepts `:` on all platforms.

**Linux**
- `--windowed` is a no-op; omit it if you want terminal output for debugging.

---

## 4. Fix asset paths at runtime

pygame loads assets with relative paths like `"assets/sprites/..."`. These break inside a PyInstaller bundle because the CWD is no longer the project root.

Add this helper near the top of `src/main.py` (or a shared `utils.py`):

```python
import sys, os

def resource_path(relative: str) -> str:
    """Return the absolute path to a bundled resource."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)
```

Then replace any bare `open("assets/...")` or `pygame.image.load("assets/...")` calls with `resource_path("assets/...")`.

> If your sprites are generated procedurally (no files loaded from disk), you can skip this step.

---

## 5. Quick test before distributing

```bash
# Run the built binary directly to catch missing assets early
./dist/Superposed          # macOS / Linux
dist\Superposed.exe        # Windows
```

---

## 6. Reducing file size (optional)

```bash
pip install pyinstaller upx
```

UPX compresses the binary automatically when PyInstaller finds it on your PATH. Typical reduction: 30–50 %.

---

## Alternative: Nuitka (faster startup, smaller binary)

```bash
pip install nuitka
python -m nuitka --standalone --onefile \
  --include-data-dir=assets=assets \
  --output-filename=Superposed \
  run.py
```

Nuitka compiles Python to C and produces a faster binary, but takes significantly longer to build. Recommended only if startup time or binary size matters.
