import React from 'react';
import { Languages, Cpu, FileText } from 'lucide-react';
import type { Language, WhisperModel } from '../types';

interface ConfigFormProps {
  languages: Language[];
  models: WhisperModel[];
  sourceLang: string;
  targetLang: string;
  modelSize: string;
  subtitleMode: 'hard' | 'soft' | 'srt';
  onSourceLangChange: (lang: string) => void;
  onTargetLangChange: (lang: string) => void;
  onModelChange: (model: string) => void;
  onSubtitleModeChange: (mode: 'hard' | 'soft' | 'srt') => void;
}

const ConfigForm: React.FC<ConfigFormProps> = ({
  languages,
  models,
  sourceLang,
  targetLang,
  modelSize,
  subtitleMode,
  onSourceLangChange,
  onTargetLangChange,
  onModelChange,
  onSubtitleModeChange,
}) => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Configuration</h2>
      
      <div className="space-y-6">
        {/* Language Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">
              <Languages className="w-4 h-4 inline mr-2" />
              Source Language
            </label>
            <select
              value={sourceLang}
              onChange={(e) => onSourceLangChange(e.target.value)}
              className="input"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">
              <Languages className="w-4 h-4 inline mr-2" />
              Target Language
            </label>
            <select
              value={targetLang}
              onChange={(e) => onTargetLangChange(e.target.value)}
              className="input"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Model Selection */}
        <div>
          <label className="label">
            <Cpu className="w-4 h-4 inline mr-2" />
            Whisper Model
          </label>
          <select
            value={modelSize}
            onChange={(e) => onModelChange(e.target.value)}
            className="input"
          >
            {models.map((model) => (
              <option key={model.value} value={model.value}>
                {model.name}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-2">
            Larger models provide better accuracy but take longer to process
          </p>
        </div>

        {/* Subtitle Mode */}
        <div>
          <label className="label">
            <FileText className="w-4 h-4 inline mr-2" />
            Subtitle Output
          </label>
          <div className="space-y-2">
            <label className="flex items-center gap-3 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="subtitle-mode"
                value="hard"
                checked={subtitleMode === 'hard'}
                onChange={() => onSubtitleModeChange('hard')}
                className="w-4 h-4 text-primary-600"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Hard Burn</p>
                <p className="text-xs text-gray-500">Permanently embed subtitles into video</p>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="subtitle-mode"
                value="soft"
                checked={subtitleMode === 'soft'}
                onChange={() => onSubtitleModeChange('soft')}
                className="w-4 h-4 text-primary-600"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Soft Subtitles</p>
                <p className="text-xs text-gray-500">Embed as toggleable subtitle track</p>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="subtitle-mode"
                value="srt"
                checked={subtitleMode === 'srt'}
                onChange={() => onSubtitleModeChange('srt')}
                className="w-4 h-4 text-primary-600"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">SRT Files Only</p>
                <p className="text-xs text-gray-500">Generate subtitle files without video</p>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfigForm;
