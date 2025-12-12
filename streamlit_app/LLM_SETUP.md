# 🤖 LLM Analysis Setup Guide

This guide explains how to set up and use the new AI-powered LLM Analysis feature in ResumeMatchAI.

## Prerequisites

Before using the LLM Analysis feature, you need:

1. **Python packages**: `torch`, `transformers`, `accelerate`
2. **Hugging Face API token** for accessing the Llama model

## Installation

### 1. Install Required Packages

```bash
pip install torch transformers accelerate
```

**Note**: These packages are already listed in `requirements.txt` and `pyproject.toml`.

### 2. Get Hugging Face API Token

1. Go to [Hugging Face](https://huggingface.co/)
2. Create an account or sign in
3. Go to your [Settings → Access Tokens](https://huggingface.co/settings/tokens)
4. Create a new token with "Read" permissions
5. Copy the token

### 3. Set Environment Variable

**On macOS/Linux:**

```bash
export HUGGING_FACE_API="your_token_here"
```

**On Windows:**

```cmd
set HUGGING_FACE_API=your_token_here
```

**For permanent setup**, add this to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
echo 'export HUGGING_FACE_API="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

## How to Use

1. **Start the application**:

   ```bash
   streamlit run app.py
   ```

2. **Complete steps 1-3** (Job Description → Resume Upload → ATS Analysis)

3. **Click "🤖 AI Analysis"** button on the results page

4. **Wait for analysis** - The AI will process your resume and job description (may take 1-3 minutes)

5. **Review results** - Get professional HR-level insights including:
   - Overall match percentage
   - Key strengths and weaknesses
   - Specific improvement recommendations
   - Interview preparation advice
   - Salary negotiation insights

## Troubleshooting

### "Could not load Llama model" Error

**Cause**: Missing or invalid Hugging Face API token
**Solution**:

1. Verify your API token is correct
2. Ensure the `HUGGING_FACE_API` environment variable is set
3. Try restarting your terminal/command prompt

### "Required packages not installed" Error

**Cause**: Missing PyTorch or Transformers
**Solution**:

```bash
pip install torch transformers accelerate bitsandbytes
```

### Analysis Takes Too Long

**Cause**: First-time model download and loading
**Solution**: The model needs to be downloaded once. Subsequent analyses will be faster.

### "Probability tensor contains inf, nan or element < 0" Error

**Cause**: Model generation parameters or input issues
**Solutions**:

1. **Update packages**: Ensure you have the latest versions:
   ```bash
   pip install --upgrade torch transformers accelerate bitsandbytes
   ```
2. **Check input length**: Very long resumes/job descriptions might cause issues. Try shorter versions first.
3. **Restart the application**: Sometimes model state gets corrupted.
4. **Use CPU mode**: If you have GPU issues, the model will automatically fall back to CPU.
5. **Reduce input complexity**: Remove special characters or complex formatting from your resume/job description.

### Memory Issues

**Cause**: Insufficient RAM for the model
**Solution**: The Llama 3.2-1B model requires ~2-4GB RAM. Close other applications if needed.

## Model Information

- **Model**: Meta Llama 3.2-1B
- **Purpose**: Advanced natural language understanding
- **Use Case**: Professional resume-job matching analysis
- **Size**: ~2GB download (first run only)

## Cost Information

- **Hugging Face API**: Free tier available
- **Model Access**: No additional cost for Llama 3.2-1B
- **Compute**: Runs locally on your machine

## Security Notes

- Your resume and job description data stays on your local machine
- No data is sent to external servers (except Hugging Face for model access)
- API token is used only for authentication with Hugging Face
