import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SeguimientoUsuarioPage } from './seguimiento-usuario.page';

describe('SeguimientoUsuarioPage', () => {
  let component: SeguimientoUsuarioPage;
  let fixture: ComponentFixture<SeguimientoUsuarioPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(SeguimientoUsuarioPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
