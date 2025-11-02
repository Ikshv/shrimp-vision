"""
Configuration for multi-class detection in Shrimp Vision
Supports hierarchical tagging: Type + Attributes
"""

# Primary shrimp types
SHRIMP_TYPES = {
    "shrimp": {
        "id": 0,
        "name": "shrimp",
        "display_name": "Shrimp",
        "color": "#10B981",  # Green
        "description": "Regular shrimp"
    },
    "shrimp_juvenile": {
        "id": 1,
        "name": "shrimp_juvenile", 
        "display_name": "Juvenile",
        "color": "#3B82F6",  # Blue
        "description": "Young/small shrimp"
    },
    "shrimp_adult": {
        "id": 2,
        "name": "shrimp_adult",
        "display_name": "Adult",
        "color": "#8B5CF6",  # Purple
        "description": "Mature shrimp"
    },
    "shrimp_egg": {
        "id": 3,
        "name": "shrimp_egg",
        "display_name": "Eggs",
        "color": "#F59E0B",  # Amber
        "description": "Shrimp eggs"
    },
    "shrimp_molt": {
        "id": 4,
        "name": "shrimp_molt",
        "display_name": "Molt",
        "color": "#6B7280",  # Gray
        "description": "Molted shell"
    },
    "shrimp_dead": {
        "id": 5,
        "name": "shrimp_dead",
        "display_name": "Dead",
        "color": "#EF4444",  # Red
        "description": "Dead shrimp"
    }
}

# Color attributes for shrimp
COLOR_ATTRIBUTES = {
    "red": {
        "name": "red",
        "display_name": "Red",
        "color": "#DC2626",
        "description": "Red coloration"
    },
    "blue": {
        "name": "blue",
        "display_name": "Blue",
        "color": "#2563EB",
        "description": "Blue coloration"
    },
    "yellow": {
        "name": "yellow",
        "display_name": "Yellow",
        "color": "#EAB308",
        "description": "Yellow/golden coloration"
    },
    "transparent": {
        "name": "transparent",
        "display_name": "Transparent",
        "color": "#94A3B8",
        "description": "Clear/transparent"
    },
    "black": {
        "name": "black",
        "display_name": "Black",
        "color": "#1F2937",
        "description": "Black/dark coloration"
    },
    "orange": {
        "name": "orange",
        "display_name": "Orange",
        "color": "#EA580C",
        "description": "Orange coloration"
    },
    "white": {
        "name": "white",
        "display_name": "White",
        "color": "#F3F4F6",
        "description": "White/pale coloration"
    },
    "green": {
        "name": "green",
        "display_name": "Green",
        "color": "#16A34A",
        "description": "Green coloration"
    },
    "brown": {
        "name": "brown",
        "display_name": "Brown",
        "color": "#92400E",
        "description": "Brown coloration"
    }
}

# Additional attributes (health, berried status, etc.)
ADDITIONAL_ATTRIBUTES = {
    "berried": {
        "name": "berried",
        "display_name": "Berried",
        "description": "Carrying eggs"
    },
    "healthy": {
        "name": "healthy",
        "display_name": "Healthy",
        "description": "Appears healthy"
    },
    "sick": {
        "name": "sick",
        "display_name": "Sick",
        "description": "Shows signs of illness"
    },
    "male": {
        "name": "male",
        "display_name": "Male",
        "description": "Male shrimp"
    },
    "female": {
        "name": "female",
        "display_name": "Female",
        "description": "Female shrimp"
    }
}

# Backward compatibility: combine into AVAILABLE_CLASSES
AVAILABLE_CLASSES = SHRIMP_TYPES.copy()

# Get class by ID
def get_class_by_id(class_id: int):
    """Get class information by ID"""
    for class_info in AVAILABLE_CLASSES.values():
        if class_info["id"] == class_id:
            return class_info
    return None

# Get class by name
def get_class_by_name(class_name: str):
    """Get class information by name"""
    return AVAILABLE_CLASSES.get(class_name)

# Get all classes as list
def get_all_classes():
    """Get all available classes as a list"""
    return list(AVAILABLE_CLASSES.values())

# Get class names for YOLO training
def get_class_names():
    """Get class names in order for YOLO training"""
    return [class_info["name"] for class_info in sorted(AVAILABLE_CLASSES.values(), key=lambda x: x["id"])]

# Get number of classes
def get_num_classes():
    """Get total number of classes"""
    return len(AVAILABLE_CLASSES)

# Validate class name
def is_valid_class(class_name: str):
    """Check if a class name is valid"""
    return class_name in AVAILABLE_CLASSES

# Get default class (for backward compatibility)
def get_default_class():
    """Get the default class (shrimp)"""
    return AVAILABLE_CLASSES["shrimp"]

# Attribute functions
def get_color_attributes():
    """Get all color attributes"""
    return COLOR_ATTRIBUTES

def get_additional_attributes():
    """Get all additional attributes"""
    return ADDITIONAL_ATTRIBUTES

def is_valid_color(color_name: str):
    """Check if a color name is valid"""
    return color_name in COLOR_ATTRIBUTES

def is_valid_attribute(attribute_name: str):
    """Check if an attribute name is valid"""
    return attribute_name in ADDITIONAL_ATTRIBUTES

def get_all_attributes():
    """Get all attributes (colors + additional)"""
    return {**COLOR_ATTRIBUTES, **ADDITIONAL_ATTRIBUTES}
