# PR Review Workflow

This document describes our pull request review process and the team agreement that governs it.

## Core Principle

**Every pull request automatically gets a Copilot code review.** Engineers are expected to resolve Copilot's comments before requesting human review.

## Why We Enforce This Today

Six months ago, we did **not** enforce this policy because the automated feedback was too noisy to be useful.

Over the last few months, the model quality has significantly improved, often catching **security** and **performance** issues on the first pass. As a result, resolving Copilot's comments before requesting a human review has become a natural part of our workflow.

## Coordination

We coordinate through a **Slack channel** where a bot posts all pull requests with **status indicators** for CI. These indicators update **in-place** as checks complete, so the team always sees the latest CI state without extra messages.

## Review Culture

Our team culture is **"give one, take one"**:

- **Submit** your own pull request for review.
- **Pick up** and review someone else's pull request.

This keeps the review queue balanced and ensures work moves forward collaboratively.
