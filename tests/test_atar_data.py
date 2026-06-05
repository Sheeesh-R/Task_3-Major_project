import sys
import os
import math

# Ensure package path is discoverable when tests run from workspace root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Task_Organiser'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from atar_data import get_scaled_mark, calculate_atar_estimate


def test_get_scaled_mark_known_subject():
    scaled = get_scaled_mark('English Advanced', 85)
    assert isinstance(scaled, float)
    assert 0 <= scaled <= 100


def test_get_scaled_mark_clamping():
    # Below min
    low = get_scaled_mark('Mathematics Advanced', 10)
    assert 0 <= low <= 100

    # Above max
    high = get_scaled_mark('Mathematics Advanced', 150)
    assert 0 <= high <= 100


def test_calculate_atar_estimate_empty():
    res = calculate_atar_estimate([])
    assert res['atar'] == 0.0
    assert res['aggregate'] == 0.0


def test_calculate_atar_estimate_simple():
    subjects = [
        {'subject_name': 'English Advanced', 'hsc_mark': 85, 'units': 2},
        {'subject_name': 'Mathematics Advanced', 'hsc_mark': 90, 'units': 2},
        {'subject_name': 'Physics', 'hsc_mark': 80, 'units': 2},
    ]
    res = calculate_atar_estimate(subjects)
    assert 'atar' in res and 'aggregate' in res
    assert isinstance(res['atar'], float)
    assert isinstance(res['aggregate'], float)
    assert res['units_counted'] <= 10
