# API Documentation with Examples

## Authentication API

### Login

**Endpoint**: `POST /api/auth/login`

**Description**: Authenticate a user and receive a JWT token.

#### Request

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

```python
# Python
import requests

response = requests.post(
    'http://localhost:5000/api/auth/login',
    json={
        'email': 'student@example.com',
        'password': 'password123'
    }
)
token = response.json()['token']
```

```javascript
// JavaScript (Node.js)
const axios = require('axios');

const response = await axios.post('http://localhost:5000/api/auth/login', {
  email: 'student@example.com',
  password: 'password123'
});
const token = response.data.token;
```

```java
// Java
import java.net.http.*;
import java.net.URI;

HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:5000/api/auth/login"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(
        "{\"email\":\"student@example.com\",\"password\":\"password123\"}"
    ))
    .build();

HttpResponse<String> response = client.send(request,
    HttpResponse.BodyHandlers.ofString());
```

#### Response

```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "student@example.com",
    "name": "John Doe",
    "role": "student"
  }
}
```

---

## Submissions API

### Submit Code

**Endpoint**: `POST /api/submissions/submit`

**Description**: Submit code for grading.

**Authentication**: Required (JWT token)

#### Request

```bash
curl -X POST http://localhost:5000/api/submissions/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
    "language": "python",
    "assignment_id": "65a1b2c3d4e5f6g7h8i9j0k1"
  }'
```

```python
# Python
import requests

headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:5000/api/submissions/submit',
    headers=headers,
    json={
        'code': 'def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)',
        'language': 'python',
        'assignment_id': '65a1b2c3d4e5f6g7h8i9j0k1'
    }
)
result = response.json()
```

```javascript
// JavaScript
const response = await fetch('http://localhost:5000/api/submissions/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    code: 'def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)',
    language: 'python',
    assignment_id: '65a1b2c3d4e5f6g7h8i9j0k1'
  })
});
const result = await response.json();
```

#### Response

```json
{
  "status": "success",
  "data": {
    "submission_id": "65a1b2c3d4e5f6g7h8i9j0k2",
    "score": 95,
    "test_results": [
      {
        "test_name": "test_factorial_base_case",
        "passed": true,
        "output": "1"
      },
      {
        "test_name": "test_factorial_recursive",
        "passed": true,
        "output": "120"
      }
    ],
    "feedback": {
      "correctness": "Your solution is correct!",
      "quality": "Good code structure and naming.",
      "efficiency": "Time complexity: O(n), Space complexity: O(n)"
    },
    "plagiarism": {
      "passed": true,
      "similarity_score": 12.5
    },
    "gamification": {
      "points_awarded": 100,
      "achievements_unlocked": ["First Submission"],
      "new_rank": 42
    }
  }
}
```

---

## Gamification API

### Get Leaderboard

**Endpoint**: `GET /api/gamification/leaderboard`

**Description**: Get the current leaderboard.

#### Request

```bash
curl -X GET http://localhost:5000/api/gamification/leaderboard \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

```python
# Python
response = requests.get(
    'http://localhost:5000/api/gamification/leaderboard',
    headers={'Authorization': f'Bearer {token}'}
)
leaderboard = response.json()['data']
```

```javascript
// JavaScript
const response = await fetch('http://localhost:5000/api/gamification/leaderboard', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const leaderboard = await response.json();
```

#### Response

```json
{
  "status": "success",
  "data": [
    {
      "rank": 1,
      "user_id": "507f1f77bcf86cd799439011",
      "name": "Alice Johnson",
      "points": 2450,
      "submissions": 15,
      "achievements": 12
    },
    {
      "rank": 2,
      "user_id": "507f1f77bcf86cd799439012",
      "name": "Bob Smith",
      "points": 2100,
      "submissions": 14,
      "achievements": 10
    }
  ],
  "my_rank": 42,
  "total_users": 150
}
```

---

## Plagiarism API

### Check for Plagiarism

**Endpoint**: `POST /api/plagiarism/check`

**Description**: Check a submission for plagiarism.

**Authentication**: Required (Lecturer/Admin only)

#### Request

```bash
curl -X POST http://localhost:5000/api/plagiarism/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "submission_id": "65a1b2c3d4e5f6g7h8i9j0k2",
    "assignment_id": "65a1b2c3d4e5f6g7h8i9j0k1"
  }'
```

```python
# Python
response = requests.post(
    'http://localhost:5000/api/plagiarism/check',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'submission_id': '65a1b2c3d4e5f6g7h8i9j0k2',
        'assignment_id': '65a1b2c3d4e5f6g7h8i9j0k1'
    }
)
```

#### Response

```json
{
  "status": "success",
  "data": {
    "submission_id": "65a1b2c3d4e5f6g7h8i9j0k2",
    "similarity_score": 87.5,
    "flagged": true,
    "matches": [
      {
        "submission_id": "65a1b2c3d4e5f6g7h8i9j0k3",
        "student_name": "Jane Doe",
        "similarity": 87.5,
        "common_patterns": [
          "identical variable naming",
          "similar algorithm structure"
        ]
      }
    ],
    "visualization_url": "/api/plagiarism/heatmap/65a1b2c3d4e5f6g7h8i9j0k2"
  }
}
```

---

## Analytics API

### Get Student Analytics

**Endpoint**: `GET /api/dashboard/analytics`

**Description**: Get analytics for the current user.

#### Request

```bash
curl -X GET http://localhost:5000/api/dashboard/analytics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

```python
# Python
response = requests.get(
    'http://localhost:5000/api/dashboard/analytics',
    headers={'Authorization': f'Bearer {token}'}
)
analytics = response.json()['data']
```

#### Response

```json
{
  "status": "success",
  "data": {
    "total_submissions": 15,
    "average_score": 87.5,
    "improvement_trend": "+12% this month",
    "performance_by_language": {
      "python": 92.3,
      "java": 85.0,
      "cpp": 81.5
    },
    "recent_achievements": [
      {
        "name": "Perfect Score",
        "earned_at": "2025-11-25T10:30:00Z",
        "points": 500
      }
    ],
    "weak_areas": [
      "Recursion",
      "Dynamic Programming"
    ],
    "strong_areas": [
      "Arrays",
      "Sorting Algorithms"
    ]
  }
}
```

---

## Rate Limiting

All API endpoints are rate-limited. Limits vary by user role:

- **Students**: 200 requests/hour
- **Lecturers**: 500 requests/hour
- **Admins**: 1000 requests/hour
- **Anonymous**: 50 requests/hour

### Rate Limit Headers

```
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 195
X-RateLimit-Reset: 1703692800
```

### Rate Limit Exceeded Response

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 3600
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "status": "error",
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "code": ["Code cannot be empty"],
    "language": ["Language must be one of: python, java, cpp, c, javascript"]
  }
}
```

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | BadRequest | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | NotFound | Resource not found |
| 429 | TooManyRequests | Rate limit exceeded |
| 500 | InternalServerError | Server error |

---

## Postman Collection

Download the complete Postman collection:

[Download Postman Collection](./postman_collection.json)

Import into Postman and set the following environment variables:
- `base_url`: http://localhost:5000
- `auth_token`: Your JWT token

---

## WebSocket Events

### Real-Time Grading Updates

```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to server');
  socket.emit('authenticate', { token: 'YOUR_JWT_TOKEN' });
});

socket.on('grading_complete', (data) => {
  console.log('Grading complete:', data);
  // data: { submission_id, score, feedback }
});

socket.on('achievement_unlocked', (data) => {
  console.log('Achievement unlocked:', data);
  // data: { achievement_name, points, description }
});
```

---

## Pagination

List endpoints support pagination:

```bash
curl -X GET "http://localhost:5000/api/submissions?page=2&limit=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response includes pagination metadata:

```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "current_page": 2,
    "total_pages": 10,
    "total_items": 200,
    "items_per_page": 20,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## Testing with curl

### Complete Workflow Example

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"password123"}' \
  | jq -r '.token')

# 2. Submit code
SUBMISSION_ID=$(curl -s -X POST http://localhost:5000/api/submissions/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "language": "python",
    "assignment_id": "test123"
  }' | jq -r '.data.submission_id')

# 3. Check leaderboard
curl -X GET http://localhost:5000/api/gamification/leaderboard \
  -H "Authorization: Bearer $TOKEN" | jq
```
