import { ProcreateBrush } from "./ProcreateBrush";

export class BrushEngine {
  ctx: CanvasRenderingContext2D;

  constructor(ctx: CanvasRenderingContext2D) {
    this.ctx = ctx;
  }

  drawStroke(points: any[], brush: ProcreateBrush) {
    points.forEach((p: any) => {
      const { x, y, pressure } = p;
      let size = brush.size * (brush.pressureSize ? pressure : 1);
      let opacity = brush.opacity * (brush.pressureOpacity ? pressure : 1);

      const positions = [{ x, y }];
      if (brush.symmetry?.horizontal) positions.push({ x: this.ctx.canvas.width - x, y });
      if (brush.symmetry?.vertical) positions.push({ x, y: this.ctx.canvas.height - y });
      if (brush.symmetry?.both) positions.push({ x: this.ctx.canvas.width - x, y: this.ctx.canvas.height - y });

      positions.forEach(pos => {
        this.ctx.save();
        this.ctx.globalAlpha = opacity;
        this.ctx.globalCompositeOperation = brush.blendMode;
        this.ctx.translate(pos.x, pos.y);
        this.ctx.rotate(brush.rotation);
        this.ctx.drawImage(brush.tip, -size / 2, -size / 2, size, size);
        this.ctx.restore();
      });
    });
  }
}
