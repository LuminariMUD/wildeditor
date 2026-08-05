"""Focused coverage for the complete LuminariMUD region type contract."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from src.config.config_database import get_db
from src.main import app
from src.schemas.region import (
    REGION_ALTITUDE_LANE,
    REGION_BATHYMETRIC,
    REGION_SKY_ISLAND,
    RegionCreate,
    RegionListResponse,
    RegionUpdate,
    get_region_type_name,
)


VESSEL_REGION_TYPES = [
    (REGION_BATHYMETRIC, "Bathymetric", 96),
    (REGION_ALTITUDE_LANE, "Altitude Lane", 100),
    (REGION_SKY_ISLAND, "Sky Island", 200),
]


@pytest.mark.unit
@pytest.mark.parametrize(("region_type", "type_name", "threshold"), VESSEL_REGION_TYPES)
def test_vessel_region_types_validate(region_type, type_name, threshold):
    response = RegionListResponse(
        vnum=7_100_000 + region_type,
        zone_vnum=10_000,
        name=f"Test {type_name}",
        region_type=region_type,
        region_props=threshold,
    )

    assert response.region_type == region_type
    assert response.region_props == threshold
    assert get_region_type_name(region_type) == type_name


@pytest.mark.unit
def test_unknown_region_types_are_rejected_for_create_and_update():
    with pytest.raises(ValidationError):
        RegionCreate(
            vnum=7_100_099,
            zone_vnum=10_000,
            name="Unsupported Region",
            region_type=8,
            coordinates=[],
        )

    with pytest.raises(ValidationError):
        RegionUpdate(region_type=8)


@pytest.mark.unit
def test_region_list_endpoint_serializes_vessel_region_types(test_client):
    rows = [
        SimpleNamespace(
            vnum=7_100_000 + region_type,
            zone_vnum=10_000,
            name=f"Test {type_name}",
            region_type=region_type,
            region_props=threshold,
            region_polygon=None,
            region_reset_data="",
            region_reset_time=None,
            region_description=None,
            description_style=None,
            description_length=None,
            is_approved=False,
        )
        for region_type, type_name, threshold in VESSEL_REGION_TYPES
    ]
    fake_db = Mock()
    fake_db.query.return_value.all.return_value = rows
    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        response = test_client.get("/api/regions")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert [region["region_type"] for region in response.json()] == [5, 6, 7]
    assert [region["region_type_name"] for region in response.json()] == [
        "Bathymetric",
        "Altitude Lane",
        "Sky Island",
    ]


@pytest.mark.unit
def test_region_types_endpoint_advertises_vessel_types(test_client):
    response = test_client.get("/api/regions/types")

    assert response.status_code == 200
    region_types = response.json()["region_types"]
    assert region_types["5"]["region_props_usage"].startswith("Minimum natural depth")
    assert region_types["6"]["region_props_usage"] == "Minimum vessel Z coordinate"
    assert region_types["7"]["region_props_usage"] == "Minimum vessel Z coordinate"
