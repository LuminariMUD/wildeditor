# Wilderness domain model

The MySQL/MariaDB wilderness schema is shared with LuminariMUD. Wildeditor maps that contract; it is not an independent source of truth for the game schema.

## Coordinates and geometry

The editor presents wilderness coordinates in the conventional `-1024..1024` range on both axes. Terrain-bridge endpoints enforce that range. Existing database geometry may be looser, so backend region/path schemas intentionally accept numeric coordinates outside it when reading or updating legacy data.

| Object | Database geometry | API representation |
| --- | --- | --- |
| Region | MySQL `POLYGON` | Array of `{x, y}` points; the backend closes the polygon for WKT persistence |
| Path | MySQL `LINESTRING` | Ordered array of `{x, y}` points |
| Landmark | Small geographic region polygon | Point chosen in the UI and expanded to a small square |

VNUMs are the primary identifiers for regions and paths. They are not auto-incremented by the mapped tables.

## Regions

| Value | Type | Meaning of `region_props` |
| --- | --- | --- |
| `1` | Geographic | Descriptive/named area; property is ignored by the game |
| `2` | Encounter | Encounter zone; comma-separated mob VNUMs live in `region_reset_data` |
| `3` | Sector Transform | Elevation adjustment |
| `4` | Sector Override | Complete sector replacement using a sector id from `0` through `36` |

Region names are required by the API and limited to 50 characters. The model also carries optional narrative and review fields, including description style/length, content flags, quality score, review state, approval state, and AI source.

## Paths

Supported path types are:

| Value | Type |
| --- | --- |
| `1` | Paved Road |
| `2` | Dirt Road |
| `3` | Geographic Feature |
| `5` | River |
| `6` | Stream |

Path names are required and limited to 50 characters. `path_props` represents the sector applied along the path and normally uses the game sector range `0..36`.

## Region hints and profiles

Hints are attached to a region VNUM and contain text, priority, activation weights, optional resource triggers, and active state. Current schema validation accepts these categories:

- `atmosphere`
- `fauna`
- `flora`
- `weather_influence`
- `sounds`
- `scents`
- `seasonal_changes`
- `time_of_day`
- `mystical`

Seasonal weights use `spring`, `summer`, `autumn`, and `winter`. Time weights use `dawn`, `morning`, `midday`, `afternoon`, `evening`, and `night`. Values are validated in the `0..2` range; hint priority is `1..10`.

A region profile stores an overall theme, dominant mood, key characteristics, description style, and complexity. The optional usage log records where and under what environmental conditions a hint was used.

## Schema authority and drift

- LuminariMUD's owning schema/migrations define shared game tables.
- `apps/backend/src/models/` defines Wildeditor's compatibility mapping.
- `apps/backend/src/schemas/` defines current API validation.
- `apps/backend/migrations/` contains Wildeditor-owned MySQL additions.
- `supabase/migrations/` is PostgreSQL/Supabase-only and must not modify MySQL game tables.

When these disagree, compare against the live/owning LuminariMUD schema before changing mappings. Add a new migration to the owning datastore; never silently rewrite an applied migration.
