
"""AFTERMATH application and simulation constants."""

# ---------------------------------------------------------
# BRANDING
# ---------------------------------------------------------

APP_NAME = "AFTERMATH"
APP_TAGLINE = "THE FUTURE IS YOURS TO DECIDE."

APP_DESCRIPTION = (
    "An interactive AI-powered city simulation where "
    "human judgement shapes the future."
)

APP_VERSION = "0.1.0"

# ---------------------------------------------------------
# CITY
# ---------------------------------------------------------

CITY_NAME = "NOVA YORK"

CITY_CENTER_LAT = 40.754
CITY_CENTER_LON = -73.985

CITY_DEFAULT_SEED = 42

CITY_INITIAL_BUDGET = 2_500_000_000

CITY_MAX_POPULATION = 250_000

# ---------------------------------------------------------
# VISUAL IDENTITY
# ---------------------------------------------------------

CITY_PALETTE = {
    "background": "#080F1D",
    "surface": "#101D2D",
    "surface_light": "#172B40",
    "primary": "#27C9D7",
    "secondary": "#8D9CAB",
    "accent": "#B9DCA8",
    "warning": "#E6B85C",
    "danger": "#E46D73",
    "success": "#45B99A",
    "text": "#E8F0F7",
    "muted": "#8295A8",
}

BUILDING_COLORS = {
    "skyscraper": [90, 165, 190],
    "residential": [105, 135, 165],
    "commercial": [70, 155, 180],
    "hospital": [70, 190, 165],
    "education": [145, 155, 195],
    "industrial": [125, 130, 145],
    "cultural": [175, 145, 190],
    "civic": [120, 175, 185],
    "park": [90, 165, 115],
    "transport": [180, 175, 145],
}

# ---------------------------------------------------------
# DISTRICT BLUEPRINTS
# name, type, latitude offset, longitude offset, population
# ---------------------------------------------------------

DISTRICT_BLUEPRINTS = [
    ("Crown District", "financial", 0.000, 0.000, 18500),
    ("Hudson Heights", "residential", 0.009, -0.009, 14200),
    ("Eastline", "commercial", 0.004, 0.010, 16800),
    ("Verdant Quarter", "green", 0.013, 0.004, 11200),
    ("Southbank", "waterfront", -0.011, -0.005, 13800),
    ("Westhaven", "residential", -0.006, -0.014, 15900),
    ("Innovation Mile", "innovation", 0.009, 0.001, 12400),
    ("Old Quarter", "cultural", -0.007, 0.009, 9800),
    ("Civic Centre", "civic", 0.002, -0.004, 11500),
    ("Harbor Point", "industrial", -0.015, 0.011, 8700),
]

# ---------------------------------------------------------
# BUILDING GENERATION
# ---------------------------------------------------------

BUILDING_TYPES_BY_DISTRICT = {
    "financial": ["skyscraper", "commercial", "civic"],
    "residential": ["residential", "commercial", "education"],
    "commercial": ["commercial", "skyscraper", "residential"],
    "green": ["residential", "education", "cultural"],
    "waterfront": ["commercial", "residential", "cultural"],
    "innovation": ["skyscraper", "commercial", "education"],
    "cultural": ["cultural", "education", "residential"],
    "civic": ["civic", "hospital", "education"],
    "industrial": ["industrial", "transport", "commercial"],
}

BUILDING_HEIGHT_RANGES = {
    "financial": (90, 310),
    "residential": (25, 115),
    "commercial": (35, 170),
    "green": (20, 90),
    "waterfront": (30, 150),
    "innovation": (55, 230),
    "cultural": (20, 85),
    "civic": (35, 125),
    "industrial": (15, 65),
}

BUILDINGS_PER_DISTRICT = 9

# ---------------------------------------------------------
# SIMULATION
# ---------------------------------------------------------

SIMULATION_TICK_SECONDS = 1.0

SIMULATION_INITIAL_DAY = 1

SIMULATION_MAX_DAYS = 365

SIMULATION_MAX_SPEED = 10

# ---------------------------------------------------------
# CITY METRIC BOUNDS
# ---------------------------------------------------------

METRIC_MIN = 0.0
METRIC_MAX = 100.0

# ---------------------------------------------------------
# HUMAN JUDGEMENT
# ---------------------------------------------------------

HUMAN_VALUES = [
    "fairness",
    "dignity",
    "accessibility",
    "safety",
    "wellbeing",
    "opportunity",
    "sustainability",
]

JUDGEMENT_WEIGHTS = {
    "fairness": 0.18,
    "dignity": 0.15,
    "accessibility": 0.16,
    "safety": 0.15,
    "wellbeing": 0.15,
    "opportunity": 0.10,
    "sustainability": 0.11,
}

# ---------------------------------------------------------
# GAMEPLAY
# ---------------------------------------------------------

INITIAL_CITY_RESOURCES = {
    "energy": 83.0,
    "water": 78.0,
    "healthcare": 70.0,
    "transport": 68.0,
    "budget": CITY_INITIAL_BUDGET,
}
