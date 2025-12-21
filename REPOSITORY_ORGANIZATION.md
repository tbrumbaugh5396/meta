# Repository Organization Summary

## Overview

This document summarizes the repository organization to align with the meta-repo architecture. Code has been moved from the monolithic `src/` directory into appropriate component repositories and meta-repos.

## Completed Moves

### Component Repositories

1. **agent-core/**
   - ✅ Moved `src/agent_core/` → `agent-core/src/agent_core/`
   - ✅ Created `setup.py`
   - ✅ Created `BUILD.bazel`
   - ✅ Created `WORKSPACE`
   - ✅ Created `__init__.py` files

2. **detector-core/**
   - ✅ Moved `src/detector_core/` → `detector-core/src/detector_core/`
   - ✅ Created `setup.py`
   - ✅ Created `BUILD.bazel`
   - ✅ Created `WORKSPACE`
   - ✅ Created `__init__.py` files

3. **ai-coding-learner/**
   - ✅ Moved `src/ai_coding_learner/` → `ai-coding-learner/src/ai_coding_learner/`
   - ✅ Created `__init__.py` files

4. **infrastructure-primitives/**
   - ✅ Copied infrastructure code from `src/scraper_platform/infrastructure/`
   - ✅ Excluded: scraping, execution, orchestration, parsing, persistence, scraper_server (belong to other components)
   - ✅ Includes: proxy, vpn, network, storage, messaging, cache, database, core, circuit_breaker, retry, queue, dead_letter_queue

5. **integrations/**
   - ✅ Moved `src/scraper_platform/integrations/` → `integrations/src/integrations/`
   - ✅ Updated `BUILD.bazel` for new structure
   - ✅ Created `__init__.py` files

### Meta-Repos

1. **scraping-platform-meta/**
   - ✅ Moved domain files: `agent.py`, `plan.py`, `policies.py`
   - ✅ Moved repositories: `domain/repositories/`
   - ✅ Moved services: `agent_service.py`, `plan_service.py`, `pipeline_registry_service.py`, `goal_service.py`, `meta_agent_service.py`
   - ✅ Updated imports in repository interfaces

2. **gambling-platform-meta/**
   - ✅ Moved domain files: `arbitrage.py`, `live_betting.py`, `fund_transfer.py`, `social.py`
   - ✅ Moved services: `arbitrage_*.py`, `fund_transfer_engine.py`, `live_game_tracker.py`, `ev_calculator.py`, `parlay_probability_calculator.py`, `pace_calculator.py`
   - ✅ Presentation and interfaces already in place

## Import Updates Needed

### High Priority

1. **scraping-platform-meta/services/**
   - Update infrastructure imports to reference `infrastructure-primitives` component
   - Update application service imports to use relative imports

2. **gambling-platform-meta/services/**
   - Update integrations imports to reference `integrations` component
   - Update domain imports to use relative imports
   - Update application service imports

3. **gambling-platform-meta/interfaces/http/**
   - Update all `scraper_platform.*` imports
   - Reference components and meta-repos correctly

### Import Mapping

```python
# OLD → NEW
scraper_platform.domain.agent → domain.agent (relative) or scraping-platform-meta.domain.agent
scraper_platform.domain.plan → domain.plan (relative) or scraping-platform-meta.domain.plan
scraper_platform.infrastructure.* → infrastructure_primitives.infrastructure_primitives.*
scraper_platform.integrations.* → integrations.integrations.*
scraper_platform.application.services.* → services.* (relative in meta-repos)
```

## Remaining Infrastructure Code

The following infrastructure code still needs to be organized:

1. **scraping/** → Should go to `scraper-capabilities` component
2. **execution/** → Should go to `execution-runtime` component (or stay in meta-repo)
3. **orchestration/** → Should go to `orchestration-engine` component
4. **parsing/** → Should go to `parsing-engine` component
5. **persistence/** → Should stay in `gambling-platform-meta` (application-specific)
6. **scraper_server/** → Should go to `scraper-server` component
7. **observability/** → Should go to `observability-platform` component
8. **monitoring/** → Should go to `observability-platform` component
9. **logging/** → Should go to `observability-platform` component
10. **security/** → Should go to `security-platform` component

## Next Steps

1. **Complete Infrastructure Extraction**
   - Move remaining infrastructure code to appropriate components
   - Update all imports

2. **Update BUILD.bazel Files**
   - Add proper dependencies between components
   - Reference component repos correctly

3. **Update components.yaml**
   - Ensure all components reference correct repos
   - Update versions if needed

4. **Test Build System**
   - Run `meta validate` in each meta-repo
   - Ensure all components build correctly

5. **Remove Old src/ Directory**
   - After all code is moved and imports updated
   - Keep only meta-repo orchestration code if needed

## Component Status

| Component | Code Moved | Setup.py | BUILD.bazel | Imports Updated |
|-----------|------------|----------|-------------|-----------------|
| agent-core | ✅ | ✅ | ✅ | ⚠️ Partial |
| detector-core | ✅ | ✅ | ✅ | ⚠️ Partial |
| ai-coding-learner | ✅ | ✅ | ✅ | ⚠️ Partial |
| infrastructure-primitives | ⚠️ Partial | ✅ | ✅ | ⚠️ Partial |
| integrations | ✅ | ✅ | ✅ | ⚠️ Partial |
| scraper-capabilities | ❌ | ✅ | ✅ | ❌ |
| emulation-engine | ❌ | ✅ | ✅ | ❌ |
| parsing-engine | ❌ | ✅ | ✅ | ❌ |
| orchestration-engine | ❌ | ✅ | ✅ | ❌ |
| workflow-engine | ❌ | ✅ | ✅ | ❌ |
| scraper-server | ❌ | ✅ | ✅ | ❌ |
| observability-platform | ⚠️ Partial | ✅ | ✅ | ❌ |
| security-platform | ⚠️ Partial | ✅ | ✅ | ❌ |
| execution-runtime | ⚠️ Partial | ✅ | ✅ | ❌ |

## Notes

- The `src/` directory still contains code that needs to be moved
- Some infrastructure code belongs to multiple components (needs careful organization)
- Import updates are partially complete - many files still reference `scraper_platform.*`
- The meta-repos (`scraping-platform-meta`, `gambling-platform-meta`) have the correct structure but imports need updating

