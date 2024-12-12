import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { RegaliasPage } from './regalias.page';

const routes: Routes = [
  {
    path: '',
    component: RegaliasPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class RegaliasPageRoutingModule {}
