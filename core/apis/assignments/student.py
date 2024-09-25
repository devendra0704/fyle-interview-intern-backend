from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum

from core.libs.assertions import assert_auth,assert_found
from core.libs import assertions
from core.libs import exceptions
from core.libs.exceptions import FyleError

from .schema import AssignmentSchema, AssignmentSubmitSchema
student_assignments_resources = Blueprint('student_assignments_resources', __name__)


@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    # print(Assignment)
    students_assignments = Assignment.get_assignments_by_student(p.student_id)
    students_assignments_dump = AssignmentSchema().dump(students_assignments, many=True)
    return APIResponse.respond(data=students_assignments_dump)


@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
    
    # Load the assignment data from the incoming payload
    assignment = AssignmentSchema().load(incoming_payload)

    # Validate that content is not null
    if assignment.content is None:
        response = APIResponse.respond(data={"error": "Content cannot be null"})
        response.status_code = 400  # Set the status code here
        return response

    assignment.student_id = p.student_id

    upserted_assignment = Assignment.upsert(assignment)
    db.session.commit()
    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)



@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def submit_assignment(p, incoming_payload):
    """Submit an assignment"""
    submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)

    # Fetch the existing assignment
    existing_assignment = Assignment.query.get(submit_assignment_payload.id)

    # Check if the assignment is already graded
    assertions.assert_found(existing_assignment, 'No assignment with this ID was found')


    if existing_assignment.state == AssignmentStateEnum.SUBMITTED:
        raise FyleError(
            status_code=400,
            message="only a draft assignment can be submitted"
        )

    # Proceed with submission if the assignment is not graded
    submitted_assignment = Assignment.submit(
        _id=submit_assignment_payload.id,
        teacher_id=submit_assignment_payload.teacher_id,
        auth_principal=p
    )

    # Set the state to SUBMITTED
    submitted_assignment.state = AssignmentStateEnum.SUBMITTED

    # Commit the changes to the database
    db.session.commit()

    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return APIResponse.respond(data=submitted_assignment_dump)

