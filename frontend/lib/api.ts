export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiClient {
  static async analyzeResume(
    file: File,
    jobDescription: string | null,
    mode: "resume_ats" | "resume_vs_jd"
  ) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("mode", mode);

    if (jobDescription) {
      formData.append("job_description", jobDescription);
    }

    const response = await fetch(`${API_BASE_URL}/ats_score/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Analysis failed");
    }

    return response.json();
  }
}
