from django.conf import settings

def info(backend, details, response, user=None, is_new=False, social_user=None,
         *args, **kwargs):
    if social_user and settings.DEBUG:
        with open('token_%d' % user.pk, 'w+') as file:
            file.write(social_user.tokens['access_token'])
