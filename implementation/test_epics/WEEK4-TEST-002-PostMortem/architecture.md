# Architecture: User Search and Filtering

**Epic ID**: WEEK4-TEST-002-PostMortem

## Design Decisions

### Query Builder Pattern
- **Choice**: Separate query builder class from repository
- **Rationale**: Testable query construction, reusable across endpoints
- **Trade-offs**: More classes but better separation of concerns

### Filter Composition
- **Choice**: Filters compose with AND logic by default
- **Rationale**: Most common use case, simpler implementation
- **Trade-offs**: OR logic requires future extension

### Pagination Strategy
- **Choice**: Offset-based pagination (page number + page size)
- **Rationale**: Simple, predictable, sufficient for current scale
- **Trade-offs**: Cursor-based would be better for very large datasets

### API Design
- **Choice**: Single endpoint with query parameters
- **Rationale**: RESTful, follows convention, easy to use
- **Trade-offs**: Many query params vs POST body with filters object

## Component Interactions

```
API Request → SearchController → UserSearchService → QueryBuilder → Database
                                         ↓
                                  PaginatedResult
```

### Components

**Backend Domain**:
1. **query_builder.py**: SQL query construction
   - `UserQueryBuilder` class
   - Methods: `filter_by_name()`, `filter_by_email_domain()`, `filter_by_age_range()`, `filter_by_status()`
   - Method: `build()` returns SQL query + params

2. **search_service.py**: Business logic
   - `UserSearchService` class
   - Method: `search(filters, page, page_size)` returns `PaginatedResult`
   - Orchestrates query builder and repository

3. **repository.py**: Database access (MODIFY existing)
   - Add `search(query, params)` method
   - Add `count(query, params)` method

**API Domain**:
4. **search_controller.py**: HTTP endpoint
   - `GET /api/users/search` endpoint
   - Parse query parameters (name, email_domain, min_age, max_age, status, page, page_size)
   - Call `UserSearchService.search()`
   - Return JSON response

5. **schemas.py**: Request/response models
   - `SearchFilters` dataclass
   - `PaginatedResult` dataclass
   - `UserResponse` dataclass

**Tests Domain**:
6. **test_query_builder.py**: Query builder tests
7. **test_search_service.py**: Service layer tests
8. **test_search_api.py**: API endpoint integration tests

## Data Flow

1. Client sends GET request with query parameters
2. Controller parses parameters into `SearchFilters`
3. Service validates filters and calls query builder
4. Query builder constructs SQL with all active filters
5. Repository executes query and count query
6. Service wraps results in `PaginatedResult`
7. Controller serializes to JSON and returns

## Testing Strategy

**Unit Tests**:
- Query builder constructs correct SQL for each filter
- Service correctly handles edge cases (no filters, invalid page)
- Each filter works independently

**Integration Tests**:
- Combined filters work correctly
- Pagination returns correct results
- Empty result sets handled properly
- API returns correct HTTP status codes

**Edge Cases**:
- Empty database
- Page number beyond available pages
- Conflicting filters (e.g., min_age > max_age)
- Special characters in name search
