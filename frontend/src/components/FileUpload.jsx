import { useCallback, useState } from 'react'

function FileUpload({ file, onFileSelect }) {
  const [dragOver, setDragOver] = useState(false)

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(true)
  }, [])

  const handleDragOut = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0])
    }
  }, [onFileSelect])

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0])
    }
  }

  const removeFile = (e) => {
    e.stopPropagation()
    onFileSelect(null)
  }

  return (
    <div
      className={`file-upload ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {file ? (
        <div className="file-info">
          <span className="file-name">{file.name}</span>
          <span className="file-size">
            {(file.size / 1024).toFixed(2)} KB
          </span>
          <button className="remove-file" onClick={removeFile} type="button">
            Remove
          </button>
        </div>
      ) : (
        <>
          <div className="upload-icon">📁</div>
          <p className="upload-text">
            Drag & drop your file here, or click to select
          </p>
          <p className="upload-hint">
            Supported formats: PDF, JPEG, JPG, PNG (max 20MB)
          </p>
          <input
            type="file"
            className="file-input"
            onChange={handleFileChange}
            accept=".pdf,.jpeg,.jpg,.png"
          />
        </>
      )}
    </div>
  )
}

export default FileUpload