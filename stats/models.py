import math
from django.db import models
from django.template.defaultfilters import slugify

class Player(models.Model):
    name    = models.CharField(max_length=50)
    slug    = models.SlugField()
    rating  = models.IntegerField(default=1200)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Player, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return u"/players/%s/" % self.slug    

class Team(models.Model):
    player_1 = models.ForeignKey('Player', related_name='team_player_1')
    player_2 = models.ForeignKey('Player', related_name='team_player_2')
    rating   = models.IntegerField(default=1200)
    
    def __unicode__(self):
        return self.player_1.name + " & " + self.player_2.name

    def get_absolute_url(self):
        return u"/teams/%d/" % self.id


def update_rating(game_type, entity_1, entity_2, entity_1_points, entity_2_points):
    expected_scores = {0:.5, 20:.53, 40:.58, 60:.62, 80:.66, 100:.69,
                       120:.73, 140:.76, 160:.79, 180:.82, 200:.84, 300:84, 400:.97}
    rating_diff = abs(entity_1.rating - entity_2.rating)
    if rating_diff < 200:
        rounded_diff = math.floor(rating_diff / 20)*20
    elif rating_diff < 500:
        rounded_diff = math.floor(rating_diff / 100)*100
    else:
        rounded_diff=400
    expected_score = expected_scores[rounded_diff]
    entity_1_points = math.floor(entity_1_points/10)
    entity_2_points = math.floor(entity_2_points/10)
    entity_1.rating = entity_1.rating + 30*(entity_1_points - expected_score)
    entity_1.save()
    entity_2.rating = entity_2.rating + 30*(entity_2_points - expected_score)
    entity_2.save()

class SinglesGame(models.Model):
    player_1 = models.ForeignKey('Player', related_name='game_player_1')
    player_2 = models.ForeignKey('Player', related_name='game_player_2')
    player_1_points = models.IntegerField()
    player_2_points = models.IntegerField()
    date_played = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return u"/games/singles/%d/" % self.id

    def save(self, *args, **kwargs):
        update_rating("singles", self.player_1, self.player_2, self.player_1_points, self.player_2_points)
        super(SinglesGame, self).save(*args, **kwargs)

class DoublesGame(models.Model):
    team_a = models.ForeignKey('Team', related_name='game_team_a')
    team_b = models.ForeignKey('Team', related_name='game_team_b')
    team_a_points = models.IntegerField()
    team_b_points = models.IntegerField()
    date_played = models.DateField(auto_now_add=True)
    def get_absolute_url(self):
        return u"/games/doubles/%d/" % self.id

    def save(self, *args, **kwargs):
        update_rating("singles", self.team_a, self.team_b, self.team_a_points, self.team_b_points)
        super(DoublesGame, self).save(*args, **kwargs)

# Create your models here.
