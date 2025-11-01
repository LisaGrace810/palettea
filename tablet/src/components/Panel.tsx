import React, { useRef, useState } from "react";

interface PanelProps {
  title: string;
  width?: number;
  height?: number;
  initialX?: number;
  initialY?: number;
  children: React.ReactNode;
}

export const Panel: React.FC<PanelProps> = ({ title, width = 300, height = 400, initialX = 50, initialY = 50, children }) => {
  const panelRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: initialX, y: initialY });
  const [dragging, setDragging] = useState(false);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const onPointerDown = (e: React.PointerEvent) => {
    setDragging(true);
    setOffset({ x: e.clientX - pos.x, y: e.clientY - pos.y });
  };
  const onPointerMove = (e: React.PointerEvent) => {
    if (!dragging) return;
    setPos({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };
  const onPointerUp = () => setDragging(false);

  return (
    <div
      ref={panelRef}
      style={{ position: "absolute", top: pos.y, left: pos.x, width, height, zIndex: 1000, background: "#222", color: "#fff", borderRadius: 6 }}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerLeave={onPointerUp}
    >
      <div style={{ cursor: "grab", padding: 6, fontWeight: "bold" }} onPointerDown={onPointerDown}>{title}</div>
      <div style={{ padding: 6, height: height - 30, overflow: "auto" }}>{children}</div>
    </div>
  );
};
