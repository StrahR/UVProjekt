from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Player


class PlayerCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = Player
        fields = ('username', 'email', 'full_name')


class PlayerChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = Player
        fields = ('username', 'email', 'full_name')
