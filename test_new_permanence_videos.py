import os
import sys
import json
import time

root_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(root_dir, "Object_permanence")
sys.path.append(sub_dir)

from src.main import process_single_video, load_config
from src.metrics import MetricsCalculator

input_dir = os.path.join(sub_dir, "data", "input")
output_dir = os.path.join(sub_dir, "outputs")
reports_dir = os.path.join(sub_dir, "outputs", "reports")

challenge_videos = [
    {"file": "kling_dog_behind_chair.mp4", "model": "Kuaishou Kling", "scenario": "Dog behind chair runs to right", "barrier": "chair"},
    {"file": "cogvideo_dog_behind_chair.mp4", "model": "THUDM CogVideo", "scenario": "Dog behind chair runs to right", "barrier": "chair"},
    {"file": "wanx_cat_box_left.mp4", "model": "Alibaba Wanx", "scenario": "Cat runs behind box to left", "barrier": "box"},
    {"file": "stepvideo_cat_box_left.mp4", "model": "StepFun StepVideo", "scenario": "Cat runs behind box to left", "barrier": "box"},
    {"file": "hunyuan_monkey_apple.mp4", "model": "Tencent Hunyuan", "scenario": "Monkey behind apple jumps front", "barrier": "apple"},
    {"file": "sora_monkey_apple.mp4", "model": "OpenAI Sora", "scenario": "Monkey behind apple jumps front", "barrier": "apple"},
    {"file": "veo3_rabbit_table.mp4", "model": "Google Veo3", "scenario": "Rabbit in front of table jumps left", "barrier": "table"},
    {"file": "wanx_elephant_behind_car.mp4", "model": "Alibaba Wanx", "scenario": "Elephant walks to back of car", "barrier": "car"}
]

print("="*80)
print(f" TESTING {len(challenge_videos)} NEW HARD OBJECT PERMANENCE CHALLENGE VIDEOS")
print("="*80)

cfg = load_config(os.path.join(sub_dir, "config", "config.yaml"))
cfg['model']['yolo_weights'] = "weights/yolov8s-worldv2.pt"
cfg['model']['device'] = 0
cfg['output']['save_annotated_video'] = False

results = []
for i, vinfo in enumerate(challenge_videos):
    fname = vinfo["file"]
    vpath = os.path.join(input_dir, fname)
    if not os.path.exists(vpath):
        print(f"[{i+1}/{len(challenge_videos)}] MISSING: {fname}")
        continue
        
    print(f"\n[{i+1}/{len(challenge_videos)}] RUNNING EVALUATION: {fname} ({vinfo['model']})...")
    t0 = time.time()
    try:
        process_single_video(vpath, output_dir, cfg)
        elap = time.time() - t0
        print(f"      -> Completed in {elap:.1f}s")
    except Exception as e:
        print(f"      -> [ERROR]: {e}")
        continue

    # Load summary report
    base = os.path.splitext(fname)[0]
    json_path = os.path.join(reports_dir, f"{base}_summary.json")
    if not os.path.exists(json_path):
        # Fallback to general summary.json
        json_path = os.path.join(reports_dir, "summary.json")
        
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        mta = data.get("model_tracking_accuracy_metrics", {})
        mets = data.get("metrics", {})
        ovr = data.get("occlusion_veracity_metrics", {})
        sai = data.get("semantic_alignment_metrics", {})
        mem = data.get("memory_bank_metrics", {})
        
        results.append({
            "video": fname,
            "model": vinfo["model"],
            "scenario": vinfo["scenario"],
            "barrier": vinfo["barrier"],
            "mta": mta.get("model_tracking_accuracy_pct", 0),
            "pwma": mets.get("physical_world_model_accuracy_pct", 0),
            "ops": mets.get("object_permanence_score_pct", 0),
            "id_cons": mets.get("identity_consistency_pct", 0),
            "ovr": ovr.get("occlusion_veracity_ratio_pct", 0),
            "sai": sai.get("semantic_alignment_index_pct", 0),
            "sta": sai.get("semantic_target_grounding_pct", 0),
            "pvr": mets.get("physical_violation_rate_per_min", 0),
            "disappearances": data.get("disappearance_events_count", 0),
            "re_ids": data.get("successful_reidentifications", 0),
            "switches": data.get("identity_switches", 0),
            "vanished": data.get("lost_without_recovery", 0),
            "morphs": data.get("morphing_events_count", 0),
            "dominant_classes": list(sai.get("dominant_classes_identified", {}).values()),
            "verdict": mets.get("physical_commonsense_verdict", "N/A")
        })

print("\n" + "="*115)
print("                   OBJECT PERMANENCE STRESS-TEST RESULTS ON 8 NEW VIDEOS")
print("="*115)
header = f"{'#':2s} | {'Model':14s} | {'Video':24s} | {'MTA':6s} | {'PWMA':6s} | {'OPS':6s} | {'OVR':6s} | {'SAI':6s} | {'PVR/min':7s} | {'Violations':10s} | {'Verdict'}"
print(header)
print("-"*115)

for idx, r in enumerate(results):
    v_str = f"Dis:{r['disappearances']}, ReID:{r['re_ids']}, Morph:{r['morphs']}, Van:{r['vanished']}"
    row = f"{idx+1:02d} | {r['model'][:14]:14s} | {r['video'][:24]:24s} | {r['mta']:5.1f}% | {r['pwma']:5.1f}% | {r['ops']:5.1f}% | {r['ovr']:5.1f}% | {r['sai']:5.1f}% | {r['pvr']:6.1f}  | {v_str:10s} | {r['verdict'][:20]}"
    print(row)
print("="*115)

# Save JSON results
out_stress_json = os.path.join(reports_dir, "permanence_stress_test_results.json")
with open(out_stress_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"[SAVED] Permanence stress test results to: {out_stress_json}")
