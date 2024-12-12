import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { MembresiaVideoPageRoutingModule } from './membresia-video-routing.module';

import { MembresiaVideoPage } from './membresia-video.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    MembresiaVideoPageRoutingModule
  ],
  declarations: [MembresiaVideoPage]
})
export class MembresiaVideoPageModule {}
