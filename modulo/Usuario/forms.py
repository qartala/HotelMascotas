from django import forms
from .models import Ficha

class FichaSaludForm(forms.ModelForm):
    # Definir las opciones para los campos con selección múltiple

    class Meta:
        model = Ficha
        fields = ['nombre_perro', 'nombre_dueno', 'raza', 'edad', 'peso', 'chip', 'comida', 'vacunas', 'alergias', 'enfermedades']

    def clean_vacunas(self):
        # Procesar el textarea, eliminando posibles saltos de línea adicionales
        vacunas = self.cleaned_data['vacunas'].strip()
        return ', '.join(vacunas.splitlines())
    def clean_alergias(self):
        # Procesar el textarea, eliminando posibles saltos de línea adicionales
        alergias = self.cleaned_data['alergias'].strip()
        return ', '.join(alergias.splitlines())
    def clean_enfermedades(self):
        # Procesar el textarea, eliminando posibles saltos de línea adicionales
        enfermedades = self.cleaned_data['enfermedades'].strip()
        return ', '.join(enfermedades.splitlines())
