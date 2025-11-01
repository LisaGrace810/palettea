export interface ProcreateBrush {
  tip: HTMLCanvasElement;
  size: number;
  spacing: number;
  streamline: number;
  scatter: number;
  rotation: number;
  opacity: number;
  flow: number;
  blendMode: GlobalCompositeOperation;
  pressureSize: boolean;
  pressureOpacity: boolean;
  tiltSize: boolean;
  tiltOpacity: boolean;
  dynamics?: { speed?: number; rotation?: number };
  grain?: { texture?: HTMLCanvasElement; scale?: number; rotation?: number };
  symmetry?: { horizontal?: boolean; vertical?: boolean; both?: boolean };
}
