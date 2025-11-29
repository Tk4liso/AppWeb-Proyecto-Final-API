from django.db.models import *
from django.db import transaction
from control_escolar_desit_api.serializers import UserSerializer
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
#ToDo: DelEdit
from django.shortcuts import get_object_or_404

class AlumnosAll(generics.CreateAPIView):
    #Verificar si el usuario esta autenticado
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        
        return Response(lista, 200)
    
class AlumnosView(generics.CreateAPIView):
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Create a profile for the user
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado con ID: ": alumno.id }, 201)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #ToDo: EditDel - brr
    def get(self, request, *args, **kwargs):
        alumno_id = request.GET.get("id")
        if not alumno_id:
            return Response({"details": "Falta el id del alumno"}, 400)

        alumno = get_object_or_404(Alumnos, id=alumno_id)
        user = alumno.user

        data = {
            "id": alumno.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "matricula": alumno.matricula,
            "curp": alumno.curp,
            "rfc": alumno.rfc,
            "fecha_nacimiento": alumno.fecha_nacimiento,
            "edad": alumno.edad,
            "telefono": alumno.telefono,
            "ocupacion": alumno.ocupacion,
            "rol": "alumno"
        }
        return Response(data, 200)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        alumno_id = request.data.get("id")
        if not alumno_id:
         return Response({"details": "Falta el id del alumno"}, 400)

        alumno = get_object_or_404(Alumnos, id=alumno_id)
        user = alumno.user

        # Actualizar datos del usuario
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.username = user.email
        user.save()

        # Actualizar perfil alumno
        alumno.matricula = request.data.get("matricula", alumno.matricula)
        alumno.curp = request.data.get("curp", alumno.curp)
        alumno.rfc = request.data.get("rfc", alumno.rfc)
        alumno.fecha_nacimiento = request.data.get("fecha_nacimiento", alumno.fecha_nacimiento)
        alumno.edad = request.data.get("edad", alumno.edad)
        alumno.telefono = request.data.get("telefono", alumno.telefono)
        alumno.ocupacion = request.data.get("ocupacion", alumno.ocupacion)
        alumno.save()

        return Response({"details": "Alumno actualizado correctamente"}, 200)
    
    #ToDo: EditDel - Eliminar alumno
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            alumno.user.delete()
            return Response({"details": "Alumno eliminado"}, 200)
        except Exception:
            return Response({"details": "Ocurrió un error al eliminar"}, 400)
