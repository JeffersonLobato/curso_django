from django.shortcuts import render
from .models import Topic

def index(request):
    """A página inicial de Learning Log"""
    return render(request, 'learning_logs/index.html')