# Polynomial Regression ATAR Scaling Implementation

## Overview

Replace the current linear interpolation approach in the ATAR prediction system with polynomial regression. This will provide a smoother curve through UAC scaling anchor points that better captures how subject scaling actually behaves across the mark range.

**Estimated complexity**: Medium  
**Files affected**: `atar_data.py`, `test_atar_data.py`  
**Backward compatibility**: Maintained (all existing tests should pass)  
**Breaking changes**: None

---

## Current State

### What Exists Now

**File**: `Task_Organiser/atar_data.py`

Current `get_scaled_mark()` uses linear interpolation:
```python
def get_scaled_mark(subject_name: str, hsc_mark: float) -> float:
    # ... setup code ...
    xs = [point[0] for point in data_points]
    ys = [point[1] for point in data_points]
    scaled_mark = float(np.interp(hsc_mark, xs, ys))
    return float(np.clip(scaled_mark, 0, 100))
```

**Issue**: Dead code exists (`get_polynomial_model()` function) that is defined but never called.

**Testing**: `tests/test_atar_data.py` tests the current linear approach.

---

## Target State

### What Should Be Implemented

1. **Implement proper polynomial regression** using scikit-learn's `PolynomialFeatures` and `LinearRegression`
2. **Create a model caching system** to avoid retraining on every call
3. **Handle boundary conditions** properly:
   - Below minimum anchor: linear scaling from origin
   - Within data range: polynomial prediction
   - Above maximum anchor: cap at highest published scaled mark
4. **Remove dead code** and clean up unused functions
5. **Update documentation** to reflect the change from linear interpolation to polynomial regression
6. **Add comprehensive tests** to verify polynomial accuracy

---

## Implementation Details

### Step 1: Implement `get_polynomial_model()` Function

**File**: `Task_Organiser/atar_data.py`

**Replace** the existing dead `get_polynomial_model()` function with this working implementation:

```python
def get_polynomial_model(subject_name: str) -> Optional[Any]:
    """Train and cache a polynomial regression model for a subject.
    
    Fits a polynomial curve through published UAC scaling anchor points.
    The polynomial degree is chosen based on data density:
    - 2-3 points: Linear (degree 1)
    - 4-7 points: Cubic (degree 3)
    - 8+ points: Quartic (degree 4)
    
    Models are cached in memory to avoid retraining on every prediction.
    
    Args:
        subject_name: Subject name matching SUBJECT_SCALING_POINTS keys
    
    Returns:
        A fitted scikit-learn pipeline with PolynomialFeatures and LinearRegression,
        or None if the subject is unknown or has insufficient data points (< 2)
    """
    subject_name = resolve_subject_name(subject_name)
    
    # Check cache first — if model already trained, return it
    if subject_name in _POLYNOMIAL_MODELS:
        return _POLYNOMIAL_MODELS[subject_name]
    
    # Unknown subject
    if subject_name not in SUBJECT_SCALING_POINTS:
        return None
    
    data_points = SUBJECT_SCALING_POINTS[subject_name]
    n = len(data_points)
    
    # Need at least 2 points to fit any curve
    if n < 2:
        return None
    
    # Determine polynomial degree based on number of data points
    # Follows the logic from ATAR_CALC.md:
    # - 2-3 points: fit a line (degree 1)
    # - 4-7 points: fit a cubic (degree 3)
    # - 8+ points: fit a quartic (degree 4)
    if n < 4:
        degree = max(1, n - 1)  # At least degree 1, at most n-1
    elif n < 8:
        degree = 3
    else:
        degree = 4
    
    # Prepare training data: X is HSC marks, y is scaled marks
    X = np.array([p[0] for p in data_points]).reshape(-1, 1)
    y = np.array([p[1] for p in data_points])
    
    # Create a pipeline that expands features to polynomial terms then fits linear model
    model = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        LinearRegression()
    )
    
    # Train on the anchor points
    model.fit(X, y)
    
    # Cache for future use
    _POLYNOMIAL_MODELS[subject_name] = model
    
    return model
```

**Key points**:
- Uses the cache dictionary `_POLYNOMIAL_MODELS` defined at module level
- Degree selection matches the specification in ATAR_CALC.md
- Returns a fitted pipeline that can be called with `model.predict([[mark]])`
- Returns `None` for unknown subjects (handled by caller)

---

### Step 2: Rewrite `get_scaled_mark()` Function

**File**: `Task_Organiser/atar_data.py`

**Replace** the current `get_scaled_mark()` with this polynomial-based version:

```python
def get_scaled_mark(subject_name: str, hsc_mark: float) -> float:
    """Convert an HSC mark to a scaled mark using polynomial regression.
    
    Uses a fitted polynomial curve through published UAC anchor points.
    Clamps extrapolation at boundaries to avoid unrealistic values.
    
    Three regions are handled differently:
    1. Below minimum anchor: Linear scaling from origin through first anchor
    2. Within data range: Polynomial prediction from fitted model
    3. Above maximum anchor: Capped at highest published scaled mark
    
    Args:
        subject_name: Name of the subject (may be aliased; will be resolved)
        hsc_mark: Raw HSC mark on 0-100 scale
                  (Note: extension marks should already be normalized to 0-100 by caller)
    
    Returns:
        Predicted scaled mark as float, clipped to [0, 100]
    
    Example:
        >>> get_scaled_mark("Physics", 85)
        78.5  # Polynomial prediction
        >>> get_scaled_mark("Physics", 10)
        7.2   # Linear extrapolation from origin to (20, 14.3)
    """
    subject_name = resolve_subject_name(subject_name)
    
    # Unknown subject — return raw mark unchanged
    if subject_name not in SUBJECT_SCALING_POINTS:
        return float(np.clip(hsc_mark, 0, 100))
    
    data_points = sorted(SUBJECT_SCALING_POINTS[subject_name], key=lambda p: p[0])
    
    # Special case: only one anchor point available
    # Use linear scaling: (hsc_mark / anchor_x) * anchor_y
    if len(data_points) == 1:
        x_anchor, y_anchor = data_points[0]
        if x_anchor > 0:
            scaled = (hsc_mark / x_anchor) * y_anchor
        else:
            scaled = 0.0
        return float(np.clip(scaled, 0, 100))
    
    # Get the fitted polynomial model (or None if insufficient data)
    model = get_polynomial_model(subject_name)
    
    # Fallback to linear interpolation if polynomial model unavailable
    # (shouldn't happen in practice, but defensive)
    if model is None:
        xs = [p[0] for p in data_points]
        ys = [p[1] for p in data_points]
        return float(np.clip(np.interp(hsc_mark, xs, ys), 0, 100))
    
    # Extract boundary points for clamping extrapolation
    min_anchor_x, max_anchor_x = data_points[0][0], data_points[-1][0]
    min_anchor_y, max_anchor_y = data_points[0][1], data_points[-1][1]
    
    # ========== HANDLE THREE REGIONS ==========
    
    if hsc_mark <= min_anchor_x:
        # REGION 1: Below minimum anchor
        # Linear scaling from origin (0,0) through first anchor point
        # E.g., Physics first anchor is (20, 14.3)
        #       So HSC 10 scales to: (10 / 20) * 14.3 = 7.15
        if min_anchor_x > 0:
            scaled = (hsc_mark / min_anchor_x) * min_anchor_y
        else:
            scaled = 0.0
    
    elif hsc_mark >= max_anchor_x:
        # REGION 3: Above maximum anchor
        # Cap at the highest published scaled mark to prevent extrapolation spike
        # Polynomial curves can exhibit wild behavior beyond training range
        scaled = max_anchor_y
    
    else:
        # REGION 2: Within training range
        # Use the polynomial model to predict
        scaled = float(model.predict([[hsc_mark]])[0])
    
    # Ensure result is in valid range [0, 100]
    return float(np.clip(scaled, 0, 100))
```

**Key points**:
- Handles three distinct regions with appropriate logic
- Single anchor point case uses linear scaling from origin
- Falls back to linear interpolation if polynomial model is None (defensive)
- Clamps extrapolation above max anchor to prevent wild polynomial behavior
- All return values are clipped to [0, 100]
- Comments explain the reasoning for each region

---

### Step 3: Update Module Docstring

**File**: `Task_Organiser/atar_data.py`

**Update** the module-level docstring to reflect polynomial regression:

```python
"""ATAR scaling and estimation utilities.

This module provides functions to convert HSC marks to scaled marks using
polynomial regression on published UAC scaling anchor points, aggregate the
scaled marks according to NSW ATAR rules, and convert an aggregate score
to an estimated ATAR.

Polynomial Regression Approach
==============================
Each subject's scaling curve is modeled using polynomial regression:
- Polynomial degree chosen based on data density (linear for 2–3 points,
  cubic for 4–7 points, quartic for 8+ points)
- Training data: published (HSC mark, scaled mark) pairs from UAC
- Models are cached to avoid retraining on every prediction
- Boundary handling:
  * Below min anchor: linear extrapolation from origin
  * Within data range: polynomial prediction
  * Above max anchor: capped at highest published scaled mark

This approach provides a smooth curve through anchor points and better
captures the non-linear behavior of UAC scaling (e.g., compression at
high marks in some subjects).

Data Sources
============
Scaling data sourced from:
- hscscalinggraphs.au (2024–2025 curves)
- matrix.edu.au (anchor point verification at HSC 20 and 75)
- UAC published conversion tables (aggregate to ATAR)
"""
```

---

### Step 4: Remove Dead Code

**File**: `Task_Organiser/atar_data.py`

**Action**: Remove any duplicate or unused helper functions. Specifically:
- Check if there are two `get_polynomial_model()` implementations — keep only the new one from Step 1
- Remove any unused imports related to the old implementation
- Verify that all references to polynomial models now use the new function

---

### Step 5: Update Tests

**File**: `tests/test_atar_data.py`

**Add** these new tests to verify polynomial accuracy:

```python
def test_polynomial_fits_anchor_points():
    """Polynomial model should predict anchor points accurately.
    
    Each anchor point in the training data should be predicted with
    minimal error (< 0.1 scaled mark).
    """
    for subject, points in SUBJECT_SCALING_POINTS.items():
        if len(points) < 2:
            continue
        
        for hsc, expected_scaled in points:
            predicted = get_scaled_mark(subject, hsc)
            assert abs(predicted - expected_scaled) < 0.1, (
                f"{subject} at HSC {hsc}: got {predicted}, "
                f"expected {expected_scaled}"
            )


def test_polynomial_smooth_between_points():
    """Polynomial should produce smooth transitions between anchor points.
    
    Check that scaled marks increase monotonically and smoothly
    (no large jumps) for an increasing sequence of HSC marks.
    """
    subject = "Physics"
    hsc_marks = [65, 70, 75, 80, 85]
    scaled = [get_scaled_mark(subject, m) for m in hsc_marks]
    
    # Scaled marks should increase
    for i in range(len(scaled) - 1):
        assert scaled[i + 1] > scaled[i], "Scaled marks should be monotonic"
    
    # Differences should be reasonable (indicates smooth curve)
    for i in range(len(scaled) - 1):
        diff = scaled[i + 1] - scaled[i]
        assert 0 < diff < 10, (
            f"Large jump in scaling detected: "
            f"HSC {hsc_marks[i]} to {hsc_marks[i+1]}, "
            f"scaled diff {diff}"
        )


def test_polynomial_clamps_at_boundaries():
    """Polynomial should not extrapolate wildly beyond data range.
    
    Check that predictions above the maximum anchor are capped
    at the highest published scaled mark.
    """
    subject = "Physics"
    # Physics max anchor is HSC 99 → scaled 100
    
    scaled_100 = get_scaled_mark(subject, 100)
    scaled_99 = get_scaled_mark(subject, 99)
    scaled_110 = get_scaled_mark(subject, 110)
    
    # All should be capped at or near max
    assert scaled_100 <= 100.5, "HSC 100 should not exceed max scaled"
    assert scaled_100 == scaled_99, "HSC 100 should be capped"
    assert scaled_110 == scaled_99, "HSC 110 should be capped at max"


def test_polynomial_below_min_anchor_linear():
    """Below minimum anchor, scaling should be linear from origin.
    
    E.g., if first anchor is (20, 14.3), then HSC 10 should scale
    to approximately (10/20) * 14.3 = 7.15
    """
    subject = "Physics"
    # Physics first anchor is (20, 14.3)
    
    scaled_10 = get_scaled_mark(subject, 10)
    expected = (10 / 20) * 14.3
    
    assert abs(scaled_10 - expected) < 0.2, (
        f"Below-min linear extrapolation: got {scaled_10}, "
        f"expected ~{expected}"
    )


def test_polynomial_model_caching():
    """Polynomial models should be cached to avoid retraining.
    
    Calling get_polynomial_model() twice for the same subject
    should return the same object from the cache.
    """
    from atar_data import get_polynomial_model, _POLYNOMIAL_MODELS
    
    subject = "Physics"
    model1 = get_polynomial_model(subject)
    model2 = get_polynomial_model(subject)
    
    # Should be identical objects (cached)
    assert model1 is model2, "Models should be cached"
    assert subject in _POLYNOMIAL_MODELS, "Subject should be in cache"


def test_polynomial_degree_selection():
    """Polynomial degree should be chosen correctly based on data points.
    
    - 2–3 points: degree 1 (linear)
    - 4–7 points: degree 3 (cubic)
    - 8+ points: degree 4 (quartic)
    """
    from atar_data import get_polynomial_model
    
    # Test a subject with few points (should be linear)
    subject_few = "Drama"  # Has 2 points
    model_few = get_polynomial_model(subject_few)
    if model_few is not None:
        # Pipeline structure: [PolynomialFeatures, LinearRegression]
        poly_features = model_few.steps[0][1]
        assert poly_features.degree == 1, "2 points should use linear (degree 1)"
    
    # Test a subject with many points (should be quartic)
    subject_many = "English Advanced"  # Has 10 points
    model_many = get_polynomial_model(subject_many)
    if model_many is not None:
        poly_features = model_many.steps[0][1]
        assert poly_features.degree == 4, "10 points should use quartic (degree 4)"


def test_polynomial_vs_linear_interpolation():
    """Polynomial and linear should be similar but polynomial smoother.
    
    This test demonstrates the difference but does not fail on large diffs,
    as both approaches are valid for different reasons.
    """
    # Physics at HSC 75 is an anchor (64→48, 75→64, 84→78)
    scaled_75 = get_scaled_mark("Physics", 75)
    
    # Should be close to published anchor
    assert abs(scaled_75 - 64.0) < 1.0, "Should match anchor point closely"
    
    # Prediction at HSC 70 (between anchors)
    scaled_70 = get_scaled_mark("Physics", 70)
    
    # Linear interp: (70-64)/(75-64) * (64-48) + 48 = 56.7
    # Polynomial will likely be higher: ~59.2 (captures curve)
    assert 55 < scaled_70 < 62, "Should be reasonable prediction between anchors"
```

**Key points**:
- Test that polynomial predictions match anchor points
- Test smooth transitions (no jumps)
- Test boundary clamping at max
- Test linear extrapolation below min
- Test caching mechanism
- Test degree selection logic
- All tests should pass with the new polynomial implementation

---

## Validation Checklist

Before considering this complete, verify:

- [ ] `get_polynomial_model()` is implemented and properly caches models
- [ ] `get_scaled_mark()` uses polynomial for within-range, linear extrapolation below, and capping above
- [ ] All new tests in `test_atar_data.py` pass
- [ ] All existing tests still pass (backward compatible)
- [ ] Module docstring is updated to describe polynomial regression
- [ ] No dead code remains (old polynomial function removed if duplicate)
- [ ] All imports are correct (`make_pipeline`, `PolynomialFeatures`, `LinearRegression`)
- [ ] Polynomial degree selection matches specification: 1 for <4 points, 3 for 4–7, 4 for 8+
- [ ] No `KeyError` or `IndexError` when calling `get_scaled_mark()` with edge cases:
  - Single anchor point subject (e.g., "Senior Science")
  - Unknown subject
  - Mark = 0, 50, 100, 110, -10
- [ ] Cache is memory-efficient (no memory leaks from storing too many models)
- [ ] Documentation strings are clear and include examples

---

## Rollback Plan

If issues arise:

1. Revert to the original `get_scaled_mark()` that uses `np.interp()`
2. Comment out or remove the new `get_polynomial_model()` function
3. The linear interpolation approach is simpler and already proven to work

---

## Notes for Implementer

1. **Understand the math**: Polynomial regression fits a degree-n polynomial through the anchor points. Use `make_pipeline()` to combine `PolynomialFeatures()` (expands features to polynomial terms) and `LinearRegression()` (fits coefficients).

2. **Why three regions?**
   - **Below min**: Polynomial extrapolation can be wild; linear from origin is safer
   - **Within range**: Polynomial is stable and smooth
   - **Above max**: Polynomial can spike; capping prevents nonsense values

3. **Cache pattern**: The `_POLYNOMIAL_MODELS` dict is initialized at module level. Models are cached so subsequent calls for the same subject don't retrain.

4. **Testing**: Run `pytest tests/test_atar_data.py -v` to verify all tests pass.

---

## Files Modified

| File | Change | Impact |
|------|--------|--------|
| `Task_Organiser/atar_data.py` | Implement polynomial `get_polynomial_model()`, rewrite `get_scaled_mark()` | Core functionality |
| `tests/test_atar_data.py` | Add 6 new test functions | Validation |
| Documentation | Update module docstring | Reference |

---

## Success Criteria

✅ All tests pass (existing + new)  
✅ Polynomial predictions match anchor points (error < 0.1)  
✅ Scaling is smooth between points (no jumps)  
✅ Extrapolation is handled safely (linear below, capped above)  
✅ Code is well-commented and clear  
✅ No performance regression (caching ensures speed)