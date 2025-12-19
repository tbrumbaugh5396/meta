# Meta-Repo Architecture

## Overview

The system has been migrated to a hierarchical meta-repo architecture with three levels:

```
Level 0: platform-meta (Foundation)
    ↓
Level 1: scraping-platform-meta (System)
    ↓
Level 2: gambling-platform-meta (Application)
```

## Level 0: Platform Meta-Repo

**Purpose:** Core infrastructure primitives, shared across all systems

**Components:**
- infrastructure-primitives (v1.0.0)
- observability-platform (v1.0.0)
- security-platform (v1.0.0)
- execution-runtime (v1.0.0)

**Dependencies:** None (base layer)

## Level 1: Scraping Platform Meta-Repo

**Purpose:** Scraping and agent system capabilities

**Components:**
- agent-core (v2.1.0)
- detector-core (v1.5.2)
- scraper-capabilities (v3.0.1)
- emulation-engine (v2.0.0)
- parsing-engine (v2.0.0)
- orchestration-engine (v2.0.0)
- workflow-engine (v2.0.0)
- scraper-server (v1.0.0)
- ai-coding-learner (v1.0.0)

**Dependencies:** platform-meta

**Contains:**
- services/ - Thin orchestration layer
- domain/ - Domain models (agent, plan, policies, repositories)

## Level 2: Gambling Platform Meta-Repo

**Purpose:** Application-specific features and UIs

**Components:**
- betting-calculators (v1.0.0)
- social-platform (v1.0.0)
- live-betting-engine (v1.0.0)
- fund-transfer-engine (v1.0.0)
- data-processing (v1.0.0)
- integrations (v1.0.0)

**Dependencies:** scraping-platform-meta, platform-meta

**Contains:**
- presentation/ - All UI applications (admin-web, admin-desktop, user-web, user-desktop)
- interfaces/http/ - FastAPI REST API (orchestration glue)
- features/ - Feature definitions (declarative YAML)
- domain/ - Application-specific domain models

## Dependency Flow

```
gambling-platform-meta
├── scraping-platform-meta
│   ├── platform-meta
│   │   ├── infrastructure-primitives
│   │   ├── observability-platform
│   │   ├── security-platform
│   │   └── execution-runtime
│   └── [9 scraping components]
└── [6 application components]
```

## Component Communication

- **Interfaces:** All components expose stable interfaces via contracts
- **Versioning:** Semantic versioning enforced
- **Orchestration:** Meta-repos orchestrate component interactions
- **Features:** Declarative YAML defines feature compositions

## Benefits

1. **Independent Evolution:** Components can evolve independently
2. **Clear Boundaries:** Each level has clear responsibilities
3. **Reusability:** Platform components reusable across systems
4. **Testability:** Components can be tested in isolation
5. **Scalability:** Easy to add new components or features


