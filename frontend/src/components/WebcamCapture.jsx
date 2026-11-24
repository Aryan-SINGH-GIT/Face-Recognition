import { useState, useRef, useEffect } from 'react';
import { Camera, RefreshCw, AlertCircle, Loader2 } from 'lucide-react';
import useWebcam from '../hooks/useWebcam';

export default function WebcamCapture({
  onCapture,
  onReset,
  label = 'Scan Face',
  autoStart = true,
}) {
  const {
    videoRef,
    canvasRef,
    streaming,
    preview,
    cameraError,
    startCamera,
    capture,
    reset,
  } = useWebcam(autoStart);

  const [videoLoaded, setVideoLoaded] = useState(false);

  // Reset video loaded flag when stream changes or resets
  useEffect(() => {
    if (!streaming) {
      setVideoLoaded(false);
    }
  }, [streaming]);

  const handleCapture = async () => {
    if (!videoLoaded && streaming) return;
    const file = await capture();
    if (file && onCapture) {
      onCapture(file);
    }
  };

  const handleReset = () => {
    setVideoLoaded(false);
    reset();
    if (onReset) onReset();
    setTimeout(() => startCamera(), 150);
  };

  return (
    <div className="webcam-box">
      <canvas ref={canvasRef} hidden />

      {/* Live Video Viewport */}
      {streaming && (
        <div className="viewport">
          <video
            ref={videoRef}
            className={`video-feed ${videoLoaded ? 'loaded' : 'loading'}`}
            autoPlay
            playsInline
            muted
            onLoadedData={() => setVideoLoaded(true)}
            onPlaying={() => setVideoLoaded(true)}
          />

          {!videoLoaded && (
            <div className="viewport-overlay">
              <Loader2 size={32} className="spin text-primary" />
              <p>Connecting to camera feed...</p>
            </div>
          )}

          {videoLoaded && (
            <div className="scan-reticle">
              <div className="reticle-frame" />
            </div>
          )}
        </div>
      )}

      {/* Captured Snapshot View */}
      {!streaming && preview && (
        <div className="viewport">
          <img src={preview} alt="Captured face" className="video-feed" />
        </div>
      )}

      {/* Camera Off / Idle State */}
      {!streaming && !preview && (
        <div className="viewport-idle">
          <Camera size={32} className="text-muted" />
          <p>Camera is in standby</p>
          <button type="button" className="btn btn-sm btn-subtle" onClick={startCamera}>
            Enable Camera
          </button>
        </div>
      )}

      {/* Error Banner */}
      {cameraError && (
        <div className="alert alert-error">
          <AlertCircle size={15} />
          <span>{cameraError}</span>
        </div>
      )}

      {/* Action Controls */}
      <div className="webcam-actions">
        {streaming && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleCapture}
            disabled={!videoLoaded}
          >
            <Camera size={15} />
            <span>{videoLoaded ? label : 'Starting Camera...'}</span>
          </button>
        )}

        {(streaming || preview) && (
          <button type="button" className="btn btn-subtle btn-sm" onClick={handleReset}>
            <RefreshCw size={13} />
            <span>Retake</span>
          </button>
        )}
      </div>
    </div>
  );
}
