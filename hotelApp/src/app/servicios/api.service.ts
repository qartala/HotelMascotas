import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { lastValueFrom } from 'rxjs';
import { Reserva } from '../Modelos/reserva.model';
import { Regalia } from '../Modelos/regalia.model';
import { ServiciosComunes } from '../Modelos/reserva.model';
import { Mensaje } from '../Modelos/usuario.model';
import { catchError } from 'rxjs/operators'; // Importa el operador catchError
import { throwError } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrlLogin = 'http://localhost:8000/api/login/';
  private apiUrlReservas = 'http://localhost:8000/api/reservas';
  private apiUrlRegalias = 'http://localhost:8000/api/regalias/';
  private apiUrlServiciosComunes = 'http://localhost:8000/api/servicios-comunes/';
  private apiUrlPerfil = 'http://localhost:8000/api/perfil/';
  private apiUrlChat = 'http://localhost:8000/api/chat/';
  private usuarioData = new BehaviorSubject<any>(null);
  private apiUrlMembresia = 'http://localhost:8000/api/membresia/';
  private apiUrlSeguimientoU = 'http://localhost:8000/api/seguimiento/servicios/';
  private apiUrl = 'http://localhost:8000/api/';
  private apiUrlVideo = 'http://localhost:8000/api/videos/';

  // private mediaUrl = 'http://localhost:8000'; // Cambia esta URL por tu dominio


  constructor(private http: HttpClient) {
    this.cargarUsuarioDesdeLocalStorage();
  }
  agregarRegalia(data: { regalia_id: number; mascota_id: number; cantidad: number }): Observable<any> {
    const url = 'http://localhost:8000/api/agregar-regalia/';
    return this.http.post<any>(url, data, { headers: this.getHeaders() });
  }


  getMediaUrl(filePath: string): string {
    const baseUrl = 'http://localhost:8000';// Cambia esto por tu dominio o IP del servidor
    const concat = `${baseUrl}${filePath}`
    console.log('concatenacion getMediaUrl',concat);
    return concat;
  }

  private cargarUsuarioDesdeLocalStorage(): void {
    const usuario = localStorage.getItem('usuario');
    if (usuario) {
      this.usuarioData.next(JSON.parse(usuario));
    }
  }

  getMembresiaDetalle(id: number): Observable<any> {
    const url = `${this.apiUrlMembresia}${id}/`; // Asegúrate de que `this.apiUrl` esté configurado correctamente
    return this.http.get<any>(url);
  }

  getUsuarioData(): Observable<any> {
    return this.usuarioData.asObservable();
  }

  async login(username: string, password: string): Promise<boolean> {
    try {
      const response = await lastValueFrom(
        this.http.post<any>(this.apiUrlLogin, { username, password })
      );

      if (response) {
        const { access, refresh, usuario } = response;

        // Guarda los tokens y datos del usuario en el almacenamiento local
        this.setToken(access);
        this.setRefreshToken(refresh);
        this.setUsuarioData(usuario);

        // Lógica adicional si es un trabajador
        if (usuario.trabajador) {
          console.log('Inicio de sesión como trabajador');
        } else {
          console.log('Inicio de sesión como usuario');
        }

        return true;
      }
      return false;
    } catch (error) {
      this.handleError(error);
      return false;
    }
  }

  private handleError(error: any): void {
    if (error instanceof HttpErrorResponse) {
      switch (error.status) {
        case 400:
          console.warn('Solicitud incorrecta. Verifica los datos enviados.');
          break;
        case 401:
          console.warn('Credenciales incorrectas.');
          break;
        case 404:
          console.warn('Usuario no encontrado.');
          break;
        case 500:
          console.error('Error en el servidor. Contacta al administrador.');
          break;
        default:
          console.error('Error inesperado:', error);
      }
    } else {
      console.error('Error no relacionado con HTTP:', error);
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  private getHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    });
  }

  setToken(token: string): void {
    localStorage.setItem('token', token);
  }

  setRefreshToken(token: string): void {
    localStorage.setItem('refresh_token', token);
  }

  setUsuarioData(usuario: any): void {
    this.usuarioData.next(usuario);
    localStorage.setItem('usuario', JSON.stringify(usuario));
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('usuario');
    this.usuarioData.next(null);
  }

  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  getReservas(): Observable<Reserva[]> {
    return this.http.get<Reserva[]>(this.apiUrlReservas, { headers: this.getHeaders() });
  }

  getReserva(id: number): Observable<Reserva> {
    const url = `${this.apiUrlReservas}/${id}/`;
    return this.http.get<Reserva>(url, { headers: this.getHeaders() });
  }

  actualizarReservaCheckIn(id: number, reserva: Partial<Reserva>): Observable<any> {
    const url = `${this.apiUrlReservas}/${id}/check-in/`;
    return this.http.put(url, reserva, { headers: this.getHeaders() });
  }

  actualizarEstadoPagado(id: number, pagado: boolean): Observable<any> {
    const url = `${this.apiUrlReservas}/${id}/pagado/`;
    return this.http.put(url, { pagado }, { headers: this.getHeaders() });
  }

  getRegalias(): Observable<Regalia[]> {
    return this.http.get<Regalia[]>(this.apiUrlRegalias, { headers: this.getHeaders() });
  }

  actualizarStockRegalia(regaliaId: number, nuevoStock: number) {
    const url = `${this.apiUrlRegalias}${regaliaId}/`; // Endpoint para actualizar la regalía
    const data = { stock: nuevoStock };

    this.http.patch(url, data, { headers: this.getHeaders() }).subscribe({
      next: (response) => {
        console.log('Stock actualizado exitosamente:', response);
        // Aquí puedes manejar la actualización de la lista de regalías en la interfaz
      },
      error: (error) => {
        console.error('Error al actualizar el stock:', error);
      },
    });
  }

  getServiciosComunes1(idFicha: number, idReserva: number): Observable<ServiciosComunes[]> {
    const url = `${this.apiUrlServiciosComunes}${idFicha}/${idReserva}/`;
    const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.getToken()}` });
    return this.http.get<ServiciosComunes[]>(url, { headers });
  }

  getServiciosComunes(reservaId: number): Observable<ServiciosComunes[]> {
    const url = `${this.apiUrlSeguimientoU}${reservaId}/`;
    const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.getToken()}` });
    return this.http.get<ServiciosComunes[]>(url, { headers });
}

  actualizarServicioComun(idFicha: number, servicio: Partial<ServiciosComunes>): Observable<any> {
    const url = `http://localhost:8000/api/servicios/${idFicha}/`;
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.getToken()}`,
      'Content-Type': 'application/json'
    });

  return this.http.patch(url, servicio, { headers });
}
  crearServiciosComunes(servicio: ServiciosComunes): Observable<ServiciosComunes> {
    const url = 'http://localhost:8000/api/servicios/';
    return this.http.post<ServiciosComunes>(url, servicio, {
      headers: this.getHeaders(),
    });
  }

  subirEvidencia(servicioId: number, campo: string, file: File): Observable<any> {
    const url = `${this.apiUrlServiciosComunes}${servicioId}/subir-evidencia/${campo}/`;
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post(url, formData, { headers: this.getHeaders() });
  }

  getUsuarioPerfil(): Observable<any> {
    const token = this.getToken();  // Obtén el token del localStorage o donde lo hayas almacenado

    const headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`,  // Agrega el token en el encabezado
    });

    return this.http.get<any>(this.apiUrlPerfil, { headers });
}

obtenerHistorialChat(reservaId: number): Observable<Mensaje[]> {
  const url = `${this.apiUrlChat}history/${reservaId}/`;
  return this.http.get<Mensaje[]>(url, { headers: this.getHeaders() });
}


enviarMensaje(reservaId: number, contenido: string, emisorId: number): Observable<Mensaje> {
  const url = `${this.apiUrlChat}enviar/`;
  const body = { reserva_id: reservaId, contenido, emisor_id: emisorId };
  return this.http.post<Mensaje>(url, body, { headers: this.getHeaders() });
}



  asignarTrabajador(reservaId: number): Observable<any> {
    const url = `http://localhost:8000/api/reservas/${reservaId}/asignar-trabajador/`;
    return this.http.patch(url, {}, { headers: this.getHeaders() });
  }


  getServiciosPorReserva(reservaId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrlServiciosComunes}/servicios/reserva/${reservaId}`);
  }

  getReservasPorUsuario(clienteId: number): Observable<Reserva[]> {
    const url = `${this.apiUrlReservas}?cliente__id=${clienteId}`;
    return this.http.get<Reserva[]>(url).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error(`Error al obtener reservas para el cliente ${clienteId}:`, error);
        return throwError(() => new Error('No se pudieron cargar las reservas del cliente.'));
      })
    );
  }

  getSeguimiento(idFicha: number, idReserva: number): Observable<any[]> {
    const url = `${this.apiUrlServiciosComunes}?ficha=${idFicha}&reserva=${idReserva}`; // Ajusta los nombres de los parámetros según tu backend
    return this.http.get<any[]>(url).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error(`Error al obtener el seguimiento para ficha ${idFicha} y reserva ${idReserva}:`, error);
        return throwError(() => new Error('No se pudieron cargar los datos de seguimiento.'));
      })
    );
  }

    // Método para crear una ReservaRegalia
    crearReservaRegalia(data: any): Observable<any> {
      const url = `${this.apiUrl}reservaregalia1/`; // Endpoint para crear reservas
      return this.http.post(url, data, { headers: this.getHeaders() });
    }
    modificarReservaRegalia(data: any): Observable<any> {
      const url = `${this.apiUrl}reservaregalia/${data.id}/`; // Asegúrate de incluir el ID
      return this.http.patch(url, data, { headers: this.getHeaders() });
    }

    getReservasRegalias(): Observable<any[]> {
      const url = `${this.apiUrl}reservaregalia/`; // Reemplaza con tu endpoint real
      return this.http.get<any[]>(url, { headers: this.getHeaders() });
    }

    cargarReservasRegaliasUsuario(idUsuario:number): Observable<any[]>{
      const url = `${this.apiUrl}reservaregalia/?cliente__id=${idUsuario}`
      return this.http.get<any[]>(url).pipe(
        catchError((error: HttpErrorResponse) => {
          console.error(`Error al obtener la reserva para el usuario ${idUsuario}:`, error);
          return throwError(() => new Error('No se pudieron cargar los datos.'));
        })
      );
    }
    cargarReservasRegaliasPorReserva(idReserva:number): Observable<any[]>{
      const url = `${this.apiUrl}reservaregalia/?reserva__id=${idReserva}`
      return this.http.get<any[]>(url).pipe(
        catchError((error: HttpErrorResponse) => {
          console.error(`Error al obtener los regalos de la reserva ${idReserva}:`, error);
          return throwError(() => new Error('No se pudieron cargar los datos.'));
        })
      );
    }

    obtenerRegaliaPorId(idRegalia: Regalia): Observable<Regalia> {
      const url = `${this.apiUrl}regalias/${idRegalia}/`;
      return this.http.get<Regalia>(url).pipe(
        catchError((error) => {
          console.error(`Error al obtener la regalia con ID ${idRegalia}:`, error);
          return throwError(() => new Error('Regalia no encontrada'));
        })
      );
    }


    getVideosPorReserva(reservaId: number): Observable<any> {
      const url = `${this.apiUrlVideo}reserva/${reservaId}/`; // URL para obtener los videos
      console.log(`Realizando petición a: ${url}`); // Verifica la URL usada en la petición
      return this.http.get<any>(url, { headers: this.getHeaders() }).pipe(
        catchError((error: HttpErrorResponse) => {
          console.error(`Error al obtener los videos para la reserva ${reservaId}:`, error);

          // Manejo de errores específicos basado en el código de estado HTTP
          if (error.status === 401) {
            return throwError(() => new Error('No estás autenticado. Por favor, inicia sesión nuevamente.'));
          }
          if (error.status === 403) {
            return throwError(() => new Error('No tienes permisos para acceder a estos videos.'));
          }
          if (error.status === 404) {
            return throwError(() => new Error('No se encontraron videos para esta reserva.'));
          }

          // Error genérico para otros códigos de estado
          return throwError(() => new Error('Ocurrió un error al cargar los videos. Inténtalo nuevamente más tarde.'));
        })
      );
    }


    getEstadoMembresia(): Observable<any> {
      return this.http.get(`${this.apiUrl}/usuarios/membresia/estado/`);
    }

    getTodasReservas(): Observable<any[]> {
      const url = `${this.apiUrl}/reservas/todas/`;
      return this.http.get<any[]>(url, { headers: this.getHeaders() }).pipe(
        catchError((error) => {
          console.error('Error al cargar todas las reservas:', error);
          return throwError(() => new Error('No se pudieron cargar las reservas.'));
        })
      );
    }





  // Servicio para subir video
  subirVideo(formData: FormData): Observable<any> {
    const token = this.getToken(); // Obtener el token desde el localStorage

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
    });

    return this.http.post(`${this.apiUrlVideo}subir/`, formData, { headers });
  }





    eliminarVideo(videoId: number): Observable<any> {
      const token = this.getToken(); // Obtener el token desde localStorage
      if (!token) {
        console.error('Token no encontrado');
        return throwError(() => new Error('No se encontró el token de autenticación.'));
      }

      const headers = new HttpHeaders({
        'Authorization': `Bearer ${token}` // Incluir el token en el encabezado
      });

      const url = `${this.apiUrlVideo}${videoId}/eliminar/`; // Endpoint para eliminar el video

      return this.http.delete<any>(url, { headers }).pipe(
        catchError((error: HttpErrorResponse) => {
          console.error(`Error al eliminar el video con ID ${videoId}:`, error);
          if (error.status === 401) {
            return throwError(() => new Error('No estás autenticado. Por favor, inicia sesión nuevamente.'));
          }
          if (error.status === 404) {
            return throwError(() => new Error('El video no existe.'));
          }
          return throwError(() => new Error('No se pudo eliminar el video.'));
        })
      );
    }





}
