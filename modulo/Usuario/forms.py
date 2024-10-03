from django import forms
from .models import Ficha  # Importa el modelo de la ficha de salud

class FichaSaludForm(forms.ModelForm):
    class Meta:
        model = Ficha
        fields = ['nombre_perro','nombre_dueno', 'raza', 'edad', 'peso', 'chip', 'comida', 'vacunas', 'alergias', 'enfermedades']