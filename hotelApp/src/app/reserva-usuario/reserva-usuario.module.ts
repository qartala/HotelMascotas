import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ReservaUsuarioPageRoutingModule } from './reserva-usuario-routing.module';

import { ReservaUsuarioPage } from './reserva-usuario.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ReservaUsuarioPageRoutingModule
  ],
  declarations: [ReservaUsuarioPage]
})
export class ReservaUsuarioPageModule {}
