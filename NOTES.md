# Cyberpunk 2077 Story Co-op — Development Notes

## Goal
Develop online, two-player story co-op for Cyberpunk 2077, with the host controlling dialogue choices and shared story progression.

## Reference Environment
- Host: Steam, Windows 11
- Game product version: 2.31
- Cyberpunk2077.exe file version: 3.0.5294808
- Executable SHA-256: `A7DE82945C03E041FC7339FCF9066224D98DB2F5D80FEA50F7947BB350A60991`
- Guest: GOG with Phantom Liberty; exact game version not yet verified.

## Existing Co-op Behavior
The current code reports the host's game time, weather, and tracked quest to guests. It also supports a story-host role and player teleportation.

Dialogue-choice synchronization and complete shared quest progression have not yet been verified.

## Design Proposal
- Host is authoritative for story choices and major quest state.
- Guests receive ordered, uniquely identified story events.
- Guests acknowledge events and can request a state resynchronization.
- Each game renders its own dialogue and cutscenes locally.
- Prevent duplicate or out-of-order events from applying twice.

## First Milestone
Research Cyberpunk's dialogue and quest APIs on patch 2.31. Identify a safe, observable conversation event before implementing runtime hooks.

## Safety and Testing
- Never modify the original game installation or saves during development.
- Do not install dependencies or download large files without approval.
- Use isolated copies for any runtime experiments.
- Distinguish implemented behavior from proposed or unverified behavior.
- Test with two isolated clients before claiming online story co-op works.

## Current Status
Research and design only. No dialogue synchronization code has been implemented or tested.
