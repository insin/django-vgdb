import datetime

from django.contrib.auth.models import User

from vgdb.models import *

admin = User.objects.create_user('admin', 'a@a.com', 'admin')
admin.first_name = 'Admin'
admin.last_name = 'User'
admin.is_staff = True
admin.is_superuser = True
admin.save()

# Regions
aus = Region.objects.create(code='AUS', name='Australia')
eu = Region.objects.create(code='EU', name='Europe')
jp = Region.objects.create(code='JP', name='Japan')
na = Region.objects.create(code='NA', name='North America')

# Companies
nintendo = Company.objects.create(name='Nintendo',
                                  url='http://www.nintendo.com')
nintendo_ead = Company.objects.create(name='Nintendo EAD')

# Platform types
console = PlatformType.objects.create(name='Console')

# Platforms
snes = Platform.objects.create(name='SNES', type=console,
                               manufacturer=nintendo)

# Platform releases
PlatformRelease.objects.create(platform=snes, name='Super Famicom', region=jp,
                               date=datetime.date(1990, 11, 21))
PlatformRelease.objects.create(platform=snes, region=na,
                               date=datetime.date(1991, 8, 13))
PlatformRelease.objects.create(platform=snes, region=eu,
                               date=datetime.date(1992, 4, 11))
PlatformRelease.objects.create(platform=snes, region=aus,
                               date=datetime.date(1992, 7, 3))

# Genres
platform = Genre.objects.create(name='Platform')
platform_2d = Genre.objects.create(name='2D Platform', parent=platform)

# Series
smb = Series.objects.create(name='Super Mario Bros.')

# Games
smw = Game.objects.create(name='Super Mario World', series=smb,
                          genre=platform_2d, publisher=nintendo,
                          developer=nintendo_ead)

# Game releases
GameRelease.objects.create(game=smw, platform=snes, region=jp,
                           date=datetime.date(1990, 11, 21))
GameRelease.objects.create(game=smw, platform=snes, region=na,
                           date=datetime.date(1991, 8, 13))
GameRelease.objects.create(game=smw, platform=snes, region=eu,
                           date=datetime.date(1992, 6, 4))
