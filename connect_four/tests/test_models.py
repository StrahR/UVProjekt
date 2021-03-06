from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import GameCF
from common.models import DataCell


class TicTacToeModelTests(TestCase):

    def setUp(self):
        self.p1 = get_user_model().objects.create_user('p1')
        self.p2 = get_user_model().objects.create_user('p2')

    def test_new_game(self):
        game = GameCF.new_game(p1=self.p1, p2=self.p2)
        self.assertIsInstance(game.pk, int)

    def test_play_returns_true(self):
        game = GameCF.new_game(p1=self.p1, p2=self.p2)
        b = game.play(0)
        self.assertTrue(b)

    def test_play_plays_as_player(self):
        game = GameCF.new_game(p1=self.p1, p2=self.p2)

        game.play(0)
        cell1 = DataCell.objects.get(id_game=game.pk, row=GameCF.HEIGHT-1, col=0)
        self.assertEqual(cell1.data, 1)
        self.assertEqual(game.player, 2)

        game.play(1)
        cell2 = DataCell.objects.get(id_game=game.pk, row=GameCF.HEIGHT-1, col=1)
        self.assertEqual(cell2.data, 2)
        self.assertEqual(game.player, 1)

    def test_check_win(self):
        game = GameCF.new_game(p1=self.p1, p2=self.p2)
        game.play(0)
        game.play(1)
        game.play(0)
        game.play(1)
        game.play(0)
        game.play(1)
        game.play(0)
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, 1)
