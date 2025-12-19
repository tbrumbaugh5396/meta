# Meta-Repo Migration Plan

## Complete Component Inventory

### Level 0: Platform Meta-Repo (`platform-meta`)
**Purpose:** Core infrastructure primitives, shared across all systems

#### Components to Extract:

1. **infrastructure-primitives** (v1.0.0)
   - **Source:** `src/scraper_platform/infrastructure/`
   - **Contents:**
     - `proxy/` - Proxy chain management, circuit breakers
     - `vpn/` - VPN provider abstraction
     - `network/` - Network topology, abstraction layer
     - `storage/` - S3, in-memory storage
     - `messaging/` - Kafka, in-memory broker
     - `cache/` - Redis, in-memory cache
     - `database/` - PostgreSQL, in-memory database
     - `core/` - Core interfaces (Redis, file storage, ID generation, time)
     - `circuit_breaker/` - Circuit breaker patterns
     - `retry/` - Retry strategies
     - `queue/` - Task/result queues
     - `dead_letter_queue/` - DLQ handling
   - **Interface:** Python package with typed interfaces
   - **Dependencies:** None (base layer)

2. **observability-platform** (v1.0.0)
   - **Source:** `src/scraper_platform/infrastructure/`
   - **Contents:**
     - `monitoring/` - Metrics, alerting, tracing
     - `observability/` - Audit, metrics
     - `logging/` - Structured logging, Sentry
   - **Interface:** Python package
   - **Dependencies:** infrastructure-primitives

3. **security-platform** (v1.0.0)
   - **Source:** `src/scraper_platform/infrastructure/security/`
   - **Contents:**
     - `security/rbac.py` - Role-based access control
     - `security/secrets_manager.py` - Secrets management
     - `domain/rbac.py`, `domain/rbac_roles.py`, `domain/rbac_permissions.py`
   - **Interface:** Python package
   - **Dependencies:** infrastructure-primitives

4. **execution-runtime** (v1.0.0)
   - **Source:** `src/scraper_platform/infrastructure/execution/`
   - **Contents:**
     - `execution/execution_engine.py` - Base execution engine
     - `execution/message_queue.py` - Message queue abstraction
   - **Interface:** Python package
   - **Dependencies:** infrastructure-primitives, observability-platform

---

### Level 1: System Meta-Repo (`scraping-platform-meta`)
**Purpose:** Scraping and agent system capabilities

#### Components to Extract:

5. **agent-core** (v2.1.0) ✅ *Already separate*
   - **Source:** `src/agent_core/`
   - **Status:** Mostly ready, needs interface contracts
   - **Dependencies:** None

6. **detector-core** (v1.5.2) ✅ *Already separate*
   - **Source:** `src/detector_core/`
   - **Status:** Mostly ready, needs interface contracts
   - **Dependencies:** None

7. **scraper-capabilities** (v3.0.1)
   - **Source:** `src/scraper_platform/infrastructure/scraping/`
   - **Contents:**
     - `scraping/base.py` - Base scraper interface
     - `scraping/http/` - HTTP scrapers (simple, TLS fingerprint)
     - `scraping/browser/` - Browser scrapers (emulated, web crawler)
     - `scraping/registry.py` - Scraper registry
   - **Interface:** Python package
   - **Dependencies:** infrastructure-primitives, agent-core

8. **emulation-engine** (v2.0.0)
   - **Source:** `src/scraper_platform/infrastructure/emulation/`
   - **Contents:**
     - `emulation/behavioral.py` - Behavioral emulation
     - `emulation/browser_runtime.py` - Browser runtime config
     - `emulation/http_fingerprint.py` - HTTP fingerprinting
     - `emulation/os_device.py` - OS/device emulation
     - `emulation/tls_fingerprint.py` - TLS fingerprinting
     - `domain/emulation.py` - Emulation domain models
   - **Interface:** Python package
   - **Dependencies:** infrastructure-primitives, detector-core

9. **parsing-engine** (v2.0.0)
   - **Source:** `src/scraper_platform/infrastructure/parsing/`
   - **Contents:**
     - `parsing/base.py` - Base parser interface
     - `parsing/default_parser.py` - Default parser implementation
     - `parsing/registry.py` - Parser registry
   - **Interface:** Python package
   - **Dependencies:** infrastructure-primitives

10. **orchestration-engine** (v2.0.0)
    - **Source:** `src/scraper_platform/infrastructure/orchestration/`
    - **Contents:**
      - `orchestration/orchestrator_registry.py` - Orchestrator registry
      - `orchestration/orchestrator_manager.py` - Orchestrator management
    - **Interface:** Python package
    - **Dependencies:** execution-runtime, infrastructure-primitives

11. **workflow-engine** (v2.0.0)
    - **Source:** `src/scraper_platform/infrastructure/execution/`
    - **Contents:**
      - `execution/workflow_executor.py` - Workflow execution
      - `execution/orchestrator.py` - Workflow orchestrator
      - `execution/execution_unit_manager.py` - Execution unit management
      - `execution/agent_core_orchestrator.py` - Agent core integration
      - `execution/pipeline_executor_impl.py` - Pipeline execution
    - **Interface:** Python package
    - **Dependencies:** execution-runtime, agent-core, orchestration-engine

12. **scraper-server** (v1.0.0)
    - **Source:** `src/scraper_platform/infrastructure/scraper_server/`
    - **Contents:**
      - `scraper_server/` - Cluster management, Docker, workers
    - **Interface:** Python package
    - **Dependencies:** infrastructure-primitives, orchestration-engine

13. **ai-coding-learner** (v1.0.0)
    - **Source:** `src/ai_coding_learner/`
    - **Contents:** Code pattern analysis, quality learning
    - **Interface:** Python package
    - **Dependencies:** None

#### What Stays in `scraping-platform-meta`:

- **services/** - Thin orchestration layer
  - `agent_service.py` - Composes agent-core + workflow-engine
  - `plan_service.py` - Composes planning + execution
  - `pipeline_registry_service.py` - Composes pipelines + scrapers
  - `goal_service.py`, `policy_service.py`, `meta_agent_service.py`
  
- **domain/** - Domain models (stays in meta-repo)
  - `agent.py`, `plan.py`, `policies.py`
  - `execution_unit.py`, `core_models.py`
  - `repositories/` - Repository interfaces
  - `interfaces/pipeline_interface.py`

---

### Level 2: Application Meta-Repo (`gambling-platform-meta`)
**Purpose:** Application-specific features and UIs

#### Components to Extract:

14. **betting-calculators** (v1.0.0)
    - **Source:** `src/scraper_platform/application/services/`
    - **Contents:**
      - `ev_calculator.py` - Expected value calculations
      - `arbitrage_calculator.py` - Arbitrage calculations
      - `arbitrage_detector.py` - Arbitrage detection
      - `arbitrage_matcher.py` - Arbitrage matching
      - `parlay_probability_calculator.py` - Parlay probabilities
      - `pace_calculator.py` - Pace calculations
      - `domain/arbitrage.py` - Arbitrage domain models
    - **Interface:** Python package
    - **Dependencies:** scraping-platform-meta

15. **social-platform** (v1.0.0)
    - **Source:** `src/scraper_platform/domain/social.py`
    - **Contents:**
      - Social features (friendships, messages, bankrolls, sessions)
      - Activity feeds, notifications
    - **Interface:** Python package
    - **Dependencies:** security-platform, infrastructure-primitives

16. **live-betting-engine** (v1.0.0)
    - **Source:** `src/scraper_platform/`
    - **Contents:**
      - `domain/live_betting.py` - Live betting models
      - `application/services/live_game_tracker.py` - Game tracking
    - **Interface:** Python package
    - **Dependencies:** scraping-platform-meta, betting-calculators

17. **fund-transfer-engine** (v1.0.0)
    - **Source:** `src/scraper_platform/`
    - **Contents:**
      - `domain/fund_transfer.py` - Fund transfer models
      - `application/services/fund_transfer_engine.py` - Transfer logic
    - **Interface:** Python package
    - **Dependencies:** infrastructure-primitives, security-platform

18. **data-processing** (v1.0.0)
    - **Source:** `src/scraper_platform/application/services/`
    - **Contents:**
      - `content_extractor.py` - Content extraction
      - `structured_data_extractor.py` - Structured extraction
      - `data_normalizer.py` - Data normalization
      - `event_normalizer.py` - Event normalization
      - `statistical_aggregator.py` - Statistical aggregation
      - `situational_correlation_analyzer.py` - Correlation analysis
    - **Interface:** Python package
    - **Dependencies:** scraping-platform-meta, parsing-engine

19. **integrations** (v1.0.0)
    - **Source:** `src/scraper_platform/integrations/`
    - **Contents:**
      - `accounting.py` - Accounting integration
      - `odds_calculator.py` - Odds calculations
      - `timezones.py` - Timezone handling
    - **Interface:** Python package
    - **Dependencies:** None

#### What Stays in `gambling-platform-meta`:

- **presentation/** - All UI applications
  - `admin-web/` - React admin interface (666 files)
  - `admin-desktop/` - wxPython desktop apps
  - `user-web/` - React user interface
  - `user-desktop/` - Desktop user app

- **interfaces/http/** - FastAPI REST API (orchestration glue)
  - All HTTP routers and endpoints
  - API orchestration logic

- **features/** - Feature definitions (declarative YAML)
  - Sports betting ingestion
  - Competitive intelligence
  - Real-time monitoring

- **domain/** - Application-specific domain models
  - `social.py`, `arbitrage.py`, `live_betting.py`
  - `fund_transfer.py`, `situational_correlation.py`

---

## Meta-Repo Structure

### Level 0: `platform-meta`
```
platform-meta/
├── meta/                    # CLI tool
├── manifests/
│   ├── components.yaml      # Infrastructure primitives
│   ├── features.yaml        # Platform features
│   └── environments.yaml
├── orchestration/           # Platform orchestration
├── ci/                      # Platform CI
└── tests/                   # Platform tests
```

### Level 1: `scraping-platform-meta`
```
scraping-platform-meta/
├── meta/                    # CLI tool
├── manifests/
│   ├── components.yaml      # Scraping components
│   ├── features.yaml        # Scraping features
│   └── environments.yaml
├── services/                # Thin orchestration
│   ├── agent_service.py
│   ├── plan_service.py
│   └── pipeline_service.py
├── domain/                  # Domain models (stays here)
│   ├── agent.py
│   ├── plan.py
│   └── repositories/
├── orchestration/           # System orchestration
└── tests/                   # System tests
```

### Level 2: `gambling-platform-meta`
```
gambling-platform-meta/
├── meta/                    # CLI tool
├── manifests/
│   ├── components.yaml      # Application components
│   ├── features.yaml        # Application features
│   └── environments.yaml
├── features/                # Feature definitions
│   ├── sports-betting-ingestion.yaml
│   └── competitive-intelligence.yaml
├── presentation/            # All UIs
│   ├── admin-web/
│   ├── admin-desktop/
│   ├── user-web/
│   └── user-desktop/
├── interfaces/http/         # FastAPI (orchestration)
└── tests/                   # Application tests
```

---

## Detailed Migration Checklist

### Phase 0: Preparation (Week 1)

#### 0.1 Setup Meta-Repo Infrastructure
- [ ] Create `platform-meta` repository
- [ ] Create `scraping-platform-meta` repository
- [ ] Create `gambling-platform-meta` repository
- [ ] Copy meta-repo CLI to all three repos
- [ ] Set up CI/CD for all meta-repos
- [ ] Create component repository templates

#### 0.2 Define Interface Contracts
- [ ] Document all component interfaces
- [ ] Create OpenAPI/gRPC schemas
- [ ] Write interface contract tests
- [ ] Set up contract testing framework

#### 0.3 Create Component Repository Templates
- [ ] Create `component-template/` with:
  - `BUILD.bazel`
  - `setup.py`
  - `contracts/` directory
  - `tests/` structure
  - `README.md` template

---

### Phase 1: Extract Platform Components (Week 2-5)

#### 1.1 Extract `infrastructure-primitives` (Week 2)
- [ ] Create `infrastructure-primitives` repo
- [ ] Copy `src/scraper_platform/infrastructure/`:
  - [ ] `proxy/`, `vpn/`, `network/`
  - [ ] `storage/`, `messaging/`, `cache/`, `database/`
  - [ ] `core/`, `circuit_breaker/`, `retry/`, `queue/`, `dead_letter_queue/`
- [ ] Create `contracts/infrastructure_interface.py`
- [ ] Add `BUILD.bazel` with all targets
- [ ] Write unit tests
- [ ] Write contract tests
- [ ] Publish as `infrastructure-primitives v1.0.0`
- [ ] Update `platform-meta/manifests/components.yaml`
- [ ] Remove from main repo
- [ ] Update imports in main repo
- [ ] Run system tests

#### 1.2 Extract `observability-platform` (Week 2-3)
- [ ] Create `observability-platform` repo
- [ ] Copy `monitoring/`, `observability/`, `logging/`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `platform-meta`
- [ ] Remove from main repo

#### 1.3 Extract `security-platform` (Week 3)
- [ ] Create `security-platform` repo
- [ ] Copy `security/` and `domain/rbac*.py`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `platform-meta`
- [ ] Remove from main repo

#### 1.4 Extract `execution-runtime` (Week 3-4)
- [ ] Create `execution-runtime` repo
- [ ] Copy base execution engine
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `platform-meta`
- [ ] Remove from main repo

#### 1.5 Create `platform-meta` (Week 4-5)
- [ ] Initialize `platform-meta` repo
- [ ] Copy meta CLI
- [ ] Create `manifests/components.yaml` with platform components
- [ ] Create `manifests/features.yaml`
- [ ] Create `manifests/environments.yaml`
- [ ] Set up CI/CD
- [ ] Write system tests
- [ ] Document platform-meta usage

---

### Phase 2: Extract Scraping Components (Week 6-11)

#### 2.1 Finalize `agent-core` (Week 6)
- [ ] Add interface contracts to `agent-core`
- [ ] Create `agent-core/contracts/agent_interface.py`
- [ ] Write contract tests
- [ ] Add Bazel build (if not present)
- [ ] Publish `v2.1.0`
- [ ] Update `scraping-platform-meta/manifests/components.yaml`

#### 2.2 Finalize `detector-core` (Week 6)
- [ ] Add interface contracts
- [ ] Write contract tests
- [ ] Add Bazel build
- [ ] Publish `v1.5.2`
- [ ] Update `scraping-platform-meta`

#### 2.3 Extract `scraper-capabilities` (Week 7)
- [ ] Create `scraper-capabilities` repo
- [ ] Copy `infrastructure/scraping/`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v3.0.1`
- [ ] Update `scraping-platform-meta`
- [ ] Remove from main repo

#### 2.4 Extract `emulation-engine` (Week 7-8)
- [ ] Create `emulation-engine` repo
- [ ] Copy `infrastructure/emulation/` and `domain/emulation.py`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v2.0.0`
- [ ] Update `scraping-platform-meta`
- [ ] Remove from main repo

#### 2.5 Extract `parsing-engine` (Week 8)
- [ ] Create `parsing-engine` repo
- [ ] Copy `infrastructure/parsing/`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v2.0.0`
- [ ] Update `scraping-platform-meta`
- [ ] Remove from main repo

#### 2.6 Extract `orchestration-engine` (Week 8-9)
- [ ] Create `orchestration-engine` repo
- [ ] Copy `infrastructure/orchestration/`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v2.0.0`
- [ ] Update `scraping-platform-meta`
- [ ] Remove from main repo

#### 2.7 Extract `workflow-engine` (Week 9-10)
- [ ] Create `workflow-engine` repo
- [ ] Copy `infrastructure/execution/` (workflow-related)
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v2.0.0`
- [ ] Update `scraping-platform-meta`
- [ ] Remove from main repo

#### 2.8 Extract `scraper-server` (Week 10)
- [ ] Create `scraper-server` repo
- [ ] Copy `infrastructure/scraper_server/`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `scraping-platform-meta`
- [ ] Remove from main repo

#### 2.9 Extract `ai-coding-learner` (Week 10-11)
- [ ] Create `ai-coding-learner` repo
- [ ] Copy `src/ai_coding_learner/`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `scraping-platform-meta`
- [ ] Remove from main repo

#### 2.10 Create `scraping-platform-meta` (Week 11)
- [ ] Initialize `scraping-platform-meta` repo
- [ ] Copy meta CLI
- [ ] Move `application/services/` (thin orchestration)
- [ ] Move `domain/` (agent, plan, policies, repositories)
- [ ] Create `manifests/components.yaml` with all scraping components
- [ ] Create `manifests/features.yaml`
- [ ] Update services to use component dependencies
- [ ] Set up CI/CD
- [ ] Write system tests
- [ ] Document usage

---

### Phase 3: Extract Application Components (Week 12-15)

#### 3.1 Extract `betting-calculators` (Week 12)
- [ ] Create `betting-calculators` repo
- [ ] Copy betting calculation services
- [ ] Copy `domain/arbitrage.py`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `gambling-platform-meta`
- [ ] Remove from main repo

#### 3.2 Extract `social-platform` (Week 12-13)
- [ ] Create `social-platform` repo
- [ ] Copy `domain/social.py`
- [ ] Copy social-related services
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `gambling-platform-meta`
- [ ] Remove from main repo

#### 3.3 Extract `live-betting-engine` (Week 13)
- [ ] Create `live-betting-engine` repo
- [ ] Copy `domain/live_betting.py`
- [ ] Copy `application/services/live_game_tracker.py`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `gambling-platform-meta`
- [ ] Remove from main repo

#### 3.4 Extract `fund-transfer-engine` (Week 13-14)
- [ ] Create `fund-transfer-engine` repo
- [ ] Copy `domain/fund_transfer.py`
- [ ] Copy `application/services/fund_transfer_engine.py`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `gambling-platform-meta`
- [ ] Remove from main repo

#### 3.5 Extract `data-processing` (Week 14)
- [ ] Create `data-processing` repo
- [ ] Copy data processing services
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `gambling-platform-meta`
- [ ] Remove from main repo

#### 3.6 Extract `integrations` (Week 14-15)
- [ ] Create `integrations` repo
- [ ] Copy `integrations/`
- [ ] Create contracts
- [ ] Add Bazel build
- [ ] Write tests
- [ ] Publish `v1.0.0`
- [ ] Update `gambling-platform-meta`
- [ ] Remove from main repo

#### 3.7 Create `gambling-platform-meta` (Week 15)
- [ ] Initialize `gambling-platform-meta` repo
- [ ] Copy meta CLI
- [ ] Move `presentation/` (all UIs)
- [ ] Move `interfaces/http/` (FastAPI orchestration)
- [ ] Move application-specific `domain/` models
- [ ] Create `manifests/components.yaml` with all application components
- [ ] Create `features/` directory with YAML definitions
- [ ] Update HTTP routes to use component dependencies
- [ ] Set up CI/CD
- [ ] Write system tests
- [ ] Document usage

---

### Phase 4: Final Integration (Week 16-17)

#### 4.1 Update All Meta-Repos
- [ ] Update `platform-meta` to reference all platform components
- [ ] Update `scraping-platform-meta` to reference platform-meta and scraping components
- [ ] Update `gambling-platform-meta` to reference scraping-platform-meta and application components
- [ ] Verify dependency flow (no cycles)

#### 4.2 System Testing
- [ ] Run all component unit tests
- [ ] Run all contract tests
- [ ] Run system tests in `platform-meta`
- [ ] Run system tests in `scraping-platform-meta`
- [ ] Run system tests in `gambling-platform-meta`
- [ ] Run end-to-end feature tests

#### 4.3 Documentation
- [ ] Document component interfaces
- [ ] Document meta-repo structure
- [ ] Create migration guide
- [ ] Update README files
- [ ] Create architecture diagrams

#### 4.4 CI/CD Setup
- [ ] Set up CI for all component repos
- [ ] Set up CI for all meta-repos
- [ ] Configure automated testing
- [ ] Configure automated publishing
- [ ] Set up dependency update automation

---

## Component Dependencies

```
gambling-platform-meta (Level 2)
├── betting-calculators
│   └── scraping-platform-meta
├── social-platform
│   ├── security-platform (from platform-meta)
│   └── infrastructure-primitives (from platform-meta)
├── live-betting-engine
│   └── scraping-platform-meta
├── fund-transfer-engine
│   ├── infrastructure-primitives
│   └── security-platform
├── data-processing
│   └── scraping-platform-meta
└── integrations

scraping-platform-meta (Level 1)
├── agent-core
├── detector-core
├── scraper-capabilities
│   ├── infrastructure-primitives
│   └── agent-core
├── emulation-engine
│   ├── infrastructure-primitives
│   └── detector-core
├── parsing-engine
│   └── infrastructure-primitives
├── orchestration-engine
│   ├── execution-runtime
│   └── infrastructure-primitives
├── workflow-engine
│   ├── execution-runtime
│   ├── agent-core
│   └── orchestration-engine
├── scraper-server
│   ├── infrastructure-primitives
│   └── orchestration-engine
└── ai-coding-learner

platform-meta (Level 0)
├── infrastructure-primitives
├── observability-platform
│   └── infrastructure-primitives
├── security-platform
│   └── infrastructure-primitives
└── execution-runtime
    ├── infrastructure-primitives
    └── observability-platform
```

---

## Testing Strategy

### Component Tests (in component repos)
- Unit tests for all functionality
- Interface contract tests
- Property-based tests
- Performance tests

### Contract Tests (in meta-repos)
- Interface compatibility tests
- Version compatibility tests
- Breaking change detection

### System Tests (in meta-repos)
- End-to-end feature tests
- Integration tests
- Failure mode tests
- Load tests

---

## Rollback Procedures

### For Each Component Extraction:
1. Keep original code in main repo until fully verified
2. Use feature flags to switch between local and package
3. Maintain backward compatibility during transition
4. Keep migration branch for easy rollback
5. Document rollback steps

### For Meta-Repo Creation:
1. Keep current structure as fallback
2. Use environment variables to switch meta-repos
3. Maintain parallel CI/CD pipelines
4. Test rollback procedure before committing

---

## Success Criteria

- [ ] All components extracted and published
- [ ] All meta-repos functional
- [ ] All tests passing
- [ ] No circular dependencies
- [ ] All features working end-to-end
- [ ] Documentation complete
- [ ] CI/CD operational
- [ ] Team trained on new structure


