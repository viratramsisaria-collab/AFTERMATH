
from disasters.models import DisasterType


DISASTER_REGISTRY = {
    DisasterType.EARTHQUAKE: {
        "title": "Seismic Emergency",
        "description": "Earthquake activity threatens urban infrastructure.",
        "measurement": "Moment Magnitude and Modified Mercalli Intensity",
        "response_window_days": 10,
    },
    DisasterType.FLOOD: {
        "title": "Urban Flood Emergency",
        "description": "Floodwater threatens residents and critical infrastructure.",
        "measurement": "Flood Hazard Index",
        "response_window_days": 10,
    },
    DisasterType.CYCLONE: {
        "title": "Cyclonic Emergency",
        "description": "Extreme winds and storm surge threaten the city.",
        "measurement": "Saffir-Simpson Wind Scale",
        "response_window_days": 10,
    },
    DisasterType.HEATWAVE: {
        "title": "Extreme Heat Emergency",
        "description": "Dangerous heat conditions threaten public health and energy supply.",
        "measurement": "Heat Index",
        "response_window_days": 10,
    },
    DisasterType.WILDFIRE: {
        "title": "Wildfire Emergency",
        "description": "Uncontrolled fire threatens districts and surrounding areas.",
        "measurement": "Fire Weather Index",
        "response_window_days": 10,
    },
    DisasterType.DROUGHT: {
        "title": "Water Security Emergency",
        "description": "Prolonged precipitation deficits threaten the city's water supply.",
        "measurement": "Standardized Precipitation Index",
        "response_window_days": 10,
    },
    DisasterType.INDUSTRIAL_ACCIDENT: {
        "title": "Industrial Hazard Emergency",
        "description": "An industrial incident threatens nearby residents and infrastructure.",
        "measurement": "Industrial Exposure Risk Index",
        "response_window_days": 10,
    },
}
