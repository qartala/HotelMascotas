import { Component, OnInit } from '@angular/core';
import { ApiService } from '../servicios/api.service';
import { Router } from '@angular/router';
import { Regalia } from '../Modelos/regalia.model';
import { Usuario } from '../Modelos/usuario.model';
import { AlertController } from '@ionic/angular';
import { ToastController } from '@ionic/angular';

@Component({
  selector: 'app-regalias',
  templateUrl: './regalias.page.html',
  styleUrls: ['./regalias.page.scss'],
})
export class RegaliasPage {
  regalias: Regalia[] = [];
  usuario: any
  constructor(private apiService: ApiService, private router: Router,  private alertController: AlertController,private toastController: ToastController) { }


  ionViewWillEnter() {
    this.cargarRegalias();
  }
  async presentToast(position: 'top' | 'middle' | 'bottom',mensaje:string) {
    const toast = await this.toastController.create({
      message: mensaje,
      duration: 3000,
      position: position,
    });

    await toast.present();
  }

  cargarRegalias() {
    this.apiService.getRegalias().subscribe(
      (data: Regalia[]) => {
        this.regalias = data;
        console.log('Regalías cargadas:', this.regalias);
      },
      (error) => {
        console.error('Error al cargar las regalías:', error);
      }
    );
  }

  home(){
    this.router.navigate(['/home'])
  }

  async confirmAgregarRegalia(regalia: any) {
    const alert = await this.alertController.create({
      header: 'Confirmar',
      message: `¿Deseas agregar "${regalia.nombre}" a tus regalos? (Lo podras ver en "Mis regalos" y podras enviarlos cuando quieras)`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
          cssClass: 'secondary',
          handler: () => {
            console.log('Acción cancelada');
          },
        },
        {
          text: 'Agregar',
          handler: () => {
            this.agregarRegalia(regalia);
          },
        },
      ],
    });

    await alert.present();
  }

  agregarRegalia(regalia: any) {
    const cantidad = 1; // Cantidad por defecto, ajustable si es necesario
    const precioTotal = regalia.precio * cantidad; // Calcula el precio total
    const nuevoStock = regalia.stock - cantidad; // Descuenta el stock

    // Validar stock disponible
    if (nuevoStock < 0) {
      this.presentToast("top", "No hay suficiente Stock del producto");
      console.error('No hay suficiente stock disponible para esta regalía.');
      return;
    }

    // Obtener información del usuario
    this.apiService.getUsuarioPerfil().subscribe({
      next: (data) => {
        this.usuario = data;
        const fecha = new Date().toISOString().split('T')[0];
        // Construir datos de la ReservaRegalia
        const reservaRegalia = {

          cliente: this.usuario.idUsuario.id, // ID del cliente
          regalia: regalia.id, // ID de la regalía
          cantidad: cantidad, // Cantidad seleccionada
          precio_total_r: precioTotal, // Precio total calculado
          fecha: fecha, // Fecha actual
        };

        // Verificar y enviar datos
        console.log('Payload enviado:', reservaRegalia);

        // Crear la ReservaRegalia
        this.apiService.crearReservaRegalia(reservaRegalia).subscribe({
          next: (response) => {
            console.log('Reserva creada exitosamente:', response);

            // Actualizar el stock después de crear la reserva
            this.apiService.actualizarStockRegalia(regalia.id, nuevoStock);
            this.presentToast('top','Le enviaste un regalo a tu mascota')
            this.ir('home')
          },
          error: (error) => {
            console.error('Error al crear la reserva:', error);
          },
        });
      },
      error: (error) => {
        console.error('Error al cargar el perfil del usuario:', error);
      },
    });
  }

  ir(url:string){
      this.router.navigate([`/${url}`])
    }


}
