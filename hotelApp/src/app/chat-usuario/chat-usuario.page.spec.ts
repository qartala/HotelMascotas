import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChatUsuarioPage } from './chat-usuario.page';

describe('ChatUsuarioPage', () => {
  let component: ChatUsuarioPage;
  let fixture: ComponentFixture<ChatUsuarioPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(ChatUsuarioPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
