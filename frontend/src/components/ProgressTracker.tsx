import React from 'react';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import type { JobStatus } from '../types';

interface ProgressTrackerProps {
  jobStatus: JobStatus | null;
}

const stages = [
  { key: 'uploaded', label: 'Uploaded' },
  { key: 'extracting', label: 'Extracting Audio' },
  { key: 'transcribing', label: 'Transcribing' },
  { key: 'translating', label: 'Translating' },
  { key: 'embedding', label: 'Processing Video' },
];

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ jobStatus }) => {
  if (!jobStatus) return null;

  const getCurrentStageIndex = (): number => {
    if (!jobStatus.progress) return 0;
    const progress = jobStatus.progress.toLowerCase();
    
    if (progress.includes('completed')) return stages.length;
    if (progress.includes('burning') || progress.includes('embedding') || progress.includes('subtitle')) return 4;
    if (progress.includes('translat')) return 3;
    if (progress.includes('transcrib')) return 2;
    if (progress.includes('extract') || progress.includes('audio')) return 1;
    return 0;
  };

  const currentStage = getCurrentStageIndex();
  const isError = jobStatus.status === 'error';
  const isCompleted = jobStatus.status === 'completed';

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Processing Status</h2>

      {/* Status Header */}
      <div className="mb-6 p-4 rounded-lg bg-gray-50 border border-gray-200">
        <div className="flex items-center gap-3">
          {isError ? (
            <XCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
          ) : isCompleted ? (
            <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
          ) : (
            <Loader2 className="w-6 h-6 text-primary-600 animate-spin flex-shrink-0" />
          )}
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">{jobStatus.filename}</p>
            <p className={`text-sm ${isError ? 'text-red-600' : 'text-gray-600'}`}>
              {jobStatus.progress}
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {isError && jobStatus.error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-900 mb-1">Error</p>
          <p className="text-sm text-red-700">{jobStatus.error}</p>
        </div>
      )}

      {/* Progress Steps */}
      {!isError && (
        <div className="space-y-3">
          {stages.map((stage, index) => {
            const isActive = index === currentStage && !isCompleted;
            const isDone = index < currentStage || isCompleted;

            return (
              <div key={stage.key} className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 transition-colors ${
                    isDone
                      ? 'bg-green-100 text-green-600'
                      : isActive
                      ? 'bg-primary-100 text-primary-600'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {isDone ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : isActive ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </div>
                <div className="flex-1">
                  <p
                    className={`text-sm font-medium ${
                      isDone
                        ? 'text-green-700'
                        : isActive
                        ? 'text-primary-700'
                        : 'text-gray-500'
                    }`}
                  >
                    {stage.label}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Completion Message */}
      {isCompleted && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm font-medium text-green-900">
            Processing completed successfully!
          </p>
          <p className="text-sm text-green-700 mt-1">
            Your subtitles are ready to download below.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProgressTracker;
