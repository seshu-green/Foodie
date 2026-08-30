from django.shortcuts import render,redirect
from user.urls import *

def enter(request):
    return redirect('home')

from django.shortcuts import render

def error_404(request, exception):
    return render(request, "404.html", status=404)