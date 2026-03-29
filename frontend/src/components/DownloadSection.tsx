import React from 'react';
import { Download, FileText, Video } from 'lucide-react';
import type { JobStatus } from '../types';
import { downloadSubtitle, downloadVideo } from '../api';

interface DownloadSectionProps {
  jobStatus: JobStatus | null;
  jobId: string | null;
}

const DownloadSection: React.FC<DownloadSectionProps> = ({ jobStatus, jobId }) => {
  if (!jobStatus || !jobId || jobStatus.status !== 'completed') {
    return null;
  }

  const hasOriginalSrt = !!jobStatus.original_srt;
  const hasTranslatedSrt = !!jobStatus.translated_srt;
  const hasVideo = !!jobStatus.output_video;
  const isTranslated = jobStatus.source_lang !== jobStatus.target_lang;

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Download Files</h2>
      
      <div className="space-y-3">
        {/* Original SRT */}
        {hasOriginalSrt && (
          <a
            href={downloadSubtitle(jobId, 'original')}
            download
            className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-all group"
          >
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Original Subtitles (SRT)</p>
              <p className="text-xs text-gray-500">
                {jobStatus.source_lang.toUpperCase()} - Transcribed from audio
              </p>
            </div>
            <Download className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
          </a>
        )}

        {/* Translated SRT */}
        {hasTranslatedSrt && isTranslated && (
          <a
            href={downloadSubtitle(jobId, 'translated')}
            download
            className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 transition-all group"
          >
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
              <FileText className="w-5 h-5 text-green-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Translated Subtitles (SRT)</p>
              <p className="text-xs text-gray-500">
                {jobStatus.target_lang.toUpperCase()} - Translated from {jobStatus.source_lang.toUpperCase()}
              </p>
            </div>
            <Download className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
          </a>
        )}

        {/* Video with Subtitles */}
        {hasVideo && (
          <a
            href={downloadVideo(jobId)}
            download
            className="flex items-center gap-4 p-4 border-2 border-primary-200 bg-primary-50 rounded-lg hover:bg-primary-100 hover:border-primary-300 transition-all group"
          >
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center group-hover:bg-primary-700 transition-colors">
              <Video className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Video with Subtitles</p>
              <p className="text-xs text-gray-600">
                {jobStatus.burn_subtitles ? 'Hard-burned subtitles (permanent)' : 'Soft subtitles (toggleable)'}
              </p>
            </div>
            <Download className="w-5 h-5 text-primary-600 group-hover:text-primary-700 transition-colors" />
          </a>
        )}
      </div>

      {!hasOriginalSrt && !hasTranslatedSrt && !hasVideo && (
        <div className="text-center py-8">
          <p className="text-sm text-gray-500">No files available for download</p>
        </div>
      )}
    </div>
  );
};

export default DownloadSection;
