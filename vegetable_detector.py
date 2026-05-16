"""
Vegetable Detection Module
Uses OpenCV color-based detection to identify vegetables in images.
"""

import cv2
import numpy as np
import os
import gc
import uuid
from PIL import Image


# Vegetable profiles with HSV color ranges and shape characteristics
VEGETABLE_PROFILES = {
    'Tomatoes': {
        'color_ranges': [
            {'lower': np.array([0, 100, 100]), 'upper': np.array([10, 255, 255])},
            {'lower': np.array([170, 100, 100]), 'upper': np.array([180, 255, 255])}
        ],
        'shape': 'round',
        'color_name': 'red',
        'emoji': '🍅',
        'nutrition': {
            'calories': '18 kcal/100g',
            'vitamins': 'Vitamin C, Vitamin A, Potassium',
            'benefits': 'Heart health, skin protection, antioxidant properties'
        }
    },
    'Red Bell Peppers': {
        'color_ranges': [
            {'lower': np.array([0, 80, 80]), 'upper': np.array([10, 255, 255])},
        ],
        'shape': 'irregular',
        'color_name': 'red',
        'emoji': '🫑',
        'nutrition': {
            'calories': '26 kcal/100g',
            'vitamins': 'Vitamin C, Vitamin B6, Vitamin A',
            'benefits': 'Immune support, eye health, anti-inflammatory'
        }
    },
    'Carrots': {
        'color_ranges': [
            {'lower': np.array([10, 100, 100]), 'upper': np.array([25, 255, 255])}
        ],
        'shape': 'elongated',
        'color_name': 'orange',
        'emoji': '🥕',
        'nutrition': {
            'calories': '41 kcal/100g',
            'vitamins': 'Vitamin A, Vitamin K, Biotin',
            'benefits': 'Eye health, immune function, skin health'
        }
    },
    'Cucumbers/Zucchini': {
        'color_ranges': [
            {'lower': np.array([35, 40, 40]), 'upper': np.array([85, 255, 255])}
        ],
        'shape': 'elongated',
        'color_name': 'green',
        'emoji': '🥒',
        'nutrition': {
            'calories': '12 kcal/100g',
            'vitamins': 'Vitamin K, Vitamin C, Potassium',
            'benefits': 'Hydration, digestive health, weight management'
        }
    },
    'Leafy Greens': {
        'color_ranges': [
            {'lower': np.array([35, 30, 30]), 'upper': np.array([90, 255, 255])}
        ],
        'shape': 'irregular',
        'color_name': 'green',
        'emoji': '🥬',
        'nutrition': {
            'calories': '23 kcal/100g',
            'vitamins': 'Vitamin K, Vitamin A, Folate, Iron',
            'benefits': 'Bone health, blood clotting, anemia prevention'
        }
    },
    'Broccoli': {
        'color_ranges': [
            {'lower': np.array([55, 50, 50]), 'upper': np.array([90, 255, 255])}
        ],
        'shape': 'irregular',
        'color_name': 'green',
        'emoji': '🥦',
        'nutrition': {
            'calories': '34 kcal/100g',
            'vitamins': 'Vitamin C, Vitamin K, Folate',
            'benefits': 'Cancer-fighting compounds, bone health, detoxification'
        }
    },
    'Corn': {
        'color_ranges': [
            {'lower': np.array([18, 80, 120]), 'upper': np.array([30, 255, 255])}
        ],
        'shape': 'elongated',
        'color_name': 'yellow',
        'emoji': '🌽',
        'nutrition': {
            'calories': '86 kcal/100g',
            'vitamins': 'Vitamin B, Magnesium, Fiber',
            'benefits': 'Digestive health, energy production, eye health'
        }
    },
    'Eggplant': {
        'color_ranges': [
            {'lower': np.array([100, 30, 30]), 'upper': np.array([140, 255, 255])}
        ],
        'shape': 'irregular',
        'color_name': 'purple',
        'emoji': '🍆',
        'nutrition': {
            'calories': '25 kcal/100g',
            'vitamins': 'Vitamin B6, Vitamin K, Folate',
            'benefits': 'Brain health, heart health, antioxidant properties'
        }
    },
    'Potatoes': {
        'color_ranges': [
            {'lower': np.array([15, 30, 100]), 'upper': np.array([30, 120, 255])}
        ],
        'shape': 'irregular',
        'color_name': 'brown',
        'emoji': '🥔',
        'nutrition': {
            'calories': '77 kcal/100g',
            'vitamins': 'Vitamin C, Vitamin B6, Potassium',
            'benefits': 'Energy, digestion, blood pressure regulation'
        }
    },
    'Onions': {
        'color_ranges': [
            {'lower': np.array([15, 40, 100]), 'upper': np.array([30, 150, 255])}
        ],
        'shape': 'round',
        'color_name': 'yellow',
        'emoji': '🧅',
        'nutrition': {
            'calories': '40 kcal/100g',
            'vitamins': 'Vitamin C, Vitamin B6, Manganese',
            'benefits': 'Anti-inflammatory, heart health, immune support'
        }
    }
}


def analyze_image(image_bytes, output_dir):
    """
    Analyze vegetables in the uploaded image bytes.
    Saves visualization images to output_dir and returns detection results.
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return None, "Could not decode image"

    # Resize large images to save memory (max 600px on longest side)
    max_dim = 600
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    del img
    gc.collect()

    detected_vegetables = []
    saved_masks = []  # Store masks separately for visualization

    for veg_name, profile in VEGETABLE_PROFILES.items():
        combined_mask = np.zeros(img_hsv.shape[:2], dtype=np.uint8)

        for color_range in profile['color_ranges']:
            mask = cv2.inRange(img_hsv, color_range['lower'], color_range['upper'])
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        # Clean up noise
        kernel = np.ones((5, 5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

        percentage = (np.sum(combined_mask > 0) / combined_mask.size) * 100

        if percentage > 1.5:
            contours, _ = cv2.findContours(
                combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            significant_contours = [c for c in contours if cv2.contourArea(c) > 400]

            detected_vegetables.append({
                'name': veg_name,
                'confidence': round(min(percentage * 5, 99.0), 1),
                'coverage': round(percentage, 2),
                'count': len(significant_contours),
                'color': profile['color_name'],
                'emoji': profile['emoji'],
                'nutrition': profile['nutrition'],
            })
            saved_masks.append(combined_mask)
        else:
            del combined_mask

    # Free HSV image
    del img_hsv
    gc.collect()

    # Sort by confidence
    detected_vegetables.sort(key=lambda x: x['confidence'], reverse=True)
    # Reorder saved_masks to match sorted order
    # Since we sorted detected_vegetables, we need to re-sync masks
    # Actually, let's just save files before sorting
    # Re-create: sort both together
    paired = list(zip(detected_vegetables, saved_masks))
    paired.sort(key=lambda x: x[0]['confidence'], reverse=True)
    detected_vegetables = [p[0] for p in paired]
    saved_masks = [p[1] for p in paired]

    # Create overlay visualization
    overlay = img_rgb.copy()
    colors_map = {
        'red': (255, 80, 80),
        'green': (80, 255, 80),
        'orange': (255, 165, 0),
        'yellow': (255, 255, 0),
        'purple': (180, 0, 255),
        'brown': (165, 85, 30)
    }

    for i, det in enumerate(detected_vegetables):
        color = colors_map.get(det['color'], (255, 255, 255))
        mask_colored = np.zeros_like(img_rgb)
        mask_colored[saved_masks[i] > 0] = color
        overlay = cv2.addWeighted(overlay, 1, mask_colored, 0.4, 0)
        del mask_colored

    # Save images to disk and return URLs
    session_id = str(uuid.uuid4())[:8]
    os.makedirs(output_dir, exist_ok=True)

    original_path = os.path.join(output_dir, f'{session_id}_original.jpg')
    overlay_path = os.path.join(output_dir, f'{session_id}_overlay.jpg')

    pil_orig = Image.fromarray(img_rgb)
    pil_orig.save(original_path, 'JPEG', quality=80)
    del pil_orig

    pil_overlay = Image.fromarray(overlay)
    pil_overlay.save(overlay_path, 'JPEG', quality=80)
    del pil_overlay, overlay
    gc.collect()

    # Create mask visualizations for each detected vegetable
    mask_visualizations = []
    for i, (det, mask) in enumerate(zip(detected_vegetables, saved_masks)):
        mask_rgb = np.zeros_like(img_rgb)
        color = colors_map.get(det['color'], (255, 255, 255))
        mask_rgb[mask > 0] = color
        mask_path = os.path.join(output_dir, f'{session_id}_mask_{i}.jpg')
        pil_mask = Image.fromarray(mask_rgb)
        pil_mask.save(mask_path, 'JPEG', quality=80)
        del pil_mask, mask_rgb
        mask_visualizations.append({
            'name': det['name'],
            'mask_url': f'/results/{session_id}_mask_{i}.jpg'
        })

    # Free remaining
    del saved_masks, img_rgb
    gc.collect()

    return {
        'original_url': f'/results/{session_id}_original.jpg',
        'overlay_url': f'/results/{session_id}_overlay.jpg',
        'mask_visualizations': mask_visualizations,
        'detections': detected_vegetables,
        'total_found': len(detected_vegetables)
    }, None
