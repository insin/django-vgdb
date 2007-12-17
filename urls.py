from django.conf.urls.defaults import *
from django.contrib import databrowse
from django.contrib.auth.models import User

from vgdb.models import *

databrowse.site.register(Article)
databrowse.site.register(Company)
databrowse.site.register(Game)
databrowse.site.register(Genre)
databrowse.site.register(Link)
databrowse.site.register(Opinion)
databrowse.site.register(Platform)
databrowse.site.register(PlatformRelease)
databrowse.site.register(PlatformType)
databrowse.site.register(Region)
databrowse.site.register(GameRelease)
databrowse.site.register(Reviewer)
databrowse.site.register(Review)
databrowse.site.register(Screenshot)
databrowse.site.register(Series)
databrowse.site.register(Story)
databrowse.site.register(Trivia)
databrowse.site.register(UserProfile)
databrowse.site.register(UserReview)

urlpatterns = patterns('',
    (r'^$', 'vgdb.views.index'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^databrowse/(.*)', databrowse.site.root),
)
