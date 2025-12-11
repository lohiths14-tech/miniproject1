# API Versioning Strategy

## Overview

This document outlines the API versioning strategy for the AI-Powered Grading System. We follow semantic versioning principles and provide backward compatibility guarantees.

## Versioning Approach

### URL-Based Versioning

We use URL path versioning for clear, explicit version identification:

```
/api/v1/resource
/api/v2/resource
```

**Benefits:**
- Clear and explicit
- Easy to route and cache
- Simple for clients to understand
- No header parsing required

### Version Format

- **Major Version**: `/api/v{major}/`
- **Full Version**: Returned in response headers and body
- **Format**: `{major}.{minor}.{patch}`

Example: `2.1.3`
- Major: 2 (breaking changes)
- Minor: 1 (new features, backward compatible)
- Patch: 3 (bug fixes)

## Version Lifecycle

### Current Versions

| Version | Status | Release Date | EOL Date | Notes |
|---------|--------|--------------|----------|-------|
| v2 | Current | 2025-11-30 | TBD | Latest features |
| v1 | Supported | 2025-01-01 | 2026-06-30 | Legacy support |

### Version States

1. **Development** - In active development, not production-ready
2. **Current** - Latest stable version, recommended for new integrations
3. **Supported** - Maintained for bug fixes and security updates
4. **Deprecated** - No new features, security updates only
5. **End of Life (EOL)** - No longer supported

### Deprecation Policy

- **Notice Period**: 6 months minimum before EOL
- **Communication**: Email, documentation, response headers
- **Migration Guide**: Provided for all breaking changes

## Breaking vs Non-Breaking Changes

### Breaking Changes (Require Major Version Bump)

- Removing endpoints
- Removing request/response fields
- Changing field types
- Changing authentication methods
- Changing error response formats
- Renaming fields
- Making optional fields required

### Non-Breaking Changes (Minor/Patch Version)

- Adding new endpoints
- Adding optional request fields
- Adding response fields
- Adding new error codes
- Performance improvements
- Bug fixes
- Documentation updates

## API Endpoints by Version

### Version 1 (v1) - Legacy

**Base URL**: `/api/v1`

**Core Endpoints:**
```
GET  /api/v1/health          - Health check
GET  /api/v1/info            - API information
POST /api/v1/auth/signup     - User registration
POST /api/v1/auth/login      - User login
POST /api/v1/submissions     - Submit code
GET  /api/v1/submissions     - List submissions
GET  /api/v1/assignments     - List assignments
```

**Features:**
- Basic authentication
- Standard grading
- Simple plagiarism detection

### Version 2 (v2) - Current

**Base URL**: `/api/v2`

**Enhanced Endpoints:**
```
GET  /api/v2/health          - Enhanced health check
GET  /api/v2/info            - Detailed API info with breaking changes
POST /api/v2/auth/signup     - Enhanced registration with validation
POST /api/v2/auth/login      - Login with MFA support
POST /api/v2/submissions     - Submit with real-time feedback
GET  /api/v2/submissions     - List with advanced filtering
GET  /api/v2/assignments     - List with pagination
GET  /api/v2/analytics       - NEW: Analytics dashboard
POST /api/v2/collaboration   - NEW: Collaboration sessions
```

**New Features:**
- Multi-factor authentication
- Real-time grading feedback
- Advanced plagiarism detection
- Collaboration features
- Analytics and insights
- Rate limiting improvements

## Version Negotiation

### 1. URL Path (Recommended)

```http
GET /api/v2/submissions HTTP/1.1
Host: api.example.com
```

### 2. Accept Header (Alternative)

```http
GET /api/submissions HTTP/1.1
Host: api.example.com
Accept: application/vnd.aigrader.v2+json
```

### 3. Custom Header (Fallback)

```http
GET /api/submissions HTTP/1.1
Host: api.example.com
API-Version: v2
```

## Response Headers

All API responses include version information:

```http
HTTP/1.1 200 OK
API-Version: 2.1.3
API-Deprecated: false
API-Sunset: 2026-06-30
Content-Type: application/json
```

**Headers:**
- `API-Version`: Current API version
- `API-Deprecated`: Boolean indicating deprecation status
- `API-Sunset`: Date when version will be EOL (if deprecated)

## Error Responses

### Version Not Found

```json
{
  "error": "version_not_found",
  "message": "API version v3 does not exist",
  "available_versions": ["v1", "v2"],
  "current_version": "v2"
}
```

### Version Deprecated

```json
{
  "error": "version_deprecated",
  "message": "API version v1 is deprecated",
  "sunset_date": "2026-06-30",
  "migration_guide": "https://docs.example.com/migration/v1-to-v2",
  "current_version": "v2"
}
```

## Migration Guide

### Migrating from v1 to v2

#### 1. Authentication Changes

**v1:**
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

**v2:**
```json
POST /api/v2/auth/login
{
  "email": "user@example.com",
  "password": "password123",
  "mfa_code": "123456"  // Optional, required if MFA enabled
}
```

#### 2. Submission Response Format

**v1:**
```json
{
  "id": "123",
  "status": "graded",
  "score": 85
}
```

**v2:**
```json
{
  "id": "123",
  "status": "graded",
  "score": 85,
  "feedback": {
    "ai_analysis": "...",
    "suggestions": [...]
  },
  "plagiarism": {
    "similarity_score": 15,
    "flagged": false
  }
}
```

#### 3. Pagination

**v1:** No pagination (returns all results)

**v2:** Cursor-based pagination
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "abc123",
    "has_more": true,
    "total": 150
  }
}
```

## Best Practices for Clients

### 1. Always Specify Version

```javascript
// Good
const response = await fetch('/api/v2/submissions');

// Bad - relies on default
const response = await fetch('/api/submissions');
```

### 2. Handle Version Deprecation

```javascript
const response = await fetch('/api/v1/submissions');
const deprecated = response.headers.get('API-Deprecated');
const sunsetDate = response.headers.get('API-Sunset');

if (deprecated === 'true') {
  console.warn(`API v1 will be sunset on ${sunsetDate}`);
  // Trigger migration workflow
}
```

### 3. Graceful Degradation

```javascript
async function getSubmissions() {
  try {
    // Try v2 first
    return await fetch('/api/v2/submissions');
  } catch (error) {
    if (error.status === 404) {
      // Fallback to v1
      return await fetch('/api/v1/submissions');
    }
    throw error;
  }
}
```

### 4. Version Discovery

```javascript
// Get available versions
const info = await fetch('/api/v2/info').then(r => r.json());
console.log('Available versions:', info.available_versions);
console.log('Current version:', info.api_version);
```

## Testing Strategy

### 1. Version-Specific Tests

```python
# tests/test_api/test_v1_endpoints.py
def test_v1_health():
    response = client.get('/api/v1/health')
    assert response.json['version'] == 'v1'

# tests/test_api/test_v2_endpoints.py
def test_v2_health():
    response = client.get('/api/v2/health')
    assert response.json['version'] == 'v2'
    assert 'enhanced_features' in response.json
```

### 2. Backward Compatibility Tests

```python
def test_v1_still_works_after_v2_release():
    """Ensure v1 endpoints remain functional"""
    v1_response = client.get('/api/v1/submissions')
    assert v1_response.status_code == 200
```

### 3. Migration Tests

```python
def test_v1_to_v2_data_compatibility():
    """Ensure data from v1 works in v2"""
    v1_data = get_v1_submission()
    v2_response = client.post('/api/v2/submissions', json=v1_data)
    assert v2_response.status_code == 200
```

## Implementation Checklist

- [x] URL-based versioning implemented
- [x] Version headers in responses
- [x] v1 endpoints functional
- [x] v2 endpoints with enhanced features
- [x] Version negotiation support
- [x] Error responses for invalid versions
- [x] Deprecation warnings
- [ ] Migration guide published
- [ ] Client SDKs updated
- [ ] Documentation complete
- [ ] Monitoring and analytics

## Monitoring

### Metrics to Track

1. **Version Usage**
   - Requests per version
   - Active clients per version
   - Version adoption rate

2. **Deprecation Impact**
   - Clients still using deprecated versions
   - Migration progress
   - Support ticket volume

3. **Performance**
   - Response times per version
   - Error rates per version
   - Cache hit rates

### Alerts

- Alert when deprecated version usage exceeds threshold
- Alert 30 days before EOL date
- Alert on version-specific error spikes

## Support

### Documentation
- API Reference: `/docs/api/`
- Migration Guides: `/docs/migrations/`
- Changelog: `/docs/changelog/`

### Contact
- Technical Support: support@example.com
- API Issues: api-issues@example.com
- Slack: #api-support

## Changelog

### v2.0.0 (2025-11-30)
- Added MFA support
- Enhanced submission feedback
- Added collaboration endpoints
- Improved pagination
- Added analytics endpoints

### v1.0.0 (2025-01-01)
- Initial release
- Basic authentication
- Code submission and grading
- Assignment management
- Simple plagiarism detection

---

**Last Updated**: 2025-11-30
**Document Version**: 1.0
**Status**: Active
