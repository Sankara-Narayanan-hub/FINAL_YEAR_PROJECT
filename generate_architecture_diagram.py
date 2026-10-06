import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

def create_clean_architecture_diagram():
    # Professional 16:9 canvas
    fig, ax = plt.subplots(figsize=(19, 10), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette - Minimalist Tech Theme
    c_text_main = '#FFFFFF'
    c_text_sub = '#94A3B8'
    c_blue = '#38BDF8'      # Input / Detection
    c_indigo = '#818CF8'    # CLIP Verifier
    c_teal = '#2DD4BF'      # Kalman Tracking
    c_purple = '#C084FC'    # Memory Bank
    c_emerald = '#34D399'   # Evaluation Suite
    c_slate = '#64748B'     # Outputs

    # Header
    ax.text(50, 95.5, "SYSTEM ARCHITECTURE", fontsize=22, weight='bold', color=c_text_main, ha='center', va='center')
    ax.text(50, 92.5, "Physical Object Permanence & Memory Recovery Framework", fontsize=12, color=c_blue, ha='center', va='center')

    # Helper: Draw Card
    def draw_card(x, y, w, h, bg_color, border_color, border_width=1.5, radius=1.0):
        bbox = FancyBboxPatch((x, y), w, h,
                              boxstyle=f"round,pad={radius},rounding_size={radius}",
                              facecolor=bg_color, edgecolor=border_color,
                              linewidth=border_width, zorder=2)
        ax.add_patch(bbox)
        return bbox

    # Helper: Draw Arrow
    def draw_arrow(x1, y1, x2, y2, color='#38BDF8', lw=2.0, label=""):
        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle=ArrowStyle("Simple", head_length=5, head_width=5, tail_width=1.5),
            color=color, linewidth=lw, zorder=4
        )
        ax.add_patch(arrow)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 1.8, label, fontsize=8, weight='bold', color='#E2E8F0', ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.25", facecolor='#0B0F19', edgecolor=color, lw=0.8), zorder=5)

    # =========================================================================
    # STAGE 1: INPUT LAYER (X: 4 - 20)
    # =========================================================================
    draw_card(4, 12, 16, 74, '#111827', '#1E293B', radius=1.2)
    ax.text(12, 82, "1. INPUT", fontsize=13, weight='bold', color=c_blue, ha='center')

    # Card 1.1: Video Input
    draw_card(5.5, 52, 13, 23, '#1E293B', '#38BDF8', radius=0.8)
    ax.text(12, 69, "AI Video Stream", fontsize=11, weight='bold', color=c_text_main, ha='center')
    ax.text(12, 63, "• Sora • Kling • Hunyuan\n• Veo-3 • CogVideoX • Wanx", fontsize=8.5, color=c_text_sub, ha='center', linespacing=1.4)
    ax.text(12, 56, "24-60 FPS MP4", fontsize=8, weight='bold', color=c_blue, ha='center')

    # Card 1.2: Prompt Input
    draw_card(5.5, 18, 13, 27, '#1E293B', '#F59E0B', radius=0.8)
    ax.text(12, 39, "Text Prompt", fontsize=11, weight='bold', color=c_text_main, ha='center')
    ax.text(12, 33, '"A dog is behind a chair,\nthen runs to the right..."', fontsize=8.5, color='#FDE047', ha='center', style='italic', linespacing=1.3)
    ax.text(12, 23, "Conditioning Specifier", fontsize=8, color=c_text_sub, ha='center')

    # =========================================================================
    # STAGE 2: PERCEPTION & VERIFICATION (X: 24 - 44)
    # =========================================================================
    draw_card(24, 12, 20, 74, '#0F172A', '#1E3A8A', radius=1.2)
    ax.text(34, 82, "2. PERCEPTION", fontsize=13, weight='bold', color=c_indigo, ha='center')

    # Card 2.1: YOLO Detector
    draw_card(25.5, 52, 17, 23, '#1E293B', '#3B82F6', radius=0.8)
    ax.text(34, 69, "YOLOv8 / World", fontsize=11, weight='bold', color=c_text_main, ha='center')
    ax.text(34, 64, "Open-Vocabulary Detector", fontsize=8.5, color=c_blue, ha='center')
    ax.text(34, 57, "Bounding Boxes [B_t]\nConfidence Scores [c_j]", fontsize=8.5, color=c_text_sub, ha='center', linespacing=1.3)

    # Card 2.2: CLIP Verifier
    draw_card(25.5, 18, 17, 27, '#1E293B', '#6366F1', radius=0.8)
    ax.text(34, 39, "OpenAI CLIP (CUDA)", fontsize=11, weight='bold', color=c_text_main, ha='center')
    ax.text(34, 34, "ViT-B/32 Zero-Shot Verifier", fontsize=8.5, color=c_indigo, ha='center')
    ax.text(34, 27, "Cosine Feature Matching\nPrunes Class Hallucinations\n(e.g., Cat vs Dog)", fontsize=8.5, color=c_text_sub, ha='center', linespacing=1.3)

    # =========================================================================
    # STAGE 3: KINEMATICS & MEMORY (X: 48 - 68)
    # =========================================================================
    draw_card(48, 12, 20, 74, '#1E1B4B', '#4C1D95', radius=1.2)
    ax.text(58, 82, "3. TRACKING & MEMORY", fontsize=13, weight='bold', color=c_purple, ha='center')

    # Card 3.1: Norfair Tracker
    draw_card(49.5, 52, 17, 23, '#2E1065', '#8B5CF6', radius=0.8)
    ax.text(58, 69, "Norfair 2D Kalman", fontsize=11, weight='bold', color=c_text_main, ha='center')
    ax.text(58, 64, "Zero-Training Tracker", fontsize=8.5, color=c_teal, ha='center')
    ax.text(58, 57, "Kalman State: [x, y, vx, vy]\nIoU Distance Matching", fontsize=8.5, color=c_text_sub, ha='center', linespacing=1.3)

    # Card 3.2: Persistent Memory Bank
    draw_card(49.5, 18, 17, 27, '#2E1065', '#A855F7', radius=0.8)
    ax.text(58, 39, "Persistent Memory Bank", fontsize=11, weight='bold', color=c_text_main, ha='center')
    ax.text(58, 34, "4-State Physical Automaton", fontsize=8.5, color=c_purple, ha='center')
    ax.text(58, 26, "• Ballistic Dead-Reckoning\n  (Cyan Ghost Box HUD)\n• Re-ID Cost <= 0.45\n  (Master ID Recovery)",
            fontsize=8.5, color=c_text_sub, ha='center', linespacing=1.3)

    # =========================================================================
    # STAGE 4: 4-TIER EVALUATION (X: 72 - 96)
    # =========================================================================
    draw_card(72, 12, 24, 74, '#14271E', '#065F46', radius=1.2)
    ax.text(84, 82, "4. 4-TIER EVALUATION", fontsize=13, weight='bold', color=c_emerald, ha='center')

    # Card 4.1: MTA
    draw_card(73.5, 65, 21, 13, '#064E3B', '#10B981', radius=0.6)
    ax.text(84, 74.5, "Tier 1: MTA (Tracking Accuracy)", fontsize=9.5, weight='bold', color=c_text_main, ha='center')
    ax.text(84, 70.5, "MTA = 0.35(IoUS) + 0.35(Conf) + 0.30(LCR)", fontsize=8, weight='bold', color='#6EE7B7', ha='center')
    ax.text(84, 67, "Evaluates Tracker Stability & Jitter", fontsize=7.5, color=c_text_sub, ha='center')

    # Card 4.2: PWMA
    draw_card(73.5, 49.5, 21, 13.5, '#064E3B', '#10B981', radius=0.6)
    ax.text(84, 59.5, "Tier 2: PWMA (Physical World Acc.)", fontsize=9.5, weight='bold', color=c_text_main, ha='center')
    ax.text(84, 55.5, "0.35(OPS) + 0.25(ID) + 0.20(KTA) + 0.20(ASA)", fontsize=8, weight='bold', color='#A7F3D0', ha='center')
    ax.text(84, 52, "Evaluates Mass & Permanence Laws", fontsize=7.5, color=c_text_sub, ha='center')

    # Card 4.3: OVR
    draw_card(73.5, 34, 21, 13.5, '#064E3B', '#10B981', radius=0.6)
    ax.text(84, 44, "Tier 3: OVR (Occlusion Veracity)", fontsize=9.5, weight='bold', color=c_text_main, ha='center')
    ax.text(84, 40, "3-Gate Physical Barrier Validation", fontsize=8, weight='bold', color='#FDE047', ha='center')
    ax.text(84, 36.5, "Filters Phantom Disappearances", fontsize=7.5, color=c_text_sub, ha='center')

    # Card 4.4: SAI
    draw_card(73.5, 18.5, 21, 13.5, '#064E3B', '#10B981', radius=0.6)
    ax.text(84, 28.5, "Tier 4: SAI (Semantic Integrity)", fontsize=9.5, weight='bold', color=c_text_main, ha='center')
    ax.text(84, 24.5, "SAI = STA × Dominant Class Ratio", fontsize=8, weight='bold', color='#6EE7B7', ha='center')
    ax.text(84, 21, "Detects Species / Attribute Morphing", fontsize=7.5, color=c_text_sub, ha='center')

    # =========================================================================
    # CONNECTING PIPELINES
    # =========================================================================
    # Video -> YOLO
    draw_arrow(18.5, 63.5, 25.5, 63.5, color=c_blue, lw=2.2, label="Frames")
    # Prompt -> CLIP & YOLO
    draw_arrow(18.5, 31.5, 25.5, 31.5, color='#F59E0B', lw=2.0, label="Prompts")

    # YOLO -> Norfair
    draw_arrow(42.5, 63.5, 49.5, 63.5, color=c_teal, lw=2.2, label="Detections")
    # YOLO -> CLIP (Crops) & CLIP -> Memory
    draw_arrow(34, 52, 34, 45, color=c_indigo, lw=1.8, label="Crops")
    draw_arrow(42.5, 31.5, 49.5, 31.5, color=c_purple, lw=2.0, label="Labels")

    # Norfair -> Memory
    draw_arrow(58, 52, 58, 45, color=c_purple, lw=2.0, label="Tracks")

    # Memory -> Evaluation Suite
    draw_arrow(66.5, 71.5, 73.5, 71.5, color=c_emerald, lw=2.0)
    draw_arrow(66.5, 56, 73.5, 56, color=c_emerald, lw=2.0)
    draw_arrow(66.5, 40.5, 73.5, 40.5, color=c_emerald, lw=2.0)
    draw_arrow(66.5, 25, 73.5, 25, color=c_emerald, lw=2.0)

    # Bottom Footer
    ax.text(50, 4.5, "Decoupled Architecture: Separates Evaluator Tracking Quality (MTA) from AI Physical Realism (PWMA) with 0 Training Epochs.",
            fontsize=10, color=c_text_sub, ha='center', style='italic')

    # Save
    out_dir = os.path.join("Object_permanence", "outputs", "plots")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "system_architecture_diagram.png")
    root_out_path = "system_architecture_diagram.png"

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    plt.savefig(root_out_path, dpi=300, bbox_inches='tight', facecolor='#0B0F19')
    plt.close()

    print(f"[SUCCESS] Clean architecture diagram generated at:\n  - {out_path}\n  - {root_out_path}")

if __name__ == "__main__":
    create_clean_architecture_diagram()
