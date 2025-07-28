from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import logout
from django.config import settings
user = settings.AUTH_USER_MODEL

class FixedSessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.settings.AUTH_USER_MODEL.is_authenticated:
            login_time = request.session.get('login_time')
            if login_time:
                login_time = timezone.datetime.fromisoformat(login_time)
                if timezone.now() - login_time > timedelta(minutes=30):
                    logout(request)
            else:
                request.session['login_time'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response