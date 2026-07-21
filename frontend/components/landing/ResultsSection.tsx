interface ResultsSectionProps {
  results: any;
}

export function ResultsSection({ results }: ResultsSectionProps) {
  if (!results) return null;

  // Check if it's the Comparison (Score) Result
  if ("ats_score" in results) {
    const { ats_score, keyword_match, formatting_score } = results;
    const {
      matched_count,
      total_keywords,
      matched_keywords,
      missing_keywords,
    } = keyword_match;
    const matchPercentage =
      Math.round((matched_count / total_keywords) * 100) || 0;

    return (
      <div className="space-y-6 animate-slide-up pb-10">
        <div className="flex items-center justify-between">
          <h3 className="text-2xl font-bold text-foreground">
            Analysis Results
          </h3>
          <span className="text-sm font-medium text-muted-foreground bg-secondary/20 px-3 py-1 rounded-full border border-secondary/20">
            Scanned just now
          </span>
        </div>

        {/* Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Score */}
          <div className="md:col-span-1 glass-panel rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-3 opacity-5 group-hover:opacity-10 transition-opacity">
              <span className="material-symbols-outlined text-9xl">
                verified
              </span>
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
                  strokeDasharray={`${ats_score}, 100`}
                  strokeLinecap="round"
                  strokeWidth="3"
                ></path>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-4xl font-black text-foreground">
                  {ats_score}%
                </span>
                <span className="text-xs font-semibold text-emerald-500">
                  {ats_score >= 70
                    ? "Good Match"
                    : ats_score >= 40
                    ? "Average"
                    : "Poor Match"}
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
                    {matched_count}
                    <span className="text-lg text-muted-foreground font-medium">
                      /{total_keywords}
                    </span>
                  </p>
                </div>
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                  <span className="material-symbols-outlined">
                    check_circle
                  </span>
                </div>
              </div>
              <div className="w-full bg-muted/30 rounded-full h-2 mt-4">
                <div
                  className="bg-emerald-500 h-2 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"
                  style={{ width: `${matchPercentage}%` }}
                ></div>
              </div>
            </div>

            {/* Missing Card */}
            <div className="glass-panel rounded-2xl p-5 flex flex-col justify-between hover:bg-card/60 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Missing Critical
                  </p>
                  <p className="text-3xl font-bold text-foreground">
                    {missing_keywords.length}
                  </p>
                </div>
                <div className="p-2 rounded-lg bg-destructive/10 text-destructive">
                  <span className="material-symbols-outlined">warning</span>
                </div>
              </div>
              <div className="w-full bg-muted/30 rounded-full h-2 mt-4">
                <div
                  className="bg-destructive h-2 rounded-full shadow-[0_0_10px_rgba(239,68,68,0.5)]"
                  style={{
                    width: `${
                      (missing_keywords.length / (total_keywords || 1)) * 100
                    }%`,
                  }}
                ></div>
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
                    Your resume formatting score is {formatting_score}/100.
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
          <details
            className="group glass-panel rounded-xl overflow-hidden"
            open={matched_keywords.length > 0}
          >
            <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors list-none">
              <div className="flex items-center gap-3">
                <div className="size-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
                <h4 className="font-semibold text-foreground">
                  Matched Keywords
                </h4>
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-muted/30 text-muted-foreground">
                  {matched_keywords.length}
                </span>
              </div>
              <span className="material-symbols-outlined transition-transform duration-300 group-open:rotate-180 text-muted-foreground">
                expand_more
              </span>
            </summary>
            {matched_keywords.length > 0 && (
              <div className="px-4 pb-4 pt-0">
                <div className="flex flex-wrap gap-2 pt-2 border-t border-white/5">
                  {matched_keywords.map((keyword: string) => (
                    <span
                      key={keyword}
                      className="px-3 py-1 rounded-md text-sm font-medium bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </details>

          {/* Missing */}
          <details
            className="group glass-panel rounded-xl overflow-hidden"
            open={missing_keywords.length > 0}
          >
            <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors list-none">
              <div className="flex items-center gap-3">
                <div className="size-2 rounded-full bg-destructive shadow-[0_0_8px_rgba(239,68,68,0.6)]"></div>
                <h4 className="font-semibold text-foreground">
                  Missing Keywords
                </h4>
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-muted/30 text-muted-foreground">
                  {missing_keywords.length}
                </span>
              </div>
              <span className="material-symbols-outlined transition-transform duration-300 group-open:rotate-180 text-muted-foreground">
                expand_more
              </span>
            </summary>
            {missing_keywords.length > 0 && (
              <div className="px-4 pb-4 pt-0">
                <div className="flex flex-col gap-2 pt-2 border-t border-white/5">
                  {missing_keywords.map((keyword: string) => (
                    <div
                      key={keyword}
                      className="flex items-center justify-between p-2 rounded-lg bg-destructive/5 border border-destructive/10"
                    >
                      <span className="text-sm font-medium text-destructive">
                        {keyword}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </details>
        </div>
      </div>
    );
  }

  // Check if it's the Extraction Result
  if ("personal_information" in results) {
    const { personal_information, skills } = results;
    return (
      <div className="space-y-6 animate-slide-up pb-10">
        <div className="flex items-center justify-between">
          <h3 className="text-2xl font-bold text-foreground">
            Extracted Profile
          </h3>
          <span className="text-sm font-medium text-muted-foreground bg-secondary/20 px-3 py-1 rounded-full border border-secondary/20">
            Processed just now
          </span>
        </div>

        <div className="glass-panel rounded-2xl p-6">
          <h4 className="text-lg font-semibold mb-4 text-primary">
            Personal Information
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {Object.entries(personal_information).map(([key, value]) => (
              <div key={key} className="flex flex-col">
                <span className="text-muted-foreground capitalize">
                  {key.replace("_", " ")}
                </span>
                <span className="text-foreground font-medium">
                  {String(value || "Not found")}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-6">
          <h4 className="text-lg font-semibold mb-4 text-primary">Skills</h4>
          <div className="space-y-4">
            <div>
              <h5 className="text-sm font-medium text-muted-foreground mb-2">
                Technical
              </h5>
              <div className="flex flex-wrap gap-2">
                {skills.technical_skills &&
                skills.technical_skills.length > 0 ? (
                  skills.technical_skills.map((skill: string) => (
                    <span
                      key={skill}
                      className="px-3 py-1 rounded-md text-sm font-medium bg-secondary/10 text-secondary-foreground border border-secondary/20"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-muted-foreground italic">
                    No technical skills extracted
                  </span>
                )}
              </div>
            </div>
            <div>
              <h5 className="text-sm font-medium text-muted-foreground mb-2">
                Soft Skills
              </h5>
              <div className="flex flex-wrap gap-2">
                {skills.soft_skills && skills.soft_skills.length > 0 ? (
                  skills.soft_skills.map((skill: string) => (
                    <span
                      key={skill}
                      className="px-3 py-1 rounded-md text-sm font-medium bg-secondary/10 text-secondary-foreground border border-secondary/20"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-muted-foreground italic">
                    No soft skills extracted
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 text-center text-muted-foreground">
      Unknown result format
    </div>
  );
}
