from flask import session

from app.models import User


def get_current_admin():
    if 'user_id' not in session:
        return None

    user = User.query.get(session['user_id'])

    if not user or not user.is_admin:
        return None

    return user
