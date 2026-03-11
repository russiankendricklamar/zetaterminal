"""
Types and constants for bond pricing module.
Day count conventions, base URLs, and shared enumerations.
"""

from enum import Enum

BASE_ISS = "https://iss.moex.com/iss"


class DayCountConvention(Enum):
    """Базисы расчета дней в году"""
    ACTUAL_365F = "Actual/365F"  # Fixed 365
    ACTUAL_360 = "Actual/360"
    ACTUAL_ACTUAL_ISDA = "Actual/Actual (ISDA)"
    THIRTY_360_US = "30/360 (US)"  # US Municipal Bond Basis
    THIRTY_E_360_ISDA = "30E/360 (ISDA)"  # German
    THIRTY_E_360 = "30E/360"  # Eurobond Basis
    ACTUAL_ACTUAL_ISMA = "Actual/Actual (ISMA)"
