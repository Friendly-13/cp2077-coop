# Cyberpunk 2077 Story Co-op — Development Notes

## Goal
Develop online, two-player story co-op for Cyberpunk 2077, with the host controlling dialogue choices and shared story progression.

## Reference Environment
- Host: Steam, Windows 11
- Game product version: 2.31
- Cyberpunk2077.exe file version: 3.0.5294808
- Executable SHA-256: `A7DE82945C03E041FC7339FCF9066224D98DB2F5D80FEA50F7947BB350A60991`
- Guest: GOG with Phantom Liberty; exact game version not yet verified.
- Engine family: REDengine 4 (repository playbook classification); runtime compatibility still needs build-specific validation.

## Existing Co-op Behavior (source inspection)
- The server chooses the first connected player as story host and can hand off host role.
- Host reports game time, weather, and a tracked quest identifier periodically.
- Server stores the last reported world snapshot and relays it to guests.
- Client redscript applies guest time/weather changes and exposes teleport support.
- The inspected `CoopServer`/`CoopClient` interfaces expose world report, chat command, role, world snapshot, and teleport calls.
- The inspected interface does not expose dialogue-choice RPCs.
- A tracked quest identifier is not evidence that the guest's quest flags, objectives, branches, or save state have been synchronized.

## Evidence and Unknowns
### Observed
- Source: [Coop.reds](https://github.com/Friendly-13/cp2077-coop/blob/main/code/assets/redscript/Plugins/Coop.reds)
- Source: [Plugin.cs](https://github.com/Friendly-13/cp2077-coop/blob/main/code/server/scripting/CoopSystem/Plugin.cs)
- Source: [generated client RPCs](https://github.com/Friendly-13/cp2077-coop/blob/main/code/server/scripting/CoopSystem/Client/Plugins.CoopClient.cs)
- Source: [generated server RPCs](https://github.com/Friendly-13/cp2077-coop/blob/main/code/server/scripting/CoopSystem/Server/Plugins.CoopServer.cs)
- RPC bindings are represented by generated C# files; adding a feature likely requires following the repository's generation workflow, not editing only generated files.

### Unknown / not tested
- Exact stable identifiers for dialogue scenes and choice options on patch 2.31.
- A safe API for making the guest select/apply the host's choice.
- Whether local scene scripts can be paused or reliably prevented from diverging.
- Whether the same build and required dependencies work on the guest's GOG installation.
- Any in-game two-client behavior. No runtime test has been run.

## Design Proposal
- Host is authoritative for story choices and major quest state.
- Guests receive ordered, uniquely identified story events.
- Guests acknowledge events and can request a state resynchronization.
- Each game renders its own dialogue and cutscenes locally.
- Prevent duplicate or out-of-order events from applying twice.
- Do not force quest flags based only on a tracked-quest string.

## First Milestone
Research Cyberpunk's dialogue and quest APIs on patch 2.31. Identify a safe, observable conversation event before implementing runtime hooks.

## Safety and Testing
- Never modify the original game installation or saves during development.
- Do not install dependencies or download large files without approval.
- Use isolated copies for any runtime experiments.
- Distinguish implemented behavior from proposed or unverified behavior.
- Test with two isolated clients before claiming online story co-op works.

## Current Status
Design documentation committed. No dialogue synchronization code has been implemented, compiled, or tested in-game.
