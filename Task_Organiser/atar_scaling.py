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
