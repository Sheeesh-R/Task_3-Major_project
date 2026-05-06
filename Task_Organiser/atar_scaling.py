# ATAR Scaling Data for HSC Study Planner
# Source: UAC Historical Scaling Reports
# Polynomial coefficients mapping raw HSC mark -> scaled mark (approx)

SCALING_DATA = {
    "English Advanced": {
        "units": 2,
        "scale_factor": 1.0,
        "coefficients": [0.001, 0.95, 2.5]  # for np.polyval
    },
    "English Standard": {
        "units": 2,
        "scale_factor": 0.9,
        "coefficients": [0.0008, 0.88, 3.2]
    },
    "Mathematics Advanced": {
        "units": 2,
        "scale_factor": 1.15,
        "coefficients": [0.0012, 0.92, 4.1]
    },
    "Mathematics Extension 1": {
        "units": 1,
        "scale_factor": 1.25,
        "coefficients": [0.0015, 0.90, 5.2]
    },
    "Mathematics Extension 2": {
        "units": 2,
        "scale_factor": 1.18,
        "coefficients": [0.0003, 0.85, 8.2]
    },
    "Physics": {
        "units": 2,
        "scale_factor": 1.12,
        "coefficients": [0.001, 0.89, 4.5]
    },
    "Chemistry": {
        "units": 2,
        "scale_factor": 1.10,
        "coefficients": [0.0009, 0.87, 4.3]
    },
    "Biology": {
        "units": 2,
        "scale_factor": 1.05,
        "coefficients": [0.0007, 0.85, 3.8]
    },
    "Modern History": {
        "units": 2,
        "scale_factor": 1.03,
        "coefficients": [0.0006, 0.84, 3.5]
    },
    "Ancient History": {
        "units": 2,
        "scale_factor": 1.02,
        "coefficients": [0.0005, 0.83, 3.3]
    },
    "Economics": {
        "units": 2,
        "scale_factor": 1.08,
        "coefficients": [0.0008, 0.86, 4.0]
    },
    "Business Studies": {
        "units": 2,
        "scale_factor": 1.04,
        "coefficients": [0.0006, 0.84, 3.6]
    },
    "Legal Studies": {
        "units": 2,
        "scale_factor": 1.06,
        "coefficients": [0.0007, 0.85, 3.9]
    },
    "Visual Arts": {
        "units": 2,
        "scale_factor": 0.95,
        "coefficients": [0.0004, 0.82, 2.8]
    },
    "Music": {
        "units": 2,
        "scale_factor": 0.98,
        "coefficients": [0.0005, 0.83, 3.0]
    },
    "Drama": {
        "units": 2,
        "scale_factor": 0.96,
        "coefficients": [0.0004, 0.82, 2.9]
    },
    "Personal Development, Health and Physical Education": {
        "units": 2,
        "scale_factor": 0.92,
        "coefficients": [0.0003, 0.80, 2.6]
    },
    "Studies of Religion I": {
        "units": 1,
        "scale_factor": 0.94,
        "coefficients": [0.0004, 0.81, 2.7]
    },
    "Studies of Religion II": {
        "units": 2,
        "scale_factor": 0.94,
        "coefficients": [0.0004, 0.81, 2.7]
    }
}

def get_scaled_mark(subject_name, raw_mark):
    """
    Convert raw HSC mark to scaled mark using polynomial coefficients
    """
    if subject_name not in SCALING_DATA:
        return raw_mark  # Return raw mark if subject not found
    
    scaling_info = SCALING_DATA[subject_name]
    coefficients = scaling_info["coefficients"]
    
    # Apply polynomial scaling: a*x^2 + b*x + c
    # where x is raw_mark and coefficients are [a, b, c]
    scaled_mark = (coefficients[0] * raw_mark ** 2 + 
                   coefficients[1] * raw_mark + 
                   coefficients[2])
    
    # Ensure scaled mark doesn't exceed 100
    return min(scaled_mark, 100.0)

def get_subject_units(subject_name):
    """
    Get the unit count for a subject
    """
    if subject_name not in SCALING_DATA:
        return 2  # Default to 2 units
    return SCALING_DATA[subject_name]["units"]

def get_scale_factor(subject_name):
    """
    Get the scale factor for a subject
    """
    if subject_name not in SCALING_DATA:
        return 1.0  # Default no scaling
    return SCALING_DATA[subject_name]["scale_factor"]

def calculate_atar_aggregate(subjects_data):
    """
    Calculate the ATAR aggregate from subject data
    subjects_data: list of dicts with 'name', 'raw_mark', 'units'
    Returns: aggregate score (out of 500)
    """
    total_units = 0
    total_scaled_marks = 0
    
    for subject in subjects_data:
        subject_name = subject['name']
        raw_mark = subject['raw_mark']
        units = subject.get('units', get_subject_units(subject_name))
        
        # Get scaled mark
        scaled_mark = get_scaled_mark(subject_name, raw_mark)
        
        # Add to total (scaled marks are per unit)
        total_scaled_marks += scaled_mark * units
        total_units += units
    
    # ATAR aggregate is based on best 10 units (including at least 2 units of English)
    # For simplicity, we'll assume all provided subjects are counted
    # Maximum aggregate is 500 (10 units × 50 marks per unit)
    if total_units > 10:
        # If more than 10 units, we'd need to select the best performing ones
        # For now, we'll scale down proportionally
        scaling_factor = 10 / total_units
        total_scaled_marks *= scaling_factor
        total_units = 10
    
    # Convert to ATAR aggregate (scaled marks are out of 100, ATAR uses 50 per unit)
    aggregate = (total_scaled_marks / 100) * 50
    
    return min(aggregate, 500)  # Cap at maximum

def aggregate_to_atar(aggregate):
    """
    Convert ATAR aggregate to ATAR score
    Uses simplified conversion table based on UAC data
    """
    # Simplified ATAR conversion (approximate)
    if aggregate >= 480:
        return 99.95
    elif aggregate >= 470:
        return 99.50
    elif aggregate >= 460:
        return 99.00
    elif aggregate >= 450:
        return 98.50
    elif aggregate >= 440:
        return 98.00
    elif aggregate >= 430:
        return 97.50
    elif aggregate >= 420:
        return 97.00
    elif aggregate >= 410:
        return 96.50
    elif aggregate >= 400:
        return 96.00
    elif aggregate >= 390:
        return 95.50
    elif aggregate >= 380:
        return 95.00
    elif aggregate >= 370:
        return 94.50
    elif aggregate >= 360:
        return 94.00
    elif aggregate >= 350:
        return 93.50
    elif aggregate >= 340:
        return 93.00
    elif aggregate >= 330:
        return 92.50
    elif aggregate >= 320:
        return 92.00
    elif aggregate >= 310:
        return 91.50
    elif aggregate >= 300:
        return 91.00
    elif aggregate >= 290:
        return 90.50
    elif aggregate >= 280:
        return 90.00
    elif aggregate >= 270:
        return 89.50
    elif aggregate >= 260:
        return 89.00
    elif aggregate >= 250:
        return 88.50
    elif aggregate >= 240:
        return 88.00
    elif aggregate >= 230:
        return 87.50
    elif aggregate >= 220:
        return 87.00
    elif aggregate >= 210:
        return 86.50
    elif aggregate >= 200:
        return 86.00
    elif aggregate >= 190:
        return 85.50
    elif aggregate >= 180:
        return 85.00
    elif aggregate >= 170:
        return 84.50
    elif aggregate >= 160:
        return 84.00
    elif aggregate >= 150:
        return 83.50
    elif aggregate >= 140:
        return 83.00
    elif aggregate >= 130:
        return 82.50
    elif aggregate >= 120:
        return 82.00
    elif aggregate >= 110:
        return 81.50
    elif aggregate >= 100:
        return 81.00
    elif aggregate >= 90:
        return 80.50
    elif aggregate >= 80:
        return 80.00
    elif aggregate >= 70:
        return 79.50
    elif aggregate >= 60:
        return 79.00
    elif aggregate >= 50:
        return 78.50
    else:
        return max(0.00, round((aggregate / 500) * 78.5, 2))

def calculate_subject_contributions(subjects_data):
    """
    Calculate each subject's contribution to the ATAR aggregate
    Returns: list of dicts with contribution details
    """
    contributions = []
    total_units = 0
    
    # Calculate total units first
    for subject in subjects_data:
        units = subject.get('units', get_subject_units(subject['name']))
        total_units += units
    
    # Calculate contributions
    for subject in subjects_data:
        subject_name = subject['name']
        raw_mark = subject['raw_mark']
        units = subject.get('units', get_subject_units(subject_name))
        
        scaled_mark = get_scaled_mark(subject_name, raw_mark)
        
        # Calculate contribution to aggregate (scaled to ATAR units)
        contribution = (scaled_mark / 100) * 50 * units
        
        # If more than 10 units total, scale down
        if total_units > 10:
            contribution *= (10 / total_units)
        
        contributions.append({
            'name': subject_name,
            'raw_mark': raw_mark,
            'scaled_mark': scaled_mark,
            'units': units,
            'contribution': contribution
        })
    
    return contributions

def calculate_atar(subjects_data):
    """
    Main function to calculate ATAR from subject data
    Returns: dict with ATAR score, aggregate, and subject contributions
    """
    # Calculate aggregate
    aggregate = calculate_atar_aggregate(subjects_data)
    
    # Convert to ATAR
    atar_score = aggregate_to_atar(aggregate)
    
    # Calculate subject contributions
    contributions = calculate_subject_contributions(subjects_data)
    
    return {
        'atar': atar_score,
        'aggregate': aggregate,
        'subjects': contributions
    }
