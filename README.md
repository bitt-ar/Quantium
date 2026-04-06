# Quantium Retail Analytics

## Overview

Quantium Retail Analytics is a comprehensive data analysis project focused on customer segmentation, purchase behavior analysis, and experimental design in the retail sector. This project combines advanced analytics techniques with an interactive Streamlit dashboard to provide actionable insights into customer purchasing patterns and the effectiveness of promotional trials.

## Projects & Resources

- **Interactive Dashboard**: [Quantium Data Streamlit App](https://quantium-data.streamlit.app/)
- **Kaggle - Task 1**: [Quantium-1 Customer Analytics](https://www.kaggle.com/code/reizoz/quantium-1)
- **Kaggle - Task 2**: [Quantium-2 Uplift Testing](https://www.kaggle.com/code/reizoz/quantium-2)

## Project Structure

The project is organized into two main tasks:

### Task 1: Data Preparation and Customer Analytics
- Exploratory data analysis of transaction and customer behavior data
- Data cleaning and preprocessing
- Customer segmentation based on lifestage and customer tier
- Visual analysis of purchasing patterns and customer demographics

### Task 2: Experimentation and Uplift Testing
- Monthly store-level aggregation and metrics computation
- Control store selection using advanced matching techniques
- A/B testing framework for evaluating promotional campaigns
- Statistical analysis of treatment effects and uplift measurement

## Key Analysis Techniques

### Data Processing & Cleaning

- **Data Type Optimization**: Conversion of categorical variables to reduce memory footprint and improve computational efficiency
- **Feature Engineering**: Creation of derived features such as age groups and family status from raw categorical variables
- **Missing Value Handling**: Systematic detection and treatment of null values in transaction and customer datasets

### Customer Segmentation

- **Hierarchical Segmentation**: Multi-dimensional customer stratification based on:
  - Customer Tier: Premium, Mainstream, Budget
  - Life Stage: Young Singles/Couples, Young Families, Older Singles/Couples, Mid-age Singles/Couples, New Families, Older Families, Retirees
  - Age Group: Young, Mid-age, Older, Retirees
  - Family Status: No Family, Family, Retirees

- **Behavioral Analysis**: Quantification of segment-level purchase frequency, transaction value, and spending patterns

### Control Store Selection (Propensity Score Matching)

The control selection methodology employs a dual-criterion similarity score:

1. **Pearson Correlation Coefficient**: Measures trend alignment between stores, capturing whether both stores exhibit similar seasonal and temporal dynamics
2. **Normalized Magnitude Distance**: Assesses absolute sales level compatibility, ensuring the control store operates at a comparable scale

The composite similarity score is calculated as:

**Similarity Score = (Correlation × 0.5) + (Magnitude Score × 0.5)**

This balanced approach ensures control stores are selected based on both behavioral similarity and operational comparability.

### Time Series & Store Aggregation

- **Monthly Resampling**: Conversion of transaction-level data to monthly store-level metrics
- **Key Metrics Computation**:
  - Total Sales: Aggregated revenue per store-month
  - Customer Count: Unique loyalty card holders per store-month
  - Transaction Volume: Total transactions per store-month
  - Average Transaction Value: Sales per transaction (proxy for basket size)

- **Data Quality Filtering**: Retention of only stores with complete 12-month records to ensure data consistency

### Experimental Design & Statistical Testing

- **Treatment-Control Comparison**: Pre-trial baseline establishment and post-trial performance evaluation
- **Difference-in-Differences (DiD) Framework**: Evaluation of causal treatment effects by comparing the change in treatment stores relative to the change in control stores
- **Statistical Hypothesis Testing**: Quantification of p-values and confidence intervals for uplift estimates
- **Confounding Control**: Use of matched control stores to isolate the causal impact of promotional interventions

### Data Visualization

- **Interactive Dashboards**: Streamlit-based visualizations for real-time data exploration
- **Time Series Plots**: Temporal trend analysis for sales, customer counts, and transaction patterns
- **Distribution Analysis**: Histograms, box plots, and violin plots for univariate and stratified distributions
- **Correlation Heatmaps**: Identification of relationships between customer segments and purchase behavior

## Technologies & Libraries

- **Python 3.x**: Core programming language
- **Pandas**: Data manipulation and aggregation
- **NumPy**: Numerical computations
- **Matplotlib & Seaborn**: Statistical visualization
- **Plotly**: Interactive and publication-quality graphics
- **Streamlit**: Web application framework for interactive dashboards

## Datasets

The project utilizes two primary data sources:

1. **QVI_purchase_behaviour.csv**: Customer-level data containing loyalty card IDs, customer tier, and life stage classification (72,637 records)
2. **QVI_transaction_data.xlsx**: Transaction-level data with store IDs, transaction dates, product quantities, and sales amounts (264,836 records)

These datasets are processed and merged to create a cleaned dataset (`cleaned_data.csv`) containing transaction-level data enriched with customer attributes.

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run app.py
```

## Analysis Workflow

1. **Data Import & Exploration**: Load and inspect raw data structures
2. **Data Cleaning**: Type conversion, outlier detection, and null value treatment
3. **Feature Engineering**: Creation of aggregate and derived features
4. **Segmentation Analysis**: Customer stratification and behavior quantification
5. **Control Selection**: Identification of matched comparison stores
6. **Experimental Evaluation**: Causal inference and uplift measurement
7. **Visualization & Reporting**: Interactive dashboards and statistical summaries

## Key Insights & Outcomes

The analysis generates actionable insights including:

- Identification of high-value customer segments and their purchasing drivers
- Quantification of promotional effectiveness through controlled experimentation
- Store-level performance benchmarking and outlier detection
- Temporal patterns in customer behavior and seasonal trends
- Evidence-based recommendations for targeted marketing and pricing strategies

## Contact & Attribution

For questions or collaboration, refer to the Kaggle notebooks linked above.

---

**Last Updated**: April 2026
