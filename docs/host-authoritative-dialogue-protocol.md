# Host-authoritative dialogue protocol (design draft)

Status: design only; not wired into runtime and not tested in-game.

## Why this is a separate milestone

The current co-op layer elects a story host and relays a periodic world snapshot (game time, weather, tracked quest identifier). It does not currently expose a dialogue-choice RPC in the inspected redscript interface. A tracked quest identifier is not proof that the guest's quest state or branching flags have been applied.

Do not add game-engine hooks until the dialogue/quest APIs and generated RPC workflow for the exact supported build are understood.

## Authority model

- The server's current story-host player ID is the sole authority for story events.
- The host client reports a candidate event; the server rejects events from non-host clients.
- The server assigns or validates a monotonically increasing session sequence and relays accepted events to guests.
- A guest never independently chooses a conflicting story branch while a host-owned scene is active.
- Each game renders its own local dialogue/cutscene. The protocol synchronizes semantic state, not frame-perfect camera animation.

## Proposed event envelope

Fields to investigate and implement:

- `protocolVersion`: allows clients to reject incompatible event schemas.
- `sessionEpoch`: changes when host ownership changes or a new campaign session begins.
- `sequence`: monotonically increasing per session epoch.
- `eventId`: unique identifier for deduplication.
- `kind`: initially limited to observed, supported event kinds; do not invent engine event names.
- `sceneKey`: stable scene/conversation identifier only if a reliable game API is found.
- `choiceKey`: stable choice identifier only if a reliable game API is found.
- `questContext`: diagnostic context, not permission to force arbitrary quest flags.

Avoid transmitting display text as the source of truth: text may be localized and is not a stable choice identifier.

## Guest handling

1. Validate protocol version and session epoch.
2. Ignore duplicate event IDs.
3. Buffer or request a snapshot for sequence gaps; never apply out-of-order events silently.
4. Acknowledge accepted events to the server.
5. Apply only through a verified game API. If the guest cannot safely apply an event, pause/mark desynchronized and report diagnostics instead of guessing.
6. On reconnect, request a state snapshot; do not replay an unbounded history blindly.

## Failure and safety rules

- If host identity changes, increment the session epoch and require a fresh snapshot.
- Do not replay choice events after a guest has independently advanced a conflicting scene.
- Never set arbitrary quest flags based only on a quest name or tracked-quest string.
- Keep original saves and game install untouched. All runtime experiments must use an isolated copy and test saves.
- Do not claim story synchronization works until a two-client test verifies the exact scenario.

## Next technical investigations

1. Read the full RPC generation conventions and build tasks before changing RPC signatures.
2. Find reliable dialogue and quest event APIs for Cyberpunk 2077 patch 2.31.
3. Identify one short, reproducible conversation with a branching choice.
4. Define the smallest supported event type and a testable acceptance criterion.
5. Only then add matching RPC declarations, generated RPC plumbing, server validation, client handling, and tests as one coherent change.
