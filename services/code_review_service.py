"""
Code Review System Service

Provides peer-to-peer code review functionality with commenting,
approval workflow, and collaboration features.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import uuid

class CodeReviewService:
    def __init__(self):
        self.reviews = self._generate_sample_reviews()
        self.review_requests = self._generate_sample_requests()
        self.comments = self._generate_sample_comments()
        self.review_templates = self._get_review_templates()
    
    def _generate_sample_reviews(self) -> List[Dict[str, Any]]:
        """Generate sample code reviews"""
        return []
    
    def _generate_sample_requests(self) -> List[Dict[str, Any]]:
        """Generate sample review requests"""
        return []
    
    def _generate_sample_comments(self) -> List[Dict[str, Any]]:
        """Generate sample review comments"""
        return []
    
    def _get_review_templates(self) -> List[Dict[str, Any]]:
        """Get review templates for different types of assignments"""
        return [
            {
                'id': 'template_001',
                'name': 'Algorithm Review Template',
                'description': 'Template for reviewing algorithm implementations',
                'categories': ['algorithms', 'data-structures'],
                'criteria': [
                    {'name': 'Correctness', 'weight': 40, 'description': 'Does the algorithm solve the problem correctly?'},
                    {'name': 'Efficiency', 'weight': 25, 'description': 'Time and space complexity considerations'},
                    {'name': 'Code Quality', 'weight': 20, 'description': 'Readability, naming, structure'},
                    {'name': 'Edge Cases', 'weight': 15, 'description': 'Handling of edge cases and error conditions'}
                ],
                'checklist': [
                    'Algorithm logic is correct',
                    'Handles empty inputs',
                    'Variable names are descriptive',
                    'Code is properly commented',
                    'Time complexity is optimal',
                    'Space usage is efficient'
                ]
            },
            {
                'id': 'template_002',
                'name': 'Web Development Review Template',
                'description': 'Template for reviewing web applications and APIs',
                'categories': ['web-development', 'api'],
                'criteria': [
                    {'name': 'Functionality', 'weight': 35, 'description': 'Does the application work as expected?'},
                    {'name': 'Security', 'weight': 25, 'description': 'Input validation, authentication, authorization'},
                    {'name': 'Code Structure', 'weight': 20, 'description': 'Organization, modularity, maintainability'},
                    {'name': 'API Design', 'weight': 20, 'description': 'RESTful principles, error handling'}
                ],
                'checklist': [
                    'All endpoints work correctly',
                    'Input validation is implemented',
                    'Error handling is comprehensive',
                    'Code follows REST principles',
                    'Authentication is secure',
                    'Documentation is clear'
                ]
            }
        ]
    
    def get_review_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get review dashboard data for a user"""
        user_reviews = [r for r in self.reviews if r['author_id'] == user_id or r['reviewer_id'] == user_id]
        my_requests = [r for r in self.review_requests if r['author_id'] == user_id]
        assigned_reviews = [r for r in self.review_requests if r.get('assigned_reviewer') == user_id]
        
        # Calculate statistics
        completed_reviews = len([r for r in user_reviews if r['status'] == 'completed'])
        pending_reviews = len([r for r in user_reviews if r['status'] in ['in_review', 'submitted']])
        average_rating = sum(r['review_data']['overall_rating'] for r in user_reviews if 'review_data' in r) / max(len([r for r in user_reviews if 'review_data' in r]), 1)
        
        return {
            'summary': {
                'total_reviews': len(user_reviews),
                'completed_reviews': completed_reviews,
                'pending_reviews': pending_reviews,
                'reviews_given': len([r for r in user_reviews if r['reviewer_id'] == user_id]),
                'reviews_received': len([r for r in user_reviews if r['author_id'] == user_id]),
                'average_rating_received': round(average_rating, 1),
                'review_requests': len(my_requests),
                'assigned_to_review': len(assigned_reviews)
            },
            'recent_activity': self._get_recent_activity(user_id),
            'pending_actions': self._get_pending_actions(user_id),
            'review_stats': self._get_review_statistics(user_id)
        }
    
    def create_review_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new code review request"""
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        
        new_request = {
            'id': request_id,
            'assignment_id': request_data.get('assignment_id'),
            'author_id': request_data.get('author_id'),
            'author_name': request_data.get('author_name'),
            'title': request_data.get('title'),
            'description': request_data.get('description'),
            'priority': request_data.get('priority', 'medium'),
            'language': request_data.get('language'),
            'estimated_review_time': request_data.get('estimated_review_time', 30),
            'created_date': datetime.now().isoformat(),
            'deadline': request_data.get('deadline'),
            'status': 'open',
            'tags': request_data.get('tags', []),
            'code_complexity': request_data.get('code_complexity', 'medium'),
            'specific_areas': request_data.get('specific_areas', []),
            'reviewer_preferences': request_data.get('reviewer_preferences', {})
        }
        
        self.review_requests.append(new_request)
        
        return {
            'success': True,
            'request_id': request_id,
            'message': 'Review request created successfully'
        }
    
    def get_available_reviews(self, reviewer_id: str) -> Dict[str, Any]:
        """Get available review requests for a reviewer"""
        available_requests = [r for r in self.review_requests if r['status'] == 'open' and r['author_id'] != reviewer_id]
        
        # Sort by priority and deadline
        priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
        available_requests.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['created_date']), reverse=True)
        
        return {
            'available_requests': available_requests,
            'total_count': len(available_requests),
            'urgent_count': len([r for r in available_requests if r['priority'] == 'urgent']),
            'filters': {
                'languages': list(set(r['language'] for r in available_requests)),
                'complexities': list(set(r['code_complexity'] for r in available_requests)),
                'priorities': ['urgent', 'high', 'medium', 'low']
            }
        }
    
    def accept_review_request(self, request_id: str, reviewer_id: str) -> Dict[str, Any]:
        """Accept a review request"""
        request = next((r for r in self.review_requests if r['id'] == request_id), None)
        
        if not request:
            return {'error': 'Review request not found'}
        
        if request['status'] != 'open':
            return {'error': 'Review request is not available'}
        
        request['status'] = 'assigned'
        request['assigned_reviewer'] = reviewer_id
        request['assigned_date'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'message': 'Review request accepted successfully'
        }
    
    def submit_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a completed code review"""
        review_id = f"rev_{uuid.uuid4().hex[:8]}"
        
        new_review = {
            'id': review_id,
            'title': review_data.get('title'),
            'assignment_id': review_data.get('assignment_id'),
            'author_id': review_data.get('author_id'),
            'author_name': review_data.get('author_name'),
            'reviewer_id': review_data.get('reviewer_id'),
            'reviewer_name': review_data.get('reviewer_name'),
            'status': 'completed',
            'created_date': datetime.now().isoformat(),
            'updated_date': datetime.now().isoformat(),
            'code_snapshot': review_data.get('code_snapshot'),
            'review_data': review_data.get('review_data'),
            'feedback': review_data.get('feedback'),
            'metrics': {
                'review_time': review_data.get('review_time', 30),
                'comments_count': len(review_data.get('comments', [])),
                'revisions_requested': review_data.get('revisions_requested', 0),
                'lines_reviewed': review_data.get('lines_reviewed', 0)
            }
        }
        
        self.reviews.append(new_review)
        
        # Update the original request status
        request = next((r for r in self.review_requests if r['id'] == review_data.get('request_id')), None)
        if request:
            request['status'] = 'completed'
        
        return {
            'success': True,
            'review_id': review_id,
            'message': 'Review submitted successfully'
        }
    
    def get_review_details(self, review_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific review"""
        review = next((r for r in self.reviews if r['id'] == review_id), None)
        
        if not review:
            return {'error': 'Review not found'}
        
        # Add comments for this review
        review_comments = [c for c in self.comments if c['review_id'] == review_id]
        
        review_details = review.copy()
        review_details['comments'] = review_comments
        review_details['comment_stats'] = {
            'total_comments': len(review_comments),
            'unresolved_comments': len([c for c in review_comments if not c['resolved']]),
            'suggestions': len([c for c in review_comments if c['comment_type'] == 'suggestion']),
            'issues': len([c for c in review_comments if c['comment_type'] == 'issue'])
        }
        
        return review_details
    
    def add_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a comment to a review"""
        comment_id = f"comment_{uuid.uuid4().hex[:8]}"
        
        new_comment = {
            'id': comment_id,
            'review_id': comment_data.get('review_id'),
            'author_id': comment_data.get('author_id'),
            'author_name': comment_data.get('author_name'),
            'line_number': comment_data.get('line_number'),
            'comment_type': comment_data.get('comment_type', 'suggestion'),
            'content': comment_data.get('content'),
            'created_date': datetime.now().isoformat(),
            'resolved': False,
            'parent_comment_id': comment_data.get('parent_comment_id'),
            'severity': comment_data.get('severity', 'low')
        }
        
        self.comments.append(new_comment)
        
        return {
            'success': True,
            'comment_id': comment_id,
            'message': 'Comment added successfully'
        }
    
    def resolve_comment(self, comment_id: str, resolver_id: str) -> Dict[str, Any]:
        """Mark a comment as resolved"""
        comment = next((c for c in self.comments if c['id'] == comment_id), None)
        
        if not comment:
            return {'error': 'Comment not found'}
        
        comment['resolved'] = True
        comment['resolved_by'] = resolver_id
        comment['resolved_date'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'message': 'Comment resolved successfully'
        }
    
    def get_review_analytics(self, user_id: str = None) -> Dict[str, Any]:
        """Get analytics data for reviews"""
        if user_id:
            reviews = [r for r in self.reviews if r['author_id'] == user_id or r['reviewer_id'] == user_id]
        else:
            reviews = self.reviews
        
        total_reviews = len(reviews)
        if total_reviews == 0:
            return {'message': 'No reviews found'}
        
        # Calculate metrics
        average_rating = sum(r['review_data']['overall_rating'] for r in reviews if 'review_data' in r) / total_reviews
        average_review_time = sum(r['metrics']['review_time'] for r in reviews if 'metrics' in r) / total_reviews
        total_comments = sum(r['metrics']['comments_count'] for r in reviews if 'metrics' in r)
        
        return {
            'overview': {
                'total_reviews': total_reviews,
                'average_rating': round(average_rating, 1),
                'average_review_time': round(average_review_time, 1),
                'total_comments': total_comments,
                'completion_rate': 85  # Mock data
            },
            'trends': {
                'reviews_per_week': [3, 5, 7, 4, 6, 8, 5],  # Last 7 weeks
                'average_ratings': [4.2, 4.1, 4.3, 4.0, 4.2, 4.4, 4.3],
                'review_times': [35, 32, 28, 30, 25, 22, 26]
            },
            'distribution': {
                'by_rating': {'5': 12, '4': 18, '3': 8, '2': 3, '1': 1},
                'by_language': {'Python': 15, 'Java': 12, 'JavaScript': 8, 'C++': 7},
                'by_complexity': {'Easy': 8, 'Medium': 22, 'Hard': 12}
            }
        }
    
    def _get_recent_activity(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent review activity for a user"""
        activities = []
        
        # Recent reviews
        user_reviews = [r for r in self.reviews if r['author_id'] == user_id or r['reviewer_id'] == user_id]
        for review in user_reviews[-5:]:
            activities.append({
                'type': 'review_completed' if review['reviewer_id'] == user_id else 'review_received',
                'title': review['title'],
                'date': review['updated_date'],
                'rating': review['review_data'].get('overall_rating'),
                'id': review['id']
            })
        
        # Recent comments
        user_comments = [c for c in self.comments if c['author_id'] == user_id]
        for comment in user_comments[-3:]:
            activities.append({
                'type': 'comment_added',
                'title': f"Comment on review",
                'date': comment['created_date'],
                'id': comment['id']
            })
        
        # Sort by date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return activities[:10]
    
    def _get_pending_actions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending actions for a user"""
        actions = []
        
        # Assigned reviews
        assigned_reviews = [r for r in self.review_requests if r.get('assigned_reviewer') == user_id and r['status'] == 'assigned']
        for request in assigned_reviews:
            actions.append({
                'type': 'review_due',
                'title': f"Review: {request['title']}",
                'deadline': request['deadline'],
                'priority': request['priority'],
                'id': request['id']
            })
        
        # Unresolved comments on my code
        my_reviews = [r for r in self.reviews if r['author_id'] == user_id]
        for review in my_reviews:
            unresolved_comments = [c for c in self.comments if c['review_id'] == review['id'] and not c['resolved']]
            if unresolved_comments:
                actions.append({
                    'type': 'comments_to_address',
                    'title': f"Unresolved comments on {review['title']}",
                    'count': len(unresolved_comments),
                    'id': review['id']
                })
        
        return actions
    
    def _get_review_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get review statistics for a user"""
        user_reviews = [r for r in self.reviews if r['author_id'] == user_id or r['reviewer_id'] == user_id]
        reviews_given = [r for r in user_reviews if r['reviewer_id'] == user_id]
        reviews_received = [r for r in user_reviews if r['author_id'] == user_id]
        