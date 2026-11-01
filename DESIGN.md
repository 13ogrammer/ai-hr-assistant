---
name: Pinnacle Solutions HR Assistant
description: A quiet, ChatGPT-structured chat interface for asking HR policy questions
colors:
  text-muted: "#6b6375"
  text-heading: "#08060d"
  bg-base: "#ffffff"
  bg-raised: "#f7f6f9"
  border: "#e5e4e7"
  accent: "#aa3bff"
  accent-bg: "rgba(170, 59, 255, 0.1)"
  accent-border: "rgba(170, 59, 255, 0.5)"
  error: "#c0372e"
  error-bg: "rgba(192, 55, 46, 0.08)"
  text-muted-dark: "#9ca3af"
  text-heading-dark: "#f3f4f6"
  bg-base-dark: "#16171d"
  bg-raised-dark: "#1f2028"
  border-dark: "#2e303a"
  accent-dark: "#c084fc"
typography:
  heading:
    fontFamily: "system-ui, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    letterSpacing: "-0.01em"
  body:
    fontFamily: "system-ui, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  sm: "0.65rem"
  md: "0.75rem"
  lg: "1.1rem"
components:
  bubble-user:
    backgroundColor: "{colors.accent-bg}"
    textColor: "{colors.text-heading}"
    rounded: "{rounded.lg}"
    padding: "0.6rem 0.95rem"
  bubble-error:
    backgroundColor: "{colors.error-bg}"
    textColor: "{colors.error}"
    rounded: "{rounded.md}"
    padding: "0.6rem 0.95rem"
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.bg-base}"
    rounded: "{rounded.sm}"
    padding: "0.65rem 1.1rem"
  input:
    backgroundColor: "{colors.bg-raised}"
    textColor: "{colors.text-heading}"
    rounded: "{rounded.sm}"
    padding: "0.65rem 0.9rem"
---

# Design System: Pinnacle Solutions HR Assistant

## Overview

A single-purpose internal tool, not a product with a brand to express: an employee asks an HR policy question and reads the answer in a familiar chat shape. The visual world is pinned directly from ChatGPT's interface language by explicit request - not a from-scratch identity - but only its structural pattern transfers, not its branding: a scrolling conversation column, a bottom-anchored composer, right-aligned user bubbles against plain-text assistant replies. Everything else (palette, type, the app's own name) is this project's own.

Density is generous rather than compact: this is a conversation, not a data table, and the gap between turns (1.5rem) is deliberately larger than the gap within one message's own lines.

**Key characteristics:**
- Restrained neutral palette with a single violet accent used only for the user's own messages and the primary action - never decorative
- System sans-serif throughout; no display face, because nothing here is persuading anyone of anything
- Full light/dark support via `prefers-color-scheme`, not a toggle - the OS decides
- One authored motion grammar (message rise-in, loading-dot pulse), nothing scattered

## Colors

Two roles only: a near-monochrome neutral scale that carries almost the entire surface, and one violet accent spent exclusively on the user's own turn and the submit action.

### Primary
- **Violet Accent** (`#aa3bff`, `#c084fc` in dark mode): the user's message bubble background (at 10%/15% opacity as `accent-bg`), its border (at 50% opacity as `accent-border`), and the composer's submit button. Nowhere else - the assistant's reply, the page's own heading, and every icon stay neutral.

### Neutral
- **Heading Ink** (`#08060d` / `#f3f4f6` dark): the empty-state heading and all message text, user and assistant alike.
- **Muted Text** (`#6b6375` / `#9ca3af` dark): the empty-state subtitle and the "Sources: ..." line under an answer.
- **Base Ground** (`#ffffff` / `#16171d` dark): the page background and the composer bar's background.
- **Raised Ground** (`#f7f6f9` / `#1f2028` dark): the text input's own background, one step off the page so it reads as an input, not a label.
- **Border** (`#e5e4e7` / `#2e303a` dark): the composer's top divider and the input's resting border.

### Error
- **Error Red** (`#c0372e` / `#f2897e` dark), on a tinted `error-bg`: a failed request renders as its own message in the conversation, in this color, distinct from both the user's accent bubble and the assistant's plain neutral text.

### Named Rule

**The One Accent Rule.** The violet accent appears in exactly two places: the user's own words, and the button that sends them. It never decorates a heading, an icon, or the assistant's reply - earning its presence by marking "this is you," not by being pretty.

## Typography

**Body/Heading Font:** `system-ui, 'Segoe UI', Roboto, sans-serif` - a single system stack, no custom webfont.

**Character:** A workhorse UI stack, deliberately unremarkable. An Operate-mode tool earns no credit for typographic personality; the only job is to disappear and let the conversation read cleanly.

### Hierarchy
- **Heading** (600, 1.5rem, -0.01em tracking): the empty-state title only, sized for a quiet opener, not a landing-page hero - this replaced an inherited 56px scaffold style that caused the title to wrap messily.
- **Body** (400, 1rem, 1.55 line-height): every message bubble and the input field. `white-space: pre-wrap` preserves the model's own line breaks in an answer.
- **Label** (0.8rem, muted color): the "Sources: ..." line beneath an assistant answer.

## Layout

A single centered column, `max-width: 48rem`, full viewport height, split into two flex regions: a scrollable message history (`flex: 1`, top-padded, bottom-padded by the last message) and a composer bar pinned as the final flex child - not `position: fixed`, which would need manual height compensation; flex layout anchors it for free. The empty state centers its content vertically and horizontally inside the same scroll region rather than using a separate layout, so the transition from empty to populated never jumps.

Spacing between messages (1.5rem) is deliberately larger than padding within a single bubble (~0.6-0.95rem) - rhythm comes from the gap between turns, not from internal padding doing double duty. Below 480px, side padding tightens (1.25rem to 1rem) and the user bubble's max-width loosens (75% to 85%) so short viewports don't force awkward wraps.

## Elevation & Depth

Flat by design - no shadows anywhere. Depth comes from color alone: the user's bubble is distinguished by background tint and a 1px border, the input field by a one-step-darker background against the page, and the composer bar by a 1px top divider against the scrolling history above it. A conversational surface this quiet has no raised surfaces to cast a shadow from.

## Shapes

Two radius steps, both soft: `0.65rem` on rectangular controls (input, button), `0.75rem` on the error bubble, and a more pronounced `1.1rem` on the user's message bubble specifically, since it's the one chat-bubble shape in the system and reads more clearly rounder than square UI chrome. No sharp corners anywhere - nothing here asks to look technical or severe.

## Components

### Message bubbles
- **User turn:** right-aligned, `accent-bg` fill, `accent-border` outline, `1.1rem` radius, `max-width: 75%` (85% below 480px) - the only boxed, colored message type.
- **Assistant turn:** left-aligned, no background or border, full available width, heading-ink color - reads as prose, not as a contained object, matching ChatGPT's own convention that the assistant's words are the page, not a card on it.
- **Error turn:** left-aligned, `error-bg` fill, error-red text, `0.75rem` radius - visually closer to the user bubble's "boxed" treatment than to the assistant's plain text, so a failure reads as a distinct event, not a bland answer.
- **Loading state:** three dots at the assistant's position, pulsing on a staggered 1.1s cycle (0.15s offset each) - occupies the exact spot the real answer will land in, so nothing shifts when it arrives.

### Composer
- Input: `bg-raised` fill, `0.65rem` radius, border transitions to full accent color on focus (0.15s ease) - the only focus treatment beyond the global `:focus-visible` ring, since a text input benefits from a clearer "you're typing here" signal than an outline alone gives.
- Button: solid accent fill, white/base text, disabled at 40% opacity with a default cursor when the input is empty or a request is in flight - never hidden, so the control's existence never depends on reading a sentence of helper text.

### Browser surfaces
Text selection and focus rings are themed from the accent (`::selection` uses `accent-bg`; `:focus-visible` is a 2px accent outline), and the scrollbar is recolored from the border token on both WebKit and Firefox rather than left at browser defaults - the system extends to the parts most redesigns forget.

## Do's and Don'ts

- **Do** keep the accent to exactly the user bubble and the submit button; introducing it anywhere else (an icon, a heading, a hover state on the assistant's text) breaks the One Accent Rule and starts reading as decoration.
- **Do** let the assistant's reply stay unboxed, plain text - boxing it would make every turn look identical and erase the user/assistant distinction the bubble asymmetry exists to create.
- **Don't** add a shadow to any surface; this system conveys depth through color and borders only, and a single shadow would read as a visual system the rest of the page never committed to.
- **Don't** reach for a sidebar, model-picker, or other ChatGPT chrome - the brief pinned the conversational *structure*, not ChatGPT's own branding or feature surface, and this is a single-purpose tool with nothing for a sidebar to navigate.
- **Don't** give the empty-state heading landing-page scale - this is an Operate-mode tool opening on a question, not a marketing moment; oversizing it was the exact bug that triggered this redesign.
