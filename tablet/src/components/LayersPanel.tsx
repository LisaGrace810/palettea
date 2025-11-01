import React from "react";

interface Layer {
  id: number;
  name: string;
  visible: boolean;
  locked: boolean;
}

interface LayersPanelProps {
  layers: Layer[];
  activeLayer: number | null;
  setActiveLayer: (id: number) => void;
  addLayer: () => void;
  deleteLayer: (id: number) => void;
  toggleVisibility: (id: number) => void;
  toggleLock: (id: number) => void;
}

export const LayersPanel: React.FC<LayersPanelProps> = ({ layers, activeLayer, setActiveLayer, addLayer, deleteLayer, toggleVisibility, toggleLock }) => {
  return (
    <div>
      <button onClick={addLayer}>+ Add Layer</button>
      {layers.map(layer => (
        <div key={layer.id} style={{ display: "flex", alignItems: "center", marginTop: 4, background: activeLayer === layer.id ? "#555" : "transparent", padding: 4, borderRadius: 4 }}>
          <span style={{ flex: 1, cursor: "pointer" }} onClick={() => setActiveLayer(layer.id)}>{layer.name}</span>
          <button onClick={() => toggleVisibility(layer.id)}>{layer.visible ? "👁️" : "🚫"}</button>
          <button onClick={() => toggleLock(layer.id)}>{layer.locked ? "🔒" : "🔓"}</button>
          <button onClick={() => deleteLayer(layer.id)}>🗑️</button>
        </div>
      ))}
    </div>
  );
};
