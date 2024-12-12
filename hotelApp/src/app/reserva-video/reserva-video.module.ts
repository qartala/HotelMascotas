import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ReservaVideoPageRoutingModule } from './reserva-video-routing.module';

import { ReservaVideoPage } from './reserva-video.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ReservaVideoPageRoutingModule
  ],
  declarations: [ReservaVideoPage]
})
export class ReservaVideoPageModule {}
