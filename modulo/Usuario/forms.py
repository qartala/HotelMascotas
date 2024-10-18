from django import forms
from .models import Ficha
from .models import Calificacion

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
    

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.NumberInput(attrs={
                'min': 1, 'max': 5, 'step': 1, 'class': 'form-control'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3
            }),
        }
        
class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Nombre',
        'class': 'form-control'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'E-mail',
        'class': 'form-control' 
    }))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Mensaje',
        'class': 'form-control',
        'rows': 4,
    }))