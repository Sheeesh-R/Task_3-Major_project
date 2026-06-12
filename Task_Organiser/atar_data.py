"""ATAR scaling and estimation utilities.

This module converts raw HSC marks into scaled marks using **Polynomial
Regression** trained on published UAC scaling anchor points.  The scaled
marks are then aggregated and mapped to an estimated ATAR.

Machine-learning pipeline
-------------------------
1. **Training data** -- Each subject has a list of (hsc_mark, scaled_mark)
   anchor points sourced from UAC / hscscalinggraphs.au / matrix.edu.au.
2. **Model selection** -- The polynomial degree is chosen automatically:
   * 8+ anchor points  -> degree 4 (captures non-linear scaling curves)
   * 3-7 anchor points -> degree 3
   * 2 anchor points   -> degree 1 (linear)
   * 1 anchor point    -> linear fallback (no model trained)
3. **Hybrid interpolation** -- For the sparse region between the first and
   second anchor points a simple linear interpolation is used to avoid
   polynomial oscillation; the polynomial model handles the denser region
   above the second anchor.
4. **Clamping** -- Predictions are clamped to [0, 100] to prevent
   unreasonable extrapolation outside the training range.
5. **Caching** -- Trained pipelines are cached in ``_POLYNOMIAL_MODELS``
   so each subject's model is fitted only once per process lifetime.

Aggregate-to-ATAR mapping
-------------------------
The aggregate (sum of the best 10 scaled unit marks divided by 2) is
converted to an ATAR via linear interpolation on the UAC published
conversion table.  The final ATAR is rounded to the nearest 0.05
(UAC reporting increment).
"""

from typing import Any, Optional

import logging
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

_LOGGER = logging.getLogger(__name__)

# Scaling data from ATAR_calc.md (hscscalinggraphs.au + matrix.edu.au anchors)
# Each entry maps a subject name to a list of (hsc_mark, scaled_mark) tuples.
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

# Cache for polynomial models to avoid retraining on every request.
_POLYNOMIAL_MODELS: dict[str, Any] = {}


def resolve_subject_name(subject_name: str) -> str:
    """Map UI / NESA subject names to the keys in SUBJECT_SCALING_POINTS."""
    return SUBJECT_ALIASES.get(subject_name, subject_name)


def get_polynomial_model(subject_name: str) -> Optional[Any]:
    """Return a cached or newly trained polynomial regression model.

    The model is a scikit-learn ``Pipeline`` that first expands features
    to polynomial terms (``PolynomialFeatures``) then fits a linear
    regression (``LinearRegression``) on those expanded features.

    Degree selection heuristic (from ATAR_calc.md):
        * >= 8 anchor points -> degree 4 (captures complex non-linearity)
        * 2 anchor points    -> degree 1 (simple linear interpolation)
        * otherwise          -> min(3, n-1)

    Args:
        subject_name: Must match a key in ``SUBJECT_SCALING_POINTS``.

    Returns:
        Fitted scikit-learn pipeline, or ``None`` for single-point subjects.
    """
    subject_name = resolve_subject_name(subject_name)
    if subject_name not in SUBJECT_SCALING_POINTS:
        return None

    # Return cached model if already trained (avoids re-fitting).
    if subject_name in _POLYNOMIAL_MODELS:
        return _POLYNOMIAL_MODELS[subject_name]

    data_points = SUBJECT_SCALING_POINTS[subject_name]
    n = len(data_points)

    # Single-point subjects have no training range; fall back to linear.
    if n == 1:
        return None

    # --- Degree selection ------------------------------------------------
    if n >= 8:
        degree = 4
    elif n == 2:
        degree = 1
    else:
        degree = min(3, n - 1)

    # --- Feature matrix and target vector --------------------------------
    X = np.array([point[0] for point in data_points]).reshape(-1, 1)
    y = np.array([point[1] for point in data_points])

    # --- Build and fit the pipeline --------------------------------------
    # PolynomialFeatures generates [x, x^2, ..., x^degree] from the raw mark.
    # LinearRegression then learns coefficients for each polynomial term.
    model = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        LinearRegression(),
    )
    model.fit(X, y)

    # Cache for future calls so each subject is trained at most once.
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
    """Convert an HSC mark to a scaled mark using the trained polynomial model.

    Hybrid approach:
        1. Below the first anchor  -> linear extrapolation from origin.
        2. Between 1st and 2nd     -> linear interpolation (avoids polynomial
           anchor points              oscillation in the sparse low-end region).
        3. Above the 2nd anchor   -> polynomial regression prediction.
        4. Above the max anchor   -> clamped to the maximum scaled value.

    Args:
        subject_name: Subject name (resolved via ``SUBJECT_ALIASES``).
        hsc_mark: Raw mark on 0-100 scale (extension marks must be
                  normalised first via ``normalize_hsc_mark_for_scaling``).

    Returns:
        Scaled mark clipped to [0, 100].
    """
    subject_name = resolve_subject_name(subject_name)
    if subject_name not in SUBJECT_SCALING_POINTS:
        return float(np.clip(hsc_mark, 0, 100))

    model = get_polynomial_model(subject_name)
    data_points = sorted(SUBJECT_SCALING_POINTS[subject_name], key=lambda p: p[0])
    min_mark = data_points[0][0]
    max_mark = data_points[-1][0]

    # The polynomial model is only reliable above the second anchor point.
    # Below that, linear interpolation avoids wild oscillation.
    poly_min_mark = min_mark
    if len(data_points) >= 2:
        poly_min_mark = data_points[1][0]

    if model is not None:
        if hsc_mark < min_mark:
            # Linear extrapolation below the training range.
            scaled_mark = (
                (hsc_mark / min_mark) * data_points[0][1] if min_mark > 0 else 0.0
            )
        elif hsc_mark > max_mark:
            # Clamp to the highest published scaled value.
            scaled_mark = data_points[-1][1]
        elif hsc_mark < poly_min_mark:
            # Sparse region: linear interpolation between the first two anchors.
            x1, y1 = data_points[0]
            x2, y2 = data_points[1]
            scaled_mark = y1 + (hsc_mark - x1) * (y2 - y1) / (x2 - x1)
        else:
            # Dense region: use the trained polynomial model.
            scaled_mark = float(model.predict([[hsc_mark]])[0])
    else:
        # Single-point subjects: linear interpolation across all anchors.
        xs = [point[0] for point in data_points]
        ys = [point[1] for point in data_points]
        min_mark, min_scaled = data_points[0]
        max_mark, max_scaled = data_points[-1]

        if hsc_mark <= min_mark:
            scaled_mark = (
                (hsc_mark / min_mark) * min_scaled if min_mark > 0 else 0.0
            )
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
    """Map an aggregate score to an estimated ATAR via linear interpolation.

    Uses the 2024 UAC published conversion table (Table A9) with
    aggregate 0 -> ATAR 0.00 up to aggregate 500 -> ATAR 99.95.

    The aggregate is the sum of the best 10 scaled unit marks divided
    by 2 (each unit contributes a maximum of 50 points).

    Args:
        aggregate: Aggregate score (typically 0-500).

    Returns:
        Estimated ATAR rounded to the nearest 0.05.
    """
    # UAC conversion breakpoints (aggregate, ATAR)
    # 2024 UAC scaling report Table A9 + detailed lookup table
    conversion_points = [
        (0.0, 0.00),
        (150.0, 47.85),
        (160.6, 50.00),
        (185.3, 55.00),
        (200.0, 58.00),
        (210.1, 60.00),
        (235.4, 65.00),
        (250.0, 67.85),
        (260.6, 70.00),
        (286.2, 75.00),
        (300.0, 77.60),
        (312.6, 80.00),
        (340.2, 85.00),
        (350.0, 86.75),
        (369.2, 90.00),
        (400.0, 94.50),
        (403.5, 95.00),
        (431.6, 98.00),
        (445.6, 99.00),
        (450.0, 99.20),
        (455.9, 99.50),
        (477.4, 99.95),
        (500.0, 99.95),
    ]

    conversion_points.sort()

    # Linear interpolation between the two bounding breakpoints.
    for i in range(len(conversion_points) - 1):
        x1, y1 = conversion_points[i]
        x2, y2 = conversion_points[i + 1]
        if x1 <= aggregate <= x2:
            atar = y1 + (aggregate - x1) * (y2 - y1) / (x2 - x1)
            return max(0.0, min(99.95, atar))

    # Edge cases: below or above the conversion table range.
    if aggregate < conversion_points[0][0]:
        return 0.0
    return conversion_points[-1][1]


def calculate_atar_estimate(subjects: list[dict]) -> dict:
    """Calculate an ATAR estimate from a list of subjects and their HSC marks.

    Algorithm:
        1. For each subject, normalise the mark (extension /50 -> /100)
           then pass it through the polynomial regression model to get a
           scaled mark.
        2. Expand 2-unit subjects into two individual unit entries, each
           carrying the same scaled mark.
        3. Rank all units by scaled mark descending and select the best
           10, enforcing the UAC rule that at least 2 units must be
           from English subjects (if available).
        4. The aggregate is the sum of the 10 selected scaled marks
           divided by 2 (each unit contributes out of 50).
        5. The aggregate is mapped to an ATAR via the UAC conversion table.

    Args:
        subjects: List of dicts, each containing:
            - ``subject_name`` (str): e.g. "Physics"
            - ``hsc_mark`` (float): raw mark 0-100 (or 0-50 for extensions)
            - ``units`` (int, optional): unit value (default 2)

    Returns:
        Dict with keys: ``atar``, ``aggregate``, ``subject_results``,
        ``units_counted``, ``english_counted``.
    """
    if not subjects:
        return {
            "atar": 0.0,
            "aggregate": 0.0,
            "subject_results": [],
            "units_counted": 0,
            "english_counted": False,
        }

    # --- Step 1: Scale each subject's mark --------------------------------
    subject_results = []
    for subject in subjects:
        subject_name = subject["subject_name"]
        hsc_mark = subject["hsc_mark"]
        units = subject.get("units", 2)

        # Normalise extension subjects (out of 50) to the /100 scale.
        scaling_mark = normalize_hsc_mark_for_scaling(subject_name, hsc_mark)
        scaled_mark = get_scaled_mark(subject_name, scaling_mark)

        subject_results.append({
            "subject_name": subject_name,
            "hsc_mark": hsc_mark,
            "scaled_mark": scaled_mark,
            "units": units,
            "contribution": scaled_mark,
        })

    # --- Step 2: Expand into individual units -----------------------------
    # A 2-unit subject counts as 2 separate units in the aggregate.
    unit_list = []
    for subject in subject_results:
        for _ in range(subject["units"]):
            unit_list.append({
                "subject_name": subject["subject_name"],
                "hsc_mark": subject["hsc_mark"],
                "scaled_mark": subject["scaled_mark"],
                "is_english": "English" in subject["subject_name"],
            })

    # --- Step 3: Select best 10 units (UAC rule) -------------------------
    # UAC requires at least 2 English units to be included in the
    # aggregate calculation if the student has 2+ English units.
    unit_list.sort(key=lambda x: x["scaled_mark"], reverse=True)

    selected_units_list = []
    english_units = [u for u in unit_list if u["is_english"]]
    english_counted = len(english_units) >= 2

    if english_counted:
        selected_units_list.extend(english_units[:2])
    elif english_units:
        selected_units_list.extend(english_units)

    remaining_units = [u for u in unit_list if u not in selected_units_list]
    remaining_needed = 10 - len(selected_units_list)
    selected_units_list.extend(remaining_units[:remaining_needed])

    # --- Step 4: Compute aggregate ----------------------------------------
    # Each unit contributes out of 50, so divide the scaled mark by 2.
    aggregate_score = sum(u["scaled_mark"] / 2 for u in selected_units_list)
    units_counted = len(selected_units_list)

    # --- Step 5: Map aggregate -> ATAR ------------------------------------
    atar_score = aggregate_to_atar(aggregate_score)

    # --- Build per-subject breakdown for display --------------------------
    selected_by_subject: dict[str, dict] = {}
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
        selected_by_subject[subj_name]["contribution"] += unit["scaled_mark"] / 2

    return {
        "atar": round_atar(atar_score),
        "aggregate": round(aggregate_score, 1),
        "subject_results": list(selected_by_subject.values()),
        "units_counted": units_counted,
        "english_counted": english_counted,
    }
