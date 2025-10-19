import React, { useState } from 'react';
import { Upload, Play, AlertCircle, CheckCircle, Loader, TrendingUp, Target, Award } from 'lucide-react';

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

      await pollForResults();
    } catch (err) {
      setError(err.message || 'An error occurred during upload');
      setUploading(false);
      setProcessing(false);
    }
  };

  const pollForResults = async () => {
    const maxAttempts = 60;
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

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)',
      padding: '2rem',
      position: 'relative',
      overflow: 'hidden'
    },
    backgroundEffect: {
      position: 'absolute',
      inset: 0,
      background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.15), transparent 50%)',
      pointerEvents: 'none'
    },
    contentWrapper: {
      position: 'relative',
      zIndex: 10,
      maxWidth: '1280px',
      margin: '0 auto'
    },
    header: {
      textAlign: 'center',
      marginBottom: '3rem'
    },
    headerIcon: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '1rem',
      marginBottom: '1rem'
    },
    iconBox: {
      height: '3rem',
      width: '3rem',
      borderRadius: '0.75rem',
      background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: '0 10px 30px rgba(139, 92, 246, 0.4)'
    },
    title: {
      fontSize: '3.5rem',
      fontWeight: 'bold',
      background: 'linear-gradient(to right, #ffffff, #a78bfa, #8b5cf6)',
      WebkitBackgroundClip: 'text',
      backgroundClip: 'text',
      color: 'transparent',
      margin: 0
    },
    subtitle: {
      color: '#c4b5fd',
      fontSize: '1.125rem',
      maxWidth: '42rem',
      margin: '0 auto'
    },
    card: {
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(20px)',
      borderRadius: '1.5rem',
      padding: '2rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
      marginBottom: '2rem'
    },
    dropzone: {
      border: '3px dashed',
      borderRadius: '1.5rem',
      padding: '3rem',
      textAlign: 'center',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    dropzoneActive: {
      borderColor: '#8b5cf6',
      background: 'rgba(139, 92, 246, 0.1)',
      transform: 'scale(1.02)'
    },
    dropzoneInactive: {
      borderColor: 'rgba(167, 139, 250, 0.3)',
      background: 'transparent'
    },
    uploadIcon: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '1rem'
    },
    iconCircle: {
      height: '5rem',
      width: '5rem',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    },
    fileName: {
      color: '#ffffff',
      fontWeight: '600',
      fontSize: '1.125rem',
      marginBottom: '0.5rem'
    },
    fileSize: {
      color: '#c4b5fd',
      fontSize: '0.875rem'
    },
    errorBox: {
      marginTop: '1rem',
      padding: '1rem',
      background: 'rgba(239, 68, 68, 0.1)',
      border: '1px solid rgba(239, 68, 68, 0.3)',
      borderRadius: '0.75rem',
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem'
    },
    buttonContainer: {
      marginTop: '1.5rem',
      display: 'flex',
      gap: '1rem',
      justifyContent: 'center',
      flexWrap: 'wrap'
    },
    button: {
      padding: '0.875rem 2rem',
      fontSize: '1rem',
      fontWeight: '600',
      borderRadius: '0.75rem',
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      transition: 'all 0.3s ease',
      boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)'
    },
    primaryButton: {
      background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
      color: '#ffffff'
    },
    secondaryButton: {
      background: 'rgba(71, 85, 105, 0.8)',
      color: '#ffffff'
    },
    disabledButton: {
      background: 'rgba(75, 85, 99, 0.5)',
      cursor: 'not-allowed',
      opacity: 0.6
    },
    processingText: {
      marginTop: '1.5rem',
      textAlign: 'center',
      color: '#c4b5fd',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.75rem',
      padding: '1rem',
      background: 'rgba(139, 92, 246, 0.1)',
      borderRadius: '9999px'
    },
    pulsingDot: {
      height: '0.5rem',
      width: '0.5rem',
      borderRadius: '50%',
      background: '#8b5cf6',
      animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
    },
    resultsContainer: {
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem'
    },
    sectionHeader: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      marginBottom: '1.5rem'
    },
    sectionTitle: {
      fontSize: '2rem',
      fontWeight: 'bold',
      color: '#ffffff',
      margin: 0
    },
    sectionSubtitle: {
      color: '#c4b5fd',
      fontSize: '0.875rem'
    },
    gridContainer: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '1.5rem'
    },
    gifCard: {
      position: 'relative',
      background: 'rgba(0, 0, 0, 0.3)',
      borderRadius: '1.25rem',
      padding: '1rem',
      border: '1px solid rgba(167, 139, 250, 0.2)',
      transition: 'all 0.3s ease'
    },
    gifCardHover: {
      transform: 'translateY(-4px)',
      boxShadow: '0 20px 40px rgba(139, 92, 246, 0.3)'
    },
    gifHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '0.75rem'
    },
    gifTitle: {
      fontSize: '1.125rem',
      fontWeight: '600',
      color: '#ffffff'
    },
    gifImage: {
      width: '100%',
      borderRadius: '0.75rem',
      aspectRatio: '16/9',
      objectFit: 'contain',
      background: 'rgba(0, 0, 0, 0.5)'
    },
    tipsBox: {
      color: '#e9d5ff',
      whiteSpace: 'pre-wrap',
      lineHeight: '1.75',
      background: 'rgba(0, 0, 0, 0.2)',
      borderRadius: '1rem',
      padding: '1.5rem',
      border: '1px solid rgba(167, 139, 250, 0.1)'
    },
    scoreContainer: {
      marginBottom: '1.5rem'
    },
    scoreHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      marginBottom: '0.75rem'
    },
    scoreValue: {
      fontSize: '3.5rem',
      fontWeight: 'bold',
      background: 'linear-gradient(to right, #a78bfa, #8b5cf6)',
      WebkitBackgroundClip: 'text',
      backgroundClip: 'text',
      color: 'transparent'
    },
    scoreLabel: {
      color: '#c4b5fd',
      fontSize: '0.875rem'
    },
    progressBar: {
      position: 'relative',
      height: '1.5rem',
      background: 'rgba(0, 0, 0, 0.3)',
      borderRadius: '9999px',
      overflow: 'hidden'
    },
    progressFill: {
      height: '100%',
      background: 'linear-gradient(to right, #a78bfa, #8b5cf6, #7c3aed)',
      borderRadius: '9999px',
      transition: 'width 1s ease-out',
      boxShadow: '0 0 20px rgba(139, 92, 246, 0.6)'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.backgroundEffect} />
      
      <div style={styles.contentWrapper}>
        {/* Header */}
        <header style={styles.header}>
          <div style={styles.headerIcon}>
            <div style={styles.iconBox}>
              <Target size={32} color="#ffffff" />
            </div>
            <h1 style={styles.title}>Motion Mentor</h1>
          </div>
          <p style={styles.subtitle}>
            Upload your badminton smash video and receive AI-powered insights to elevate your technique
          </p>
        </header>

        {/* Upload Section */}
        {!results && (
          <div style={styles.card}>
            <div
              style={{
                ...styles.dropzone,
                ...(dragActive ? styles.dropzoneActive : styles.dropzoneInactive)
              }}
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
                style={{ display: 'none' }}
                disabled={uploading || processing}
              />
              
              <label htmlFor="video-upload" style={{ cursor: 'pointer', display: 'block' }}>
                <div style={styles.uploadIcon}>
                  {file ? (
                    <>
                      <div style={{ ...styles.iconCircle, background: 'rgba(34, 197, 94, 0.2)' }}>
                        <CheckCircle size={48} color="#22c55e" />
                      </div>
                      <div>
                        <p style={styles.fileName}>{file.name}</p>
                        <p style={styles.fileSize}>
                          {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <div style={{ ...styles.iconCircle, background: 'rgba(139, 92, 246, 0.2)' }}>
                        <Upload size={48} color="#8b5cf6" />
                      </div>
                      <div>
                        <p style={styles.fileName}>
                          Drop your video here or click to browse
                        </p>
                        <p style={styles.fileSize}>
                          Supports MP4, MOV, AVI and more
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </label>
            </div>

            {error && (
              <div style={styles.errorBox}>
                <AlertCircle size={20} color="#ef4444" />
                <p style={{ color: '#fca5a5', margin: 0 }}>{error}</p>
              </div>
            )}

            <div style={styles.buttonContainer}>
              <button
                onClick={handleUpload}
                disabled={!file || uploading || processing}
                style={{
                  ...styles.button,
                  ...styles.primaryButton,
                  ...(!file || uploading || processing ? styles.disabledButton : {})
                }}
                onMouseEnter={(e) => {
                  if (file && !uploading && !processing) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(139, 92, 246, 0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
                }}
              >
                {uploading || processing ? (
                  <>
                    <Loader size={20} style={{ animation: 'spin 1s linear infinite' }} />
                    {uploading ? 'Uploading...' : 'Processing...'}
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    Analyze Video
                  </>
                )}
              </button>
              
              {file && !uploading && !processing && (
                <button
                  onClick={resetUpload}
                  style={{
                    ...styles.button,
                    ...styles.secondaryButton
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.background = 'rgba(71, 85, 105, 1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.background = 'rgba(71, 85, 105, 0.8)';
                  }}
                >
                  Clear
                </button>
              )}
            </div>

            {processing && (
              <div style={styles.processingText}>
                <div style={styles.pulsingDot} />
                <p style={{ margin: 0, fontWeight: '500' }}>
                  Analyzing your technique with AI... This may take a minute.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Results Section */}
        {results && (
          <div style={styles.resultsContainer}>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <button
                onClick={resetUpload}
                style={{
                  ...styles.button,
                  ...styles.primaryButton
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(139, 92, 246, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
                }}
              >
                <Upload size={20} />
                Analyze Another Video
              </button>
            </div>

            {/* Similarity Score */}
            {results.similarity && (
              <div style={styles.card}>
                <div style={styles.sectionHeader}>
                  <div style={{ ...styles.iconBox, height: '3rem', width: '3rem' }}>
                    <Award size={28} color="#ffffff" />
                  </div>
                  <div>
                    <h2 style={styles.sectionTitle}>Similarity Score</h2>
                    <p style={styles.sectionSubtitle}>Match with professional technique</p>
                  </div>
                </div>
                <div style={styles.scoreContainer}>
                  <div style={styles.scoreHeader}>
                    <span style={styles.scoreValue}>{results.similarity}%</span>
                    <span style={styles.scoreLabel}>similarity</span>
                  </div>
                  <div style={styles.progressBar}>
                    <div
                      style={{
                        ...styles.progressFill,
                        width: `${results.similarity}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* GIF Comparison */}
            <div style={styles.card}>
              <div style={styles.sectionHeader}>
                <TrendingUp size={24} color="#8b5cf6" />
                <h2 style={styles.sectionTitle}>Technique Comparison</h2>
              </div>
              <div style={styles.gridContainer}>
                <div
                  style={styles.gifCard}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 20px 40px rgba(139, 92, 246, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={styles.gifHeader}>
                    <h3 style={styles.gifTitle}>Professional Form</h3>
                    <Award size={20} color="#a78bfa" />
                  </div>
                  <img
                    src="http://localhost:8000/gifs/proshot.gif"
                    alt="Professional technique"
                    style={styles.gifImage}
                  />
                </div>
                <div
                  style={styles.gifCard}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 20px 40px rgba(139, 92, 246, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={styles.gifHeader}>
                    <h3 style={styles.gifTitle}>Your Form</h3>
                    <Target size={20} color="#8b5cf6" />
                  </div>
                  <img
                    src="http://localhost:8000/gifs/badminton_shot_user_video.gif"
                    alt="Your technique"
                    style={styles.gifImage}
                  />
                </div>
              </div>
            </div>

            {/* AI Tips */}
            <div style={styles.card}>
              <div style={styles.sectionHeader}>
                <div style={{ ...styles.iconBox, height: '2.5rem', width: '2.5rem' }}>
                  <TrendingUp size={20} color="#ffffff" />
                </div>
                <div>
                  <h2 style={styles.sectionTitle}>AI-Powered Insights</h2>
                  <p style={styles.sectionSubtitle}>Personalized recommendations</p>
                </div>
              </div>
              <div style={styles.tipsBox}>
                {results.tips || 'No tips available'}
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}