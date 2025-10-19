import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Spinner from '../components/Spinner';
import ResultsDisplay from '../components/ResultsDisplay';

// Match the interfaces in ResultsDisplay.tsx
interface CriticalIssue {
  body_part: string;
  problem: string;
  injury_risk: string;
  correction: string;
  drill: string;
}
interface FeedbackData {
  overall_score: number;
  injury_risk: 'LOW' | 'MODERATE' | 'HIGH';
  injury_risk_explanation: string;
  critical_issues: CriticalIssue[];
  positive_feedback: string;
  summary: string;
}

const AnalysisPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState<FeedbackData | null>(null);
  const [gifUrl, setGifUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError(null);
      setFeedback(null); // Reset previous results
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'video/*': ['.mp4', '.mov', '.avi'] },
    multiple: false,
  });

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a video file first.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setStatus('Uploading video...');

    const formData = new FormData();
    formData.append('video', file);

    try {
      setStatus('Processing... This may take up to a minute.');
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'An unknown error occurred.');
      }

      const result = await response.json();
      setFeedback(result.feedback);
      setGifUrl(result.gifUrl);

    } catch (err: any) {
      setError(err.message || 'Failed to connect to the analysis server.');
      setFeedback(null);
    } finally {
      setIsLoading(false);
      setStatus('');
    }
  };
  
  const resetState = () => {
    setFile(null);
    setFeedback(null);
    setGifUrl(null);
    setError(null);
  }

  // --- Render Logic ---
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh]">
        <Spinner />
        <p className="mt-4 text-lg text-cyan-400">{status}</p>
      </div>
    );
  }

  if (feedback && gifUrl) {
    return (
      <div className="container mx-auto py-8">
        <ResultsDisplay feedback={feedback} gifUrl={gifUrl} />
        <div className="text-center mt-8">
            <button
                onClick={resetState}
                className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-6 rounded-full transition-colors"
            >
                Analyze Another Video
            </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-12 flex flex-col items-center">
      <div className="w-full max-w-2xl">
        <div
          {...getRootProps()}
          className={`border-4 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${isDragActive ? 'border-cyan-400 bg-gray-800' : 'border-gray-600 hover:border-cyan-500'}`}
        >
          <input {...getInputProps()} />
          {file ? (
            <div>
              <p className="text-xl font-semibold text-green-400">✅ Video Selected!</p>
              <p className="text-gray-400">{file.name}</p>
            </div>
          ) : (
            <p className="text-lg text-gray-400">
              {isDragActive ? 'Drop the video here...' : 'Drag & drop a video, or click to select'}
            </p>
          )}
        </div>

        {error && <p className="text-red-500 mt-4 text-center">{error}</p>}
        
        <div className="mt-6 text-center">
          <button
            onClick={handleSubmit}
            disabled={!file || isLoading}
            className="bg-cyan-500 text-white font-bold py-3 px-10 rounded-full text-lg transition-all disabled:bg-gray-600 disabled:cursor-not-allowed hover:bg-cyan-600"
          >
            Analyze My Smash
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;