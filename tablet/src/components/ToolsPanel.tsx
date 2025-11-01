import React, { useState } from "react";
import { ProcreateBrush } from "../brushes/ProcreateBrush";
import { startRecording, stopRecording } from "../utils/ScreenRecorder";

interface ToolsPanelProps {
  brush: ProcreateBrush;
  setBrush: React.Dispatch<React.SetStateAction<ProcreateBrush>>;
}

export const ToolsPanel: React.FC<ToolsPanelProps> = ({ brush, setBrush }) => {
  const [recording, setRecording] = useState(false);

  const handleStartRecording = () => {
    const canvas = document.querySelector("canvas") as HTMLCanvasElement;
    if (!canvas) return;
    startRecording(canvas);
    setRecording(true);
  };

  const handleStopRecording = async () => {
    const videoBlob = await stopRecording();
    const url = URL.createObjectURL(videoBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "recording.webm";
    a.click();
    setRecording(false);
  };

  return (
    <div>
      <label>
        Size: <input type="range" min={1} max={100} value={brush.size} onChange={e => setBrush({ ...brush, size: Number(e.target.value) })} />
      </label>
      <label>
        Opacity: <input type="range" min={0} max={1} step={0.01} value={brush.opacity} onChange={e => setBrush({ ...brush, opacity: Number(e.target.value) })} />
      </label>
      <label>
        Flow: <input type="range" min={0} max={1} step={0.01} value={brush.flow} onChange={e => setBrush({ ...brush, flow: Number(e.target.value) })} />
      </label>

      <div>
        <label>
          <input type="checkbox" checked={brush.symmetry?.horizontal} onChange={e => setBrush({ ...brush, symmetry: { ...brush.symmetry, horizontal: e.target.checked } })} />
          Horizontal Symmetry
        </label>
        <label>
          <input type="checkbox" checked={brush.symmetry?.vertical} onChange={e => setBrush({ ...brush, symmetry: { ...brush.symmetry, vertical: e.target.checked } })} />
          Vertical Symmetry
        </label>
        <label>
          <input type="checkbox" checked={brush.symmetry?.both} onChange={e => setBrush({ ...brush, symmetry: { ...brush.symmetry, both: e.target.checked } })} />
          Mirror Symmetry
        </label>
      </div>

      <div>
        {!recording ? (
          <button onClick={handleStartRecording}>Start Recording</button>
        ) : (
          <button onClick={handleStopRecording}>Stop Recording</button>
        )}
      </div>
    </div>
  );
};
