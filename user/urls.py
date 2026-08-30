from django.urls import path
from user.views import chat_page, foods_page, log, home, out, flush, save_chat_history, start_chat,health_page
# Food/urls.py
handler404 = "user.views.error_404"
urlpatterns = [
    path('', log, name='log'),
    path('home/', home, name='home'),
    path('flush/', flush, name='flush'),
    path('out/', out, name='bye'),
    path('chat/', chat_page, name='chat'), # <-- Renders the actual layout interface,
    path('save_chat_history/', save_chat_history, name='save_chat_history'),
    path('start_chat/', start_chat, name='start_chat'),  # <-- add this
    path('foods/', foods_page, name='foods'),
    path('health/', health_page, name='health_page')
]
