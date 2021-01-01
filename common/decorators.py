from django.contrib.auth.decorators import user_passes_test


def anonymous_required(redirect_url='common:home'):
    """
    Decorator for views that checks that the user is not logged in, redirecting
    to the home page if it's logged in.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url,
        redirect_field_name=None
    )

    return actual_decorator
