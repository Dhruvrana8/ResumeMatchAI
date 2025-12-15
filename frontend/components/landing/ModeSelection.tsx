"use client";

interface ModeSelectionProps {
  selectedMode: "score" | "compare" | "create-resume";
  onSelectMode: (mode: "score" | "compare" | "create-resume") => void;
}

export function ModeSelection({
  selectedMode,
  onSelectMode,
}: ModeSelectionProps) {
  return (
    <div className="flex justify-center w-full">
      <div className="relative inline-flex p-1.5 bg-muted/30 backdrop-blur-sm rounded-xl border border-white/5">
        {/* Animated Background Pill */}
        <div
          className={`absolute top-1.5 bottom-1.5 rounded-lg bg-card border border-white/5 shadow-sm transition-all duration-300 ease-out`}
          style={{
            left: selectedMode === "compare" ? "33.33%" : "6px",
            width: "calc(33.33% - 6px)",
            transform: selectedMode === "compare" ? "translateX(-3px)" : "none",
          }}
        />

        <button
          onClick={() => onSelectMode("score")}
          className={`
            relative z-10 flex-1 px-6 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2
            ${
              selectedMode === "score"
                ? "text-primary"
                : "text-muted-foreground hover:text-foreground"
            }
          `}
        >
          <span className="material-symbols-outlined text-[18px]">speed</span>
          Resume ATS Score
        </button>

        <button
          onClick={() => onSelectMode("compare")}
          className={`
            relative z-10 flex-1 px-6 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2
            ${
              selectedMode === "compare"
                ? "text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }
          `}
        >
          <span className="material-symbols-outlined text-[18px]">
            compare_arrows
          </span>
          Resume vs Job Description
        </button>

        <button
          onClick={() => {}}
          disabled={true}
          className={`
            relative z-10 flex-1 px-6 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2
            ${
              selectedMode === "create-resume"
                ? "create-resume"
                : "text-muted-foreground hover:text-foreground"
            }
          `}
        >
          <span className="material-symbols-outlined">lock</span>
          Create Resume
        </button>
      </div>
    </div>
  );
}
