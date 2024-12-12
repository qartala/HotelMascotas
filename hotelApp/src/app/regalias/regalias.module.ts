import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { RegaliasPageRoutingModule } from './regalias-routing.module';

import { RegaliasPage } from './regalias.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    RegaliasPageRoutingModule
  ],
  declarations: [RegaliasPage]
})
export class RegaliasPageModule {}
