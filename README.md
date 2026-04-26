# ESG and Revenue Analysis App

## Product Link / Demo
- **GitHub Repository:** [https://github.com/yjsong337/ESG-Analysis]
- **Demo Video:** [paste your demo video link here]
- **Live App:** [https://esg-analysis-4l6zrnssdsc3gxsmselgsb.streamlit.app/]

## 1. Problem and User
This project explores how ESG indicators may be associated with company revenue through an interactive Streamlit app.  
The intended users are ESG-focused investors, corporate strategy managers, and sustainability analysts who want a simple tool for exploratory business analysis.

## 2. Data
This app uses a processed dataset: `ESG_sta1_selected_one_company_per_region.csv`.

- **Original data/source:** `ESG_sta1.csv`
- **Access date:** 2026.4.23
- **Processed dataset used in this app:** `ESG_sta1_selected_one_company_per_region.csv`
- **Key fields:** company name, region, year, revenue, ESG overall score, environmental score, social score, governance score

The processed dataset was created by selecting one representative company from each region while keeping all available yearly observations for that company. This was done to make the analysis and the Streamlit tool more focused and manageable.

## 3. Methods
The project was developed in Python and presented through a local Streamlit app.

Main Python steps:
- load the processed CSV dataset with pandas
- clean and inspect the selected variables
- calculate descriptive statistics and average ESG benchmarks
- compare ESG indicators and revenue across regions and years
- visualise trends and patterns using matplotlib
- build interactive user inputs in Streamlit
- provide simple exploratory estimation from ESG score to revenue and from revenue to ESG score
- generate user-friendly summaries, comparisons, and ranking outputs

## 4. Key Findings
- The selected sample shows noticeable variation in both ESG performance and revenue across regions.
- Companies above the average ESG overall score may show different revenue patterns from those below the average ESG level.
- ESG indicators can be useful as a reference point for exploratory investment and strategy discussion.
- The relationship between ESG indicators and revenue is not perfectly consistent across all observations and should be interpreted carefully.
- The app is suitable for exploratory analysis, but it does not prove causation.

## 5. How to Run
After downloading or cloning this repository, run the app locally.

### Required files
- `app.py`
- `requirements.txt`
- `ESG_sta1_selected_one_company_per_region.csv`
- `ESG_sta1.csv`

### Install packages
```bash
pip install -r requirements.txt
