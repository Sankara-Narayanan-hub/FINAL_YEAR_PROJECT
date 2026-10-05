# 🔬 Physical Object Permanence, Attribute Stability & Memory Bank Evaluation Framework

An enterprise-grade, zero-training computer vision and cognitive evaluation framework designed to quantify **physical object permanence**, **semantic attribute stability**, and **long-term occlusion recovery** across modern Generative AI Video Architectures (OpenAI Sora, Kuaishou Kling, Tencent HunyuanVideo, Google Veo-3, THUDM CogVideoX, Alibaba Wanx-2.1, and StepVideo).

---

## 📑 Table of Contents
1. [Executive Summary & Core Innovations](#-executive-summary--core-innovations)
2. [High-Level Architecture & Dataflow](#-high-level-architecture--dataflow)
3. [Zero-Training Norfair 2D Kalman Tracking](#-zero-training-norfair-2d-kalman-tracking)
4. [Persistent Memory Bank & Dead-Reckoning Engine](#-persistent-memory-bank--dead-reckoning-engine)
5. [OpenAI CLIP Zero-Shot Foundation Verifier](#-openai-clip-zero-shot-foundation-verifier)
6. [4-Tier Quantitative Evaluation Framework (Formulas & Examples)](#-4-tier-quantitative-evaluation-framework)
   - [Tier 1: Metric Tracking Accuracy (MTA)](#tier-1-metric-tracking-accuracy-mta)
   - [Tier 2: Prompt-Weighted Metric Accuracy (PWMA)](#tier-2-prompt-weighted-metric-accuracy-pwma)
   - [Tier 3: Occlusion Verification Rate (OVR)](#tier-3-occlusion-verification-rate-ovr)
   - [Tier 4: Semantic Attribute Integrity (SAI)](#tier-4-semantic-attribute-integrity-sai)
7. [Comprehensive Benchmark Results across 25 AI Videos](#-comprehensive-benchmark-results-across-25-ai-videos)
8. [Real-World Physical Object Permanence Stress Test (8 Occlusion Challenges)](#-real-world-physical-object-permanence-stress-test)
9. [Repository Structure & Cleaned File Map](#-repository-structure--cleaned-file-map)
10. [Step-by-Step Reproduction Guide](#-step-by-step-reproduction-guide)
11. [Research Foundations & Academic References](#-research-foundations--academic-references)

---

## 🚀 Executive Summary & Core Innovations

Modern text-to-video generative models demonstrate photorealistic motion, yet fundamentally struggle with **physical commonsense reasoning**—specifically **Object Permanence** (Jean Piaget, 1954; Baillargeon, 1987). When an entity passes behind an occluding barrier, AI video generators frequently:
1. **Erase the object from existence** (0% recovery upon barrier clearing).
2. **Morph geometric and semantic attributes** (e.g., a domestic cat emerges with canine facial structures or altered textures).
3. **Teleport or duplicate entities** (spurious track births and identity fragmentations).

This framework resolves traditional tracking limitations and introduces an objective, multi-tier auditing system:
- **Zero-Training Kinematic Tracking:** Integrates **Norfair** 2D Kalman filter multi-object tracking, eliminating the need for expensive Re-ID network training or dataset fine-tuning.
- **Persistent Memory Bank Engine:** Implements a deterministic 4-state physical automaton (`VISIBLE`, `OCCLUDED`, `OUT_OF_BOUNDS`, `LOST`) with ballistic dead-reckoning extrapolation and dual-metric cost association.
- **OpenAI CLIP Zero-Shot Foundation Verifier:** Couples YOLO-World open-vocabulary detections with a CUDA-accelerated `ViT-B/32` embedding verifier to eliminate hallucinated class labels and compute true semantic cosine similarities.
- **4-Tier Quantitative Evaluation Suite:** Introduces **MTA**, **PWMA**, **OVR**, and the dual-component **SAI** ($\text{STA} \times \text{Temporal Stability}$) to quantitatively distinguish physical tracking performance from semantic hallucination.

```
+---------------------------------------------------------------------------------------------------+
|                                FRAMEWORK PERFORMANCE AT A GLANCE                                 |
+--------------------------+-----------------------+-----------------------+------------------------+
| 25 Benchmark Videos      | 8 Occlusion Stress    | Zero Training Needed  | CUDA CLIP Verification |
| Across 7 AI Architectures| 7/8 Frontier AI Failed| Real-Time Kalman MOT  | ViT-B/32 Foundation    |
+--------------------------+-----------------------+-----------------------+------------------------+
```

---

## 🧠 High-Level Architecture & Dataflow

```mermaid
graph TD
    A["Raw AI Video Stream (.mp4)"] --> B["YOLOv8 / YOLO-World Detector"]
    B -->|"Candidate Bounding Boxes & Confidence"| C["OpenAI CLIP Zero-Shot Foundation Verifier (ViT-B/32)"]
    C -->|"Verified Class Label & Visual Embeddings"| D["Norfair 2D Kalman Multi-Object Tracker"]
    D -->|"Continuous Frame Associations (Track IDs)"| E["Persistent Memory Bank Engine"]
    
    subgraph "Persistent Memory Bank"
        E --> F{"Occlusion Check"}
        F -->|"Object Visible"| G["Update Memory Vector & Kinematic Velocity"]
        F -->|"Object Missing"| H["Ballistic Dead-Reckoning Extrapolation"]
        H --> I["Render Dashed Cyan Ghost HUD"]
        G --> J{"Re-Emergence Event?"}
        H --> J
        J -->|"Candidate Detected"| K["Evaluate Re-ID Cost Matrix (Distance + Area)"]
        K -->|"Cost < Threshold"| L["Heal Track: Restore Master ID"]
        K -->|"Cost >= Threshold"| M["Track Lost / New Track"]
    end

    E --> N["4-Tier Evaluation Metrics Engine"]
    N --> O["MTA: Metric Tracking Accuracy"]
    N --> P["PWMA: Prompt-Weighted Metric Accuracy"]
    N --> Q["OVR: Occlusion Verification Rate"]
    N --> R["SAI: Semantic Attribute Integrity"]
    
    O & P & Q & R --> S["Master Reports, CSV Audits & PDF Methodology"]
```

---

## ⚡ Zero-Training Norfair 2D Kalman Tracking

### Why Traditional Tracking Pipelines Are Obsolete
Previous tracking architectures (DeepSORT, ByteTrack with custom appearance encoders, FairMOT) required:
- Supervised fine-tuning on hundreds of thousands of video frames.
- Re-ID neural networks prone to domain shift when applied to AI-generated surrealist scenes.
- Fragile hyperparameter tuning sensitive to frame rate variations.

### The Norfair Kalman Filter Solution
Norfair utilizes a mathematical, zero-training kinematic state estimator:
1. **State Vector:** Each track maintains position and velocity vectors $[x, y, v_x, v_y]^T$.
2. **Kinematic Projection:** For frame $t$, prior state $\hat{x}_t = F x_{t-1}$ predicts the object position purely through velocity continuation.
3. **IoU & Centroid Distance Association:** Detections are matched to predicted tracks using an optimized Hungarian association algorithm:
   $$\mathcal{D}(d_i, t_j) = 1 - \text{IoU}(B_{d_i}, B_{t_j})$$
4. **Instant Portability:** Works out-of-the-box across any pre-trained detector (YOLOv8, YOLO-World) with zero training epochs, delivering smooth 60+ FPS tracking on RTX GPUs.

---

## 🛡️ Persistent Memory Bank & Dead-Reckoning Engine

When severe occlusions occur (e.g., an object disappears behind a building, tree, or box for 10 to 90 consecutive frames), standard Kalman trackers exceed their `max_distance_threshold` and terminate the track, creating an identity switch upon re-emergence.

The **Persistent Memory Bank** overcomes this through an explicit 4-state physical automaton:

```
                  +----------------------------------------------------+
                  |                                                    |
                  v                                                    |
            +------------+     Occlusion Occurs      +-------------+   | Re-Identification
            |  VISIBLE   | ------------------------> |  OCCLUDED   |   | Match (< Threshold)
            +------------+                           +-------------+   |
                  |                                         |          |
                  | Leaves Frame Boundary                   | Frame Boundary Exceeded
                  v                                         v          |
          +---------------+                         +---------------+  |
          | OUT_OF_BOUNDS |                         |     LOST      | -+
          +---------------+                         +---------------+
```

### 1. Ballistic Dead-Reckoning Extrapolation
During frames where the object is occluded, the memory bank maintains a physical phantom trajectory:
$$\hat{P}(t) = P(t-1) + \vec{V}_{\text{smoothed}} \cdot \Delta t$$
$$\hat{S}(t) = S(t-1)$$
The visualizer renders a dashed cyan ghost bounding box with crosshairs at $\hat{P}(t)$, signaling the model's hypothesis of where the occluded entity physically exists.

### 2. Multi-Metric Re-Identification Cost Function
When a new detection appears near the occlusion boundary, the memory bank matches it against stored persistent states using a normalized spatial-geometric cost:
$$\text{Cost} = w_{\text{dist}} \cdot \frac{\|\vec{P}_{\text{det}} - \hat{P}_{\text{ghost}}\|_2}{D_{\text{frame}}} + w_{\text{area}} \cdot \frac{|A_{\text{det}} - A_{\text{ghost}}|}{\max(A_{\text{det}}, A_{\text{ghost}})}$$
- Default weights: $w_{\text{dist}} = 0.70, w_{\text{area}} = 0.30$.
- If $\text{Cost} \le 0.45$, the new track is matched and its track ID is restored to the original **Master Track ID**.

---

## 👁️ OpenAI CLIP Zero-Shot Foundation Verifier

Standard YOLO detectors operating on arbitrary open prompts frequently misclassify visually ambiguous or morphed entities (e.g., classifying a cat under a table as a "dog", or classifying a lion as a "dog").

To prevent these label hallucinations from distorting tracking metrics, the pipeline integrates a **CLIP Zero-Shot Foundation Verifier** (`ViT-B/32` running on CUDA):
1. **Bounding Box Crop:** For each detected object, the RGB crop is extracted and normalized to $224 \times 224$.
2. **Text Feature Prompts:** A candidate vocabulary is tokenized using prompt engineering templates:
   $$\mathcal{T} = \{\text{"a photo of a " } + c \mid c \in \mathcal{C}_{\text{candidates}}\}$$
3. **Cosine Similarity Embedding:**
   $$\text{Sim}(I_{\text{crop}}, T_c) = \frac{\mathbf{f}_{\text{visual}} \cdot \mathbf{f}_{\text{text}, c}}{\|\mathbf{f}_{\text{visual}}\|_2 \|\mathbf{f}_{\text{text}, c}\|_2}$$
4. **Verification & Correction:** If the detector's raw label disagrees with CLIP's top candidate by more than $\tau_{\text{margin}} = 0.12$, the label is corrected to the foundation model's prediction.

---

## 📐 4-Tier Quantitative Evaluation Framework

The framework assesses generative video quality across 4 complementary tiers.

```
========================================================================================================
                          4-TIER COMPREHENSIVE ACCURACY EVALUATION FRAMEWORK
========================================================================================================
 Tier 1: MTA   | Metric Tracking Accuracy       | Low-level Kalman & IoU temporal tracking fidelity
 Tier 2: PWMA  | Prompt-Weighted Metric Acc.   | Foreground-weighted prompt-aligned trajectory score
 Tier 3: OVR   | Occlusion Verification Rate   | Long-term object permanence & physical recovery rate
 Tier 4: SAI   | Semantic Attribute Integrity  | Dual-component: Taxonomic Accuracy x Temporal Stability
========================================================================================================
```

### Tier 1: Metric Tracking Accuracy (MTA)
Quantifies basic kinematic tracking quality, sensor confidence, detection persistence, and identity switches.

$$\text{MTA} = w_{\text{IoU}} \cdot \overline{\text{IoU}} + w_{\text{conf}} \cdot \overline{c} + w_{\text{det}} \cdot \left(\frac{N_{\text{detected}}}{N_{\text{total}}}\right) - w_{\text{switch}} \cdot \left(\frac{N_{\text{switches}}}{N_{\text{tracks}}}\right)$$

- **Weights:** $w_{\text{IoU}} = 0.40$, $w_{\text{conf}} = 0.30$, $w_{\text{det}} = 0.30$, $w_{\text{switch}} = 0.20$.
- **Example Calculation:**
  $$\overline{\text{IoU}} = 0.82,\quad \overline{c} = 0.88,\quad \frac{N_{\text{detected}}}{N_{\text{total}}} = \frac{114}{120} = 0.95,\quad \frac{N_{\text{switches}}}{N_{\text{tracks}}} = \frac{0}{1} = 0.00$$
  $$\text{MTA} = (0.40 \times 0.82) + (0.30 \times 0.88) + (0.30 \times 0.95) - (0.20 \times 0.00) = 0.328 + 0.264 + 0.285 = \mathbf{87.7\%}$$

---

### Tier 2: Prompt-Weighted Metric Accuracy (PWMA)
Prevents background clutter (e.g., parked cars, clouds, spectator crowds) from artificially inflating or depressing the score of the primary foreground subject specified in the user's prompt.

$$\text{PWMA} = \frac{\sum_{i=1}^M \lambda_i \cdot \text{MTA}_i}{\sum_{i=1}^M \lambda_i}$$

- $\lambda_i = 1.00$ for Primary Foreground Subjects specified in prompt.
- $\lambda_i = 0.50$ for Secondary Interacting Entities.
- $\lambda_i = 0.25$ for Background / Ambient Clutter.
- **Example Calculation:**
  - Foreground subject (Dog): $\text{MTA}_1 = 88.0\%$, $\lambda_1 = 1.00$.
  - Background clutter (Chair): $\text{MTA}_2 = 62.0\%$, $\lambda_2 = 0.25$.
  $$\text{PWMA} = \frac{(1.00 \times 88.0) + (0.25 \times 62.0)}{1.00 + 0.25} = \frac{88.0 + 15.5}{1.25} = \mathbf{82.8\%}$$

---

### Tier 3: Occlusion Verification Rate (OVR)
The core physical permanence benchmark. Measures whether an occluded object survives behind a barrier and successfully recovers upon re-emergence.

$$\text{OVR} = 0.50 \cdot \left(\frac{N_{\text{recovered}}}{N_{\text{occlusions}}}\right) + 0.30 \cdot \overline{S}_{\text{IoU}} + 0.20 \cdot \left(1 - \frac{\text{MAE}_{\text{centroid}}}{D_{\text{diag}}}\right)$$

- **Component 1 (50%):** Binary Re-Identification Recovery Rate.
- **Component 2 (30%):** Post-recovery Bounding Box Spatial Continuity ($\overline{S}_{\text{IoU}}$).
- **Component 3 (20%):** Centroid Dead-Reckoning Extrapolation Accuracy ($1 - \frac{\text{MAE}}{D_{\text{diag}}}$).
- **Example Calculation:**
  - Object successfully recovers: $N_{\text{recovered}} / N_{\text{occlusions}} = 1.0$.
  - Spatial continuity IoU: $\overline{S}_{\text{IoU}} = 0.88$.
  - Centroid drift error: $\text{MAE} = 18\text{px}$, $D_{\text{diag}} = 900\text{px} \implies 1 - \frac{18}{900} = 0.98$.
  $$\text{OVR} = (0.50 \times 1.00) + (0.30 \times 0.88) + (0.20 \times 0.98) = 0.50 + 0.264 + 0.196 = \mathbf{96.0\%}$$
  - *If the object is deleted upon occlusion (e.g. Kling dog):* $N_{\text{recovered}}=0, \overline{S}_{\text{IoU}}=0 \implies \text{OVR} = \mathbf{0.0\%}$.

---

### Tier 4: Semantic Attribute Integrity (SAI)
Evaluates whether the entity preserved its semantic identity, color, scale, and species throughout the sequence without morphing or hallucinating.

$$\text{SAI} = \text{STA} \times \text{Temporal Stability}$$

Where:
$$\text{STA} = \frac{1}{N_{\text{detected}}} \sum_{t=1}^{N_{\text{detected}}} \mathbf{1}[\text{CLIP\_Match}(I_t, \text{Target}) \ge \tau_{\text{CLIP}}]$$
$$\text{Temporal Stability} = 1 - \frac{N_{\text{switches}}}{N_{\text{detected}} - 1}$$

- **Multiplicative Guarantee:** If an object is tracked with 100% stability but CLIP verifies it as the wrong species (e.g., Cat predicted as Dog $\implies \text{STA} = 0\%$), the composite SAI drops immediately to **0.0%**.
- **Example Calculation (Morphing Lion in Wanx):**
  - $\text{STA} = 0.90$ (CLIP confirms lion across 90% of frames).
  - Entity morphs into dog-like snout 3 times in 30 frames: $N_{\text{switches}} = 3 \implies \text{Stability} = 1 - \frac{3}{29} = 0.896$.
  $$\text{SAI} = 0.90 \times 0.896 = \mathbf{80.6\%}$$

---

## 📊 Comprehensive Benchmark Results across 25 AI Videos

The framework was evaluated across a standardized suite of 25 benchmark videos covering 7 leading generative video architectures and physical CGI baselines:

| Architecture | Videos Evaluated | Mean MTA | Mean PWMA | Mean OVR | Mean SAI | Primary Failure Mode Observed |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **OpenAI Sora** | 8 | 71.7% | 75.3% | 52.4% | 63.9% | Partial barrier absorption, scale distortion |
| **Kuaishou Kling** | 3 | 74.4% | 79.5% | 33.3% | 64.9% | Entity deletion behind opaque obstacles |
| **Tencent Hunyuan** | 2 | 74.1% | 78.5% | 0.0% | 72.8% | Complete occlusion drop; camera parallax drift |
| **Google Veo-3** | 3 | 75.1% | 78.7% | 54.2% | 64.6% | Entity dissolution into floor planes |
| **THUDM CogVideoX** | 2 | 79.2% | 82.2% | 60.0% | 80.4% | Best physical permanence; sustained 34-frame recovery |
| **Alibaba Wanx-2.1** | 3 | 72.6% | 77.2% | 50.0% | 60.2% | Attribute & species morphing during motion |
| **StepVideo** | 2 | 76.6% | 81.3% | 50.0% | 69.3% | Scale distortion under geometric barriers |
| **CGI / Real-World Baseline** | 2 | **82.9%** | **88.0%** | **80.0%** | **86.8%** | Controlled ground truth baseline |

![Benchmark Comparison](file:///d:/projects/gpu%20ml%20model/FINAL_YEAR_PROJECT-main/Object_permanence/outputs/plots/benchmark_comparison_plot.png)
![Architecture Summary](file:///d:/projects/gpu%20ml%20model/FINAL_YEAR_PROJECT-main/Object_permanence/outputs/plots/benchmark_architecture_summary.png)

*Full matrix available in [master_benchmark_table.md](file:///d:/projects/gpu%20ml%20model/FINAL_YEAR_PROJECT-main/Object_permanence/outputs/reports/master_benchmark_table.md).*

---

## 💥 Real-World Physical Object Permanence Stress Test

To specifically test **Physical Object Permanence (Piagetian Stage 4/5 Object Permanence)**, 8 dedicated occlusion-challenge videos from VBench-2.0 were subjected to rigorous isolation testing:

| Challenge Scenario | Model | Detected Category | Frames | Occluded Frames | Recovery Rate | SAI Score | Empirical Finding |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `kling_dog_behind_chair` | Kling AI | Dog | 125 | 45 | **0.0% (FAILED)** | 67.2% | **Entity Deleted:** Dog steps behind chair leg and vanishes from existence. Never re-emerges. |
| `veo3_rabbit_table` | Google Veo-3 | Rabbit | 121 | 38 | **0.0% (FAILED)** | 66.7% | **Entity Dissolved:** Rabbit hops behind table and dissolves into the flooring texture. |
| `stepvideo_cat_box_left` | StepVideo | Cat | 125 | 29 | **0.0% (FAILED)** | 66.7% | **Spatial Dropout:** Cat disappears behind box; frame ends with empty scene. |
| `wanx_elephant_behind_car` | Wanx-2.1 | Elephant | 121 | 24 | **0.0% (FAILED)** | 66.7% | **Boundary Dissolution:** Elephant blends into car chassis and does not recover. |
| `hunyuan_monkey_apple` | Hunyuan | Monkey | 121 | 18 | **0.0% (FAILED)** | 66.7% | **Occlusion Failure:** Monkey disappears behind oversized apple graphic. |
| `sora_monkey_apple` | OpenAI Sora | Monkey | 125 | 22 | **0.0% (FAILED)** | 66.7% | **Re-emergence Dropped:** Monkey fails to re-materialize on right side of obstacle. |
| `wanx_cat_box_left` | Wanx-2.1 | Cat | 125 | 15 | **0.0% (FAILED)** | **51.7%** | **Severe Morphing:** Cat changes fur pattern and body volume upon reaching box corner. |
| `cogvideo_dog_behind_chair`| CogVideoX | Dog | 125 | **34** | **100.0% (PASSED)** | **72.6%** | **Flawless Permanence:** Dog walks behind chair, is occluded for 34 frames, and cleanly re-emerges with 100% ID recovery! |

> [!CRITICAL]
> **Key Scientific Takeaway:** 7 out of 8 frontier AI video generation models fail basic physical object permanence. The video diffusion process acts as an auto-regressive 2D texture painter rather than maintaining an internal 3D world model. THUDM CogVideoX was the sole model demonstrating true object persistence across a prolonged 34-frame occlusion.

---

## 🗂️ Repository Structure & Cleaned File Map

```text
FINAL_YEAR_PROJECT-main/
│
├── WALKTHROUGH.md                             # Comprehensive technical guide (this document)
├── README.md                                  # Repository overview and quickstart
├── requirements.txt                           # Master Python package dependencies
├── main.py                                    # Root execution entrypoint
├── test.py                                    # Environment & CUDA readiness verification
│
├── Object_permanence/                         # Canonical core package
│   ├── config/                                # Configuration files
│   ├── data/
│   │   └── input/                             # Benchmark input video dataset (.mp4)
│   ├── outputs/
│   │   ├── plots/                             # Comparison & trajectory visualizations (.png)
│   │   └── reports/                           # Detection logs, lifecycle audits & summary CSVs/JSONs
│   ├── papers/                                # Academic papers & reference PDFs
│   └── src/
│       ├── detector_tracker.py                # YOLO-World + Norfair + CLIP Foundation Verifier
│       ├── main.py                            # Pipeline execution engine
│       ├── memory_bank.py                     # Persistent Memory Bank state machine & dead-reckoning
│       ├── metrics.py                         # 4-Tier evaluation metrics (MTA, PWMA, OVR, SAI)
│       ├── permanence_analyzer.py             # Occlusion lifecycle audit analyzer
│       ├── video_processor.py                 # OpenCV video read/write & frame pipeline
│       └── visualization.py                   # Annotated HUD video rendering with cyan ghost boxes
│
├── batch_run_all_benchmark_videos.py          # Batch runner across all 25 benchmark videos
├── test_new_permanence_videos.py              # Dedicated runner for 8 occlusion stress-test videos
├── generate_master_benchmark_report.py        # Aggregator producing master summary JSON & Markdown
├── generate_comparison_chart.py               # Generates benchmark comparison charts (.png)
├── download_more_ai_videos.py                 # Utility to fetch additional VBench-2.0 clips
├── build_accuracy_methodology_pdf.py          # Generates the official methodology PDF document
├── generate_final_report.py                   # Generates the academic phase-1 Word report (.docx)
│
├── Model_Accuracy_Calculation_Methodology.pdf # Official 7-page publication-grade methodology guide
├── AI23721_Project_Phase_1_Report.docx         # Student project phase-1 formal documentation
└── new_ai_videos_metadata.json                # Metadata and source URLs for AI benchmark videos
```

---

## 💻 Step-by-Step Reproduction Guide

### Step 1: Environment Setup & Activation
Activate the project's dedicated virtual environment:

**PowerShell (Windows):**
```powershell
& "d:\projects\gpu ml model\venv\Scripts\Activate.ps1"
```

**Verify CUDA & Framework Dependencies:**
```powershell
python test.py
```
*Expected Output:*
```text
==================================================
 ENVIRONMENT & FRAMEWORK VERIFICATION
==================================================
PyTorch Version:   2.6.0+cu124
CUDA Available:    True
GPU Device:        NVIDIA GeForce RTX 3050 Laptop GPU
OpenCV Version:    4.11.0
Norfair Version:   2.2.0
Norfair Tracker:   READY (Zero-training 2D Kalman tracking)
==================================================
```

---

### Step 2: Running a Single Video Evaluation
Execute the framework on any video with real-time HUD rendering:

```powershell
python main.py --input Object_permanence/data/input/TESTBALL.mp4
```

To run with target class filtering and open-vocabulary detection:
```powershell
python main.py --input Object_permanence/data/input/sora_car_mountain_road.mp4 --target car
```

---

### Step 3: Run the Master 25-Video Benchmark Suite
To execute the pipeline across the entire benchmark suite:
```powershell
python batch_run_all_benchmark_videos.py
```

To aggregate all metrics into the master matrix:
```powershell
python generate_master_benchmark_report.py
```
*Outputs generated:*
- `Object_permanence/outputs/reports/master_benchmark_summary.json`
- `Object_permanence/outputs/reports/master_benchmark_table.md`
- `Object_permanence/outputs/reports/master_benchmark_matrix.csv`

---

### Step 4: Run the Dedicated Permanence Stress Test
To run the 8 occlusion challenges and evaluate Piagetian permanence:
```powershell
python test_new_permanence_videos.py
```
*Output generated:* `Object_permanence/outputs/reports/permanence_stress_test_results.json`

---

### Step 5: Generate Comparison Charts
Generate the publication comparison bar charts:
```powershell
python generate_comparison_chart.py
```
*Plots generated:*
- `Object_permanence/outputs/plots/benchmark_comparison_plot.png`
- `Object_permanence/outputs/plots/benchmark_architecture_summary.png`

---

### Step 6: Compile the Official Methodology PDF
To recompile `Model_Accuracy_Calculation_Methodology.pdf`:
```powershell
python build_accuracy_methodology_pdf.py
```

---

## 📚 Research Foundations & Academic References

1. **Physical Reasoning & Cognitive Permanence:**
   - Piaget, J. (1954). *The Construction of Reality in the Child*. Basic Books.
   - Baillargeon, R. (1987). "Object permanence in 3½- and 4½-month-old infants." *Developmental Psychology*, 23(5), 655–664.
2. **Multi-Object Kinematic Tracking:**
   - Bewley, A., Ge, Z., Ott, L., Ramos, F., & Upcroft, B. (2016). "Simple online and real-time tracking (SORT)." *IEEE ICIP*.
   - Tryolabs. (2021). "Norfair: Lightweight 2D Kalman Multi-Object Tracking Library." [GitHub: tryolabs/norfair](https://github.com/tryolabs/norfair).
3. **Open-Vocabulary & Foundation Vision-Language Models:**
   - Radford, A., et al. (2021). "Learning Transferable Visual Models From Natural Language Supervision (CLIP)." *ICML*.
   - Cheng, T., et al. (2024). "YOLO-World: Real-Time Open-Vocabulary Object Detection." *CVPR*.
4. **Generative Video Benchmarks:**
   - Huang, Z., et al. (2024). "VBench: Comprehensive Benchmark Suite for Video Generative Models." *CVPR*.
   - Wang, F., et al. (2024). "VidProM: A Million-scale Real Prompt-Video Dataset for Diffusion Models." *NeurIPS*.
   - TOC-Bench. (2024). "Temporal Object Consistency and Permanence Benchmark for Generative Video." *arXiv*.
