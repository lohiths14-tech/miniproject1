"""
Mock objects and helpers for testing external dependencies
"""
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List


class MockOpenAI:
    """Mock OpenAI API for testing"""

    def __init__(self, response_data=None):
        self.response_data = response_data or {
            'score': 85,
            'feedback': 'Good code quality',
            'suggestions': ['Add error handling', 'Improve variable names']
        }
        self.call_count = 0
        self.last_request = None

    def create_completion(self, **kwargs):
        """Mock completion creation"""
        self.call_count += 1
        self.last_request = kwargs

        return Mock(
            choices=[
                Mock(
                    message=Mock(
                        content=str(self.response_data)
                    )
                )
            ]
        )

    def reset(self):
        """Reset mock state"""
        self.call_count = 0
        self.last_request = None


class MockEmail:
    """Mock email service for testing"""

    def __init__(self):
        self.sent_emails = []
        self.should_fail = False

    def send(self, message):
        """Mock email sending"""
        if self.should_fail:
            raise Exception("Email sending failed")

        self.sent_emails.append({
            'to': message.recipients,
            'subject': message.subject,
            'body': message.body,
            'html': message.html
        })

    def get_sent_count(self):
        """Get count of sent emails"""
        return len(self.sent_emails)

    def get_last_email(self):
        """Get last sent email"""
        return self.sent_emails[-1] if self.sent_emails else None

    def reset(self):
        """Reset mock state"""
        self.sent_emails = []
        self.should_fail = False


class MockRedis:
    """Mock Redis client for testing"""

    def __init__(self):
        self.data = {}
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key):
        """Mock get operation"""
        if key in self.data:
            self.hit_count += 1
            return self.data[key]
        self.miss_count += 1
        return None

    def set(self, key, value, ex=None):
        """Mock set operation"""
        self.data[key] = value
        return True

    def delete(self, key):
        """Mock delete operation"""
        if key in self.data:
            del self.data[key]
            return 1
        return 0

    def flushdb(self):
        """Mock flush database"""
        self.data = {}
        return True

    def exists(self, key):
        """Mock exists check"""
        return key in self.data

    def get_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return (self.hit_count / total) * 100

    def reset(self):
        """Reset mock state"""
        self.data = {}
        self.hit_count = 0
        self.miss_count = 0


class MockMongoDB:
    """Mock MongoDB client for testing"""

    def __init__(self):
        self.collections = {}

    def __getitem__(self, collection_name):
        """Get or create collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = MockCollection()
        return self.collections[collection_name]

    def list_collection_names(self):
        """List all collections"""
        return list(self.collections.keys())

    def reset(self):
        """Reset all collections"""
        self.collections = {}


class MockCollection:
    """Mock MongoDB collection"""

    def __init__(self):
        self.documents = []
        self.next_id = 1

    def insert_one(self, document):
        """Mock insert one document"""
        doc = document.copy()
        doc['_id'] = self.next_id
        self.next_id += 1
        self.documents.append(doc)
        return Mock(inserted_id=doc['_id'])

    def insert_many(self, documents):
        """Mock insert many documents"""
        inserted_ids = []
        for doc in documents:
            result = self.insert_one(doc)
            inserted_ids.append(result.inserted_id)
        return Mock(inserted_ids=inserted_ids)

    def find_one(self, query):
        """Mock find one document"""
        for doc in self.documents:
            if self._matches_query(doc, query):
                return doc
        return None

    def find(self, query=None):
        """Mock find documents"""
        if query is None:
            return self.documents.copy()
        return [doc for doc in self.documents if self._matches_query(doc, query)]

    def update_one(self, query, update):
        """Mock update one document"""
        for doc in self.documents:
            if self._matches_query(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                return Mock(modified_count=1)
        return Mock(modified_count=0)

    def delete_one(self, query):
        """Mock delete one document"""
        for i, doc in enumerate(self.documents):
            if self._matches_query(doc, query):
                self.documents.pop(i)
                return Mock(deleted_count=1)
        return Mock(deleted_count=0)

    def count_documents(self, query=None):
        """Mock count documents"""
        if query is None:
            return len(self.documents)
        return len([doc for doc in self.documents if self._matches_query(doc, query)])

    def drop(self):
        """Mock drop collection"""
        self.documents = []

    def _matches_query(self, document, query):
        """Check if document matches query"""
        if not query:
            return True
        for key, value in query.items():
            if key not in document or document[key] != value:
                return False
        return True


class MockCelery:
    """Mock Celery task queue for testing"""

    def __init__(self):
        self.tasks = []
        self.results = {}

    def apply_async(self, args=None, kwargs=None):
        """Mock async task application"""
        task_id = f'task-{len(self.tasks) + 1}'
        self.tasks.append({
            'id': task_id,
            'args': args,
            'kwargs': kwargs,
            'status': 'PENDING'
        })
        return Mock(id=task_id, state='PENDING')

    def get_task_result(self, task_id):
        """Get task result"""
        return self.results.get(task_id)

    def set_task_result(self, task_id, result):
        """Set task result"""
        self.results[task_id] = result
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'SUCCESS'

    def reset(self):
        """Reset mock state"""
        self.tasks = []
        self.results = {}


class MockWebSocket:
    """Mock WebSocket for testing real-time features"""

    def __init__(self):
        self.messages = []
        self.connected = False

    def connect(self):
        """Mock connection"""
        self.connected = True

    def disconnect(self):
        """Mock disconnection"""
        self.connected = False

    def send(self, message):
        """Mock send message"""
        if not self.connected:
            raise Exception("WebSocket not connected")
        self.messages.append(message)

    def receive(self):
        """Mock receive message"""
        if not self.connected:
            raise Exception("WebSocket not connected")
        if self.messages:
            return self.messages.pop(0)
        return None

    def reset(self):
        """Reset mock state"""
        self.messages = []
        self.connected = False


# Context managers for patching

class mock_openai_api:
    """Context manager for mocking OpenAI API"""

    def __init__(self, response_data=None):
        self.mock = MockOpenAI(response_data)
        self.patcher = None

    def __enter__(self):
        self.patcher = patch('openai.ChatCompletion.create', self.mock.create_completion)
        self.patcher.__enter__()
        return self.mock

    def __exit__(self, *args):
        if self.patcher:
            self.patcher.__exit__(*args)


class mock_email_service:
    """Context manager for mocking email service"""

    def __init__(self):
        self.mock = MockEmail()
        self.patcher = None

    def __enter__(self):
        self.patcher = patch('flask_mail.Mail.send', self.mock.send)
        self.patcher.__enter__()
        return self.mock

    def __exit__(self, *args):
        if self.patcher:
            self.patcher.__exit__(*args)


class mock_redis_client:
    """Context manager for mocking Redis client"""

    def __init__(self):
        self.mock = MockRedis()
        self.patcher = None

    def __enter__(self):
        self.patcher = patch('redis.Redis', return_value=self.mock)
        self.patcher.__enter__()
        return self.mock

    def __exit__(self, *args):
        if self.patcher:
            self.patcher.__exit__(*args)


# Helper functions

def create_mock_response(status_code=200, json_data=None, text=None):
    """Create a mock HTTP response"""
    response = Mock()
    response.status_code = status_code
    response.json = Mock(return_value=json_data or {})
    response.text = text or ''
    response.content = (text or '').encode()
    return response


def create_mock_file(filename='test.txt', content='test content'):
    """Create a mock file object"""
    from io import BytesIO
    file_obj = BytesIO(content.encode())
    file_obj.name = filename
    return file_obj


def create_mock_request(method='GET', path='/', data=None, headers=None):
    """Create a mock Flask request"""
    request = Mock()
    request.method = method
    request.path = path
    request.data = data
    request.headers = headers or {}
    request.json = data if isinstance(data, dict) else {}
    return request

