from django.contrib.auth.decorators import login_required, user_passes_test


def role_login_required(role):

    def inner_role_login_required(view_func):
        role_required = user_passes_test(lambda user: user.access_role() == role,
                                         login_url='sis:access_denied')
        decorated_func = login_required(role_required(view_func))
        return decorated_func

    return inner_role_login_required
