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

# 20 New AI Videos + Metadata
new_videos = [
    {"file": "stepvideo_a_cat_is_under_the_table_then_th.mp4", "model": "StepVideo", "scenario": "Cat under table running left (under-table occlusion)", "category": "Dynamic Spatial Relationship"},
    {"file": "hunyuanvideo_a_kangaroo_is_on_the_left_of_a_b.mp4", "model": "Tencent Hunyuan", "scenario": "Kangaroo jumps behind opaque barrier board", "category": "Dynamic Spatial Relationship"},
    {"file": "cogvideo_an_elephant_is_on_the_right_of_a.mp4", "model": "THUDM CogVideo", "scenario": "Elephant walks in front of car (multi-agent occlusion)", "category": "Dynamic Spatial Relationship"},
    {"file": "veo3_a_rabbit_is_in_front_of_a_flower.mp4", "model": "Google Veo3", "scenario": "Rabbit hops behind and around flowerpot", "category": "Dynamic Spatial Relationship"},
    {"file": "cogvideo_a_beige_tiger_is_in_front_of_a_t.mp4", "model": "THUDM CogVideo", "scenario": "Tiger passes behind tree trunk", "category": "Instance Preservation"},
    {"file": "wanx_a_beige_lion_changes_from_big_to.mp4", "model": "Alibaba Wanx", "scenario": "Lion approaches and changes scale and perspective", "category": "Instance Preservation"},
    {"file": "cogvideo_a_man_is_playing_basketball.mp4", "model": "THUDM CogVideo", "scenario": "Player dribbling basketball with dynamic motion", "category": "Instance Preservation"},
    {"file": "kling_a_black_drone_is_floating_in_the.mp4", "model": "Kuaishou Kling", "scenario": "Drone hovering and navigating 3D airspace", "category": "Instance Preservation"},
    {"file": "cogvideo_a_person_is_walking_down_the_str.mp4", "model": "THUDM CogVideo", "scenario": "Pedestrian walking along street perspective", "category": "Motion Rationality"},
    {"file": "veo3_a_sharp_object_slowly_presses_in.mp4", "model": "Google Veo3", "scenario": "Sharp object pressing into elastic balloon surface", "category": "Mechanics & Surface Contact"},
    {"file": "sora_a_bird_is_behind_a_apple_then_the_b.mp4", "model": "OpenAI Sora", "scenario": "Bird occluded behind apple re-emerging right", "category": "Dynamic Spatial Relationship"},
    {"file": "sora_a_bird_is_behind_a_tree_then_the_bi.mp4", "model": "OpenAI Sora", "scenario": "Bird flying behind tree trunk and re-emerging above", "category": "Dynamic Spatial Relationship"},
    {"file": "sora_a_bird_is_above_a_tree_then_the_bir.mp4", "model": "OpenAI Sora", "scenario": "Bird navigating around dense foliage canopy", "category": "Dynamic Spatial Relationship"},
    {"file": "sora_a_bird_is_in_front_of_a_table_then.mp4", "model": "OpenAI Sora", "scenario": "Bird in front of table flying to the right", "category": "Dynamic Spatial Relationship"},
    {"file": "sora_the_match_began_and_team_a_quickly.mp4", "model": "OpenAI Sora", "scenario": "Soccer players sprinting and passing ball with occlusions", "category": "Complex Multi-Agent Plot"},
    {"file": "sora_the_race_began_and_all_the_runners.mp4", "model": "OpenAI Sora", "scenario": "Multi-runner sprint track with dynamic passing", "category": "Complex Multi-Agent Plot"},
    {"file": "sora_the_three_little_pigs_decide_to_bui.mp4", "model": "OpenAI Sora", "scenario": "Three cartoon animals building houses with material interaction", "category": "Complex Plot & Animation"},
    {"file": "sora_a_child_sees_a_lonely_tree_every_da.mp4", "model": "OpenAI Sora", "scenario": "Child walking around park tree with perspective shift", "category": "Complex Narrative Plot"},
    {"file": "sora_in_an_ancient_city_a_young_painter.mp4", "model": "OpenAI Sora", "scenario": "Painter looking out window at street pedestrians", "category": "Complex Urban Narrative"},
    {"file": "sora_the_violet_flower_glowed_mysterious.mp4", "model": "OpenAI Sora", "scenario": "Character walking through glowing fantasy landscape", "category": "Complex Fantasy Narrative"}
]

print("================================================================================")
print(f" BATCH BENCHMARK RUNNER: EVALUATING {len(new_videos)} NEW AI GENERATED VIDEOS")
print("================================================================================")

cfg = load_config(os.path.join(sub_dir, "config", "config.yaml"))
cfg['model']['yolo_weights'] = "weights/yolov8s-worldv2.pt"
cfg['model']['device'] = 0
cfg['output']['save_annotated_video'] = False  # fast processing without video rendering

t0 = time.time()
processed_count = 0

for i, vinfo in enumerate(new_videos):
    fname = vinfo["file"]
    vpath = os.path.join(input_dir, fname)
    if not os.path.exists(vpath):
        print(f"[{i+1}/{len(new_videos)}] MISSING: {fname}")
        continue
        
    print(f"\n[{i+1}/{len(new_videos)}] PROCESSING: {fname} ({vinfo['model']})...")
    v_t0 = time.time()
    try:
        success = process_single_video(vpath, output_dir, cfg)
        elap = time.time() - v_t0
        print(f"      -> Completed in {elap:.1f}s | Success: {success}")
        processed_count += 1
    except Exception as e:
        print(f"      -> [ERROR] Failed: {e}")

total_elapsed = time.time() - t0
print("\n" + "="*80)
print(f"[COMPLETE] Processed {processed_count}/{len(new_videos)} videos in {total_elapsed:.1f}s ({total_elapsed/max(1, processed_count):.1f}s / video)")
print("="*80)
