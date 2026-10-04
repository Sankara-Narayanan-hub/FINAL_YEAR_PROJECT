import os
import cv2
import pandas as pd
import numpy as np

# Disable Ultralytics telemetry and online sync
os.environ["YOLO_VERBOSE"] = "False"
os.environ["ULTRALYTICS_TELEMETRY"] = "False"

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def calculate_delta_e(lab1: tuple, lab2: tuple) -> float:
    """Euclidean distance in CIELAB color space (CIE76 metric)."""
    if not lab1 or not lab2:
        return 0.0
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2
    return float(np.sqrt((l1 - l2)**2 + (a1 - a2)**2 + (b1 - b2)**2))


def extract_visual_attributes(frame: np.ndarray, box: tuple, class_name: str = "object") -> dict:
    """
    Robust physical and visual attribute extraction:
    - Geometric properties (width, height, area, aspect ratio)
    - Shape profile (Spherical / Regular, Horizontal Oblong, Vertical Oblong)
    - Central foreground prior (inner 60% window) to eliminate peripheral background bleed
    - Metric CIELAB coordinates (L*, a*, b*) for continuous color distance (Delta-E)
    - Chroma gating (C* = sqrt(a*^2 + b*^2)) to reliably identify neutral tones (Grey, Black, White)
    - Wide, stable semantic hue boundaries
    """
    x1, y1, x2, y2 = box
    w = max(float(x2 - x1), 1.0)
    h = max(float(y2 - y1), 1.0)
    area = round(float(w * h), 2)
    aspect_ratio = round(float(w / h), 2)

    # Determine geometric shape profile
    if 0.80 <= aspect_ratio <= 1.25:
        shape_type = "Spherical / Regular"
    elif aspect_ratio > 1.25:
        shape_type = "Horizontal Oblong"
    else:
        shape_type = "Vertical Oblong"

    color_name = "Neutral"
    lab_coords = (0.0, 0.0, 0.0)
    hsv_coords = (0, 0, 0)
    chroma = 0.0

    if frame is not None and frame.size > 0:
        h_img, w_img = frame.shape[:2]
        ix1, ix2 = max(0, min(int(x1), w_img - 1)), max(0, min(int(x2), w_img - 1))
        iy1, iy2 = max(0, min(int(y1), h_img - 1)), max(0, min(int(y2), h_img - 1))

        if ix2 > ix1 + 2 and iy2 > iy1 + 2:
            crop = frame[iy1:iy2, ix1:ix2]
            ch, cw = crop.shape[:2]

            lab_full = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
            hsv_full = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

            L_all = lab_full[:, :, 0].astype(float) * (100.0 / 255.0)
            a_all = lab_full[:, :, 1].astype(float) - 128.0
            b_all = lab_full[:, :, 2].astype(float) - 128.0
            chroma_all = np.sqrt(a_all**2 + b_all**2)

            # Check for significant chromatic presence
            chroma_mask = (hsv_full[:, :, 1] >= 38) & (hsv_full[:, :, 2] >= 30) & (chroma_all >= 12.0)
            num_chroma = int(np.sum(chroma_mask))
            total_px = max(ch * cw, 1)
            pct_chroma = (num_chroma / total_px) * 100.0

            # Central foreground focus: 60% inner window
            m_y1, m_y2 = int(ch * 0.20), max(int(ch * 0.80), int(ch * 0.20) + 1)
            m_x1, m_x2 = int(cw * 0.20), max(int(cw * 0.80), int(cw * 0.20) + 1)
            core_crop = crop[m_y1:m_y2, m_x1:m_x2]
            if core_crop.size == 0:
                core_crop = crop

            core_lab = cv2.cvtColor(core_crop, cv2.COLOR_BGR2LAB)
            core_hsv = cv2.cvtColor(core_crop, cv2.COLOR_BGR2HSV)

            core_med_l = float(np.median(core_lab[:, :, 0])) * (100.0 / 255.0)
            core_med_a = float(np.median(core_lab[:, :, 1])) - 128.0
            core_med_b = float(np.median(core_lab[:, :, 2])) - 128.0
            core_chroma = float(np.sqrt(core_med_a**2 + core_med_b**2))
            core_med_s = float(np.median(core_hsv[:, :, 1]))

            # 1. Solid colored objects (balls, balloons, cars) have high core chroma
            if core_chroma >= 10.0 and core_med_s >= 35:
                med_l, med_a, med_b = core_med_l, core_med_a, core_med_b
                med_h = float(np.median(core_hsv[:, :, 0]))
                med_s = core_med_s
                med_v = float(np.median(core_hsv[:, :, 2]))
                is_chromatic = True
            # 2. Wireframe / tubular vehicles (bicycle, motorcycle) whose center is empty road
            elif class_name.lower() in ("bicycle", "bike", "cycle", "motorcycle", "motorbike") and pct_chroma >= 5.0 and num_chroma >= 40:
                med_l = float(np.median(L_all[chroma_mask]))
                med_a = float(np.median(a_all[chroma_mask]))
                med_b = float(np.median(b_all[chroma_mask]))
                med_h = float(np.median(hsv_full[:, :, 0][chroma_mask]))
                med_s = float(np.median(hsv_full[:, :, 1][chroma_mask]))
                med_v = float(np.median(hsv_full[:, :, 2][chroma_mask]))
                is_chromatic = True
            # 3. High chromatic density across full object (>= 25%)
            elif pct_chroma >= 25.0 and num_chroma >= 100:
                med_l = float(np.median(L_all[chroma_mask]))
                med_a = float(np.median(a_all[chroma_mask]))
                med_b = float(np.median(b_all[chroma_mask]))
                med_h = float(np.median(hsv_full[:, :, 0][chroma_mask]))
                med_s = float(np.median(hsv_full[:, :, 1][chroma_mask]))
                med_v = float(np.median(hsv_full[:, :, 2][chroma_mask]))
                is_chromatic = True
            else:
                med_l, med_a, med_b = core_med_l, core_med_a, core_med_b
                med_h = float(np.median(core_hsv[:, :, 0]))
                med_s = core_med_s
                med_v = float(np.median(core_hsv[:, :, 2]))
                is_chromatic = False

            chroma = float(np.sqrt(med_a**2 + med_b**2))
            lab_coords = (round(med_l, 2), round(med_a, 2), round(med_b, 2))
            hsv_coords = (int(med_h), int(med_s), int(med_v))

            # Achromatic / Neutral test using Chroma C* and Saturation
            if not is_chromatic or chroma < 10.0 or med_s < 35:
                if med_l < 22:
                    color_name = "Black"
                elif med_l > 80:
                    color_name = "White"
                elif chroma >= 6.5 and med_b > 4.0 and med_l < 55:
                    color_name = "Brown"
                else:
                    color_name = "Grey"
            else:
                # Standard OpenCV HSV Hue bins:
                if med_h < 11 or med_h >= 168:
                    color_name = "Red"
                elif med_h < 25:
                    color_name = "Orange"
                elif med_h < 38:
                    color_name = "Yellow"
                elif med_h < 85:
                    color_name = "Green"
                elif med_h < 102:
                    color_name = "Cyan"
                elif med_h < 125:
                    color_name = "Blue"
                elif med_h < 155:
                    color_name = "Purple"
                else:
                    color_name = "Pink"

    return {
        "width": round(w, 2),
        "height": round(h, 2),
        "area": area,
        "aspect_ratio": aspect_ratio,
        "shape_type": shape_type,
        "color": color_name,
        "chroma": round(chroma, 2),
        "lab": lab_coords,
        "hsv": hsv_coords
    }


# Universal Physical Object Vocabulary for Zero-Code Open-World Video Understanding
UNIVERSAL_PHYSICAL_VOCABULARY = [
    # Everyday physical items & permanence benchmark objects (no spurious fruits/household hallucinations)
    "ball", "sports ball", "sphere", "balloon", "box", "cardboard box", "cube", "crate",
    "toy", "block", "cup", "bottle", "can", "bowl", "cylinder",
    # Vehicles & transit
    "car", "automobile", "vehicle", "truck", "bus", "van", "suv", "motorcycle", "bicycle", "boat", "airplane",
    # Living beings
    "person", "pedestrian", "dog", "cat", "horse", "animal", "bird",
    # Props & furniture
    "chair", "table", "backpack", "handbag", "suitcase"
]


def get_class_family(class_name: str) -> str:
    """Groups open-world object classes into distinct tracking families to eliminate cross-class track hijacking."""
    c = class_name.lower().strip()
    if c in {"person", "pedestrian", "runner", "cyclist"}:
        return "people"
    if c in {"bicycle", "bike", "cycle", "motorcycle", "motorbike"}:
        return "two_wheelers"
    if c in {
        "ball", "sports ball", "sphere", "toy", "block", "cube", "fruit", "apple", "orange",
        "bottle", "cup", "can", "balloon", "bowl", "frisbee", "disc", "cylinder"
    }:
        return "small_objects"
    if c in {"box", "cardboard box", "crate"}:
        return "containers"
    if c in {"car", "automobile", "vehicle", "truck", "bus", "van", "suv", "boat", "airplane"}:
        return "vehicles"
    return "general"


class ObjectDetectorTracker:
    """
    Unified Open-World Object Detection, Attribute Extraction, and Real-Time Multi-Object Tracking.
    Integrates Ultralytics YOLO-World v2 with Norfair (Kalman-filter multi-object tracking).
    Operates on a universal vocabulary to eliminate manual per-video code modifications.
    Extracts physical object attributes (size, area, aspect ratio, shape, dominant color).
    """

    def __init__(
        self,
        weights: str = "weights/yolov8x-worldv2.pt",
        tracker_type: str = "norfair",
        tracker_config: str = "bytetrack.yaml",
        conf_threshold: float = 0.15,
        iou_threshold: float = 0.35,
        img_size: int = 640,
        device: str = "0",
        target_class: str = None,
        custom_prompts: list = None,
        norfair_distance_function: str = "iou",
        norfair_distance_threshold: float = 0.7,
        norfair_hit_counter_max: int = 15,
        norfair_initialization_delay: int = 1,
        norfair_past_detections_length: int = 5
    ):
        self.weights = weights
        self.tracker_type = tracker_type.lower() if tracker_type else "norfair"
        self.tracker_config = tracker_config
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.img_size = img_size
        
        # Configure compute device safely
        if str(device) in ("0", "cuda", "gpu") and TORCH_AVAILABLE and torch.cuda.is_available():
            self.device = 0
        else:
            self.device = "cpu"
            
        self.target_class = target_class.lower().strip() if target_class else None
        self.is_universal = (custom_prompts is None and self.target_class is None)
        self.custom_prompts = custom_prompts or list(UNIVERSAL_PHYSICAL_VOCABULARY)
        self.detections_history = []
        self.use_fallback = False
        
        # Norfair settings
        self.distance_function_name = norfair_distance_function
        self.distance_threshold = norfair_distance_threshold
        self.hit_counter_max = norfair_hit_counter_max
        self.initialization_delay = norfair_initialization_delay
        self.past_detections_length = norfair_past_detections_length
        self.norfair_trackers = {}
        self.local_to_global_id = {}
        self.global_id_counter = 1

        # Resolve weights path if relative
        resolved_weights = self._resolve_weights_path(weights)

        # 1. Initialize Norfair Tracker if requested
        if self.tracker_type == "norfair":
            try:
                from norfair import Tracker
                # Eagerly initialize default family tracker to verify Norfair import
                self.norfair_trackers["default"] = Tracker(
                    distance_function=self.distance_function_name,
                    distance_threshold=self.distance_threshold,
                    hit_counter_max=self.hit_counter_max,
                    initialization_delay=self.initialization_delay,
                    past_detections_length=self.past_detections_length
                )
                print(f"[INFO] Initialized Norfair 2D Kalman Tracker (metric={self.distance_function_name}, threshold={self.distance_threshold}, hit_max={self.hit_counter_max}).")
            except Exception as e:
                print(f"[WARNING] Could not initialize Norfair ({e}). Falling back to ByteTrack.")
                self.tracker_type = "bytetrack"

        # 2. Try loading YOLO / YOLO-World model
        try:
            if "world" in str(resolved_weights).lower():
                from ultralytics import YOLOWorld
                print(f"[INFO] Loading YOLO-World Open-Vocabulary Model: {resolved_weights} (device={self.device}, imgsz={img_size})...")
                self.model = YOLOWorld(resolved_weights)
                self.model.set_classes(self.custom_prompts)
                print(f"[INFO] Open-Vocabulary Classes Locked To: {self.custom_prompts}")
            else:
                from ultralytics import YOLO
                print(f"[INFO] Loading YOLO model: {resolved_weights} (device={self.device}, imgsz={img_size})...")
                self.model = YOLO(resolved_weights)
            print("[INFO] Detection model loaded successfully.")
        except Exception as e:
            print(f"[WARNING] Failed to load YOLO model ({e}). Switching to color/contour fail-safe tracker.")
            self.model = None
            self.use_fallback = True

    def _get_family_tracker(self, family: str):
        """Retrieves or creates an isolated Norfair Tracker instance for a specific semantic family."""
        if family not in self.norfair_trackers:
            from norfair import Tracker
            self.norfair_trackers[family] = Tracker(
                distance_function=self.distance_function_name,
                distance_threshold=self.distance_threshold,
                hit_counter_max=self.hit_counter_max,
                initialization_delay=self.initialization_delay,
                past_detections_length=self.past_detections_length
            )
        return self.norfair_trackers[family]

    def _resolve_weights_path(self, path: str) -> str:
        """Resolves weights path relative to current dir, project root, or parent folders."""
        if not path:
            return "yolov8n.pt"
        if os.path.exists(path):
            return path
            
        candidates = [
            os.path.join("weights", os.path.basename(path)),
            os.path.join("Object_permanence", "weights", os.path.basename(path)),
            os.path.join("Object_permanence", "weights", "yolov8x-worldv2.pt"),
            os.path.join("Object_permanence", "weights", "yolov8m-worldv2.pt"),
            os.path.join("Object_permanence", "weights", "yolov8s-worldv2.pt"),
            "yolov8x-worldv2.pt",
            "yolov8m-worldv2.pt",
            "yolov8s-worldv2.pt",
            "yolov8n.pt"
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return path

    def _matches_target_class(self, class_name: str) -> bool:
        """
        Validates detected class against targets.
        If running in universal mode, accepts all valid open-world objects from vocabulary.
        """
        if self.is_universal:
            return True
        c = class_name.lower().strip()
        allowed = [self.target_class.lower()] if self.target_class else [p.lower().strip() for p in self.custom_prompts]

        for tgt in allowed:
            if tgt == c or tgt in c or c in tgt:
                return True
            if tgt == "balloon" and any(k in c for k in ("balloon", "air balloon", "party balloon")):
                return True
            if tgt == "ball" and any(k in c for k in ("ball", "sports ball", "sphere", "baseball", "tennis ball")) and "balloon" not in c:
                return True
            if tgt == "box" and any(k in c for k in ("box", "cardboard", "crate", "cube")):
                return True
        return False

    def _normalize_class_name(self, class_name: str) -> str:
        """Standardizes detected label names into clean semantic canonical forms."""
        c = class_name.lower().strip()
        if "balloon" in c:
            return "balloon"
        if any(k in c for k in ("ball", "sphere", "baseball", "tennis")):
            return "ball"
        if any(k in c for k in ("box", "cardboard", "crate", "cube")):
            return "box"
        if any(k in c for k in ("car", "automobile", "vehicle", "sedan", "suv", "van")):
            return "car"
        if "truck" in c:
            return "truck"
        if "bus" in c:
            return "bus"
        if "motorcycle" in c or "bike" in c:
            return "motorcycle"
        if "pedestrian" in c or "person" in c:
            return "person"
        return class_name

    def _to_norfair_detections(self, xyxy_list, conf_list, cls_list) -> list:
        """Converts raw YOLO bounding boxes into Norfair Detection objects with strict class filtering."""
        from norfair import Detection
        norfair_detections = []
        for i in range(len(xyxy_list)):
            x1, y1, x2, y2 = xyxy_list[i]
            conf = float(conf_list[i])
            cls_id = int(cls_list[i])
            raw_class_name = self.model.names.get(cls_id, f"cls_{cls_id}") if self.model else "object"

            # Reject classes not in target prompts (prevents apple, bed, vase, etc.)
            if not self._matches_target_class(raw_class_name):
                continue

            class_name = self._normalize_class_name(raw_class_name)

            if self.distance_function_name == "iou":
                points = np.array([[float(x1), float(y1)], [float(x2), float(y2)]], dtype=float)
            else:
                cx = float(x1 + (x2 - x1) / 2.0)
                cy = float(y1 + (y2 - y1) / 2.0)
                points = np.array([[cx, cy]], dtype=float)

            norfair_det = Detection(
                points=points,
                scores=np.array([conf, conf] if self.distance_function_name == "iou" else [conf]),
                data={
                    "class_name": class_name,
                    "confidence": conf,
                    "cls_id": cls_id,
                    "bbox": (float(x1), float(y1), float(x2), float(y2))
                }
            )
            norfair_detections.append(norfair_det)

        return norfair_detections

    def process_frame(self, frame: np.ndarray, frame_idx: int) -> list:
        """
        Runs object detection + tracking on a single frame.
        Extracts physical attributes (shape, size, color, aspect ratio) for every entity.
        """
        frame_detections = []

        if not self.use_fallback and self.model is not None:
            try:
                # ----------------- OPTION A: NORFAIR TRACKER -----------------
                if self.tracker_type == "norfair":
                    results = self.model.predict(
                        source=frame,
                        conf=self.conf_threshold,
                        iou=self.iou_threshold,
                        imgsz=self.img_size,
                        device=self.device,
                        agnostic_nms=True,
                        verbose=False
                    )

                    norfair_dets = []
                    if len(results) > 0 and results[0].boxes is not None:
                        boxes = results[0].boxes
                        xyxy_list = boxes.xyxy.cpu().numpy() if boxes.xyxy is not None else []
                        conf_list = boxes.conf.cpu().numpy() if boxes.conf is not None else []
                        cls_list = boxes.cls.cpu().numpy() if boxes.cls is not None else []
                        norfair_dets = self._to_norfair_detections(xyxy_list, conf_list, cls_list)

                    # Group detections by semantic family (people, two_wheelers, small_objects, vehicles, etc.)
                    norfair_dets_by_family = {}
                    for det in norfair_dets:
                        fam = get_class_family(det.data.get("class_name", "object"))
                        if fam not in norfair_dets_by_family:
                            norfair_dets_by_family[fam] = []
                        norfair_dets_by_family[fam].append(det)

                    # Ensure existing family trackers update even if 0 detections in this frame
                    for fam in list(self.norfair_trackers.keys()):
                        if fam not in norfair_dets_by_family and fam != "default":
                            norfair_dets_by_family[fam] = []

                    tracked_objects = []
                    for fam, dets in norfair_dets_by_family.items():
                        tr = self._get_family_tracker(fam)
                        objs = tr.update(detections=dets)
                        for obj in objs:
                            key = (fam, obj.id)
                            if key not in self.local_to_global_id:
                                self.local_to_global_id[key] = self.global_id_counter
                                self.global_id_counter += 1
                            obj.global_id = self.local_to_global_id[key]
                            tracked_objects.append(obj)

                    for obj in tracked_objects:
                        if self.distance_function_name == "iou" and obj.estimate is not None:
                            x1, y1 = float(obj.estimate[0][0]), float(obj.estimate[0][1])
                            x2, y2 = float(obj.estimate[1][0]), float(obj.estimate[1][1])
                        elif obj.last_detection is not None and "bbox" in obj.last_detection.data:
                            x1, y1, x2, y2 = obj.last_detection.data["bbox"]
                        else:
                            continue

                        x1, x2 = min(x1, x2), max(x1, x2)
                        y1, y2 = min(y1, y2), max(y1, y2)
                        width = max(float(x2 - x1), 1.0)
                        height = max(float(y2 - y1), 1.0)
                        center_x = float(x1 + width / 2.0)
                        center_y = float(y1 + height / 2.0)

                        class_name = "object"
                        conf = 0.80
                        if obj.last_detection is not None and obj.last_detection.data:
                            class_name = obj.last_detection.data.get("class_name", "object")
                            conf = float(obj.last_detection.data.get("confidence", 0.80))

                        # Extract rich physical attributes (shape, size, aspect ratio, color)
                        attrs = extract_visual_attributes(frame, (x1, y1, x2, y2), class_name=class_name)

                        det_record = {
                            "frame": frame_idx,
                            "track_id": int(obj.global_id),
                            "class_name": class_name,
                            "confidence": round(conf, 4),
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "x2": round(x2, 2),
                            "y2": round(y2, 2),
                            "center_x": round(center_x, 2),
                            "center_y": round(center_y, 2),
                            "width": attrs["width"],
                            "height": attrs["height"],
                            "area": attrs["area"],
                            "aspect_ratio": attrs["aspect_ratio"],
                            "shape_type": attrs["shape_type"],
                            "color": attrs["color"],
                            "color_hsv": str(attrs["hsv"]),
                            "lab": attrs["lab"],
                            "chroma": attrs["chroma"]
                        }
                        frame_detections.append(det_record)
                        self.detections_history.append(det_record)

                    return frame_detections

                # ----------------- OPTION B: BYTETRACK FALLBACK -----------------
                else:
                    results = self.model.track(
                        source=frame,
                        persist=True,
                        tracker=self.tracker_config,
                        conf=self.conf_threshold,
                        iou=self.iou_threshold,
                        imgsz=self.img_size,
                        device=self.device,
                        verbose=False
                    )

                    if len(results) > 0 and results[0].boxes is not None:
                        boxes = results[0].boxes
                        xyxy_list = boxes.xyxy.cpu().numpy() if boxes.xyxy is not None else []
                        conf_list = boxes.conf.cpu().numpy() if boxes.conf is not None else []
                        cls_list = boxes.cls.cpu().numpy() if boxes.cls is not None else []
                        track_ids = (
                            boxes.id.cpu().numpy().astype(int)
                            if boxes.id is not None
                            else [None] * len(xyxy_list)
                        )

                        for i in range(len(xyxy_list)):
                            x1, y1, x2, y2 = xyxy_list[i]
                            conf = float(conf_list[i])
                            cls_id = int(cls_list[i])
                            raw_class_name = self.model.names.get(cls_id, f"cls_{cls_id}")
                            track_id = int(track_ids[i]) if track_ids[i] is not None else -1

                            if not self._matches_target_class(raw_class_name):
                                continue

                            class_name = self._normalize_class_name(raw_class_name)
                            attrs = extract_visual_attributes(frame, (x1, y1, x2, y2), class_name=class_name)
                            center_x = float(x1 + attrs["width"] / 2.0)
                            center_y = float(y1 + attrs["height"] / 2.0)

                            det_record = {
                                "frame": frame_idx,
                                "track_id": track_id,
                                "class_name": class_name,
                                "confidence": round(conf, 4),
                                "x1": round(float(x1), 2),
                                "y1": round(float(y1), 2),
                                "x2": round(float(x2), 2),
                                "y2": round(float(y2), 2),
                                "center_x": round(center_x, 2),
                                "center_y": round(center_y, 2),
                                "width": attrs["width"],
                                "height": attrs["height"],
                                "area": attrs["area"],
                                "aspect_ratio": attrs["aspect_ratio"],
                                "shape_type": attrs["shape_type"],
                                "color": attrs["color"],
                                "color_hsv": str(attrs["hsv"]),
                                "lab": attrs["lab"],
                                "chroma": attrs["chroma"]
                            }
                            frame_detections.append(det_record)
                            self.detections_history.append(det_record)

                    return frame_detections

            except Exception as ex:
                print(f"[WARNING] Tracking error on frame {frame_idx}: {ex}.")
                return frame_detections

        return frame_detections

    def get_dataframe(self) -> pd.DataFrame:
        if not self.detections_history:
            return pd.DataFrame(columns=[
                "frame", "track_id", "class_name", "confidence",
                "x1", "y1", "x2", "y2", "center_x", "center_y", "width", "height",
                "area", "aspect_ratio", "shape_type", "color", "color_hsv", "lab", "chroma"
            ])
        return pd.DataFrame(self.detections_history)

    def save_to_csv(self, output_csv_path: str):
        df = self.get_dataframe()
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        df.to_csv(output_csv_path, index=False)
        print(f"[INFO] Detections history saved to: {output_csv_path} ({len(df)} records)")
        return output_csv_path
