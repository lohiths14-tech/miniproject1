"""
Comprehensive API Tests for Assignment Endpoints (Task 19)
Tests for /api/assignments CRUD operations and authorization
"""

import pytest
from datetime import datetime, timedelta
from bson.objectid import ObjectId


# ==================== 19.1 Test Assignment CRUD Operations ====================

class TestAssignmentCRUD:
    """Test suite for Assignment CRUD operations (Task 19.1)"""

    def test_create_assignment_success(self, client):
        """Test POST /api/assignments - successful creation by lecturer"""
        # First, create and login as lecturer
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer1@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer1',
            'role': 'lecturer',
            'lecturer_id': 'LEC001'
        })
        assert signup_response.status_code == 201
        token = signup_response.get_json()['access_token']

        # Create assignment
        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Python Basics Assignment',
                'description': 'Write a function to calculate factorial',
                'deadline': deadline,
                'test_cases': [
                    {'input': '5', 'expected_output': '120'},
                    {'input': '0', 'expected_output': '1'}
                ],
                'programming_language': 'python',
                'max_score': 100,
                'starter_code': 'def factorial(n):\n    pass',
                'difficulty': 'easy'
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert 'message' in data
        assert 'assignment' in data
        assert data['assignment']['title'] == 'Python Basics Assignment'
        assert data['assignment']['programming_language'] == 'python'
        assert data['assignment']['max_score'] == 100
        assert data['assignment']['difficulty'] == 'easy'
        assert len(data['assignment']['test_cases']) == 2
        assert data['assignment']['is_active'] is True

    def test_create_assignment_minimal_fields(self, client):
        """Test creating assignment with only required fields"""
        # Create and login as lecturer
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer2@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer2',
            'role': 'lecturer',
            'lecturer_id': 'LEC002'
        })
        token = signup_response.get_json()['accen']

        # Create assignment with minimal fields
        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Minimal Assignment',
                'description': 'Test description',
                'deadline': deadline
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['assignment']['title'] == 'Minimal Assignment'
        # Check defaults
        assert data['assignment']['programming_language'] == 'python'
        assert data['assignment']['max_score'] == 100
        assert data['assignment']['difficulty'] == 'medium'
        assert data['assignment']['test_cases'] == []

    def test_create_assignment_missing_title(self, client):
        """Test POST /api/assignments - missing title returns 400"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer3@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer3',
            'role': 'lecturer',
            'lecturer_id': 'LEC003'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'description': 'Test description',
                'deadline': deadline
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'title' in data['error'].lower()

    def test_create_assignment_missing_description(self, client):
        """Test POST /api/assignments - missing description returns 400"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer4@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer4',
            'role': 'lecturer',
            'lecturer_id': 'LEC004'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Assignment',
                'deadline': deadline
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'description' in data['error'].lower()

    def test_create_assignment_missing_deadline(self, client):
        """Test POST /api/assignments - missing deadline returns 400"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer5@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer5',
            'role': 'lecturer',
            'lecturer_id': 'LEC005'
        })
        token = signup_response.get_json()['access_token']

        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Assignment',
                'description': 'Test description'
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'deadline' in data['error'].lower()

    def test_create_assignment_invalid_deadline_format(self, client):
        """Test POST /api/assignments - invalid deadline format returns 400"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer6@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer6',
            'role': 'lecturer',
            'lecturer_id': 'LEC006'
        })
        token = signup_response.get_json()['access_token']

        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Assignment',
                'description': 'Test description',
                'deadline': 'invalid-date-format'
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'deadline' in data['error'].lower()

    def test_create_assignment_invalid_test_cases(self, client):
        """Test POST /api/assignments - invalid test cases format returns 400"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer7@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer7',
            'role': 'lecturer',
            'lecturer_id': 'LEC007'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Assignment',
                'description': 'Test description',
                'deadline': deadline,
                'test_cases': 'not-a-list'  # Should be a list
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'test_cases' in data['error'].lower()

    def test_create_assignment_test_case_missing_fields(self, client):
        """Test POST /api/assignments - test case missing required fields returns 400"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer8@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer8',
            'role': 'lecturer',
            'lecturer_id': 'LEC008'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Assignment',
                'description': 'Test description',
                'deadline': deadline,
                'test_cases': [
                    {'input': '5'}  # Missing expected_output
                ]
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'test case' in data['error'].lower()

    def test_list_assignments_success(self, client):
        """Test GET /api/assignments - list all active assignments"""
        # Create lecturer and assignment
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer9@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer9',
            'role': 'lecturer',
            'lecturer_id': 'LEC009'
        })
        lecturer_token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        client.post('/api/assignments',
            headers={'Authorization': f'Bearer {lecturer_token}'},
            json={
                'title': 'Assignment 1',
                'description': 'Description 1',
                'deadline': deadline
            }
        )

        # Create student and list assignments
        student_response = client.post('/api/auth/signup', json={
            'email': 'student1@test.com',
            'password': 'SecurePass123',
            'username': 'student1',
            'role': 'student',
            'usn': 'STU001'
        })
        student_token = student_response.get_json()['access_token']

        response = client.get('/api/assignments',
            headers={'Authorization': f'Bearer {student_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'assignments' in data
        assert isinstance(data['assignments'], list)
        assert len(data['assignments']) >= 1

    def test_list_assignments_requires_auth(self, client):
        """Test GET /api/assignments - requires authentication"""
        response = client.get('/api/assignments')

        assert response.status_code == 401

    def test_get_assignment_details_success(self, client):
        """Test GET /api/assignments/:id - get assignment details"""
        # Create lecturer and assignment
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer10@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer10',
            'role': 'lecturer',
            'lecturer_id': 'LEC010'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Detailed Assignment',
                'description': 'Detailed description',
                'deadline': deadline
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Get assignment details
        response = client.get(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Detailed Assignment'
        assert data['description'] == 'Detailed description'
        assert '_id' in data

    def test_get_assignment_details_not_found(self, client):
        """Test GET /api/assignments/:id - non-existent assignment returns 404"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer11@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer11',
            'role': 'lecturer',
            'lecturer_id': 'LEC011'
        })
        token = signup_response.get_json()['access_token']

        # Use a valid ObjectId format but non-existent
        fake_id = str(ObjectId())
        response = client.get(f'/api/assignments/{fake_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_update_assignment_success(self, client):
        """Test PUT /api/assignments/:id - successful update"""
        # Create lecturer and assignment
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer12@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer12',
            'role': 'lecturer',
            'lecturer_id': 'LEC012'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Original Title',
                'description': 'Original description',
                'deadline': deadline
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Update assignment
        new_deadline = (datetime.utcnow() + timedelta(days=14)).isoformat()
        response = client.put(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Updated Title',
                'description': 'Updated description',
                'deadline': new_deadline,
                'max_score': 150,
                'difficulty': 'hard'
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert data['assignment']['title'] == 'Updated Title'
        assert data['assignment']['description'] == 'Updated description'
        assert data['assignment']['max_score'] == 150
        assert data['assignment']['difficulty'] == 'hard'

    def test_update_assignment_partial(self, client):
        """Test PUT /api/assignments/:id - partial update"""
        # Create lecturer and assignment
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer13@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer13',
            'role': 'lecturer',
            'lecturer_id': 'LEC013'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Original Title',
                'description': 'Original description',
                'deadline': deadline,
                'max_score': 100
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Update only title
        response = client.put(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Only Title Updated'
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['assignment']['title'] == 'Only Title Updated'
        assert data['assignment']['description'] == 'Original description'  # Unchanged
        assert data['assignment']['max_score'] == 100  # Unchanged

    def test_update_assignment_not_found(self, client):
        """Test PUT /api/assignments/:id - non-existent assignment returns 404"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer14@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer14',
            'role': 'lecturer',
            'lecturer_id': 'LEC014'
        })
        token = signup_response.get_json()['access_token']

        fake_id = str(ObjectId())
        response = client.put(f'/api/assignments/{fake_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Updated Title'
            }
        )

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_delete_assignment_success(self, client):
        """Test DELETE /api/assignments/:id - successful soft delete"""
        # Create lecturer and assignment
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer15@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer15',
            'role': 'lecturer',
            'lecturer_id': 'LEC015'
        })
        token = signup_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'To Be Deleted',
                'description': 'This will be deleted',
                'deadline': deadline
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Delete assignment
        response = client.delete(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

        # Verify assignment is soft deleted (not in active list)
        list_response = client.get('/api/assignments',
            headers={'Authorization': f'Bearer {token}'}
        )
        assignments = list_response.get_json()['assignments']
        assignment_ids = [a['_id'] for a in assignments]
        assert assignment_id not in assignment_ids

    def test_delete_assignment_not_found(self, client):
        """Test DELETE /api/assignments/:id - non-existent assignment returns 404"""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'lecturer16@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer16',
            'role': 'lecturer',
            'lecturer_id': 'LEC016'
        })
        token = signup_response.get_json()['access_token']

        fake_id = str(ObjectId())
        response = client.delete(f'/api/assignments/{fake_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


# ==================== 19.2 Test Assignment Authorization ====================

class TestAssignmentAuthorization:
    """Test suite for Assignment authorization (Task 19.2)"""

    def test_student_cannot_create_assignment(self, client):
        """Test only lecturers can create assignments (403 for students)"""
        # Create and login as student
        signup_response = client.post('/api/auth/signup', json={
            'email': 'student2@test.com',
            'password': 'SecurePass123',
            'username': 'student2',
            'role': 'student',
            'usn': 'STU002'
        })
        token = signup_response.get_json()['access_token']

        # Try to create assignment as student
        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Student Assignment',
                'description': 'Should not be allowed',
                'deadline': deadline
            }
        )

        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'lecturer' in data['error'].lower() or 'denied' in data['error'].lower()

    def test_unauthenticated_cannot_create_assignment(self, client):
        """Test unauthenticated users cannot create assignments"""
        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post('/api/assignments',
            json={
                'title': 'Unauthorized Assignment',
                'description': 'Should not be allowed',
                'deadline': deadline
            }
        )

        assert response.status_code == 401

    def test_only_creator_can_update_assignment(self, client):
        """Test only assignment creator can update (403 for other lecturers)"""
        # Create first lecturer and assignment
        lecturer1_response = client.post('/api/auth/signup', json={
            'email': 'lecturer17@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer17',
            'role': 'lecturer',
            'lecturer_id': 'LEC017'
        })
        lecturer1_token = lecturer1_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {lecturer1_token}'},
            json={
                'title': 'Lecturer 1 Assignment',
                'description': 'Created by lecturer 1',
                'deadline': deadline
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Create second lecturer
        lecturer2_response = client.post('/api/auth/signup', json={
            'email': 'lecturer18@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer18',
            'role': 'lecturer',
            'lecturer_id': 'LEC018'
        })
        lecturer2_token = lecturer2_response.get_json()['access_token']

        # Try to update as different lecturer
        response = client.put(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {lecturer2_token}'},
            json={
                'title': 'Unauthorized Update'
            }
        )

        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'own' in data['error'].lower() or 'denied' in data['error'].lower()

    def test_student_cannot_update_assignment(self, client):
        """Test students cannot update assignments"""
        # Create lecturer and assignment
        lecturer_response = client.post('/api/auth/signup', json={
            'email': 'lecturer19@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer19',
            'role': 'lecturer',
            'lecturer_id': 'LEC019'
        })
        lecturer_token = lecturer_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {lecturer_token}'},
            json={
                'title': 'Protected Assignment',
                'description': 'Students cannot update',
                'deadline': deadline
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Create student
        student_response = client.post('/api/auth/signup', json={
            'email': 'student3@test.com',
            'password': 'SecurePass123',
            'username': 'student3',
            'role': 'student',
            'usn': 'STU003'
        })
        student_token = student_response.get_json()['access_token']

        # Try to update as student
        response = client.put(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'title': 'Student Update Attempt'
            }
        )

        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data

    def test_only_creator_can_delete_assignment(self, client):
        """Test only assignment creator can delete (403 for other lecturers)"""
        # Create first lecturer and assignment
        lecturer1_response = client.post('/api/auth/signup', json={
            'email': 'lecturer20@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer20',
            'role': 'lecturer',
            'lecturer_id': 'LEC020'
        })
        lecturer1_token = lecturer1_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {lecturer1_token}'},
            json={
                'title': 'Lecturer 1 Assignment',
                'description': 'Created by lecturer 1',
                'deadline': deadline
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Create second lecturer
        lecturer2_response = client.post('/api/auth/signup', json={
            'email': 'lecturer21@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer21',
            'role': 'lecturer',
            'lecturer_id': 'LEC021'
        })
        lecturer2_token = lecturer2_response.get_json()['access_token']

        # Try to delete as different lecturer
        response = client.delete(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {lecturer2_token}'}
        )

        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'own' in data['error'].lower() or 'denied' in data['error'].lower()

    def test_student_cannot_delete_assignment(self, client):
        """Test students cannot delete assignments"""
        # Create lecturer and assignment
        lecturer_response = client.post('/api/auth/signup', json={
            'email': 'lecturer22@test.com',
            'password': 'SecurePass123',
            'username': 'lecturer22',
            'role': 'lecturer',
            'lecturer_id': 'LEC022'
        })
        lecturer_token = lecturer_response.get_json()['access_token']

        deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        create_response = client.post('/api/assignments',
            headers={'Authorization': f'Bearer {lecturer_token}'},
            json={
                'title': 'Protected Assignment',
                'description': 'Students cannot delete',
                'deadline': deadline
            }
        )

        assignment_id = create_response.get_json()['assignment']['_id']

        # Create student
        student_response = client.post('/api/auth/signup', json={
            'email': 'student4@test.com',
            'password': 'SecurePass123',
            'username': 'student4',
            'role': 'student',
            'usn': 'STU004'
        })
        student_token = student_response.get_json()['access_token']

        # Try to delete as student
        response = client.delete(f'/api/assignments/{assignment_id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )

        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data

    def test_unauthenticated_cannot_update_assignment(self, client):
        """Test unauthenticated users cannot update assignments"""
        fake_id = str(ObjectId())
        response = client.put(f'/api/assignments/{fake_id}',
            json={
                'title': 'Unauthorized Update'
            }
        )

        assert response.status_code == 401

    def test_unauthenticated_cannot_delete_assignment(self, client):
        """Test unauthenticated users cannot delete assignments"""
        fake_id = str(ObjectId())
        response = client.delete(f'/api/assignments/{fake_id}')

        assert response.status_code == 401

