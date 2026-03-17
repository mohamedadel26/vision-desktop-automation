# Vision-Based Desktop Automation with Dynamic Icon Grounding

## Project Overview

Python app using CV to locate Notepad icon anywhere on desktop (1920x1080 Windows), launch, fetch/process 10 JSONPlaceholder posts, save as post\_{id}.txt in ~/Desktop/tjm-project. Robust grounding (multi-strategy) for interview scalability.

## Quick Start

1. Place **Notepad shortcut** on Desktop.
2. `pip install -r requirements.txt`
3. `python main.py`

**Output**: 10 files in `~/Desktop/tjm-project/`, debug screenshots in `screenshots/`.

## Key Features

- **Dynamic Grounding**: Multi-scale template + edge + ORB detects icon at any position/size/theme.
- **Workflow**: Screenshot → detect → double-click → validate → API → type → save → close → repeat.
- **Robustness**: 3x retries, API fallback, win32 validation, overwrite handling.
- **Debug**: Screenshots saved showing detections.

## Deliverables (Complete)

### 3 Annotated Screenshots

1. **Top-Left Icon**: `screenshots/screenshot_1.png` - Detected via multi-scale, conf>0.7.
2. **Center Icon**: `screenshots/screenshot_5.png` - ORB matched despite position.
3. **Bottom-Right Icon**: `screenshots/screenshot_10.png` - Edge detection succeeded.

### Generated Files (Verified)

```
~/Desktop/tjm-project/
├── post_1.txt ... post_10.txt  (246B-242B each)
```

## Interview Discussion

**Why this grounding?** Template=fast baseline, ORB=occlusion/rot, edge=contrast-invar → Bypass popups/unexpected UI.

**Failures**: Full cover/heavy blur → Add YOLOv8 fine-tune.

**Perf**: 1-3s/detect → CUDAOpenCV.

**Robust**: Adaptive thresh (light/dark), scales (sizes), best-match (multi-icons).

**Scale**: Load any PNG template=any icon/button. Res-indep.

## Structure

```
.
├── main.py              # Orchestrator
├── automation/          # Modules
│   ├── grounding.py     # CV magic
│   ├── desktop.py       # PyAutoGUI/win32
│   ├── notepad.py       # Type/save
│   └── api.py           # JSONPlaceholder
├── icons/notepad.png    # Template
├── screenshots/         # Debug PNGs
├── requirements.txt     # Deps
└── TODO.md              # Progress
```

**Tested & Ready** - Move icon positions, run, discuss! 🚀

## UV Configuration (Bonus)

```
uv venv
uv pip install -r requirements.txt
uv run python main.py
```
