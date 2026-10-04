# Project Walkthrough: Object Permanence Evaluation & Memory Bank Framework

This walkthrough provides a comprehensive guide to the **Object Permanence in AI-Generated Videos** project, explaining the architecture, the **Norfair 2D Kalman Tracking** integration, the **Persistent Memory Bank** framework, empirical results, and how to execute every component of the framework.

---

## 📌 Executive Summary & Current Status

| Component | Target Scope | Current Status | Key Features |
| :--- | :--- | :--- | :--- |
| **Object Tracking** | Real-Time Multi-Object Tracking without Training | **Completed & Integrated** | **[Norfair](https://github.com/tryolabs/norfair)** 2D Kalman filter multi-object tracker with IoU/Euclidean distance matching. Zero training required, eliminating heavy training datasets and tracking fine-tuning. |
| **Object Detection** | Open-Vocabulary & Pretrained Detectors | **Completed** | YOLOv8 / YOLO-World zero-shot open-vocabulary detection. |
| **Persistent Memory Bank** | Long-Term Object State Memory Bank | **Completed & Verified** | 4-state physical visibility machine (`VISIBLE`, `OCCLUDED`, `OUT_OF_BOUNDS`, `LOST`), ballistic dead-reckoning extrapolation ($P(t) = P(t-1) + V \cdot dt$), dashed cyan ghost boxes, online re-ID cost matching. |
| **Quantitative Metrics** | Empirical Evaluation Suite | **Completed** | Detection Consistency, Identity Consistency, Object Permanence Score, Memory Recovery Rate, and MAE trajectory logs. |
| **Cleaned Codebase** | Clutter & Redundant Training Files Removed | **Completed** | Removed unneeded prompt moderation training (`train_vidprom_stream.py`), unused dataset slice scripts (`prepare_dataset.py`, `train_custom_yolo.py`), leaving a clean, high-performance repo. |

---

## 🧠 System Architecture & Workflow

```text
                     INPUT VIDEO FRAME
                            |
                            v
               +---------------------------+
               |     YOLO Object Detector  |
               +-------------+-------------+
                            | (Bounding boxes + confidences)
                            v
               +---------------------------+
               |   Norfair 2D Kalman       | <--- Zero training needed!
               |      Multi-Tracker        |      Real-time Kalman motion estimation
               +-------------+-------------+      with IoU distance matching
                            | (Smooth track IDs + boxes)
                            v
   +---------------------------------------------------+
   |         PERSISTENT MEMORY BANK ENGINE             |
   |                                                   |
   |  1. State Machine:                                |
   |     [VISIBLE] -> [OCCLUDED] -> [OUT_OF_BOUNDS]     |
   |                                                   |
   |  2. Ballistic Dead-Reckoning:                     |
   |     P_hat(t) = P(t-1) + V_smooth * dt             |
   |     Renders dashed cyan ghost box with crosshair  |
   |                                                   |
   |  3. Memory Re-Identification Cost Function:       |
   |     Cost = 0.70 * NormDist + 0.30 * AreaDelta     |
   |     Re-links re-emerging tracks back to Master ID |
   +-------------------------+-------------------------+
                             |
                             v
   +---------------------------------------------------+
   |        OUTPUTS & QUANTITATIVE AUDITS              |
   |  - Annotated Video with [OCCLUDED] Ghost HUD      |
   |  - Healed Persistent Detections CSV               |
   |  - Memory Bank Lifecycle Audit CSV                |
   |  - Memory Recoveries Log CSV                      |
   |  - Summary Metrics Report (Recovery Rate, MAE)    |
   +---------------------------------------------------+
```

---

## 🔬 How Norfair Cuts Short Object Tracking Training

1. **Why Traditional Tracking Needed Training:**
   - Previous pipelines required training or fine-tuning association models (e.g. DeepSORT Re-ID networks) or custom YOLO models on thousands of labeled video frames (`prepare_dataset.py`, `train_custom_yolo.py`).
2. **How Norfair Replaces It:**
   - Norfair uses mathematical kinematic modeling (Kalman filtering) and configurable distance metrics (IoU bounding box overlap or Euclidean centroid distance).
   - Detections from **any** pre-trained YOLO detector are fed directly to `tracker.update(detections)`.
   - Norfair assigns and preserves Track IDs smoothly across frames with Kalman-filtered bounding box estimates, requiring **0 epochs of training**.
3. **Synergy with the Memory Bank:**
   - Norfair excels at continuous frame-by-frame tracking and smoothing out sensor jitter.
   - When severe occlusions occur (e.g., behind a wall for 20-90 frames) where standard trackers drop the object, the **Persistent Memory Bank** steps in with physical dead-reckoning extrapolation and re-ID healing.

---

## 💻 How to Run the Project

### Step 1: Activate Virtual Environment
The virtual environment is located in `d:\projects\gpu ml model\venv`.

**PowerShell:**
```powershell
& "d:\projects\gpu ml model\venv\Scripts\Activate.ps1"
```

**Command Prompt (cmd):**
```cmd
"d:\projects\gpu ml model\venv\Scripts\activate.bat"
```

### Step 2: Run Single Video Evaluation
From the project directory (`d:\projects\gpu ml model\FINAL_YEAR_PROJECT-main`):
```powershell
python main.py --input Object_permanence/data/input/TESTBALL.mp4
```

Or from inside `Object_permanence`:
```powershell
cd Object_permanence
python src/main.py --input data/input/TESTBALL.mp4
```

### Step 3: Run Batch Processing Across All Input Videos
```powershell
python main.py --input_dir Object_permanence/data/input
```

### Step 4: Run with Custom Flags
```powershell
# Specify tracker explicitly (norfair or bytetrack)
python main.py --input Object_permanence/data/input/TESTBALL.mp4 --tracker norfair

# Specify custom target class filter
python main.py --input Object_permanence/data/input/TESTBALL.mp4 --target ball
```

---

## 📊 Outputs & Evaluation Artifacts

All outputs are saved to `Object_permanence/outputs/`:
- `annotated_videos/`: Rendered MP4s with bounding boxes, HUD metrics, and dashed cyan ghost boxes during occlusion.
- `reports/`:
  - `*_detections.csv`: Frame-level detection history.
  - `*_memory_lifecycle.csv`: Object state machine transitions (`VISIBLE`, `OCCLUDED`, `OUT_OF_BOUNDS`, `LOST`).
  - `*_memory_recoveries.csv`: Re-identification match events.
  - `*_summary.json` & `*_summary.txt`: Research benchmark metrics.
- `plots/`: Trajectory paths and event breakdown charts.
