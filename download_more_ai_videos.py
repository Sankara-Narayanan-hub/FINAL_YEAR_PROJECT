import os
import re
from huggingface_hub import HfApi, hf_hub_download

api = HfApi()
repo_id = "Vchitect/VBench-2.0_sampled_videos"

target_dir = os.path.join("Object_permanence", "data", "input")
os.makedirs(target_dir, exist_ok=True)

print("[INFO] Fetching candidate file list from VBench-2.0...")
all_files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
mp4_files = [f for f in all_files if f.endswith(".mp4")]

# Search for targeted physical permanence & occlusion scenarios
keywords = [
    "behind", "in front of", "under the table", "tree", "board", "car", "table",
    "flowerpot", "box", "ball", "drone", "elephant", "kangaroo", "cat", "dog",
    "rabbit", "tiger", "lion", "basketball", "walking", "running"
]

target_cats = [
    "Dynamic_Spatial_Relationship",
    "Instance_Preservation",
    "Motion_Rationality",
    "Mechanics",
    "Complex_Plot"
]

models_order = ["Sora", "Kling", "HunyuanVideo", "Veo3", "CogVideo", "Wanx", "StepVideo"]

selected_candidates = []
seen_prompts = set()

for model_target in models_order:
    for f in mp4_files:
        parts = f.split("/")
        if len(parts) >= 3:
            model, cat, filename = parts[0], parts[1], parts[2]
            if model == model_target and cat in target_cats:
                fl_lower = filename.lower()
                if any(k in fl_lower for k in keywords):
                    # Normalized prompt key to avoid duplicates
                    key = re.sub(r'-\d+\.mp4$', '', fl_lower)
                    if key not in seen_prompts:
                        seen_prompts.add(key)
                        selected_candidates.append({
                            "model": model,
                            "category": cat,
                            "repo_path": f,
                            "orig_filename": filename
                        })

print(f"[INFO] Total unique targeted candidates identified: {len(selected_candidates)}")

# Select top 21 diverse videos across the models
final_selection = []
per_model_counts = {}

for c in selected_candidates:
    m = c["model"]
    if per_model_counts.get(m, 0) < 3 and len(final_selection) < 21:
        final_selection.append(c)
        per_model_counts[m] = per_model_counts.get(m, 0) + 1

# If still under 20, fill in with any remaining candidates
for c in selected_candidates:
    if c not in final_selection and len(final_selection) < 21:
        final_selection.append(c)

print(f"\n[INFO] Selected {len(final_selection)} AI videos for download:")
for i, item in enumerate(final_selection):
    print(f"  {i+1:02d}. [{item['model']:12s}] ({item['category']:27s}): {item['orig_filename'][:60]}")

print("\n[INFO] Starting download to Object_permanence/data/input/ ...")
downloaded_files = []

for i, item in enumerate(final_selection):
    m_clean = item["model"].lower()
    cat_clean = item["category"].lower()
    
    # Generate clean short slug
    raw_name = re.sub(r'-\d+\.mp4$', '', item["orig_filename"]).lower()
    raw_name = re.sub(r'[^a-z0-9_]', '_', raw_name)
    raw_name = re.sub(r'_+', '_', raw_name).strip('_')
    # Limit length
    slug = raw_name[:35].rstrip('_')
    local_name = f"{m_clean}_{slug}.mp4"
    dest_path = os.path.join(target_dir, local_name)
    
    print(f"[{i+1}/{len(final_selection)}] Downloading: {item['repo_path']} -> {local_name}")
    try:
        cached_path = hf_hub_download(
            repo_id=repo_id,
            repo_type="dataset",
            filename=item["repo_path"],
            local_dir="cache_hf_downloads"
        )
        import shutil
        shutil.copy2(cached_path, dest_path)
        sz_kb = os.path.getsize(dest_path) / 1024
        print(f"       -> Saved ({sz_kb:.1f} KB)")
        downloaded_files.append({
            "video_name": local_name,
            "model": item["model"],
            "category": item["category"],
            "prompt": item["orig_filename"].replace(".mp4", ""),
            "path": dest_path
        })
    except Exception as e:
        print(f"       [ERROR] Failed to download: {e}")

print(f"\n[SUCCESS] Successfully downloaded {len(downloaded_files)} new AI videos!")
import json
with open("new_ai_videos_metadata.json", "w", encoding="utf-8") as f:
    json.dump(downloaded_files, f, indent=2)
