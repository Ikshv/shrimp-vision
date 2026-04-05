"""
Per-dataset YAML manifest: detection class order (YOLO indices) and metadata.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

MANIFEST_FILENAME = "dataset_manifest.yaml"
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _default_detection_classes() -> List[Dict[str, Any]]:
    from config.classes import SHRIMP_TYPES
    return [
        {
            "name": v["name"],
            "display_name": v["display_name"],
            "color": v["color"],
            "description": v.get("description", ""),
        }
        for v in sorted(SHRIMP_TYPES.values(), key=lambda x: x["id"])
    ]


def _default_color_attributes_list() -> List[Dict[str, Any]]:
    from config.classes import COLOR_ATTRIBUTES
    out = []
    for name in sorted(COLOR_ATTRIBUTES.keys()):
        v = COLOR_ATTRIBUTES[name]
        out.append(
            {
                "name": v["name"],
                "display_name": v["display_name"],
                "color": v["color"],
                "description": v.get("description", ""),
            }
        )
    return out


def _default_additional_attributes_list() -> List[Dict[str, Any]]:
    from config.classes import ADDITIONAL_ATTRIBUTES
    out = []
    for name in sorted(ADDITIONAL_ATTRIBUTES.keys()):
        v = ADDITIONAL_ATTRIBUTES[name]
        out.append(
            {
                "name": v["name"],
                "display_name": v["display_name"],
                "description": v.get("description", ""),
            }
        )
    return out


def manifest_path(dataset_root: str) -> Path:
    return Path(dataset_root) / MANIFEST_FILENAME


def load_manifest(dataset_root: str) -> Dict[str, Any]:
    path = manifest_path(dataset_root)
    if not path.exists():
        data = {
            "schema_version": 1,
            "detection_classes": _default_detection_classes(),
            "color_attributes": _default_color_attributes_list(),
            "additional_attributes": _default_additional_attributes_list(),
        }
        save_manifest(dataset_root, data)
        return data
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "schema_version" not in data:
        data["schema_version"] = 1
    classes = data.get("detection_classes")
    if not classes:
        data["detection_classes"] = _default_detection_classes()
        save_manifest(dataset_root, data)
    migrated = False
    if "color_attributes" not in data or data["color_attributes"] is None:
        data["color_attributes"] = _default_color_attributes_list()
        migrated = True
    if "additional_attributes" not in data or data["additional_attributes"] is None:
        data["additional_attributes"] = _default_additional_attributes_list()
        migrated = True
    if migrated:
        save_manifest(dataset_root, data)
    return data


def save_manifest(dataset_root: str, data: Dict[str, Any]) -> None:
    path = manifest_path(dataset_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = {
        "schema_version": data.get("schema_version", 1),
        "detection_classes": data.get("detection_classes", []),
        "color_attributes": data.get("color_attributes", []),
        "additional_attributes": data.get("additional_attributes", []),
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(out, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def color_attributes_as_map(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        name = r["name"]
        out[name] = {
            "name": name,
            "display_name": r.get("display_name") or name,
            "color": r.get("color") or "#6B7280",
            "description": r.get("description") or "",
        }
    return out


def additional_attributes_as_map(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        name = r["name"]
        out[name] = {
            "name": name,
            "display_name": r.get("display_name") or name,
            "description": r.get("description") or "",
        }
    return out


def colors_for_annotate(dataset_root: Optional[str]) -> Dict[str, Dict[str, Any]]:
    if not dataset_root:
        from config.classes import COLOR_ATTRIBUTES
        return {k: dict(v) for k, v in COLOR_ATTRIBUTES.items()}
    m = load_manifest(dataset_root)
    return color_attributes_as_map(m.get("color_attributes", []))


def additional_for_annotate(dataset_root: Optional[str]) -> Dict[str, Dict[str, Any]]:
    if not dataset_root:
        from config.classes import ADDITIONAL_ATTRIBUTES
        return {k: dict(v) for k, v in ADDITIONAL_ATTRIBUTES.items()}
    m = load_manifest(dataset_root)
    return additional_attributes_as_map(m.get("additional_attributes", []))


def is_valid_color_attr(dataset_root: Optional[str], color: Optional[str]) -> bool:
    if not color:
        return True
    return color in colors_for_annotate(dataset_root)


def is_valid_additional_attr(dataset_root: Optional[str], attr: str) -> bool:
    return attr in additional_for_annotate(dataset_root)


def validate_color_attributes_list(rows: List[Dict[str, Any]]) -> Tuple[bool, str]:
    seen: Set[str] = set()
    for c in rows:
        n = (c.get("name") or "").strip()
        if not n or not _NAME_RE.match(n):
            return False, f"Invalid color attribute name '{c.get('name')}'"
        if n in seen:
            return False, f"Duplicate color attribute: {n}"
        seen.add(n)
    return True, ""


def validate_additional_attributes_list(rows: List[Dict[str, Any]]) -> Tuple[bool, str]:
    seen: Set[str] = set()
    for c in rows:
        n = (c.get("name") or "").strip()
        if not n or not _NAME_RE.match(n):
            return False, f"Invalid additional attribute name '{c.get('name')}'"
        if n in seen:
            return False, f"Duplicate additional attribute: {n}"
        seen.add(n)
    return True, ""


def normalize_color_attribute_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for r in rows:
        name = (r.get("name") or "").strip()
        disp = (r.get("display_name") or "").strip() or name
        color = (r.get("color") or "#6B7280").strip()
        desc = (r.get("description") or "").strip()
        normalized.append(
            {"name": name, "display_name": disp, "color": color, "description": desc}
        )
    return normalized


def normalize_additional_attribute_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for r in rows:
        name = (r.get("name") or "").strip()
        disp = (r.get("display_name") or "").strip() or name
        desc = (r.get("description") or "").strip()
        normalized.append({"name": name, "display_name": disp, "description": desc})
    return normalized


def scrub_annotation_attributes(
    annotation_dir: str,
    valid_colors: Set[str],
    valid_additional: Set[str],
) -> None:
    if not os.path.isdir(annotation_dir):
        return
    for fn in os.listdir(annotation_dir):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(annotation_dir, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        boxes = data.get("bounding_boxes", [])
        dirty = False
        for box in boxes:
            c = box.get("color")
            if c and c not in valid_colors:
                box["color"] = None
                dirty = True
            attrs = box.get("attributes") or []
            new_attrs = [a for a in attrs if a in valid_additional]
            if new_attrs != attrs:
                box["attributes"] = new_attrs
                dirty = True
        if dirty:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)


def detection_classes_as_types(detection_classes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Shape expected by annotate UI: keyed by slug name."""
    out: Dict[str, Dict[str, Any]] = {}
    for i, c in enumerate(detection_classes):
        name = c["name"]
        out[name] = {
            "id": i,
            "name": name,
            "display_name": c.get("display_name") or name,
            "color": c.get("color") or "#6B7280",
            "description": c.get("description") or "",
        }
    return out


def validate_detection_classes(classes: List[Dict[str, Any]]) -> Tuple[bool, str]:
    if not classes:
        return False, "At least one detection class is required"
    seen: Set[str] = set()
    for c in classes:
        n = (c.get("name") or "").strip()
        if not n or not _NAME_RE.match(n):
            return (
                False,
                f"Invalid class name '{c.get('name')}': use lowercase, start with a letter, "
                "then letters/digits/underscores only",
            )
        if n in seen:
            return False, f"Duplicate class name: {n}"
        seen.add(n)
    return True, ""


def yolo_names_from_manifest(dataset_root: Optional[str]) -> List[str]:
    if not dataset_root:
        from config.classes import get_class_names
        return get_class_names()
    m = load_manifest(dataset_root)
    return [c["name"] for c in m["detection_classes"]]


def yolo_num_classes(dataset_root: Optional[str]) -> int:
    return len(yolo_names_from_manifest(dataset_root))


TrainingSignature = Tuple[str, Optional[str], Tuple[str, ...]]


def bbox_training_signature(bbox: Dict[str, Any]) -> TrainingSignature:
    """Stable tuple for grouping a box into a YOLO class (type + optional color + optional tags)."""
    label = (bbox.get("label") or "shrimp").strip()
    color = bbox.get("color")
    if color is not None:
        color = str(color).strip() or None
    attrs = tuple(
        sorted({str(a).strip() for a in (bbox.get("attributes") or []) if a and str(a).strip()})
    )
    return (label, color, attrs)


def slug_from_training_signature(sig: TrainingSignature) -> str:
    label, color, attrs = sig
    parts: List[str] = [label]
    if color:
        parts.append(f"c_{color}")
    if attrs:
        parts.append("a_" + "::".join(attrs))
    return "__".join(parts)


def build_yolo_composite_labels(
    annotated_images: List[Dict[str, Any]],
    dataset_root: Optional[str],
) -> Tuple[List[str], Dict[TrainingSignature, int]]:
    """
    Build YOLO class names and index map from all bounding boxes.
    Color tags and additional attributes (e.g. shiny) become part of the class slug so the
    detector can learn to distinguish them (single-label per box).
    """
    unique: Set[TrainingSignature] = set()
    for item in annotated_images:
        data = item.get("annotation_data") or {}
        for bbox in data.get("bounding_boxes", []):
            unique.add(bbox_training_signature(bbox))

    manifest_names = yolo_names_from_manifest(dataset_root)

    if not unique:
        names = list(manifest_names)
        mapping = {(n, None, ()): i for i, n in enumerate(names)}
        return names, mapping

    def sig_key(sig: TrainingSignature):
        label, color, attrs = sig
        try:
            li = manifest_names.index(label)
        except ValueError:
            li = 999
        return (li, label, color or "", attrs)

    sorted_sigs = sorted(unique, key=sig_key)
    slugs = [slug_from_training_signature(s) for s in sorted_sigs]
    mapping = {s: i for i, s in enumerate(sorted_sigs)}
    return slugs, mapping


def parse_composite_yolo_slug(slug: str) -> Dict[str, Any]:
    """Parse training slug back into type, color tag, and additional attributes (for inference UI)."""
    if not slug or "__" not in slug:
        return {"base_label": slug, "color": None, "attributes": []}
    parts = slug.split("__")
    base = parts[0]
    color: Optional[str] = None
    attributes: List[str] = []
    for p in parts[1:]:
        if p.startswith("c_"):
            color = p[2:] or None
        elif p.startswith("a_"):
            rest = p[2:]
            attributes = [x for x in rest.split("::") if x] if rest else []
    return {"base_label": base, "color": color, "attributes": attributes}


def types_for_annotate(dataset_root: Optional[str]) -> Dict[str, Dict[str, Any]]:
    if not dataset_root:
        from config.classes import SHRIMP_TYPES
        return {k: dict(v) for k, v in SHRIMP_TYPES.items()}
    m = load_manifest(dataset_root)
    return detection_classes_as_types(m["detection_classes"])


def is_valid_label(dataset_root: Optional[str], label: str) -> bool:
    types = types_for_annotate(dataset_root)
    return label in types


def get_class_by_name_for_dataset(dataset_root: Optional[str], class_name: str) -> Optional[Dict[str, Any]]:
    types = types_for_annotate(dataset_root)
    return types.get(class_name)


def _collect_removed_names(old_names: List[str], new_names: List[str]) -> Set[str]:
    return set(old_names) - set(new_names)


def _labels_used_in_annotations(annotation_dir: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    if not os.path.isdir(annotation_dir):
        return counts
    for fn in os.listdir(annotation_dir):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(annotation_dir, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for box in data.get("bounding_boxes", []):
            lab = box.get("label")
            if lab:
                counts[lab] = counts.get(lab, 0) + 1
    return counts


def validate_classes_update(
    dataset_root: str,
    new_classes: List[Dict[str, Any]],
    annotation_dir: str,
) -> Tuple[bool, str]:
    ok, err = validate_detection_classes(new_classes)
    if not ok:
        return False, err
    old = load_manifest(dataset_root)
    old_names = [c["name"] for c in old.get("detection_classes", [])]
    new_names = [c["name"] for c in new_classes]
    removed = _collect_removed_names(old_names, new_names)
    if not removed:
        return True, ""
    usage = _labels_used_in_annotations(annotation_dir)
    for name in removed:
        if usage.get(name, 0) > 0:
            return (
                False,
                f"Cannot remove class '{name}': it is used on {usage[name]} bounding box(es). "
                "Edit or delete those annotations first.",
            )
    return True, ""


def remap_and_save_annotations(annotation_dir: str, detection_classes: List[Dict[str, Any]]) -> None:
    name_to_idx = {c["name"]: i for i, c in enumerate(detection_classes)}
    if not os.path.isdir(annotation_dir):
        return
    for fn in os.listdir(annotation_dir):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(annotation_dir, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        boxes = data.get("bounding_boxes", [])
        dirty = False
        for box in boxes:
            lab = box.get("label")
            if lab not in name_to_idx:
                raise ValueError(
                    f"{fn}: unknown label '{lab}'. Add that class back or fix the annotation."
                )
            new_id = name_to_idx[lab]
            if box.get("class_id") != new_id:
                box["class_id"] = new_id
                dirty = True
        if dirty:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)


def normalize_detection_class_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for r in rows:
        name = (r.get("name") or "").strip()
        disp = (r.get("display_name") or "").strip() or name
        color = (r.get("color") or "#6B7280").strip()
        desc = (r.get("description") or "").strip()
        normalized.append(
            {"name": name, "display_name": disp, "color": color, "description": desc}
        )
    return normalized


def apply_manifest_labels_update(
    dataset_root: str,
    new_classes: List[Dict[str, Any]],
    new_colors: List[Dict[str, Any]],
    new_additional: List[Dict[str, Any]],
    annotation_dir: str,
) -> None:
    """
    Remap detection class_id, scrub stale color/tags, persist full manifest.
    """
    ok, err = validate_classes_update(dataset_root, new_classes, annotation_dir)
    if not ok:
        raise ValueError(err)
    ok, err = validate_color_attributes_list(new_colors)
    if not ok:
        raise ValueError(err)
    ok, err = validate_additional_attributes_list(new_additional)
    if not ok:
        raise ValueError(err)
    remap_and_save_annotations(annotation_dir, new_classes)
    valid_color_names = {r["name"] for r in new_colors}
    valid_add_names = {r["name"] for r in new_additional}
    scrub_annotation_attributes(annotation_dir, valid_color_names, valid_add_names)
    data = load_manifest(dataset_root)
    data["detection_classes"] = new_classes
    data["color_attributes"] = new_colors
    data["additional_attributes"] = new_additional
    save_manifest(dataset_root, data)


def apply_classes_update(
    dataset_root: str,
    new_classes: List[Dict[str, Any]],
    annotation_dir: str,
) -> None:
    """Backward-compatible: only updates detection classes; keeps current attribute defs."""
    m = load_manifest(dataset_root)
    apply_manifest_labels_update(
        dataset_root,
        new_classes,
        m.get("color_attributes") or _default_color_attributes_list(),
        m.get("additional_attributes") or _default_additional_attributes_list(),
        annotation_dir,
    )
