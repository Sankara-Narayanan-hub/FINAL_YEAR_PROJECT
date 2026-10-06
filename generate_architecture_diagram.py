import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

def build_sih_architecture_diagram(output_path, dark_mode=True):
    # Set up high-res 16:9 canvas (20 x 11.25 inches @ 200 DPI = 4000 x 2250 px)
    fig_w, fig_h = 20.0, 11.25
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Color Palette
    if dark_mode:
        bg_color = "#0B1120"        # Deep slate navy
        header_text = "#FFFFFF"     # Crisp white
        sub_text = "#94A3B8"        # Slate light
        card_bg = "#111A2E"         # Slate card fill
        card_border = "#1E293B"     # Card border
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        divider_color = "#1E293B"
        pill_bg = "#1A243B"
        sih_pill_bg = "#1E293B"
        sih_pill_border = "#38BDF8"
        sih_pill_text = "#38BDF8"
        bar_bg = "#111A2E"
        bar_border = "#38BDF8"
        bar_badge_bg = "#1A243B"
        bar_badge_border = "#0284C7"
    else:
        bg_color = "#F8FAFC"        # Crisp studio white / light slate
        header_text = "#0F172A"     # Deep slate
        sub_text = "#475569"        # Charcoal
        card_bg = "#FFFFFF"         # Pure white cards
        card_border = "#E2E8F0"     # Light grey border
        text_primary = "#0F172A"
        text_secondary = "#475569"
        divider_color = "#E2E8F0"
        pill_bg = "#F1F5F9"
        sih_pill_bg = "#EEF2FF"
        sih_pill_border = "#6366F1"
        sih_pill_text = "#4338CA"
        bar_bg = "#F0F9FF"
        bar_border = "#38BDF8"
        bar_badge_bg = "#E0F2FE"
        bar_badge_border = "#7DD3FC"

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    icons_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    icon_urls = {
        "video": "https://img.icons8.com/fluency/96/video.png",
        "prompt": "https://img.icons8.com/fluency/96/speech-bubble.png",
        "yolo": "https://img.icons8.com/fluency/96/visible.png",
        "clip": "https://img.icons8.com/fluency/96/brain.png",
        "ai": "https://img.icons8.com/fluency/96/artificial-intelligence.png",
        "tracker": "https://img.icons8.com/fluency/96/radar.png",
        "memory": "https://img.icons8.com/fluency/96/database.png",
        "accuracy": "https://img.icons8.com/fluency/96/checked-checkbox.png",
        "speedometer": "https://img.icons8.com/fluency/96/speedometer.png",
        "output": "https://img.icons8.com/fluency/96/monitor.png",
        "report": "https://img.icons8.com/fluency/96/summary-list.png",
        "gpu": "https://img.icons8.com/fluency/96/processor.png",
        "server": "https://img.icons8.com/fluency/96/server.png"
    }

    def get_icon(name, zoom=0.40):
        path = os.path.join(icons_dir, f"{name}.png")
        if not os.path.exists(path) and name in icon_urls:
            try:
                import urllib.request
                req = urllib.request.Request(icon_urls[name], headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as resp:
                    with open(path, "wb") as f:
                        f.write(resp.read())
            except Exception:
                pass
        if os.path.exists(path):
            img = Image.open(path)
            return OffsetImage(img, zoom=zoom)
        return None

    # ----------------------------------------------------
    # 1. TOP HEADER BANNER (SIH PRESENTATION BLUEPRINT)
    # ----------------------------------------------------
    # SIH Competition Pill Tag
    sih_pill = patches.FancyBboxPatch(
        (3.5, 93.6), 28.0, 3.2,
        boxstyle="round,pad=0.2,rounding_size=1.2",
        facecolor=sih_pill_bg,
        edgecolor=sih_pill_border,
        linewidth=1.2,
        zorder=3
    )
    ax.add_patch(sih_pill)
    ax.text(
        17.5, 95.2, "SMART INDIA HACKATHON  •  SYSTEM ARCHITECTURE",
        fontsize=9, weight="bold", color=sih_pill_text,
        ha="center", va="center", zorder=4
    )

    # Main Title & Subtitle
    ax.text(
        3.5, 90.3, "REAL-TIME OBJECT PERMANENCE TRACKING ARCHITECTURE",
        fontsize=21, weight="bold", color=header_text, va="center", zorder=3
    )
    ax.text(
        3.5, 87.0, "Zero-Shot Multi-Modal Perception • Kinematic Kalman MOT • 4-State Ephemeral Memory • 4-Tier Accuracy Engine",
        fontsize=11.5, weight="normal", color=sub_text, va="center", zorder=3
    )

    # Header Divider Line
    ax.plot([3.5, 96.5], [84.6, 84.6], color=divider_color, linewidth=1.5, zorder=2)

    # ----------------------------------------------------
    # 2. THE 5 PIPELINE MODULE STAGES (COLUMNS)
    # ----------------------------------------------------
    stages = [
        {
            "id": "STAGE 01",
            "name": "INPUT & INGESTION",
            "accent": "#0284C7",      # Cyan
            "icon_bg": "#0C2340" if dark_mode else "#E0F2FE",
            "x": 3.5,
            "width": 16.5,
            "cards": [
                {
                    "title": "Video Ingestion",
                    "badge": "OpenCV • RTSP / MP4",
                    "icon": "video",
                    "bullets": [
                        "High-FPS video frame buffer",
                        "Temporal frame de-queuing",
                        "Resolution normalization"
                    ]
                },
                {
                    "title": "Prompt Query",
                    "badge": "Open-Vocabulary Text",
                    "icon": "prompt",
                    "bullets": [
                        "Natural language target prompt",
                        "Dynamic tokenization pipeline",
                        "Zero-shot class conditioning"
                    ]
                }
            ]
        },
        {
            "id": "STAGE 02",
            "name": "PERCEPTION ENGINE",
            "accent": "#6366F1",      # Indigo
            "icon_bg": "#1E1B4B" if dark_mode else "#EEF2FF",
            "x": 22.25,
            "width": 16.5,
            "cards": [
                {
                    "title": "YOLO-World Detector",
                    "badge": "Ultralytics v8-L • FP16",
                    "icon": "yolo",
                    "bullets": [
                        "Zero-shot candidate localization",
                        "Confidence threshold gating (0.35)",
                        "Real-time bounding box stream"
                    ]
                },
                {
                    "title": "CLIP Verifier",
                    "badge": "OpenAI ViT-B/32 • CUDA",
                    "icon": "clip",
                    "bullets": [
                        "512-d visual embedding extraction",
                        "Cross-modal cosine verification",
                        "False-positive crop rejection"
                    ]
                }
            ]
        },
        {
            "id": "STAGE 03",
            "name": "KINEMATICS & MOT",
            "accent": "#10B981",      # Emerald
            "icon_bg": "#064E3B" if dark_mode else "#ECFDF5",
            "x": 41.0,
            "width": 16.5,
            "cards": [
                {
                    "title": "Norfair Kalman MOT",
                    "badge": "Constant-Velocity Model",
                    "icon": "tracker",
                    "bullets": [
                        "State vector [x, y, vx, vy] filtering",
                        "Euclidean distance cost matrix",
                        "Blind-spot track extrapolation"
                    ]
                },
                {
                    "title": "Kinematic Cache",
                    "badge": "Temporal Motion Bank",
                    "icon": "server",
                    "bullets": [
                        "Historical velocity vector log",
                        "Motion momentum smoothing",
                        "Plausible occlusion exit vectors"
                    ]
                }
            ]
        },
        {
            "id": "STAGE 04",
            "name": "MEMORY AUTOMATON",
            "accent": "#F59E0B",      # Amber
            "icon_bg": "#451A03" if dark_mode else "#FEF3C7",
            "x": 59.75,
            "width": 16.5,
            "cards": [
                {
                    "title": "4-State Automaton",
                    "badge": "FSM State Controller",
                    "icon": "memory",
                    "bullets": [
                        "VISIBLE ⇄ OCCLUDED → LOST",
                        "Adaptive occlusion grace window",
                        "Deterministic ghost-track purge"
                    ]
                },
                {
                    "title": "Zero-Shot Re-ID",
                    "badge": "Dual Cosine Re-ID",
                    "icon": "ai",
                    "bullets": [
                        "Ephemeral feature bank matching",
                        "Re-identification cost gating",
                        "Zero-shot target re-acquisition"
                    ]
                }
            ]
        },
        {
            "id": "STAGE 05",
            "name": "AUDIT & PRESENTATION",
            "accent": "#F43F5E",      # Rose
            "icon_bg": "#4C0519" if dark_mode else "#FFE4E6",
            "x": 78.5,
            "width": 17.5,
            "cards": [
                {
                    "title": "4-Tier Accuracy",
                    "badge": "Benchmark Engine",
                    "icon": "accuracy",
                    "bullets": [
                        "MTA (Kinematics) & PWMA (Recall)",
                        "OVR (Spatial IoU) & SAI (Semantics)",
                        "Autonomous audit validation"
                    ]
                },
                {
                    "title": "HUD & Telemetry",
                    "badge": "Annotated Video & CSV",
                    "icon": "output",
                    "bullets": [
                        "Color-coded state bounding boxes",
                        "Live occlusion counter HUD",
                        "Frame-level telemetry CSV logs"
                    ]
                }
            ]
        }
    ]

    card_h = 28.5
    y_card1 = 51.5
    y_card2 = 19.5

    # ----------------------------------------------------
    # 3. DRAW STAGE CONTAINERS & CARDS
    # ----------------------------------------------------
    for stage in stages:
        sx = stage["x"]
        sw = stage["width"]
        accent = stage["accent"]

        # Stage Column Header Pill
        stage_pill = patches.FancyBboxPatch(
            (sx, 80.2), sw, 3.2,
            boxstyle="round,pad=0.2,rounding_size=0.8",
            facecolor="#151E33" if dark_mode else "#F1F5F9",
            edgecolor=accent,
            linewidth=1.2,
            zorder=3
        )
        ax.add_patch(stage_pill)

        # Stage Tag & Title
        ax.text(
            sx + 1.2, 81.8, stage["id"],
            fontsize=8, weight="bold", color=accent,
            va="center", zorder=4
        )
        ax.text(
            sx + sw - 1.2, 81.8, stage["name"],
            fontsize=8.5, weight="bold", color=text_primary,
            ha="right", va="center", zorder=4
        )

        # Draw the 2 Cards per stage
        card_ys = [y_card1, y_card2]
        for i, card in enumerate(stage["cards"]):
            cy = card_ys[i]

            # Main Card Box with clean rounded borders
            card_box = patches.FancyBboxPatch(
                (sx, cy), sw, card_h,
                boxstyle="round,pad=0.3,rounding_size=1.2",
                facecolor=card_bg,
                edgecolor=card_border,
                linewidth=1.3,
                zorder=3
            )
            ax.add_patch(card_box)

            # Left Accent Strip
            accent_strip = patches.FancyBboxPatch(
                (sx, cy + 1.2), 0.5, card_h - 2.4,
                boxstyle="round,pad=0.1,rounding_size=0.25",
                facecolor=accent,
                edgecolor=accent,
                linewidth=0,
                zorder=4
            )
            ax.add_patch(accent_strip)

            # Circular Icon Container Badge at top-left
            icon_cx = sx + 2.7
            icon_cy = cy + card_h - 4.5
            icon_badge = patches.Circle(
                (icon_cx, icon_cy), radius=1.9,
                facecolor=stage["icon_bg"],
                edgecolor=accent,
                linewidth=1.2,
                zorder=4
            )
            ax.add_patch(icon_badge)

            # Centered Icon inside Badge
            icon_obj = get_icon(card["icon"], zoom=0.40)
            if icon_obj:
                ab = AnnotationBbox(
                    icon_obj, (icon_cx, icon_cy),
                    frameon=False, zorder=5
                )
                ax.add_artist(ab)

            # Card Title next to icon
            ax.text(
                sx + 5.3, cy + card_h - 3.6, card["title"],
                fontsize=11.0, weight="bold", color=text_primary,
                va="center", zorder=5
            )

            # Tech Badge Pill below title
            badge_w = len(card["badge"]) * 0.44 + 1.6
            badge_pill = patches.FancyBboxPatch(
                (sx + 5.3, cy + card_h - 6.6), badge_w, 2.0,
                boxstyle="round,pad=0.1,rounding_size=0.5",
                facecolor=pill_bg,
                edgecolor=accent,
                linewidth=0.8,
                zorder=4
            )
            ax.add_patch(badge_pill)
            ax.text(
                sx + 5.3 + badge_w / 2.0, cy + card_h - 5.6, card["badge"],
                fontsize=7.5, weight="bold", color=accent if dark_mode else accent,
                ha="center", va="center", zorder=5
            )

            # Inner Divider Line
            ax.plot([sx + 1.5, sx + sw - 1.5], [cy + card_h - 8.6, cy + card_h - 8.6],
                    color=divider_color, linewidth=0.8, zorder=4)

            # Clean bullet points
            by = cy + card_h - 12.2
            for bullet in card["bullets"]:
                # Custom bullet icon / dot
                ax.plot(sx + 2.5, by, marker="o", markersize=3.2, color=accent, zorder=5)
                # Bullet text
                ax.text(
                    sx + 3.6, by, bullet,
                    fontsize=8.5, color=text_secondary,
                    va="center", zorder=5
                )
                by -= 4.6

    # ----------------------------------------------------
    # 4. DATA FLOW INTER-STAGE ARROWS & LABELS
    # ----------------------------------------------------
    flows = [
        # Stage 1 -> Stage 2
        {"x1": 20.0, "x2": 22.25, "y": 65.5, "accent": "#0284C7"},
        {"x1": 20.0, "x2": 22.25, "y": 33.5, "accent": "#0284C7"},

        # Stage 2 -> Stage 3
        {"x1": 38.75, "x2": 41.0, "y": 65.5, "accent": "#6366F1"},
        {"x1": 38.75, "x2": 41.0, "y": 33.5, "accent": "#6366F1"},

        # Stage 3 -> Stage 4
        {"x1": 57.5, "x2": 59.75, "y": 65.5, "accent": "#10B981"},
        {"x1": 57.5, "x2": 59.75, "y": 33.5, "accent": "#10B981"},

        # Stage 4 -> Stage 5
        {"x1": 76.25, "x2": 78.5, "y": 65.5, "accent": "#F59E0B"},
        {"x1": 76.25, "x2": 78.5, "y": 33.5, "accent": "#F59E0B"},
    ]

    for flow in flows:
        arrow = patches.FancyArrowPatch(
            (flow["x1"], flow["y"]), (flow["x2"], flow["y"]),
            arrowstyle="-|>",
            mutation_scale=15,
            linewidth=2.2,
            color=flow["accent"],
            zorder=4
        )
        ax.add_patch(arrow)

    # Re-ID Feedback Loop Arrow (Stage 4 to Stage 3 / 2)
    reid_arrow = patches.FancyArrowPatch(
        (68.0, 19.5), (30.5, 19.5),
        connectionstyle="arc3,rad=-0.22",
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=2.0,
        linestyle="--",
        color="#F59E0B",
        zorder=4
    )
    ax.add_patch(reid_arrow)

    # Pill for Re-ID feedback loop
    reid_pill = patches.FancyBboxPatch(
        (42.5, 11.2), 18.0, 2.6,
        boxstyle="round,pad=0.1,rounding_size=0.6",
        facecolor="#1A243B" if dark_mode else "#FEF3C7",
        edgecolor="#F59E0B",
        linewidth=1.0,
        zorder=5
    )
    ax.add_patch(reid_pill)
    ax.text(
        51.5, 12.5, "↺ Zero-Shot Re-ID Feature Bank Matching Loop",
        fontsize=7.8, weight="bold", color="#F59E0B" if dark_mode else "#B45309",
        ha="center", va="center", zorder=6
    )

    # ----------------------------------------------------
    # 5. BOTTOM FOUNDATION & HARDWARE ACCELERATION BAR
    # ----------------------------------------------------
    bar_y = 3.5
    bar_h = 6.0
    bar_box = patches.FancyBboxPatch(
        (3.5, bar_y), 93.0, bar_h,
        boxstyle="round,pad=0.2,rounding_size=1.0",
        facecolor=bar_bg,
        edgecolor=bar_border,
        linewidth=1.2,
        zorder=3
    )
    ax.add_patch(bar_box)

    # GPU / Hardware Icon Container
    gpu_badge = patches.Circle(
        (6.5, bar_y + bar_h / 2.0), radius=2.0,
        facecolor="#0C2340" if dark_mode else "#E0F2FE",
        edgecolor="#38BDF8",
        linewidth=1.2,
        zorder=4
    )
    ax.add_patch(gpu_badge)

    gpu_icon = get_icon("gpu", zoom=0.42)
    if gpu_icon:
        ab = AnnotationBbox(gpu_icon, (6.5, bar_y + bar_h / 2.0), frameon=False, zorder=5)
        ax.add_artist(ab)

    # Hardware Bar Content Title
    ax.text(
        9.6, bar_y + bar_h / 2.0 + 1.2,
        "HARDWARE ACCELERATION & HIGH-PERFORMANCE RUNTIME FOUNDATION",
        fontsize=10.2, weight="bold", color="#38BDF8" if dark_mode else "#0284C7",
        va="center", zorder=5
    )

    # Hardware Badges
    pills = [
        "NVIDIA CUDA 12.x Core Acceleration",
        "PyTorch 2.x Deep Learning",
        "Ultralytics YOLO-World FP16",
        "OpenAI ViT-B/32 Zero-Shot",
        "Sub-30ms Real-Time Inference"
    ]
    px = 9.6
    for ptext in pills:
        pw = len(ptext) * 0.38 + 1.6
        pbox = patches.FancyBboxPatch(
            (px, bar_y + 1.0), pw, 1.8,
            boxstyle="round,pad=0.1,rounding_size=0.5",
            facecolor=bar_badge_bg,
            edgecolor=bar_badge_border,
            linewidth=0.8,
            zorder=4
        )
        ax.add_patch(pbox)
        ax.text(
            px + pw / 2.0, bar_y + 1.9, ptext,
            fontsize=7.2, weight="bold", color=text_primary,
            ha="center", va="center", zorder=5
        )
        px += pw + 1.2

    # Save outputs
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(output_path, dpi=200, facecolor=bg_color, edgecolor="none", bbox_inches="tight", pad_inches=0.1)
    plt.close()
    print(f"Architecture diagram successfully generated: {output_path}")

if __name__ == "__main__":
    dark_out1 = os.path.join(os.path.dirname(__file__), "system_architecture_diagram.png")
    dark_out2 = os.path.join(os.path.dirname(__file__), "Object_permanence", "outputs", "plots", "system_architecture_diagram.png")
    light_out = os.path.join(os.path.dirname(__file__), "system_architecture_diagram_light.png")

    os.makedirs(os.path.dirname(dark_out2), exist_ok=True)
    
    # 1. Primary SIH PPT Dark Mode version
    build_sih_architecture_diagram(dark_out1, dark_mode=True)
    build_sih_architecture_diagram(dark_out2, dark_mode=True)

    # 2. Report / Paper Light Mode version
    build_sih_architecture_diagram(light_out, dark_mode=False)
