import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

# New comprehensive ATAR scaling data from NEW_ATAR_CALC.md
SUBJECT_SCALING_POINTS = {
    # English subjects
    "English Advanced": [
        (64, 44), (70, 49), (77, 55), (82, 67), (85, 78), (90, 84), (95, 93), (99, 100)
    ],
    "English Standard": [
        (68, 29), (73, 40), (77, 52), (80, 63), (85, 73), (88, 80), (95, 93), (98, 99)
    ],
    "English Extension 1": [
        (82, 64), (84, 67), (88, 74), (92, 82), (94, 88), (98, 96), (100, 100)
    ],
    "English Extension 2": [
        (76, 64), (83, 73), (90, 81), (92, 81), (95, 85), (96, 88), (98, 96), (100, 100)
    ],
    
    # Mathematics subjects
    "Mathematics Extension 2": [
        (75, 83), (85, 89.5), (93, 93.5), (96, 96.5), (99, 99.5), (100, 100)
    ],
    "Mathematics Extension 1": [
        (70, 73), (80, 80), (84, 83), (92, 89.5), (96, 94.5), (99, 99), (100, 100)
    ],
    "Mathematics Advanced": [
        (72, 52), (80, 66.5), (85, 72.5), (89, 78), (94, 86), (96, 95), (100, 100)
    ],
    "General Maths": [
        (84, 84.15), (90, 91.75), (95, 95.25), (98, 94), (100, 100)
    ],
    "Maths Standard 2": [
        (64, 30.5), (73, 46.5), (75, 50.5), (81, 63), (82, 63.5), (85, 69.5), (89, 75), (95, 85.5), (98, 94)
    ],
    
    # Science subjects
    "Physics": [
        (64, 48), (75, 64), (84, 78), (90, 86), (95, 94.5), (99, 100)
    ],
    "Biology": [
        (66, 36), (75, 53), (84, 70), (88, 80), (95, 90), (99, 100)
    ],
    "Chemistry": [
        (68, 51.5), (75, 68), (80, 74), (84, 79.5), (90, 87), (95, 94.5), (99, 100)
    ],
    "Investigating Science": [
        (68, 23), (76, 40), (85, 58), (89, 71), (94, 85), (98, 93.5)
    ],
    "Earth & Environmental Science": [
        (67, 28), (76, 46.5), (80, 63), (88, 74.5), (90, 85), (95, 86), (99, 96)
    ],
    "Senior Science": [
        (20, 6.5)  # Only low-end anchor point available
    ],
    
    # Humanities and Social Sciences
    "Business Studies": [
        (66, 30.5), (71, 46.5), (80, 55), (85, 65), (90, 79.5), (96, 91), (99, 100)
    ],
    "Economics": [
        (66, 33), (71, 50), (80, 66), (87, 78), (90, 86), (96, 94), (100, 100)
    ],
    "Legal Studies": [
        (66, 33), (75, 47), (80, 52), (85, 65), (90, 80), (96, 91), (99, 100)
    ],
    "Geography": [
        (64, 27.5), (68, 33.5), (70, 42), (75, 51), (80, 51), (85, 65.5), (86, 69), (90, 81.5), (95, 94.5), (100, 100)
    ],
    "Modern History": [
        (64, 27.5), (68, 34), (75, 52), (76, 56), (80, 59.5), (85, 67.5), (86, 68.5), (90, 79), (95, 92), (99, 100)
    ],
    "Ancient History": [
        (64, 27.5), (70, 41.5), (75, 45), (80, 56), (85, 62.5), (86, 69), (90, 75), (95, 89), (99, 97)
    ],
    "Studies of Religion I": [
        (70, 41.5), (75, 51.5), (80, 59.5), (85, 62.5), (86, 69.5), (90, 75.5), (95, 80), (97, 88.5), (99, 97)
    ],
    "Studies of Religion II": [
        (20, 11.9)  # Only low-end anchor point available
    ],
    "PDHPE": [
        (67, 28.5), (75, 46), (80, 63), (85, 63.5), (90, 75), (95, 87), (97, 96.5), (99, 100)
    ],
    "Society & Culture": [
        (72, 29.5), (75, 46.5), (80, 46.5), (85, 63), (87, 67.5), (90, 75.5), (95, 89.5), (99, 96.5), (100, 100)
    ],
    
    # Arts and Technologies
    "Drama": [
        (75, 9.1), (85, 49), (89, 65), (95, 79), (98, 89), (99, 93)
    ],
    "Music 1": [
        (75, 28), (85, 49), (89, 65), (95, 79), (98, 89), (99, 93)
    ],
    "Music 2": [
        (75, 51.4), (85, 67), (90, 75.5), (95, 89.5), (98, 96), (99, 100)
    ],
    "Music Extension": [
        (75, 50.6), (85, 67), (90, 75.5), (95, 89.5), (98, 96), (99, 100)
    ],
    "Visual Arts": [
        (75, 30.7), (85, 62.5), (90, 75.5), (95, 89.5), (98, 96), (99, 100)
    ],
    "Community & Family Studies": [
        (67, 19.5), (72, 29.5), (75, 36), (80, 53.5), (85, 67), (87, 67.5), (95, 88.5), (99, 93), (100, 100)
    ],
    "Dance": [
        (79, 30.5), (85, 49), (89, 65), (95, 79), (98, 89), (99, 93)
    ],
    "Software Design & Development": [
        (69, 38.5), (76, 54.5), (82, 69.5), (89, 81), (96, 94), (99, 100)
    ],
    "Textiles & Design": [
        (65, 19), (69, 35.5), (74, 35.5), (82, 54.5), (89, 71.5), (95, 86), (98, 91.5), (99, 100)
    ],
    "Engineering Studies": [
        (67, 37.5), (71, 44.5), (75, 53), (80, 67), (90, 79.5), (96, 91.5), (100, 99.5)
    ],
    "Industrial Technology": [
        (63, 18.5), (71, 33.5), (79, 51), (85, 65.5), (88, 65.5), (90, 72.5), (95, 79.5), (99, 84.5), (100, 100)
    ],
    "Food Technology": [
        (65, 19), (69, 35.5), (74, 35.5), (82, 54.5), (89, 71.5), (95, 86), (98, 91.5), (99, 100)
    ],
    "Design & Technology": [
        (78, 30), (80, 45.5), (85, 62), (90, 74.5), (95, 90), (99, 95.5), (100, 100)
    ],
    "ESL": [
        (20, 7.6)  # Only low-end anchor point available
    ]
}

# Cache for polynomial models to avoid retraining
_POLYNOMIAL_MODELS = {}

def get_polynomial_model(subject_name: str):
    """
    Get or create a polynomial regression model for a subject.
    
    Args:
        subject_name: Subject name matching SUBJECT_SCALING_POINTS keys
        
    Returns:
        Trained polynomial model or None if subject not found
    """
    if subject_name not in SUBJECT_SCALING_POINTS:
        return None
    
    # Return cached model if already created
    if subject_name in _POLYNOMIAL_MODELS:
        return _POLYNOMIAL_MODELS[subject_name]
    
    # Get scaling data for this subject
    data_points = SUBJECT_SCALING_POINTS[subject_name]
    
    # Determine polynomial degree based on data availability
    if len(data_points) >= 8:
        degree = 4  # Use degree 4 for subjects with good data coverage
    else:
        degree = 2  # Use degree 2 for subjects with limited data to avoid overfitting
    
    # Create polynomial features and fit model
    X = np.array([point[0] for point in data_points]).reshape(-1, 1)
    y = np.array([point[1] for point in data_points])
    
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
        return float(np.clip(scaled_mark, 0, 100))
    
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
    
    # Sort points by aggregate score
    conversion_points.sort()
    
    # Find the appropriate range and interpolate
    for i in range(len(conversion_points) - 1):
        if aggregate >= conversion_points[i][0] and aggregate <= conversion_points[i + 1][0]:
            # Linear interpolation between two points
            x1, y1 = conversion_points[i]
            x2, y2 = conversion_points[i + 1]
            
            atar = y1 + (aggregate - x1) * (y2 - y1) / (x2 - x1)
            return max(0, min(99.95, atar))  # Cap at 99.95
    
    # If aggregate is below minimum or above maximum, return nearest value
    if aggregate < conversion_points[0][0]:
        return 0.0
    elif aggregate > conversion_points[-1][0]:
        return 99.95
    else:
        return conversion_points[-1][1]

def calculate_atar_estimate(subjects: list[dict]) -> dict:
    """
    Calculate ATAR estimate from list of subjects with HSC marks.
    
    Args:
        subjects: List of dictionaries with 'subject_name', 'hsc_mark', and 'units'
        
    Returns:
        Dictionary with ATAR calculation results
    """
    if not subjects:
        return {
            'atar': 0.0,
            'aggregate': 0.0,
            'subject_results': [],
            'units_counted': 0,
            'english_counted': False
        }
    
    # Calculate scaled marks for each subject
    subject_results = []
    for subject in subjects:
        subject_name = subject['subject_name']
        hsc_mark = subject['hsc_mark']
        units = subject.get('units', 2)
        
        scaled_mark = get_scaled_mark(subject_name, hsc_mark)
        
        subject_results.append({
            'subject_name': subject_name,
            'hsc_mark': hsc_mark,
            'scaled_mark': scaled_mark,
            'units': units
        })
    
    # Sort subjects by scaled mark (descending) for best units selection
    subject_results.sort(key=lambda x: x['scaled_mark'], reverse=True)
    
    # Select best units (mandatory English + best remaining)
    selected_units = []
    english_counted = False
    aggregate_score = 0.0
    units_counted = 0
    
    # First, include best English subject (mandatory)
    english_subjects = [s for s in subject_results if 'English' in s['subject_name']]
    if english_subjects:
        best_english = max(english_subjects, key=lambda x: x['scaled_mark'])
        selected_units.append(best_english)
        aggregate_score += best_english['scaled_mark'] * best_english['units']
        units_counted += best_english['units']
        english_counted = True
        
        # Remove used English subject from list
        subject_results = [s for s in subject_results if s != best_english]
    
    # Then add best remaining units until we reach 10 units total
    for subject in subject_results:
        if units_counted >= 10:
            break
        
        # Check if adding this subject would exceed 10 units
        if units_counted + subject['units'] <= 10:
            selected_units.append(subject)
            aggregate_score += subject['scaled_mark'] * subject['units']
            units_counted += subject['units']
    
    # Convert aggregate to ATAR
    atar_score = aggregate_to_atar(aggregate_score)
    
    return {
        'atar': round(atar_score, 2),
        'aggregate': round(aggregate_score, 1),
        'subject_results': selected_units,
        'units_counted': units_counted,
        'english_counted': english_counted
    }
