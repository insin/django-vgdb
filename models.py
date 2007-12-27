"""
Video game database models.

These fall broadly into two categories:

Cold, Hard Facts
================

Models which capture information and facts about games.

Warm, Soft People
=================

Models which capture people's experiences with games.
"""
from django.db import models
from django.utils.text import truncate_words

from django.contrib.auth.models import User

from vgdb import mptt

__all__ = ['Region', 'Company', 'PlatformType', 'Platform', 'PlatformRelease',
    'Genre', 'Series', 'Game', 'GameRelease', 'Screenshot', 'Trivia', 'Link',
    'Reviewer', 'Review', 'UserProfile', 'Opinion', 'Story', 'UserReview',
    'Article']

####################
# Cold, Hard Facts #
####################

class Region(models.Model):
    """
    A region or territory in which games are released.
    """
    code        = models.CharField(max_length=3, unique=True)
    name        = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('code',)

    class Admin:
        list_display = ('code', 'name',)
        search_fields = ('description',)

    def __unicode__(self):
        return self.name

class Company(models.Model):
    """
    A company in the games industry.
    """
    name        = models.CharField(max_length=100, unique=True)
    image       = models.ImageField(upload_to='companies', blank=True)
    url         = models.URLField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'companies'
        ordering = ('name',)

    class Admin:
        search_fields = ('description',)

    def __unicode__(self):
        return self.name

class PlatformType(models.Model):
    """
    A type of platform.
    """
    name        = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'platform type'
        ordering = ('name',)

    class Admin:
        list_display = ('name', 'description')
        search_fields = ('description',)

    def __unicode__(self):
        return self.name

class Platform(models.Model):
    """
    A games platform, for which games are released.
    """
    name         = models.CharField(max_length=100)
    type         = models.ForeignKey(PlatformType, related_name='platforms')
    manufacturer = models.ForeignKey(Company, related_name='manufactured_platforms')
    image        = models.ImageField(upload_to='platforms', blank=True)
    description  = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)

    class Admin:
        list_display = ('name', 'type', 'manufacturer')
        list_filter = ('type',)
        search_fields = ('description',)

    def __unicode__(self):
        return self.name

class PlatformRelease(models.Model):
    """
    A release of a platform in a particular region.
    """
    platform    = models.ForeignKey(Platform, related_name='releases')
    name        = models.CharField(max_length=100)
    region      = models.ForeignKey(Region, related_name='platform_releases')
    date        = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'platform release'
        ordering = ('-date',)

    class Admin:
        list_display = ('platform', 'region', 'date')
        list_filter = ('region',)
        search_fields = ('description',)

    def __unicode__(self):
        return u'%s (%s)' % (self.platform, self.region.code)

class Genre(models.Model):
    """
    A type of game.
    """
    name        = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True, related_name='children')

    # Modified Preorder Tree Traversal fields
    tree_id = models.PositiveIntegerField(db_index=True, editable=False)
    level   = models.PositiveIntegerField(editable=False)
    lft     = models.PositiveIntegerField(db_index=True, editable=False)
    rght    = models.PositiveIntegerField(db_index=True, editable=False)

    class Meta:
        ordering = ('tree_id', 'lft', 'name')

    class Admin:
        list_display = ('name', 'parent')
        search_fields = ('description',)

    def __unicode__(self):
        return self.name

mptt.treeify(Genre, 'parent', 'lft', 'rght', 'tree_id', 'level')

class Series(models.Model):
    """
    A game series or franchise.
    """
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'series'
        ordering = ('name',)

    class Admin:
        search_fields = ('description',)

    def __unicode__(self):
        return self.name

class Game(models.Model):
    """
    A game!
    """
    name        = models.CharField(max_length=255)
    series      = models.ForeignKey(Series, null=True, blank=True, related_name='games')
    genre       = models.ForeignKey(Genre, null=True, blank=True, related_name='games')
    publisher   = models.ForeignKey(Company, related_name='published_games')
    developer   = models.ForeignKey(Company, related_name='developed_games')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)

    class Admin:
        list_display = ('name', 'series', 'genre', 'publisher', 'developer')
        search_fields = ('name', 'description')

    def __unicode__(self):
        return self.name

class GameRelease(models.Model):
    """
    A release of a game in a particular region on a particular platform.
    """
    game        = models.ForeignKey(Game, related_name='releases')
    name        = models.CharField(max_length=255, blank=True)
    platform    = models.ForeignKey(Platform, related_name='game_releases')
    region      = models.ForeignKey(Region, related_name='game_releases')
    publisher   = models.ForeignKey(Company, null=True, blank=True, related_name='published_releases')
    date        = models.DateField()
    cover       = models.ImageField(upload_to='covers', blank=True)
    description = models.TextField(blank=True)

    class Admin:
        list_display = ('game', 'platform', 'region', 'date')
        list_filter = ('region',)
        search_fields = ('name', 'description')

    def __unicode__(self):
        return u'%s (%s, %s)' % (self.game, self.region.code, self.platform)

class Screenshot(models.Model):
    """
    A screenshot of a game.
    """
    game        = models.ForeignKey(Game, related_name='screenshots')
    screenshot  = models.ImageField(upload_to='screenshots')
    description = models.TextField(blank=True)

    class Admin:
        list_display = ('game', 'screenshot')
        search_fields = ('description',)

    def __unicode__(self):
        return u'%s screenshot - %s' % (self.game, self.description)

class Trivia(models.Model):
    """
    An item of trivia about a game.
    """
    game   = models.ForeignKey(Game, related_name='trivia')
    body   = models.TextField()
    source = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = 'trivia'

    class Admin:
        search_fields = ('body',)

    def __unicode__(self):
        return u'%s trivia - %s' % (self.game, truncate_words(self.body, 30))

class Link(models.Model):
    """
    A link to an external resource related to a game.
    """
    game        = models.ForeignKey(Game, related_name='links')
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url         = models.URLField()

    class Admin:
        search_fields = ('title', 'description')

    def __unicode__(self):
        return u'%s link - %s' % (self.game, self.url)

class Reviewer(models.Model):
    """
    A games reviewer.
    """
    name        = models.CharField(max_length=100)
    image       = models.ImageField(upload_to='reviewers', blank=True)
    url         = models.URLField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)

    class Admin:
        list_display = ('name', 'url')
        search_fields = ('description',)

    def __unicode__(self):
        return self.name

class Review(models.Model):
    """
    A review of a game.

    Scores should be normalised to a ten-point scale with a single
    decimal place where necessary.
    """
    game        = models.ForeignKey(Game, related_name='reviews')
    reviewer    = models.ForeignKey(Reviewer, related_name='reviews')
    score       = models.DecimalField(max_digits=3, decimal_places=1)
    description = models.TextField(blank=True)
    url         = models.URLField(blank=True)

    class Admin:
        list_display = ('game', 'reviewer', 'score')
        search_fields = ('description',)

    def __unicode__(self):
        return u'%s review of %s' % (self.reviewer, self.game)

#####################
# Warm, Soft People #
#####################

class UserProfile(models.Model):
    user           = models.ForeignKey(User, unique=True, related_name='profile')
    forum_username = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'user profile'
        ordering = ('user',)

    class Admin:
        list_display = ('user', 'forum_username')

    def __unicode__(self):
        return self.forum_username

class Opinion(models.Model):
    """
    Someone's opinion about a game.
    """
    user     = models.ForeignKey(User, related_name='opinions')
    game     = models.ForeignKey(Game, related_name='opinions')
    release  = models.ForeignKey(GameRelease, null=True, blank=True, related_name='opinions')
    pub_date = models.DateTimeField()
    body     = models.TextField()
    source   = models.URLField(blank=True)

    class Meta:
        ordering = ('-pub_date',)

    class Admin:
        list_display = ('user', 'game', 'pub_date')
        list_filter = ('pub_date',)
        search_fields = ('body',)

    def __unicode__(self):
        return u'Opinion about %s by %s' % (self.game, self.user)

class Story(models.Model):
    """
    A story about an experience someone had playing a game.
    """
    user     = models.ForeignKey(User, related_name='stories')
    game     = models.ForeignKey(Game, related_name='stories')
    release  = models.ForeignKey(GameRelease, null=True, blank=True, related_name='stories')
    pub_date = models.DateTimeField()
    title    = models.CharField(max_length=255)
    body     = models.TextField()
    source   = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = 'stories'
        ordering = ('-pub_date',)

    class Admin:
        list_display = ('user', 'game', 'title', 'pub_date')
        list_filter = ('pub_date',)
        search_fields = ('body',)

    def __unicode__(self):
        return u'Story about %s by %s' % (self.game, self.user)

class UserReview(models.Model):
    """
    A user's review of a game.
    """
    user     = models.ForeignKey(User, related_name='reviews')
    game     = models.ForeignKey(Game, related_name='user_reviews')
    release  = models.ForeignKey(GameRelease, null=True, blank=True, related_name='reviews')
    pub_date = models.DateTimeField()
    title    = models.CharField(max_length=255)
    body     = models.TextField()
    score    = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    source   = models.URLField(blank=True)

    class Meta:
        verbose_name = 'user review'
        ordering = ('-pub_date',)

    class Admin:
        list_display = ('user', 'game', 'title', 'pub_date')
        list_filter = ('pub_date',)
        search_fields = ('body',)

    def __unicode__(self):
        return u'Review of %s by %s' % (self.game, self.user)

class Article(models.Model):
    """
    An article about a game.
    """
    user     = models.ForeignKey(User, related_name='articles')
    game     = models.ForeignKey(Game, related_name='articles')
    release  = models.ForeignKey(GameRelease, null=True, blank=True, related_name='articles')
    pub_date = models.DateTimeField()
    title    = models.CharField(max_length=255)
    body     = models.TextField()
    source   = models.URLField(blank=True)

    class Meta:
        ordering = ('-pub_date',)

    class Admin:
        list_display = ('user', 'game', 'title', 'pub_date')
        list_filter = ('pub_date',)
        search_fields = ('title', 'body',)

    def __unicode__(self):
        return u'Article about %s by %s' % (self.game, self.user)
