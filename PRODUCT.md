# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Employees, managers, and HR staff at Pinnacle Solutions (a fictional mid-size professional services company, ~250 FTE), asking natural-language questions about HR policy - leave entitlements, pay/benefits, code of conduct, performance process, etc. - instead of digging through policy documents themselves. [Inferred from the project's HR docs, system prompt, and prior conversation - not independently confirmed with the user.]

## Product Purpose

Answer HR policy questions by retrieving the relevant passage from the company's HR documents (RAG over `apps/api/docs`) and having an LLM compose a grounded answer with its sources, instead of staff searching policy PDFs themselves or interrupting HR with repetitive questions.

## Positioning

An internal tool, not a market-facing product. [This project is an educational build exercise working through a staged RAG build plan - chapter by chapter, deliberately naive first, hardening later (access control, citations, evals, etc. are explicit later chapters, not yet built).]

## Operating Context

Used at a desk, during a work task, to get a quick policy answer. Currently a single `POST /ask` endpoint (question in, answer + source filenames out) with no auth, no per-user identity, and no conversation persistence - every question is independent. [These gaps are deliberate and known, not oversights - they're scheduled for later build-plan chapters.]

## Capabilities and Constraints

- Backend (`apps/api`): FastAPI, retrieval-augmented generation over Postgres/pgvector, OpenAI (gpt-4o-mini) for generation. No access control yet - anyone can ask anything.
- Frontend (`apps/web`): Vite + React, currently a bare single-question form, being redesigned now into a ChatGPT-like structural pattern (message history, bottom-anchored input) - not required to visually match ChatGPT's branding.
- No streaming yet; answers return as a single completed response.
- No login/identity - open question for a later chapter.

## Evidence on Hand

- `apps/api/docs/`: real (fictional-company) HR policy documents used for retrieval.
- No logos, brand marks, or visual identity exist yet for "Pinnacle Solutions" beyond its name in document text.

## Product Principles

- Naive and working beats polished and incomplete - this project explicitly builds the simplest version first and hardens it only once a real failure demonstrates the need.
- Internal tool, not a marketing surface - prioritize clarity and task completion over persuasion or brand expression.
- Every current limitation (no auth, no streaming, no citation verification) is a known, logged gap, not a silent omission.
