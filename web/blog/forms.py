from django import forms


class SearchWordForm(forms.Form):
    search_word = forms.CharField(label="search_word", max_length=100)
