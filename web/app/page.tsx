'use client';

import { useState } from 'react';
import UploadZone from './components/UploadZone';
import StreamingProgress from './components/StreamingProgress';
import ReportView from './components/ReportView';
import RecentReports from './components/RecentReports';

interface Report {
  doc_name: string;
  page_count?: number;
  summary: string;
  overall_risk: number;
  flags: any[];
}

interface StreamingState {
  stage: string;
  message: string;
}

export default function Home() {
  const [report, setReport] = useState<Report | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true);
  const [streamingState, setStreamingState] = useState<StreamingState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);

  const handleFileSelect = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setReport(null);
    setStreamingState(null);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    if (useStreaming) {
      await handleStreamingUpload(file, apiUrl);
    } else {
      await handleNormalUpload(file, apiUrl);
    }

    setIsUploading(false);
  };

  const handleStreamingUpload = async (file: File, apiUrl: string) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiUrl}/analyze_sse`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue;

          const [eventLine, dataLine] = line.split('\n');
          if (!eventLine.startsWith('event:') || !dataLine.startsWith('data:')) continue;

          const event = eventLine.substring(6).trim();
          const data = JSON.parse(dataLine.substring(5).trim());

          if (event === 'progress') {
            setStreamingState({ stage: data.stage, message: data.message });
          } else if (event === 'done') {
            setReport(data);
            setStreamingState({ stage: 'done', message: 'Complete!' });
          } else if (event === 'error') {
            throw new Error(data.error);
          }
        }
      }
    } catch (err: any) {
      console.error('Streaming error:', err);
      setError(getErrorMessage(err));
    }
  };

  const handleNormalUpload = async (file: File, apiUrl: string) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setReport(data);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(getErrorMessage(err));
    }
  };

  const getErrorMessage = (err: any): string => {
    const message = err.message || String(err);
    
    if (message.includes('413') || message.includes('File size exceeds')) {
      return 'File size exceeds 10MB limit. Please upload a smaller file.';
    }
    if (message.includes('400') || message.includes('Only PDF')) {
      return 'Invalid file format. Only PDF files are accepted.';
    }
    if (message.includes('401') || message.includes('Unauthorized')) {
      return 'Authentication failed. Please check API credentials.';
    }
    if (message.includes('Could not extract')) {
      return 'Unable to extract text from PDF. The file may be corrupted or image-based.';
    }
    
    return `Analysis failed: ${message}`;
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
        <div className="container mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-4 mb-4">
              <h1 className="text-4xl font-bold dark:text-white">AI Compliance Copilot</h1>
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                aria-label="Toggle dark mode"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              Ultra-fast compliance analysis powered by{' '}
              <a
                href="https://groq.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
              >
                Groq
              </a>
            </p>
          </div>

          {/* Upload Zone */}
          <UploadZone
            onFileSelect={handleFileSelect}
            isUploading={isUploading}
            useStreaming={useStreaming}
            onToggleStreaming={setUseStreaming}
          />

          {/* Error Message */}
          {error && (
            <div className="w-full max-w-2xl mx-auto mt-6 p-4 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-300 rounded-lg">
              <p className="font-medium">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Streaming Progress */}
          {useStreaming && streamingState && streamingState.stage !== 'done' && (
            <StreamingProgress stage={streamingState.stage} message={streamingState.message} />
          )}

          {/* Report View */}
          {report && <ReportView report={report} />}

          {/* Recent Reports */}
          {!isUploading && <RecentReports />}

          {/* Footer */}
          <footer className="mt-16 text-center text-gray-600 dark:text-gray-400">
            <p>
              Powered by{' '}
              <a
                href="https://groq.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
              >
                Groq
              </a>
              {' '}| Built with Next.js & FastAPI
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}
