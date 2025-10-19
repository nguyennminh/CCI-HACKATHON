import React, { useState } from 'react';
import { Upload, Play, AlertCircle, CheckCircle, Loader } from 'lucide-react';

export default function SmashAnalyzer() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type.startsWith('video/')) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please upload a video file');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a video file');
      return;
    }

    const formData = new FormData();
    formData.append('video', file);

    setUploading(true);
    setProcessing(false);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      setUploading(false);
      setProcessing(true);

      // Poll for results
      await pollForResults();
    } catch (err) {
      setError(err.message || 'An error occurred during upload');
      setUploading(false);
      setProcessing(false);
    }
  };

  const pollForResults = async () => {
    // Poll every 2 seconds for results
    const maxAttempts = 60; // 2 minutes max
    let attempts = 0;

    const poll = setInterval(async () => {
      attempts++;
      
      try {
        const response = await fetch('http://localhost:8000/results');
        
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'completed') {
            setResults(data);
            setProcessing(false);
            clearInterval(poll);
          }
        } else if (response.status === 202) {
          // Still processing, continue polling
          console.log('Still processing...');
        } else if (attempts >= maxAttempts) {
          throw new Error('Processing timeout');
        }
      } catch (err) {
        if (attempts >= maxAttempts) {
          setError('Processing took too long. Please try again.');
          setProcessing(false);
          clearInterval(poll);
        }
      }
    }, 2000);
  };

  const resetUpload = () => {
    setFile(null);
    setResults(null);
    setError(null);
    setUploading(false);
    setProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Smash Technique Analyzer
          </h1>
          <p className="text-purple-200 text-lg">
            Upload your smash video and get AI-powered insights to improve your technique
          </p>
        </div>

        {/* Upload Section */}
        {!results && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8 border border-white/20">
            <div
              className={`border-4 border-dashed rounded-xl p-12 text-center transition-all ${
                dragActive
                  ? 'border-purple-400 bg-purple-500/20'
                  : 'border-purple-300/50 hover:border-purple-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="video-upload"
                accept="video/*"
                onChange={handleFileChange}
                className="hidden"
                disabled={uploading || processing}
              />
              
              <label htmlFor="video-upload" className="cursor-pointer">
                <div className="flex flex-col items-center gap-4">
                  {file ? (
                    <>
                      <CheckCircle className="w-16 h-16 text-green-400" />
                      <div className="text-white">
                        <p className="font-semibold text-lg">{file.name}</p>
                        <p className="text-sm text-purple-200">
                          {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <Upload className="w-16 h-16 text-purple-300" />
                      <div className="text-white">
                        <p className="font-semibold text-lg">
                          Drop your video here or click to browse
                        </p>
                        <p className="text-sm text-purple-200 mt-2">
                          Supports MP4, MOV, AVI and more
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </label>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-400" />
                <p className="text-red-200">{error}</p>
              </div>
            )}

            <div className="mt-6 flex gap-4 justify-center">
              <button
                onClick={handleUpload}
                disabled={!file || uploading || processing}
                className="px-8 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
              >
                {uploading || processing ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    {uploading ? 'Uploading...' : 'Processing...'}
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Analyze Video
                  </>
                )}
              </button>
              
              {file && !uploading && !processing && (
                <button
                  onClick={resetUpload}
                  className="px-8 py-3 bg-slate-600 hover:bg-slate-700 text-white font-semibold rounded-lg transition-colors"
                >
                  Clear
                </button>
              )}
            </div>

            {processing && (
              <div className="mt-6 text-center">
                <p className="text-purple-200 animate-pulse">
                  Analyzing your technique with AI... This may take a minute.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Results Section */}
        {results && (
          <div className="space-y-8">
            <button
              onClick={resetUpload}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors"
            >
              Analyze Another Video
            </button>

            {/* GIF Comparison */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <h2 className="text-3xl font-bold text-white mb-6">
                Technique Comparison
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-black/30 rounded-xl p-4">
                  <h3 className="text-xl font-semibold text-purple-300 mb-4">
                    Professional Form
                  </h3>
                  <img
                    src={"http://localhost:8000/gifs/proshot.gif"}
                    alt="Professional technique"
                    className="w-full rounded-lg"
                  />
                </div>
                <div className="bg-black/30 rounded-xl p-4">
                  <h3 className="text-xl font-semibold text-purple-300 mb-4">
                    Your Form
                  </h3>
                  <img
                    src={"http://localhost:8000/gifs/badminton_shot_user_video.gif"}
                    alt="Your technique"
                    className="w-full rounded-lg"
                  />
                </div>
              </div>
            </div>

            {/* AI Tips */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <h2 className="text-3xl font-bold text-white mb-6">
                AI-Powered Insights
              </h2>
              <div className="prose prose-invert max-w-none">
                <div className="text-purple-100 whitespace-pre-wrap leading-relaxed">
                  {results.tips || 'No tips available'}
                </div>
              </div>
            </div>

            {/* Similarity Score */}
            {results.similarity && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
                <h2 className="text-3xl font-bold text-white mb-4">
                  Similarity Score
                </h2>
                <div className="flex items-center gap-4">
                  <div className="flex-1 bg-black/30 rounded-full h-8 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-full transition-all duration-1000 flex items-center justify-end pr-4"
                      style={{ width: `${results.similarity}%` }}
                    >
                      <span className="text-white font-bold text-sm">
                        {results.similarity}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}