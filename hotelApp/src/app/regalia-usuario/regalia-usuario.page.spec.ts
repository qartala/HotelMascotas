import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RegaliaUsuarioPage } from './regalia-usuario.page';

describe('RegaliaUsuarioPage', () => {
  let component: RegaliaUsuarioPage;
  let fixture: ComponentFixture<RegaliaUsuarioPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(RegaliaUsuarioPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
