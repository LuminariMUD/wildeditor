"""Disposable compatibility probe against the LuminariMUD MariaDB schema."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient
from sqlalchemy import text


REGION_VNUM = 91_000_001
PATH_VNUM = 91_000_002
CANONICAL_TABLES = {
    "description_templates",
    "hint_usage_log",
    "path_data",
    "path_index",
    "path_types",
    "region_data",
    "region_hints",
    "region_index",
    "region_profiles",
}
EXPECTED_TRIGGERS = {
    "ad_maintain_path_index",
    "ad_maintain_region_index",
    "ai_maintain_path_index",
    "ai_maintain_region_index",
    "au_maintain_path_index",
    "au_maintain_region_index",
    "bi_digitalize_linestring",
    "bu_digitalize_linestring",
}


def require_response(response, expected_status: int):
    assert response.status_code == expected_status, (
        f"{response.request.method} {response.request.url.path} returned "
        f"{response.status_code}: {response.text[:500]}"
    )
    return response


def main() -> None:
    database_url = os.environ.get("MYSQL_DATABASE_URL", "")
    service_key = os.environ.get("WILDEDITOR_BACKEND_SERVICE_KEY", "")
    assert database_url.startswith("mysql+pymysql://")
    assert service_key

    # Import after the disposable database/auth contract is present.
    from src.config.config_database import engine
    from src.main import app

    headers = {"Authorization": f"Bearer {service_key}"}
    client = TestClient(app)

    with engine.connect() as connection:
        tables = {
            row[0]
            for row in connection.execute(
                text(
                    "SELECT TABLE_NAME FROM information_schema.TABLES "
                    "WHERE TABLE_SCHEMA = DATABASE()"
                )
            )
        }
        assert CANONICAL_TABLES <= tables

        triggers = {
            row[0].lower()
            for row in connection.execute(
                text(
                    "SELECT TRIGGER_NAME FROM information_schema.TRIGGERS "
                    "WHERE TRIGGER_SCHEMA = DATABASE()"
                )
            )
        }
        assert EXPECTED_TRIGGERS <= triggers

        spatial_indexes = {
            (row[0], row[1])
            for row in connection.execute(
                text(
                    "SELECT TABLE_NAME, INDEX_NAME FROM information_schema.STATISTICS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND INDEX_TYPE = 'SPATIAL'"
                )
            )
        }
        assert ("region_index", "region_polygon") in spatial_indexes
        assert ("path_index", "path_linestring") in spatial_indexes

    region_body = {
        "vnum": REGION_VNUM,
        "zone_vnum": 10_001,
        "name": "Auth Migration Compatibility Region",
        "region_type": 1,
        "coordinates": [
            {"x": 0, "y": 0},
            {"x": 4, "y": 0},
            {"x": 4, "y": 4},
            {"x": 0, "y": 4},
        ],
        "region_props": 0,
        "region_reset_data": "",
        "region_description": "Disposable MariaDB compatibility fixture.",
    }
    require_response(
        client.post("/api/regions/", json=region_body, headers=headers),
        201,
    )

    path_body = {
        "vnum": PATH_VNUM,
        "zone_vnum": 10_001,
        "name": "Compatibility Path",
        "path_type": 1,
        "coordinates": [{"x": 0, "y": 0}, {"x": 3, "y": 3}],
        "path_props": 11,
    }
    require_response(
        client.post("/api/paths/", json=path_body, headers=headers),
        201,
    )

    point = require_response(
        client.get("/api/points?x=2&y=2&radius=0.1", headers=headers),
        200,
    ).json()
    assert {region["vnum"] for region in point["regions"]} == {REGION_VNUM}
    assert {path["vnum"] for path in point["paths"]} == {PATH_VNUM}

    with engine.connect() as connection:
        spatial = connection.execute(
            text(
                "SELECT ST_AsText(pd.path_linestring), "
                "ST_Equals(pd.path_linestring, pi.path_linestring), "
                "ST_Equals(rd.region_polygon, ri.region_polygon) "
                "FROM path_data pd JOIN path_index pi ON pi.vnum = pd.vnum "
                "JOIN region_data rd ON rd.vnum = :region_vnum "
                "JOIN region_index ri ON ri.vnum = rd.vnum "
                "WHERE pd.vnum = :path_vnum"
            ),
            {"path_vnum": PATH_VNUM, "region_vnum": REGION_VNUM},
        ).one()
        assert spatial[0] == "LINESTRING(0 0,1 1,2 2,3 3)"
        assert bool(spatial[1]) is True
        assert bool(spatial[2]) is True

    require_response(
        client.put(
            f"/api/paths/{PATH_VNUM}",
            json={"coordinates": [{"x": 0, "y": 0}, {"x": 0, "y": 3}]},
            headers=headers,
        ),
        200,
    )
    require_response(
        client.put(
            f"/api/regions/{REGION_VNUM}",
            json={
                "zone_vnum": 10_002,
                "coordinates": [
                    {"x": 0, "y": 0},
                    {"x": 5, "y": 0},
                    {"x": 5, "y": 5},
                    {"x": 0, "y": 5},
                ],
            },
            headers=headers,
        ),
        200,
    )

    hint_body = {
        "hints": [
            {
                "hint_category": "atmosphere",
                "hint_text": "A controlled compatibility hint lingers over the test region.",
                "priority": 8,
                "weather_conditions": ["clear", "rainy"],
            }
        ]
    }
    hint = require_response(
        client.post(
            f"/api/regions/{REGION_VNUM}/hints",
            json=hint_body,
            headers=headers,
        ),
        201,
    ).json()[0]

    profile_body = {
        "overall_theme": "A disposable region used only for schema compatibility proof.",
        "dominant_mood": "controlled",
        "key_characteristics": ["spatial", "temporary"],
        "description_style": "practical",
        "complexity_level": 2,
    }
    require_response(
        client.post(
            f"/api/regions/{REGION_VNUM}/profile",
            json=profile_body,
            headers=headers,
        ),
        200,
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO hint_usage_log "
                "(hint_id, room_vnum, weather_condition, season, time_of_day) "
                "VALUES (:hint_id, 9000001, 'clear', 'summer', 'midday')"
            ),
            {"hint_id": hint["id"]},
        )
        connection.execute(
            text(
                "INSERT INTO description_templates "
                "(region_vnum, template_type, template_text, is_active) "
                "VALUES (:region_vnum, 'intro', 'Compatibility template', TRUE)"
            ),
            {"region_vnum": REGION_VNUM},
        )

    analytics = require_response(
        client.get(
            f"/api/regions/{REGION_VNUM}/hints/analytics",
            headers=headers,
        ),
        200,
    ).json()
    assert analytics["total_hints"] == 1
    assert analytics["profile_exists"] is True
    assert analytics["usage_stats"][0]["usage_count"] == 1
    assert analytics["usage_stats"][0]["unique_rooms"] == 1

    with engine.connect() as connection:
        updated = connection.execute(
            text(
                "SELECT ST_NumPoints(pd.path_linestring), "
                "ST_Equals(pd.path_linestring, pi.path_linestring), "
                "rd.zone_vnum, ri.zone_vnum, "
                "ST_Equals(rd.region_polygon, ri.region_polygon) "
                "FROM path_data pd JOIN path_index pi ON pi.vnum = pd.vnum "
                "JOIN region_data rd ON rd.vnum = :region_vnum "
                "JOIN region_index ri ON ri.vnum = rd.vnum "
                "WHERE pd.vnum = :path_vnum"
            ),
            {"path_vnum": PATH_VNUM, "region_vnum": REGION_VNUM},
        ).one()
        assert updated[0] == 4
        assert bool(updated[1]) is True
        assert updated[2:4] == (10_002, 10_002)
        assert bool(updated[4]) is True

    require_response(
        client.delete(
            f"/api/regions/{REGION_VNUM}/hints/{hint['id']}",
            headers=headers,
        ),
        204,
    )
    with engine.begin() as connection:
        usage_count = connection.execute(
            text("SELECT COUNT(*) FROM hint_usage_log WHERE hint_id = :hint_id"),
            {"hint_id": hint["id"]},
        ).scalar_one()
        assert usage_count == 0
        connection.execute(
            text("DELETE FROM description_templates WHERE region_vnum = :vnum"),
            {"vnum": REGION_VNUM},
        )
        connection.execute(
            text("DELETE FROM region_profiles WHERE region_vnum = :vnum"),
            {"vnum": REGION_VNUM},
        )

    require_response(
        client.delete(f"/api/paths/{PATH_VNUM}", headers=headers),
        204,
    )
    require_response(
        client.delete(f"/api/regions/{REGION_VNUM}", headers=headers),
        204,
    )
    with engine.connect() as connection:
        leftovers = connection.execute(
            text(
                "SELECT "
                "(SELECT COUNT(*) FROM path_index WHERE vnum = :path_vnum), "
                "(SELECT COUNT(*) FROM region_index WHERE vnum = :region_vnum)"
            ),
            {"path_vnum": PATH_VNUM, "region_vnum": REGION_VNUM},
        ).one()
        assert leftovers == (0, 0)

    if os.environ.get("SEED_LUMINARI_BOOT_FIXTURES") == "true":
        require_response(
            client.post("/api/regions/", json=region_body, headers=headers),
            201,
        )
        require_response(
            client.post("/api/paths/", json=path_body, headers=headers),
            201,
        )
        require_response(
            client.post(
                f"/api/regions/{REGION_VNUM}/hints",
                json=hint_body,
                headers=headers,
            ),
            201,
        )
        require_response(
            client.post(
                f"/api/regions/{REGION_VNUM}/profile",
                json=profile_body,
                headers=headers,
            ),
            200,
        )

    print(
        "LuminariMUD MariaDB schema, Wildeditor APIs, spatial triggers, "
        "hints/profiles/usage, and index cleanup passed."
    )


if __name__ == "__main__":
    main()
