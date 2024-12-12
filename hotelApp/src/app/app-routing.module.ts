import { NgModule } from '@angular/core';
import { PreloadAllModules, RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './auth.guard';

const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'home',
    loadChildren: () => import('./home/home.module').then(m => m.HomePageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'login',
    loadChildren: () => import('./login/login.module').then(m => m.LoginPageModule)
  },
  {
    path: 'reservas',
    loadChildren: () => import('./reservas/reservas.module').then(m => m.ReservasPageModule)
  },
  {
    path: 'regalias',
    loadChildren: () => import('./regalias/regalias.module').then(m => m.RegaliasPageModule)
  },
  {
    path: 'seguimiento/:id',
    loadChildren: () => import('./seguimiento/seguimiento.module').then(m => m.SeguimientoPageModule)
  },
  {
    path: 'perfil',
    loadChildren: () => import('./perfil/perfil.module').then( m => m.PerfilPageModule)
  },
  {
    path: 'reserva-usuario',
    loadChildren: () => import('./reserva-usuario/reserva-usuario.module').then( m => m.ReservaUsuarioPageModule)
  },
  {
    path: 'seguimiento-usuario/:reservaId',
    loadChildren: () => import('./seguimiento-usuario/seguimiento-usuario.module').then( m => m.SeguimientoUsuarioPageModule)
  },
  {
    path: 'chat-usuario/:id',
    loadChildren: () =>
      import('./chat-usuario/chat-usuario.module').then(
        (m) => m.ChatUsuarioPageModule
      ),
  },
  {
    path: 'regalia-usuario',
    loadChildren: () => import('./regalia-usuario/regalia-usuario.module').then( m => m.RegaliaUsuarioPageModule)
  },
  {
    path: 'membresia-video/:reservaId/:fichaId',
    loadChildren: () => import('./membresia-video/membresia-video.module').then(m => m.MembresiaVideoPageModule)
  },
  {
    path: 'reserva-video',
    loadChildren: () =>
      import('./reserva-video/reserva-video.module').then( (m) => m.ReservaVideoPageModule)
  },
  {
    path: 'video-trabajador/:reservaId',
    loadChildren: () =>
      import('./video-trabajador/video-trabajador.module').then(
        (m) => m.VideoTrabajadorPageModule
      ),
  },



];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
