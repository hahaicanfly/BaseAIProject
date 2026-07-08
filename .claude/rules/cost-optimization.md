---
name: cost-optimization
description: AI model cost-optimization rules
always: true
---

# Cost Optimization Rules

## Model Selection

Model tiering, escalation/de-escalation, and delegation rules are single-sourced in `.claude/rules/model-dispatch.md`; this file does not duplicate the model table.

## API Cost Control

### Caching Strategy
- Do not repeat identical requests
- Cache results locally
- Set a reasonable cache expiry

### Input Optimization
- Compress images / lower resolution
- Trim prompts
- Avoid unnecessary context

### Batch Processing
- Merge multiple small requests
- Reduce API call count

## Edge AI First

Don't call an API for tasks that can run locally on-device:
- OCR text recognition
- Language detection
- Basic text processing
- Image preprocessing
- Format validation

## Monitoring Reminders

Proactively flag the following to the user:
- Large volumes of repeated API requests
- Cloud API used for tasks that could be localized
- High-cost operations with no caching
- An over-tiered model used for a simple task

## Cost-Awareness Checklist

When designing a feature, consider:
- [ ] Does this operation need an API? Could it run locally?
- [ ] Is the chosen model tier appropriate?
- [ ] Is there a caching mechanism?
- [ ] Is the input data optimized?
- [ ] Are retry attempts on failure capped?
