from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
import time
from .models import Message
from .serializers import MessageSerializer
from django.views.generic import TemplateView

# Configura el cliente de OpenAI
client = OpenAI(api_key="sk-terra-ia-CuzITqoRaFH3F4QtAHE1T3BlbkFJuj8VNwIRpjQJIDsbO6UX")
ASSISTANT_ID = "asst_yTj33ljPkSdtgbRJi3DyezYs"

class ChatBotView(APIView):
    def post(self, request):
        user_message = request.data.get('message')
        if user_message:
            # Crear un nuevo hilo de chat
            chat = client.beta.threads.create(messages=[{"role": "user", "content": user_message}])
            
            # Crear una nueva ejecución de hilo
            run = client.beta.threads.runs.create(thread_id=chat.id, assistant_id=ASSISTANT_ID, tool_choice="auto")
            
            # Esperar a que se complete la ejecución
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(thread_id=chat.id, run_id=run.id)
                if run.status == "failed":
                    return Response({"error": "Failed to get a response from the assistant"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                time.sleep(0.5)
            
            # Obtener la respuesta del asistente
            messages_response = client.beta.threads.messages.list(thread_id=chat.id)
            messages = messages_response.data
            latest_message = messages[0].content[0].text.value
            
            # Guardar el mensaje y la respuesta en la base de datos
            message = Message.objects.create(user_message=user_message, bot_response=latest_message)
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Message not provided"}, status=status.HTTP_400_BAD_REQUEST)

class ChatPageView(TemplateView):
    template_name = "chat.html"