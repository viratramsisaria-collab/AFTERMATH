
"""Procedural neon megacity renderer for AFTERMATH."""

from typing import Any
import math

import pydeck as pdk
import streamlit as st

from core.constants import CITY_CENTER_LAT, CITY_CENTER_LON


MAP_STYLE = (
    "https://basemaps.cartocdn.com/gl/"
    "dark-matter-gl-style/style.json"
)

NEON_CYAN = [35, 225, 245, 255]
NEON_BLUE = [45, 125, 255, 255]
NEON_PURPLE = [155, 75, 255, 255]
NEON_GREEN = [40, 245, 180, 255]
NEON_RED = [255, 65, 100, 255]


def _rgb(color: Any, fallback=(70, 155, 190)) -> list[int]:
    """Convert a supplied building color to RGBA."""

    if isinstance(color, (tuple, list)) and len(color) >= 3:
        try:
            return [
                max(0, min(255, int(float(value))))
                for value in color[:3]
            ] + [255]
        except (TypeError, ValueError):
            pass

    if isinstance(color, str):
        value = color.strip().lstrip("#")

        if len(value) == 3:
            value = "".join(char * 2 for char in value)

        if len(value) == 6:
            try:
                return [
                    int(value[index:index + 2], 16)
                    for index in (0, 2, 4)
                ] + [255]
            except ValueError:
                pass

    return list(fallback) + [255]


def _coordinates_to_lon_lat(coordinate: Any) -> list[float] | None:
    """Convert coordinates into [longitude, latitude]."""

    if isinstance(coordinate, dict):
        latitude = coordinate.get("latitude", coordinate.get("lat"))
        longitude = coordinate.get("longitude", coordinate.get("lon"))

        if latitude is not None and longitude is not None:
            return [float(longitude), float(latitude)]

        return None

    if isinstance(coordinate, (tuple, list)) and len(coordinate) >= 2:
        latitude, longitude = coordinate[0], coordinate[1]

        try:
            return [float(longitude), float(latitude)]
        except (TypeError, ValueError):
            return None

    return None


def _building_shape(
    longitude: float,
    latitude: float,
    area_m2: float,
    building_id: str,
) -> list[list[float]]:
    """Create varied procedural architectural footprints."""

    area = max(180.0, float(area_m2))

    width = math.sqrt(area * 1.4)
    depth = math.sqrt(area / 1.4)

    seed = sum(ord(char) for char in str(building_id))
    shape_type = seed % 5

    # Local footprint coordinates, in metres.
    if shape_type == 0:
        # Chamfered tower.
        points = [
            (-0.38, -0.5), (0.38, -0.5),
            (0.5, -0.35), (0.5, 0.35),
            (0.38, 0.5), (-0.38, 0.5),
            (-0.5, 0.35), (-0.5, -0.35),
        ]

    elif shape_type == 1:
        # L-shaped building.
        points = [
            (-0.5, -0.5), (0.5, -0.5),
            (0.5, -0.22), (-0.12, -0.22),
            (-0.12, 0.5), (-0.5, 0.5),
        ]

    elif shape_type == 2:
        # Stepped footprint.
        points = [
            (-0.5, -0.5), (0.5, -0.5),
            (0.5, 0.5), (0.22, 0.5),
            (0.22, -0.12), (-0.5, -0.12),
        ]

    elif shape_type == 3:
        # Octagonal tower.
        points = [
            (-0.3, -0.5), (0.3, -0.5),
            (0.5, -0.3), (0.5, 0.3),
            (0.3, 0.5), (-0.3, 0.5),
            (-0.5, 0.3), (-0.5, -0.3),
        ]

    else:
        # Rectangular high-rise.
        points = [
            (-0.5, -0.5), (0.5, -0.5),
            (0.5, 0.5), (-0.5, 0.5),
        ]

    # Rotate each building for a less repetitive skyline.
    angle = math.radians((seed % 4) * 15)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    polygon = []

    for x, y in points:
        x *= width
        y *= depth

        rotated_x = x * cos_a - y * sin_a
        rotated_y = x * sin_a + y * cos_a

        point_lat = latitude + rotated_y / 111_320
        point_lon = longitude + (
            rotated_x /
            (111_320 * max(0.1, math.cos(math.radians(latitude))))
        )

        polygon.append([point_lon, point_lat])

    polygon.append(polygon[0])

    return polygon


def _building_data(city) -> list[dict]:
    """Prepare procedurally modelled buildings."""

    buildings = []

    for building in city.buildings:
        height = max(8.0, float(building.height_m))

        base_color = _rgb(building.color)
        seed = sum(ord(char) for char in str(building.id))

        if not building.operational:
            base_color = [75, 85, 100, 255]
            edge_color = [110, 115, 130, 255]
        else:
            edge_color = (
                NEON_PURPLE if seed % 5 == 0
                else NEON_CYAN if seed % 3 == 0
                else NEON_BLUE
            )

        buildings.append({
            "name": building.name,
            "building_type": (
                str(building.building_type)
                .replace("_", " ")
                .title()
            ),
            "polygon": _building_shape(
                float(building.longitude),
                float(building.latitude),
                float(building.footprint_m2),
                str(building.id),
            ),
            "height": height,
            "height_label": f"{height:.0f} m",
            "color": base_color,
            "edge_color": edge_color,
            "operational": bool(building.operational),
        })

    return buildings


def _road_data(city) -> list[dict]:
    """Prepare the road network with neon traffic colours."""

    roads = []

    for road in city.roads:
        path = [
            converted
            for coordinate in road.coordinates
            if (
                converted := _coordinates_to_lon_lat(coordinate)
            ) is not None
        ]

        if len(path) < 2:
            continue

        congestion = max(
            0.0,
            min(100.0, float(road.congestion)),
        )

        if not road.operational:
            color = [85, 95, 110, 180]
        elif congestion >= 75:
            color = NEON_RED
        elif congestion >= 45:
            color = [255, 170, 55, 255]
        else:
            color = NEON_CYAN

        roads.append({
            "name": road.name,
            "path": path,
            "color": color,
            "congestion": congestion,
            "road_type": str(road.road_type).title(),
            "width": 17,
            "core_width": 5,
            "operational": bool(road.operational),
        })

    return roads


def _district_data(city) -> list[dict]:
    """Prepare district centres and neon labels."""

    districts = []

    for district in city.districts:
        districts.append({
            "name": district.name,
            "position": [
                float(district.center_lon),
                float(district.center_lat),
            ],
            "population": int(district.population),
            "happiness": float(district.happiness),
            "color": NEON_GREEN,
        })

    return districts


def build_city_deck(city) -> pdk.Deck:
    """Build the interactive procedural 3D neon city."""

    buildings = _building_data(city)
    roads = _road_data(city)
    districts = _district_data(city)

    if districts:
        center_lat = sum(
            item["position"][1] for item in districts
        ) / len(districts)

        center_lon = sum(
            item["position"][0] for item in districts
        ) / len(districts)
    else:
        center_lat = CITY_CENTER_LAT
        center_lon = CITY_CENTER_LON

    layers = [
        # Wide translucent road underlay.
        pdk.Layer(
            "PathLayer",
            id="neon-road-glow",
            data=roads,
            get_path="path",
            get_color="color",
            get_width="width",
            width_units="meters",
            width_min_pixels=5,
            pickable=False,
        ),

        # Bright road centre lines.
        pdk.Layer(
            "PathLayer",
            id="neon-road-core",
            data=roads,
            get_path="path",
            get_color="color",
            get_width="core_width",
            width_units="meters",
            width_min_pixels=2,
            pickable=True,
            auto_highlight=True,
        ),

        # Main extruded architectural geometry.
        pdk.Layer(
            "PolygonLayer",
            id="neon-building-geometry",
            data=buildings,
            get_polygon="polygon",
            get_elevation="height",
            get_fill_color="color",
            get_line_color="edge_color",
            get_line_width=2,
            line_width_min_pixels=1.5,
            line_width_units="pixels",
            stroked=True,
            filled=True,
            extruded=True,
            wireframe=True,
            elevation_scale=1,
            pickable=True,
            auto_highlight=True,
        ),

        # District centre indicators.
        pdk.Layer(
            "ScatterplotLayer",
            id="district-neon-markers",
            data=districts,
            get_position="position",
            get_fill_color="color",
            get_radius=35,
            radius_units="meters",
            stroked=True,
            get_line_color=[180, 255, 230, 255],
            line_width_min_pixels=2,
            pickable=True,
            auto_highlight=True,
        ),

        # District labels.
        pdk.Layer(
            "TextLayer",
            id="district-labels",
            data=districts,
            get_position="position",
            get_text="name",
            get_size=15,
            get_color=[160, 255, 240, 255],
            get_angle=0,
            get_text_anchor='"middle"',
            get_alignment_baseline='"bottom"',
            billboard=True,
            pickable=False,
        ),
    ]

    tooltip = {
        "html": """
            <div style="
                padding: 12px 14px;
                min-width: 190px;
                background: #071522;
                color: #e8faff;
                border: 1px solid #27e1f5;
                border-radius: 8px;
                box-shadow: 0 0 18px rgba(39, 225, 245, 0.25);
            ">
                <div style="
                    font-weight: 800;
                    font-size: 14px;
                    margin-bottom: 7px;
                    color: #ffffff;
                ">{name}</div>

                <div style="
                    color: #27e1f5;
                    font-size: 11px;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    margin-bottom: 9px;
                ">{building_type}</div>

                <div>Height: <b>{height_label}</b></div>
                <div>Status: <b>{operational}</b></div>
            </div>
        """,
        "style": {
            "backgroundColor": "transparent",
            "color": "#e8faff",
            "fontSize": "12px",
            "border": "none",
            "padding": "0",
        },
    }

    return pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=13,
            pitch=62,
            bearing=-25,
        ),
        map_style=MAP_STYLE,
        tooltip=tooltip, # type: ignore[arg-type]
    )


def render_city_map(
    city,
    height: int = 720,
    key: str = "aftermath_city_map",
) -> None:
    """Render the interactive AFTERMATH megacity."""

    deck = build_city_deck(city)

    st.pydeck_chart(
        deck,
        height=height,
        use_container_width=True,
        key=key,
    )