import React from 'react'
import { Container, Box, Typography } from '@mui/material'
import FileUpload from './components/FileUpload'

export default function App() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundImage: `url('../src/images/image.png')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        filter: 'brightness(0.78)',
        opacity: 0.9,
      }}
    >

      <Container sx={{ mt: 4 }}>
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
        >
          <Typography variant='h4' gutterBottom color="white">
            Speech Recognition App
          </Typography>
          {/* <LangSelector />
          <Recorder />
          <Divider sx={{my:4}} /> */}
          <FileUpload />
        </Box>
      </Container>

      <Box
        component="footer"
        sx={{
          py: 2,
          textAlign: 'center',
          backgroundColor: 'rgba(0,0,0,0.5)',
          color: 'white',
        }}
      >
        © {new Date().getFullYear()} Designed & Developed by Sri Teja Muthangi. All rights reserved.
      </Box>
    </Box>
  )
}


