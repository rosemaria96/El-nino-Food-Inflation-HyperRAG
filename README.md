\# Modelling the Economic Impact of El Niño on Food Inflation in India



An econometric analysis with HyperRAG-based evidence retrieval.



This project asks whether El Niño conditions (measured by the Oceanic Niño Index, ONI) affect monthly food price changes in India. It has two parts:



1\. \*\*Quantitative analysis (R):\*\* stationarity testing, correlation and lag analysis, and incremental OLS regressions on differenced series.

2\. \*\*Qualitative evidence retrieval (Python):\*\* a hypergraph-based retrieval-augmented generation (HyperRAG) pipeline over RBI and IMD annual reports, used to interpret the econometric result.



\## Key Findings



\- Fuel price change is the dominant short-run predictor of food price change (p < .001).

\- ONI has no statistically significant direct effect once fuel price is included, in any specification, including lagged ones.

\- ONI and food price still show a significant unconditional Spearman correlation (ρ = -0.323, p < .001).

\- The preferred model is Model 1 (ONI + fuel price change), with adjusted R² of about .106.

\- Retrieved report passages describe delayed, regionally uneven, multi-stage transmission channels (rainfall deficits, reservoir levels, rabi output, input costs). A national monthly linear model is not designed to detect these.



\## Data



\*\*Quantitative (162 monthly observations, July 2012 onwards)\*\*



| Variable | Description | Source |

|---|---|---|

| `ONI` | Oceanic Niño Index | NOAA |

| `CRUDE\_BRENT` | Brent crude oil price | World Bank commodity price series |

| `USD\_INR` | Exchange rate | RBI |

| `fuel price` | Domestic fuel price index | EPWRF Time Series |

| `food price` | Domestic food price index | EPWRF Time Series |



\*\*Qualitative:\*\* 29 annual reports (14 IMD, 15 RBI), 2011–2023.



\## Methodology



\### Econometric pipeline (R)



1\. Data checks: missing values, duplicates, date parsing.

2\. Exploratory analysis: time-series plots, distributions, correlation matrix, Pearson and Spearman tests.

3\. Lag analysis: ONI lags of 1, 2, 3 and 6 months, plus a cross-correlation function.

4\. Stationarity: ADF tests on levels, then first-differencing of food price, Brent crude and fuel price.

5\. Regression: four nested OLS models (Model 0 to Model 3) of differenced food price on ONI, fuel price change, crude change and USD/INR.

6\. Diagnostics: VIF, Breusch-Pagan, Durbin-Watson, Shapiro-Wilk, and HC1 robust standard errors.

7\. Comparison: adjusted R², AIC, BIC, RMSE, MAE and nested F-tests.

8\. Time-series decomposition of the food price series.



\### HyperRAG pipeline (Python)



| Stage | Input | Output |

|---|---|---|

| Document collection | 29 annual reports | 417 candidate passages |

| Cleaning | 417 candidate passages | 240 high-quality records |

| Chunking | 240 records | 418 text chunks |

| Embedding | 418 chunks | 418 embeddings (384 dimensions) |

| FAISS indexing | 418 embeddings | 418-vector index |

| Hypergraph construction | 418 chunks | 45 hyperedges |

| Hybrid retrieval | FAISS + hypergraph expansion | 15 chunks per query |



An LLM generates a grounded answer that cites only the retrieved passages.



\## Repository Structure



> Adjust this to match your actual files.



```

.

├── dataset/

│   └── Dataset.xlsx          # monthly quantitative data

├── r/

│   └── analysis.R            # econometric analysis

├── hyperrag/

│   └── ...                   # Python retrieval pipeline

├── figures/

└── README.md

```



\## Requirements



\*\*R (4.x):\*\* `readxl`, `ggplot2`, `corrplot`, `tidyverse`, `tseries`, `car`, `lmtest`, `sandwich`, `Metrics`



\*\*Python:\*\* sentence-embedding model, FAISS, an LLM API for answer generation `\[list exact packages from your requirements file]`



\## How to Run



\*\*Econometric analysis\*\*



1\. Place `Dataset.xlsx` in the `dataset/` folder and update the file path at the top of the R script.

2\. Run the script in R or RStudio. It prints the correlation tests, ADF results, model summaries and diagnostics, and produces the plots.



\*\*HyperRAG pipeline\*\*



```bash

pip install -r requirements.txt

python <your\_script>.py

```



\## Limitations



\- The models mix variables of different integration orders. A cointegration test and an ARDL or error-correction model are the natural next step.

\- Adjusted R² is low (about .106), so most short-run food price variation is unexplained by these predictors.

\- Fuel price, food price and the exchange rate may be jointly determined, so coefficients should be read as associations, not causal effects.

\- The HyperRAG component was evaluated qualitatively. No retrieval metrics (precision, recall, nDCG) or FAISS-only ablation were run.



\## Author



Rose Maria Jose

MSc Computer Science (Data Analytics), Rajagiri College of Social Sciences (Autonomous), Kochi, Kerala



\## License



`\[Add a license, e.g. MIT, or remove this section.]`



