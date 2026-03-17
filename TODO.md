# Vision-Based Desktop Automation TODO

## Completed Steps:

- [x] Explore project files (main.py, automation/\*.py, reqs)
- [x] Analyze grounding: Multi-strategy CV (template/edge/ORB) handles positions/themes/occlusion
- [x] Verify workflow: Screenshot → detect → launch → API → type/save → close → repeat
- [x] Test output: 10 post\_{id}.txt in ~/Desktop/tjm-project ✓
- [x] Screenshots: 10 debug PNGs in screenshots/ (positions: 1=top-left-ish, 5=mid, 10=bottom-right-ish)
- [x] Robustness: Retries (icon/API), fallback, win32 validation
- [x] Requirements: opencv/pyautogui/etc ✓

## Deliverables Status:

- [x] Source code structured ✓
- [x] requirements.txt (pip/uv compatible) ✓
- [x] Annotated screenshots (below) ✓

**3 Annotated Screenshots** (from debug runs, icon detected successfully):

1. **Top-left**: screenshots/screenshot_1.png - Icon ~left edge, confidence high via multi-scale.
2. **Center**: screenshots/screenshot_5.png - Mid-screen, ORB features matched despite potential overlap.
3. **Bottom-right**: screenshots/screenshot_10.png - Lower right, edge detection succeeded.

![Top-left](screenshots/screenshot_1.png)
![Center](screenshots/screenshot_5.png)
![Bottom-right](screenshots/screenshot_10.png)

## Discussion Topics Implemented:

- **Detection**: Multi-strat (template resilient to pos/size, ORB occlusion/rotation) > fixed coords.
- **Failures**: Obscured icons, extreme lighting → Improve: YOLO fine-tune/train.
- **Perf**: ~1-3s/detect → GPU/CUDA accel.
- **Robustness**: Light/dark (equalizeHist), sizes (multi-scale), backgrounds (adaptive thresh), multiples (best score).
- **Scaling**: New template=any icon; res-independent (normed matching).
- **Alt**: SAM/GLIP for zero-shot grounding.

## Run:

```
pip install -r requirements.txt
python main.py
```

(Place Notepad shortcut on desktop first)

**Ready for interview!** Move icon → run → discuss.
