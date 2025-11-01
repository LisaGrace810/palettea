import React from "react";

export const GesturesPanel: React.FC = () => {
  const handleUndo = () => { document.execCommand("undo"); };
  const handleRedo = () => { document.execCommand("redo"); };

  const handleZoomIn = () => {
    const canvas = document.querySelector("canvas")!;
    canvas.style.transform = `scale(1.2)`;
  };
  const handleZoomOut = () => {
    const canvas = document.querySelector("canvas")!;
    canvas.style.transform = `scale(0.8)`;
  };
  const handleRotate = () => {
    const canvas = document.querySelector("canvas")!;
    canvas.style.transform = `rotate(15deg)`;
  };

  const handleMove = (dx: number, dy: number) => {
    const canvas = document.querySelector("canvas")!;
    const transform = canvas.style.transform || "";
    canvas.style.transform = `${transform} translate(${dx}px, ${dy}px)`;
  };

  return (
    <div>
      <button onClick={handleUndo}>Undo</button>
      <button onClick={handleRedo}>Redo</button>
      <button onClick={handleZoomIn}>Zoom +</button>
      <button onClick={handleZoomOut}>Zoom -</button>
      <button onClick={handleRotate}>Rotate</button>
      <button onClick={() => handleMove(10, 0)}>Move Right</button>
      <button onClick={() => handleMove(-10, 0)}>Move Left</button>
      <button onClick={() => handleMove(0, 10)}>Move Down</button>
      <button onClick={() => handleMove(0, -10)}>Move Up</button>
    </div>
  );
};
