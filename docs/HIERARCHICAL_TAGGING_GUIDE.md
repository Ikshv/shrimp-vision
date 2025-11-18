# Hierarchical Multi-Attribute Tagging Guide

## Overview

The Shrimp Vision annotation system now supports **hierarchical tagging** where you can tag each shrimp with:
1. **Type** (e.g., Shrimp, Juvenile, Adult, Eggs, Molt, Dead)
2. **Color** (e.g., Red, Blue, Yellow, Transparent, Black, Orange, White, Green, Brown)
3. **Additional Attributes** (e.g., Berried, Healthy, Sick, Male, Female)

This allows you to create rich, detailed annotations like:
- "Adult Shrimp • Red • Berried"
- "Juvenile • Blue • Healthy"
- "Shrimp • Transparent • Female"

## How to Use

### Step 1: Select Type
Click on the shrimp type button (required):
- **Shrimp** - Regular shrimp
- **Juvenile** - Young/small shrimp
- **Adult** - Mature shrimp
- **Eggs** - Shrimp eggs
- **Molt** - Molted shell
- **Dead** - Dead shrimp

### Step 2: Select Color (Optional)
Click on a color button to tag the shrimp's coloration:
- **Red** - Red coloration
- **Blue** - Blue coloration
- **Yellow** - Yellow/golden coloration
- **Transparent** - Clear/transparent
- **Black** - Black/dark coloration
- **Orange** - Orange coloration
- **White** - White/pale coloration
- **Green** - Green coloration
- **Brown** - Brown coloration
- **None** - Skip color tagging

### Step 3: Select Additional Attributes (Optional)
Click on attribute buttons (can select multiple):
- **Berried** - Carrying eggs
- **Healthy** - Appears healthy
- **Sick** - Shows signs of illness
- **Male** - Male shrimp
- **Female** - Female shrimp

### Step 4: Draw Bounding Box
Draw a bounding box around the shrimp - it will automatically be tagged with all selected attributes!

## Example Workflows

### Workflow 1: Basic Tagging (Type Only)
```
1. Select "Shrimp"
2. Draw bounding box
Result: "Shrimp #1"
```

### Workflow 2: Type + Color
```
1. Select "Adult"
2. Select "Red"
3. Draw bounding box
Result: "Adult #1 • Red"
```

### Workflow 3: Full Tagging
```
1. Select "Shrimp"
2. Select "Blue"
3. Select "Berried" and "Healthy"
4. Draw bounding box
Result: "Shrimp #1 • Blue • Berried, Healthy"
```

## UI Features

### Current Selection Summary
At the bottom of the selector panel, you'll see what you're about to tag:
```
Drawing: Adult • Red • Berried, Healthy
```

### Bounding Box List
Each annotated box shows:
- Type indicator (colored dot)
- Type name and number
- Color badge (if selected)
- Attribute badges (if selected)

Example display:
```
🟣 Adult #1
   Red  Berried  Healthy
```

### Color-Coded Visual Feedback
- Type colors are used for the bounding box border
- Each type has its own distinct color
- Color attributes are shown as badges
- Additional attributes are shown in blue badges

## Data Storage

### Bounding Box JSON Structure
```json
{
  "x": 0.25,
  "y": 0.30,
  "width": 0.15,
  "height": 0.20,
  "label": "shrimp_adult",
  "class_id": 2,
  "color": "red",
  "attributes": ["berried", "healthy"],
  "confidence": 1.0
}
```

### Annotation File Structure
```json
{
  "image_id": "abc123",
  "image_filename": "image.jpg",
  "image_width": 1920,
  "image_height": 1080,
  "bounding_boxes": [
    {
      "x": 0.25,
      "y": 0.30,
      "width": 0.15,
      "height": 0.20,
      "label": "shrimp_adult",
      "class_id": 2,
      "color": "red",
      "attributes": ["berried", "healthy"]
    }
  ],
  "total_shrimp": 1
}
```

## Available Attributes Reference

### Types (Primary Classes)
| ID | Name | Display | Color | Description |
|----|------|---------|-------|-------------|
| 0 | shrimp | Shrimp | Green | Regular shrimp |
| 1 | shrimp_juvenile | Juvenile | Blue | Young/small shrimp |
| 2 | shrimp_adult | Adult | Purple | Mature shrimp |
| 3 | shrimp_egg | Eggs | Amber | Shrimp eggs |
| 4 | shrimp_molt | Molt | Gray | Molted shell |
| 5 | shrimp_dead | Dead | Red | Dead shrimp |

### Colors
| Name | Display | Color Code | Description |
|------|---------|------------|-------------|
| red | Red | #DC2626 | Red coloration |
| blue | Blue | #2563EB | Blue coloration |
| yellow | Yellow | #EAB308 | Yellow/golden |
| transparent | Transparent | #94A3B8 | Clear/transparent |
| black | Black | #1F2937 | Black/dark |
| orange | Orange | #EA580C | Orange coloration |
| white | White | #F3F4F6 | White/pale |
| green | Green | #16A34A | Green coloration |
| brown | Brown | #92400E | Brown coloration |

### Additional Attributes
| Name | Display | Description |
|------|---------|-------------|
| berried | Berried | Carrying eggs |
| healthy | Healthy | Appears healthy |
| sick | Sick | Shows signs of illness |
| male | Male | Male shrimp |
| female | Female | Female shrimp |

## Customization

### Adding New Colors
Edit `backend/config/classes.py`:
```python
COLOR_ATTRIBUTES = {
    "pink": {
        "name": "pink",
        "display_name": "Pink",
        "color": "#EC4899",
        "description": "Pink coloration"
    }
}
```

### Adding New Attributes
Edit `backend/config/classes.py`:
```python
ADDITIONAL_ATTRIBUTES = {
    "juvenile_features": {
        "name": "juvenile_features",
        "display_name": "Juvenile Features",
        "description": "Shows juvenile characteristics"
    }
}
```

### Adding New Types
Edit `backend/config/classes.py`:
```python
SHRIMP_TYPES = {
    "shrimp_breeding": {
        "id": 6,
        "name": "shrimp_breeding",
        "display_name": "Breeding",
        "color": "#F472B6",
        "description": "Shrimp in breeding condition"
    }
}
```

## Training with Multi-Attribute Data

### Current Limitation
YOLO training currently uses only the **primary type** (label) for object detection. Color and additional attributes are stored but not used for training.

### Future Enhancement Options

#### Option 1: Multi-Label Classification
Train separate classifiers for:
- Type detection (current YOLO model)
- Color classification (separate model)
- Attribute classification (separate model)

#### Option 2: Combined Labels
Create combined classes like:
- `shrimp_red_berried` (ID: 100)
- `adult_blue_healthy` (ID: 101)

This would require modifying `dataset_manager.py` to combine attributes into class IDs.

#### Option 3: Attribute Prediction
Add attribute prediction heads to the YOLO model (requires custom model architecture).

## API Endpoints

### Get Available Classes and Attributes
```bash
GET /api/annotate/classes
```

Response:
```json
{
  "success": true,
  "types": { /* shrimp types */ },
  "colors": { /* color attributes */ },
  "attributes": { /* additional attributes */ }
}
```

### Save Annotation with Attributes
```bash
POST /api/annotate/save
```

Body:
```json
{
  "image_id": "abc123",
  "image_filename": "image.jpg",
  "image_width": 1920,
  "image_height": 1080,
  "bounding_boxes": [
    {
      "x": 0.25,
      "y": 0.30,
      "width": 0.15,
      "height": 0.20,
      "label": "shrimp_adult",
      "color": "red",
      "attributes": ["berried", "healthy"]
    }
  ],
  "total_shrimp": 1
}
```

## Tips & Best Practices

### 1. Consistency is Key
- Develop consistent criteria for each attribute
- Document your annotation guidelines
- Review annotations regularly

### 2. Start Simple
- Begin with just types if you're new
- Add colors once comfortable
- Add additional attributes for advanced analysis

### 3. Use Keyboard Shortcuts (Future Enhancement)
Suggested shortcuts:
- `1-6`: Select type
- `R,B,Y,T,etc.`: Select color
- `H,S,M,F`: Toggle attributes

### 4. Batch Similar Annotations
- Annotate all red shrimp together
- Then all blue shrimp
- This reduces mental switching

### 5. Quality Over Quantity
- Accurate attributes are more valuable than many incomplete annotations
- Skip attributes you're uncertain about

## Common Use Cases

### Breeding Programs
Track reproductive health:
- Female + Berried = Ready to breed
- Adult + Healthy = Breeding stock
- Juvenile + Color variants = Selective breeding

### Health Monitoring
Identify sick shrimp:
- Any + Sick = Needs attention
- Dead + Recent = Check water parameters
- Molt + Frequent = Stress indicator

### Color Strain Documentation
Track color genetics:
- Blue + Healthy = Pure blue line
- Red + Yellow = Possible mixed genetics
- Transparent + Adult = Wild type

### Population Analysis
Analyze demographics:
- Count juveniles vs adults
- Track berried females
- Monitor male/female ratio

## Troubleshooting

### Attributes Not Saving
- Check browser console for errors
- Verify backend is running
- Check annotation JSON file format

### Colors Not Displaying
- Refresh browser cache
- Check color hex codes in config
- Verify CSS is loading

### Slow Performance with Many Attributes
- Limit visible bounding boxes
- Use pagination for large datasets
- Consider database storage vs JSON files

## Future Enhancements

### Planned Features
- [ ] Keyboard shortcuts for attributes
- [ ] Attribute search/filter in gallery
- [ ] Bulk attribute editing
- [ ] Attribute statistics dashboard
- [ ] Export with attribute filtering
- [ ] Multi-attribute training support
- [ ] Attribute-based model evaluation
- [ ] Attribute autocomplete suggestions
- [ ] Template presets (e.g., "Common Red Adult")
- [ ] Attribute confidence scores

## Support

For issues or questions about hierarchical tagging:
1. Check annotation JSON format
2. Verify classes.py configuration
3. Test API endpoint `/api/annotate/classes`
4. Review browser console for errors





