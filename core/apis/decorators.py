import json
from flask import request, jsonify
from core.libs import assertions
from functools import wraps


class AuthPrincipal:
    def __init__(self, user_id, student_id=None, teacher_id=None, principal_id=None):
        self.user_id = user_id
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.principal_id = principal_id


def accept_payload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        incoming_payload = request.json
        return func(incoming_payload, *args, **kwargs)
    return wrapper


def authenticate_principal(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # print("testing",request.headers)
        p_str = request.headers.get('X-Principal')
        assertions.assert_auth(p_str is not None, 'principal not found')
        p_dict = json.loads(p_str)
        p = AuthPrincipal(
            user_id=p_dict['user_id'],
            student_id=p_dict.get('student_id'),
            teacher_id=p_dict.get('teacher_id'),
            principal_id=p_dict.get('principal_id')
        )

        if request.path.startswith('/student'):
            assertions.assert_true(p.student_id is not None, 'requester should be a student')
        elif request.path.startswith('/teacher'):
            assertions.assert_true(p.teacher_id is not None, 'requester should be a teacher')
        elif request.path.startswith('/principal'):
            assertions.assert_true(p.principal_id is not None, 'requester should be a principal')
        else:
            assertions.assert_found(None, 'No such api')

        return func(p, *args, **kwargs)
    return wrapper




from core.models.teachers import Teacher  # Assuming you have a Teacher model
from core.libs.assertions import assert_auth, assert_found 

def authenticate_teacher(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        teacher_header = request.headers.get('X-Principal')
        
        # Use assert_auth to check if the teacher header is present
        assert_auth(teacher_header, 'Teacher authorization header missing')

        try:
            teacher_data = json.loads(teacher_header)
            teacher_id = teacher_data.get('teacher_id')
            user_id = teacher_data.get('user_id')
        except ValueError:
            raise FyleError(status_code=400, message='Invalid header format')
        
        teacher = Teacher.query.filter_by(id=teacher_id, user_id=user_id).first()

        if not teacher:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        return f(teacher, *args, **kwargs)

    return decorated_function
