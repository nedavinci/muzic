import md5

from django.http import HttpResponse
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class ScrobblerMixin(object):
    def getSessionString(self, username):
        return '17E61E13454CDD8B68E8D7DEEEDF6170'

    def checkSession(self, sess_string):
        return sess_string == '17E61E13454CDD8B68E8D7DEEEDF6170'


class HandShake(ScrobblerMixin, View):
    def auth(self, username, authstring, timestamp):
        if not username or not authstring or not timestamp:
            return False
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return False
        if (authstring == md5.new(user.password + str(timestamp)).hexdigest() and
                username == user.username):
            return True
        else:
            return False

    def get(self, request, *args, **kwargs):
        if self.auth(request.GET.get('u'), request.GET.get('a'), request.GET.get('t')):
            resultlines = [
                "OK",
                self.getSessionString(request.GET.get('u')),
                request.build_absolute_uri(reverse('now_playing')),
                request.build_absolute_uri(reverse('submission')),
            ]
            return HttpResponse("\n".join(resultlines))
        else:
            return HttpResponse('BADAUTH')


class NowPlaying(ScrobblerMixin, View):
    def get(self, request, *args, **kwargs):
        if not self.checkSession(request.GET.get('s')):
            return HttpResponse('BADSESSION')
        else:
            return HttpResponse('OK')


class Submission(ScrobblerMixin, View):
    def get(self, request, *args, **kwargs):
        if not self.checkSession(request.GET.get('s')):
            return HttpResponse('BADSESSION')
        else:
            pass
