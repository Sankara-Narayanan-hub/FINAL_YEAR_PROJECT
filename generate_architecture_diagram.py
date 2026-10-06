import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

def generate_sih_modular_architecture():
    # Presentation-ready 16:9 canvas (300 DPI)
    fig, ax = plt.subplots(figsize=(22, 11), dpi=300)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette
    c_card = '#FFFFFF'
    c_text_dark = '#0F172A'
    c_text_muted = '#475569'

    # Module Accent Colors
    c_blue = '#0284C7'      # 1. Ingestion
    c_indigo = '#4F46E5'    # 2. Perception
    c_purple = '#7C3AED'    # 3. Kinematics & Memory
    c_emerald = '#059669'   # 4. Evaluation Engine
    c_rose = '#E11D48'      # 5. Presentation & Audit

    # -------------------------------------------------------------
    # 1. TITLE & SUBTITLE
    # -------------------------------------------------------------
    ax.text(50, 96.6, "SYSTEM ARCHITECTURE PIPELINE",
            fontsize=23, weight='bold', color=c_text_dark, ha='center', va='center')
    ax.text(50, 93.4, "Physical Object Permanence & Attribute Consistency Framework for Generative AI Video",
            fontsize=11.5, weight='medium', color=c_indigo, ha='center', va='center')

    # -------------------------------------------------------------
    # 2. ICON DRAWING HELPERS (Clean vector glyphs)
    # -------------------------------------------------------------
    def draw_icon_avatar(cx, cy, icon_type, fill_color):
        # Circle badge
        ax.add_patch(Circle((cx, cy), 1.5, facecolor=fill_color, edgecolor='none', zorder=5))
        
        if icon_type == 'video':
            # Video camera
            ax.add_patch(FancyBboxPatch((cx - 0.75, cy - 0.5), 1.0, 1.0, boxstyle="round,pad=0.04", facecolor='#FFFFFF', zorder=6))
            pts = [[cx + 0.35, cy - 0.4], [cx + 0.85, cy - 0.65], [cx + 0.85, cy + 0.65], [cx + 0.35, cy + 0.4]]
            ax.add_patch(Polygon(pts, facecolor='#FFFFFF', zorder=6))
        elif icon_type == 'ai':
            # Neural network
            p1, p2, p3, p4 = (cx-0.55, cy), (cx+0.55, cy-0.45), (cx+0.55, cy+0.45), (cx, cy+0.65)
            for p in [p1, p2, p3, p4]:
                ax.add_patch(Circle(p, 0.22, facecolor='#FFFFFF', zorder=7))
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#FFFFFF', lw=1.2, zorder=6)
            ax.plot([p1[0], p3[0]], [p1[1], p3[1]], color='#FFFFFF', lw=1.2, zorder=6)
            ax.plot([p1[0], p4[0]], [p1[1], p4[1]], color='#FFFFFF', lw=1.2, zorder=6)
            ax.plot([p4[0], p2[0]], [p4[1], p2[1]], color='#FFFFFF', lw=1.2, zorder=6)
            ax.plot([p4[0], p3[0]], [p4[1], p3[1]], color='#FFFFFF', lw=1.2, zorder=6)
        elif icon_type == 'radar':
            # Crosshair
            ax.add_patch(Circle((cx, cy), 0.8, facecolor='none', edgecolor='#FFFFFF', lw=1.3, zorder=6))
            ax.add_patch(Circle((cx, cy), 0.3, facecolor='none', edgecolor='#FFFFFF', lw=1.0, zorder=6))
            ax.plot([cx-1.0, cx+1.0], [cy, cy], color='#FFFFFF', lw=1.2, zorder=6)
            ax.plot([cx, cx], [cy-1.0, cy+1.0], color='#FFFFFF', lw=1.2, zorder=6)
        elif icon_type == 'chart':
            # Bar chart
            ax.add_patch(Rectangle((cx - 0.7, cy - 0.6), 0.32, 0.7, facecolor='#FFFFFF', zorder=6))
            ax.add_patch(Rectangle((cx - 0.22, cy - 0.6), 0.32, 1.1, facecolor='#FFFFFF', zorder=6))
            ax.add_patch(Rectangle((cx + 0.26, cy - 0.6), 0.32, 1.4, facecolor='#FFFFFF', zorder=6))
        elif icon_type == 'report':
            # Document
            ax.add_patch(FancyBboxPatch((cx - 0.55, cy - 0.75), 1.1, 1.5, boxstyle="round,pad=0.04", facecolor='#FFFFFF', zorder=6))
            ax.plot([cx - 0.3, cx + 0.3], [cy + 0.3, cy + 0.3], color=fill_color, lw=1.4, zorder=7)
            ax.plot([cx - 0.3, cx + 0.3], [cy - 0.05, cy - 0.05], color=fill_color, lw=1.4, zorder=7)
            ax.plot([cx - 0.3, cx + 0.1], [cy - 0.4, cy - 0.4], color=fill_color, lw=1.4, zorder=7)

    # -------------------------------------------------------------
    # 3. MODULE CONTAINER BUILDER
    # -------------------------------------------------------------
    def draw_module(x, y, w, h, mod_num, title, accent_color, icon_name):
        # Drop shadow
        ax.add_patch(FancyBboxPatch((x + 0.3, y - 0.3), w, h,
                                    boxstyle="round,pad=0.7,rounding_size=0.9",
                                    facecolor='#E2E8F0', edgecolor='none', zorder=1))
        # Container body
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.7,rounding_size=0.9",
                                    facecolor=c_card, edgecolor='#CBD5E1', lw=1.4, zorder=2))
        
        # Header banner
        banner_h = 5.2
        ax.add_patch(FancyBboxPatch((x + 0.9, y + h - banner_h - 0.6), w - 1.8, banner_h,
                                    boxstyle="round,pad=0.3,rounding_size=0.5",
                                    facecolor=accent_color, edgecolor='none', zorder=3))
        
        # Icon inside header
        draw_icon_avatar(x + 2.7, y + h - 3.2, icon_name, '#0F172A')
        
        # Header titles
        ax.text(x + 4.8, y + h - 2.3, f"MODULE {mod_num}", fontsize=7.5, weight='bold', color='#FFFFFF', alpha=0.9, zorder=4)
        ax.text(x + 4.8, y + h - 4.2, title, fontsize=10.0, weight='bold', color='#FFFFFF', zorder=4)

    # -------------------------------------------------------------
    # 4. COMPONENT CARD BUILDER (Clean title + badge below title)
    # -------------------------------------------------------------
    def draw_component_card(x, y, w, h, title, badge_tag, accent_color, bullet_lines=[]):
        # Card body
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.3,rounding_size=0.5",
                                    facecolor='#F8FAFC', edgecolor='#E2E8F0', lw=1.2, zorder=3))
        # Left colored indicator bar
        ax.add_patch(FancyBboxPatch((x + 0.35, y + 0.6), 0.5, h - 1.2,
                                    boxstyle="round,pad=0.08", facecolor=accent_color, edgecolor='none', zorder=4))
        
        # Title (Line 1)
        ax.text(x + 1.4, y + h - 2.0, title, fontsize=9.0, weight='bold', color=c_text_dark, zorder=4)
        
        # Badge Pill (Line 2)
        bw = len(badge_tag) * 0.55 + 1.2
        ax.add_patch(FancyBboxPatch((x + 1.4, y + h - 4.0), bw, 1.5,
                                    boxstyle="round,pad=0.1,rounding_size=0.3",
                                    facecolor='#EEF2F6', edgecolor='#CBD5E1', lw=0.7, zorder=4))
        ax.text(x + 1.4 + bw/2, y + h - 3.25, badge_tag, fontsize=6.5, weight='bold', color=accent_color, ha='center', va='center', zorder=5)

        # Bullets (Lines 3+)
        start_y = y + h - 5.6
        for line in bullet_lines:
            ax.text(x + 1.4, start_y, line, fontsize=7.4, color=c_text_muted, zorder=4)
            start_y -= 1.6

    # =========================================================================
    # 5 MODULES SETUP
    # =========================================================================
    mod_w = 17.5
    gap = 2.0
    start_x = 2.25

    # -------------------------------------------------------------
    # MODULE 1: DATA INGESTION
    # -------------------------------------------------------------
    m1_x = start_x
    draw_module(m1_x, 9, mod_w, 79, 1, "DATA INGESTION", c_blue, 'video')
    
    draw_component_card(m1_x + 1.0, 62.5, mod_w - 2.0, 20.5,
                        "Video Stream Source", "MP4 24-60 FPS", c_blue,
                        ["• Sora, Kling, Hunyuan", "• Veo-3, CogVideo, Wanx", "• VBench-2.0 Suite"])

    draw_component_card(m1_x + 1.0, 38.5, mod_w - 2.0, 21.0,
                        "Prompt Conditioner", "Text NLP Tokenizer", c_blue,
                        ["• Target Subject Extraction", "• Barrier / Obstacle Specifier", "• Candidate Vocab Parsing"])

    draw_component_card(m1_x + 1.0, 14.0, mod_w - 2.0, 21.5,
                        "OpenCV Preprocessor", "RGB Normalizer", c_blue,
                        ["• Frame Buffer Decoder", "• Aspect Ratio Normalization", "• 1080p Stream Synchronization"])

    # -------------------------------------------------------------
    # MODULE 2: AI PERCEPTION & FOUNDATION
    # -------------------------------------------------------------
    m2_x = m1_x + mod_w + gap
    draw_module(m2_x, 9, mod_w, 79, 2, "AI PERCEPTION", c_indigo, 'ai')

    draw_component_card(m2_x + 1.0, 49.5, mod_w - 2.0, 33.5,
                        "YOLO-World Detector", "Ultralytics Open-Vocab", c_indigo,
                        ["• Zero-Shot Open Inference", "• Candidate BBoxes [B_t]", "• Neural Confidence [c_j]", "• Threshold Gate: 0.35 - 0.40", "• Real-Time GPU Detection"])

    draw_component_card(m2_x + 1.0, 14.0, mod_w - 2.0, 32.5,
                        "OpenAI CLIP Verifier", "ViT-B/32 on CUDA", c_indigo,
                        ["• Zero-Shot Visual Embedding", "• Visual-Prompt Cosine Match", "• Eliminates Morph Glitches", "  (e.g., Cat vs Dog Morph)", "• Ground-Truth Verification"])

    # -------------------------------------------------------------
    # MODULE 3: TRACKING & MEMORY CORE
    # -------------------------------------------------------------
    m3_x = m2_x + mod_w + gap
    draw_module(m3_x, 9, mod_w, 79, 3, "TRACKING & MEMORY", c_purple, 'radar')

    draw_component_card(m3_x + 1.0, 49.5, mod_w - 2.0, 33.5,
                        "Norfair 2D Kalman Filter", "Zero-Training MOT", c_purple,
                        ["• State: [x, y, vx, vy]^T", "• Consecutive IoU Association", "• Hungarian Distance Match", "• Kalman Trajectory Smoothing", "• Zero Epochs Needed"])

    draw_component_card(m3_x + 1.0, 14.0, mod_w - 2.0, 32.5,
                        "Persistent Memory Bank", "4-State Automaton", c_purple,
                        ["• [VISIBLE ➔ OCCLUDED ➔ LOST]", "• Ballistic Dead-Reckoning", "  (P_pred = P_last + v*dt)", "• Cyan Ghost Box HUD", "• Re-ID Cost Match <= 0.45"])

    # -------------------------------------------------------------
    # MODULE 4: ACCURACY EVALUATION ENGINE
    # -------------------------------------------------------------
    m4_x = m3_x + mod_w + gap
    draw_module(m4_x, 9, mod_w, 79, 4, "EVALUATION ENGINE", c_emerald, 'chart')

    draw_component_card(m4_x + 1.0, 68.0, mod_w - 2.0, 15.0,
                        "Tier 1: MTA", "Tracker Quality", c_emerald,
                        ["0.35(IoUS) + 0.35(c) + 0.30(LCR)", "Evaluates Tracking Jitter"])

    draw_component_card(m4_x + 1.0, 50.0, mod_w - 2.0, 15.0,
                        "Tier 2: PWMA", "Physical Realism", c_emerald,
                        ["0.35(OPS) + 0.25(ID) + 0.20(KTA)", "Evaluates Mass & Permanence"])

    draw_component_card(m4_x + 1.0, 32.0, mod_w - 2.0, 15.0,
                        "Tier 3: OVR", "3 Physical Gates", c_emerald,
                        ["Barrier Contact & Kinematics", "Filters Phantom Disappearances"])

    draw_component_card(m4_x + 1.0, 14.0, mod_w - 2.0, 15.0,
                        "Tier 4: SAI", "Taxonomic Audit", c_emerald,
                        ["STA x Dominant Class Ratio", "Detects Species Morphing"])

    # -------------------------------------------------------------
    # MODULE 5: OUTPUTS & AUDIT DOSSIER
    # -------------------------------------------------------------
    m5_x = m4_x + mod_w + gap
    draw_module(m5_x, 9, mod_w, 79, 5, "OUTPUTS & AUDIT", c_rose, 'report')

    draw_component_card(m5_x + 1.0, 62.5, mod_w - 2.0, 20.5,
                        "Annotated Video HUD", "Rendered MP4", c_rose,
                        ["• Dashed Cyan Ghost HUD", "• Occlusion Alert Banner", "• Re-ID Track Trajectories"])

    draw_component_card(m5_x + 1.0, 38.5, mod_w - 2.0, 21.0,
                        "Telemetry CSV Audits", "DataFrames", c_rose,
                        ["• Frame Detections Log", "• State Machine Transitions", "• Re-ID Recovery History"])

    draw_component_card(m5_x + 1.0, 14.0, mod_w - 2.0, 21.5,
                        "Methodology Dossier", "Master PDF Dossier", c_rose,
                        ["• 7-Page Academic Report", "• 25-Video Benchmark Suite", "• Piagetian Permanence Test"])

    # =========================================================================
    # PIPELINE CONNECTING BUSES (SIH Bus Lines)
    # =========================================================================
    def draw_bus(x1, y1, x2, y2, color, label=""):
        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle=patches.ArrowStyle("Simple", head_length=4.0, head_width=4.0, tail_width=1.5),
            color=color, linewidth=1.5, zorder=5
        )
        ax.add_patch(arrow)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 1.1, label, fontsize=6.8, weight='bold', color=color, ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='#FFFFFF', edgecolor=color, lw=0.8), zorder=6)

    # Ingestion -> Perception
    draw_bus(m1_x + mod_w, 72.5, m2_x, 72.5, c_blue, "Frames")
    draw_bus(m1_x + mod_w, 48.0, m2_x, 30.0, c_blue, "Prompts")

    # Perception -> Tracking
    draw_bus(m2_x + mod_w, 66.0, m3_x, 66.0, c_indigo, "BBoxes")
    draw_bus(m2_x + mod_w, 30.0, m3_x, 30.0, c_indigo, "Classes")

    # Tracking -> Evaluation
    draw_bus(m3_x + mod_w, 75.5, m4_x, 75.5, c_purple, "IoU/Jitter")
    draw_bus(m3_x + mod_w, 57.5, m4_x, 57.5, c_purple, "Re-IDs")
    draw_bus(m3_x + mod_w, 39.5, m4_x, 39.5, c_purple, "States")
    draw_bus(m3_x + mod_w, 21.5, m4_x, 21.5, c_purple, "Attributes")

    # Evaluation -> Outputs
    draw_bus(m4_x + mod_w, 72.5, m5_x, 72.5, c_emerald, "HUD Overlay")
    draw_bus(m4_x + mod_w, 49.0, m5_x, 49.0, c_emerald, "Logs")
    draw_bus(m4_x + mod_w, 24.5, m5_x, 24.5, c_emerald, "Metrics")

    # -------------------------------------------------------------
    # FOOTER KEY TAKEAWAYS BAR
    # -------------------------------------------------------------
    foot_bg = FancyBboxPatch((2.25, 2.5), 95.5, 4.5, boxstyle="round,pad=0.3,rounding_size=0.6",
                             facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=1.2, zorder=2)
    ax.add_patch(foot_bg)
    ax.text(4.0, 4.75, "KEY INNOVATIONS:", fontsize=8.5, weight='bold', color=c_indigo, va='center')
    ax.text(15.5, 4.75, "Decoupled Evaluation (Evaluator MTA vs Generative Physics PWMA)  •  Zero-Training Kalman MOT (Norfair)  •  Ballistic Memory Automaton",
            fontsize=8, weight='medium', color=c_text_dark, va='center')

    # Save
    out_dir = os.path.join("Object_permanence", "outputs", "plots")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "system_architecture_diagram.png")
    root_out_path = "system_architecture_diagram.png"

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='#F8FAFC')
    plt.savefig(root_out_path, dpi=300, bbox_inches='tight', facecolor='#F8FAFC')
    plt.close()

    print(f"[SUCCESS] SIH-Style Architecture Diagram generated successfully at:\n  - {out_path}\n  - {root_out_path}")

if __name__ == "__main__":
    generate_sih_modular_architecture()
