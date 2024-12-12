from django import forms
from .models import Ficha
from modulo.Usuario.models import Usuario

class FichaSaludForm(forms.ModelForm):

    class Meta:
        model = Ficha
        fields = ['nombre_perro', 'nombre_dueno', 'raza', 'edad', 'peso', 'chip', 'comida', 'vacunas', 'alergias', 'enfermedades', 'imagen_mascota']

    def clean_vacunas(self):
        vacunas = self.cleaned_data['vacunas'].strip()
        return ', '.join(vacunas.splitlines())
    def clean_alergias(self):
        alergias = self.cleaned_data['alergias'].strip()
        return ', '.join(alergias.splitlines())
    def clean_enfermedades(self):
        enfermedades = self.cleaned_data['enfermedades'].strip()
        return ', '.join(enfermedades.splitlines())
    
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'idUsuario', 'tipo_cuenta', 'membresia', 'telefono', 
            'direccion', 'fecha_nacimiento', 'trabajador'
        ]
        widgets = {
            'trabajador': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }