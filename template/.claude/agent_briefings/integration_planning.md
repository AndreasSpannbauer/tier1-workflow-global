# Integration Planning - Domain Briefing

**Domain**: Epic Integration Analysis
**Agent**: `integration_planning_agent_v1`
**Version**: 1.0
**Last Updated**: 2025-10-23

---

## Purpose of Integration Planning

Integration planning answers two critical questions:

1. **Backward Integration**: How does this epic connect to what we've already built?
2. **Forward Integration**: How will future epics connect to what we're building now?

Without integration planning, epics become isolated silos. Components get duplicated, APIs are inconsistent, and technical debt accumulates rapidly.

**Integration planning prevents**:
- Breaking changes to existing code
- Duplicate implementations of shared logic
- Inconsistent patterns across features
- Coupling that makes refactoring impossible
- Integration bugs discovered late in development

---

## How to Analyze Epic Relationships

### 1. Dependency Relationships

**Depends On** (`blocked_by`):
- This epic cannot be completed without another epic's work
- Example: "User Dashboard" depends on "Authentication System"
- Look for: Imports, API calls, database models, shared configuration

**Blocks** (`blocks`):
- Another epic cannot proceed until this one is complete
- Example: "Authentication System" blocks "User Dashboard"
- Look for: Foundation features, APIs, data models, infrastructure

**Integrates With** (`integrates_with`):
- This epic and another share components or collaborate
- Example: "Notification Service" integrates with "Email System" and "SMS System"
- Look for: Shared services, coordinated features, data flow between features

### 2. Tag-Based Discovery

Tags categorize epics by domain. Related epics often share tags:

**Common Tags**:
- `backend`: Server-side logic, APIs, databases
- `frontend`: UI components, user interactions
- `auth`: Authentication, authorization, security
- `data`: Data pipelines, ETL, analytics
- `infrastructure`: Deployment, monitoring, DevOps
- `refactoring`: Code quality, technical debt

**Discovery Strategy**:
1. Find epics with matching tags (same domain)
2. Read their `spec.md` to understand what they do
3. Read their `architecture.md` to see how they work
4. Identify shared components, APIs, data models

### 3. Post-Mortem Mining

Past `post_mortem.md` files contain:
- **Integration lessons**: "We should have versioned the API"
- **Common patterns**: "Always use centralized logging"
- **Technical debt**: "Database schema changes caused downtime"
- **Best practices**: "Feature flags enabled safe rollout"

**Mining Strategy**:
1. Find all `post_mortem.md` files in `.tasks/completed/*/`
2. Search for integration-related keywords: "API", "breaking change", "dependency", "migration"
3. Extract lessons learned
4. Apply to current epic's integration plan

---

## Common Integration Patterns

### Pattern 1: Shared Service Integration

**Scenario**: Epic creates a service that multiple features use

**Example**: EPIC-002 creates `NotificationService`

**Backward Integration**:
- None (first to implement notifications)

**Forward Integration**:
- EPIC-005 (User Dashboard) needs notifications → Add as dependency
- EPIC-007 (Admin Panel) needs notifications → Add as dependency
- Document API: `send_email(user, template, context)`
- Provide usage examples

**Key Points**:
- Create clear API documentation
- Provide integration examples
- Version the API from the start
- List all future epics that will use it

### Pattern 2: Feature Extension Integration

**Scenario**: Epic extends an existing feature

**Example**: EPIC-004 adds "notification preferences" to existing user settings (EPIC-002)

**Backward Integration**:
- Update EPIC-002's `UserSettings` model (add `notification_preferences` field)
- Update EPIC-002's settings UI (add new tab)
- Update EPIC-002's API (add endpoints for preferences)

**Forward Integration**:
- EPIC-006 (scheduled reports) checks preferences before sending
- EPIC-008 (mobile app) syncs preferences

**Key Points**:
- Minimize changes to existing code
- Follow existing patterns (UI layout, API design)
- Backward compatibility if possible
- Update documentation in original epic

### Pattern 3: Data Model Evolution Integration

**Scenario**: Epic adds/modifies database schema

**Example**: EPIC-005 adds `last_login` field to User model (from EPIC-001)

**Backward Integration**:
- Database migration script (add column with default value)
- Update EPIC-001's User model class
- Update EPIC-001's queries (select new field)
- Update existing tests

**Forward Integration**:
- All future epics use updated User model
- Document migration process
- Note: Schema is versioned, use `last_login` safely

**Key Points**:
- Always write migration scripts (up and down)
- Default values for existing rows
- Update ORM models immediately
- Test backward compatibility

### Pattern 4: API Versioning Integration

**Scenario**: Epic changes an existing API

**Example**: EPIC-006 adds pagination to `/users` endpoint (from EPIC-001)

**Backward Integration**:
- Keep old endpoint: `GET /api/v1/users` (returns all)
- New endpoint: `GET /api/v2/users?page=1&limit=20` (paginated)
- Deprecation warning in v1 response headers
- Update EPIC-001's API documentation

**Forward Integration**:
- All future epics use v2 API
- Document migration path from v1 to v2
- Set deprecation timeline for v1

**Key Points**:
- Never break existing APIs
- Version URLs (`/api/v1/`, `/api/v2/`)
- Deprecate old versions gracefully
- Communicate timeline to clients

### Pattern 5: Configuration Integration

**Scenario**: Epic adds configuration options

**Example**: EPIC-007 adds email templates configuration

**Backward Integration**:
- Update `.env.example` with new variables
- Update config parsing code
- Provide default values
- Update deployment documentation

**Forward Integration**:
- Document all config options
- Provide validation
- All future epics follow same config pattern

**Key Points**:
- Always provide defaults
- Document in `.env.example`
- Validate on startup
- Consider environment-specific configs

---

## How to Prioritize Integration Tasks

### Priority Levels

**High Priority** (must be done BEFORE this epic deploys):
- Blocking dependencies (epic cannot function without this)
- Breaking changes (existing code will fail without this)
- Security-critical integrations
- Data integrity issues

**Medium Priority** (should be done WITH this epic):
- Important but non-blocking integrations
- Performance optimizations
- User experience improvements
- Documentation updates

**Low Priority** (can be done AFTER this epic):
- Technical debt reduction
- Code cleanup
- Nice-to-have features
- Refactoring opportunities

### Effort Estimation Guidelines

**Small (< 1 hour)**:
- Add a method to existing service
- Update documentation
- Add configuration variable
- Write a simple test

**Medium (1-4 hours)**:
- Add API endpoint
- Extend data model (with migration)
- Update UI component
- Refactor small module

**Large (4-8 hours)**:
- Major API refactoring
- Complex data migration
- Multi-component feature
- Significant architecture change

**Extra Large (> 8 hours)**:
- Cross-system integration
- Breaking change across entire codebase
- Database schema redesign
- Consider breaking into multiple tasks

---

## Examples of Good Integration Plans

### Example 1: Simple Dependency

**Epic**: EPIC-003 "Add user logout functionality"

**Backward Integration**:
```json
{
  "related_epics": [
    {
      "epic_id": "EPIC-001",
      "epic_title": "Authentication System",
      "relationship": "extends"
    }
  ],
  "integration_tasks": [
    {
      "task": "Add logout() method to AuthService",
      "epic_reference": "EPIC-001",
      "priority": "high",
      "estimated_effort": "1 hour",
      "files_to_modify": [
        "src/services/auth_service.py",
        "tests/test_auth_service.py"
      ],
      "rationale": "Logout needs to invalidate session tokens"
    }
  ]
}
```

**Forward Integration**:
```json
{
  "future_epic_updates": [
    {
      "epic_id": "EPIC-004",
      "epic_title": "User Dashboard",
      "update_type": "integration_note",
      "description": "Dashboard should call logout() on 'Sign Out' button click",
      "reference_files": ["src/services/auth_service.py"]
    }
  ]
}
```

### Example 2: Complex Integration

**Epic**: EPIC-008 "Notification Service"

**Backward Integration**:
```json
{
  "related_epics": [
    {
      "epic_id": "EPIC-001",
      "epic_title": "Authentication System",
      "relationship": "depends_on"
    },
    {
      "epic_id": "EPIC-005",
      "epic_title": "Email System",
      "relationship": "integrates_with"
    }
  ],
  "integration_tasks": [
    {
      "task": "Extend User model to include notification_preferences",
      "epic_reference": "EPIC-001",
      "priority": "high",
      "estimated_effort": "3 hours",
      "files_to_modify": [
        "src/models/user.py",
        "migrations/add_notification_preferences.sql",
        "tests/test_user_model.py"
      ]
    },
    {
      "task": "Refactor EmailSystem to expose send_template() method",
      "epic_reference": "EPIC-005",
      "priority": "medium",
      "estimated_effort": "4 hours",
      "files_to_modify": [
        "src/services/email_service.py"
      ],
      "rationale": "NotificationService needs templated email sending"
    }
  ],
  "integration_risks": [
    {
      "risk": "Email service API change might affect existing callers",
      "mitigation": "Add new method without modifying existing send() method",
      "severity": "medium"
    }
  ]
}
```

**Forward Integration**:
```json
{
  "reusable_components": [
    {
      "component": "NotificationService",
      "location": "src/services/notification_service.py",
      "description": "Centralized service for all user notifications (email, SMS, in-app)",
      "usage_example": "notification_service.notify(user, 'new_message', context={'sender': 'Alice'})"
    }
  ],
  "future_epic_updates": [
    {
      "epic_id": "EPIC-010",
      "epic_title": "Scheduled Reports",
      "update_type": "dependency",
      "description": "Add EPIC-008 as dependency for sending report notifications"
    },
    {
      "epic_id": "EPIC-012",
      "epic_title": "Mobile App Push Notifications",
      "update_type": "integration_note",
      "description": "Extend NotificationService to support push notifications"
    }
  ],
  "integration_patterns": [
    {
      "pattern": "Always check user notification preferences before sending",
      "rationale": "Respects user choices, reduces spam complaints"
    }
  ]
}
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Vague Integration Tasks

**Bad**:
```json
{
  "task": "Integrate with authentication",
  "priority": "high"
}
```

**Good**:
```json
{
  "task": "Add checkPermission('admin') call before dashboard data load",
  "epic_reference": "EPIC-001",
  "priority": "high",
  "estimated_effort": "30 minutes",
  "files_to_modify": ["src/components/Dashboard.tsx"]
}
```

### ❌ Mistake 2: Missing File Paths

**Bad**:
```json
{
  "task": "Update the user model"
}
```

**Good**:
```json
{
  "task": "Add last_login field to User model",
  "files_to_modify": [
    "src/models/user.py",
    "migrations/add_last_login.sql",
    "tests/test_user_model.py"
  ]
}
```

### ❌ Mistake 3: Ignoring Past Lessons

**Bad**: Not consulting post-mortems, repeating past mistakes

**Good**: Read past post-mortems, apply lessons:
```json
{
  "post_mortem_insights": [
    {
      "lesson": "API versioning prevented breaking changes in EPIC-003",
      "applied_to": "backward_integration",
      "recommendation": "Version all new endpoints as /api/v2/"
    }
  ]
}
```

### ❌ Mistake 4: No Risk Assessment

**Bad**: Only listing tasks, no risks identified

**Good**: Call out risks with mitigations:
```json
{
  "integration_risks": [
    {
      "risk": "Changing database schema requires downtime",
      "mitigation": "Use online migration with default values",
      "severity": "high"
    }
  ]
}
```

### ❌ Mistake 5: Forgetting Forward Integration

**Bad**: Only looking backward at past epics

**Good**: Documenting what future epics should know:
```json
{
  "reusable_components": [
    {
      "component": "PDFExporter",
      "location": "src/services/pdf_exporter.py",
      "description": "Export any data structure to PDF with templates"
    }
  ]
}
```

---

## Integration Planning Checklist

Before finalizing an integration plan, verify:

- [ ] **Backward Integration**
  - [ ] Identified all related past epics (by dependencies, tags, domain)
  - [ ] Listed concrete integration tasks with file paths
  - [ ] Assigned priorities and effort estimates
  - [ ] Identified integration risks and mitigations
  - [ ] Consulted past post-mortems for lessons

- [ ] **Forward Integration**
  - [ ] Documented reusable components with usage examples
  - [ ] Identified future epics that will integrate with this
  - [ ] Suggested registry updates for dependencies
  - [ ] Established integration patterns for future work

- [ ] **Quality**
  - [ ] All tasks are specific and actionable
  - [ ] File paths provided for all changes
  - [ ] Priorities match impact and blocking status
  - [ ] JSON is valid and follows schema
  - [ ] Explanations provided for unusual cases

---

## Tools and Resources

### Epic Registry Queries

```python
from tools.epic_registry import load_registry

registry = load_registry()

# Get current epic
epic = registry.get_epic("EPIC-003")

# Find related epics by status
implemented_epics = registry.get_epics_by_status("implemented")

# Find by tags
backend_epics = [e for e in registry.data.epics if "backend" in e.tags]

# Check dependencies
if epic.dependencies.blocked_by:
    print(f"This epic is blocked by: {epic.dependencies.blocked_by}")
```

### Post-Mortem Mining

```bash
# Find all post-mortems
find .tasks/completed -name "post_mortem.md"

# Search for integration keywords
grep -r "API" .tasks/completed/*/post_mortem.md
grep -r "breaking change" .tasks/completed/*/post_mortem.md
```

### Epic Discovery

```bash
# List all epics
cat .tasks/epic_registry.json | jq '.epics[] | {id: .epic_id, title: .title, status: .status}'

# Find epics by tag
cat .tasks/epic_registry.json | jq '.epics[] | select(.tags | contains(["backend"]))'
```

---

## Success Metrics

A good integration plan should result in:

- **Zero integration surprises**: No "oh, we didn't know X depended on Y" moments
- **Clear task list**: Developer can start work immediately with actionable tasks
- **Knowledge transfer**: Future developers understand how components relate
- **Reduced technical debt**: Integration patterns documented and reused
- **Faster development**: Future epics integrate smoothly by following established patterns

---

## Related Documentation

- **Agent Definition**: `.claude/agents/integration_planning_agent_v1.md`
- **Epic Registry Models**: `tools/epic_registry/models.py`
- **Execute Workflow Command**: `.claude/commands/execute-workflow.md`
- **ADR-013**: Epic Registry and Longitudinal Tracking specification
