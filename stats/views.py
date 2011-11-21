from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.shortcuts import render
from models import Player, Team, SinglesGame, DoublesGame
import json

def index(request):
    singles_games = SinglesGame.objects.all()[:5]
    return render(request, 'stats/index.html',
                  {'player_list': Player.objects.all().order_by('-rating'), 
                   'team_list': Team.objects.all().order_by('-rating'),
                   'game_list': singles_games},
                  content_type="html")

def games(request):
    return render(request, 'stats/addgame.html',
                  {'player_list': Player.objects.all(), 'team_list': Team.objects.all()},
                  content_type="html")

def players(request):
    return render(request, 'stats/players.html',
                  {'player_list': Player.objects.all().order_by('-rating')},
                  content_type="html")

def player_detail(request, slug):
    current_player = Player.objects.filter(slug=slug)[0]
    all_players = Player.objects.all().order_by('-rating')
    player_count = all_players.count()
    rank_num = 0
    for index, player in enumerate(all_players):
        if player.slug == slug:
            rank_num = index+1

    game_list_1 = SinglesGame.objects.filter(player_1=current_player)
    game_list_1_wins = game_list_1.filter(player_1_points=10).count()
    total_points = 0
    for game in game_list_1:
        total_points += game.player_1_points
    game_list_2 = SinglesGame.objects.filter(player_2=current_player)
    game_list_2_wins = game_list_2.filter(player_2_points=10).count()
    for game in game_list_2:
        total_points += game.player_2_points
    wins = game_list_1_wins + game_list_2_wins
    total_games = game_list_1.count() + game_list_2.count()
    points_per_game = float(total_points) / float(total_games)
    points_per_game = "%.3f" % (points_per_game)
    losses = total_games - wins
    game_list = game_list_1 | game_list_2
    
    return render(request, 'stats/player_detail.html',
                  {'player': current_player,
                   'game_list': game_list,
                   'rank_num': rank_num,
                   'wins':wins,
                   'total_games':total_games,
                   'losses':losses,
                   'player_count':player_count,
                   'points_per_game':points_per_game},
                  content_type="html")

def teams(request):
    return render(request, 'stats/teams.html',
                  {'team_list': Team.objects.all(),
                   'player_list': Player.objects.all()},
                  content_type="html")

def team_lookup(request,slug):
    current_player = Player.objects.get(slug=slug)
    team_list_1 = Team.objects.filter(player_1=current_player)
    team_list_2 = Team.objects.filter(player_2=current_player)
    team_list = team_list_1 | team_list_2
    return render(request, 'stats/team_lookup.html',
                  {'team_list':team_list,
                   'player':current_player},
                  content_type="html")

def team_detail(request, id):
    current_team = Team.objects.get(id=id)
    all_teams = Team.objects.all().order_by('-rating')
    team_count = all_teams.count()
    rank_num = 0
    for index, team in enumerate(all_teams):
        if team == current_team:
            rank_num = index+1
    game_list_1 = DoublesGame.objects.filter(team_a=current_team)
    game_list_1_wins = game_list_1.filter(team_a_points=10).count()
    total_points = 0
    for game in game_list_1:
        total_points += game.team_a_points
    game_list_2 = DoublesGame.objects.filter(team_b=current_team)
    game_list_2_wins = game_list_2.filter(team_b_points=10).count()
    for game in game_list_2:
        total_points += game.team_b_points
    wins = game_list_1_wins + game_list_2_wins
    total_games = game_list_1.count() + game_list_2.count()
    points_per_game = float(total_points) / float(total_games)
    points_per_game = "%.3f" % (points_per_game)
    losses = total_games - wins
    game_list = game_list_1 | game_list_2
    
    return render(request, 'stats/team_detail.html',
                  {'team': current_team,
                   'game_list': game_list,
                   'rank_num': rank_num,
                   'wins':wins,
                   'total_games':total_games,
                   'losses':losses,
                   'team_count':team_count,
                   'points_per_game':points_per_game},
                  content_type="html")

def create_player(request):
    error_msg = u"No POST data sent."
    if request.method == "POST":
        post = request.POST.copy()
        if post.has_key('name'):
            if Player.objects.filter(name=post['name']).count() > 0:
                error_msg = u"Player with that name already exists!"
            else:
                new_player = Player.objects.create(name=post['name'])
                return HttpResponseRedirect(new_player.get_absolute_url())
        else:
            error_msg = u"Gotta have a name, chief"
    return HttpResponseServerError(error_msg)

def update_player(request):
    if request.method == "POST":
        post = request.POST.copy()
        player = Player.objects.get(slug=post['slug'])
        if post.has_key('name'):
            name = post['name']
            if player.name != name:
                if Player.objects.filter(name=name).count() > 0:
                    error_msg = u"Name already taken."
                    return HttpResponseServerError(error_msg)
                player.name = name
        player.save()
        return_dict = {}
        return_dict['new_slug'] = player.slug
        return HttpResponse(json.dumps(return_dict), mimetype="application/json")
    error_msg = u"No POST data sent."
    return HttpResponseServerError(error_msg)

def return_team_or_none(player_1, player_2):
    player_1_instance = Player.objects.get(slug=player_1)
    player_2_instance = Player.objects.get(slug=player_2)
    first_try = Team.objects.filter(player_1=player_1_instance, player_2=player_2_instance)
    if first_try.count() > 0:
        return first_try[0]
    second_try = Team.objects.filter(player_1=player_2_instance, player_2=player_1_instance)
    if second_try.count() > 0:
        return second_try[0]
    else:
        new_team = Team.objects.create(player_1=player_1_instance, player_2=player_2_instance)
        return new_team

def create_team(request):
    error_msg = u"No POST data sent."
    if request.method == "POST":
        post = request.POST.copy()
        if post.has_key('team_player_1') and post.has_key('team_player_2'):
            if not post['team_player_1'] == post['team_player_2']:
                player_1 = Player.objects.filter(slug=post['team_player_1'])
                player_1_instance = player_1[0]
                player_2 = Player.objects.filter(slug=post['team_player_2'])
                player_2_instance = player_2[0]
                if not return_team_or_none(player_1_instance.slug, player_2_instance.slug):
                    new_team = Team.objects.create(player_1=player_1_instance,
                                                   player_2=player_2_instance)
                    return HttpResponseRedirect(new_team.get_absolute_url())
                else:
                    error_msg = u"Team already exists"
            else:
                error_msg = u"Select 2 DIFFERENT players!"
        else:
            error_msg = u"Gotta select 2 players!"
    return HttpResponseServerError(error_msg)

def add_game(request):
    error_msg = u"No POST data sent."
    if request.method == "POST":
        post = request.POST.copy()
        if (post['team_a_points'] == "10") or (post['team_b_points'] == "10"):
            player_a_1 = Player.objects.filter(slug=post['name_a_1'])
            player_a_1_instance = player_a_1[0]
            player_b_1 = Player.objects.filter(slug=post['name_b_1'])
            player_b_1_instance = player_b_1[0]
            if post['game_type'] == 'singles':
                new_game = SinglesGame.objects.create(player_1=player_a_1_instance, 
                                                      player_2=player_b_1_instance,
                                                      player_1_points = int(post['team_a_points']),
                                                      player_2_points = int(post['team_b_points']))
                return HttpResponseRedirect(new_game.get_absolute_url())
            elif post['game_type'] == 'doubles':
                team_a_maybe = return_team_or_none(post['name_a_1'], post['name_a_2'])
                team_b_maybe = return_team_or_none(post['name_b_1'], post['name_b_2'])
                if team_b_maybe and team_b_maybe:
                    new_game = DoublesGame.objects.create(team_a=team_a_maybe, team_b=team_b_maybe,
                                                          team_a_points=int(post['team_a_points']),
                                                          team_b_points=int(post['team_b_points']))
                    return HttpResponseRedirect(new_game.get_absolute_url())
                else:
                    error_msg = u"No team for that combination"
        else:
            error_msg = u"Nobody won!"
    return HttpResponseServerError(error_msg)

def singles_game_detail(request, id):
    game = SinglesGame.objects.get(id=id)
    return render(request, 'stats/singles_game_detail.html',
                  {'game':game},
                  content_type="html")

def singles_game_list(request):
    singles_game_list = SinglesGame.objects.all()
    player_list = Player.objects.all().order_by('-rating')
    return render(request, 'stats/singles_game_list.html',
                  {'singles_game_list':singles_game_list, 'player_list':player_list},
                  content_type="html")

def doubles_game_detail(request, id):
    game = DoublesGame.objects.get(id=id)
    return render(request, 'stats/doubles_game_detail.html',
                  {'game':game},
                  content_type="html")

def doubles_game_list(request):
    doubles_game_list = DoublesGame.objects.all()
    team_list = Team.objects.all().order_by('-rating')
    return render(request, 'stats/doubles_game_list.html',
                  {'doubles_game_list':doubles_game_list, 'team_list':team_list},
                  content_type="html")
