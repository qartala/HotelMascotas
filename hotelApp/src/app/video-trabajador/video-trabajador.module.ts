import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { VideoTrabajadorPageRoutingModule } from './video-trabajador-routing.module';

import { VideoTrabajadorPage } from './video-trabajador.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    VideoTrabajadorPageRoutingModule
  ],
  declarations: [VideoTrabajadorPage]
})
export class VideoTrabajadorPageModule {}
