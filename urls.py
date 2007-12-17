from django.conf.urls.defaults import *
from django.contrib import databrowse
from django.contrib.auth.models import User

from vgdb.models import (Company, PlatformType, Platform, Genre, Series, Game,
    Screenshot, Trivia, Region, Release, Reviewer, Review, Link, Opinion,
    Story, UserReview, Article)

databrowse.site.register(User)

databrowse.site.register(Company)
databrowse.site.register(PlatformType)
databrowse.site.register(Platform)
databrowse.site.register(Genre)
databrowse.site.register(Series)
databrowse.site.register(Game)
databrowse.site.register(Screenshot)
databrowse.site.register(Trivia)
databrowse.site.register(Region)
databrowse.site.register(Release)
databrowse.site.register(Reviewer)
databrowse.site.register(Review)
databrowse.site.register(Link)
databrowse.site.register(Opinion)
databrowse.site.register(Story)
databrowse.site.register(UserReview)
databrowse.site.register(Article)

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^databrowse/(.*)', databrowse.site.root),
)
