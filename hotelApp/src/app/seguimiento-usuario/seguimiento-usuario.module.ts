import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { SeguimientoUsuarioPageRoutingModule } from './seguimiento-usuario-routing.module';

import { SeguimientoUsuarioPage } from './seguimiento-usuario.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    SeguimientoUsuarioPageRoutingModule
  ],
  declarations: [SeguimientoUsuarioPage]
})
export class SeguimientoUsuarioPageModule {}
