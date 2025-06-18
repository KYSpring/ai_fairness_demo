# README

## Project Overview
This project includes two callable functions:
1. **Call API for Data Processing** - `modify_and_run`
2. **Call Stata for Data Analysis** - `main`

## Environment Requirements

This project requires the installation of the following dependencies:

### Stata Dependencies

Stata 18 must be installed locally, along with the necessary packages in Stata:

```stata
ssc install reghdfe
ssc install ftools
```

### Python Dependencies

The following Python libraries are required for this project:

- stata_setup (for interacting with Stata)

  For deploying pystata, please refer to the official documentation（https://www.stata.com/python/pystata18/notebook/Magic%20Commands1.html）

- pandas(for data processing)

- numpy(for numerical computations)

- scipy.stats.binom(for statistical calculations)

## Usage Example

### 1. Call API for Data Processing (`modify_and_run`)
#### Input Parameters Format
- `file_path` (str): Path to the Python file that needs modification.
- `new_values` (dict): Configuration values to be updated, including:
  - `OPENROUTER_API_KEY` (str)
  - `MODEL_NAME` (str)
  - `API_URL` (str)
  - `providers` (list[str])
  - `output_dir` (str)

#### Example Usage
```python
file_path = "/Users/yuki/Desktop/batch/DeepSeek_R1_Example.py"

new_values = {
  "OPENROUTER_API_KEY": "yourAPIkey",
  "MODEL_NAME": "deepseek/deepseek-r1:free",
  "API_URL": "https://openrouter.ai/api/v1/chat/completions",
  "providers": ["Azure", "Chutes"],
  "output_dir": "/Users/～/output_for_experiment/"
}

modify_and_run(file_path, new_values)
```

The judgment predictions obtained from the LLMs will be saved in the output_dir path specified.

### 2. Call Stata for Data Analysis (`main`)

#### Input Parameters Format

- `model` (str): The name of the model to be processed.
- `path_base` (str): The base path of the local dataset.
- `output_for_experiment_dir` (str): Directory where the results generated from LLMs API calls are saved.

#### Example Usage

```python
path_base = r"/Users/～/law_ethnics"
model = "qwen25_7b_t0"
output_for_experiment_dir = r"/Users/～/output_for_experiment_t0"

json_Consistency, json_main_p0_1, json_main_P_N, json_inaccuracy_p0_1, json_inaccuracy_P_N, df_dict = main(path_base, model, output_for_experiment_dir)
```

### Output Format

- `json_Consistency` : JSON data related to Part I: Consistency Analysis table.

- `json_main_p0_1` : JSON data for Part II: Bias Analysis table, with labels having a significance level < 0.1.

- `json_main_P_N` : JSON data for Part II: Bias Analysis, specific classification results for labels showing significant bias.

- `json_inaccuracy_p0_1` : JSON data for Part III: Unfair Inaccuracy Analysis table, with labels having a significance level < 0.1.

- `json_inaccuracy_P_N` : JSON data for Part III: Unfair Inaccuracy Analysis, specific classification results for labels showing significant unfair inaccuracy.

- `df_dict` : JSON data required for the textual part.

  Example:

  ```json
  [
      {
          "model": "llama3_1",   // Model name
          "main_p0_1value": 2.1403870629445287e-14,   // Part II: Probability of systematic bias
          "inaccuracy_p0_1value": 2.1403870629445287e-14,  // Part III: Probability of unfair inaccuracy
          "main_p0_05value": 2.7161306139462403e-17,
          "inaccuracy_p0_05value": 2.7161306139462403e-17,
          "main_p0_01value": 3.812785434269691e-22,
          "inaccuracy_p0_01value": 3.812785434269691e-22,
          "avg_valid_id_ratio": 0.1743215495253777,  // Average percentage of samples with inconsistency per label
          "avg_mae": 61.44939024123505,  // Weighted average MAE
          "avg_mape": 142.9436988284994,  // Weighted average MAPE 
          "main_total_biased_labels": 31,  // Part II: Number of labels with significant bias
          "inaccuracy_total_biased_labels": 21   // Part III: Number of labels with significant unfair inaccuracy
      }
  ]
  ```

##  Stata Analysis Output
### Stata Log Output
The log files generated from the Stata analysis will be saved in the following directory:`path_base/model/log`。

### Figure Output:
The images from your Stata analysis will be saved in`path_base/model/figure`。

### CSV and JSON Output
The analysis results will be saved in `output_dir` in both CSV and JSON formats.

- Bias_Analysis_P.csv:Labels with a significance < 0.1 from the main regression analysis.
- Bias_Analysis_Pnum.csv:Detailed classification results for labels showing significant bias from the main regression.
- crime_clustered_P.csv:Labels with a significance < 0.1 from the clustered crime analysis.
- crime_clustered_Pnum.csv:Detailed classification results for labels showing significant bias from the clustered crime analysis.
- df_dict.json:Overall analysis results, including weighted average MAE, MAPE, and sample validity rates.
- inaccuracy_p.csv: Labels with a significance < 0.1 from the inaccuracy analysis.
- inaccuracy_results_Pnum.csv:Detailed classification results for labels showing significant unfair inaccuracy.
- original_main_P.csv:Labels with a significance < 0.1 from the original main regression.
- original_main_Pnum.csv:Detailed classification results for labels showing significant bias from the original main regression.
- output_Consistency.csv:Consistency analysis table showing overall results.
- post_2014_P.csv:Labels with a significance < 0.1 for the post-2014 analysis.
- post_2014_Pnum.csv:Detailed classification results for labels showing significant bias for the post-2014 analysis.
- result.json:Raw data exported from Stata after the analysis.
- results_special_P.csv: Labels with a significance < 0.1 for the special crime regression.
- results_special_Pnum.csv:Detailed classification results for labels showing significant bias for the special crime regression.
- robust_standard_errors_P.csv:Labels with a significance < 0.1 from the robust standard errors analysis.
- robust_standard_errors_Pnum.csv:Detailed classification results for labels showing significant bias from the robust standard errors analysis.
- robustness_lgxq_llm_full_P.csv:Labels with a significance < 0.1 for the robustness of lgxq_llm_full analysis.
- robustness_lgxq_llm_full_Pnum.csv:Detailed classification results for labels showing significant bias from the robustness of lgxq_llm_full analysis.
