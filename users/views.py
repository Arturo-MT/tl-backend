from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from users.models import User
from users.permissions import IsSelfOrStaffOrSuperuser
from users.serializers import MyTokenObtainPairSerializer, UserSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (AllowAny,)

class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            return Response({'detail': 'A user with that username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=serializer.validated_data['email']).exists():
            return Response({'detail': 'A user with that email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'is_seller': user.is_seller,
            'id': user.id,
        }
        return Response(data, status=status.HTTP_201_CREATED)

class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrStaffOrSuperuser]
