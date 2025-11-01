import React, { useState } from "react";
import { ProcreateBrush } from "../brushes/ProcreateBrush";

interface ColorPickerPanelProps {
  brush: ProcreateBrush;
  setBrush: React.Dispatch<React.SetStateAction<ProcreateBrush>>;
}

export const ColorPickerPanel: React.FC<ColorPickerPanelProps> = ({ brush, setBrush }) => {
  const [color, setColor] = useState("#ff0000");

  const handleColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setColor(e.target.value);
    if (brush.tip) {
      const ctx = brush.tip.getContext("2d")!;
      ctx.clearRect(0, 0, brush.tip.width, brush.tip.height);
      ctx.fillStyle = e.target.value;
      ctx.beginPath();
      ctx.arc(brush.tip.width / 2, brush.tip.height / 2, brush.tip.width / 2, 0, Math.PI * 2);
      ctx.fill();
    }
  };

  return (
    <div>
      <input type="color" value={color} onChange={handleColorChange} />
      <label>Hex: <input type="text" value={color} onChange={handleColorChange} /></label>
    </div>
  );
};
