import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { SeguimientoUsuarioPage } from './seguimiento-usuario.page';

const routes: Routes = [
  {
    path: '',
    component: SeguimientoUsuarioPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class SeguimientoUsuarioPageRoutingModule {}
