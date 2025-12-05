import React from 'react'
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material'

export default function LangSelector() {
  const [lang, setLang] = React.useState(localStorage.getItem('lang') || 'en')

  React.useEffect(() => localStorage.setItem('lang', lang), [lang])

  return (
    <FormControl sx={{ minWidth: 180, mb: 2 }}>
      <InputLabel id='lang-label'>Language</InputLabel>
      <Select
        labelId='lang-label'
        value={lang}
        label='Language'
        onChange={(e) => setLang(e.target.value)}
      >
        <MenuItem value='en'>English</MenuItem>
        <MenuItem value='multi'>Multilingual (xlsr)</MenuItem>
      </Select>
    </FormControl>
  )
}
