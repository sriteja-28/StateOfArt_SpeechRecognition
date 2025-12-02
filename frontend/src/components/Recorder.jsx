import React, { useState, useRef, useEffect } from 'react'
import { Button, Stack, Typography } from '@mui/material'
import WaveSurfer from 'wavesurfer.js'

export default function Recorder() {
  const [status, setStatus] = useState('closed')
  const [conn, setConn] = useState('disconnected')
  const [text, setText] = useState('')
  const [audioUrl, setAudioUrl] = useState(null)

  const mediaRef = useRef(null)
  const wsRef = useRef(null)
  const streamRef = useRef(null)
  const chunksRef = useRef([])
  const waveRef = useRef(null)
  const canvasRef = useRef(null)
  const audioCtxRef = useRef(null)
  const analyserRef = useRef(null)
  const animationRef = useRef(null)

  // initialize waveform container
  useEffect(() => {
    waveRef.current = WaveSurfer.create({
      container: '#waveform',
      waveColor: 'violet',
      progressColor: 'purple',
      height: 80
    })

    const canvas = document.createElement('canvas')
    canvas.style.width = '100%'
    canvas.style.height = '80px'
    const container = document.getElementById('waveform')
    if (container) container.appendChild(canvas)
    canvasRef.current = canvas
  }, [])

  // websocket connection
  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/stream/')
    wsRef.current.onopen = () => setConn('connected')
    wsRef.current.onclose = () => setConn('disconnected')
    wsRef.current.onerror = () => setConn('error')
    wsRef.current.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.text) setText(prev => prev + " " + data.text)
      } catch {}
    }
    return () => wsRef.current?.close()
  }, [])

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    streamRef.current = stream
    const mr = new MediaRecorder(stream)
    mediaRef.current = mr
    chunksRef.current = []
    setText('')
    setAudioUrl(null)

    // setup Web Audio API for waveform
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    audioCtxRef.current = audioCtx
    const source = audioCtx.createMediaStreamSource(stream)
    const analyser = audioCtx.createAnalyser()
    analyser.fftSize = 2048
    source.connect(analyser)
    analyserRef.current = analyser

    const canvas = canvasRef.current
    const canvasCtx = canvas.getContext('2d')
    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)

    const draw = () => {
      animationRef.current = requestAnimationFrame(draw)
      analyser.getByteTimeDomainData(dataArray)
      canvasCtx.fillStyle = '#fff'
      canvasCtx.fillRect(0, 0, canvas.width, canvas.height)
      canvasCtx.lineWidth = 2
      canvasCtx.strokeStyle = 'purple'
      canvasCtx.beginPath()
      let x = 0
      const sliceWidth = canvas.width / bufferLength
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128
        const y = (v * canvas.height) / 2
        if (i === 0) canvasCtx.moveTo(x, y)
        else canvasCtx.lineTo(x, y)
        x += sliceWidth
      }
      canvasCtx.stroke()
    }

    const resize = () => {
      if (!canvas) return
      canvas.width = canvas.clientWidth * devicePixelRatio
      canvas.height = canvas.clientHeight * devicePixelRatio
    }
    resize()
    window.addEventListener('resize', resize)
    draw()

    mr.ondataavailable = (e) => {
      if (e.data.size === 0) return
      chunksRef.current.push(e.data)

      if (wsRef.current && wsRef.current.readyState === 1) {
        e.data.arrayBuffer().then(buf => wsRef.current.send(buf))
      }
    }

    mr.start(250)
    setStatus('live')
  }

  const stop = () => {
    if (wsRef.current?.readyState === 1) wsRef.current.send("FLUSH")
    mediaRef.current?.stop()
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
    setStatus('closed')

    // create final audio blob
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
    const url = URL.createObjectURL(blob)
    setAudioUrl(url)
    waveRef.current.loadBlob(blob)

    // cleanup audio context
    if (animationRef.current) cancelAnimationFrame(animationRef.current)
    analyserRef.current?.disconnect()
    audioCtxRef.current?.close()
  }

  const clear = () => {
    setText('')
    setAudioUrl(null)
    waveRef.current.empty()
  }

  return (
    <Stack spacing={2} alignItems='flex-start'>
      <Typography variant='h6'>Live Speech Input</Typography>
      <div id='waveform'></div>

      <Stack direction='row' spacing={1}>
        <Button variant='contained' onClick={start} disabled={status === 'live'}>Start</Button>
        <Button variant='outlined' onClick={stop} disabled={status !== 'live'}>Stop</Button>
        <Button color='error' onClick={clear}>Clear</Button>
      </Stack>

      <Typography variant='body1' sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>{text}</Typography>

      {audioUrl && (
        <audio controls src={audioUrl} style={{ marginTop: '10px', width: '100%' }} />
      )}

      <Typography variant='body2' sx={{ color: conn === 'connected' ? 'green' : 'gray' }}>
        websocket: {conn} | mic: {status}
      </Typography>
    </Stack>
  )
}
