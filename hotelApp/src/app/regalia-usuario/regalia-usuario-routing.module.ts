import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { RegaliaUsuarioPage } from './regalia-usuario.page';

const routes: Routes = [
  {
    path: '',
    component: RegaliaUsuarioPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class RegaliaUsuarioPageRoutingModule {}
