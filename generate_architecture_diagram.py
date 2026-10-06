import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

def create_architecture_diagram():
    # Set up high-resolution canvas
    fig, ax = plt.subplots(figsize=(20, 11), dpi=300)
    fig.patch.set_facecolor('#0B0F19') # Deep tech dark background
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette - Professional Modern Research Theme
    c_bg_dark = '#0B0F19'
    c_card_bg = '#131B2E'
    c_card_border = '#1E293B'
    c_text_white = '#F8FAFC'
    c_text_muted = '#94A3B8'
    c_text_dim = '#64748B'

    # Accent Colors for Layers
    c_blue = '#38BDF8'      # Vision & Detection
    c_indigo = '#818CF8'    # CLIP Foundation
    c_teal = '#2DD4BF'      # Kalman Tracking
    c_purple = '#C084FC'    # Memory Bank
    c_amber = '#FBBF24'     # 4-Tier Evaluation
    c_emerald = '#34D399'   # Outputs & Audits

    # 1. Main Header
    ax.text(50, 96.5, "PHYSICAL OBJECT PERMANENCE & ATTRIBUTE CONSISTENCY FRAMEWORK",
            fontsize=20, weight='bold', color=c_text_white, ha='center', va='center', fontfamily='sans-serif')
    ax.text(50, 93.8, "End-to-End Zero-Training System Architecture for Generative AI Video Auditing & Cognitive Memory Recovery",
            fontsize=11, color=c_blue, ha='center', va='center', fontfamily='sans-serif')

    # Helper function to draw rounded container cards
    def draw_card(x, y, w, h, bg_color, border_color, border_width=1.5, radius=1.2, alpha=1.0):
        bbox = FancyBboxPatch((x, y), w, h,
                              boxstyle=f"round,pad={radius},rounding_size={radius}",
                              facecolor=bg_color, edgecolor=border_color,
                              linewidth=border_width, alpha=alpha, zorder=2)
        ax.add_patch(bbox)
        return bbox

    # Helper function for arrows
    def draw_arrow(x1, y1, x2, y2, color=c_blue, style='->', lw=2, dashed=False, label="", label_pos=(0.5, 0.5), label_col=c_text_muted):
        ls = '--' if dashed else '-'
        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle=ArrowStyle("Simple", head_length=5, head_width=5, tail_width=1.2),
            color=color, linewidth=lw, linestyle=ls, zorder=4
        )
        ax.add_patch(arrow)
        if label:
            lx = x1 + (x2 - x1) * label_pos[0]
            ly = y1 + (y2 - y1) * label_pos[1]
            ax.text(lx, ly, label, fontsize=8, color=label_col, weight='bold', ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=c_bg_dark, edgecolor='none', alpha=0.85), zorder=5)

    # =========================================================================
    # COLUMN 1: INPUT & MULTIMODAL INGESTION LAYER (X: 3 - 22)
    # =========================================================================
    draw_card(3, 10, 19, 79, '#111827', '#374151', border_width=1.5)
    ax.text(12.5, 86.5, "1. INPUT INGESTION LAYER", fontsize=11, weight='bold', color=c_blue, ha='center', va='center')
    ax.text(12.5, 84.5, "Video Stream & Conditioning", fontsize=8, color=c_text_muted, ha='center', va='center')

    # Sub-card 1: Video Sources
    draw_card(4.5, 62, 16, 19, '#1F2937', '#4B5563', radius=0.8)
    ax.text(12.5, 78.5, "Generative Video Stream", fontsize=9.5, weight='bold', color=c_text_white, ha='center')
    ax.text(12.5, 75.8, "• Sora • Kling • Hunyuan\n• Veo-3 • CogVideoX • Wanx\n• Real-World / CGI Baselines",
            fontsize=8, color=c_text_muted, ha='center', va='top', linespacing=1.3)
    ax.text(12.5, 64, "Raw Frames: 24-60 FPS", fontsize=7.5, color=c_blue, ha='center', weight='bold')

    # Sub-card 2: Prompt Conditioning
    draw_card(4.5, 38, 16, 20, '#1F2937', '#4B5563', radius=0.8)
    ax.text(12.5, 55.5, "Prompt Conditioning", fontsize=9.5, weight='bold', color=c_text_white, ha='center')
    ax.text(12.5, 52.8, 'Text Prompt Specifier:\n"A dog is behind a chair,\nthen runs to the right..."',
            fontsize=8, color='#FDE047', ha='center', va='top', style='italic', linespacing=1.2)
    ax.text(12.5, 41, "Subject & Barrier Entities", fontsize=7.5, color=c_text_muted, ha='center')

    # Sub-card 3: Video Processor
    draw_card(4.5, 14, 16, 20, '#1F2937', '#4B5563', radius=0.8)
    ax.text(12.5, 31.5, "OpenCV Video Engine", fontsize=9.5, weight='bold', color=c_text_white, ha='center')
    ax.text(12.5, 28.5, "• Frame Decoder & Buffer\n• Dynamic Aspect Scaling\n• Resolution: 1080p / 720p\n• Timestamp Normalization",
            fontsize=8, color=c_text_muted, ha='center', va='top', linespacing=1.3)

    # =========================================================================
    # COLUMN 2: PERCEPTION & FOUNDATION VERIFICATION (X: 25 - 46)
    # =========================================================================
    draw_card(25, 10, 21, 79, '#0F172A', '#1E3A8A', border_width=1.5)
    ax.text(35.5, 86.5, "2. PERCEPTION & FOUNDATION", fontsize=11, weight='bold', color=c_indigo, ha='center', va='center')
    ax.text(35.5, 84.5, "Detection & Zero-Shot Verification", fontsize=8, color=c_text_muted, ha='center', va='center')

    # Sub-card 1: YOLO Detector
    draw_card(26.5, 53, 18, 28, '#1E293B', '#3B82F6', radius=0.8)
    ax.text(35.5, 78.5, "YOLOv8 / YOLO-World", fontsize=10, weight='bold', color=c_text_white, ha='center')
    ax.text(35.5, 76, "Open-Vocabulary Detector", fontsize=8, color=c_blue, ha='center')
    ax.text(35.5, 72.5, "• Backbone: CSPDarknet\n• Candidate Bounding Boxes [B_t]\n• Confidence Scores [c_j]\n• Multi-Class Vocab Filter",
            fontsize=8, color=c_text_muted, ha='center', va='top', linespacing=1.3)
    ax.text(35.5, 56.5, "Confidence Threshold: 0.35 - 0.40", fontsize=7.5, color='#38BDF8', ha='center', weight='bold')

    # Sub-card 2: CLIP Verifier
    draw_card(26.5, 14, 18, 35, '#1E293B', '#6366F1', radius=0.8)
    ax.text(35.5, 46.5, "OpenAI CLIP Verifier", fontsize=10, weight='bold', color=c_text_white, ha='center')
    ax.text(35.5, 44, "ViT-B/32 on CUDA", fontsize=8, color=c_indigo, ha='center')
    ax.text(35.5, 40.5, "• Zero-Shot Visual Embedding\n• Cropped Entity Resolution\n• Cosine Similarity vs Prompts:\n  cos(e_img, e_txt) / tau\n• Prunes Misclassifications\n  (e.g., Cat vs Dog Hallucination)",
            fontsize=8, color=c_text_muted, ha='center', va='top', linespacing=1.25)
    ax.text(35.5, 17.5, "Taxonomic Consensus Gate", fontsize=7.5, color='#A5B4FC', ha='center', weight='bold')

    # =========================================================================
    # COLUMN 3: KINEMATICS & MEMORY BANK (X: 49 - 72)
    # =========================================================================
    draw_card(49, 10, 23, 79, '#1E1B4B', '#4C1D95', border_width=1.5)
    ax.text(60.5, 86.5, "3. KINEMATICS & MEMORY BANK", fontsize=11, weight='bold', color=c_purple, ha='center', va='center')
    ax.text(60.5, 84.5, "Zero-Training Tracking & State Machine", fontsize=8, color=c_text_muted, ha='center', va='center')

    # Sub-card 1: Norfair 2D Kalman Filter
    draw_card(50.5, 57, 20, 24, '#2E1065', '#7C3AED', radius=0.8)
    ax.text(60.5, 78.5, "Norfair 2D Kalman Filter", fontsize=10, weight='bold', color=c_text_white, ha='center')
    ax.text(60.5, 76, "Zero-Training Multi-Object Tracker", fontsize=8, color=c_teal, ha='center')
    ax.text(60.5, 72.5, "• State Vector: [x, y, vx, vy]^T\n• IoU & Centroid Distance Metric\n• Hungarian Assignment Algorithm\n• Smooth Kalman Trajectories",
            fontsize=8, color=c_text_muted, ha='center', va='top', linespacing=1.3)
    ax.text(60.5, 60, "Zero Training Epochs Required", fontsize=7.5, color='#5EEAD4', ha='center', weight='bold')

    # Sub-card 2: Persistent Memory Bank & State Machine
    draw_card(50.5, 14, 20, 39, '#2E1065', '#9333EA', radius=0.8)
    ax.text(60.5, 50.5, "Persistent Memory Bank Engine", fontsize=10, weight='bold', color=c_text_white, ha='center')
    ax.text(60.5, 48, "4-State Physical Automaton", fontsize=8, color=c_purple, ha='center')
    
    # State pills
    ax.text(60.5, 44, "[VISIBLE] ➔ [OCCLUDED] ➔ [LOST / OUT_OF_BOUNDS]", fontsize=7.5, color='#F3E8FF', ha='center', weight='bold')
    
    ax.text(60.5, 40.5, "1. Ballistic Dead-Reckoning:\n   P_pred(t) = P(t-1) + V_smooth * dt\n   (Renders Dashed Cyan Ghost HUD)\n\n2. Spatial-Scale Re-ID Cost:\n   Cost = 0.70*(Dist/Diag) + 0.30*(AreaDelta)\n   Threshold <= 0.45 ➔ Heals Master ID",
            fontsize=7.8, color=c_text_muted, ha='center', va='top', linespacing=1.2)
    ax.text(60.5, 17.5, "Heals Identity Across 30+ Frames", fontsize=7.5, color='#D8B4FE', ha='center', weight='bold')

    # =========================================================================
    # COLUMN 4: 4-TIER EVALUATION SUITE (X: 75 - 97)
    # =========================================================================
    draw_card(75, 10, 22, 79, '#14271E', '#065F46', border_width=1.5)
    ax.text(86, 86.5, "4. 4-TIER EVALUATION & AUDIT", fontsize=11, weight='bold', color=c_emerald, ha='center', va='center')
    ax.text(86, 84.5, "Quantitative Decoupling & Metrics", fontsize=8, color=c_text_muted, ha='center', va='center')

    # Sub-card: Tier 1 MTA
    draw_card(76.5, 68, 19, 14, '#064E3B', '#059669', radius=0.6)
    ax.text(86, 79.5, "Tier 1: Model Tracking Acc. (MTA)", fontsize=8.5, weight='bold', color=c_text_white, ha='center')
    ax.text(86, 76.5, "MTA = 0.35(IoUS) + 0.35(Conf) + 0.30(LCR)", fontsize=7.5, color='#6EE7B7', ha='center', weight='bold')
    ax.text(86, 71.5, "Evaluates Tracker Smoothness & Jitter", fontsize=7.5, color=c_text_muted, ha='center')

    # Sub-card: Tier 2 PWMA
    draw_card(76.5, 51.5, 19, 14.5, '#064E3B', '#10B981', radius=0.6)
    ax.text(86, 63.5, "Tier 2: Physical World Acc. (PWMA)", fontsize=8.5, weight='bold', color=c_text_white, ha='center')
    ax.text(86, 60.5, "PWMA = 0.35(OPS) + 0.25(ID) + 0.20(KTA) + 0.20(ASA)", fontsize=7, color='#A7F3D0', ha='center', weight='bold')
    ax.text(86, 55.5, "Evaluates Mass/Permanence Conservation", fontsize=7.5, color=c_text_muted, ha='center')

    # Sub-card: Tier 3 OVR
    draw_card(76.5, 35, 19, 14.5, '#064E3B', '#059669', radius=0.6)
    ax.text(86, 47, "Tier 3: Occlusion Veracity (OVR)", fontsize=8.5, weight='bold', color=c_text_white, ha='center')
    ax.text(86, 44, "3-Gate Physical Barrier Validation", fontsize=7.5, color='#FDE047', ha='center', weight='bold')
    ax.text(86, 39, "Gate 1: Barrier Contact | Gate 2: Kinematics\nGate 3: Ballistic Trajectory Exit Check",
            fontsize=7, color=c_text_muted, ha='center', linespacing=1.2)

    # Sub-card: Tier 4 SAI
    draw_card(76.5, 18.5, 19, 14.5, '#064E3B', '#10B981', radius=0.6)
    ax.text(86, 30.5, "Tier 4: Semantic Integrity (SAI)", fontsize=8.5, weight='bold', color=c_text_white, ha='center')
    ax.text(86, 27.5, "SAI = STA x Dominant Class Ratio", fontsize=7.5, color='#6EE7B7', ha='center', weight='bold')
    ax.text(86, 22.5, "Shannon Entropy H(C) + CLIP Verification\nPrunes Animal/Object Morphing Events",
            fontsize=7, color=c_text_muted, ha='center', linespacing=1.2)

    # Sub-card: Artifact Outputs
    draw_card(76.5, 12, 19, 5, '#1E293B', '#475569', radius=0.4)
    ax.text(86, 14.5, "Outputs: CSV Logs • JSON Summary • HUD Video", fontsize=7.5, color='#CBD5E1', ha='center', weight='bold')

    # =========================================================================
    # CONNECTING ARROWS & DATA PIPELINES
    # =========================================================================
    # Input -> YOLO
    draw_arrow(20.5, 71.5, 26.5, 71.5, color=c_blue, lw=2.5, label="RGB Frames", label_pos=(0.4, 0.5))
    # Input -> Prompt Conditioning -> YOLO & CLIP
    draw_arrow(20.5, 48, 26.5, 35, color=c_indigo, lw=2, label="Text Prompts", label_pos=(0.5, 0.4))
    
    # YOLO -> Norfair
    draw_arrow(44.5, 69, 50.5, 69, color=c_teal, lw=2.5, label="[B_t, Conf]", label_pos=(0.5, 0.5))
    # YOLO -> CLIP (Crops)
    draw_arrow(35.5, 53, 35.5, 49, color=c_indigo, lw=2, label="BBox Crops", label_pos=(0.5, 0.5))
    # CLIP -> Memory Bank & Metrics
    draw_arrow(44.5, 31, 50.5, 31, color=c_purple, lw=2, label="Verified Class", label_pos=(0.5, 0.5))

    # Norfair -> Memory Bank
    draw_arrow(60.5, 57, 60.5, 53, color=c_purple, lw=2.5, label="Track IDs & Velocity", label_pos=(0.5, 0.5))

    # Kinematics & Memory Bank -> Evaluation Suite
    draw_arrow(70.5, 75, 76.5, 75, color=c_emerald, lw=2, label="IoU/Jitter", label_pos=(0.5, 0.5))
    draw_arrow(70.5, 58, 76.5, 58, color=c_emerald, lw=2, label="Re-ID/OPS", label_pos=(0.5, 0.5))
    draw_arrow(70.5, 41, 76.5, 41, color=c_emerald, lw=2, label="Occlusions", label_pos=(0.5, 0.5))
    draw_arrow(70.5, 25, 76.5, 25, color=c_emerald, lw=2, label="Attributes", label_pos=(0.5, 0.5))

    # Bottom Footer Note
    ax.text(50, 4.5, "Framework Key Advantage: Completely decouples Vision Evaluator Performance (MTA) from AI Generative Physical Realism (PWMA) with 0 Training Epochs.",
            fontsize=9.5, color=c_text_muted, ha='center', style='italic')

    # Save outputs
    out_dir = os.path.join("Object_permanence", "outputs", "plots")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "system_architecture_diagram.png")
    root_out_path = "system_architecture_diagram.png"

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    plt.savefig(root_out_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    plt.close()

    print(f"[SUCCESS] Architecture diagram generated at:\n  - {out_path}\n  - {root_out_path}")

if __name__ == "__main__":
    create_architecture_diagram()
