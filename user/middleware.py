import datetime
from http.client import responses

from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # before response
        print(f"Request Method: {request.method}, Request Path: {request.path}")

        response = self.get_response(request)
        print(f"Response Status Code: {response.status_code}")
        #after response
        return response

class AuthCheckMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):

        protected_routes = ["/", "/admin"]

        if not request.user.is_authenticated and request.path in protected_routes:
            return redirect("user/login")

        response = self.get_response(request)

        return response


class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        timeout = getattr(settings, 'AUTO_LOGOUT_DELAY', 300)
        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed_time = (datetime.datetime.now() - datetime.datetime.fromisoformat(last_activity)).total_seconds()
            if elapsed_time > timeout:
                logout(request)
                request.session.flush()
                messages.info(request, "inactive for more than 12 seconds. please, log back in")
                return

        request.session['last_activity'] = datetime.datetime.now().isoformat()
