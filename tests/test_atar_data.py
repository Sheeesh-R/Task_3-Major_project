import sys
import os
# Ensure package path is discoverable when tests run from workspace root
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "Task_Organiser")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from atar_data import (  # noqa: E402
    SUBJECT_SCALING_POINTS,
    get_scaled_mark,
    calculate_atar_estimate,
    normalize_hsc_mark_for_scaling,
    round_atar,
    resolve_subject_name,
)


def test_get_scaled_mark_known_subject():
    scaled = get_scaled_mark("English Advanced", 85)
    assert isinstance(scaled, float)
    assert 0 <= scaled <= 100


def test_get_scaled_mark_clamping():
    # Below min
    low = get_scaled_mark("Mathematics Advanced", 10)
    assert 0 <= low <= 100

    # Above max
    high = get_scaled_mark("Mathematics Advanced", 150)
    assert 0 <= high <= 100


def test_calculate_atar_estimate_empty():
    res = calculate_atar_estimate([])
    assert res["atar"] == 0.0
    assert res["aggregate"] == 0.0


def test_calculate_atar_estimate_simple():
    subjects = [
        {"subject_name": "English Advanced", "hsc_mark": 85, "units": 2},
        {"subject_name": "Mathematics Advanced", "hsc_mark": 90, "units": 2},
        {"subject_name": "Physics", "hsc_mark": 80, "units": 2},
    ]
    res = calculate_atar_estimate(subjects)
    assert "atar" in res and "aggregate" in res
    assert isinstance(res["atar"], float)
    assert isinstance(res["aggregate"], float)
    assert res["units_counted"] <= 10


def test_calculate_atar_estimate_full_10_units():
    """Test that 10 units are correctly selected from mix of 2-unit and 1-unit subjects."""
    subjects = [
        {"subject_name": "English Advanced", "hsc_mark": 88, "units": 2},
        {"subject_name": "Mathematics Advanced", "hsc_mark": 91, "units": 2},
        {"subject_name": "Mathematics Extension 1", "hsc_mark": 47, "units": 1},
        {"subject_name": "Physics", "hsc_mark": 89, "units": 2},
        {"subject_name": "Chemistry", "hsc_mark": 87, "units": 2},
        {"subject_name": "Engineering Studies", "hsc_mark": 80, "units": 2},
    ]
    res = calculate_atar_estimate(subjects)
    # With 11 total units available, should select exactly 10
    assert res["units_counted"] == 10, f"Expected 10 units, got {res['units_counted']}"
    assert res["english_counted"] is True
    assert res["atar"] > 0


def test_normalize_extension_mark_out_of_50():
    assert normalize_hsc_mark_for_scaling("Mathematics Extension 1", 50) == 100
    assert normalize_hsc_mark_for_scaling("English Extension 1", 35) == 70
    assert normalize_hsc_mark_for_scaling("Mathematics Extension 2", 94) == 94
    assert normalize_hsc_mark_for_scaling("English Advanced", 85) == 85


def test_extension_50_of_50_scales_like_100_of_100():
    scaled_perfect = get_scaled_mark(
        "Mathematics Extension 1",
        normalize_hsc_mark_for_scaling("Mathematics Extension 1", 50),
    )
    assert scaled_perfect >= 99.0


def test_round_atar_to_nearest_0_05():
    assert round_atar(75.68) == 75.70
    assert round_atar(79.98) == 80.00
    assert round_atar(99.97) == 99.95
    assert round_atar(90.00) == 90.00
    assert round_atar(79.95) == 79.95


def test_subject_aliases_resolve_to_scaling_keys():
    assert resolve_subject_name("Society and Culture") == "Society & Culture"
    assert resolve_subject_name("Software Design & Development") == "Software Engineering"
    assert resolve_subject_name("English Advanced") == "English Advanced"


def test_matrix_anchor_points_present_in_scaling_data():
    """Key matrix.edu.au anchors from ATAR_calc.md must exist in scaling data."""
    anchors = {
        "English Advanced": (20, 14.1),
        "Mathematics Extension 1": (20, 19.4),
        "Physics": (20, 14.3),
        "Business Studies": (20, 9.3),
        "History Extension": (75, 66.5),
        "Software Engineering": (89, 81),
        "Drama": (75, 40.7),
        "Music 1": (75, 28.0),
    }
    for subject, point in anchors.items():
        assert point in SUBJECT_SCALING_POINTS[subject], f"{subject} missing {point}"


def test_scaled_mark_near_matrix_hsc_75_benchmarks():
    """Polynomial model should land near published matrix HSC=75 scaled marks."""
    benchmarks = {
        "English Advanced": (75, 53.1, 0.1),
        "Chemistry": (75, 63.8, 0.1),
        "Economics": (75, 63.5, 0.1),
        "Biology": (75, 57.3, 0.1),
    }
    for subject, (hsc, expected, tolerance) in benchmarks.items():
        scaled = get_scaled_mark(subject, hsc)
        assert abs(scaled - expected) <= tolerance, (
            f"{subject} at HSC {hsc}: got {scaled}, expected ~{expected}"
        )


def test_alias_subject_uses_same_scaling_data():
    scaled_direct = get_scaled_mark("Software Engineering", 89)
    scaled_alias = get_scaled_mark("Software Design & Development", 89)
    assert scaled_direct == scaled_alias


def test_calculate_atar_estimate_uses_0_05_increments():
    subjects = [
        {"subject_name": "English Advanced", "hsc_mark": 85, "units": 2},
        {"subject_name": "Mathematics Advanced", "hsc_mark": 90, "units": 2},
        {"subject_name": "Physics", "hsc_mark": 80, "units": 2},
    ]
    res = calculate_atar_estimate(subjects)
    assert res["atar"] == round_atar(res["atar"])
    assert abs((res["atar"] * 20) % 1) < 1e-9
