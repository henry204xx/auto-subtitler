import { useState, useEffect, useCallback, useMemo } from 'react';
import Layout from './components/Layout';
import VideoUpload from './components/VideoUpload';
import ConfigForm from './components/ConfigForm';
import ProgressTracker from './components/ProgressTracker';
import DownloadSection from './components/DownloadSection';
import { ToastProvider, useToast } from './components/Toast';
import { getLanguages, getModels, uploadVideo, getJobStatus } from './api';
import type { Language, WhisperModel, JobStatus } from './types';

function AppContent() {
  const { showSuccess, showError } = useToast();
  
  const [languages, setLanguages] = useState<Language[]>([]);
  const [models, setModels] = useState<WhisperModel[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('es');
  const [modelSize, setModelSize] = useState('medium');
  const [subtitleMode, setSubtitleMode] = useState<'hard' | 'soft' | 'srt'>('hard');
  const [isProcessing, setIsProcessing] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);

  const languageByCode = useMemo(() => {
    return new Map(languages.map((lang) => [lang.code, lang]));
  }, [languages]);

  const targetLanguages = useMemo(() => {
    if (!languages.length) return [];
    const source = languageByCode.get(sourceLang);
    const supportedTargets = source?.targets?.length
      ? source.targets
      : languages.map((lang) => lang.code);
    const allowed = new Set([sourceLang, ...supportedTargets]);
    return languages.filter((lang) => allowed.has(lang.code));
  }, [languages, sourceLang, languageByCode]);

  const sourceLanguages = useMemo(() => {
    if (!languages.length) return [];
    return languages.filter((lang) => {
      if (lang.code === targetLang) return true;
      const supportedTargets = lang.targets?.length
        ? lang.targets
        : languages.map((item) => item.code);
      return supportedTargets.includes(targetLang);
    });
  }, [languages, targetLang]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [langsData, modelsData] = await Promise.all([
          getLanguages(),
          getModels(),
        ]);
        setLanguages(langsData);
        setModels(modelsData);
      } catch (error) {
        showError('Failed to load configuration data');
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, [showError]);

  useEffect(() => {
    if (!languages.length) return;

    const sourceStillValid = sourceLanguages.some((lang) => lang.code === sourceLang);
    if (!sourceStillValid) {
      setSourceLang(sourceLanguages[0]?.code ?? languages[0].code);
      return;
    }

    const targetStillValid = targetLanguages.some((lang) => lang.code === targetLang);
    if (!targetStillValid) {
      setTargetLang(targetLanguages[0]?.code ?? sourceLang);
    }
  }, [languages, sourceLanguages, targetLanguages, sourceLang, targetLang]);

  useEffect(() => {
    if (!jobId || !isProcessing) return;

    const pollStatus = async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);

        if (status.status === 'completed') {
          setIsProcessing(false);
          showSuccess('Processing completed successfully!');
        } else if (status.status === 'error') {
          setIsProcessing(false);
          showError(status.error || 'An error occurred during processing');
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [jobId, isProcessing, showSuccess, showError]);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setJobId(null);
    setJobStatus(null);
  }, []);

  const handleClearFile = useCallback(() => {
    setSelectedFile(null);
    setJobId(null);
    setJobStatus(null);
  }, []);

  const handleSubmit = async () => {
    if (!selectedFile) {
      showError('Please select a video file');
      return;
    }

    try {
      setIsProcessing(true);
      const response = await uploadVideo({
        video: selectedFile,
        source_lang: sourceLang,
        target_lang: targetLang,
        model_size: modelSize,
        burn_subtitles: subtitleMode === 'hard',
        soft_subtitles: subtitleMode === 'soft',
      });
      
      setJobId(response.job_id);
      showSuccess('Upload successful! Processing started...');
    } catch (error: any) {
      setIsProcessing(false);
      showError(error.response?.data?.error || 'Failed to upload video');
      console.error('Upload error:', error);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setJobId(null);
    setJobStatus(null);
    setIsProcessing(false);
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Upload Section */}
        <VideoUpload
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
          onClear={handleClearFile}
        />

        {/* Configuration Section */}
        {selectedFile && !isProcessing && !jobStatus && (
          <>
            <ConfigForm
              sourceLanguages={sourceLanguages}
              targetLanguages={targetLanguages}
              models={models}
              sourceLang={sourceLang}
              targetLang={targetLang}
              modelSize={modelSize}
              subtitleMode={subtitleMode}
              onSourceLangChange={setSourceLang}
              onTargetLangChange={setTargetLang}
              onModelChange={setModelSize}
              onSubtitleModeChange={setSubtitleMode}
            />

            <div className="flex gap-4">
              <button
                onClick={handleSubmit}
                disabled={!selectedFile || isProcessing}
                className="btn btn-primary flex-1 py-3 text-base"
              >
                Start Processing
              </button>
            </div>
          </>
        )}

        {/* Progress Section */}
        {isProcessing && (
          <ProgressTracker jobStatus={jobStatus} />
        )}

        {/* Download Section */}
        {jobStatus?.status === 'completed' && (
          <>
            <ProgressTracker jobStatus={jobStatus} />
            <DownloadSection jobStatus={jobStatus} jobId={jobId} />
            
            <div className="flex justify-center">
              <button
                onClick={handleReset}
                className="btn btn-outline"
              >
                Process Another Video
              </button>
            </div>
          </>
        )}

        {/* Error State */}
        {jobStatus?.status === 'error' && (
          <>
            <ProgressTracker jobStatus={jobStatus} />
            <div className="flex justify-center">
              <button
                onClick={handleReset}
                className="btn btn-outline"
              >
                Try Again
              </button>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}

function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}

export default App;

