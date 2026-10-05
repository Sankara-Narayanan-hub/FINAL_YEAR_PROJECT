import math
from collections import deque
from enum import Enum
import numpy as np
import pandas as pd


def calculate_delta_e(lab1: tuple, lab2: tuple) -> float:
    """Euclidean distance in CIELAB color space (CIE76 metric)."""
    if not lab1 or not lab2:
        return 0.0
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2
    return float(math.sqrt((l1 - l2)**2 + (a1 - a2)**2 + (b1 - b2)**2))


class ObjectVisibilityState(Enum):
    """Discrete state machine representing physical object persistence."""
    VISIBLE = "VISIBLE"               # Actively detected by sensor/vision model
    OCCLUDED = "OCCLUDED"             # Missing from sensory view, but predicted within frame bounds
    OUT_OF_BOUNDS = "OUT_OF_BOUNDS"   # Extrapolated trajectory has exited frame boundaries
    LOST = "LOST"                     # Exceeded maximum temporal memory retention threshold

class MemoryTrackSlot:
    """
    Maintains persistent kinematic state, trajectory buffer, ballistic prediction,
    and physical attribute stability (shape, scale, color) for a single tracked physical entity.
    """

    def __init__(
        self,
        track_id: int,
        class_name: str,
        initial_box: tuple,
        confidence: float,
        frame_idx: int,
        history_len: int = 30,
        attributes: dict = None
    ):
        self.track_id = track_id
        self.class_name = class_name
        self.state = ObjectVisibilityState.VISIBLE
        
        # Kinematic history buffers
        self.history_centroids = deque(maxlen=history_len)
        self.history_boxes = deque(maxlen=history_len)
        self.history_areas = deque(maxlen=history_len)
        self.history_frames = deque(maxlen=history_len)
        
        # Motion vectors (pixels / frame)
        self.velocity = np.zeros(2, dtype=np.float32)  # [vx, vy]
        self.acceleration = np.zeros(2, dtype=np.float32)  # [ax, ay]
        
        # Ballistic predictions during occlusion
        self.predicted_centroid = None  # (pred_x, pred_y)
        self.predicted_box = None       # (pred_x1, pred_y1, pred_x2, pred_y2)
        
        # Counters and lifetime metrics
        self.first_seen_frame = frame_idx
        self.last_seen_frame = frame_idx
        self.frames_visible = 0
        self.frames_occluded = 0
        self.total_occlusion_episodes = 0
        self.confidence_decay = float(confidence)

        # Attribute tracking (shape, size, aspect ratio, color)
        self.baseline_attributes = dict(attributes or {})
        self.current_attributes = dict(attributes or {})
        self.pre_occlusion_attributes = None
        self.morph_count = 0
        
        # Appearance prototype & temporal hysteresis accumulator (ObjectLedger principle)
        self.appearance_prototype_lab = attributes.get("lab") if attributes else None
        self.morph_candidate = {"color": None, "lab": None, "streak": 0, "start_frame": 0}
        
        # Initialize with first detection
        self.update_visible(frame_idx, initial_box, confidence, class_name, attributes)

    def update_visible(self, frame_idx: int, box: tuple, confidence: float, class_name: str = None, attributes: dict = None):
        """Updates slot with active sensory detection and refreshed physical attributes."""
        if class_name:
            self.class_name = class_name
        if attributes:
            self.current_attributes = dict(attributes)
            if not self.baseline_attributes:
                self.baseline_attributes = dict(attributes)
            
            # Smoothly update appearance prototype if observation is within normal illumination envelope
            new_lab = attributes.get("lab")
            if new_lab:
                if self.appearance_prototype_lab is None:
                    self.appearance_prototype_lab = tuple(new_lab)
                else:
                    de = calculate_delta_e(self.appearance_prototype_lab, new_lab)
                    if de < 22.0:
                        self.appearance_prototype_lab = tuple(
                            round(0.85 * p + 0.15 * n, 2)
                            for p, n in zip(self.appearance_prototype_lab, new_lab)
                        )
            
        x1, y1, x2, y2 = box
        w = max(float(x2 - x1), 1.0)
        h = max(float(y2 - y1), 1.0)
        cx = float(x1 + w / 2.0)
        cy = float(y1 + h / 2.0)
        area = w * h

        # Update velocity using exponential moving average (EMA)
        if len(self.history_centroids) > 0:
            prev_cx, prev_cy = self.history_centroids[-1]
            prev_frame = self.history_frames[-1]
            dt = max(frame_idx - prev_frame, 1)
            instant_vx = (cx - prev_cx) / dt
            instant_vy = (cy - prev_cy) / dt
            instant_vel = np.array([instant_vx, instant_vy], dtype=np.float32)

            alpha = 0.70  # EMA smoothing factor
            if np.all(self.velocity == 0):
                self.velocity = instant_vel
            else:
                new_velocity = alpha * instant_vel + (1.0 - alpha) * self.velocity
                self.acceleration = (new_velocity - self.velocity) / dt
                self.velocity = new_velocity

        # Append to histories
        self.history_centroids.append((cx, cy))
        self.history_boxes.append((x1, y1, x2, y2))
        self.history_areas.append(area)
        self.history_frames.append(frame_idx)

        # Update state
        self.state = ObjectVisibilityState.VISIBLE
        self.last_seen_frame = frame_idx
        self.frames_visible += 1
        self.frames_occluded = 0
        self.confidence_decay = float(confidence)
        self.predicted_centroid = (cx, cy)
        self.predicted_box = (x1, y1, x2, y2)

    def predict_dead_reckoning(
        self,
        frame_idx: int,
        frame_width: int,
        frame_height: int,
        max_reappearance_gap: int = 90
    ) -> tuple:
        """
        Projects object trajectory forward during sensory absence (dead-reckoning).
        Snapshots pre-occlusion attributes when transitioning to OCCLUDED.
        """
        self.frames_occluded += 1
        
        # If transitioning from VISIBLE to OCCLUDED, count episode and snapshot pre-occlusion attributes
        if self.state == ObjectVisibilityState.VISIBLE:
            self.total_occlusion_episodes += 1
            self.state = ObjectVisibilityState.OCCLUDED
            self.pre_occlusion_attributes = dict(self.current_attributes)

        # Extrapolate centroid position using current velocity
        last_cx, last_cy = self.history_centroids[-1]
        dt = self.frames_occluded
        
        # Dead-reckoning position: P_pred = P_last + V * dt
        pred_cx = last_cx + float(self.velocity[0]) * dt
        pred_cy = last_cy + float(self.velocity[1]) * dt
        self.predicted_centroid = (pred_cx, pred_cy)

        # Extrapolate bounding box keeping last known dimensions
        last_box = self.history_boxes[-1]
        w = last_box[2] - last_box[0]
        h = last_box[3] - last_box[1]
        
        pred_x1 = pred_cx - w / 2.0
        pred_y1 = pred_cy - h / 2.0
        pred_x2 = pred_cx + w / 2.0
        pred_y2 = pred_cy + h / 2.0
        self.predicted_box = (pred_x1, pred_y1, pred_x2, pred_y2)

        # Decay confidence
        decay_factor = max(0.0, 1.0 - (self.frames_occluded / float(max_reappearance_gap)))
        self.confidence_decay = round(decay_factor, 3)

        # Boundary condition check
        margin = 20  # pixel margin
        is_outside = (
            pred_cx < -margin or pred_cx > (frame_width + margin) or
            pred_cy < -margin or pred_cy > (frame_height + margin)
        )

        if is_outside:
            self.state = ObjectVisibilityState.OUT_OF_BOUNDS
        elif self.frames_occluded > max_reappearance_gap:
            self.state = ObjectVisibilityState.LOST
        else:
            self.state = ObjectVisibilityState.OCCLUDED

        return self.predicted_box, self.state


def are_classes_compatible(cls1: str, cls2: str) -> bool:
    """Semantic compatibility check for robust re-identification across synonym/open-world shifts."""
    c1, c2 = cls1.lower().strip(), cls2.lower().strip()
    if c1 == c2:
        return True
    small_objects = {
        "ball", "sports ball", "sphere", "toy", "block", "cube", "fruit", "apple", "orange",
        "bottle", "cup", "can", "balloon", "bowl", "frisbee", "disc", "cylinder"
    }
    if c1 in small_objects and c2 in small_objects:
        return True
    box_objects = {"box", "cardboard box", "crate", "cube"}
    if c1 in box_objects and c2 in box_objects:
        return True
    vehicles = {"car", "automobile", "vehicle", "truck", "bus", "van", "suv"}
    if c1 in vehicles and c2 in vehicles:
        return True
    people = {"person", "pedestrian", "runner", "cyclist"}
    if c1 in people and c2 in people:
        return True
    two_wheelers = {"bicycle", "bike", "cycle", "motorcycle", "motorbike"}
    if c1 in two_wheelers and c2 in two_wheelers:
        return True
    return False


class PersistentMemoryBank:
    """
    50% Milestone Core Engine: Maintains an explicit memory bank of all tracked entities,
    manages visibility state transitions, performs dead-reckoning extrapolation during occlusion,
    executes memory-guided re-identification, and tracks physical attribute continuity
    (shape invariance, scale stability, color morphing).
    """

    def __init__(
        self,
        frame_width: int = 1920,
        frame_height: int = 1080,
        max_reappearance_gap: int = 90,
        spatial_proximity_thresh: float = 0.35,
        size_similarity_thresh: float = 0.60
    ):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.max_reappearance_gap = max_reappearance_gap
        self.spatial_proximity_thresh = spatial_proximity_thresh
        self.size_similarity_thresh = size_similarity_thresh
        self.diagonal = math.sqrt(frame_width**2 + frame_height**2) if (frame_width and frame_height) else 1.0
        
        # Memory state storage
        self.slots: dict[int, MemoryTrackSlot] = {}
        self.next_master_id = 1
        
        # ID re-mapping table (temporary tracker IDs -> persistent master IDs)
        self.tracker_id_to_master_id: dict[int, int] = {}
        
        # Lifecycle, event, and attribute audit histories
        self.lifecycle_log = []
        self.recovery_events = []
        self.attribute_audits = []

    def update(self, frame_idx: int, detections: list[dict]) -> tuple[list[dict], list[dict]]:
        """
        Processes one video frame:
        1. Associates detections with existing memory slots or performs memory re-ID.
        2. Extrapolates missing slots using dead-reckoning.
        3. Measures attribute consistency (shape, scale, color) across occlusions.
        4. Returns (enhanced_active_detections, ghost_predictions_for_occluded_objects).
        """
        active_master_ids_this_frame = set()
        enhanced_detections = []
        unmatched_detections = []
        
        for det in detections:
            raw_track_id = det.get("track_id", -1)
            box = (det["x1"], det["y1"], det["x2"], det["y2"])
            conf = det.get("confidence", 0.0)
            class_name = det.get("class_name", "object")

            if raw_track_id in self.tracker_id_to_master_id:
                master_id = self.tracker_id_to_master_id[raw_track_id]
                slot = self.slots.get(master_id)
                if slot and slot.state == ObjectVisibilityState.VISIBLE:
                    # In-stream physical continuity check (detect plain-sight color/shape shift)
                    prev_color = slot.current_attributes.get("color", "Unknown")
                    base_color = slot.baseline_attributes.get("color", "Unknown")
                    new_color = det.get("color", "Unknown")
                    proto_lab = slot.appearance_prototype_lab or slot.baseline_attributes.get("lab")
                    new_lab = det.get("lab")
                    
                    delta_e = calculate_delta_e(proto_lab, new_lab) if (proto_lab and new_lab) else 0.0
                    
                    # Continuous CIE76 Delta-E and semantic category check
                    is_distinct_color = (
                        prev_color not in ("Unknown", "N/A") and
                        new_color not in ("Unknown", "N/A") and
                        prev_color.lower() != new_color.lower() and
                        delta_e >= 35.0
                    )
                    
                    # Neutral and adjacent alias protection
                    if {prev_color.lower(), new_color.lower()}.issubset({"grey", "black", "dark grey"}) and delta_e < 45.0:
                        is_distinct_color = False
                    if {prev_color.lower(), new_color.lower()}.issubset({"yellow", "orange"}) and delta_e < 28.0:
                        is_distinct_color = False

                    if is_distinct_color:
                        cand = slot.morph_candidate
                        if cand.get("color") == new_color:
                            cand["streak"] = cand.get("streak", 0) + 1
                        else:
                            slot.morph_candidate = {
                                "color": new_color,
                                "lab": new_lab,
                                "streak": 1,
                                "start_frame": frame_idx
                            }
                        
                        # Temporal Persistence: must be sustained for >= 5 consecutive frames!
                        if slot.morph_candidate["streak"] == 5:
                            slot.morph_count = getattr(slot, "morph_count", 0) + 1
                            print(f"\n[PLAIN-SIGHT MORPHING @ Frame {frame_idx:03d}] ID {master_id} ({class_name}) COLOR SHIFT: {base_color} -> {new_color} (Delta-E: {delta_e:.1f}, Sustained 5 frames)")
                            
                            prev_w = slot.current_attributes.get('width', 0)
                            prev_h = slot.current_attributes.get('height', 0)
                            prev_area = float(slot.current_attributes.get('area', 1.0))
                            new_w = det.get('width', 0)
                            new_h = det.get('height', 0)
                            new_area = float(det.get('area', 1.0))
                            area_cons = round(min(prev_area, new_area) / max(prev_area, new_area, 1.0) * 100.0, 2)
                            
                            attr_audit = {
                                "frame": frame_idx,
                                "master_track_id": master_id,
                                "raw_tracker_id": raw_track_id,
                                "class_name": class_name,
                                "occlusion_gap_frames": 0,
                                "pre_size": f"{prev_w}x{prev_h} ({prev_area:.0f}px)",
                                "post_size": f"{new_w}x{new_h} ({new_area:.0f}px)",
                                "size_consistency_pct": area_cons,
                                "pre_shape": f"AR {slot.current_attributes.get('aspect_ratio', 1.0):.2f}",
                                "post_shape": f"AR {det.get('aspect_ratio', 1.0):.2f}",
                                "shape_consistency_pct": 100.0,
                                "pre_color": base_color,
                                "post_color": new_color,
                                "color_preserved": False,
                                "overall_attribute_score_pct": 30.0,
                                "morphing_detected": True
                            }
                            self.attribute_audits.append(attr_audit)
                            slot.appearance_prototype_lab = new_lab
                    else:
                        if slot.morph_candidate.get("streak", 0) > 0:
                            slot.morph_candidate["streak"] = max(0, slot.morph_candidate["streak"] - 1)

                    # Continuous tracking confirmation
                    slot.update_visible(frame_idx, box, conf, class_name, attributes=det)
                    active_master_ids_this_frame.add(master_id)
                    
                    det_copy = dict(det)
                    det_copy["raw_track_id"] = raw_track_id
                    det_copy["track_id"] = master_id
                    det_copy["memory_state"] = slot.state.value
                    det_copy["velocity_x"] = round(float(slot.velocity[0]), 2)
                    det_copy["velocity_y"] = round(float(slot.velocity[1]), 2)
                    enhanced_detections.append(det_copy)
                    continue

            unmatched_detections.append(det)

        # 2. Memory-Guided Re-Identification for unmatched/new detections
        candidate_slots = [
            slot for slot in self.slots.values()
            if slot.state == ObjectVisibilityState.OCCLUDED and slot.track_id not in active_master_ids_this_frame
        ]

        for det in unmatched_detections:
            raw_track_id = det.get("track_id", -1)
            box = (det["x1"], det["y1"], det["x2"], det["y2"])
            w = det.get("width", max(box[2] - box[0], 1.0))
            h = det.get("height", max(box[3] - box[1], 1.0))
            det_cx = det.get("center_x", box[0] + w / 2.0)
            det_cy = det.get("center_y", box[1] + h / 2.0)
            det_area = w * h
            conf = det.get("confidence", 0.0)
            class_name = det.get("class_name", "object")

            best_slot = None
            best_cost = float("inf")
            best_spatial_err = 0.0

            # Robust spatial proximity threshold (generative video motion corridor)
            effective_proximity_thresh = max(0.35, self.spatial_proximity_thresh)

            for slot in candidate_slots:
                if slot.track_id in active_master_ids_this_frame:
                    continue
                if not are_classes_compatible(slot.class_name, class_name):
                    continue

                # Predicted coordinates vs detected coordinates
                pred_cx, pred_cy = slot.predicted_centroid if slot.predicted_centroid else slot.history_centroids[-1]
                spatial_dist = math.sqrt((det_cx - pred_cx)**2 + (det_cy - pred_cy)**2)
                norm_dist = spatial_dist / self.diagonal

                # Scale area comparison
                last_area = max(slot.history_areas[-1], 1.0)
                area_ratio = det_area / last_area
                size_diff = abs(area_ratio - 1.0)

                # Cost function: 70% normalized spatial proximity + 30% scale deviation
                cost = (0.70 * norm_dist) + (0.30 * min(size_diff, 1.0))

                # Allow partial emergence slivers (when an object emerges from behind an occluder)
                size_acceptable = (size_diff <= self.size_similarity_thresh) or (area_ratio >= 0.20 and norm_dist <= effective_proximity_thresh * 0.75)

                if norm_dist <= effective_proximity_thresh and size_acceptable:
                    if cost < best_cost:
                        best_cost = cost
                        best_slot = slot
                        best_spatial_err = spatial_dist

            if best_slot is not None:
                # SUCCESSFUL MEMORY RECOVERY
                master_id = best_slot.track_id
                self.tracker_id_to_master_id[raw_track_id] = master_id
                
                # Attribute Continuity Analysis (Pre-Occlusion vs Post-Occlusion)
                pre_attrs = best_slot.pre_occlusion_attributes or best_slot.baseline_attributes or {}
                post_attrs = dict(det)
                
                pre_area = max(float(pre_attrs.get("area", 1.0)), 1.0)
                post_area = max(float(post_attrs.get("area", 1.0)), 1.0)
                size_consistency = round(min(pre_area, post_area) / max(pre_area, post_area) * 100.0, 2)

                pre_ar = max(float(pre_attrs.get("aspect_ratio", 1.0)), 0.01)
                post_ar = max(float(post_attrs.get("aspect_ratio", 1.0)), 0.01)
                shape_consistency = round(min(pre_ar, post_ar) / max(pre_ar, post_ar) * 100.0, 2)

                color_pre = pre_attrs.get("color", "Unknown")
                color_post = post_attrs.get("color", "Unknown")
                pre_lab = pre_attrs.get("lab") or best_slot.appearance_prototype_lab
                post_lab = post_attrs.get("lab")

                delta_e = calculate_delta_e(pre_lab, post_lab) if (pre_lab and post_lab) else 0.0

                # Strict semantic category and metric verification
                if color_pre.lower() != color_post.lower():
                    if {color_pre.lower(), color_post.lower()}.issubset({"grey", "black", "dark grey"}) and delta_e < 40.0:
                        color_preserved = True
                    elif {color_pre.lower(), color_post.lower()}.issubset({"yellow", "orange"}) and delta_e < 28.0:
                        color_preserved = True
                    elif {color_pre.lower(), color_post.lower()}.issubset({"cyan", "blue"}) and delta_e < 22.0:
                        color_preserved = True
                    else:
                        color_preserved = False
                else:
                    color_preserved = (delta_e < 35.0)

                overall_attribute_score = round(
                    0.40 * size_consistency + 0.40 * shape_consistency + (20.0 if color_preserved else 0.0), 2
                )
                
                # Physical emergence tolerance: partial slivers upon re-emergence are normal physical disocclusion.
                morphing_detected = (not color_preserved) or (shape_consistency < 45.0) or (size_consistency < 25.0 and best_slot.frames_occluded > 15)

                attr_audit = {
                    "frame": frame_idx,
                    "master_track_id": master_id,
                    "raw_tracker_id": raw_track_id,
                    "class_name": class_name,
                    "occlusion_gap_frames": best_slot.frames_occluded,
                    "pre_size": f"{pre_attrs.get('width', 0)}x{pre_attrs.get('height', 0)} ({pre_area:.0f}px)",
                    "post_size": f"{post_attrs.get('width', 0)}x{post_attrs.get('height', 0)} ({post_area:.0f}px)",
                    "size_consistency_pct": size_consistency,
                    "pre_shape": f"AR {pre_ar:.2f} ({pre_attrs.get('shape_type', 'N/A')})",
                    "post_shape": f"AR {post_ar:.2f} ({post_attrs.get('shape_type', 'N/A')})",
                    "shape_consistency_pct": shape_consistency,
                    "pre_color": color_pre,
                    "post_color": color_post,
                    "color_preserved": color_preserved,
                    "overall_attribute_score_pct": overall_attribute_score,
                    "morphing_detected": morphing_detected
                }
                self.attribute_audits.append(attr_audit)

                # Log recovery event
                recovery_record = {
                    "frame": frame_idx,
                    "master_track_id": master_id,
                    "raw_tracker_id": raw_track_id,
                    "class_name": class_name,
                    "occlusion_gap_frames": best_slot.frames_occluded,
                    "prediction_error_px": round(best_spatial_err, 2),
                    "matching_cost": round(best_cost, 4),
                    "event": "MEMORY_RECOVERY_SUCCESS",
                    "color_pre": color_pre,
                    "color_post": color_post,
                    "color_preserved": color_preserved,
                    "size_consistency_pct": size_consistency,
                    "shape_consistency_pct": shape_consistency
                }
                self.recovery_events.append(recovery_record)
                
                # Restore slot to VISIBLE with new attributes
                best_slot.update_visible(frame_idx, box, conf, class_name, attributes=det)
                active_master_ids_this_frame.add(master_id)
                
                det_copy = dict(det)
                det_copy["raw_track_id"] = raw_track_id
                det_copy["track_id"] = master_id
                det_copy["memory_state"] = best_slot.state.value
                det_copy["velocity_x"] = round(float(best_slot.velocity[0]), 2)
                det_copy["velocity_y"] = round(float(best_slot.velocity[1]), 2)
                enhanced_detections.append(det_copy)
            else:
                # Brand new entity
                if raw_track_id != -1 and raw_track_id not in self.tracker_id_to_master_id:
                    master_id = raw_track_id
                else:
                    master_id = self.next_master_id
                    self.next_master_id += 1

                self.tracker_id_to_master_id[raw_track_id] = master_id
                new_slot = MemoryTrackSlot(
                    track_id=master_id,
                    class_name=class_name,
                    initial_box=box,
                    confidence=conf,
                    frame_idx=frame_idx,
                    attributes=det
                )
                self.slots[master_id] = new_slot
                active_master_ids_this_frame.add(master_id)

                det_copy = dict(det)
                det_copy["raw_track_id"] = raw_track_id
                det_copy["track_id"] = master_id
                det_copy["memory_state"] = new_slot.state.value
                det_copy["velocity_x"] = 0.0
                det_copy["velocity_y"] = 0.0
                enhanced_detections.append(det_copy)

        # 3. Predict dead-reckoning for slots NOT detected in this frame
        ghost_predictions = []
        for master_id, slot in self.slots.items():
            if master_id not in active_master_ids_this_frame:
                pred_box, state = slot.predict_dead_reckoning(
                    frame_idx=frame_idx,
                    frame_width=self.frame_width,
                    frame_height=self.frame_height,
                    max_reappearance_gap=self.max_reappearance_gap
                )
                
                if state == ObjectVisibilityState.OCCLUDED:
                    ghost_predictions.append({
                        "frame": frame_idx,
                        "track_id": master_id,
                        "class_name": slot.class_name,
                        "x1": round(pred_box[0], 2),
                        "y1": round(pred_box[1], 2),
                        "x2": round(pred_box[2], 2),
                        "y2": round(pred_box[3], 2),
                        "center_x": round(slot.predicted_centroid[0], 2),
                        "center_y": round(slot.predicted_centroid[1], 2),
                        "confidence_decay": slot.confidence_decay,
                        "frames_occluded": slot.frames_occluded,
                        "color": slot.current_attributes.get("color", "Unknown"),
                        "aspect_ratio": slot.current_attributes.get("aspect_ratio", 1.0)
                    })

            # Record continuous lifecycle state
            self.lifecycle_log.append({
                "frame": frame_idx,
                "master_track_id": master_id,
                "class_name": slot.class_name,
                "state": slot.state.value,
                "frames_visible": slot.frames_visible,
                "frames_occluded": slot.frames_occluded,
                "confidence_decay": slot.confidence_decay,
                "centroid_x": round(slot.predicted_centroid[0], 2) if slot.predicted_centroid else None,
                "centroid_y": round(slot.predicted_centroid[1], 2) if slot.predicted_centroid else None,
                "velocity_x": round(float(slot.velocity[0]), 2),
                "velocity_y": round(float(slot.velocity[1]), 2),
                "color": slot.current_attributes.get("color", "N/A"),
                "area": slot.current_attributes.get("area", 0)
            })

        return enhanced_detections, ghost_predictions

    def get_lifecycle_dataframe(self) -> pd.DataFrame:
        if not self.lifecycle_log:
            return pd.DataFrame(columns=[
                "frame", "master_track_id", "class_name", "state",
                "frames_visible", "frames_occluded", "confidence_decay",
                "centroid_x", "centroid_y", "velocity_x", "velocity_y", "color", "area"
            ])
        return pd.DataFrame(self.lifecycle_log)

    def get_recoveries_dataframe(self) -> pd.DataFrame:
        if not self.recovery_events:
            return pd.DataFrame(columns=[
                "frame", "master_track_id", "raw_tracker_id", "class_name",
                "occlusion_gap_frames", "prediction_error_px", "matching_cost", "event",
                "color_pre", "color_post", "color_preserved", "size_consistency_pct", "shape_consistency_pct"
            ])
        return pd.DataFrame(self.recovery_events)

    def get_attribute_audits_dataframe(self) -> pd.DataFrame:
        if not self.attribute_audits:
            return pd.DataFrame(columns=[
                "frame", "master_track_id", "raw_tracker_id", "class_name",
                "occlusion_gap_frames", "pre_size", "post_size", "size_consistency_pct",
                "pre_shape", "post_shape", "shape_consistency_pct",
                "pre_color", "post_color", "color_preserved", "overall_attribute_score_pct", "morphing_detected"
            ])
        return pd.DataFrame(self.attribute_audits)

    def get_entity_attribute_summaries(self) -> list:
        """Returns comprehensive attribute stability summary for each persistent entity."""
        summaries = []
        for slot_id, slot in self.slots.items():
            base = slot.baseline_attributes or {}
            curr = slot.current_attributes or {}
            
            base_area = float(base.get("area", 1.0))
            curr_area = float(curr.get("area", 1.0))

            # Filter out spurious single-frame or tiny background noise specks (e.g. sidewalk garbage cans or distant leaves)
            if slot.frames_visible < 4 and slot.total_occlusion_episodes == 0 and max(base_area, curr_area) < 800:
                continue

            size_retention = round(min(base_area, curr_area) / max(base_area, curr_area, 1.0) * 100.0, 2)

            base_ar = float(base.get("aspect_ratio", 1.0))
            curr_ar = float(curr.get("aspect_ratio", 1.0))
            shape_retention = round(min(base_ar, curr_ar) / max(base_ar, curr_ar, 0.01) * 100.0, 2)

            color_base = base.get("color", "N/A")
            color_curr = curr.get("color", "N/A")
            base_lab = base.get("lab") or slot.appearance_prototype_lab
            curr_lab = curr.get("lab")
            delta_e = calculate_delta_e(base_lab, curr_lab) if (base_lab and curr_lab) else 0.0

            # Strict semantic category check
            if color_base.lower() != color_curr.lower():
                if {color_base.lower(), color_curr.lower()}.issubset({"grey", "black", "dark grey"}) and delta_e < 40.0:
                    color_held = True
                elif {color_base.lower(), color_curr.lower()}.issubset({"yellow", "orange"}) and delta_e < 28.0:
                    color_held = True
                elif {color_base.lower(), color_curr.lower()}.issubset({"cyan", "blue"}) and delta_e < 22.0:
                    color_held = True
                else:
                    color_held = False
            else:
                color_held = (delta_e < 35.0)

            morph_episodes = getattr(slot, "morph_count", 0)
            had_audit_morph = any(a.get("master_track_id") == slot_id and a.get("morphing_detected", False) for a in self.attribute_audits)
            
            # Perspective scaling tolerance: if an entity has been tracked across many frames, scale change from 3D motion is natural
            size_thresh = 40.0 if slot.frames_visible > 40 else 65.0
            is_consistent = (size_retention >= size_thresh and shape_retention >= 55.0 and color_held and morph_episodes == 0 and not had_audit_morph)

            summaries.append({
                "id": slot_id,
                "class_name": slot.class_name,
                "frames_visible": slot.frames_visible,
                "occlusions": slot.total_occlusion_episodes,
                "base_size": f"{base.get('width', 0)}x{base.get('height', 0)} ({base.get('area', 0):.0f}px)",
                "final_size": f"{curr.get('width', 0)}x{curr.get('height', 0)} ({curr.get('area', 0):.0f}px)",
                "size_retention_pct": size_retention,
                "base_shape": f"AR {base_ar:.2f} ({base.get('shape_type', 'N/A')})",
                "final_shape": f"AR {curr_ar:.2f} ({curr.get('shape_type', 'N/A')})",
                "shape_retention_pct": shape_retention,
                "initial_color": color_base,
                "final_color": color_curr,
                "delta_e": round(delta_e, 2),
                "color_consistent": color_held and (morph_episodes == 0),
                "status": "CONSISTENT" if is_consistent else "MORPHED / INCONSISTENT"
            })
        return summaries

    def compute_50_percent_metrics(self) -> dict:
        """Calculates advanced quantitative metrics for the 50% milestone."""
        total_episodes = sum(slot.total_occlusion_episodes for slot in self.slots.values())
        successful_recoveries = len(self.recovery_events)
        
        recovery_rate = (
            round((successful_recoveries / total_episodes) * 100.0, 2)
            if total_episodes > 0 else 100.0
        )
        
        pred_errors = [e["prediction_error_px"] for e in self.recovery_events]
        mean_pred_error = round(float(np.mean(pred_errors)), 2) if pred_errors else 0.0
        max_occlusion_survived = max(
            [e["occlusion_gap_frames"] for e in self.recovery_events],
            default=0
        )

        # Average attribute stability
        attr_scores = [a["overall_attribute_score_pct"] for a in self.attribute_audits]
        mean_attr_stability = round(float(np.mean(attr_scores)), 2) if attr_scores else 100.0
        morphed_count = sum(1 for a in self.attribute_audits if a.get("morphing_detected", False))

        return {
            "total_occlusion_episodes": total_episodes,
            "successful_memory_recoveries": successful_recoveries,
            "memory_recovery_rate_pct": recovery_rate,
            "mean_trajectory_prediction_error_px": mean_pred_error,
            "max_occlusion_gap_survived_frames": max_occlusion_survived,
            "mean_attribute_stability_pct": mean_attr_stability,
            "persistent_entities_count": len(self.slots),
            "morphing_events_count": morphed_count
        }
