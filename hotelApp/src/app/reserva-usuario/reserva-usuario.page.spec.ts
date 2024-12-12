import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReservaUsuarioPage } from './reserva-usuario.page';

describe('ReservaUsuarioPage', () => {
  let component: ReservaUsuarioPage;
  let fixture: ComponentFixture<ReservaUsuarioPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(ReservaUsuarioPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
