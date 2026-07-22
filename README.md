# Entertainment Media Analysis

> A Streamlit app that turns your Goodreads, Letterboxd, and Steam exports into dashboards and insights.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)
![Stars](https://img.shields.io/github/stars/HighnessAtharva/Media-Analysis?style=flat-square)

<img width="1604" src="https://raw.githubusercontent.com/HighnessAtharva/Media-Analysis/main/assets/screengrabs/0.png">

## Overview

Upload your export from a media platform and get back charts, dashboards, and stats about your reading, watching, and gaming habits. Everything runs locally in a Streamlit web app. No account, no upload to a server.

## Supported Platforms

- Goodreads
- Letterboxd
- Steam

## Screenshots

| 📕 Goodreads | 🍿 Letterboxd | 🎮 Steam |
|:-------------------------:|:-------------------------:|:-------------------------:|
|<img width="1604" src="https://github.com/HighnessAtharva/Media-Analysis/blob/main/assets/screengrabs/2.png?raw=true"> Dashboards | <img width="1604" src="https://github.com/HighnessAtharva/Media-Analysis/blob/main/assets/screengrabs/8.png?raw=true"> In-Depth Analysis |<img width="1604" src="https://github.com/HighnessAtharva/Media-Analysis/blob/main/assets/screengrabs/9.png?raw=true"> Stats |
|<img width="1604" src="https://github.com/HighnessAtharva/Media-Analysis/blob/main/assets/screengrabs/3.png?raw=true"> | <img width="1604" src="https://github.com/HighnessAtharva/Media-Analysis/blob/main/assets/screengrabs/7.png?raw=true">|<img width="1604" src="https://github.com/HighnessAtharva/Media-Analysis/blob/main/assets/screengrabs/10.png?raw=true">|

## Getting Started

```bash
git clone https://github.com/HighnessAtharva/Media-Analysis.git
cd Media-Analysis
python -m venv env
env\Scripts\activate        # Windows
# source env/bin/activate   # macOS / Linux
pip install -r requirements.txt
streamlit run app.py
```

Then:

1. Pick a platform from the sidebar
2. Upload your CSV, or use the sample CSVs in `pages/sample-csv`
3. Explore your data

## Project Layout

- `app.py` is the main Streamlit entry point
- `pages/` holds the code and example CSVs for each sub-page in the sidebar

## Contributing

Fork the repo, branch off `main`, commit with clear messages, and open a pull request.

## License

MIT.
