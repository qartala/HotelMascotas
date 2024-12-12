import { Component, OnInit } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Router } from '@angular/router';
import { Membresia, Usuario } from '../Modelos/usuario.model';

@Component({
  selector: 'app-perfil',
  templateUrl: './perfil.page.html',
  styleUrls: ['./perfil.page.scss'],
})
export class PerfilPage {

  usuario: any;
  membresia?: Membresia;
  selectedIcon: string | null = null;
  iconList: string[] = ['person-circle', 'star', 'heart', 'paw', 'happy', 'camera'];

  constructor(private apiService: ApiService,private router: Router) {}

  ionViewWillEnter() {
    this.cargarPerfil();
    this.cargarIcono();
  }

  cargarPerfil() {
    this.apiService.getUsuarioPerfil().subscribe(
      (data) => {
        this.usuario = data;
        this.cargarIcono();
        this.obtenerDetalleMembresia(this.usuario.membresia);
        console.log('Datos del perfil:', data);
        console.log('Datos del perfil:', this.usuario.membresia);
      },
      (error) => {
        console.error('Error al cargar el perfil:', error);
      }
    );
  }

  regresar() {
    this.router.navigate(['/home']);
  }

  selectIcon(icon: string) {
    this.selectedIcon = icon;
    if (this.usuario && this.usuario.idUsuario.username) {
      localStorage.setItem(`icon_${this.usuario.idUsuario.username}`, icon);  // Guardar icono con clave específica del usuario
    }
  }

  cargarIcono() {
    if (this.usuario && this.usuario.idUsuario.username) {
      const savedIcon = localStorage.getItem(`icon_${this.usuario.idUsuario.username}`);
      this.selectedIcon = savedIcon ? savedIcon : 'person-circle-outline';  // Icono por defecto si no existe
    }
  }


  logout() {
    //this.apiService.logout();  // Llama al método de logout en el servicio de la API
    //this.usuario = null;       // Limpia los datos del perfil en la vista
    // this.selectedIcon = null;  // Limpia el icono si también lo guardas en la sesión
    //localStorage.removeItem('selectedIcon');  // Opcional: limpiar el icono seleccionado

    this.router.navigate(['/login']);  // Redirige al login después de cerrar sesión
  }

  obtenerDetalleMembresia(membresiaId: number) {
    if (!membresiaId) {
      this.membresia = undefined; // Si no hay membresía, asegúrate de limpiar la variable
      return;
    }

    this.apiService.getMembresiaDetalle(membresiaId).subscribe(
      (data) => {
        this.membresia = data;
        console.log('Detalle de membresía:', data);
      },
      (error) => {
        console.error('Error al obtener detalle de membresía:', error);
        this.membresia = undefined; // Manejo en caso de error
      }
    );
  }


}
