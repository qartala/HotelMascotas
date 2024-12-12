import { ComponentFixture, TestBed } from '@angular/core/testing';
import { VideoTrabajadorPage } from './video-trabajador.page';

describe('VideoTrabajadorPage', () => {
  let component: VideoTrabajadorPage;
  let fixture: ComponentFixture<VideoTrabajadorPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(VideoTrabajadorPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
