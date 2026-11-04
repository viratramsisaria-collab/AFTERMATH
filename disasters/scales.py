
from __future__ import annotations

from disasters.models import ScaleAssessment


def _clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def _require_nonnegative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


def _category(score: float) -> str:
    if score < 15:
        return "Minor"
    if score < 35:
        return "Moderate"
    if score < 55:
        return "Major"
    if score < 75:
        return "Severe"
    return "Catastrophic"


def earthquake_assessment(
    magnitude_mw: float,
    depth_km: float,
    intensity_mmi: int | None = None,
) -> ScaleAssessment:
    if not 0 <= magnitude_mw <= 10:
        raise ValueError("Magnitude must be between 0 and 10.")

    _require_nonnegative("Depth", depth_km)

    if intensity_mmi is not None and not 1 <= intensity_mmi <= 12:
        raise ValueError("MMI intensity must be between I and XII (1-12).")

    if intensity_mmi is not None:
        score = ((intensity_mmi - 1) / 11) * 100
        category = f"MMI Intensity {intensity_mmi}"
        scale = "Modified Mercalli Intensity"
        value = float(intensity_mmi)
        unit = "MMI"
    else:
        score = _clamp(((magnitude_mw - 3) / 6) * 100)
        category = _category(score)
        scale = "Moment Magnitude (Mw)"
        value = magnitude_mw
        unit = "Mw"

    return ScaleAssessment(
        scale_name=scale,
        measured_value=value,
        unit=unit,
        category=category,
        severity_score=round(score, 2),
        description=(
            "Earthquake size and/or local shaking intensity. "
            "Actual damage also depends on depth, distance, soil "
            "conditions and building resilience."
        ),
        secondary_values={
            "magnitude_mw": magnitude_mw,
            "depth_km": depth_km,
            "mmi": intensity_mmi if intensity_mmi is not None else "not supplied",
        },
    )


def flood_assessment(
    water_depth_m: float,
    water_velocity_ms: float,
    duration_hours: float,
) -> ScaleAssessment:
    for name, value in (
        ("Water depth", water_depth_m),
        ("Water velocity", water_velocity_ms),
        ("Duration", duration_hours),
    ):
        _require_nonnegative(name, value)

    depth_score = _clamp((water_depth_m / 3.0) * 100)
    velocity_score = _clamp((water_velocity_ms / 3.0) * 100)
    duration_score = _clamp((duration_hours / 72) * 100)

    score = (
        depth_score * 0.50
        + velocity_score * 0.30
        + duration_score * 0.20
    )

    return ScaleAssessment(
        scale_name="Flood Hazard Index",
        measured_value=round(score, 2),
        unit="index",
        category=_category(score),
        severity_score=round(score, 2),
        description=(
            "Game hazard index combining inundation depth, "
            "flow velocity and exposure duration."
        ),
        secondary_values={
            "water_depth_m": water_depth_m,
            "water_velocity_ms": water_velocity_ms,
            "duration_hours": duration_hours,
        },
    )


def cyclone_assessment(
    sustained_wind_kmh: float,
    storm_surge_m: float,
) -> ScaleAssessment:
    _require_nonnegative("Wind speed", sustained_wind_kmh)
    _require_nonnegative("Storm surge", storm_surge_m)

    mph = sustained_wind_kmh / 1.609344

    if mph < 74:
        category = "Below Category 1"
        wind_score = _clamp((mph / 74) * 30)
    elif mph < 96:
        category, wind_score = "Category 1", 35
    elif mph < 111:
        category, wind_score = "Category 2", 48
    elif mph < 130:
        category, wind_score = "Category 3", 63
    elif mph < 157:
        category, wind_score = "Category 4", 80
    else:
        category, wind_score = "Category 5", 100

    surge_score = _clamp((storm_surge_m / 6) * 100)
    score = _clamp(wind_score * 0.75 + surge_score * 0.25)

    return ScaleAssessment(
        scale_name="Saffir-Simpson Wind Scale",
        measured_value=round(mph, 2),
        unit="mph",
        category=category,
        severity_score=round(score, 2),
        description=(
            "Wind category combined with a separate storm-surge "
            "hazard contribution for gameplay."
        ),
        secondary_values={
            "wind_speed_kmh": sustained_wind_kmh,
            "storm_surge_m": storm_surge_m,
        },
    )


def heatwave_assessment(
    heat_index_c: float,
    duration_hours: float,
) -> ScaleAssessment:
    _require_nonnegative("Duration", duration_hours)

    if heat_index_c < -20 or heat_index_c > 80:
        raise ValueError("Heat index must be between -20 and 80 Celsius.")

    if heat_index_c < 27:
        category, base = "Low", 5
    elif heat_index_c < 32:
        category, base = "Caution", 20
    elif heat_index_c < 41:
        category, base = "Extreme Caution", 45
    elif heat_index_c < 54:
        category, base = "Danger", 70
    else:
        category, base = "Extreme Danger", 90

    duration_factor = _clamp(duration_hours / 72, 0.25, 1.5)
    score = _clamp(base * duration_factor)

    return ScaleAssessment(
        scale_name="Heat Index",
        measured_value=heat_index_c,
        unit="°C",
        category=category,
        severity_score=round(score, 2),
        description=(
            "Heat stress severity combined with exposure duration. "
            "The supplied heat index must already account for humidity."
        ),
        secondary_values={"duration_hours": duration_hours},
    )


def wildfire_assessment(
    fire_weather_index: float,
    wind_speed_kmh: float,
) -> ScaleAssessment:
    _require_nonnegative("Fire Weather Index", fire_weather_index)
    _require_nonnegative("Wind speed", wind_speed_kmh)

    if fire_weather_index < 5:
        category = "Low"
    elif fire_weather_index < 10:
        category = "Moderate"
    elif fire_weather_index < 20:
        category = "High"
    elif fire_weather_index < 30:
        category = "Very High"
    else:
        category = "Extreme"

    base_score = _clamp((fire_weather_index / 50) * 100)
    wind_factor = _clamp(wind_speed_kmh / 100, 0, 1)
    score = _clamp(base_score * 0.80 + wind_factor * 20)

    return ScaleAssessment(
        scale_name="Fire Weather Index (FWI)",
        measured_value=fire_weather_index,
        unit="FWI",
        category=category,
        severity_score=round(score, 2),
        description=(
            "Fire-weather danger indicator combined with wind influence "
            "for the game's spread-risk model."
        ),
        secondary_values={"wind_speed_kmh": wind_speed_kmh},
    )


def drought_assessment(spi_value: float) -> ScaleAssessment:
    if not -5 <= spi_value <= 5:
        raise ValueError("SPI must be between -5 and 5.")

    if spi_value > -0.5:
        category, score = "No significant drought", 0
    elif spi_value > -0.8:
        category, score = "Abnormally Dry", 15
    elif spi_value > -1.3:
        category, score = "Moderate Drought", 35
    elif spi_value > -1.6:
        category, score = "Severe Drought", 55
    elif spi_value > -2:
        category, score = "Extreme Drought", 75
    else:
        category, score = "Exceptional Drought", 95

    return ScaleAssessment(
        scale_name="Standardized Precipitation Index (SPI)",
        measured_value=spi_value,
        unit="SPI",
        category=category,
        severity_score=float(score),
        description=(
            "Precipitation anomaly indicator. Negative values indicate "
            "drier-than-normal conditions."
        ),
    )


def industrial_accident_assessment(
    exposure_index: float,
    exposed_population: int,
    duration_hours: float,
) -> ScaleAssessment:
    if not 0 <= exposure_index <= 100:
        raise ValueError("Exposure index must be between 0 and 100.")

    if exposed_population < 0:
        raise ValueError("Exposed population cannot be negative.")

    _require_nonnegative("Exposure duration", duration_hours)

    duration_factor = _clamp(duration_hours / 24, 0.25, 2)
    population_factor = _clamp(exposed_population / 10000, 0.25, 1.5)

    score = _clamp(
        exposure_index * 0.65
        + duration_factor * 15
        + population_factor * 20
    )

    return ScaleAssessment(
        scale_name="Industrial Exposure Risk Index",
        measured_value=round(exposure_index, 2),
        unit="index",
        category=_category(score),
        severity_score=round(score, 2),
        description=(
            "Game exposure-risk index based on supplied hazard exposure, "
            "population and duration. It is not a toxicological model."
        ),
        secondary_values={
            "exposed_population": exposed_population,
            "duration_hours": duration_hours,
        },
    )