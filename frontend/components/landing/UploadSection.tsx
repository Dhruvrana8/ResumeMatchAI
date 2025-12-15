"use client";

import { useMemo } from "react";

interface UploadSectionProps {
  onAnalyze: () => void;
  isAnalyzing: boolean;
  mode: "score" | "compare" | "create-resume";
}

export function UploadSection({
  onAnalyze,
  isAnalyzing,
  mode,
}: UploadSectionProps) {
  const isCompareMode = mode === "compare";

  return (
    <div className="glass-panel rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5">
      <div className="p-1 border-b border-white/5 bg-white/5 px-6 py-4 flex items-center justify-between">
        <h3 className="font-bold text-foreground flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">
            upload_file
          </span>
          Upload Documents
        </h3>
        {mode === "score" && (
          <span className="text-xs font-medium px-2 py-1 rounded-full bg-primary/10 text-primary border border-primary/20">
            ATS Score Mode
          </span>
        )}
        {mode === "compare" && (
          <span className="text-xs font-medium px-2 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Comparison Mode
          </span>
        )}
      </div>

      <div
        className={`p-6 grid gap-8 ${
          isCompareMode ? "md:grid-cols-2" : "md:grid-cols-1 max-w-2xl mx-auto"
        }`}
      >
        {/* File Upload Area */}
        <div className="flex flex-col gap-3">
          <label className="text-sm font-semibold text-muted-foreground">
            Resume (PDF)
          </label>
          <div className="group relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-muted hover:border-primary/50 rounded-xl bg-card hover:bg-card/80 transition-all cursor-pointer">
            <input
              type="file"
              accept=".pdf"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center px-4 transition-transform group-hover:scale-105 duration-300">
              <div className="size-16 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-4 shadow-inner">
                <span className="material-symbols-outlined text-4xl">
                  cloud_upload
                </span>
              </div>
              <p className="mb-2 text-sm text-foreground font-medium">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-muted-foreground">
                PDF files only (MAX. 5MB)
              </p>
            </div>
            {/* Visual indicator for hover state handled by CSS helper or just default interactions */}
          </div>
        </div>

        {/* Job Description Text Area - Only for compare mode */}
        {isCompareMode && (
          <div className="flex flex-col gap-3 h-full animate-fade-in">
            <label className="text-sm font-semibold text-muted-foreground">
              Job Description
            </label>
            <div className="relative flex-1">
              <textarea
                className="w-full h-64 p-4 rounded-xl border border-input bg-card text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary focus:outline-none resize-none transition-all text-sm leading-relaxed"
                placeholder="Paste the full job description here to compare keywords..."
              ></textarea>
              <div className="absolute bottom-3 right-3 text-xs text-muted-foreground bg-black/20 backdrop-blur-sm px-2 py-1 rounded">
                0 characters
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="px-6 py-5 bg-black/20 border-t border-white/5 flex justify-end">
        <button
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className={`
            w-full md:w-auto flex items-center justify-center gap-2 
            bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 
            text-white font-bold py-3 px-8 rounded-xl 
            shadow-lg shadow-primary/25 transition-all 
            hover:shadow-primary/40 active:scale-[0.98] 
            disabled:opacity-70 disabled:cursor-not-allowed
            ${isAnalyzing ? "animate-pulse" : ""}
          `}
        >
          {isAnalyzing ? (
            <>
              <span className="material-symbols-outlined animate-spin text-[20px]">
                sync
              </span>
              Analyzing...
            </>
          ) : (
            <>
              <span className="material-symbols-outlined">analytics</span>
              {isCompareMode ? "Analyze & Compare" : "Calculate Score"}
            </>
          )}
        </button>
      </div>
    </div>
  );
}
