from django.contrib.auth.decorators import login_required, user_passes_test


def role_login_required(*roles):

    def inner_role_login_required(view_func):
        role_required = user_passes_test(lambda user: user.profile.role in roles,
                                         login_url='sis:access_denied')
        decorated_func = login_required(role_required(view_func))
        return decorated_func

    return inner_role_login_required
