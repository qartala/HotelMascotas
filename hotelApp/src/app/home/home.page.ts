import { Component, OnInit, OnDestroy } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage implements OnInit, OnDestroy {
  esTrabajador: boolean = false;
  private usuarioSubscription!: Subscription;

  constructor(private apiService: ApiService, private router: Router) {}

  ngOnInit() {
    this.suscribirseAlUsuario();
  }

  ngOnDestroy() {
    if (this.usuarioSubscription) {
      this.usuarioSubscription.unsubscribe();
    }
  }

  suscribirseAlUsuario() {
    this.usuarioSubscription = this.apiService.getUsuarioData().subscribe(usuario => {
      if (usuario) {
        console.log('Usuario encontrado:', usuario);
        this.esTrabajador = usuario.trabajador;
      } else {
        console.warn('No se encontró el usuario');
        this.esTrabajador = false;
      }
    });
  }

  logout() {
    this.apiService.logout();
    this.router.navigate(['/login']);
  }

  reedirigir() {
    if (this.esTrabajador) {
      console.log('Redirigiendo a Reservas');
      this.router.navigate(['/reservas']);
    } else {
      console.warn('El usuario no es trabajador. Redirigiendo a Home');
      this.router.navigate(['/home']);
    }
  }



  ir(url:string){
    this.router.navigate([`/${url}`])
  }

  redirigirPerfil() {
    this.router.navigate(['/perfil']);  // Reemplaza 'perfil' por la ruta correcta en tu sistema de rutas
  }

  irSeguimientoUsuario() {
    this.router.navigate(['/seguimiento-usuario']);
  }
}
