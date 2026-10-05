import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sub_dir = "Object_permanence"
json_path = os.path.join(sub_dir, "outputs", "reports", "benchmark_evaluation_summary.json")
with open(json_path, "r", encoding="utf-8") as f:
    all_data = json.load(f)

# 1. Curate 12 diverse representative benchmark videos covering all 8 architectures + CGI baseline
target_keys = [
    ("sora_car_mountain_road.mp4", "OpenAI Sora\n(Mountain Car)"),
    ("sora_elephant_car.mp4", "OpenAI Sora\n(Elephant & Car)"),
    ("sora_bouncing_balls.mp4", "OpenAI Sora\n(Bouncing Balls)"),
    ("kling_mountain_car.mp4", "Kling\n(Mountain Car)"),
    ("kling_kangaroo_board.mp4", "Kling\n(Kangaroo Board)"),
    ("kling_a_black_drone.mp4", "Kling\n(Black Drone)"),
    ("hunyuan_mountain_car.mp4", "Hunyuan\n(Mountain Car)"),
    ("gemini_bike.mp4", "Google Veo\n(Cyclist Behind Tree)"),
    ("veo3_a_rabbit_is_in_front_of_a_flower.mp4", "Google Veo3\n(Rabbit & Flower)"),
    ("cogvideo_a_beige_tiger.mp4", "CogVideo\n(Beige Tiger)"),
    ("stepvideo_a_cat_is_under_the_table.mp4", "StepVideo\n(Cat Under Table)"),
    ("wanx_a_beige_lion_changes_from_big_to.mp4", "Alibaba Wanx\n(Lion Morph/Scale)"),
    ("testball3.mp4", "CGI Baseline\n(Physics Ball)"),
]

data = []
labels = []
for fname_prefix, short_label in target_keys:
    match = next((d for d in all_data if d["video"].startswith(fname_prefix.replace(".mp4", ""))), None)
    if match:
        data.append(match)
        labels.append(short_label)

mta = [d["mta"] for d in data]
pwma = [d["pwma"] for d in data]
ovr = [d["ovr"] for d in data]
sai = [d["sai"] for d in data]
iou_sm = [d["iou_smoothness"] for d in data]
jitter = [d["jitter"] for d in data]

x = np.arange(len(labels))
width = 0.38

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 14))
fig.patch.set_facecolor("#0f172a")

for ax in (ax1, ax2, ax3):
    ax.set_facecolor("#1e293b")
    ax.tick_params(colors="white")
    ax.grid(color="#334155", linestyle="--", alpha=0.7)
    for spine in ax.spines.values():
        spine.set_color("#475569")

# Panel 1: MTA vs PWMA Dual Framework
rects1 = ax1.bar(x - width/2, mta, width, label="Tier 1: Model Tracking Accuracy (MTA %)", color="#38bdf8", edgecolor="#0284c7", alpha=0.9)
rects2 = ax1.bar(x + width/2, pwma, width, label="Tier 2: Physical World Model Accuracy (PWMA %)", color="#a855f7", edgecolor="#7e22ce", alpha=0.9)

ax1.set_ylabel("Accuracy (%)", color="white", fontsize=11, fontweight="bold")
ax1.set_title("Dual Framework: Evaluator Tracking Accuracy (MTA) vs Generative Physical Consistency (PWMA)", color="white", fontsize=13, fontweight="bold", pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, color="#cbd5e1", fontsize=9, rotation=0)
ax1.set_ylim(0, 118)
ax1.legend(loc="upper right", facecolor="#0f172a", edgecolor="#475569", labelcolor="white", fontsize=9.5)

for rect in rects1:
    h = rect.get_height()
    ax1.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", color="#38bdf8", fontsize=8, fontweight="bold")

for rect in rects2:
    h = rect.get_height()
    ax1.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", color="#c084fc", fontsize=8, fontweight="bold")

# Panel 2: OVR vs SAI Physical Veracity Framework
rects_ovr = ax2.bar(x - width/2, ovr, width, label="Tier 3: Occlusion Veracity Ratio (OVR %)", color="#f97316", edgecolor="#ea580c", alpha=0.9)
rects_sai = ax2.bar(x + width/2, sai, width, label="Tier 4: Semantic Alignment Index (SAI %)", color="#10b981", edgecolor="#059669", alpha=0.9)

ax2.set_ylabel("Veracity (%)", color="white", fontsize=11, fontweight="bold")
ax2.set_title("Physical Grounding: Occlusion Veracity Ratio (OVR) vs Semantic Label Stability (SAI)", color="white", fontsize=13, fontweight="bold", pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(labels, color="#cbd5e1", fontsize=9, rotation=0)
ax2.set_ylim(0, 118)
ax2.legend(loc="upper right", facecolor="#0f172a", edgecolor="#475569", labelcolor="white", fontsize=9.5)

for rect in rects_ovr:
    h = rect.get_height()
    ax2.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", color="#fb923c", fontsize=8, fontweight="bold")

for rect in rects_sai:
    h = rect.get_height()
    ax2.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", color="#34d399", fontsize=8, fontweight="bold")

# Panel 3: Kinematic Fidelity - IoU Smoothness & Spatial Jitter
rects3 = ax3.bar(x - width/2, iou_sm, width, label="Bounding Box IoU Smoothness (%)", color="#22c55e", edgecolor="#15803d", alpha=0.9)
ax3_twin = ax3.twinx()
ax3_twin.tick_params(colors="#f43f5e")
ax3_twin.set_ylabel("Spatial Jitter (px/frame)", color="#f43f5e", fontsize=11, fontweight="bold")
line1 = ax3_twin.plot(x, jitter, color="#f43f5e", marker="o", linewidth=2.2, markersize=7, label="Spatial Jitter (px/frame)")

ax3.set_ylabel("IoU Smoothness (%)", color="white", fontsize=11, fontweight="bold")
ax3.set_title("Evaluator Kinematic Fidelity: IoU Smoothness & Bounding Box Spatial Jitter", color="white", fontsize=13, fontweight="bold", pad=10)
ax3.set_xticks(x)
ax3.set_xticklabels(labels, color="#cbd5e1", fontsize=9, rotation=0)
ax3.set_ylim(50, 108)
ax3_twin.set_ylim(0, 5)

for rect in rects3:
    h = rect.get_height()
    ax3.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", color="#4ade80", fontsize=8, fontweight="bold")

for i, txt in enumerate(jitter):
    ax3_twin.annotate(f"{txt:.2f}px", (x[i], jitter[i]), textcoords="offset points", xytext=(0, 6),
                      ha="center", color="#fb7185", fontsize=8, fontweight="bold")

plt.tight_layout()
out_plot = os.path.join(sub_dir, "outputs", "plots", "benchmark_comparison_plot.png")
os.makedirs(os.path.dirname(out_plot), exist_ok=True)
plt.savefig(out_plot, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Successfully generated 3-panel benchmark comparison chart at: {out_plot}")

# 2. Generate Model-by-Model Architecture Summary Plot
model_order = [
    "OpenAI Sora",
    "Kuaishou Kling",
    "Tencent Hunyuan",
    "Google Veo3",
    "THUDM CogVideo",
    "StepVideo",
    "Alibaba Wanx",
    "CGI Physics Baseline"
]

m_stats = {}
for d in all_data:
    m = d["model"].replace("Google Veo / Gemini", "Google Veo3")
    if m not in m_stats:
        m_stats[m] = {"mta": [], "pwma": [], "ovr": [], "sai": []}
    m_stats[m]["mta"].append(d["mta"])
    m_stats[m]["pwma"].append(d["pwma"])
    m_stats[m]["ovr"].append(d["ovr"])
    m_stats[m]["sai"].append(d["sai"])

clean_models = [m for m in model_order if m in m_stats]
avg_mta = [np.mean(m_stats[m]["mta"]) for m in clean_models]
avg_pwma = [np.mean(m_stats[m]["pwma"]) for m in clean_models]
avg_ovr = [np.mean(m_stats[m]["ovr"]) for m in clean_models]
avg_sai = [np.mean(m_stats[m]["sai"]) for m in clean_models]

fig_arch, ax_arch = plt.subplots(figsize=(14, 7))
fig_arch.patch.set_facecolor("#0f172a")
ax_arch.set_facecolor("#1e293b")
ax_arch.tick_params(colors="white")
ax_arch.grid(color="#334155", linestyle="--", alpha=0.7)
for spine in ax_arch.spines.values():
    spine.set_color("#475569")

xm = np.arange(len(clean_models))
w = 0.20

r1 = ax_arch.bar(xm - 1.5*w, avg_mta, w, label="MTA (Tracking Accuracy)", color="#38bdf8", edgecolor="#0284c7")
r2 = ax_arch.bar(xm - 0.5*w, avg_pwma, w, label="PWMA (Physical Consistency)", color="#a855f7", edgecolor="#7e22ce")
r3 = ax_arch.bar(xm + 0.5*w, avg_ovr, w, label="OVR (Occlusion Veracity)", color="#f97316", edgecolor="#ea580c")
r4 = ax_arch.bar(xm + 1.5*w, avg_sai, w, label="SAI (Semantic Stability)", color="#10b981", edgecolor="#059669")

ax_arch.set_ylabel("Metric Mean (%)", color="white", fontsize=11, fontweight="bold")
ax_arch.set_title("Cross-Architecture Benchmark Performance: 8 Foundation AI Video Models vs CGI Baseline (25 Videos)", color="white", fontsize=13, fontweight="bold", pad=12)
ax_arch.set_xticks(xm)
ax_arch.set_xticklabels(clean_models, color="#cbd5e1", fontsize=9.5, fontweight="bold")
ax_arch.set_ylim(0, 115)
ax_arch.legend(loc="upper right", facecolor="#0f172a", edgecolor="#475569", labelcolor="white", fontsize=9.5)

for group, col in [(r1, "#38bdf8"), (r2, "#c084fc"), (r3, "#fb923c"), (r4, "#34d399")]:
    for bar in group:
        h = bar.get_height()
        ax_arch.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2),
                         textcoords="offset points", ha="center", va="bottom", color=col, fontsize=7.5, fontweight="bold")

plt.tight_layout()
arch_plot = os.path.join(sub_dir, "outputs", "plots", "benchmark_architecture_summary.png")
plt.savefig(arch_plot, dpi=200, bbox_inches="tight")
plt.close(fig_arch)
print(f"Successfully generated cross-architecture summary chart at: {arch_plot}")

