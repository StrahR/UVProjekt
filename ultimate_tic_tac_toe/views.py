from django.views import generic

from common.views import (BaseCreateGameView, BaseIndexView, BaseNewGameView,
                          BasePlayView)

from .models import GameUTTT, GameUTTT_ChildGame


class IndexView(BaseIndexView):
    template_name = 'ultimate_tic_tac_toe/index.html'
    model = GameUTTT
    queryset = model.objects.filter(game_over=False)


class CreateGameView(BaseCreateGameView):
    pattern_name = 'uttt:game'
    model = GameUTTT


class GameView(generic.DetailView):
    model = GameUTTT
    template_name = 'ultimate_tic_tac_toe/game.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        g: GameUTTT = context['game']
        context['free_pick'] = GameUTTT_ChildGame.get_game(g, g.prev_i, g.prev_j).winner != 0
        context['my_turn'] = g.current_player() == self.request.user
        return context


class PlayView(BasePlayView):
    pattern_name = 'uttt:game'
    model = GameUTTT
    play_args = ['i', 'j']


class PickView(BasePlayView):
    pattern_name = 'uttt:game'
    model = GameUTTT
    play_args = ['i', 'j', 'row', 'col']


class NewGameView(BaseNewGameView):
    template_name = 'ultimate_tic_tac_toe/new_game.html'
