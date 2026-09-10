from django.contrib.auth.models import User
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import ProfileSerializer, ChangePasswordSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny] # регистрация открыта для всех

    
class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        # считаем доски и задачи юзера одним запросом через аннотации
        from django.contrib.auth.models import User
        from django.db.models import Q
        return User.objects.annotate(
            boards_count=Count("boards", distinct=True),
            tasks_count=Count("boards__tasks", distinct=True),
        ).get(pk=self.request.user.pk)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Пароль изменён"}, status=status.HTTP_200_OK)


class AvatarUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = request.user.profile
        avatar = request.FILES.get("avatar")
        if not avatar:
            return Response({"detail": "Файл не передан"}, status=400)
        profile.avatar = avatar
        profile.save()
        # вернём URL для мгновенного показа
        url = request.build_absolute_uri(profile.avatar.url)
        return Response({"avatar": url}, status=200)


