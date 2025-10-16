'use client'

import { useState, useRef } from 'react'
import { Upload, FileText, X, AlertCircle } from 'lucide-react'
import { AnalysisResult } from '../utils/export'

interface FileUploadProps {
  onAnalysisComplete: (result: AnalysisResult) => void
  onError: (error: string) => void
  useStreaming?: boolean
}

export function FileUpload({ onAnalysisComplete, onError, useStreaming = false }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      onError('Please select a PDF file')
      return
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB
      onError('File size must be less than 10MB')
      return
    }
    
    setSelectedFile(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadProgress(0)
    setCurrentStage('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      if (useStreaming) {
        await handleStreamingUpload(formData)
      } else {
        await handleRegularUpload(formData)
      }
    } catch (error) {
      console.error('Upload error:', error)
      onError('Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
      setCurrentStage('')
    }
  }

  const handleStreamingUpload = async (formData: FormData) => {
    const response = await fetch('http://localhost:8000/analyze_sse', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.stage === 'ingest') {
              setCurrentStage('Processing uploaded file...')
              setUploadProgress(25)
            } else if (data.stage === 'extract') {
              setCurrentStage('Extracting text from PDF...')
              setUploadProgress(50)
            } else if (data.stage === 'analyze') {
              setCurrentStage('Analyzing compliance issues with Groq AI...')
              setUploadProgress(75)
            } else if (data.stage === 'done') {
              setCurrentStage('Analysis complete!')
              setUploadProgress(100)
              onAnalysisComplete(data.result)
              return
            } else if (data.stage === 'error') {
              throw new Error(data.message)
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e)
          }
        }
      }
    }
  }

  const handleRegularUpload = async (formData: FormData) => {
    setCurrentStage('Uploading and analyzing...')
    setUploadProgress(50)

    const response = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    setUploadProgress(100)
    setCurrentStage('Analysis complete!')
    
    const result = await response.json()
    onAnalysisComplete(result)
  }

  const clearFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-groq-blue bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileInputChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isUploading}
        />
        
        {selectedFile ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <FileText className="h-8 w-8 text-groq-blue" />
              <span className="text-lg font-medium">{selectedFile.name}</span>
              <button
                onClick={clearFile}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                disabled={isUploading}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
            </div>
            
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="px-6 py-2 bg-groq-blue text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? 'Analyzing...' : 'Analyze Document'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="h-12 w-12 text-gray-400 mx-auto" />
            <div>
              <p className="text-lg font-medium">Drop your PDF here</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                or click to browse files
              </p>
            </div>
            <p className="text-xs text-gray-400">
              Maximum file size: 10MB
            </p>
          </div>
        )}
      </div>

      {isUploading && (
        <div className="mt-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span>{currentStage}</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-groq-blue h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}