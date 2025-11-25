"""
GraphQL API for AI Grading System
Provides efficient data fetching with flexible queries
"""
import graphene
from graphene import ObjectType, String, Int, Float, List, Field
from typing import Optional

# Types
class UserType(ObjectType):
    id = String()
    email = String()
    name = String()
    role = String()
    created_at = String()

class SubmissionType(ObjectType):
    id = String()
    student_id = String()
    assignment_id = String()
    code = String()
    language = String()
    score = Float()
    feedback = String()
    submitted_at = String()

class AssignmentType(ObjectType):
    id = String()
    title = String()
    description = String()
    difficulty = String()
    due_date = String()
    test_cases = List(String)

class PlagiarismResultType(ObjectType):
    submission_id = String()
    similar_submissions = List(String)
    similarity_score = Float()
    has_plagiarism = graphene.Boolean()

# Query
class Query(ObjectType):
    # User queries
    user = Field(UserType, id=String(required=True))
    users = List(UserType, role=String())

    # Submission queries
    submission = Field(SubmissionType, id=String(required=True))
    submissions = List(
        SubmissionType,
        student_id=String(),
        assignment_id=String(),
        limit=Int(default_value=20)
    )

    # Assignment queries
    assignment = Field(AssignmentType, id=String(required=True))
    assignments = List(AssignmentType, difficulty=String())

    # Plagiarism queries
    plagiarism_check = Field(
        PlagiarismResultType,
        submission_id=String(required=True)
    )

    # Resolvers
    def resolve_user(self, info, id):
        # TODO: Fetch from database
        return UserType(
            id=id,
            email="user@example.com",
            name="Sample User",
            role="student"
        )

    def resolve_submissions(self, info, student_id=None, assignment_id=None, limit=20):
        # TODO: Fetch from database with filters
        return []

    def resolve_assignment(self, info, id):
        # TODO: Fetch from database
        return None

# Mutations
class SubmitCodeMutation(graphene.Mutation):
    class Arguments:
        code = String(required=True)
        language = String(required=True)
        assignment_id = String(required=True)

    submission = Field(SubmissionType)
    success = graphene.Boolean()

    def mutate(self, info, code, language, assignment_id):
        # TODO: Process submission
        return SubmitCodeMutation(
            submission=None,
            success=True
        )

class CreateAssignmentMutation(graphene.Mutation):
    class Arguments:
        title = String(required=True)
        description = String(required=True)
        difficulty = String()

    assignment = Field(AssignmentType)
    success = graphene.Boolean()

    def mutate(self, info, title, description, difficulty=None):
        # TODO: Create assignment in database
        return CreateAssignmentMutation(
            assignment=None,
            success=True
        )

class Mutation(ObjectType):
    submit_code = SubmitCodeMutation.Field()
    create_assignment = CreateAssignmentMutation.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Flask integration
def init_graphql(app):
    """Initialize GraphQL endpoint"""
    from flask_graphql import GraphQLView

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True  # Enable GraphiQL interface
        )
    )
