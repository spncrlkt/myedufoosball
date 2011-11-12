from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^$',
     'stats.views.index'),
    (r'^players/$',
     'stats.views.players'),
    (r'^players/(?P<slug>.+)/$',
     'stats.views.player_detail'),
    #AJAXY POST
    (r'createplayer/$',
     'stats.views.create_player'),
    (r'^teams/$',
     'stats.views.teams'),
    (r'^teams/(?P<id>\d+)/$',
     'stats.views.team_detail'),
    (r'^teams/(?P<slug>.+?)/$',
     'stats.views.team_lookup'),
    #AJAXY POST
    (r'^createteam/$',
     'stats.views.create_team'),
    #AJAXY POST
    (r'^addgame/$',
     'stats.views.add_game'),
    (r'^games/$',
     'stats.views.games'),
    (r'^games/singles/(?P<id>\d+)/$',
     'stats.views.singles_game_detail'),
    (r'^games/singles/$',
     'stats.views.singles_game_list'),
    (r'^games/doubles/(?P<id>\d+)/$',
     'stats.views.doubles_game_detail'),
    (r'^games/doubles/$',
     'stats.views.doubles_game_list'),
)
