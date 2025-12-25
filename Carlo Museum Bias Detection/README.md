# Carlos Museum Artifact Bias Detector

## Summary

This project analyzes cultural and linguistic bias in artifact descriptions from the Michael C. Carlos Museum. It combines a multi‑label BERT classifier with a fine‑tuned GPT‑style model to detect four bias categories—**Subjective**, **Gender**, **Jargon**, and **Social**—and propose clearer, more inclusive rewrites.

## Scope of This Repository

This repository documents the full bias‑detection pipeline and the tools built around it. The original fine‑tuned GPT model was hosted on a private account that is no longer active, so the exact chatbot can’t be queried at the moment. The code and artifacts here act as a blueprint for recreating the system on a new LLM backend.
--
## Team Contributions

This cohort’s work focused on:

- **Data engineering**
  - Building a unified artifact dataset by joining museum tables on `ObjectID` and standardizing text fields.
  - Producing cleaned CSVs used for annotation, evaluation, and model training.

- **Annotation and evaluation**
  - Defining and applying labels for four bias types (Subjective, Gender, Jargon, Social).
  - Comparing manual labels, BERT predictions, and GPT outputs using accuracy, F1, and partial‑match metrics.

- **LLM integration**
  - Designing JSONL training conversations for a GPT‑style model that explains and rewrites biased text.
  - Implementing command‑line chat tools and batch scripts that call the model, parse its responses into binary labels, and write structured outputs.

- **Analysis and visualization**
  - Creating R and Python scripts to visualize bias distributions, compare models, and explore geographic patterns.

The core BERT model was inherited from earlier work and is evaluated and extended here rather than trained from scratch.
--
## Directory Guide

### Root

- `clean_data.py` – creates the cleaned, merged artifact dataset from raw museum tables.  
- `compile_annotations.py` – compiles and sanity‑checks manual bias annotations.  
- `requirements.txt` – Python dependencies.  
- `AI Data Lab Final _MCCM group 4 .pptx`, `MCCM M4 DataLab.pdf` – slides and poster summarizing problem, methods, and curator workflow.

### `bert/` – Multi‑Label Bias Classifier (Inherited)

- `bert.ipynb` – notebook for fine‑tuning and evaluating the multi‑label BERT bias classifier.  
- `preprocess.py` – converts annotated CSV data into model‑ready input.  
- `cm/`, `logs/`, `test_accuracy.txt` – saved models, training logs, and summary metrics.

### `chatgpt/` – GPT Assistant and Evaluation Tools

- `GPT_Chatbox MI` – interactive chat interface for the fine‑tuned GPT‑style model.  
- `openai_chatbot(output with binary result)` – console chatbot that returns explanations plus a binary bias pattern.  
- `process_bias_detection_by_objectID.py` – runs the GPT model on artifacts selected by `ObjectID`.  
- `process_bias_detection_by_rowNumber.py` – runs the GPT model on artifacts selected by row index.  
- `Accuracy/` – scripts for per‑bias accuracy, exact match, partial accuracy, and F1 metrics.  
- `Trainging data/` – JSONL conversations used to fine‑tune the GPT‑style model as a bias explainer.

### `Data_analysis/` – Bias Analytics and Plots

- `data_analysis.R` – main R script for distributions, object‑ID bin analysis, and model comparisons.  
- `bias_proportion_byContinent` – Python script for bias proportions and counts across continents.  
- `Meger_and_group_by_Continent` – merges geography with tagged bias data and splits by continent.  
- `man_dist_bias.jpeg`, `perct_cat_bin.jpeg`, `bias count comparison.jpeg` – exported figures used in the write‑up and poster.

### `preliminary_solutions/` – Baseline Models

- `AFINN_test.py`, `hurtlex_test.py`, `perspectiveAPI_test.py`, `roBERTa-bias.py` – baseline experiments with lexicons and external APIs.  
- `*_test_output.csv` – corresponding outputs from these baselines.

### `vale_test/` and Other Helpers

- Additional tests and scratch scripts created during exploration.
--
## End‑to‑End Pipeline

1. **Ingest and clean museum data**  
   Use `clean_data.py` to load multiple museum tables, standardize schema, and join on `ObjectID`, producing a single artifact‑level dataset.

2. **Create a labeled bias dataset**  
   Manually annotate each description for Subjective, Gender, Jargon, and Social bias (0/1 per type) and compile labels with `compile_annotations.py`.

3. **Evaluate the BERT classifier**  
   Run `bert/preprocess.py` and `bert.ipynb` to generate multi‑label predictions from the inherited BERT model and record performance.

4. **Fine‑tune and connect the GPT assistant**  
   Use JSONL files in `chatgpt/Trainging data` to fine‑tune a GPT‑style model. Drive it via `GPT_Chatbox MI` or the batch scripts to obtain explanations, binary labels, and suggested rewrites.

5. **Analyze and visualize results**  
   Use `Data_analysis/data_analysis.R` and the continent scripts to compare manual, BERT, and GPT outputs and to explore where and how bias appears across the collection.
--
## Reuse and Extension

Because the original fine‑tuned GPT model is tied to an inactive account, anyone who wants a running system should:

1. Connect to a new LLM endpoint (hosted or open‑source).  
2. Reuse the cleaned/annotated datasets, JSONL training format, and scripts in `chatgpt/`, updating only the model identifier and authentication.  
3. Optionally retrain or replace the BERT classifier in `bert/` with a newer encoder model.
--
## Contributions

This project originated as a student collaboration with the Michael C. Carlos Museum. 

Team:

Jessie Ni,
Mori Schacter,
Kultum Lhabaik,
Hamza Alkadir,

## License

Unless otherwise noted in individual files, this repository is released under the **MIT License**. You are free to use, modify, and distribute the code with appropriate attribution. See `LICENSE` for full details.
