from django import forms
from .models import Ficha, Disponibilidad,Colaborador

class FichaSaludForm(forms.ModelForm):
    # Definir las opciones para los campos con selección múltiple

    class Meta:
        model = Ficha
        fields = ['nombre_perro', 'nombre_dueno', 'raza', 'edad', 'peso', 'chip', 'comida', 'vacunas', 'alergias', 'enfermedades', 'imagen_mascota']

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
    
class PerfilColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['descripcion', 'foto_perfil']  # Asegúrate de que estos campos existen en tu modelo

    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Descripción",
        required=False
    )

    foto_perfil = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Foto de Perfil",
        required=False
    )


class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model = Disponibilidad
        fields = ['fecha', 'hora_inicio', 'hora_fin']

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Selecciona la fecha"
    )
    
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Hora de inicio"
    )

    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Hora de fin"
    )

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                raise forms.ValidationError("La hora de fin debe ser mayor a la hora de inicio.")
