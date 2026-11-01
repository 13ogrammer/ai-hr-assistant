---
version: 1
slug: "apps-web-src-app-jsx"
primary_target: "apps/web/src/App.jsx"
related_targets: []
---

## Direction contract

THESIS: A quiet, focused chat column that answers HR questions one at a time, refusing the "form with a results panel" shape most internal tools default to - the conversation itself is the product, not a sidebar around it.

OWN-WORLD: ChatGPT's interface language, pinned by explicit user request, not a from-scratch exploration. Per Operate-mode rules, it lends exactly four things: a restrained near-monochrome palette (light neutral ground, dark-mode aware via existing `prefers-color-scheme` tokens) with one small accent for the primary action; a calm system sans-serif type voice at comfortable reading size; generous vertical density between turns (conversation, not a dense data table); and one signature move - the composer bar pinned to the bottom of the viewport while the message history scrolls above it, auto-scrolling to the latest turn. Navigation and controls stay standard web form elements (text input, submit button), never a costume of ChatGPT's own chrome (no fake sidebar, no fake model-picker, no invented branding).

STORY: An employee opens the page, sees an empty conversation with a single centered input at the bottom, types a question, and watches it appear as their own message bubble while the assistant's answer streams in below it (or appears once ready) as a distinctly-styled bubble, with its source documents shown underneath in a quiet secondary line. They can keep asking follow-ups in the same scrolling thread.

FIRST VIEWPOINT: Full-height column, max-width ~740px, centered. Empty state: a short centered heading/prompt ("Ask about HR policy...") vertically centered with the input directly below it. Once a conversation starts: message history fills the scrollable area from the top, newest at the bottom, composer bar fixed at the very bottom of the viewport with a soft top border separating it from the scroll area.

FORM: Direction pinned directly by user request ("design it like ChatGPT, structure doesn't have to be exact") - no concept-seed roll run; this is the explicit brief, not a candidate chosen from a dealt hand.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
