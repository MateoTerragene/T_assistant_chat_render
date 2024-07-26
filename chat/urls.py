from django.urls import path
from .views import ChatBotView, ChatPageView

urlpatterns = [
    path('', ChatPageView.as_view(), name='chat_page'),
    path('api/chat/', ChatBotView.as_view(), name='chatbot'),
]