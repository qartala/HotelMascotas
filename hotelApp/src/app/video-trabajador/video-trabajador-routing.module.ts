import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { VideoTrabajadorPage } from './video-trabajador.page';

const routes: Routes = [
  {
    path: '',
    component: VideoTrabajadorPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class VideoTrabajadorPageRoutingModule {}
