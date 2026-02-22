"use client"

import { useEffect, useRef, useState } from "react"

export default function WebcamCapture() {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  const [image, setImage] = useState<string | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    startCamera()

    return () => {
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
      })

      setStream(mediaStream)

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      setError("Could not access webcam.")
    }
  }

  const stopCamera = () => {
    stream?.getTracks().forEach((track) => track.stop())
  }

  const takePhoto = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return

    const context = canvas.getContext("2d")
    if (!context) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    context.drawImage(video, 0, 0)

    const dataUrl = canvas.toDataURL("image/png")
    setImage(dataUrl)
  }

  return (
    <div className="space-y-4">
      {error && <p className="text-red-500">{error}</p>}

      <div className="relative w-full max-w-md">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="rounded border w-full"
        />
      </div>

      <button
        onClick={takePhoto}
        type="button"
        className="px-4 py-2 bg-black text-white rounded"
      >
        Take Photo
      </button>

      <canvas ref={canvasRef} className="hidden" />

      {image && (
        <div className="space-y-2">
          <p className="font-semibold">Preview:</p>
          <img src={image} alt="Captured" className="rounded border" />
        </div>
      )}
    </div>
  )
}