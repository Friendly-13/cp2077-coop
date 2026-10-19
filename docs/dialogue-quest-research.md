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
