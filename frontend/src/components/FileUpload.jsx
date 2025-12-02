import React, { useState } from 'react';
import { Button, Typography, Stack, Box, FormControl, Select, MenuItem } from '@mui/material';

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [usedModel, setUsedModel] = useState('');
  const [model, setModel] = useState("wav2vec2-base");

  const audioUrl = file ? URL.createObjectURL(file) : null;

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setText('');
    setProgress(0);
  };

  const transcribe = async () => {
    if (!file) return;
    setLoading(true);
    setProgress(10);

    const fd = new FormData();
    fd.append('file', file);
    const lang = localStorage.getItem('lang') || 'en';

    try {
      const timer = setInterval(() => {
        setProgress((old) => (old < 90 ? old + 10 : old));
      }, 500);

      const res = await fetch(
        `http://localhost:8000/transcribe/?lang=${lang}&model=${model}`,
        { method: "POST", body: fd }
      );

      clearInterval(timer);
      setProgress(100);

      const j = await res.json();
      setText(j.text || '(no transcription returned)');
      setUsedModel(j.model || '');
    } catch (err) {
      console.error(err);
      setText('Error during transcription.');
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const clear = () => {
    setFile(null);
    setText('');
    setProgress(0);
    setLoading(false);
    setModel("wav2vec2-base");
    setUsedModel('');
  };

  return (
    <Stack spacing={3} alignItems='center' sx={{ width: '100%', mt: 4 }}>
      <Button variant='contained' component='label'>
        Choose Audio File
        <input hidden type='file' accept='audio/*' onChange={handleFileSelect} />
      </Button>

      {file && (
        <Stack spacing={1} alignItems='center' sx={{ p: 1, borderRadius: 1 }}>
          <Typography variant='body2' color='#fff'>
            Selected: {file.name}
          </Typography>
          <audio controls src={audioUrl} style={{ width: '80%', borderRadius: 4 }} />
        </Stack>
      )}

      <Box display="flex" alignItems="center" gap={2} flexWrap="wrap" width="100%" justifyContent="center">
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant='h6' sx={{ color: '#fff', whiteSpace: 'nowrap' }}>
            Choose Model:
          </Typography>
          <FormControl sx={{ minWidth: 200, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
            <Select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              size='small'
              sx={{ color: '#fff' }}
            >
              <MenuItem value="wav2vec2-small">wav2vec2-small (English only)</MenuItem>
              <MenuItem value="wav2vec2-base">wav2vec2-base (English only)</MenuItem>
              <MenuItem value="wav2vec2-large">wav2vec2-large (English only)</MenuItem>
              <MenuItem value="whisper-base">whisper-base (Multilingual, basic support)</MenuItem>
              <MenuItem value="whisper-small">whisper-small (Multilingual, better support)</MenuItem>
              <MenuItem value="xlsr-53-large">xlsr-53-large (Multilingual, ~53 languages)</MenuItem>

            </Select>
          </FormControl>
        </Box>

        <Button
          variant='contained'
          onClick={transcribe}
          disabled={!file || loading}
          sx={{
            color: '#fff',
            backgroundColor: 'rgba(0,0,0,0.7)',
            '&:hover': { backgroundColor: 'rgba(0,0,0,0.85)' },
          }}
        >
          {loading ? (
            <span style={{ color: '#fff', fontWeight: 'bold' }}>
              Transcribing... {progress}%
            </span>
          ) : 'Transcribe'}
        </Button>


        <Button
          onClick={clear}
          disabled={loading}
          sx={{
            color: '#fff',
            backgroundColor: 'rgba(255,0,0,0.8)',
            '&:hover': {
              backgroundColor: 'rgba(255,0,0,1)',
            },
          }}
        >
          Clear
        </Button>

      </Box>

      {text && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            borderRadius: 2,
            backgroundColor: 'rgba(0,0,0,0.6)',
            maxWidth: '90%',
            width: 'fit-content',
            textAlign: 'center'
          }}
        >
          <Typography variant='subtitle1' sx={{ color: '#fff', fontWeight: 'bold', mb: 1 }}>
            Transcribed Text:
          </Typography>
          <Typography variant='body1' sx={{ color: '#fff', whiteSpace: 'pre-wrap' }}>
            {text}
          </Typography>
        </Box>
      )}


      {usedModel && (
        <Typography variant='body2' color='#fff'>
          Model used: {usedModel}
        </Typography>
      )}
    </Stack>
  );
}
