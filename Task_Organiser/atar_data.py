"""ATAR scaling and estimation utilities.

This module provides functions to convert HSC marks to scaled marks using
polynomial regression on published scaling anchor points, aggregate the
scaled marks and convert an aggregate score to an estimated ATAR.
"""

from typing import Any, Optional

import logging
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

_LOGGER = logging.getLogger(__name__)

# Scaling data from ATAR_calc.md (hscscalinggraphs.au + matrix.edu.au anchors)
SUBJECT_SCALING_POINTS = {
    # English subjects
    "English Advanced": [
        (20, 14.1),
        (64, 44),
        (70, 49),
        (75, 53.1),
        (77, 55),
        (82, 67),
        (85, 78),
        (90, 84),
        (95, 93),
        (99, 100),
    ],
    "English Standard": [
        (20, 8.2),
        (68, 29),
        (73, 40),
        (75, 51.4),
        (77, 52),
        (80, 63),
        (85, 73),
        (88, 80),
        (95, 93),
        (98, 99),
    ],
    "English Extension 1": [
        (20, 17.3),
        (75, 64.8),
        (82, 70),
        (84, 74),
        (88, 78),
        (92, 82),
        (94, 88),
        (98, 96),
        (100, 100),
    ],
    "English Extension 2": [
        (20, 17.9),
        (75, 67.2),
        (76, 68),
        (83, 73),
        (90, 81),
        (92, 83),
        (95, 85),
        (96, 88),
        (98, 96),
        (100, 100),
    ],
    # Mathematics subjects
    "Mathematics Extension 2": [
        (20, 21.6),
        (40, 43.3),
        (75, 83),
        (85, 89.5),
        (93, 93.5),
        (96, 96.5),
        (99, 99.5),
        (100, 100),
    ],
    "Mathematics Extension 1": [
        (20, 19.4),
        (50, 48.6),
        (70, 73),
        (75, 75),
        (80, 80),
        (84, 83),
        (92, 89.5),
        (96, 94.5),
        (99, 99),
        (100, 100),
    ],
    "Mathematics Advanced": [
        (20, 14.1),
        (70, 49.3),
        (72, 52),
        (75, 58.5),
        (80, 66.5),
        (85, 72.5),
        (89, 78),
        (94, 86),
        (96, 95),
        (100, 100),
    ],
    "Maths Standard 2": [
        (20, 8.4),
        (64, 30.5),
        (73, 46.5),
        (75, 50.5),
        (81, 63),
        (82, 63.5),
        (85, 69.5),
        (89, 75),
        (95, 85.5),
        (98, 94),
    ],
    # Science subjects
    "Physics": [
        (20, 14.3),
        (64, 48),
        (75, 64),
        (84, 78),
        (90, 86),
        (95, 94.5),
        (99, 100),
    ],
    "Biology": [
        (20, 11.9),
        (66, 36),
        (75, 57.3),
        (84, 70),
        (88, 80),
        (95, 90),
        (99, 100),
    ],
    "Chemistry": [
        (20, 14.9),
        (68, 51.5),
        (75, 63.8),
        (80, 74),
        (84, 79.5),
        (90, 87),
        (95, 94.5),
        (99, 100),
    ],
    "Investigating Science": [
        (68, 23),
        (76, 40),
        (85, 58),
        (89, 71),
        (94, 85),
        (98, 93.5),
    ],
    "Earth & Environmental Science": [
        (20, 9.8),
        (67, 28),
        (76, 46.5),
        (80, 63),
        (88, 74.5),
        (90, 85),
        (95, 86),
        (99, 96),
    ],
    "Senior Science": [(20, 6.5)],
    # Humanities and Social Sciences
    "Business Studies": [
        (20, 9.3),
        (66, 30.5),
        (75, 46.5),
        (80, 55),
        (85, 65),
        (90, 79.5),
        (96, 91),
        (99, 100),
    ],
    "Economics": [
        (20, 15.2),
        (66, 33),
        (71, 50),
        (75, 63.5),
        (80, 66),
        (87, 78),
        (90, 86),
        (96, 94),
        (100, 100),
    ],
    "Legal Studies": [
        (20, 10.4),
        (66, 33),
        (75, 47),
        (80, 52),
        (85, 65),
        (90, 80),
        (96, 91),
        (99, 100),
    ],
    "Geography": [
        (64, 27.5),
        (68, 33.5),
        (70, 42),
        (75, 51),
        (80, 56),
        (85, 65.5),
        (86, 69),
        (90, 81.5),
        (95, 94.5),
        (100, 100),
    ],
    "Modern History": [
        (20, 11.3),
        (64, 27.5),
        (68, 34),
        (75, 52),
        (76, 56),
        (80, 59.5),
        (85, 67.5),
        (86, 68.5),
        (90, 79),
        (95, 92),
        (99, 100),
    ],
    "Ancient History": [
        (20, 10.4),
        (64, 27.5),
        (70, 41.5),
        (75, 45),
        (80, 56),
        (85, 62.5),
        (86, 69),
        (90, 75),
        (95, 89),
        (99, 97),
    ],
    "Studies of Religion I": [
        (20, 12.3),
        (70, 41.5),
        (75, 51.5),
        (80, 59.5),
        (85, 62.5),
        (86, 69.5),
        (90, 75.5),
        (95, 80),
        (97, 88.5),
        (99, 97),
    ],
    "Studies of Religion II": [(20, 11.9)],
    "History Extension": [(20, 17.8), (75, 66.5)],
    "PDHPE": [
        (20, 9.1),
        (67, 28.5),
        (75, 46),
        (80, 63),
        (85, 63.5),
        (90, 75),
        (95, 87),
        (97, 96.5),
    ],
    "Society & Culture": [
        (20, 9.1),
        (72, 29.5),
        (75, 46.5),
        (80, 52),
        (85, 63),
        (87, 66.5),
        (90, 75.5),
        (95, 89.5),
        (99, 96.5),
        (100, 100),
    ],
    # Arts and Technologies
    "Drama": [(20, 9.1), (75, 40.7)],
    "Music 1": [(20, 7.5), (75, 28.0)],
    "Music 2": [(20, 13.7), (75, 51.4)],
    "Music Extension": [(20, 13.5), (75, 50.6)],
    "Visual Arts": [(20, 7.7), (75, 30.7)],
    "Community & Family Studies": [
        (20, 6.6),
        (67, 19.5),
        (72, 29.5),
        (75, 36),
        (80, 53.5),
        (85, 67),
        (87, 67.5),
        (95, 88.5),
        (99, 93),
        (100, 100),
    ],
    "Dance": [(79, 30.5), (85, 49), (89, 65), (95, 79), (98, 89), (99, 93)],
    "Software Engineering": [
        (69, 38.5),
        (76, 54.5),
        (82, 69.5),
        (89, 81),
        (96, 94),
        (99, 100),
    ],
    "Textiles & Design": [(20, 8.3)],
    "Engineering Studies": [
        (20, 11.1),
        (67, 37.5),
        (71, 44.5),
        (75, 53),
        (80, 67),
        (90, 79.5),
        (96, 91.5),
        (100, 99.5),
    ],
    "Industrial Technology": [
        (20, 5.6),
        (63, 18.5),
        (71, 33.5),
        (79, 51),
        (85, 65.5),
        (88, 68),
        (90, 72.5),
        (95, 79.5),
        (99, 84.5),
        (100, 100),
    ],
    "Food Technology": [
        (65, 19),
        (69, 35.5),
        (74, 42),
        (82, 54.5),
        (89, 71.5),
        (95, 86),
        (98, 91.5),
        (99, 100),
    ],
    "Design & Technology": [
        (20, 7.9),
        (78, 30),
        (80, 45.5),
        (85, 62),
        (90, 74.5),
        (95, 90),
        (99, 95.5),
        (100, 100),
    ],
    "ESL": [(20, 7.6)],
}

# Map UI / NESA subject names to scaling-data keys
SUBJECT_ALIASES = {
    "Earth and Environmental Science": "Earth & Environmental Science",
    "Society and Culture": "Society & Culture",
    "Community and Family Studies": "Community & Family Studies",
    "Design and Technology": "Design & Technology",
    "Textiles and Design": "Textiles & Design",
    "General Maths": "Maths Standard 2",
    "English EAL/D": "ESL",
    "Software Design & Development": "Software Engineering",
}

# Cache for polynomial models to avoid retraining
_POLYNOMIAL_MODELS = {}


def resolve_subject_name(subject_name: str) -> str:
    """Map UI/NESA subject names to SUBJECT_SCALING_POINTS keys."""
    return SUBJECT_ALIASES.get(subject_name, subject_name)


def get_polynomial_model(subject_name: str) -> Optional[Any]:
    """Return a cached or newly trained polynomial regression model.

    Args:
        subject_name: Subject name matching SUBJECT_SCALING_POINTS keys.

    Returns:
        A scikit-learn pipeline model or ``None`` if the subject is unknown.
    """
    subject_name = resolve_subject_name(subject_name)
    if subject_name not in SUBJECT_SCALING_POINTS:
        return None

    # Return cached model if already created
    if subject_name in _POLYNOMIAL_MODELS:
        return _POLYNOMIAL_MODELS[subject_name]

    # Get scaling data for this subject
    data_points = SUBJECT_SCALING_POINTS[subject_name]
    n = len(data_points)

    # Single-point subjects use linear fallback in get_scaled_mark
    if n == 1:
        return None

    # Degree selection per ATAR_calc.md
    if n >= 8:
        degree = 4
    elif n == 2:
        degree = 1
    else:
        degree = min(3, n - 1)

    # Create polynomial features and fit model
    X = np.array([point[0] for point in data_points]).reshape(-1, 1)
    y = np.array([point[1] for point in data_points])

    model = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False), LinearRegression()
    )

    model.fit(X, y)

    # Cache and return the model
    _POLYNOMIAL_MODELS[subject_name] = model
    return model


def is_extension_out_of_50(subject_name: str) -> bool:
    """Return True for extension subjects whose raw marks are entered out of 50."""
    return (
        "Extension" in subject_name
        and subject_name != "Mathematics Extension 2"
    )


def normalize_hsc_mark_for_scaling(subject_name: str, hsc_mark: float) -> float:
    """Convert user-entered marks to the 0-100 scale used by scaling data."""
    if is_extension_out_of_50(subject_name):
        return hsc_mark * 2
    return hsc_mark


def round_atar(atar: float) -> float:
    """Round ATAR to the nearest 0.05 (UAC reporting increment)."""
    atar = max(0.0, min(99.95, atar))
    return round(atar * 20) / 20


def get_scaled_mark(subject_name: str, hsc_mark: float) -> float:
    """Convert an HSC mark to a scaled mark for a specific subject.

    Uses polynomial regression (degree 4 for subjects with 8+ data points,
    degree 3 for fewer) trained on published scaling anchor points.
    For sparse low-end data regions, uses linear interpolation from the first
    anchor point to the second anchor point to avoid polynomial oscillation.
    Inputs are clamped to the training range to avoid unreasonable extrapolation.
    The returned value is clipped to the 0-100 range.

    Args:
        subject_name: Name of the subject as found in SUBJECT_SCALING_POINTS.
        hsc_mark: Raw HSC mark on the 0-100 scale used by scaling data
            (extension marks out of 50 should be normalised before calling).

    Returns:
        Scaled mark as a float between 0 and 100.
    """
    subject_name = resolve_subject_name(subject_name)
    if subject_name not in SUBJECT_SCALING_POINTS:
        return float(np.clip(hsc_mark, 0, 100))

    # Get the polynomial model
    model = get_polynomial_model(subject_name)
    data_points = sorted(SUBJECT_SCALING_POINTS[subject_name], key=lambda p: p[0])
    min_mark = data_points[0][0]
    max_mark = data_points[-1][0]

    # Determine the reliable range for polynomial regression.
    # For subjects with a gap after the first point, use linear interpolation
    # up to the second data point, then polynomial regression.
    poly_min_mark = min_mark
    if len(data_points) >= 2:
        # Use polynomial only from the 2nd data point onwards
        # This avoids oscillation in the sparse region between 1st and 2nd point
        poly_min_mark = data_points[1][0]

    if model is not None:
        if hsc_mark < min_mark:
            # Linear extrapolation below minimum
            if min_mark > 0:
                scaled_mark = (hsc_mark / min_mark) * data_points[0][1]
            else:
                scaled_mark = 0.0
        elif hsc_mark > max_mark:
            # Clamp to maximum
            scaled_mark = data_points[-1][1]
        elif hsc_mark < poly_min_mark:
            # Sparse region: linear interpolation between 1st and 2nd data point
            x1, y1 = data_points[0]
            x2, y2 = data_points[1]
            scaled_mark = y1 + (hsc_mark - x1) * (y2 - y1) / (x2 - x1)
        else:
            # Dense region: use polynomial model
            scaled_mark = float(model.predict([[hsc_mark]])[0])
    else:
        # Single-point subjects: use linear interpolation
        xs = [point[0] for point in data_points]
        ys = [point[1] for point in data_points]
        min_mark, min_scaled = data_points[0]
        max_mark, max_scaled = data_points[-1]

        if hsc_mark <= min_mark:
            if min_mark > 0:
                scaled_mark = (hsc_mark / min_mark) * min_scaled
            else:
                scaled_mark = 0.0
        elif hsc_mark >= max_mark:
            scaled_mark = max_scaled
        else:
            scaled_mark = float(np.interp(hsc_mark, xs, ys))

    return float(np.clip(scaled_mark, 0, 100))


def generate_chart_curve_points(subject_name: str) -> list[dict[str, float]]:
    """Return dense HSC→scaled samples for smooth chart curves.

    Uses the actual scaling function (hybrid linear + polynomial) to match
    calculator behavior exactly.
    """
    subject_name = resolve_subject_name(subject_name)
    
    # Use consistent small step size for smooth curves (0.5 increments = 201 points)
    hsc_marks = [round(i * 0.5, 1) for i in range(0, 201)]  # 0 to 100 in 0.5 increments

    return [
        {"x": hsc, "y": round(get_scaled_mark(subject_name, hsc), 2)}
        for hsc in hsc_marks
    ]


def generate_polynomial_curve_points(subject_name: str) -> list[dict[str, float]]:
    """Return dense HSC→scaled samples showing a smooth polynomial regression curve.

    Uses the actual scaling function (hybrid linear + polynomial) which produces
    a single smooth continuous line with no sharp turns, matching calculator behavior.
    """
    subject_name = resolve_subject_name(subject_name)
    
    # Use consistent small step size for smooth curves (0.5 increments = 201 points)
    hsc_marks = [round(i * 0.5, 1) for i in range(0, 201)]  # 0 to 100 in 0.5 increments

    model = get_polynomial_model(subject_name)
    if model is None:
        # Single-point subjects: fallback to linear
        return [
            {"x": hsc, "y": round(get_scaled_mark(subject_name, hsc), 2)}
            for hsc in hsc_marks
        ]

    # Use the actual scaling function (hybrid linear + polynomial) for smooth curves
    return [
        {"x": hsc, "y": round(get_scaled_mark(subject_name, hsc), 2)}
        for hsc in hsc_marks
    ]


def aggregate_to_atar(aggregate: float) -> float:
    """
    Convert aggregate score to ATAR using linear interpolation.

    Based on UAC published conversion table.
    """
    # UAC conversion breakpoints (aggregate, ATAR) — ATAR_calc.md
    conversion_points = [
        (500, 99.95),
        (490, 99.70),
        (480, 99.50),
        (470, 99.20),
        (460, 99.00),
        (450, 98.50),
        (440, 98.00),
        (430, 97.00),
        (420, 96.00),
        (410, 95.00),
        (400, 93.50),
        (390, 92.00),
        (380, 90.00),
        (370, 88.00),
        (360, 85.00),
        (350, 82.00),
        (340, 79.00),
        (330, 76.00),
        (320, 73.00),
        (310, 70.00),
        (300, 67.00),
        (280, 61.00),
        (260, 55.00),
        (240, 49.00),
        (220, 43.00),
        (200, 37.00),
        (180, 32.00),
        (160, 27.00),
        (140, 22.00),
        (120, 17.00),
        (100, 12.00),
        (80, 8.00),
        (60, 4.00),
        (0, 0.00),
    ]

    # Sort points by aggregate score (ascending)
    conversion_points.sort()

    # Find the appropriate range and interpolate
    for i in range(len(conversion_points) - 1):
        x1, y1 = conversion_points[i]
        x2, y2 = conversion_points[i + 1]
        if aggregate >= x1 and aggregate <= x2:
            # Linear interpolation between two points
            atar = y1 + (aggregate - x1) * (y2 - y1) / (x2 - x1)
            return max(0.0, min(99.95, atar))

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
            "atar": 0.0,
            "aggregate": 0.0,
            "subject_results": [],
            "units_counted": 0,
            "english_counted": False,
        }

    # Calculate scaled marks for each subject
    subject_results = []
    for subject in subjects:
        subject_name = subject["subject_name"]
        hsc_mark = subject["hsc_mark"]
        units = subject.get("units", 2)

        scaling_mark = normalize_hsc_mark_for_scaling(subject_name, hsc_mark)
        scaled_mark = get_scaled_mark(subject_name, scaling_mark)
        contribution = scaled_mark

        subject_results.append(
            {
                "subject_name": subject_name,
                "hsc_mark": hsc_mark,
                "scaled_mark": scaled_mark,
                "units": units,
                "contribution": contribution,
            }
        )

    # Expand subjects into individual units
    # Each unit gets the same scaled mark as the subject
    unit_list = []
    for subject in subject_results:
        units_count = subject["units"]
        for _ in range(units_count):
            unit_list.append(
                {
                    "subject_name": subject["subject_name"],
                    "hsc_mark": subject["hsc_mark"],
                    "scaled_mark": subject["scaled_mark"],
                    "is_english": "English" in subject["subject_name"],
                }
            )

    # Sort all units by scaled mark descending
    unit_list.sort(key=lambda x: x["scaled_mark"], reverse=True)

    # Select top 10 units, ensuring at least 2 English units if available
    selected_units_list = []
    english_units = [u for u in unit_list if u["is_english"]]
    
    # Ensure at least 2 English units are included
    english_counted = len(english_units) >= 2
    if english_counted:
        selected_units_list.extend(english_units[:2])
    elif english_units:
        selected_units_list.extend(english_units)

    # Add remaining best units to reach 10
    remaining_units = [u for u in unit_list if u not in selected_units_list]
    remaining_needed = 10 - len(selected_units_list)
    selected_units_list.extend(remaining_units[:remaining_needed])

    # Calculate aggregate score from selected units
    # Scaled marks are out of 100, but each unit contributes out of 50 to the aggregate
    aggregate_score = sum(u["scaled_mark"] / 2 for u in selected_units_list)
    units_counted = len(selected_units_list)

    # Reconstruct subject_results for display (group units by subject)
    # This shows which subjects contributed and how many units
    selected_by_subject = {}
    for unit in selected_units_list:
        subj_name = unit["subject_name"]
        if subj_name not in selected_by_subject:
            selected_by_subject[subj_name] = {
                "subject_name": subj_name,
                "hsc_mark": unit["hsc_mark"],
                "scaled_mark": unit["scaled_mark"],
                "units": 0,
                "contribution": 0.0,
            }
        selected_by_subject[subj_name]["units"] += 1
        selected_by_subject[subj_name]["contribution"] += unit["scaled_mark"] / 2  # Add per-unit contribution

    selected_units = list(selected_by_subject.values())

    # Convert aggregate to ATAR
    atar_score = aggregate_to_atar(aggregate_score)

    return {
        "atar": round_atar(atar_score),
        "aggregate": round(aggregate_score, 1),
        "subject_results": selected_units,
        "units_counted": units_counted,
        "english_counted": english_counted,
    }
