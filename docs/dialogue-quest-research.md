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


## Follow-up: q003 candidate facts and source-version caveat

The RedSync extracted base-game reference lists several q003 facts for The Pickup, including q003_deal_started, q003_deal_done, q003_deal_combat_done, q003_royce_bossfight_done, and q003_done. This makes q003 a practical candidate for a future observation test, but the list is an extracted fact inventory—not a verified mapping from dialogue options to outcomes.

- [RedSync base-game quest whitelist](https://github.com/nobody71004/RedSync/blob/main/release/BASE-QUEST-WHITELIST.md)
- [CDPR Modding Docs: visualizing quest files](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/modding-guides/quest/visualize-quest-files.md)
- [The Pickup overview](https://cyberpunk.fandom.com/wiki/The_Pickup)

### Important version boundary

The RedSync base quest extraction documents a game install build labelled 1.0.148, while the user's Cyberpunk2077.exe file version is 3.0.5294808 and the public patch is 2.31. Its fact list is a lead to verify, not proof that the exact quest resources, fact names, or listener behavior match the user's installation.

### First observation test — no state mutation

1. Use a separate disposable save and choose one route through The Pickup.
2. At runtime, read the baseline values of the candidate q003 facts.
3. Register exact-name listeners and log callback time, fact name, and current value; do not call SetFact and do not relay anything over the network.
4. Repeat from a clean test save using a different route, then compare which facts changed and at what point.
5. Inspect the matching q003 .quest / .questphase resources with a quest graph viewer to confirm what each changed fact means.
6. Only nominate a fact as a branch signal if both the resource graph and repeated observations support that interpretation.

### Go/no-go criteria

Proceed to a network prototype only if the observer compiles on the target build, callbacks fire predictably, and the candidate fact maps unambiguously to an outcome. If multiple branches share the same fact or the event arrives too late to prevent local divergence, keep the scope to post-outcome diagnostics and investigate a stronger signal.

No such observer has been implemented in this fork yet. No runtime tests or builds have been performed.

## Follow-up: what the external listener implementation actually tells us

A closer source read of RedSync's mission-sync implementation sharpens the candidate API, but also reinforces the need for a diagnostic-only first step:

- Its comments say `QuestsSystem` is native-only and that wrapping script methods would miss quest-graph fact writes. It uses the engine's exact-name `RegisterListener` mechanism because the callback is reported for native or scripted writes to that fact.
- There is no wildcard listener in the implementation: it registers one listener per curated fact name.
- The listener runs after the fact has changed. Its follower approach therefore pins the value back after local divergence; it does not prevent the local quest graph from briefly taking a different route.
- The source contains an explicitly temporary verification hook and describes its observed install as build `1.0.148`. This is evidence of the project's reported test environment, not validation on our target executable.

Source: [RedSync mission-sync source](https://github.com/nobody71004/RedSync/blob/main/client/RedscriptModule/src/Network/RedSyncMissionSync.reds).

### Updated decision

Keep the first implementation scoped to **logging only**. Do not copy RedSync's broad fact pinning or snapshot behavior into this fork yet. The safest sequence is:

1. Establish whether the exact-name listener compiles and fires on the user's target build.
2. Log fact name, value, and timestamp without mutating facts or sending network messages.
3. Compare the observed changes against the quest graph from a disposable save.
4. Only after that, choose whether a narrowly defined post-outcome event can be synchronized.

This still does not identify the `.quest` / `.questphase` branch mapping for The Pickup; those game resources have not been inspected in this repository. No code was added and no build/runtime test was performed as part of this research update.
## Resource-level investigation result: q003 graph not yet available

Public searches located the q003 fact-name inventory, but did not locate the actual vanilla `q003` `.quest` / `.questphase` / `.scene` resource payload in the checked repositories. Therefore we still cannot responsibly map `q003_deal_started`, `q003_deal_done`, or `q003_royce_bossfight_done` to a particular dialogue branch.

The CDPR modding documentation describes the correct next resource-inspection workflow: locate the questphase resource in WolvenKit's Asset Browser, open it in the graph editor, follow external phase references, and inspect any referenced scene resources. A questphase graph owns progression and fact/journal operations; a scene owns dialogue choices and scene-local exits. The named exit and the questphase continuation are related but distinct.

References:
- [CDPR Modding Docs: visualize quest files](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/modding-guides/quest/visualize-quest-files.md)
- [RED Questbook: resource map](https://hlky.github.io/cyberpunk-quest-authoring/reference/resource-map.html)
- [REDmodding Wiki: quest facts and files](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/files-and-what-they-do/file-formats/quests-.scene-files/quests-facts-and-files)
- [RedSync extracted tracked facts](https://github.com/nobody71004/RedSync/blob/main/release/tracked_facts.json)

### Safe next steps when resource access is approved

1. Use a game-resource browser against the installed game archives; do not modify or repack the original archives.
2. Locate the `q003` quest root and follow its referenced phase resources to the scene that contains the Militech/Maelstrom negotiation.
3. Export/read-only inspect the relevant graph and record only resource paths, node types/IDs, outgoing socket names, and exact fact writes.
4. Trace each candidate fact's writer and downstream readers before treating it as an outcome key.
5. Keep the eventual runtime test on a disposable save; listener observation first, no fact writes or network relay.

No quest resources were extracted, no tools were installed, and no game/save files were changed during this research pass. Resource-level branch mapping remains blocked pending access to the actual quest assets.
## Follow-up: make the resource-inspection step reproducible

The official CDPR guide confirms that quest progression is represented by `.questphase` graphs which reference other phases and scenes; WolvenKit's Asset Browser can open a resource for inspection without adding it to a mod project. The RED Questbook's vanilla-inspection procedure adds an important safety boundary: use a separate disposable inspection project, keep extracted vanilla resources local, and never package them as part of the mod.

References:
- [CDPR Modding Docs: visualize quest files](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/modding-guides/quest/visualize-quest-files.md)
- [RED Questbook: inspect a vanilla questphase](https://hlky.github.io/cyberpunk-quest-authoring/start-here/inspecting-vanilla.html)
- [WolvenKit Quest Editor guide](https://wiki.redmodding.org/wolvenkit/wolvenkit-app/editor/quest-editor)

### Read-only inspection checklist

1. In WolvenKit's Asset Browser, ensure base-game archive browsing is selected rather than Mod Browser mode.
2. Search for `q003` and identify the root quest/phase resources and their referenced child phases/scenes. Do not assume the depot path from the fact prefix; follow actual resource references.
3. Open the relevant `.questphase` and `.scene` resources without adding them to a distributable mod project, or place them in a dedicated inspection-only project that is never built.
4. Record source depot path, resource type, node IDs/types, outgoing socket names, scene exit names, fact write nodes, and downstream fact readers. Avoid copying full vanilla resource payloads into this repository.
5. Trace any candidate fact from its writer to the questphase/scene branch and to later readers. A name or value alone is insufficient to classify a dialogue outcome.
6. If the correct resource cannot be located, record the search terms and results and stop rather than guessing a path or using a similarly named resource.

### Current blocker

The public references found so far explain the inspection workflow but do not publish the exact q003 resource graph needed to prove the branch mapping. This research pass did not access the user's local game archives, install WolvenKit, or extract game resources. The next concrete action requires the user to approve tool installation or provide read-only exports of the relevant resource metadata/graphs. Until then, no branch-to-fact mapping should be treated as confirmed.
## Follow-up: exact resource workflow and version pinning

Current documentation research confirms a practical way to proceed without touching the game install: WolvenKit's Asset Browser can open a vanilla resource without adding it to a project, and its Quest Editor displays `.questphase` node graphs. The RED Questbook recommends a disposable inspection project when a resource must be extracted and warns not to package the vanilla resource. These are inspection procedures, not proof of q003's actual branch mapping.

References:
- [CDPR Modding Docs: visualize quest files](https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs/blob/main/modding-guides/quest/visualize-quest-files.md)
- [WolvenKit Quest Editor guide](https://wiki.redmodding.org/wolvenkit/wolvenkit-app/editor/quest-editor)
- [RED Questbook: inspect a vanilla questphase](https://hlky.github.io/cyberpunk-quest-authoring/start-here/inspecting-vanilla.html)

### Version rule

Pin all observations to the user's own installation: public patch label 2.31 and executable file version 3.0.5294808. The RED Questbook's 2.31a inspection baseline is a useful cross-check but must not substitute for reading the user's own archives. Record the WolvenKit version and the exact depot path with every finding.

### What counts as evidence

For each candidate q003 fact, record: (a) the exact resource where it is written, (b) the writer node type and ID, (c) the connected input/output socket path, (d) the downstream reader(s), and (e) a separate label for whether the relationship is only structural or has been observed in-game. Do not equate a fact prefix or a tracked-fact list with a dialogue branch.

### Next checkpoint

At present, the actual q003 resources have not been opened. This environment has not installed WolvenKit or accessed the user's local archives, so the graph-to-fact mapping remains unresolved. The next action requiring user-side participation is to open the q003 quest/phase/scene resources in WolvenKit or provide a small text summary of the relevant node IDs, sockets, and fact-write properties. Do not upload full vanilla resource dumps or modify the original game files.
## Follow-up: identify the quest root, but do not guess depot paths

Public quest references identify The Pickup's technical base ID as `q003_maelstrom` and describe several materially different routes through Meredith Stout, the Militech credchip, and the Maelstrom negotiation. This is useful for narrowing the Asset Browser search, but it does not reveal the exact questphase/scene depot paths or prove which fact records each branch.

Reference: [The Pickup technical overview and branch descriptions](https://cyberpunk.fandom.com/wiki/The_Pickup).

### Asset Browser search order

1. Search the installed base-game archives for `q003_maelstrom` first, then `q003` if no exact root appears.
2. Filter/inspect results by resource type (`.quest`, `.questphase`, `.scene`) and use the resource dependency view to follow references. Do not infer the depot path from the quest ID or file name alone.
3. Start at the quest root and follow phase references until the scene that owns the Militech/Maelstrom negotiation is identified. Record exact depot paths and node IDs locally.
4. From the relevant scene, record choice-node outputs and named scene exits. Follow the corresponding questphase branch and locate fact writes and later readers.
5. Keep the evidence separate: public walkthroughs describe player-visible branches; resource graphs show authored structure; only a runtime observation can show when a particular fact changes on the target build.

### Why the next milestone is still blocked

The public sources found so far establish the quest identity and a safe inspection workflow, but not the actual resource graph. I cannot access the user's installed game archives from this session, and I have not installed or run WolvenKit. No exact q003 resource path or branch-to-fact mapping is claimed. The next concrete input needed is a read-only node/property summary from the user's local Asset Browser, or explicit approval to proceed with setting up the inspection tool.