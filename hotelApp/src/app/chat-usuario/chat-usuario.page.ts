import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../servicios/api.service';
import { Mensaje } from '../Modelos/usuario.model';

@Component({
  selector: 'app-chat-usuario',
  templateUrl: './chat-usuario.page.html',
  styleUrls: ['./chat-usuario.page.scss'],
})
export class ChatUsuarioPage implements OnInit {
  reservaId: number = 0;
  mensajes: any[] = [];
  nuevoMensaje: string = '';
  emisorId: number = 0; // ID del cliente
  receptorId: number = 0; // ID del trabajador

  constructor(private route: ActivatedRoute, private apiService: ApiService) {}

  ngOnInit() {
    this.reservaId = Number(this.route.snapshot.paramMap.get('id'));
    const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');
    this.emisorId = usuario?.id || 0;

    if (this.reservaId) {
      this.apiService.getReserva(this.reservaId).subscribe((reserva) => {
        this.receptorId = reserva.trabajador?.id || 0; // Trabajador es el receptor
      });
      this.cargarHistorialChat();
    } else {
      console.error('ID de reserva inválido.');
    }
  }

  cargarHistorialChat() {
    this.apiService.obtenerHistorialChat(this.reservaId).subscribe(
      (mensajes: Mensaje[]) => {
        // Agregar propiedad `esEnviado` para diferenciar mensajes
        this.mensajes = mensajes.map((mensaje) => ({
          ...mensaje,
          esEnviado: mensaje.emisor.id === this.emisorId, // Compara con el ID del usuario actual
        }));
        console.log('Historial cargado:', this.mensajes);
      },
      (error) => {
        console.error('Error al cargar el historial del chat:', error);
      }
    );
  }

  enviarMensaje() {
    if (!this.nuevoMensaje.trim()) {
      console.warn('No se puede enviar un mensaje vacío');
      return;
    }

    console.log('Datos que se envían al backend:', {
      reserva_id: this.reservaId,
      contenido: this.nuevoMensaje,
      emisor_id: this.emisorId,
    });

    this.apiService
      .enviarMensaje(this.reservaId, this.nuevoMensaje, this.emisorId)
      .subscribe({
        next: (mensaje) => {
          this.mensajes.push({
            ...mensaje,
            esEnviado: true,
          });
          this.nuevoMensaje = '';
        },
        error: (error) => {
          console.error('Error al enviar el mensaje:', error);
        },
      });
  }


}
