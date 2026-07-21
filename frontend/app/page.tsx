"use client";

import { useState } from "react";
import { Header } from "@/components/landing/Header";
import { ModeSelection } from "@/components/landing/ModeSelection";
import { UploadSection } from "@/components/landing/UploadSection";
import { ResultsSection } from "@/components/landing/ResultsSection";
import { Footer } from "@/components/landing/Footer";
import { ApiClient } from "@/lib/api";

export default function Dashboard() {
  const [selectedMode, setSelectedMode] = useState<
    "score" | "compare" | "create-resume"
  >("compare");
  const [showResults, setShowResults] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!file) {
      alert("Please upload a resume first.");
      return;
    }

    if (selectedMode === "compare" && !jobDescription) {
      alert("Please enter a job description.");
      return;
    }

    setIsAnalyzing(true);
    setShowResults(false);

    try {
      const modeMap = {
        score: "resume_ats",
        compare: "resume_vs_jd",
        "create-resume": "resume_ats", // Fallback or handle appropriately
      };

      const results = await ApiClient.analyzeResume(
        file,
        selectedMode === "compare" ? jobDescription : null,
        modeMap[selectedMode] as "resume_ats" | "resume_vs_jd"
      );

      setAnalysisResults(results);
      setShowResults(true);

      // Scroll to results
      setTimeout(() => {
        document
          .getElementById("results-section")
          ?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (error) {
      console.error("Analysis failed:", error);
      alert("Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col bg-background font-sans text-foreground selection:bg-primary/30">
      <Header />

      <main className="flex-1 flex flex-col items-center px-4 py-8 lg:px-8">
        <div className="w-full max-w-5xl flex flex-col gap-8">
          <div className="flex flex-col items-center gap-4 text-center py-6">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 animate-fade-in">
              Optimize Your Resume
            </h1>
            <p
              className="text-muted-foreground text-lg max-w-2xl animate-fade-in"
              style={{ animationDelay: "0.1s" }}
            >
              Tailor your resume to any job description with AI-powered insights
              and ATS scoring.
            </p>
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <ModeSelection
              selectedMode={selectedMode}
              onSelectMode={setSelectedMode}
            />
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "0.3s" }}>
            <UploadSection
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
              mode={selectedMode}
              onFileSelect={setFile}
              onJobDescriptionChange={setJobDescription}
            />
          </div>

          {showResults && analysisResults && (
            <div id="results-section" className="animate-slide-up">
              <ResultsSection results={analysisResults} />
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
