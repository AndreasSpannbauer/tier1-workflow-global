# Architecture: User Profile Validation

**Epic ID**: WEEK4-TEST-001-ValidationRetry

## Design Decisions

### Validation Strategy
- **Choice**: Explicit validator functions over Pydantic
- **Rationale**: Demonstrates custom validation logic for testing purposes
- **Trade-offs**: More code but clearer validation flow

### Error Handling
- **Choice**: Custom exception hierarchy (ValidationError base class)
- **Rationale**: Allows specific error handling per validation type
- **Trade-offs**: More classes but better error granularity

### Batch Processing
- **Choice**: Collect all validation errors before raising
- **Rationale**: Better UX - show all issues at once
- **Trade-offs**: Slightly more complex error aggregation logic

## Component Interactions

```
User Input → Validator → Profile Model → Database
                ↓
          ValidationError (if invalid)
```

### Components

1. **validators.py**: Core validation logic
   - Field-level validators (email, age, bio length)
   - Batch validation orchestrator

2. **exceptions.py**: Custom exception classes
   - `ValidationError` (base)
   - `EmailValidationError`
   - `AgeValidationError`
   - `BioValidationError`

3. **models.py**: User profile model
   - Integrates validators before save
   - Exposes validation API

4. **test_validators.py**: Comprehensive test suite
   - Field validator tests
   - Batch validation tests
   - Error message validation

## Data Flow

1. Client submits profile data
2. Validator checks each field
3. Errors collected (if any)
4. All errors raised together OR profile marked valid
5. Valid profiles persist to database

## Testing Strategy

- Unit tests for each validator function
- Integration tests for batch validation
- Edge cases (empty strings, boundary values, malformed input)
- Error message content validation
