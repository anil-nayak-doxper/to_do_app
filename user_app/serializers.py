from curses.ascii import US
from django.contrib.auth.models import User
from rest_framework import serializers


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    def save(self):
        password = self.validated_data['password']
        account = User(
            email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(password)
        account.save()
        return account
