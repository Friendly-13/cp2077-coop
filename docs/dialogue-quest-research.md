# Dialogue and quest research findings

Status: documentation research only; no game runtime test has been performed.

## Findings from Cyberpunk quest-authoring documentation

- A visible dialogue choice is not equivalent to a durable story result. Scene choices route through scene graph outputs, and the quest phase may record a named result after the scene exits.
- Choice captions/localized text are not safe network identifiers. A choice can involve a screenplay option, a scene choice node/row, graph output, and a later quest outcome.
- Phone replies, performed dialogue scenes, journal messages, and calls use different systems and completion signals; they should not be handled as one generic conversation API.
- Quest facts are persistent state inputs read by downstream quest logic. Forcing arbitrary facts can create delayed quest bugs and should not be used as a generic synchronization strategy.
- This means the safest first milestone is to observe and replicate a stable, semantically meaningful event from a narrow known scene, then verify both clients' resulting quest state. Do not attempt to force all guest quest facts from the host.
- The public RED Questbook lists a GOG Windows 2.31a baseline (the public patch is called 2.31) and provides scene-resource examples. This is useful reference material, but it does not establish that a hook works in our mod or that the user's Steam executable has identical resource behavior.

## Candidate first experiment

Choose a short base-game conversation with a clear branch and no irreversible consequences for a test save. Inspect its scene graph and the downstream questphase outcome. Capture:
1. A stable scene/choice identity available at runtime (still unknown).
2. The selected graph route or named result (still unknown).
3. The durable quest outcome on both clients after scene completion.
4. Recovery behavior when the guest disconnects before or after the outcome is committed.

Do not use a display string, localized caption, or tracked quest label as the authoritative choice key.

## References

- [RED Questbook: choices, outcomes, and localization](https://hlky.github.io/cyberpunk-quest-authoring/scenes/choices-outcomes-and-localization.html)
- [RED Questbook: branching choices and debriefs](https://hlky.github.io/cyberpunk-quest-authoring/patterns/branching-choices-and-debriefs.html)
- [RED Questbook: messages, calls, and conversations](https://hlky.github.io/cyberpunk-quest-authoring/patterns/messages-calls-and-conversations.html)
- [REDmodding Wiki: quest facts and files](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/files-and-what-they-do/file-formats/quests-.scene-files/quests-facts-and-files)
- [CDPR Modding Documentation: scene node definitions](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/modding-guides/quest/scene-node-definitions.md)

## Status and next research

No dialogue RPC or runtime hook has been implemented. Next, inspect available REDscript/RED4ext event APIs and existing CyberpunkMP native lookup patterns to determine whether a reliable runtime event can be observed without replacing vanilla scene resources.

## Runtime-hook investigation (follow-up)

The CDPR Modding Documentation's scene-node reference confirms that `scnChoiceNode` exposes option rows and output sockets, while the RED Questbook's node/socket index distinguishes scene-local routing from the named scene exit and the questphase result. These are useful authoring-time identities, but the documents do **not** establish that a stable runtime callback for a player's selected option is exposed to redscript or RED4ext.

- [CDPR Modding Docs: scene node definitions](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/modding-guides/quest/scene-node-definitions.md)
- [RED Questbook: node and socket index](https://hlky.github.io/cyberpunk-quest-authoring/reference/node-and-socket-index.html)
- [CDPR Modding Docs: visualize quest files](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/modding-guides/quest/visualize-quest-files.md)

### Implication for implementation

Do not implement a guessed hook such as a generic `OnChoice` callback yet. The current fork has no such hook or dialogue RPC in the inspected files, and repository code search did not reveal one. The existing native wrapper demonstrates guarded runtime function lookup, but it only covers game-time, weather, and journal tracking; its existence is not evidence that dialogue functions are safe to call.

The next research gate is to identify a concrete runtime event source (for example, a scene/quest callback or an observable transition) and verify its signature against the user's exact game build before wiring networking. If no stable callback exists, a safer first prototype may be **post-outcome synchronization for one known branch**, rather than attempting to mirror every live dialogue click.

### Confidence labels

- **Confirmed by source inspection:** the current fork's inspected scripts expose no dialogue-choice RPC; tracked quest reporting is journal-path telemetry only.
- **Confirmed by authoring documentation:** choice option, graph output, named scene exit, and durable quest result are distinct structures.
- **Not yet established:** a reliable runtime callback for a selected dialogue option; a safe generic way to apply arbitrary story outcomes; behavior parity between the user's Steam build and the documented GOG 2.31a baseline.

## Follow-up: fact-change listeners may be a better first milestone

A public Cyberpunk multiplayer project, [RedSync](https://github.com/nobody71004/RedSync), documents a different strategy from trying to intercept the visible dialogue button. Its redscript source uses `QuestsSystem.RegisterListener(factName, listener, callbackName)` for a curated list of exact fact names. When a tracked fact changes, the host reads the new value and relays it; its follower logic attempts to suppress divergent local progression by pinning tracked facts to host-known values. It also includes a snapshot path for late joiners.

References:
- [RedSync mission-sync implementation](https://github.com/nobody71004/RedSync/blob/main/client/RedscriptModule/src/Network/RedSyncMissionSync.reds)
- [RedSync quest fact whitelist and extracted quest coverage](https://github.com/nobody71004/RedSync/blob/main/release/BASE-QUEST-WHITELIST.md)
- [RedSync quest fact update packet](https://github.com/nobody71004/RedSync/blob/main/server/Managed/NativeLayer/Protocol/Serverbound/QuestFactUpdate.cs)

### What we can reuse as a research lead

- `QuestsSystem.RegisterListener` is a concrete API candidate for observing changes to *known fact names*, without needing a generic dialogue-click hook.
- The event reports a fact change, not the semantic choice itself. One choice may write multiple facts, and a fact may be set by unrelated quest logic. The name/value alone cannot be treated as a complete dialogue event.
- Listener registration appears to require one exact fact name at a time; the RedSync source uses a curated tracked-fact manifest rather than a wildcard listener.
- RedSync's own code comments describe follower pin-back as an approach that needs runtime verification. It is not evidence that arbitrary fact pinning is safe for every mission, nor that it works with our exact Steam executable and mod stack.

### Revised first prototype

Prefer a narrow **quest-fact observation prototype** before any attempt to mirror live dialogue input:

1. Pick one low-risk branch in a disposable test save.
2. Inspect its `.scene` and `.questphase` resources to identify a fact written specifically for the outcome.
3. Register a listener for that exact fact and log name/value only; do not write or synchronize it yet.
4. Confirm in-game that the listener fires at the expected point on the user's 2.31 build.
5. Only then design a host-to-guest relay for that known outcome, including conflict handling and a clean-save test matrix.

This does not solve full-story synchronization, but it gives us a measurable first milestone and avoids guessing at a dialogue API.

### Confidence

- **Documented in an external project's source:** RedSync implements exact-name quest-fact listeners and a host-authoritative fact relay design.
- **Not independently validated here:** whether its listener callbacks work identically on the user's Steam build; whether its full implementation is robust for all quests; whether it can be adapted directly to this fork.
- **Still unimplemented in our fork:** listeners, fact relay, snapshots, and quest-state enforcement.

## Concrete candidate: The Pickup (q003) for a later disposable-save test

RedSync's extracted quest-fact reference includes several `q003_*` facts for **The Pickup**, including `q003_deal_started`, `q003_deal_done`, `q003_deal_combat_done`, `q003_royce_bossfight_done`, and `q003_done`. This provides concrete candidate names to inspect in the actual scene/questphase resources; it does not prove which single fact uniquely identifies each dialogue branch.

- [RedSync base-game quest whitelist](https://github.com/nobody71004/RedSync/blob/main/release/BASE-QUEST-WHITELIST.md)
- [RedSync tracked-fact list](https://github.com/nobody71004/RedSync/blob/main/release/tracked_facts.json)
- [The Pickup branch overview](https://www.powerpyx.com/cyberpunk-2077-the-pickup-walkthrough/)

### Why q003 is a useful test target (not a production sync plan)

The Pickup has clear, consequential branches involving Meredith Stout, the Militech credchip, and the Maelstrom negotiation. That makes it easy to notice whether two clients diverge, but it is also a risky mission to use casually because decisions can affect later content. Use only a separate, disposable test save.

Proposed observation-only checklist:
1. Before starting, log current values for the candidate `q003_*` facts.
2. Perform one documented route on the host; log every listener callback with fact name, value, and timestamp.
3. Repeat a different route from a fresh test save and compare the event sequences.
4. Check which facts are merely progress markers and which facts actually distinguish outcomes by inspecting the matching `.quest` / `.questphase` resources.
5. Do not relay or write any of these values to the guest until the listener timing and semantic meaning are verified.

**Do not assume `q003_no_deal` or `q003_royce_boss` is a complete outcome key based only on its name.** The extracted lists may contain historical or derived facts, and a single branch may update several facts.
