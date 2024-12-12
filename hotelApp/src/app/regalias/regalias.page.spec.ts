import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RegaliasPage } from './regalias.page';

describe('RegaliasPage', () => {
  let component: RegaliasPage;
  let fixture: ComponentFixture<RegaliasPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(RegaliasPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
