from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from user_app.serializers import SignupSerializer


@api_view(['POST', ])
def signup_view(request):
    if request.method == 'POST':
        serializer = SignupSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            token, created = Token.objects.get_or_create(user=account)
            data['response'] = "Signup Successful!"
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['username'] = account.username
            data['email'] = account.email
            data['token'] = token.key
        else:
            data = serializer.errors
        return Response(data)


@api_view(['POST', ])
def logout_view(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response({'response': 'Logged out and token removed'})
