# Implementation Plan: User Profile Validation

**Epic ID**: WEEK4-TEST-001-ValidationRetry

## Domain: backend

### File 1: `src/user_profile/exceptions.py` (NEW)

**Task**: Create custom validation exception hierarchy

**Changes**:
1. Create `ValidationError` base exception class
2. Create `EmailValidationError(ValidationError)`
3. Create `AgeValidationError(ValidationError)`
4. Create `BioValidationError(ValidationError)`
5. Each exception should accept and store field name and value
6. Include clear error message formatting

**Validation Notes**:
- INTENTIONAL ISSUE: Missing type hints on exception __init__ methods
- Will trigger mypy/ruff validation errors

---

### File 2: `src/user_profile/validators.py` (NEW)

**Task**: Implement profile field validators

**Changes**:
1. Create `validate_email(email: str) -> None` function
   - Check email format using regex
   - Raise `EmailValidationError` if invalid
2. Create `validate_age(age: int) -> None` function
   - Check age >= 13 and <= 120
   - Raise `AgeValidationError` if out of range
3. Create `validate_bio(bio: str) -> None` function
   - Check bio length <= 500 characters
   - Raise `BioValidationError` if too long
4. Create `validate_profile(name, email, age, bio) -> dict` function
   - Call all validators, collect errors
   - Return dict of validation results

**Validation Notes**:
- INTENTIONAL ISSUE: Inconsistent spacing around operators
- INTENTIONAL ISSUE: Missing docstrings
- Will trigger ruff formatting/documentation errors

---

### File 3: `src/user_profile/models.py` (MODIFY)

**Task**: Integrate validators into UserProfile model

**Existing Code**:
```python
class UserProfile:
    def __init__(self, name, email, age, bio):
        self.name = name
        self.email = email
        self.age = age
        self.bio = bio

    def save(self):
        # TODO: add validation
        pass
```

**Changes**:
1. Import validators module
2. Add `validate()` method that calls `validate_profile()`
3. Update `save()` to call `validate()` before persisting
4. Add `to_dict()` method for serialization

**Validation Notes**:
- INTENTIONAL ISSUE: Missing return type hints on new methods

---

### File 4: `tests/test_validators.py` (NEW)

**Task**: Create comprehensive validator tests

**Changes**:
1. Test `validate_email()` with valid/invalid emails
2. Test `validate_age()` with boundary values (12, 13, 120, 121)
3. Test `validate_bio()` with short/long bios
4. Test `validate_profile()` with multiple errors
5. Test error message contents

**Validation Notes**:
- Should be mostly correct (tests usually pass validation)
- INTENTIONAL ISSUE: One test function missing type hint on parameter

---

### File 5: `tests/test_models.py` (NEW)

**Task**: Test UserProfile integration

**Changes**:
1. Test `UserProfile.validate()` calls validators correctly
2. Test `UserProfile.save()` raises errors on invalid data
3. Test `UserProfile.save()` succeeds with valid data
4. Test `to_dict()` serialization

**Validation Notes**:
- Should be clean (minimal issues to ensure some tests pass)

---

## Implementation Notes

**Estimated Time**: 4 hours

**Order of Implementation**:
1. exceptions.py (defines error types)
2. validators.py (uses exceptions)
3. models.py (uses validators)
4. test_validators.py (tests validators)
5. test_models.py (tests integration)

**Testing Strategy**:
- Run tests after each file to ensure correctness
- Validation will catch the intentional formatting/type issues
- Build fixer agent should resolve issues automatically

**Known Validation Errors** (intentional):
- Missing type hints: exceptions.py, validators.py, models.py, test_validators.py
- Missing docstrings: validators.py
- Formatting issues: validators.py (spacing)
- Total expected errors: 8-10 validation failures
