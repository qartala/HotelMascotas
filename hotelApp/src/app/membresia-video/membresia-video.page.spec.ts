import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MembresiaVideoPage } from './membresia-video.page';

describe('MembresiaVideoPage', () => {
  let component: MembresiaVideoPage;
  let fixture: ComponentFixture<MembresiaVideoPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(MembresiaVideoPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
