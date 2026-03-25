import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ResultsDisplay from './components/ResultsDisplay'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [format, setFormat] = useState('json')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [downloadUrl, setDownloadUrl] = useState(null)

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile)
    setResult(null)
    setError(null)
    setDownloadUrl(null)
  }

  const handleFormatChange = (e) => {
    setFormat(e.target.value)
  }

  const handleSubmit = async () => {
    if (!file) return

    setLoading(true)
    setError(null)
    setResult(null)
    setDownloadUrl(null)

    const formData = new FormData()
    formData.append('document', file)

    try {
      const url = format !== 'json'
        ? `/api/extract?format=${format}`
        : '/api/extract'

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      if (format === 'json') {
        const data = await response.json()
        setResult(data)
      } else {
        // For file downloads, create blob URL
        const blob = await response.blob()
        const blobUrl = URL.createObjectURL(blob)
        setDownloadUrl(blobUrl)

        // Auto-trigger download
        const a = document.createElement('a')
        a.href = blobUrl
        a.download = `extraction.${format}`
        a.click()
        URL.revokeObjectURL(blobUrl)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <h1>Image to Excel</h1>
        <p className="subtitle">Extract structured data from PDFs and images</p>

        <div className="card">
          <FileUpload
            file={file}
            onFileSelect={handleFileSelect}
          />

          <div className="format-selector">
            <label htmlFor="format">Output Format:</label>
            <select id="format" value={format} onChange={handleFormatChange}>
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="xlsx">Excel (XLSX)</option>
            </select>
          </div>

          <button
            className="submit-btn"
            onClick={handleSubmit}
            disabled={!file || loading}
          >
            {loading ? 'Processing...' : 'Extract Data'}
          </button>

          {error && (
            <div className="error">
              <strong>Error:</strong> {error}
            </div>
          )}

          {loading && (
            <div className="loading">
              Processing your document...
            </div>
          )}
        </div>

        {result && (
          <ResultsDisplay data={result} />
        )}
      </div>
    </div>
  )
}

export default App