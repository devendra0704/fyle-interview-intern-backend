# from flask import Blueprint
# from core import app  # Import the Flask app
# from core.apis import decorators
# from core.apis.responses import APIResponse
# from core.models.assignments import Assignment
# from .schema import AssignmentSchema  # Import your schema as needed

# # Define the Blueprint
# principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

# @principal_assignments_resources.route('/assignments', methods=['GET'],strict_slashes=False)
# @decorators.authenticate_principal
# def get_principal_assignments(principal):
#     """Fetch all assignments submitted and graded by teachers."""
#     assignments = fetch_assignments_from_db()  # Fetch all assignments
#     assignments_dump = AssignmentSchema().dump(assignments, many=True)  # Serialize assignments
#     return APIResponse.respond(data=assignments_dump), 200

# def fetch_assignments_from_db():
#     """Fetch all assignments from the database."""
#     assignments = Assignment.query.all()  # Fetch all assignments
#     return assignments



from flask import Blueprint
from core import app  # Import the Flask app
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum  # Import AssignmentStateEnum to filter by state
from .schema import AssignmentSchema  # Import your schema as needed
from flask import Blueprint, request
from core.models.assignments import GradeEnum
from core import db
from flask import request
from core.libs.exceptions import FyleError 



# Define the Blueprint
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def get_principal_assignments(principal):
    """Fetch all assignments submitted and graded by teachers."""
    assignments = fetch_assignments_from_db()  # Fetch filtered assignments
    assignments_dump = AssignmentSchema().dump(assignments, many=True)  # Serialize assignments
    return APIResponse.respond(data=assignments_dump), 200

def fetch_assignments_from_db():
    """Fetch all assignments in SUBMITTED or GRADED state from the database."""
    assignments = Assignment.query.filter(
        Assignment.state.in_([AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])
    ).all()  # Filter assignments by state
    return assignments


@principal_assignments_resources.route('/assignments/grade', methods=['POST'])
@decorators.authenticate_principal
def grade_assignment(principal):
    data = request.get_json()
    assignment = Assignment.query.get(data['id'])

    # if not assignment:
    #     # Raise FyleError if assignment is not found
    #     raise FyleError(status_code=404, message="Assignment not found")

    # Check if the assignment is in draft state
    if assignment.state == "DRAFT":
        # Raise FyleError if trying to grade a draft assignment
        raise FyleError(status_code=400, message="Cannot grade a draft assignment")

    # Validate grade
    grade = data.get('grade')

    # If the assignment has been graded, allow regrading
    assignment.grade = grade
    assignment.state = AssignmentStateEnum.GRADED
    db.session.commit()  # Save the changes to the database

    # Include the state and grade in the response
    return APIResponse.respond(data={
        "message": "Assignment graded successfully",
        "state": assignment.state.value,
        "grade": assignment.grade
    }), 200


