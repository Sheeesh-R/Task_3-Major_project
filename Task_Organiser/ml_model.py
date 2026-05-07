"""
ATAR Prediction Module
======================
Legacy module - now uses atar_data.py for accurate calculations.

This module is kept for backward compatibility but delegates to the new
atar_data module which uses real UAC scaling data and proper
polynomial regression models.
"""

from .atar_data import get_scaled_mark, calculate_atar_estimate

# Re-export functions for backward compatibility
__all__ = ['get_scaled_mark', 'calculate_aggregate']

def calculate_aggregate(subject_scaled_marks: list[dict]) -> float:
    """
    Legacy function - use calculate_atar_estimate from atar_data instead.
    
    This function is kept for backward compatibility but should be replaced
    with calculate_atar_estimate for new development.
    """
    # Convert to format expected by new function
    subjects = []
    for item in subject_scaled_marks:
        # Handle both dict and SQLite Row objects
        if hasattr(item, 'get'):
            # It's a dict
            subject_name = item.get('subject_name', 'Unknown')
            hsc_mark = item.get('hsc_mark', item.get('scaled_mark', 0))
            units = item.get('units', 2)
        else:
            # It's a SQLite Row object
            subject_name = item['subject_name'] if 'subject_name' in item.keys() else 'Unknown'
            hsc_mark = item['hsc_mark'] if 'hsc_mark' in item.keys() else (item['scaled_mark'] if 'scaled_mark' in item.keys() else 0)
            units = item['units'] if 'units' in item.keys() else 2
        
        subjects.append({
            'subject_name': subject_name,
            'hsc_mark': hsc_mark,
            'units': units
        })
    
    result = calculate_atar_estimate(subjects)
    return result['atar']
