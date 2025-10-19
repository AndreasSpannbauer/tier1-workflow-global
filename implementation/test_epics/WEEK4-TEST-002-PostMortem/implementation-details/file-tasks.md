# Implementation Plan: User Search and Filtering

**Epic ID**: WEEK4-TEST-002-PostMortem

## Domain: backend

### File 1: `src/user_search/query_builder.py` (NEW)

**Task**: Create SQL query builder for user search

**Changes**:
1. Create `UserQueryBuilder` class
2. Add `__init__(self)` - initialize empty filters list
3. Add `filter_by_name(self, name: str) -> "UserQueryBuilder"` method
   - Add SQL WHERE clause: `name ILIKE %name%`
   - Return self for chaining
4. Add `filter_by_email_domain(self, domain: str) -> "UserQueryBuilder"` method
   - Add SQL WHERE clause: `email LIKE %@domain`
   - Return self for chaining
5. Add `filter_by_age_range(self, min_age: int | None, max_age: int | None) -> "UserQueryBuilder"` method
   - Add WHERE clauses for min/max age
   - Return self for chaining
6. Add `filter_by_status(self, status: str) -> "UserQueryBuilder"` method
   - Add WHERE clause: `status = status`
   - Return self for chaining
7. Add `build(self) -> tuple[str, list]` method
   - Combine all filters with AND
   - Return (query_string, params_list)

**Notes**:
- Use proper type hints throughout
- Add docstrings for all public methods
- Clean, well-formatted code (should pass validation)

---

### File 2: `src/user_search/schemas.py` (NEW)

**Task**: Create data models for search

**Changes**:
1. Create `SearchFilters` dataclass:
   - Fields: `name: str | None`, `email_domain: str | None`, `min_age: int | None`, `max_age: int | None`, `status: str | None`
   - Add `validate()` method (check min_age <= max_age if both present)
2. Create `PaginatedResult[T]` generic dataclass:
   - Fields: `items: list[T]`, `total: int`, `page: int`, `page_size: int`, `total_pages: int`
3. Create `UserResponse` dataclass:
   - Fields: `id: int`, `name: str`, `email: str`, `age: int`, `status: str`
   - Add `from_model(user: User) -> UserResponse` classmethod

**Notes**:
- Use proper type hints (including generics for PaginatedResult)
- Add docstrings
- Clean code

---

### File 3: `src/user_search/search_service.py` (NEW)

**Task**: Implement user search business logic

**Changes**:
1. Create `UserSearchService` class
2. Add `__init__(self, repository: UserRepository)` - dependency injection
3. Add `search(self, filters: SearchFilters, page: int = 1, page_size: int = 20) -> PaginatedResult[UserResponse]` method:
   - Validate filters using `filters.validate()`
   - Create `UserQueryBuilder` and apply filters
   - Build query using `builder.build()`
   - Execute count query via repository
   - Execute search query via repository
   - Calculate total_pages
   - Convert users to `UserResponse` objects
   - Return `PaginatedResult`

**Notes**:
- Proper error handling for invalid page numbers
- Type hints and docstrings
- Clean code

---

### File 4: `src/user_repository/repository.py` (MODIFY)

**Task**: Add search methods to existing UserRepository

**Existing Code**:
```python
class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all(self) -> list[User]:
        # existing implementation
        pass

    def get_by_id(self, user_id: int) -> User | None:
        # existing implementation
        pass
```

**Changes**:
1. Add `search(self, query: str, params: list, limit: int, offset: int) -> list[User]` method
   - Execute query with params, limit, offset
   - Return list of User objects
2. Add `count(self, query: str, params: list) -> int` method
   - Execute count query with same filters
   - Return total count

**Notes**:
- Maintain existing method signatures
- Add proper type hints to new methods
- Clean, consistent code style

---

## Domain: api

### File 5: `src/api/search_controller.py` (NEW)

**Task**: Create REST API endpoint for user search

**Changes**:
1. Import FastAPI router, SearchFilters, UserSearchService
2. Create `router = APIRouter(prefix="/api/users")`
3. Add `GET /search` endpoint:
   - Query params: `name: str | None`, `email_domain: str | None`, `min_age: int | None`, `max_age: int | None`, `status: str | None`, `page: int = 1`, `page_size: int = 20`
   - Create `SearchFilters` from query params
   - Call `UserSearchService.search()`
   - Return JSON response with `PaginatedResult`
4. Add error handling for validation errors (400 Bad Request)

**Notes**:
- RESTful API design
- Proper HTTP status codes
- Type hints on all route handlers
- Clean code

---

### File 6: `src/api/main.py` (MODIFY)

**Task**: Register search router

**Existing Code**:
```python
from fastapi import FastAPI

app = FastAPI()

# existing routes
```

**Changes**:
1. Import `search_controller`
2. Add `app.include_router(search_controller.router)`

**Notes**:
- Minimal change, just router registration

---

## Domain: tests

### File 7: `tests/unit/test_query_builder.py` (NEW)

**Task**: Test query builder logic

**Changes**:
1. Test `filter_by_name()` constructs correct SQL
2. Test `filter_by_email_domain()` constructs correct SQL
3. Test `filter_by_age_range()` with min only, max only, both
4. Test `filter_by_status()` constructs correct SQL
5. Test chaining multiple filters
6. Test `build()` returns correct query and params
7. Test edge cases (empty filters, special characters)

**Notes**:
- Comprehensive coverage
- Test both individual filters and combinations
- Clean, well-structured tests

---

### File 8: `tests/integration/test_search_api.py` (NEW)

**Task**: Test search API endpoint

**Changes**:
1. Test GET /api/users/search with no filters (returns all users)
2. Test name filter (partial match, case-insensitive)
3. Test email_domain filter
4. Test age_range filter
5. Test status filter
6. Test combined filters
7. Test pagination (page 1, page 2, beyond last page)
8. Test validation errors (min_age > max_age returns 400)
9. Test empty results

**Notes**:
- Use test database with known data
- Test HTTP status codes and response structure
- Clean, readable tests

---

## Implementation Notes

**Estimated Time**: 8 hours

**Order of Implementation**:
1. schemas.py (defines data models)
2. query_builder.py (query construction)
3. repository.py (database access)
4. search_service.py (business logic)
5. search_controller.py (API layer)
6. main.py (router registration)
7. test_query_builder.py (unit tests)
8. test_search_api.py (integration tests)

**Testing Strategy**:
- Unit tests for query builder (isolated, fast)
- Integration tests for API (realistic, end-to-end)
- Use test fixtures for database setup
- Run tests after each component to ensure correctness

**Validation Expectations**:
- Should PASS all validation checks on first try
- Clean code with proper type hints, docstrings, formatting
- Purpose: Test post-mortem generation, not validation retry
- Post-mortem should analyze multi-domain implementation
