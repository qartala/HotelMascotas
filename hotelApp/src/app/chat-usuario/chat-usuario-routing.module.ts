import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ChatUsuarioPage } from './chat-usuario.page';

const routes: Routes = [
  {
    path: '',
    component: ChatUsuarioPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ChatUsuarioPageRoutingModule {}
