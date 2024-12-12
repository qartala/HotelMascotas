import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { MembresiaVideoPage } from './membresia-video.page';

const routes: Routes = [
  {
    path: '',
    component: MembresiaVideoPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class MembresiaVideoPageRoutingModule {}
