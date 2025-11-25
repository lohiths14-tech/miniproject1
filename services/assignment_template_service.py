"""
Assignment Templates Manager Service

Provides functionality for creating, managing, and using reusable assignment templates
with categorization, version control, and collaborative features.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import uuid

class AssignmentTemplateService:
    def __init__(self):
        self.templates = self._generate_sample_templates()
        self.categories = self._get_template_categories()
    
    def _generate_sample_templates(self) -> List[Dict[str, Any]]:
        """Generate sample assignment templates"""
        return [
            {
                'id': 'tmpl_001',
                'name': 'Basic Array Operations',
                'description': 'Template for basic array manipulation assignments',
                'category': 'Data Structures',
                'difficulty': 'Easy',
                'language': 'Python',
                'created_by': 'Dr. Smith',
                'created_date': '2024-01-15',
                'modified_date': '2024-03-10',
                'usage_count': 25,
                'rating': 4.7,
                'tags': ['arrays', 'loops', 'beginner'],
                'estimated_time': 45,
                'template_data': {
                    'problem_statement': 'Write a function to manipulate arrays according to the given requirements.',
                    'starter_code': {
                        'python': 'def solution(arr):\n    # Your code here\n    pass',
                        'java': 'public class Solution {\n    public int[] solution(int[] arr) {\n        // Your code here\n        return arr;\n    }\n}',
                        'cpp': '#include <vector>\nusing namespace std;\n\nvector<int> solution(vector<int> arr) {\n    // Your code here\n    return arr;\n}'
                    },
                    'test_cases': [
                        {'input': '[1, 2, 3, 4, 5]', 'expected': '[5, 4, 3, 2, 1]', 'description': 'Reverse array'},
                        {'input': '[10, 20, 30]', 'expected': '[30, 20, 10]', 'description': 'Reverse small array'}
                    ],
                    'grading_criteria': {
                        'correctness': 60,
                        'efficiency': 20,
                        'code_quality': 20
                    },
                    'hints': [
                        'Consider using two pointers approach',
                        'Think about in-place vs creating new array'
                    ]
                },
                'metadata': {
                    'learning_objectives': ['Array manipulation', 'Basic algorithms'],
                    'prerequisites': ['Basic programming', 'Loops'],
                    'related_concepts': ['Iteration', 'Index manipulation']
                }
            },
            {
                'id': 'tmpl_002',
                'name': 'Binary Search Implementation',
                'description': 'Template for implementing binary search algorithm',
                'category': 'Algorithms',
                'difficulty': 'Medium',
                'language': 'Python',
                'created_by': 'Prof. Johnson',
                'created_date': '2024-02-01',
                'modified_date': '2024-03-15',
                'usage_count': 18,
                'rating': 4.9,
                'tags': ['binary-search', 'algorithms', 'searching'],
                'estimated_time': 60,
                'template_data': {
                    'problem_statement': 'Implement binary search algorithm to find target element in sorted array.',
                    'starter_code': {
                        'python': 'def binary_search(arr, target):\n    # Implement binary search\n    pass',
                        'java': 'public class Solution {\n    public int binarySearch(int[] arr, int target) {\n        // Implement binary search\n        return -1;\n    }\n}',
                        'cpp': '#include <vector>\nusing namespace std;\n\nint binarySearch(vector<int>& arr, int target) {\n    // Implement binary search\n    return -1;\n}'
                    },
                    'test_cases': [
                        {'input': 'arr=[1,2,3,4,5], target=3', 'expected': '2', 'description': 'Find element in middle'},
                        {'input': 'arr=[1,2,3,4,5], target=1', 'expected': '0', 'description': 'Find first element'},
                        {'input': 'arr=[1,2,3,4,5], target=6', 'expected': '-1', 'description': 'Element not found'}
                    ],
                    'grading_criteria': {
                        'correctness': 50,
                        'efficiency': 30,
                        'edge_cases': 20
                    },
                    'hints': [
                        'Use left and right pointers',
                        'Calculate middle index carefully to avoid overflow',
                        'Handle edge cases: empty array, single element'
                    ]
                },
                'metadata': {
                    'learning_objectives': ['Binary search algorithm', 'Divide and conquer'],
                    'prerequisites': ['Arrays', 'Basic recursion or iteration'],
                    'related_concepts': ['Logarithmic time complexity', 'Sorted arrays']
                }
            },
            {
                'id': 'tmpl_003',
                'name': 'Database Design Project',
                'description': 'Template for designing and implementing database schemas',
                'category': 'Database',
                'difficulty': 'Hard',
                'language': 'SQL',
                'created_by': 'Dr. Wilson',
                'created_date': '2024-01-20',
                'modified_date': '2024-03-20',
                'usage_count': 12,
                'rating': 4.5,
                'tags': ['database', 'sql', 'schema-design'],
                'estimated_time': 120,
                'template_data': {
                    'problem_statement': 'Design a database schema for a given business scenario and implement required queries.',
                    'starter_code': {
                        'sql': '-- Create your database schema here\n-- Include tables, relationships, and constraints\n\n-- Example queries will be tested'
                    },
                    'test_cases': [
                        {'input': 'Query: Find all customers with orders > $1000', 'expected': 'Result set with customer details', 'description': 'Complex join query'},
                        {'input': 'Query: Calculate monthly sales totals', 'expected': 'Aggregated results by month', 'description': 'Aggregation query'}
                    ],
                    'grading_criteria': {
                        'schema_design': 40,
                        'query_correctness': 30,
                        'normalization': 20,
                        'performance': 10
                    },
                    'hints': [
                        'Follow database normalization principles',
                        'Use appropriate data types and constraints',
                        'Consider indexing for performance'
                    ]
                },
                'metadata': {
                    'learning_objectives': ['Database design', 'SQL queries', 'Normalization'],
                    'prerequisites': ['Basic SQL', 'Database concepts'],
                    'related_concepts': ['Entity-relationship modeling', 'ACID properties']
                }
            },
            {
                'id': 'tmpl_004',
                'name': 'Web API Development',
                'description': 'Template for creating RESTful web APIs',
                'category': 'Web Development',
                'difficulty': 'Medium',
                'language': 'Python',
                'created_by': 'Prof. Davis',
                'created_date': '2024-02-10',
                'modified_date': '2024-03-25',
                'usage_count': 22,
                'rating': 4.6,
                'tags': ['web-api', 'rest', 'flask'],
                'estimated_time': 90,
                'template_data': {
                    'problem_statement': 'Create a RESTful API with CRUD operations for a given resource.',
                    'starter_code': {
                        'python': 'from flask import Flask, request, jsonify\n\napp = Flask(__name__)\n\n# Implement your API endpoints here\n\nif __name__ == "__main__":\n    app.run(debug=True)'
                    },
                    'test_cases': [
                        {'input': 'GET /api/users', 'expected': 'List of users in JSON format', 'description': 'Get all users'},
                        {'input': 'POST /api/users with valid data', 'expected': 'Created user with 201 status', 'description': 'Create new user'},
                        {'input': 'PUT /api/users/1 with valid data', 'expected': 'Updated user data', 'description': 'Update existing user'}
                    ],
                    'grading_criteria': {
                        'functionality': 40,
                        'rest_compliance': 25,
                        'error_handling': 20,
                        'code_structure': 15
                    },
                    'hints': [
                        'Use appropriate HTTP methods and status codes',
                        'Implement proper error handling',
                        'Validate input data'
                    ]
                },
                'metadata': {
                    'learning_objectives': ['REST API design', 'HTTP methods', 'JSON handling'],
                    'prerequisites': ['Python basics', 'Web concepts', 'HTTP protocol'],
                    'related_concepts': ['API design patterns', 'Status codes', 'Authentication']
                }
            },
            {
                'id': 'tmpl_005',
                'name': 'Machine Learning Model',
                'description': 'Template for implementing basic ML classification models',
                'category': 'Machine Learning',
                'difficulty': 'Hard',
                'language': 'Python',
                'created_by': 'Dr. Anderson',
                'created_date': '2024-03-01',
                'modified_date': '2024-03-28',
                'usage_count': 8,
                'rating': 4.8,
                'tags': ['machine-learning', 'classification', 'scikit-learn'],
                'estimated_time': 150,
                'template_data': {
                    'problem_statement': 'Implement and evaluate a machine learning classification model for the given dataset.',
                    'starter_code': {
                        'python': 'import pandas as pd\nimport numpy as np\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.metrics import accuracy_score, classification_report\n\n# Load and preprocess data\n# Implement your model here\n# Evaluate performance'
                    },
                    'test_cases': [
                        {'input': 'Training data with features and labels', 'expected': 'Trained model with >80% accuracy', 'description': 'Model training'},
                        {'input': 'Test data for prediction', 'expected': 'Predicted labels with confidence scores', 'description': 'Model prediction'},
                        {'input': 'Cross-validation request', 'expected': 'CV scores and metrics', 'description': 'Model validation'}
                    ],
                    'grading_criteria': {
                        'model_implementation': 35,
                        'data_preprocessing': 25,
                        'evaluation_metrics': 25,
                        'code_quality': 15
                    },
                    'hints': [
                        'Start with data exploration and visualization',
                        'Handle missing values appropriately',
                        'Use cross-validation for robust evaluation'
                    ]
                },
                'metadata': {
                    'learning_objectives': ['ML model implementation', 'Data preprocessing', 'Model evaluation'],
                    'prerequisites': ['Python', 'Statistics', 'Pandas', 'NumPy'],
                    'related_concepts': ['Feature engineering', 'Overfitting', 'Cross-validation']
                }
            }
        ]
    
    def _get_template_categories(self) -> List[Dict[str, Any]]:
        """Get template categories with metadata"""
        return [
            {
                'name': 'Data Structures',
                'description': 'Templates for data structure implementations and manipulations',
                'icon': 'fas fa-database',
                'color': '#3498db',
                'count': 8
            },
            {
                'name': 'Algorithms',
                'description': 'Algorithm implementation and optimization templates',
                'icon': 'fas fa-cogs',
                'color': '#e74c3c',
                'count': 12
            },
            {
                'name': 'Web Development',
                'description': 'Web application and API development templates',
                'icon': 'fas fa-globe',
                'color': '#2ecc71',
                'count': 6
            },
            {
                'name': 'Database',
                'description': 'Database design and query templates',
                'icon': 'fas fa-server',
                'color': '#f39c12',
                'count': 4
            },
            {
                'name': 'Machine Learning',
                'description': 'ML model implementation and data science templates',
                'icon': 'fas fa-brain',
                'color': '#9b59b6',
                'count': 3
            },
            {
                'name': 'Object-Oriented Programming',
                'description': 'OOP design and implementation templates',
                'icon': 'fas fa-cube',
                'color': '#1abc9c',
                'count': 7
            }
        ]
    
    def get_all_templates(self, category: Optional[str] = None, difficulty: Optional[str] = None, 
                         language: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """Get all templates with optional filtering"""
        templates = self.templates.copy()
        
        # Apply filters
        if category:
            templates = [t for t in templates if t['category'] == category]
        
        if difficulty:
            templates = [t for t in templates if t['difficulty'] == difficulty]
        
        if language:
            templates = [t for t in templates if t['language'] == language]
        
        if search:
            search_lower = search.lower()
            templates = [t for t in templates if 
                        search_lower in t['name'].lower() or 
                        search_lower in t['description'].lower() or
                        any(search_lower in tag for tag in t['tags'])]
        
        # Sort by rating and usage
        templates.sort(key=lambda x: (x['rating'], x['usage_count']), reverse=True)
        
        return {
            'templates': templates,
            'total_count': len(templates),
            'categories': self.categories,
            'filters': {
                'difficulties': ['Easy', 'Medium', 'Hard'],
                'languages': ['Python', 'Java', 'C++', 'JavaScript', 'SQL'],
                'popular_tags': self._get_popular_tags()
            }
        }
    
    def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """Get detailed template information"""
        template = next((t for t in self.templates if t['id'] == template_id), None)
        
        if not template:
            return {'error': 'Template not found'}
        
        # Add usage statistics and reviews
        template_details = template.copy()
        template_details['usage_stats'] = self._get_usage_stats(template_id)
        template_details['reviews'] = self._get_template_reviews(template_id)
        template_details['similar_templates'] = self._get_similar_templates(template)
        
        return template_details
    
    def create_template(self, template_data: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        """Create a new assignment template"""
        template_id = f"tmpl_{uuid.uuid4().hex[:8]}"
        
        new_template = {
            'id': template_id,
            'name': template_data.get('name', ''),
            'description': template_data.get('description', ''),
            'category': template_data.get('category', ''),
            'difficulty': template_data.get('difficulty', 'Medium'),
            'language': template_data.get('language', 'Python'),
            'created_by': creator_id,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'modified_date': datetime.now().strftime('%Y-%m-%d'),
            'usage_count': 0,
            'rating': 0.0,
            'tags': template_data.get('tags', []),
            'estimated_time': template_data.get('estimated_time', 60),
            'template_data': template_data.get('template_data', {}),
            'metadata': template_data.get('metadata', {}),
            'status': 'draft'  # draft, published, archived
        }
        
        # Validate template data
        validation_result = self._validate_template(new_template)
        if not validation_result['valid']:
            return {'error': validation_result['errors']}
        
        self.templates.append(new_template)
        
        return {
            'success': True,
            'template_id': template_id,
            'message': 'Template created successfully'
        }
    
    def update_template(self, template_id: str, update_data: Dict[str, Any], updater_id: str) -> Dict[str, Any]:
        """Update an existing template"""
        template = next((t for t in self.templates if t['id'] == template_id), None)
        
        if not template:
            return {'error': 'Template not found'}
        
        # Check permissions (mock)
        if template['created_by'] != updater_id:
            return {'error': 'Permission denied'}
        
        # Update fields
        for key, value in update_data.items():
            if key in ['name', 'description', 'category', 'difficulty', 'language', 'tags', 
                      'estimated_time', 'template_data', 'metadata']:
                template[key] = value
        
        template['modified_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Validate updated template
        validation_result = self._validate_template(template)
        if not validation_result['valid']:
            return {'error': validation_result['errors']}
        
        return {
            'success': True,
            'message': 'Template updated successfully'
        }
    
    def duplicate_template(self, template_id: str, duplicator_id: str, new_name: str = None) -> Dict[str, Any]:
        """Create a copy of an existing template"""
        original = next((t for t in self.templates if t['id'] == template_id), None)
        
        if not original:
            return {'error': 'Template not found'}
        
        # Create duplicate
        new_template = original.copy()
        new_template['id'] = f"tmpl_{uuid.uuid4().hex[:8]}"
        new_template['name'] = new_name or f"Copy of {original['name']}"
        new_template['created_by'] = duplicator_id
        new_template['created_date'] = datetime.now().strftime('%Y-%m-%d')
        new_template['modified_date'] = datetime.now().strftime('%Y-%m-%d')
        new_template['usage_count'] = 0
        new_template['rating'] = 0.0
        new_template['status'] = 'draft'
        
        self.templates.append(new_template)
        
        return {
            'success': True,
            'template_id': new_template['id'],
            'message': 'Template duplicated successfully'
        }
    
    def get_template_versions(self, template_id: str) -> Dict[str, Any]:
        """Get version history of a template"""
        # Mock version data
        versions = [
            {
                'version': '1.0',
                'date': '2024-01-15',
                'author': 'Dr. Smith',
                'changes': 'Initial version',
                'status': 'published'
            },
            {
                'version': '1.1',
                'date': '2024-02-10',
                'author': 'Dr. Smith',
                'changes': 'Added more test cases, improved hints',
                'status': 'published'
            },
            {
                'version': '1.2',
                'date': '2024-03-10',
                'author': 'Dr. Smith',
                'changes': 'Updated grading criteria, fixed typos',
                'status': 'current'
            }
        ]
        
        return {
            'template_id': template_id,
            'versions': versions,
            'current_version': '1.2'
        }
    
    def publish_template(self, template_id: str, publisher_id: str) -> Dict[str, Any]:
        """Publish a template for public use"""
        template = next((t for t in self.templates if t['id'] == template_id), None)
        
        if not template:
            return {'error': 'Template not found'}
        
        if template['created_by'] != publisher_id:
            return {'error': 'Permission denied'}
        
        # Validate before publishing
        validation_result = self._validate_template(template)
        if not validation_result['valid']:
            return {'error': f'Cannot publish: {validation_result["errors"]}'}
        
        template['status'] = 'published'
        
        return {
            'success': True,
            'message': 'Template published successfully'
        }
    
    def get_my_templates(self, user_id: str) -> Dict[str, Any]:
        """Get templates created by a specific user"""
        user_templates = [t for t in self.templates if t['created_by'] == user_id]
        
        # Group by status
        by_status = {
            'draft': [t for t in user_templates if t.get('status') == 'draft'],
            'published': [t for t in user_templates if t.get('status') == 'published'],
            'archived': [t for t in user_templates if t.get('status') == 'archived']
        }
        
        return {
            'templates': user_templates,
            'by_status': by_status,
            'stats': {
                'total': len(user_templates),
                'published': len(by_status['published']),
                'draft': len(by_status['draft']),
                'total_usage': sum(t['usage_count'] for t in user_templates),
                'average_rating': sum(t['rating'] for t in user_templates) / len(user_templates) if user_templates else 0
            }
        }
    
    def _validate_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template data"""
        errors = []
        
        if not template.get('name'):
            errors.append('Name is required')
        
        if not template.get('description'):
            errors.append('Description is required')
        
        if not template.get('category'):
            errors.append('Category is required')
        
        if not template.get('template_data', {}).get('problem_statement'):
            errors.append('Problem statement is required')
        
        if not template.get('template_data', {}).get('starter_code'):
            errors.append('Starter code is required')
        
        if not template.get('template_data', {}).get('test_cases'):
            errors.append('Test cases are required')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _get_usage_stats(self, template_id: str) -> Dict[str, Any]:
        """Get usage statistics for a template"""
        return {
            'total_usage': 25,
            'recent_usage': 8,
            'success_rate': 78,
            'average_score': 82.5,
            'completion_time': 52,
            'user_ratings': [5, 4, 5, 4, 5, 3, 4, 5],
            'usage_trend': [2, 4, 6, 8, 5, 7, 3, 8]  # Last 8 weeks
        }
    
    def _get_template_reviews(self, template_id: str) -> List[Dict[str, Any]]:
        """Get reviews for a template"""
        return [
            {
                'user': 'student123',
                'rating': 5,
                'comment': 'Great template! Clear instructions and good test cases.',
                'date': '2024-03-20',
                'helpful_votes': 12
            },
            {
                'user': 'lecturer456',
                'rating': 4,
                'comment': 'Well structured, could use more challenging test cases.',
                'date': '2024-03-15',
                'helpful_votes': 8
            },
            {
                'user': 'student789',
                'rating': 5,
                'comment': 'Perfect for learning arrays. The hints were very helpful.',
                'date': '2024-03-10',
                'helpful_votes': 15
            }
        ]
    
    def _get_similar_templates(self, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get templates similar to the given template"""
        similar = []
        
        for t in self.templates:
            if t['id'] == template['id']:
                continue
            
            similarity_score = 0
            
            # Same category
            if t['category'] == template['category']:
                similarity_score += 3
            
            # Same difficulty
            if t['difficulty'] == template['difficulty']:
                similarity_score += 2
            
            # Shared tags
            shared_tags = set(t['tags']) & set(template['tags'])
            similarity_score += len(shared_tags)
            
            if similarity_score >= 3:
                similar.append({
                    'id': t['id'],
                    'name': t['name'],
                    'category': t['category'],
                    'difficulty': t['difficulty'],
                    'rating': t['rating'],
                    'similarity_score': similarity_score
                })
        
        # Sort by similarity score
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar[:5]  # Return top 5 similar templates
    
    def _get_popular_tags(self) -> List[str]:
        """Get most popular tags across all templates"""
        tag_counts = {}
        
        for template in self.templates:
            for tag in template['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count and return top tags
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags[:15]]  # Return top 15 tags
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template by its ID"""
        return next((t for t in self.templates if t['id'] == template_id), None)
    
    def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assignment template"""
        template_id = f"tmpl_{len(self.templates) + 1:03d}"
        
        new_template = {
            'id': template_id,
            'name': template_data.get('name', ''),
            'description': template_data.get('description', ''),
            'category': template_data.get('category', ''),
            'difficulty': template_data.get('difficulty', 'Medium'),
            'language': template_data.get('language', 'Python'),
            'created_by': template_data.get('created_by', 'Unknown'),
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'modified_date': datetime.now().strftime('%Y-%m-%d'),
            'usage_count': 0,
            'rating': 0.0,
            'tags': template_data.get('tags', []),
            'estimated_time': template_data.get('estimated_time', 60),
            'template_data': template_data.get('template_data', {}),
            'metadata': template_data.get('metadata', {}),
            'status': 'draft'
        }
        
        self.templates.append(new_template)
        return new_template
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing template"""
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Update fields
        for key, value in template_data.items():
            if key in ['name', 'description', 'category', 'difficulty', 'language', 'tags', 
                      'estimated_time', 'template_data', 'metadata']:
                template[key] = value
        
        template['modified_date'] = datetime.now().strftime('%Y-%m-%d')
        return template
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        template = self.get_template_by_id(template_id)
        if template:
            self.templates.remove(template)
            return True
        return False
    
    def duplicate_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Create a duplicate of an existing template"""
        original = self.get_template_by_id(template_id)
        if not original:
            return None
        
        new_template = original.copy()
        new_template['id'] = f"tmpl_{len(self.templates) + 1:03d}"
        new_template['name'] = f"Copy of {original['name']}"
        new_template['created_date'] = datetime.now().strftime('%Y-%m-%d')
        new_template['modified_date'] = datetime.now().strftime('%Y-%m-%d')
        new_template['usage_count'] = 0
        new_template['rating'] = 0.0
        
        self.templates.append(new_template)
        return new_template
    
    def create_assignment_from_template(self, template_id: str, assignment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new assignment from a template"""
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Increment usage count
        template['usage_count'] += 1
        
        # Create new assignment based on template
        assignment = {
            'id': f"assg_{len(self.templates) * 10 + 1:03d}",
            'template_id': template_id,
            'title': assignment_data.get('title', template['name']),
            'description': assignment_data.get('description', template['description']),
            'due_date': assignment_data.get('due_date'),
            'max_score': assignment_data.get('max_score', 100),
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'template_data': template['template_data'].copy(),
            'customizations': assignment_data.get('customizations', {})
        }
        
        return assignment
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all template categories"""
        return self.categories
    
    def rate_template(self, template_id: str, rating: int) -> bool:
        """Rate a template"""
        template = self.get_template_by_id(template_id)
        if not template or not (1 <= rating <= 5):
            return False
        
        # Simple rating update (in real implementation, would track individual ratings)
        current_rating = template['rating']
        template['rating'] = (current_rating + rating) / 2
        return True
    
    def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular templates"""
        sorted_templates = sorted(self.templates, key=lambda x: (x['rating'], x['usage_count']), reverse=True)
        return sorted_templates[:limit]
    
    def get_recent_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently created or modified templates"""
        sorted_templates = sorted(self.templates, key=lambda x: x['modified_date'], reverse=True)
        return sorted_templates[:limit]
    
    def get_template_versions(self, template_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get version history of a template"""
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Mock version data
        return [
            {
                'version': '1.0',
                'date': template['created_date'],
                'author': template['created_by'],
                'changes': 'Initial version'
            },
            {
                'version': '1.1',
                'date': template['modified_date'],
                'author': template['created_by'],
                'changes': 'Updated content and test cases'
            }
        ]
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get template management statistics"""
        total_templates = len(self.templates)
        categories_count = {}
        languages_count = {}
        
        for template in self.templates:
            category = template['category']
            language = template['language']
            
            categories_count[category] = categories_count.get(category, 0) + 1
            languages_count[language] = languages_count.get(language, 0) + 1
        
        return {
            'total_templates': total_templates,
            'categories_distribution': categories_count,
            'languages_distribution': languages_count,
            'average_rating': sum(t['rating'] for t in self.templates) / total_templates if total_templates > 0 else 0,
            'total_usage': sum(t['usage_count'] for t in self.templates),
            'most_popular': self.get_popular_templates(5),
            'recent_activity': self.get_recent_templates(5)
        }