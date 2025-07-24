from flask_jwt_extended import get_jwt

def get_current_user():
    """Helper function to get current user info from JWT claims"""
    claims = get_jwt()
    return {
        'id': claims.get('user_id'),
        'type': claims.get('user_type')
    }