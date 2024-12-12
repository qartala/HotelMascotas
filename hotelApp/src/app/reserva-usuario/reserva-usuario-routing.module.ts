import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ReservaUsuarioPage } from './reserva-usuario.page';

const routes: Routes = [
  {
    path: '',
    component: ReservaUsuarioPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ReservaUsuarioPageRoutingModule {}
