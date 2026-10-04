# Final Year Project: Object Permanence Evaluation & Memory Bank Framework for AI-Generated Videos

This repository contains the research, dataset analysis framework, model pipeline, and evaluation benchmarks for investigating and resolving **Object Permanence failures in AI-Generated Videos**.

---

## 📌 Project Overview
Generative video models (e.g., Sora, Runway Gen-2, Pika, VideoCrafter) frequently violate basic laws of intuitive physics. Objects that become occluded behind obstacles often morph, lose identity, or vanish permanently upon reappearance.

This project implements:
1. **Zero-Shot Detection & Zero-Training Tracking:** Powered by YOLOv8 / YOLO-World and **[Norfair](https://github.com/tryolabs/norfair)** (lightweight real-time 2D multi-object tracking with Kalman filters and IoU distance matching). By using Norfair, custom model training for object tracking is completely eliminated!
2. **Persistent Memory Bank (50% Milestone):** An explicit state machine (`VISIBLE`, `OCCLUDED`, `OUT_OF_BOUNDS`, `LOST`) with ballistic dead-reckoning extrapolation and kinematic cost matching to preserve entity identity across severe occlusions.
3. **Automated Quantitative Research Metrics:** Measuring Detection Consistency, Identity Consistency, and Object Permanence Score.
4. **Comprehensive Research Artifacts:** Complete IEEE-style research papers, project abstracts, architecture diagrams, and empirical reports.

---

## 📂 Repository Structure

```
FINAL_YEAR_PROJECT/
├── Object_permanence/                     # Core Project Root
│   ├── config/                            # YAML Pipeline & Memory Bank Configurations
│   │   └── config.yaml                    # Tracker (Norfair) & model settings
│   ├── data/
│   │   └── input/                         # Test videos with challenging occlusions
│   ├── outputs/
│   │   ├── annotated_videos/              # Rendered MP4s with ghost boxes and status tags
│   │   ├── plots/                         # Trajectory, breakdown, and metric graphs
│   │   └── reports/                       # CSV lifecycle audits, recoveries, and summary reports
│   ├── src/                               # Source Code Modules
│   │   ├── detector_tracker.py            # YOLO + Norfair multi-object tracking integration
│   │   ├── memory_bank.py                 # 50% Persistent Memory Bank Engine
│   │   ├── metrics.py                     # Quantitative permanence metrics calculator
│   │   ├── permanence_analyzer.py         # Temporal occlusion & switch event analyzer
│   │   ├── video_processor.py             # OpenCV rendering (dashed ghost boxes, HUD)
│   │   └── visualization.py               # Research plot visualizers
│   ├── tools/                             # Demo creation & utility scripts
│   │   ├── analyze_results.py             # Results summary viewer
│   │   ├── create_demo_video.py           # Synthetic occlusion test generator
│   │   ├── download_weights.py            # YOLO weights downloader
│   │   ├── generate_research_paper.py     # IEEE docx generator
│   │   ├── run_pipeline.py                # Quick single-video runner
│   │   └── stream_vidprom.py              # VidProM video streaming utility
│   ├── weights/                           # Model weights (YOLO)
│   ├── architecture_diagram.jpg           # Visual Architecture Diagram
│   └── README.md                          # Detailed module documentation
├── main.py                                # Root entrypoint (routes to Object_permanence/src/main.py)
├── requirements.txt                       # Python dependencies (including norfair & filterpy)
├── WALKTHROUGH.md                         # Detailed project walkthrough & verification
└── README.md                              # This file
```

---

## 🚀 Quick Start Guide

### 1. Activate the Virtual Environment
Activate the virtual environment located in the `gpu ml model` parent folder:

**Windows PowerShell:**
```powershell
# From the project folder:
..\venv\Scripts\Activate.ps1

# Or using the absolute path:
& "d:\projects\gpu ml model\venv\Scripts\Activate.ps1"
```

**Windows Command Prompt (cmd):**
```cmd
..\venv\Scripts\activate.bat
```

### 2. Verify / Install Dependencies
If needed, ensure `norfair` and dependencies are installed:
```powershell
pip install -r requirements.txt
```

### 3. Run the Evaluation Pipeline
Run tracking with **Norfair + Persistent Memory Bank** enabled:

**Single Video:**
```powershell
python main.py --input Object_permanence/data/input/TESTBALL.mp4
```

**Batch Processing on all test videos:**
```powershell
python main.py --input_dir Object_permanence/data/input
```

**Custom Tracker / Parameters:**
```powershell
python main.py --input Object_permanence/data/input/TESTBALL.mp4 --tracker norfair
```

Outputs are automatically saved to `Object_permanence/outputs/`:
- `outputs/annotated_videos/*.mp4`: Video overlays with Norfair tracking and Memory Bank dashed ghost boxes.
- `outputs/reports/*_detections.csv`: Frame-by-frame detections with healed track IDs.
- `outputs/reports/*_memory_lifecycle.csv`: Memory state history for all entities.
- `outputs/reports/*_summary.json`: Quantitative metrics (Detection Consistency, Identity Consistency, Object Permanence Score).
- `outputs/plots/`: Trajectory and breakdown graphs.

---

## 💡 Why Norfair? (Cutting Short Tracking Training)
1. **Zero-Training Tracking:** Unlike heavy deep association models that require extensive annotated datasets and fine-tuning, Norfair uses Kalman filters and 2D spatial distance metrics (e.g., IoU) to track objects from any detector out of the box.
2. **Real-Time Performance:** Norfair adds negligible latency (~80+ FPS on GPU with YOLOv8), ensuring real-time multi-object tracking.
3. **Synergy with Persistent Memory Bank:** Norfair handles continuous frame-to-frame Kalman state estimation and short-gap reacquisition, while the **Persistent Memory Bank** manages long-term physical object permanence across severe occlusions and out-of-frame departures.
