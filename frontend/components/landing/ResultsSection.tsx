export function ResultsSection() {
  return (
    <div className="space-y-6 animate-slide-up pb-10">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold text-foreground">Analysis Results</h3>
        <span className="text-sm font-medium text-muted-foreground bg-secondary/20 px-3 py-1 rounded-full border border-secondary/20">
          Scanned just now
        </span>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main Score */}
        <div className="md:col-span-1 glass-panel rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 opacity-5 group-hover:opacity-10 transition-opacity">
            <span className="material-symbols-outlined text-9xl">verified</span>
          </div>
          <h4 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider">
            ATS Match Score
          </h4>
          <div className="relative size-40 hover:scale-105 transition-transform duration-500 ease-out">
            <svg
              className="size-full -rotate-90"
              viewBox="0 0 36 36"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                className="text-muted/20"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
              ></path>
              <path
                className="text-primary drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeDasharray="85, 100"
                strokeLinecap="round"
                strokeWidth="3"
              ></path>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center flex-col">
              <span className="text-4xl font-black text-foreground">85%</span>
              <span className="text-xs font-semibold text-emerald-500">
                Good Match
              </span>
            </div>
          </div>
        </div>

        {/* Stats & Insights */}
        <div className="md:col-span-2 grid grid-cols-2 gap-4">
          {/* Keyword Card */}
          <div className="glass-panel rounded-2xl p-5 flex flex-col justify-between hover:bg-card/60 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">
                  Keywords Matched
                </p>
                <p className="text-3xl font-bold text-foreground">
                  12
                  <span className="text-lg text-muted-foreground font-medium">
                    /15
                  </span>
                </p>
              </div>
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                <span className="material-symbols-outlined">check_circle</span>
              </div>
            </div>
            <div className="w-full bg-muted/30 rounded-full h-2 mt-4">
              <div className="bg-emerald-500 h-2 rounded-full w-[80%] shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>
          </div>

          {/* Missing Card */}
          <div className="glass-panel rounded-2xl p-5 flex flex-col justify-between hover:bg-card/60 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">
                  Missing Critical
                </p>
                <p className="text-3xl font-bold text-foreground">3</p>
              </div>
              <div className="p-2 rounded-lg bg-destructive/10 text-destructive">
                <span className="material-symbols-outlined">warning</span>
              </div>
            </div>
            <div className="w-full bg-muted/30 rounded-full h-2 mt-4">
              <div className="bg-destructive h-2 rounded-full w-[20%] shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div>
            </div>
          </div>

          {/* Formatting Card */}
          <div className="col-span-2 glass-panel rounded-2xl p-5 flex items-center justify-between hover:bg-card/60 transition-colors">
            <div className="flex gap-4 items-center">
              <div className="p-3 rounded-xl bg-blue-500/10 text-primary">
                <span className="material-symbols-outlined">
                  format_align_left
                </span>
              </div>
              <div>
                <p className="text-base font-bold text-foreground">
                  Formatting Check
                </p>
                <p className="text-sm text-muted-foreground">
                  Your resume is parsable by 98% of ATS systems.
                </p>
              </div>
            </div>
            <button className="text-sm font-semibold text-primary hover:text-blue-400 cursor-pointer transition-colors">
              View Report
            </button>
          </div>
        </div>
      </div>

      {/* Accordions */}
      <div className="flex flex-col gap-4">
        {/* Matched */}
        <details className="group glass-panel rounded-xl overflow-hidden" open>
          <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors list-none">
            <div className="flex items-center gap-3">
              <div className="size-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
              <h4 className="font-semibold text-foreground">
                Matched Keywords
              </h4>
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-muted/30 text-muted-foreground">
                12
              </span>
            </div>
            <span className="material-symbols-outlined transition-transform duration-300 group-open:rotate-180 text-muted-foreground">
              expand_more
            </span>
          </summary>
          <div className="px-4 pb-4 pt-0">
            <div className="flex flex-wrap gap-2 pt-2 border-t border-white/5">
              {[
                "Python",
                "SQL",
                "Data Analysis",
                "Machine Learning",
                "Project Management",
                "Communication",
              ].map((keyword) => (
                <span
                  key={keyword}
                  className="px-3 py-1 rounded-md text-sm font-medium bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        </details>

        {/* Partial */}
        <details className="group glass-panel rounded-xl overflow-hidden">
          <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors list-none">
            <div className="flex items-center gap-3">
              <div className="size-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.6)]"></div>
              <h4 className="font-semibold text-foreground">Partial Matches</h4>
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-muted/30 text-muted-foreground">
                2
              </span>
            </div>
            <span className="material-symbols-outlined transition-transform duration-300 group-open:rotate-180 text-muted-foreground">
              expand_more
            </span>
          </summary>
          <div className="px-4 pb-4 pt-0">
            <div className="flex flex-wrap gap-2 pt-2 border-t border-white/5">
              <span className="px-3 py-1 rounded-md text-sm font-medium bg-amber-500/10 text-amber-500 border border-amber-500/20">
                React (Context found, skill implied)
              </span>
            </div>
          </div>
        </details>

        {/* Missing */}
        <details className="group glass-panel rounded-xl overflow-hidden" open>
          <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors list-none">
            <div className="flex items-center gap-3">
              <div className="size-2 rounded-full bg-destructive shadow-[0_0_8px_rgba(239,68,68,0.6)]"></div>
              <h4 className="font-semibold text-foreground">
                Missing Keywords
              </h4>
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-muted/30 text-muted-foreground">
                3
              </span>
            </div>
            <span className="material-symbols-outlined transition-transform duration-300 group-open:rotate-180 text-muted-foreground">
              expand_more
            </span>
          </summary>
          <div className="px-4 pb-4 pt-0">
            <div className="flex flex-col gap-2 pt-2 border-t border-white/5">
              <div className="flex items-center justify-between p-2 rounded-lg bg-destructive/5 border border-destructive/10">
                <span className="text-sm font-medium text-destructive">
                  Docker
                </span>
                <span className="text-xs text-muted-foreground">
                  High Importance
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-destructive/5 border border-destructive/10">
                <span className="text-sm font-medium text-destructive">
                  AWS
                </span>
                <span className="text-xs text-muted-foreground">
                  Medium Importance
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-destructive/5 border border-destructive/10">
                <span className="text-sm font-medium text-destructive">
                  Kubernetes
                </span>
                <span className="text-xs text-muted-foreground">
                  Low Importance
                </span>
              </div>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}
