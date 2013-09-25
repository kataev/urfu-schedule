
from social_auth.middleware import SocialAuthExceptionMiddleware

class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    # def get_message(request, exception):

    # get_redirect_uri(request, exception)
    def get_message(self, request, exception):
        request.session['500'] = super(SocialAuthExceptionMiddleware, self).get_message(request, exception)
