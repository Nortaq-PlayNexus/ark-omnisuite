# Operations usability milestone

Sources and competitor caveats: `research/05-event-coordination.md`. No novelty claim.

1. Implement a pure event-window comparison with UTC/offset-aware ISO instants, 1–20 bounded entries, positive duration, UTC normalization, [start,end) overlap, all pairs, fixed UTC output, and Discord timestamp text. No data persistence or notifications. Browser offers four UTC windows and clear timezone disclaimer.
2. Allow route pin subsets (1–8) selected using accessible labelled checkboxes; preserve world isolation, duplicate names and the original route algorithm. No automatic terrain routing.
3. Replace tribute JSON field with explicitly labelled non-negative numeric counts for the seven sourced tribute items. Maintain zero for missing values; endpoint remains compatible with existing clients.
4. Verify edge cases, network endpoint, browser interactions and theme accessibility; document actual scope and rebuild ZIP.
