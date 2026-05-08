"""
ATAR Calculation Module
==================
Uses Polynomial Regression (degree 4) to model the non-linear relationship
between HSC marks and scaled marks per subject.

Based on real UAC scaling data from hscscalinggraphs.au and matrix.edu.au
"""

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

# Subject scaling data points from hscscalinggraphs.au and matrix.edu.au
# Format: subject_name -> list of (hsc_mark, scaled_mark) pairs
SUBJECT_SCALING_POINTS = {
    "English Advanced": [
        (64, 44), (70, 49), (77, 55), (82, 67), (85, 78), 
        (90, 84), (95, 93), (99, 100)
    ],
    "English Standard": [
        (68, 29), (73, 40), (77, 52), (80, 63), (85, 73), 
        (88, 80), (95, 93), (98, 99)
    ],
    "English Extension 1": [
        (82, 64), (84, 67), (88, 74), (92, 82), (94, 88), 
        (98, 96), (100, 100)
    ],
    "English Extension 2": [
        (76, 64), (83, 73), (90, 81), (92, 81), (95, 85), 
        (96, 88), (98, 96), (100, 100)
    ],
    "Mathematics Extension 2": [
        (75, 83), (85, 89.5), (93, 93.5), (96, 96.5), 
        (99, 99.5), (100, 100)
    ],
    "Mathematics Extension 1": [
        (70, 73), (80, 80), (84, 83), (92, 89.5), 
        (96, 94.5), (99, 99), (100, 100)
    ],
    "Mathematics Advanced": [
        (72, 52), (80, 66.5), (85, 72.5), (89, 78), 
        (94, 86), (96, 95), (100, 100)
    ],
    "Mathematics Standard 2": [
        (64, 30.5), (73, 46.5), (75, 50.5), (81, 63), 
        (82, 63.5), (85, 69.5), (89, 75), (95, 85.5), (98, 94)
    ],
    "Physics": [
        (64, 48), (75, 64), (84, 78), (90, 86), 
        (95, 94.5), (99, 100)
    ],
    "Biology": [
        (66, 36), (75, 53), (84, 70), (88, 80), 
        (95, 90), (99, 100)
    ],
    "Chemistry": [
        (68, 51.5), (75, 68), (80, 74), (84, 79.5), 
        (90, 87), (95, 94.5), (99, 100)
    ],
    "Investigating Science": [
        (68, 23), (76, 40), (85, 58), (89, 71), 
        (94, 85), (98, 93.5)
    ],
    "Earth & Environmental Science": [
        (67, 28), (76, 46.5), (80, 63), (88, 74.5), 
        (90, 85), (95, 86), (99, 96)
    ],
    "Economics": [
        (66, 33), (71, 50), (80, 66), (87, 78), 
        (90, 86), (96, 94), (100, 100)
    ],
    "Business Studies": [
        (66, 30.5), (75, 46.5), (80, 55), (85, 65), 
        (90, 79.5), (96, 91), (99, 100)
    ],
    "Legal Studies": [
        (66, 33), (75, 47), (80, 52), (85, 65), 
        (90, 80), (96, 91), (99, 100)
    ],
    "Geography": [
        (64, 27.5), (68, 33.5), (70, 42), (75, 51), 
        (80, 51), (85, 65.5), (86, 69), (90, 81.5), 
        (95, 94.5), (100, 100)
    ],
    "Modern History": [
        (64, 27.5), (68, 34), (75, 52), (76, 56), 
        (80, 59.5), (85, 67.5), (86, 68.5), (90, 79), 
        (95, 92), (99, 100)
    ],
    "Ancient History": [
        (64, 27.5), (70, 41.5), (75, 45), (80, 56), 
        (85, 62.5), (86, 69), (90, 75), (95, 89), (99, 97)
    ],
    "Studies of Religion I": [
        (70, 41.5), (75, 51.5), (80, 59.5), (85, 62.5), 
        (86, 69.5), (90, 75.5), (95, 80), (97, 88.5), (99, 97)
    ],
    "PDHPE": [
        (67, 28.5), (75, 46), (80, 63), (85, 63.5), 
        (90, 75), (95, 87), (97, 96.5)
    ],
    "Society & Culture": [
        (72, 29.5), (75, 46.5), (80, 46.5), (85, 63), 
        (87, 66.5), (90, 75.5), (95, 89.5), (99, 96.5)
    ],
    "Community & Family Studies": [
        (67, 19.5), (72, 29.5), (75, 36), (80, 53.5), 
        (85, 67), (87, 67.5), (95, 88.5), (99, 93)
    ],
    "Dance": [
        (79, 30.5), (85, 49), (89, 65), (95, 79), 
        (98, 89), (99, 93)
    ],
    "Software Engineering": [
        (69, 38.5), (76, 54.5), (82, 69.5), (89, 81), 
        (96, 94), (99, 100)
    ],
    "Food Technology": [
        (65, 19), (69, 35.5), (74, 35.5), (82, 54.5), 
        (89, 71.5), (95, 86), (98, 91.5)
    ],
    "Engineering Studies": [
        (67, 37.5), (71, 44.5), (75, 53), (80, 67), 
        (90, 79.5), (96, 91.5), (100, 99.5)
    ],
    "Design & Technology": [
        (78, 30), (80, 45.5), (85, 62), (90, 74.5), 
        (95, 90), (99, 95.5)
    ],
    "Industrial Technology": [
        (63, 18.5), (71, 33.5), (79, 51), (85, 65.5), 
        (88, 65.5), (90, 72.5), (95, 79.5), (99, 84.5)
    ]
}

# Cache for trained polynomial models
_POLYNOMIAL_MODELS = {}

def get_polynomial_model(subject_name: str):
    """
    Get or create a polynomial regression model for a subject.
    
    Uses degree 4 for subjects with 8+ data points, degree 3 for others.
    """
    if subject_name in _POLYNOMIAL_MODELS:
        return _POLYNOMIAL_MODELS[subject_name]
    
    if subject_name not in SUBJECT_SCALING_POINTS:
        return None
    
    data_points = SUBJECT_SCALING_POINTS[subject_name]
    
    # Determine polynomial degree based on data availability
    degree = 4 if len(data_points) >= 8 else 3
    
    # Prepare training data
    X = np.array([point[0] for point in data_points]).reshape(-1, 1)
    y = np.array([point[1] for point in data_points])
    
    # Create and train polynomial regression model
    model = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        LinearRegression()
    )
    model.fit(X, y)
    
    # Cache the model
    _POLYNOMIAL_MODELS[subject_name] = model
    return model

def get_scaled_mark(subject_name: str, hsc_mark: float) -> float:
    """
    Convert HSC mark to scaled mark using polynomial regression.
    
    Args:
        subject_name: Subject name matching SUBJECT_SCALING_POINTS keys
        hsc_mark: HSC mark (0-100, or 0-50 for extensions)
    
    Returns:
        Scaled mark (0-100, capped)
    """
    model = get_polynomial_model(subject_name)
    if model is None:
        # Default to no scaling for unknown subjects
        return min(hsc_mark, 100)
    
    # Get the training data range to prevent extrapolation
    if subject_name not in SUBJECT_SCALING_POINTS:
        return min(hsc_mark, 100)
    
    data_points = SUBJECT_SCALING_POINTS[subject_name]
    min_mark = min(point[0] for point in data_points)
    max_mark = max(point[0] for point in data_points)
    
    # If the original mark was below the training range, apply linear scaling
    if hsc_mark < min_mark:
        # Linear interpolation from 0 to the minimum scaled mark
        min_scaled = min(point[1] for point in data_points)
        scaled_mark = (hsc_mark / min_mark) * min_scaled
    else:
        # Clamp the input to the training data range
        clamped_mark = np.clip(hsc_mark, min_mark, max_mark)
        
        # Predict scaled mark
        predicted = model.predict([[clamped_mark]])[0]
        scaled_mark = float(np.clip(predicted, 0, 100))
    
    return scaled_mark

def aggregate_to_atar(aggregate: float) -> float:
    """
    Convert aggregate score to ATAR using linear interpolation.
    
    Based on UAC published conversion table.
    """
    # UAC conversion breakpoints (aggregate, ATAR)
    conversion_points = [
        (500, 99.95), (490, 99.70), (480, 99.50), (470, 99.20),
        (460, 99.00), (450, 98.50), (440, 98.00), (430, 97.00),
        (420, 96.00), (410, 95.00), (400, 93.50), (390, 92.00),
        (380, 90.00), (370, 88.00), (360, 85.00), (350, 82.00),
        (340, 79.00), (330, 76.00), (320, 73.00), (310, 70.00),
        (300, 67.00), (280, 61.00), (260, 55.00), (240, 49.00),
        (220, 43.00), (200, 37.00), (180, 32.00), (160, 27.00),
        (140, 22.00), (120, 17.00), (100, 12.00), (80, 8.00),
        (60, 4.00), (0, 0.00)
    ]
    
    # Handle edge cases
    if aggregate >= 500:
        return 99.95
    if aggregate <= 0:
        return 0.00
    
    # Find the two conversion points to interpolate between
    for i in range(len(conversion_points) - 1):
        lower_agg, lower_atar = conversion_points[i]
        upper_agg, upper_atar = conversion_points[i + 1]
        
        if lower_agg >= aggregate >= upper_agg:
            # Linear interpolation
            ratio = (aggregate - upper_agg) / (lower_agg - upper_agg)
            atar = upper_atar + ratio * (lower_atar - upper_atar)
            return round(atar, 2)
    
    # If we get here, aggregate is between 0 and 60
    ratio = aggregate / 60
    return round(ratio * 4.00, 2)

def calculate_atar_estimate(subjects: list[dict]) -> dict:
    """
    Calculate ATAR estimate from list of subjects with HSC marks.
    
    Args:
        subjects: List of dicts with keys:
            - 'subject_name': str
            - 'hsc_mark': float
            - 'units': int (1 or 2)
    
    Returns:
        Dict with calculation results:
            - 'atar': float
            - 'aggregate': float
            - 'subject_results': list of dicts with scaled marks
    """
    if not subjects:
        return {'atar': 0.0, 'aggregate': 0.0, 'subject_results': []}
    
    # Calculate scaled marks for each subject
    subject_results = []
    for subject in subjects:
        scaled_mark = get_scaled_mark(subject['subject_name'], subject['hsc_mark'])
        subject_results.append({
            'subject_name': subject['subject_name'],
            'hsc_mark': subject['hsc_mark'],
            'scaled_mark': scaled_mark,
            'units': subject['units']
        })
    
    # Sort by scaled mark descending for best 10 units selection
    sorted_results = sorted(subject_results, key=lambda x: x['scaled_mark'], reverse=True)
    
    # Select best 10 units (English mandatory)
    aggregate = 0.0
    units_counted = 0
    english_counted = False
    
    # First, ensure at least 2 units of English are counted
    english_subjects = [s for s in sorted_results if 'English' in s['subject_name']]
    if english_subjects:
        # Take best English result
        best_english = english_subjects[0]
        english_units = min(best_english['units'], 2)
        aggregate += best_english['scaled_mark'] * (english_units / best_english['units'])
        units_counted += english_units
        english_counted = True
        # Remove from list to avoid double-counting
        sorted_results.remove(best_english)
    
    # Count remaining units until we reach 10
    for subject in sorted_results:
        if units_counted >= 10:
            break
        
        units_to_add = min(subject['units'], 10 - units_counted)
        aggregate += subject['scaled_mark'] * (units_to_add / subject['units'])
        units_counted += units_to_add
    
    # Convert aggregate to ATAR
    atar = aggregate_to_atar(aggregate)
    
    return {
        'atar': atar,
        'aggregate': round(aggregate, 1),
        'subject_results': subject_results,
        'units_counted': units_counted,
        'english_counted': english_counted
    }

def get_subject_units(subject_name: str) -> int:
    """
    Get the unit value for a subject.
    
    Returns:
        2 for standard subjects, 1 for most extensions
    """
    extension_subjects = [
        'English Extension 1', 'English Extension 2', 
        'Mathematics Extension 1', 'History Extension', 
        'Music Extension', 'Studies of Religion I'
    ]
    return 1 if subject_name in extension_subjects else 2
