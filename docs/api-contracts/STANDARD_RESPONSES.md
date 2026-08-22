# API Contracts

Standard API response formats and error handling for ERP03 services.

## Base Response Format

All successful responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Paginated Response Format

For list endpoints:

```json
{
  "success": true,
  "data": [
    { ...item1 },
    { ...item2 }
  ],
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_items": 150,
      "total_pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## Error Response Format

All error responses follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH requests |
| 201 | Created | Successful POST request creating a resource |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid request syntax or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Service temporarily unavailable |

## Error Codes

### Authentication & Authorization

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required |
| `INVALID_TOKEN` | 401 | JWT token is invalid or expired |
| `ACCESS_DENIED` | 403 | User lacks required permissions |
| `INVALID_CREDENTIALS` | 401 | Wrong username or password |

### Validation Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request body validation failed |
| `MISSING_FIELD` | 422 | Required field is missing |
| `INVALID_FORMAT` | 422 | Field format is incorrect |
| `OUT_OF_RANGE` | 422 | Value outside acceptable range |

### Resource Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `NOT_FOUND` | 404 | Resource not found |
| `ALREADY_EXISTS` | 409 | Resource already exists |
| `CONFLICT` | 409 | Operation conflicts with current state |
| `DEPENDENT_RESOURCES` | 409 | Cannot delete due to dependencies |

### System Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INTERNAL_ERROR` | 500 | Unexpected internal error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down |
| `TIMEOUT` | 504 | Request timeout |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

## Standard Query Parameters

### Pagination

All list endpoints support:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `per_page` | integer | 20 | Items per page (max 100) |
| `sort_by` | string | varies | Field to sort by |
| `sort_order` | string | `asc` | Sort order (`asc` or `desc`) |

### Filtering

Common filter patterns:

| Pattern | Example | Description |
|---------|---------|-------------|
| Exact match | `?status=active` | Filter by exact value |
| Range | `?created_at_gte=2024-01-01` | Greater than or equal |
| Range | `?created_at_lte=2024-12-31` | Less than or equal |
| In list | `?status=in:active,pending` | Match any in list |
| Search | `?q=search+term` | Full-text search |

## API Versioning

API version is specified in the URL path:

```
/api/v1/finance/accounts
/api/v1/hcm/employees
/api/v1/scm/purchase-orders
```

Version changes occur when:
- Breaking changes to response structure
- Removing fields or endpoints
- Changing authentication mechanisms

Non-breaking changes (adding fields, new optional parameters) do not require version bump.

## Rate Limiting

Rate limits are enforced per API key:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642234567
```

When exceeded:

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please retry after 60 seconds.",
    "retry_after": 60
  }
}
```

## Idempotency

For POST requests that create resources, clients can send an idempotency key:

```
Idempotency-Key: <unique-key>
```

The server will cache the response for 24 hours and return the same response for duplicate keys.

## Example Requests

### Create Resource

**Request:**
```http
POST /api/v1/finance/accounts
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Cash Account",
  "account_number": "1000",
  "type": "asset"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "acc_123",
    "name": "Cash Account",
    "account_number": "1000",
    "type": "asset",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### List Resources

**Request:**
```http
GET /api/v1/finance/accounts?page=1&per_page=20&sort_by=created_at&sort_order=desc
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "acc_123",
      "name": "Cash Account",
      "account_number": "1000",
      "type": "asset"
    }
  ],
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### Error Response

**Response (422 Unprocessable Entity):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "account_number",
        "message": "Account number must be numeric"
      },
      {
        "field": "type",
        "message": "Must be one of: asset, liability, equity, revenue, expense"
      }
    ]
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Module-Specific Contracts

See individual module documentation for specific endpoint details:
- [Finance API](./api-finance.md)
- [HCM API](./api-hcm.md)
- [SCM API](./api-scm.md)
- [Manufacturing API](./api-mfg.md)
- [CRM API](./api-crm.md)
