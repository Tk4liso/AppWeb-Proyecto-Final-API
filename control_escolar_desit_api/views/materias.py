from django.db.models import *
from django.db import transaction
from control_escolar_desit_api.serializers import MateriasSerializer
from control_escolar_desit_api.models import Materias
from rest_framework import permissions
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class MateriasAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        lista = MateriasSerializer(materias, many=True).data
        return Response(lista, 200)


class MateriasView(generics.CreateAPIView):
    @transaction.atomic
    #Registrar
    def post(self, request, *args, **kwargs):
        serializer = MateriasSerializer(data=request.data)
        if serializer.is_valid():
            materia = serializer.save()
            return Response({"materia_created_id": materia.id}, 201)
        return Response(serializer.errors, 400)

    #Obtener
    def get(self, request, *args, **kwargs):
        materia_id = request.GET.get("id")
        if not materia_id:
            return Response({"details": "Falta el id de la materia"}, 400)

        materia = get_object_or_404(Materias, id=materia_id)
        data = MateriasSerializer(materia).data
        return Response(data, 200)

    #Actualizar
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        materia_id = request.data.get("id")
        if not materia_id:
            return Response({"details": "Falta el id de la materia"}, 400)

        materia = get_object_or_404(Materias, id=materia_id)
        serializer = MateriasSerializer(materia, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"details": "Materia actualizada correctamente"}, 200)

        return Response(serializer.errors, 400)

    #Eliminar
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details": "Materia eliminada"}, 200)
        except Exception:
            return Response({"details": "Algo pasó al eliminar"}, 400)
