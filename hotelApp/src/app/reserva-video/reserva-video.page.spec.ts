import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReservaVideoPage } from './reserva-video.page';

describe('ReservaVideoPage', () => {
  let component: ReservaVideoPage;
  let fixture: ComponentFixture<ReservaVideoPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(ReservaVideoPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
