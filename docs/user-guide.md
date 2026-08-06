# User guide

Wildeditor provides a three-pane map editor for regions, paths, landmarks, descriptions, and region hints. Because saves modify the configured LuminariMUD datastore, confirm the target environment before editing.

## Sign in and load data

Production-style builds show the Supabase email/password flow. A development build may use `VITE_DISABLE_AUTH=true` to bypass the login screen. After access is established, the editor checks backend health and loads regions and paths.

The status bar shows API state, region/path counts, cursor coordinates, zoom, and the number of unsaved items.

## Interface

- **Left pane:** drawing tools, layer visibility, and the region/path tree.
- **Center pane:** interactive coordinate map and geometry.
- **Right pane:** selected-item properties, coordinates, descriptions, hints, review state, and save controls.
- **Status bar:** connectivity summary, counts, draft actions, and zoom.
- **Chat window:** optional assistant for staged editing actions.

Panes can be resized. Layer controls independently show or hide the background map, grid, coordinate axes, origin, regions, and paths. Tree visibility controls can hide a whole group, type folder, or individual item without deleting it.

## Drawing tools

| Tool | Shortcut | Behavior |
| --- | --- | --- |
| Select | `S` | Select a map or tree item for inspection/editing |
| Landmark | `L` | Place a small geographic region around one coordinate |
| Region | `R` | Add polygon vertices; at least three points are required by the UI |
| Path | `P` | Add line vertices; at least two points are required by the UI |

Press `Enter` to finish an active region/path drawing. Press `Escape` to cancel a drawing or clear the current selection. Keyboard shortcuts are ignored while typing in an input or text area.

The frontend prevents interactive drawing outside `-1024..1024`. Existing database data may still contain geometry outside that conventional range.

## Draft, save, discard, and delete

New geometry and property edits are staged in browser state and marked as unsaved. They do not reach the database until you choose **Save Changes** or **Save All**.

- **Save Changes** writes the selected item.
- **Save All** writes every current draft sequentially.
- **Discard** removes the current dirty item from the in-memory list when no separate clean copy is present. It does not undo a server write or reliably restore the originally loaded fields; reload data to recover the saved version.
- **Discard All** applies that current discard behavior to every dirty item after confirmation.
- **Delete** immediately calls the backend after confirmation; it is not a local hide action.

Region and staged-hint writes are separate. A hint write can fail after the region save and the current UI may still clear the dirty marker, so reopen the Hints tab and verify the result. Save All is sequential and is not a database transaction across drafts.

## Regions and layers

Region properties depend on the selected type:

- Geographic regions name an area without changing terrain.
- Encounter regions use reset data for mob VNUMs.
- Sector Transform regions adjust elevation.
- Sector Override regions replace terrain with a sector type.

For a geographic region, the properties panel can create matching transform or sector layers with copied coordinates. Review the generated type and property before saving.

## Descriptions and hints

Region tabs expose properties, descriptions, hints, and review metadata. You can edit a description directly or request AI generation through the backend MCP proxy. Generated descriptions and generated hint sets are staged locally for review before the region save workflow persists them.

Hints can also be added, edited, or deleted individually. Hint categories, priorities, environmental weights, and validation rules are summarized in [Domain model](domain-model.md).

AI output is untrusted draft content. Check lore, coordinates, categories, review flags, and any proposed mutation before saving.

## Chat assistant

The optional chat assistant can analyze terrain and propose editor actions. Its path is `frontend -> chat agent -> MCP -> backend`. Proposed region/path actions are converted into frontend drafts so they can be inspected in the normal editor workflow.

If chat is unhealthy, core map editing can still work. Check the agent readiness endpoint, MCP health/authentication, and configured AI provider rather than bypassing MCP.

## Current limitations

- Save All is not a database transaction across every draft.
- Discard does not currently retain an original snapshot for reliable in-memory rollback.
- There is no offline mode or conflict-resolution workflow for concurrent editors.

Browser, backend, and chat identity is end to end: protected APIs receive the
current user token, roles come from protected claims, and chat sessions are
bound to the token subject. Networked deployments still require the TLS,
private-database, secret-storage, backup, and monitoring controls described in
[Configuration](configuration.md) and [Operations](operations.md).
