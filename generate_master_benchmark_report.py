import os
import sys
import json
import math
import cv2
import pandas as pd
import numpy as np

root_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(root_dir, "Object_permanence")
sys.path.append(sub_dir)

from src.metrics import MetricsCalculator

reports_dir = os.path.join(sub_dir, "outputs", "reports")
input_dir = os.path.join(sub_dir, "data", "input")

# Comprehensive Suite of 25 Representative AI Generated Benchmark Videos
benchmark_suite = [
    # 1. OpenAI Sora
    {"file": "sora_car_mountain_road.mp4", "model": "OpenAI Sora", "scenario": "Alpine road car occluded by roadside pine trees", "type": "Vehicle Occlusion"},
    {"file": "sora_elephant_car.mp4", "model": "OpenAI Sora", "scenario": "Miniature elephant walking on toy car", "type": "Multi-Entity Interaction"},
    {"file": "sora_bouncing_balls.mp4", "model": "OpenAI Sora", "scenario": "Colored balls bouncing down steps with mutual occlusions", "type": "Dynamic Mechanics"},
    {"file": "sora_a_bird_is_behind_a_apple_then_the_b.mp4", "model": "OpenAI Sora", "scenario": "Bird occluded behind red apple re-emerging right", "type": "Barrier Occlusion"},
    {"file": "sora_a_bird_is_behind_a_tree_then_the_bi.mp4", "model": "OpenAI Sora", "scenario": "Bird flying behind tree trunk and emerging above", "type": "Natural Barrier Occlusion"},
    {"file": "sora_the_match_began_and_team_a_quickly.mp4", "model": "OpenAI Sora", "scenario": "Soccer players sprinting and passing ball", "type": "Multi-Agent Sports"},
    {"file": "sora_the_race_began_and_all_the_runners.mp4", "model": "OpenAI Sora", "scenario": "Multi-runner sprint track with crossing paths", "type": "Crowd Dynamic Tracking"},
    {"file": "sora_the_three_little_pigs_decide_to_bui.mp4", "model": "OpenAI Sora", "scenario": "Three animated pigs building houses", "type": "Cartoon Morphing"},

    # 2. Kuaishou Kling
    {"file": "kling_mountain_car.mp4", "model": "Kuaishou Kling", "scenario": "Car speeding along mountain road occluded by roadside trees", "type": "Vehicle Occlusion"},
    {"file": "kling_kangaroo_board.mp4", "model": "Kuaishou Kling", "scenario": "Kangaroo hops behind opaque wooden board (volume morph)", "type": "Barrier Occlusion & Morph"},
    {"file": "kling_a_black_drone_is_floating_in_the.mp4", "model": "Kuaishou Kling", "scenario": "Black drone navigating 3D airspace", "type": "Small Aerial Entity"},

    # 3. Tencent HunyuanVideo
    {"file": "hunyuan_mountain_car.mp4", "model": "Tencent Hunyuan", "scenario": "Car driving along steep mountain road with camera panning", "type": "Camera Motion & Tracking"},
    {"file": "hunyuanvideo_a_kangaroo_is_on_the_left_of_a_b.mp4", "model": "Tencent Hunyuan", "scenario": "Kangaroo jumps behind opaque barrier board", "type": "Barrier Occlusion"},

    # 4. Google Veo3 / Gemini
    {"file": "gemini_bike.mp4", "model": "Google Veo / Gemini", "scenario": "Cyclists traversing busy city intersection with dense crossings", "type": "Dense Multi-Agent Crossing"},
    {"file": "veo3_a_rabbit_is_in_front_of_a_flower.mp4", "model": "Google Veo3", "scenario": "Rabbit hops behind and around flowerpot", "type": "Object Occlusion"},
    {"file": "veo3_a_sharp_object_slowly_presses_in.mp4", "model": "Google Veo3", "scenario": "Sharp object pressing into elastic balloon surface", "type": "Deformation Mechanics"},

    # 5. THUDM CogVideo
    {"file": "cogvideo_an_elephant_is_on_the_right_of_a.mp4", "model": "THUDM CogVideo", "scenario": "Elephant walks in front of car (spatial crossing)", "type": "Multi-Agent Crossing"},
    {"file": "cogvideo_a_beige_tiger_is_in_front_of_a_t.mp4", "model": "THUDM CogVideo", "scenario": "Tiger passes behind tree trunk", "type": "Natural Barrier Occlusion"},
    {"file": "cogvideo_a_man_is_playing_basketball.mp4", "model": "THUDM CogVideo", "scenario": "Player dribbling basketball with dynamic motion", "type": "Fast Kinematics"},
    {"file": "cogvideo_a_person_is_walking_down_the_str.mp4", "model": "THUDM CogVideo", "scenario": "Pedestrian walking along street perspective", "type": "Perspective Shift"},

    # 6. StepFun StepVideo
    {"file": "stepvideo_a_cat_is_under_the_table_then_th.mp4", "model": "StepVideo", "scenario": "Cat under table running left (under-table occlusion)", "type": "Furniture Occlusion"},

    # 7. Alibaba Wanx
    {"file": "wanx_a_beige_lion_changes_from_big_to.mp4", "model": "Alibaba Wanx", "scenario": "Lion approaches and changes scale and perspective", "type": "Scale & Perspective"},

    # 8. CGI Ground Truth Baselines
    {"file": "testball3.mp4", "model": "CGI Physics Baseline", "scenario": "Ball rolling behind solid wooden pillar (synthetic ground truth)", "type": "Controlled Occlusion"},
    {"file": "TESTBALL.mp4", "model": "CGI Physics Baseline", "scenario": "Red ball bouncing behind gray occluding slab", "type": "Controlled Occlusion"},
    {"file": "demo_occlusion.mp4", "model": "CGI Physics Baseline", "scenario": "Synthetic sphere traversing occluding panel", "type": "Controlled Occlusion"}
]

print("================================================================================")
print(f" COMPUTING MASTER EVALUATION MATRIX ACROSS {len(benchmark_suite)} BENCHMARK VIDEOS")
print("================================================================================")

results = []

for item in benchmark_suite:
    vname = item["file"]
    vpath = os.path.join(input_dir, vname)
    base = os.path.splitext(vname)[0]
    
    det_csv = os.path.join(reports_dir, f"{base}_detections.csv")
    ev_csv = os.path.join(reports_dir, f"{base}_events.csv")
    rec_csv = os.path.join(reports_dir, f"{base}_memory_recoveries.csv")
    attr_csv = os.path.join(reports_dir, f"{base}_attribute_consistency.csv")
    
    if not os.path.exists(det_csv):
        print(f"[SKIP] Detections CSV not found for: {base}")
        continue
        
    def safe_read_csv(p):
        if not os.path.exists(p) or os.path.getsize(p) < 10:
            return pd.DataFrame()
        try:
            return pd.read_csv(p)
        except Exception:
            return pd.DataFrame()

    det_df = safe_read_csv(det_csv)
    ev_df = safe_read_csv(ev_csv)
    
    # Load video info
    w, h, fps, tot, dur = 1280, 720, 24.0, 100, 4.0
    if os.path.exists(vpath):
        cap = cv2.VideoCapture(vpath)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or w
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or h
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or fps
        tot = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or tot
        dur = round(tot / fps, 2) if fps > 0 else dur
        cap.release()
        
    v_info = {
        "file_name": vname,
        "width": w,
        "height": h,
        "fps": fps,
        "total_frames": tot,
        "duration_sec": dur
    }
    
    memory_metrics = None
    if os.path.exists(rec_csv) or os.path.exists(attr_csv):
        df_rec = safe_read_csv(rec_csv)
        df_attr = safe_read_csv(attr_csv)
        
        n_rec = len(df_rec)
        err = float(df_rec['prediction_error_px'].mean()) if (n_rec > 0 and 'prediction_error_px' in df_rec) else 0.0
        max_gap = int(df_rec['occlusion_gap_frames'].max()) if (n_rec > 0 and 'occlusion_gap_frames' in df_rec) else 0
        attr_score = float(df_attr['overall_attribute_score_pct'].mean()) if (not df_attr.empty and 'overall_attribute_score_pct' in df_attr) else 100.0
        morphs = int(df_attr['morphing_detected'].sum()) if (not df_attr.empty and 'morphing_detected' in df_attr) else 0
        
        total_episodes = len(ev_df) if not ev_df.empty else n_rec
        rec_rate = (n_rec / max(1, total_episodes)) * 100.0 if total_episodes > 0 else 100.0
        
        memory_metrics = {
            "total_occlusion_episodes": total_episodes,
            "successful_memory_recoveries": n_rec,
            "memory_recovery_rate_pct": round(rec_rate, 2),
            "mean_trajectory_prediction_error_px": round(err, 2),
            "max_occlusion_gap_survived_frames": max_gap,
            "mean_attribute_stability_pct": round(attr_score, 2),
            "persistent_entities_count": det_df['track_id'].nunique() if ('track_id' in det_df and not det_df.empty) else 1,
            "morphing_events_count": morphs
        }

    calc = MetricsCalculator(v_info)
    summary = calc.compute_metrics(det_df, ev_df, memory_metrics=memory_metrics)
    
    mta = summary["model_tracking_accuracy_metrics"]
    pwma = summary["metrics"]
    ovr = summary["occlusion_veracity_metrics"]
    sai = summary["semantic_alignment_metrics"]
    
    record = {
        "video": vname,
        "model": item["model"],
        "scenario": item["scenario"],
        "type": item["type"],
        "resolution": f"{w}x{h}",
        "fps": fps,
        "frames": tot,
        "duration": f"{dur}s",
        "mta": mta["model_tracking_accuracy_pct"],
        "iou_smoothness": mta["bbox_iou_smoothness_pct"],
        "jitter": mta["bbox_spatial_jitter_px"],
        "confidence": mta["mean_detection_confidence_pct"],
        "lcr": mta["track_lifespan_coverage_pct"],
        "pwma": pwma["physical_world_model_accuracy_pct"],
        "pvr": pwma["physical_violation_rate_per_min"],
        "ovr": ovr["occlusion_veracity_ratio_pct"],
        "true_occlusions": ovr["verified_true_occlusions"],
        "phantom_disappearances": ovr["phantom_disappearances"],
        "detector_dropouts": ovr["detector_dropouts"],
        "sai": sai["semantic_alignment_index_pct"],
        "sta": sai["semantic_target_grounding_pct"],
        "class_stability": sai["semantic_class_stability_pct"],
        "class_entropy": sai["mean_class_entropy"],
        "transient_flickers": sai["transient_label_flickers_count"],
        "target_entities": sai.get("target_prompt_entities", []),
        "dominant_classes": sai.get("dominant_classes_identified", {}),
        "verdict": pwma["physical_commonsense_verdict"]
    }
    results.append(record)
    print(f"[{len(results):02d}] {item['model'][:12]:12s} | {vname[:32]:32s} | MTA: {record['mta']:5.2f}% | PWMA: {record['pwma']:5.2f}% | OVR: {record['ovr']:5.2f}% | SAI: {record['sai']:5.2f}% (STA: {record['sta']:.1f}%)")

# Save JSON
out_json = os.path.join(reports_dir, "benchmark_evaluation_summary.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("\n" + "="*110)
print("                       COMPREHENSIVE MULTI-MODEL BENCHMARK EVALUATION MATRIX")
print("="*110)
print(f"{'#':<3} | {'Video Asset':<34} | {'Model':<16} | {'MTA':<7} | {'PWMA':<7} | {'OVR':<7} | {'SAI':<7} | {'PVR':<6} | {'Verdict'}")
print("-"*110)
for i, r in enumerate(results):
    v_clean = r["verdict"].replace("HIGH PHYSICAL ACCURACY (COMPLIANT)", "COMPLIANT").replace("MODERATE PHYSICAL ACCURACY (PARTIAL COMPLIANCE)", "PARTIAL").replace("LOW PHYSICAL ACCURACY (FREQUENT HALLUCINATIONS)", "HALLUCINATIONS")
    print(f"{i+1:02d} | {r['video']:<34} | {r['model']:<16} | {r['mta']:5.2f}% | {r['pwma']:5.2f}% | {r['ovr']:5.2f}% | {r['sai']:5.2f}% | {r['pvr']:5.2f} | {v_clean}")
print("="*110)
print(f"[SUCCESS] Consolidated {len(results)} evaluated benchmark videos into: {out_json}")
