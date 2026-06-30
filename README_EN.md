English | [中文](README.md)

# 📊 Customer Service Sentiment Analysis System

Upload Feishu-exported customer service chat logs to generate data visualization reports + AI in-depth analysis with one click.

## Features

- **Auto-parse chat logs** (Feishu export format)
- **13 consultation category** auto-classification and ranking
- **Keyword frequency** statistics with sentiment classification
- **Negative sentiment deep analysis** with dialogue samples
- **Daily trends**, pre-sale vs. after-sale comparison
- **One-click PDF export** (7-page charts)
- **Optional DeepSeek AI** for 8-module in-depth analysis (appended to PDF)
- **AI prompt customization**: Custom analysis modules, multi-round analysis, extra instructions
- **Auto font download**: First run automatically downloads LXGW WenKai font for Chinese PDF rendering

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. Open the Streamlit page in your browser
2. Upload chat log file (.log / .txt)
3. Browse interactive charts across 5 tabs:
   - 📈 Daily Trends
   - 🔑 Keyword Analysis
   - ⚠️ Negative Deep Dive
   - 📋 Scenario Rankings
   - 📥 Export Report
4. Switch to "Export Report" tab to download PDF

### AI Analysis (Optional)

Enter your DeepSeek API Key in the sidebar to enable "Full Report" generation, which calls AI to produce 8 modules of in-depth analysis text.

### AI Prompt Configuration (Sidebar)

- **Analysis rounds**: 1-10 rounds, each deepens the previous conclusions
- **Custom analysis modules**: Add, edit, delete, or restore default modules (8 default modules included)
- **Extra instructions**: Append custom requirements to guide AI analysis

## File Structure

- `app.py` — Streamlit web interface
- `parser.py` — Chat log parsing engine
- `visualizer.py` — Charts and PDF generation engine (with auto font download)
- `requirements.txt` — Dependencies

## Font Handling

The system uses **LXGW WenKai** (霞鹜文楷) font for Chinese PDF rendering. On first run, the font file (~18MB) is automatically downloaded from GitHub Releases. No manual setup required.

If automatic download fails, manually download from:
https://github.com/lxgw/LxgwWenKai/releases/download/v1.501/LXGWWenKai-Regular.ttf

Place the file in the project root directory.

## Notes

- Designed for Feishu-exported chat log format
- Keyword-based sentiment analysis; may not detect sarcasm or memes
- Delete `__pycache__/` folder after updating source files
