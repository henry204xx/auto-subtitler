export interface Language {
  code: string;
  name: string;
}

export interface WhisperModel {
  value: string;
  name: string;
  size: string;
}

export interface UploadResponse {
  job_id: string;
  message: string;
}

export interface JobStatus {
  status: 'queued' | 'processing' | 'completed' | 'error';
  progress: string;
  filename: string;
  source_lang: string;
  target_lang: string;
  model_size: string;
  burn_subtitles: boolean;
  original_srt?: string;
  translated_srt?: string;
  output_video?: string;
  error?: string;
}

export interface UploadOptions {
  video: File;
  source_lang: string;
  target_lang: string;
  model_size: string;
  burn_subtitles: boolean;
  soft_subtitles: boolean;
}
