let mediaRecorder: MediaRecorder;
let recordedChunks: BlobPart[] = [];

export function startRecording(canvas: HTMLCanvasElement) {
  const stream = canvas.captureStream(60);
  mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm;codecs=vp9" });
  recordedChunks = [];
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.start();
}

export function stopRecording() {
  return new Promise<Blob>(resolve => {
    mediaRecorder.onstop = () => resolve(new Blob(recordedChunks, { type: "video/webm" }));
    mediaRecorder.stop();
  });
}
