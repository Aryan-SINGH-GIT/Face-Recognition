import { useRef, useState, useCallback, useEffect } from 'react';

/**
 * useWebcam – Robust shared hook for browser camera capture.
 * Handles mounting lifecycles, stream cleanup, autoPlay, and detailed error messages.
 */
export default function useWebcam(autoStart = false) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [stream, setStream] = useState(null);
  const [streaming, setStreaming] = useState(false);
  const [capturedBlob, setCapturedBlob] = useState(null);
  const [preview, setPreview] = useState(null);
  const [cameraError, setCameraError] = useState('');

  // Attach stream to video element whenever both are available
  useEffect(() => {
    const video = videoRef.current;
    if (video && stream) {
      video.srcObject = stream;
      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          console.warn('[useWebcam] video.play() warning:', err);
        });
      }
    }
  }, [stream, streaming]);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setStream(null);
    setStreaming(false);
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  const startCamera = useCallback(async () => {
    setCameraError('');
    setCapturedBlob(null);
    setPreview(null);

    if (!navigator?.mediaDevices?.getUserMedia) {
      setCameraError('Webcam access is not supported by your browser or connection is not secure (requires localhost or HTTPS).');
      return;
    }

    try {
      // First attempt with ideal resolution
      let mediaStream;
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user',
          },
          audio: false,
        });
      } catch (err) {
        // Fallback to basic video constraint if ideal fails
        console.warn('[useWebcam] Ideal constraints failed, falling back to simple video:', err);
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      }

      streamRef.current = mediaStream;
      setStream(mediaStream);
      setStreaming(true);

      // Also directly assign if ref already mounted
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play().catch(() => {});
      }
    } catch (err) {
      console.error('[useWebcam] getUserMedia error:', err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setCameraError('Camera permission was denied. Please click the camera icon in your browser address bar and choose "Allow".');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setCameraError('No webcam was detected on this device. You can use the "Upload Photo" tab instead.');
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setCameraError('Camera is already in use by another application. Please close other camera apps and retry.');
      } else {
        setCameraError(`Camera error: ${err.message || err.name || 'Unknown error'}`);
      }
      setStreaming(false);
    }
  }, []);

  const capture = useCallback(() => {
    return new Promise((resolve) => {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      if (!canvas || !video || video.readyState < 2 || !video.videoWidth) {
        console.warn('[useWebcam] Video not ready for frame capture');
        resolve(null);
        return;
      }

      const width = video.videoWidth || 640;
      const height = video.videoHeight || 480;

      canvas.width = width;
      canvas.height = height;

      const ctx = canvas.getContext('2d');
      // Mirror image horizontally to match webcam display
      ctx.translate(width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0, width, height);

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            resolve(null);
            return;
          }
          const file = new File([blob], 'face_capture.jpg', { type: 'image/jpeg' });
          const url = URL.createObjectURL(blob);
          setCapturedBlob(file);
          setPreview(url);
          stopCamera();
          resolve(file);
        },
        'image/jpeg',
        0.95
      );
    });
  }, [stopCamera]);

  const reset = useCallback(() => {
    stopCamera();
    setCapturedBlob(null);
    setPreview(null);
    setCameraError('');
  }, [stopCamera]);

  // Clean up stream on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Auto start if requested
  useEffect(() => {
    if (autoStart) {
      startCamera();
    }
  }, [autoStart, startCamera]);

  return {
    videoRef,
    canvasRef,
    stream,
    streaming,
    capturedBlob,
    preview,
    cameraError,
    startCamera,
    stopCamera,
    capture,
    reset,
  };
}
