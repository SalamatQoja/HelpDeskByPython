from helpdeskside.models import Ticket, Comment
from django import forms


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': forms.TextInput(attrs={'rows': 3 ,'placeholder': 'Ваш комментарий'})}
