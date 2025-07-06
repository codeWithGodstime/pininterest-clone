from django import forms
from .models import Board, Pin, Tag

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'description', 'privacy', 'image']

class PinForm(forms.ModelForm):
    class Meta:
        model = Pin
        fields = ['title', 'description', 'image', 'board', 'tags']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['board'].queryset = Board.objects.filter(owner=user)
        else:
            self.fields['board'].queryset = Board.objects.none()

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name'] 