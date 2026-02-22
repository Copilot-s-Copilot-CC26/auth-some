'use client'

import { useRef, useState } from 'react'

const FiveSecondRecorder = ({ setter }: { setter: (arg0: string) => void }) => {
  const [recording, setRecording] = useState(false)
  const [audioURL, setAudioURL] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        const url = URL.createObjectURL(blob)
        setAudioURL(url)
        setter(url)
        console.log(url)

        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setRecording(true)

      setTimeout(() => {
        mediaRecorder.stop()
        setRecording(false)
      }, 5000)

    } catch (err) {
      console.error('Microphone permission denied or error:', err)
    }
  }

  return (
    <div className="flex flex-col gap-4 items-start">
      <button
        type="button"
        onClick={startRecording}
        disabled={recording}
        className="px-4 py-2 bg-black text-white rounded"
      >
        {recording ? 'Recording...' : 'Record 5 Seconds'}
      </button>

      {audioURL && (
        <audio controls src={audioURL} />
      )}
    </div>
  )
}

export default FiveSecondRecorder;