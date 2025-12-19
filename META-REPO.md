# Meta-Repo Governance

## Purpose

This repository exists to **coordinate components, not to implement business logic**.

The meta-repo acts as a control plane that:
- Orchestrates multiple independent component repositories
- Enforces system-level invariants and correctness
- Defines features as declarative compositions of components
- Manages environment-specific configurations
- Provides system-level testing and validation

## Core Principles

### 1. No Business Logic

**This repo orchestrates components, does not implement them.**

- Business logic belongs in component repositories
- This repo only contains:
  - Orchestration code (how components work together)
  - Feature definitions (declarative YAML/JSON)
  - System-level tests
  - CI/CD pipelines
  - Environment configurations

### 2. Versioned Dependencies

**All components must be versioned and pinned.**

- Components are referenced by version in `manifests/components.yaml`
- Version changes require explicit updates
- System tests must pass before version bumps
- Rollback is always possible

### 3. Declarative Features

**Features are YAML/JSON, not code.**

- Features define *what* components compose, not *how*
- Feature logic lives in components, not here
- Features can be added/modified without touching component code
- Features are environment-aware

### 4. Interface Stability

**Component interfaces must be stable before extraction.**

- Components expose stable APIs (OpenAPI, gRPC, typed interfaces)
- Breaking changes require version bumps
- Contract tests validate interface compatibility
- Backward compatibility is maintained

### 5. One-Way Dependencies

**Dependencies flow: Meta-Repo → Components (never reverse).**

- Meta-repo depends on components
- Components never depend on meta-repo
- Components can depend on other components (declared in features)
- No circular dependencies allowed

## Repository Structure

```
meta-repo/
├── meta/                    # CLI tool for meta-repo management
├── manifests/                # Declarative definitions
│   ├── components.yaml      # Component registry
│   ├── features.yaml        # Feature compositions
│   └── environments.yaml    # Environment configs
├── orchestration/           # Orchestration logic (stays here)
├── features/                # Feature definitions (declarative)
├── services/                # Service composition (thin layer)
├── interfaces/               # API layer (orchestration glue)
├── presentation/             # UI applications
├── environments/             # Environment configs
├── ci/                      # System-level CI
└── tests/                   # System-level tests
```

## Component Lifecycle

### Adding a Component

1. **Define the component** in `manifests/components.yaml`:
   ```yaml
   components:
     my-component:
       repo: "git@github.com:org/my-component.git"
       version: "v1.0.0"
       type: "bazel"
       build_target: "//my_component:all"
   ```

2. **Validate the component**:
   ```bash
   meta validate --env dev
   ```

3. **Plan the addition**:
   ```bash
   meta plan --env dev
   ```

4. **Apply the component**:
   ```bash
   meta apply --env dev
   ```

5. **Test the integration**:
   ```bash
   meta test --env dev
   ```

### Updating a Component

1. Update version in `manifests/components.yaml`
2. Run `meta plan` to see changes
3. Run `meta apply` to update
4. Run `meta test` to verify

### Removing a Component

1. Remove from `manifests/components.yaml`
2. Remove from any features that reference it
3. Run `meta validate` to check for broken references
4. Remove component directory if needed

## Feature Definitions

Features are declarative compositions of components:

```yaml
features:
  my-feature:
    description: "What this feature does"
    components:
      - component-a
      - component-b
    contracts:
      - "component-a.output -> component-b.input"
    policies:
      - type: "rate-limit"
        max_requests_per_minute: 30
```

Features:
- Compose components (don't implement logic)
- Define contracts between components
- Specify policies (rate limits, compliance, etc.)
- Can depend on other features

## Environment Management

Environments are defined in `manifests/environments.yaml`:

```yaml
environments:
  dev:
    component-a: "dev"
    component-b: "dev"
  staging:
    component-a: "staging"
    component-b: "staging"
  prod:
    component-a: "prod"
    component-b: "prod"
```

Each environment can have different component versions or configurations.

## Enforcement Rules

### Automated Checks

The following are enforced via CI:

1. **No direct component imports** - Components must be consumed via packages/APIs
2. **Features must be declarative** - No complex logic in feature definitions
3. **Version bumps require tests** - System tests must pass before merging
4. **Dependency acyclicity** - No circular dependencies
5. **Contract validation** - Component contracts must be satisfied

### Manual Reviews

The following require code review:

1. New component additions
2. Feature definitions
3. Environment configurations
4. Orchestration logic changes
5. System test additions

## Testing Strategy

### Tier 1: Component Tests (in component repos)
- Unit tests
- Component-specific integration tests
- Fast, deterministic
- Required to pass before publish

### Tier 2: Contract Tests (in meta-repo)
- Validate interfaces between components
- Run on version bumps
- Catch breaking changes early

### Tier 3: System Tests (in meta-repo)
- End-to-end feature tests
- Realistic data
- Failure-mode validation
- Performance tests

## Migration Guidelines

When extracting a capability from this repo to a component:

1. **Freeze the interface** - Define explicit inputs/outputs
2. **Write contract tests** - Validate the interface
3. **Create component repo** - Copy code to new repo
4. **Publish versioned artifact** - Make it available
5. **Update meta-repo** - Replace local code with dependency
6. **Run system tests** - Verify everything still works

## Common Mistakes to Avoid

❌ **Don't add business logic to meta-repo**
- Logic belongs in components
- Meta-repo only orchestrates

❌ **Don't create circular dependencies**
- Components can't depend on meta-repo
- Features can't create cycles

❌ **Don't skip versioning**
- Always pin component versions
- Never use "latest" in production

❌ **Don't mix concerns**
- Keep orchestration separate from implementation
- Keep features declarative

❌ **Don't break interfaces**
- Maintain backward compatibility
- Version breaking changes

## Getting Help

- See `README.md` for CLI usage
- See `QUICKSTART.md` for getting started
- Check `manifests/` for examples
- Review `tests/system_tests/` for test patterns

## Questions?

If you're unsure whether something belongs in meta-repo or a component:

**Ask: "Can this be tested independently?"**
- Yes → It's a component
- No → It might be orchestration (or needs refactoring)

**Ask: "Does this compose other things?"**
- Yes → It's a feature (declarative)
- No → It might be a component

**Ask: "Does this enforce system correctness?"**
- Yes → It belongs in meta-repo
- No → It belongs in a component

---

**Remember: Correctness lives where invariants are enforced, not where features are defined.**


