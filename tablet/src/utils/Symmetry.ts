import { ProcreateBrush } from "../brushes/ProcreateBrush";

export function applySymmetry(x: number, y: number, brush: ProcreateBrush, canvasWidth: number, canvasHeight: number) {
  const points = [{ x, y }];
  if (brush.symmetry?.horizontal) points.push({ x: canvasWidth - x, y });
  if (brush.symmetry?.vertical) points.push({ x, y: canvasHeight - y });
  if (brush.symmetry?.both) points.push({ x: canvasWidth - x, y: canvasHeight - y });
  return points;
}
