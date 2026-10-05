import os
import json
import math
import pandas as pd
import numpy as np

class MetricsCalculator:
    """
    Computes preliminary object permanence research metrics:
    1. Detection Consistency
    2. Identity Consistency
    3. Object Permanence Score
    """

    def __init__(self, video_info: dict):
        self.video_info = video_info

    def compute_metrics(
        self,
        detections_df: pd.DataFrame,
        events_df: pd.DataFrame,
        memory_metrics: dict = None
    ) -> dict:
        total_frames = self.video_info.get("total_frames", 1)
        if total_frames <= 0:
            total_frames = 1

        # 1. Detection Consistency
        if not detections_df.empty and 'frame' in detections_df.columns:
            frames_with_detections = detections_df['frame'].nunique()
            detection_consistency = min(1.0, frames_with_detections / total_frames)
        else:
            frames_with_detections = 0
            detection_consistency = 0.0

        # Unique Tracked Objects count
        if not detections_df.empty and 'track_id' in detections_df.columns:
            valid_tracks = detections_df[detections_df['track_id'] != -1]
            tracked_objects_count = valid_tracks['track_id'].nunique()
        else:
            tracked_objects_count = 0

        # Event counts
        disappearance_events_count = 0
        reappearance_events_count = 0
        successful_reidentifications = 0
        identity_switches = 0
        lost_without_recovery = 0

        if not events_df.empty and 'event_type' in events_df.columns:
            disappearance_events_count = len(events_df)
            successful_reidentifications = len(events_df[events_df['event_type'] == "SUCCESSFUL_REIDENTIFICATION"])
            identity_switches = len(events_df[events_df['event_type'].isin(["IDENTITY_SWITCH", "TRACK_ID_SWAP"])])
            lost_without_recovery = len(events_df[events_df['event_type'] == "DISAPPEARANCE_WITHOUT_RECOVERY"])
            reappearance_events_count = successful_reidentifications + identity_switches

        # 2. Identity Consistency = 1 - (identity switches / total tracked objects)
        if tracked_objects_count > 0:
            identity_consistency = max(0.0, 1.0 - (identity_switches / tracked_objects_count))
        else:
            identity_consistency = 1.0

        # 3. Object Permanence Score = (successful re-identifications) / (total valid disappearance-reappearance events)
        total_reappearance_opportunities = successful_reidentifications + identity_switches
        if total_reappearance_opportunities > 0:
            permanence_score_ratio = successful_reidentifications / total_reappearance_opportunities
        else:
            # If no disappearances/switches occurred, identity remained perfectly intact
            permanence_score_ratio = 1.0

        permanence_score_pct = round(permanence_score_ratio * 100.0, 2)

        # Trajectory kinematic accuracy relative to characteristic frame scale
        w = float(self.video_info.get("width", 1920) or 1920)
        h = float(self.video_info.get("height", 1080) or 1080)
        diag = math.sqrt(w**2 + h**2)
        char_scale = 0.5 * diag if diag > 0 else 1000.0

        if memory_metrics:
            mean_pred_err = float(memory_metrics.get("mean_trajectory_prediction_error_px", 0.0))
            if memory_metrics.get("successful_memory_recoveries", 0) > 0 and mean_pred_err > 0:
                kinematic_accuracy = max(0.0, 1.0 - (mean_pred_err / char_scale)) * 100.0
            else:
                kinematic_accuracy = 100.0
            attr_stability = float(memory_metrics.get("mean_attribute_stability_pct", 100.0))
            morph_count = int(memory_metrics.get("morphing_events_count", 0))
        else:
            kinematic_accuracy = 100.0
            attr_stability = 100.0
            morph_count = 0

        kinematic_accuracy = round(kinematic_accuracy, 2)
        attr_stability = round(attr_stability, 2)

        # Composite Physical World Model Accuracy (PWMA %)
        # 35% Permanence Score + 25% Identity Consistency + 20% Kinematic Trajectory Accuracy + 20% Attribute Stability
        pwma_score = (
            0.35 * permanence_score_pct +
            0.25 * (identity_consistency * 100.0) +
            0.20 * kinematic_accuracy +
            0.20 * attr_stability
        )
        pwma_score = round(min(100.0, max(0.0, pwma_score)), 2)

        # Physical Violation Rate (PVR / min)
        duration_sec = float(self.video_info.get("duration_sec", 0.0))
        if duration_sec <= 0:
            fps = float(self.video_info.get("fps", 24.0) or 24.0)
            duration_sec = total_frames / fps if fps > 0 else 1.0

        total_violations = lost_without_recovery + identity_switches + morph_count
        pvr_per_min = round((total_violations / max(1.0, duration_sec)) * 60.0, 2)

        # Physical Commonsense Compliance Verdict
        if pwma_score >= 85.0 and pvr_per_min <= 1.5:
            verdict = "HIGH PHYSICAL ACCURACY (COMPLIANT)"
        elif pwma_score >= 60.0 and pvr_per_min <= 6.0:
            verdict = "MODERATE PHYSICAL ACCURACY (PARTIAL COMPLIANCE)"
        else:
            verdict = "LOW PHYSICAL ACCURACY (FREQUENT HALLUCINATIONS)"

        model_acc = self.compute_model_tracking_accuracy(detections_df)
        ovr_metrics = self.compute_occlusion_veracity_metrics(detections_df, events_df)
        semantic_metrics = self.compute_semantic_alignment_metrics(detections_df, video_prompt=self.video_info.get("file_name", None))

        summary = {
            "video_file": self.video_info.get("file_name", "N/A"),
            "total_frames": total_frames,
            "duration_sec": self.video_info.get("duration_sec", 0.0),
            "fps": self.video_info.get("fps", 0.0),
            "frames_with_detections": frames_with_detections,
            "tracked_objects_count": tracked_objects_count,
            "disappearance_events_count": disappearance_events_count,
            "reappearance_events_count": reappearance_events_count,
            "successful_reidentifications": successful_reidentifications,
            "identity_switches": identity_switches,
            "lost_without_recovery": lost_without_recovery,
            "morphing_events_count": morph_count,
            "total_physical_violations": total_violations,
            "model_tracking_accuracy_metrics": model_acc,
            "occlusion_veracity_metrics": ovr_metrics,
            "semantic_alignment_metrics": semantic_metrics,
            "metrics": {
                "detection_consistency_pct": round(detection_consistency * 100.0, 2),
                "identity_consistency_pct": round(identity_consistency * 100.0, 2),
                "object_permanence_score_pct": permanence_score_pct,
                "kinematic_trajectory_accuracy_pct": kinematic_accuracy,
                "attribute_stability_pct": attr_stability,
                "physical_world_model_accuracy_pct": pwma_score,
                "occlusion_veracity_ratio_pct": ovr_metrics["occlusion_veracity_ratio_pct"],
                "semantic_alignment_index_pct": semantic_metrics["semantic_alignment_index_pct"],
                "semantic_target_grounding_pct": semantic_metrics["semantic_target_grounding_pct"],
                "semantic_class_stability_pct": semantic_metrics["semantic_class_stability_pct"],
                "mean_class_entropy": semantic_metrics["mean_class_entropy"],
                "transient_label_flickers": semantic_metrics["transient_label_flickers_count"],
                "physical_violation_rate_per_min": pvr_per_min,
                "physical_commonsense_verdict": verdict,
                "occlusion_veracity_verdict": ovr_metrics["occlusion_veracity_verdict"],
                "semantic_stability_grade": semantic_metrics["semantic_stability_grade"]
            }
        }

        if memory_metrics:
            summary["memory_bank_metrics"] = memory_metrics

        return summary

    def compute_model_tracking_accuracy(self, detections_df: pd.DataFrame) -> dict:
        """
        Evaluates the intrinsic accuracy and stability of the vision model and tracker:
        1. Bounding Box IoU Smoothness (%)
        2. Mean Spatial Center Jitter (px/frame)
        3. Mean Detection Confidence & Confidence Stability (std dev)
        4. Track Lifespan Coverage Ratio (%)
        5. Track Fragmentation Count
        6. Composite Model Tracking Accuracy (MTA %)
        """
        if detections_df.empty or "track_id" not in detections_df.columns:
            return {
                "mean_detection_confidence_pct": 0.0,
                "confidence_std_dev_pct": 0.0,
                "bbox_iou_smoothness_pct": 0.0,
                "bbox_spatial_jitter_px": 0.0,
                "track_lifespan_coverage_pct": 0.0,
                "track_fragmentations": 0,
                "model_tracking_accuracy_pct": 0.0,
                "model_performance_grade": "NO DETECTIONS"
            }

        valid_df = detections_df[detections_df["track_id"] != -1].copy()
        if valid_df.empty:
            return {
                "mean_detection_confidence_pct": 0.0,
                "confidence_std_dev_pct": 0.0,
                "bbox_iou_smoothness_pct": 0.0,
                "bbox_spatial_jitter_px": 0.0,
                "track_lifespan_coverage_pct": 0.0,
                "track_fragmentations": 0,
                "model_tracking_accuracy_pct": 0.0,
                "model_performance_grade": "NO TRACKS"
            }

        # 1. Detection Confidence Metrics
        conf_series = valid_df["confidence"].dropna()
        mean_conf = float(conf_series.mean()) * 100.0 if not conf_series.empty else 0.0
        conf_std = float(conf_series.std()) * 100.0 if len(conf_series) > 1 else 0.0

        # 2. Per-track IoU Smoothness, Jitter, and Lifespan Coverage
        iou_smoothness_list = []
        jitter_list = []
        coverage_list = []
        total_fragmentations = 0

        for track_id, group in valid_df.groupby("track_id"):
            sorted_grp = group.sort_values("frame").reset_index(drop=True)
            n_obs = len(sorted_grp)
            if n_obs < 2:
                continue

            first_frame = sorted_grp["frame"].iloc[0]
            last_frame = sorted_grp["frame"].iloc[-1]
            active_span = max(1, last_frame - first_frame + 1)
            coverage_pct = min(100.0, (n_obs / active_span) * 100.0)
            coverage_list.append(coverage_pct)

            # Count gaps (fragmentations) where frame difference > 1
            frame_diffs = sorted_grp["frame"].diff().dropna()
            frags = int((frame_diffs > 1).sum())
            total_fragmentations += frags

            # Compute consecutive IoU and spatial displacement for adjacent frames
            for i in range(len(sorted_grp) - 1):
                f1 = sorted_grp["frame"].iloc[i]
                f2 = sorted_grp["frame"].iloc[i + 1]
                
                # Compare consecutive frames
                if f2 == f1 + 1:
                    b1 = (sorted_grp["x1"].iloc[i], sorted_grp["y1"].iloc[i], sorted_grp["x2"].iloc[i], sorted_grp["y2"].iloc[i])
                    b2 = (sorted_grp["x1"].iloc[i+1], sorted_grp["y1"].iloc[i+1], sorted_grp["x2"].iloc[i+1], sorted_grp["y2"].iloc[i+1])
                    
                    # IoU
                    inter_x1 = max(b1[0], b2[0])
                    inter_y1 = max(b1[1], b2[1])
                    inter_x2 = min(b1[2], b2[2])
                    inter_y2 = min(b1[3], b2[3])
                    inter_w = max(0.0, inter_x2 - inter_x1)
                    inter_h = max(0.0, inter_y2 - inter_y1)
                    inter_area = inter_w * inter_h
                    
                    a1 = max(0.0, b1[2] - b1[0]) * max(0.0, b1[3] - b1[1])
                    a2 = max(0.0, b2[2] - b2[0]) * max(0.0, b2[3] - b2[1])
                    union_area = a1 + a2 - inter_area
                    iou = (inter_area / union_area) if union_area > 0 else 0.0
                    iou_smoothness_list.append(iou)

                    # Center jitter
                    c1x = sorted_grp["center_x"].iloc[i] if "center_x" in sorted_grp else (b1[0] + b1[2])/2
                    c1y = sorted_grp["center_y"].iloc[i] if "center_y" in sorted_grp else (b1[1] + b1[3])/2
                    c2x = sorted_grp["center_x"].iloc[i+1] if "center_x" in sorted_grp else (b2[0] + b2[2])/2
                    c2y = sorted_grp["center_y"].iloc[i+1] if "center_y" in sorted_grp else (b2[1] + b2[3])/2
                    dist = math.sqrt((c2x - c1x)**2 + (c2y - c1y)**2)
                    jitter_list.append(dist)

        mean_iou_smoothness = float(np.mean(iou_smoothness_list) * 100.0) if iou_smoothness_list else 85.0
        mean_jitter = float(np.mean(jitter_list)) if jitter_list else 0.0
        mean_coverage = float(np.mean(coverage_list)) if coverage_list else 95.0

        # Composite Model Tracking Accuracy (MTA %)
        # 35% IoU Smoothness + 35% Mean Detection Confidence + 30% Lifespan Coverage
        mta_score = (
            0.35 * mean_iou_smoothness +
            0.35 * min(100.0, mean_conf) +
            0.30 * mean_coverage
        )
        mta_score = round(min(100.0, max(0.0, mta_score)), 2)

        # Performance Grade
        if mta_score >= 85.0 and total_fragmentations <= 1:
            grade = "EXCELLENT TRACKING ACCURACY (STABLE & PRECISE)"
        elif mta_score >= 70.0:
            grade = "GOOD TRACKING ACCURACY (ACCEPTABLE)"
        else:
            grade = "MODERATE / NOISY TRACKING ACCURACY"
        return {
            "mean_detection_confidence_pct": round(mean_conf, 2),
            "confidence_std_dev_pct": round(conf_std, 2),
            "bbox_iou_smoothness_pct": round(mean_iou_smoothness, 2),
            "bbox_spatial_jitter_px": round(mean_jitter, 2),
            "track_lifespan_coverage_pct": round(mean_coverage, 2),
            "track_fragmentations": total_fragmentations,
            "model_tracking_accuracy_pct": mta_score,
            "model_performance_grade": grade
        }

    def compute_occlusion_veracity_metrics(
        self,
        detections_df: pd.DataFrame,
        events_df: pd.DataFrame
    ) -> dict:
        """
        Evaluates whether disappearance events represent genuine physical occlusions
        behind another foreground barrier or frame boundary, versus detector dropouts
        or generative vanishing hallucinations.
        
        Gates:
        1. Boundary / Occluder Contact: Overlap with another track or frame border.
        2. Kinematic Duration: Time hidden vs occluder scale.
        3. Trajectory Alignment: Re-emergence on predicted exit side.
        """
        if events_df.empty or "last_visible_frame" not in events_df.columns:
            return {
                "total_disappearance_events": 0,
                "verified_true_occlusions": 0,
                "phantom_disappearances": 0,
                "detector_dropouts": 0,
                "occlusion_veracity_ratio_pct": 100.0,
                "occlusion_veracity_verdict": "NO DISAPPEARANCES (CONTINUOUS)"
            }

        w = float(self.video_info.get("width", 1920) or 1920)
        h = float(self.video_info.get("height", 1080) or 1080)
        border_margin = 25.0  # px margin for frame boundary exit

        total_events = len(events_df)
        verified_true = 0
        phantom_vanish = 0
        detector_dropouts = 0

        # Pre-group detections by frame for fast spatial lookups
        frame_detections = {}
        if not detections_df.empty and "frame" in detections_df.columns:
            for frame_num, grp in detections_df.groupby("frame"):
                frame_detections[int(frame_num)] = grp

        for _, ev in events_df.iterrows():
            f_dis = ev.get("last_visible_frame")
            if pd.isna(f_dis):
                continue
            f_dis = int(f_dis)
            target_id = ev.get("original_track_id")
            missing_dur = ev.get("missing_duration", 0)
            if pd.isna(missing_dur):
                missing_dur = 0
            missing_dur = int(missing_dur)

            df_frame = frame_detections.get(f_dis, pd.DataFrame())
            target_row = df_frame[df_frame["track_id"] == target_id] if not df_frame.empty else pd.DataFrame()

            is_boundary_exit = False
            has_spatial_occluder = False

            if not target_row.empty:
                t_x1 = float(target_row["x1"].iloc[0])
                t_y1 = float(target_row["y1"].iloc[0])
                t_x2 = float(target_row["x2"].iloc[0])
                t_y2 = float(target_row["y2"].iloc[0])
                t_area = max(1.0, (t_x2 - t_x1) * (t_y2 - t_y1))

                # Frame boundary exit check
                if t_x1 <= border_margin or t_y1 <= border_margin or t_x2 >= (w - border_margin) or t_y2 >= (h - border_margin):
                    is_boundary_exit = True

                # Check other foreground tracks at f_dis
                other_tracks = df_frame[df_frame["track_id"] != target_id]
                for _, o_row in other_tracks.iterrows():
                    o_x1 = float(o_row["x1"])
                    o_y1 = float(o_row["y1"])
                    o_x2 = float(o_row["x2"])
                    o_y2 = float(o_row["y2"])

                    # Overlap / Intersection
                    ix1 = max(t_x1, o_x1)
                    iy1 = max(t_y1, o_y1)
                    ix2 = min(t_x2, o_x2)
                    iy2 = min(t_y2, o_y2)
                    iw = max(0.0, ix2 - ix1)
                    ih = max(0.0, iy2 - iy1)
                    inter_area = iw * ih
                    overlap_ratio = inter_area / t_area

                    # Proximity / contact (within 60 pixels)
                    tc_x = (t_x1 + t_x2) / 2.0
                    tc_y = (t_y1 + t_y2) / 2.0
                    oc_x = (o_x1 + o_x2) / 2.0
                    oc_y = (o_y1 + o_y2) / 2.0
                    center_dist = math.sqrt((tc_x - oc_x)**2 + (tc_y - oc_y)**2)

                    if overlap_ratio >= 0.10 or center_dist <= 60.0:
                        has_spatial_occluder = True
                        break

            # Classification
            if is_boundary_exit or has_spatial_occluder:
                verified_true += 1
            else:
                if missing_dur <= 5 and ev.get("reidentified", False):
                    detector_dropouts += 1
                else:
                    phantom_vanish += 1

        ovr_ratio = (verified_true / total_events * 100.0) if total_events > 0 else 100.0
        ovr_ratio = round(ovr_ratio, 2)

        if ovr_ratio >= 85.0:
            verdict = "HIGH OCCLUSION VERACITY (PHYSICALLY GROUNDED)"
        elif ovr_ratio >= 50.0:
            verdict = "MODERATE OCCLUSION VERACITY (MIXED WITH DROPOUTS)"
        else:
            verdict = "LOW OCCLUSION VERACITY (DOMINATED BY VANISHING GLITCHES / DROPOUTS)"

        return {
            "total_disappearance_events": total_events,
            "verified_true_occlusions": verified_true,
            "phantom_disappearances": phantom_vanish,
            "detector_dropouts": detector_dropouts,
            "occlusion_veracity_ratio_pct": ovr_ratio,
            "occlusion_veracity_verdict": verdict
        }

    def compute_semantic_alignment_metrics(
        self,
        detections_df: pd.DataFrame,
        video_prompt: str = None
    ) -> dict:
        """
        Evaluates semantic label consistency, target prompt grounding,
        and temporal class entropy to expose label hallucinations and misclassifications.
        """
        import re

        prompt_str = str(video_prompt or self.video_info.get("file_name", ""))
        clean_prompt = prompt_str.lower().replace(".mp4", "").replace("_", " ").replace("-", " ")
        
        known_entities = [
            "cat", "kitten", "dog", "puppy", "lion", "tiger", "bear", "elephant",
            "kangaroo", "rabbit", "drone", "car", "automobile", "vehicle", "bicycle",
            "bike", "motorcycle", "truck", "bus", "ball", "person", "runner",
            "cyclist", "pedestrian", "table", "chair", "bird", "flower", "tree",
            "monkey", "squirrel", "fox", "rock", "box"
        ]
        target_entities = []
        for k in known_entities:
            if re.search(r'\b' + re.escape(k) + r'\b', clean_prompt) or (k in clean_prompt and len(k) >= 4):
                target_entities.append(k)
        target_entities = list(dict.fromkeys(target_entities))

        def _calc_target_similarity(pred_class: str, targets: list) -> float:
            if not targets:
                return 1.0  # Open-world unconstrained
            pred = pred_class.lower().strip()
            for t in targets:
                t = t.lower().strip()
                if pred == t or t in pred or pred in t:
                    return 1.0
                if (pred, t) in {("car", "vehicle"), ("automobile", "car"), ("bike", "bicycle"), ("bicycle", "bike"), ("pedestrian", "person"), ("runner", "person"), ("kitten", "cat"), ("puppy", "dog")}:
                    return 1.0
                if (t, pred) in {("car", "vehicle"), ("automobile", "car"), ("bike", "bicycle"), ("bicycle", "bike"), ("pedestrian", "person"), ("runner", "person"), ("kitten", "cat"), ("puppy", "dog")}:
                    return 1.0
                if pred in {"cat", "kitten", "lion", "tiger"} and t in {"cat", "kitten", "lion", "tiger"}:
                    return 0.70
                if (pred in {"dog", "puppy"} and t in {"cat", "kitten", "lion", "tiger"}) or (pred in {"cat", "kitten", "lion", "tiger"} and t in {"dog", "puppy"}):
                    return 0.15
                if pred in {"dog", "puppy"} and t in {"lion", "tiger", "bear", "elephant", "kangaroo", "rabbit", "monkey", "squirrel", "fox"}:
                    return 0.15
            if pred in {"table", "chair", "tree", "plant", "flower", "desk", "sofa", "bed", "board", "barrier", "road", "wall", "rock", "box"}:
                return 1.0
            return 0.20

        if detections_df.empty or "track_id" not in detections_df.columns:
            return {
                "semantic_alignment_index_pct": 100.0,
                "semantic_target_grounding_pct": 100.0,
                "semantic_class_stability_pct": 100.0,
                "mean_class_entropy": 0.0,
                "transient_label_flickers_count": 0,
                "dominant_classes_identified": {},
                "semantic_stability_grade": "NO DETECTIONS",
                "target_prompt_entities": target_entities
            }

        valid_df = detections_df[detections_df["track_id"] != -1].copy()
        if valid_df.empty:
            return {
                "semantic_alignment_index_pct": 100.0,
                "semantic_target_grounding_pct": 100.0,
                "semantic_class_stability_pct": 100.0,
                "mean_class_entropy": 0.0,
                "transient_label_flickers_count": 0,
                "dominant_classes_identified": {},
                "semantic_stability_grade": "NO TRACKS",
                "target_prompt_entities": target_entities
            }

        track_sais = []
        track_target_groundings = []
        track_stabilities = []
        track_entropies = []
        total_flickers = 0
        dominant_classes = {}

        for track_id, grp in valid_df.groupby("track_id"):
            n_obs = len(grp)
            if n_obs < 1:
                continue

            class_counts = grp["class_name"].value_counts()
            dom_class = str(class_counts.index[0])
            dom_count = class_counts.iloc[0]
            temporal_stability = (dom_count / n_obs) * 100.0
            track_stabilities.append(temporal_stability)

            # Target grounding
            target_sim = _calc_target_similarity(dom_class, target_entities)
            target_grounding_pct = target_sim * 100.0
            track_target_groundings.append(target_grounding_pct)

            # Unified SAI = Target Grounding * Temporal Stability
            composite_sai = (target_grounding_pct / 100.0) * temporal_stability
            track_sais.append(composite_sai)

            # Flickers (minority class frames)
            flickers = n_obs - dom_count
            total_flickers += flickers

            # Shannon entropy H(C) = - sum(p * log2(p))
            probs = class_counts / n_obs
            entropy = float(-np.sum([p * math.log2(p) for p in probs if p > 0]))
            track_entropies.append(entropy)

            dominant_classes[str(track_id)] = {
                "dominant_class": dom_class,
                "target_grounding_pct": round(target_grounding_pct, 2),
                "temporal_stability_pct": round(temporal_stability, 2),
                "composite_sai_pct": round(composite_sai, 2),
                "entropy": round(entropy, 3),
                "total_frames": n_obs,
                "flicker_frames": flickers,
                "status": "CORRECTLY ALIGNED" if target_grounding_pct >= 70.0 else "LABEL MISCLASSIFICATION / HALLUCINATION"
            }

        mean_sai = float(np.mean(track_sais)) if track_sais else 100.0
        mean_grounding = float(np.mean(track_target_groundings)) if track_target_groundings else 100.0
        mean_stability = float(np.mean(track_stabilities)) if track_stabilities else 100.0
        mean_entropy = float(np.mean(track_entropies)) if track_entropies else 0.0

        if mean_sai >= 90.0 and mean_entropy <= 0.15:
            grade = "EXCELLENT SEMANTIC ALIGNMENT & STABILITY"
        elif mean_sai >= 70.0:
            grade = "MODERATE SEMANTIC ALIGNMENT (OCCASIONAL FLICKERS)"
        else:
            grade = "LOW SEMANTIC ALIGNMENT (LABEL MISCLASSIFICATION / HALLUCINATION)"

        return {
            "semantic_alignment_index_pct": round(mean_sai, 2),
            "semantic_target_grounding_pct": round(mean_grounding, 2),
            "semantic_class_stability_pct": round(mean_stability, 2),
            "mean_class_entropy": round(mean_entropy, 3),
            "transient_label_flickers_count": total_flickers,
            "dominant_classes_identified": dominant_classes,
            "semantic_stability_grade": grade,
            "target_prompt_entities": target_entities
        }

    def save_reports(self, summary: dict, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        
        def _json_default(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, (np.ndarray,)):
                return obj.tolist()
            return str(obj)

        json_path = os.path.join(output_dir, "summary.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=_json_default)
            
        # Save Text Summary Report
        txt_path = os.path.join(output_dir, "summary.txt")
        m = summary['metrics']

        mta_section = ""
        if summary.get("model_tracking_accuracy_metrics"):
            mta = summary["model_tracking_accuracy_metrics"]
            mta_section = f"""
--------------------------------------------------
 MODEL DETECTION & TRACKING ACCURACY METRICS
--------------------------------------------------
MODEL TRACKING ACCURACY (MTA):        {mta.get('model_tracking_accuracy_pct', 0.0):.2f}%
Bounding Box IoU Smoothness:          {mta.get('bbox_iou_smoothness_pct', 0.0):.2f}%
Mean Spatial Jitter:                  {mta.get('bbox_spatial_jitter_px', 0.0):.2f} px/frame
Mean Detection Confidence:            {mta.get('mean_detection_confidence_pct', 0.0):.2f}% (±{mta.get('confidence_std_dev_pct', 0.0):.2f}%)
Track Lifespan Coverage Ratio:        {mta.get('track_lifespan_coverage_pct', 0.0):.2f}%
Track Fragmentations:                 {mta.get('track_fragmentations', 0)}
Model Performance Grade:              {mta.get('model_performance_grade', 'N/A')}
"""

        ovr_section = ""
        if summary.get("occlusion_veracity_metrics"):
            ovr = summary["occlusion_veracity_metrics"]
            ovr_section = f"""
--------------------------------------------------
 OCCLUSION VERACITY & DROPOUT DIAGNOSTICS (OVR)
--------------------------------------------------
OCCLUSION VERACITY RATIO (OVR):       {ovr.get('occlusion_veracity_ratio_pct', 100.0):.2f}%
Verified True Physical Occlusions:    {ovr.get('verified_true_occlusions', 0)}
Phantom Generative Vanishings:        {ovr.get('phantom_disappearances', 0)}
Transient Detector Dropouts:          {ovr.get('detector_dropouts', 0)}
Veracity Diagnosis Verdict:           {ovr.get('occlusion_veracity_verdict', 'N/A')}
"""

        sai_section = ""
        if summary.get("semantic_alignment_metrics"):
            sai = summary["semantic_alignment_metrics"]
            sai_val = sai.get('semantic_alignment_index_pct', sai.get('semantic_class_stability_pct', 100.0))
            sai_section = f"""
--------------------------------------------------
 SEMANTIC TARGET GROUNDING & FLICKER METRICS (SAI)
--------------------------------------------------
SEMANTIC ALIGNMENT INDEX (SAI):        {sai_val:.2f}%
Target Semantic Grounding:             {sai.get('semantic_target_grounding_pct', 100.0):.2f}%
Temporal Class Stability:              {sai.get('semantic_class_stability_pct', 100.0):.2f}%
Mean Class Entropy H(C):               {sai.get('mean_class_entropy', 0.0):.3f}
Transient Label Hallucinations:        {sai.get('transient_label_flickers_count', 0)} frames
Target Prompt Entities:                {', '.join(sai.get('target_prompt_entities', [])) or 'Universal Open-World'}
Semantic Stability Grade:              {sai.get('semantic_stability_grade', 'N/A')}
"""

        pwma_section = f"""
--------------------------------------------------
 PHYSICAL WORLD MODEL ACCURACY & VIOLATION METRICS
--------------------------------------------------
Physical World Model Accuracy (PWMA): {m.get('physical_world_model_accuracy_pct', 0.0):.2f}%
Physical Violation Rate:               {m.get('physical_violation_rate_per_min', 0.0):.2f} violations/min
Kinematic Trajectory Accuracy:        {m.get('kinematic_trajectory_accuracy_pct', 100.0):.2f}%
Attribute & Morphological Stability:  {m.get('attribute_stability_pct', 100.0):.2f}%
Physical Commonsense Verdict:         {m.get('physical_commonsense_verdict', 'N/A')}
"""

        mb_section = ""
        if summary.get("memory_bank_metrics"):
            mb = summary["memory_bank_metrics"]
            mb_section = f"""
--------------------------------------------------
 PERSISTENT MEMORY BANK METRICS
--------------------------------------------------
Persistent Entities Managed:   {mb.get('persistent_entities_count', 0)}
Total Occlusion Episodes:      {mb.get('total_occlusion_episodes', 0)}
Successful Memory Recoveries:  {mb.get('successful_memory_recoveries', 0)}
MEMORY RECOVERY RATE:          {mb.get('memory_recovery_rate_pct', 0.0):.2f}%
Mean Dead-Reckoning Error:     {mb.get('mean_trajectory_prediction_error_px', 0.0):.2f} px
Max Occlusion Gap Survived:    {mb.get('max_occlusion_gap_survived_frames', 0)} frames
"""

        report_text = f"""==================================================
 OBJECT PERMANENCE & MODEL ACCURACY REPORT
==================================================

Video File:                  {summary['video_file']}
Total Frames:                {summary['total_frames']} ({summary['duration_sec']} sec @ {summary['fps']} fps)
Frames with Detections:      {summary['frames_with_detections']}
Unique Tracked Objects:      {summary['tracked_objects_count']}

--------------------------------------------------
 EVENT & ANOMALY BREAKDOWN
--------------------------------------------------
Total Disappearance Events:  {summary['disappearance_events_count']}
Reappearance Events:         {summary['reappearance_events_count']}
  - Successful Re-IDs:       {summary['successful_reidentifications']}
  - Identity Switches:       {summary['identity_switches']}
Permanent Losses (Vanished): {summary['lost_without_recovery']}
Attribute Morphing Events:   {summary.get('morphing_events_count', 0)}
TOTAL PHYSICAL VIOLATIONS:   {summary.get('total_physical_violations', 0)}

--------------------------------------------------
 OBJECT PERMANENCE & IDENTITY METRICS
--------------------------------------------------
Detection Consistency:       {m['detection_consistency_pct']:.2f}%
Identity Consistency:        {m['identity_consistency_pct']:.2f}%
OBJECT PERMANENCE SCORE:     {m['object_permanence_score_pct']:.2f}%{mta_section}{ovr_section}{sai_section}{mb_section}{pwma_section}==================================================
"""
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(report_text)
            
        print(f"[INFO] Summary reports saved to: {output_dir}")
        print(report_text)
        return json_path, txt_path
