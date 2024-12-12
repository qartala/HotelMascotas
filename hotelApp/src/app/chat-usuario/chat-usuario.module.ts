import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ChatUsuarioPageRoutingModule } from './chat-usuario-routing.module';

import { ChatUsuarioPage } from './chat-usuario.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ChatUsuarioPageRoutingModule
  ],
  declarations: [ChatUsuarioPage]
})
export class ChatUsuarioPageModule {}
