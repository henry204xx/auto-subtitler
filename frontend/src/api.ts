import axios from 'axios';
import type { Language, WhisperModel, UploadResponse, JobStatus, UploadOptions } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getLanguages = async (): Promise<Language[]> => {
  const response = await api.get<Language[]>('/languages');
  return response.data;
};

export const getModels = async (): Promise<WhisperModel[]> => {
  const response = await api.get<WhisperModel[]>('/models');
  return response.data;
};

export const uploadVideo = async (options: UploadOptions): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('video', options.video);
  formData.append('source_lang', options.source_lang);
  formData.append('target_lang', options.target_lang);
  formData.append('model_size', options.model_size);
  formData.append('burn_subtitles', options.burn_subtitles.toString());
  formData.append('soft_subtitles', options.soft_subtitles.toString());

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await api.get<JobStatus>(`/status/${jobId}`);
  return response.data;
};

export const downloadSubtitle = (jobId: string, type: 'original' | 'translated' = 'translated'): string => {
  return `${API_BASE_URL}/download/${jobId}?type=${type}`;
};

export const downloadVideo = (jobId: string): string => {
  return `${API_BASE_URL}/download-video/${jobId}`;
};

export default api;
