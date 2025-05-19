# Data Labeling and Versioning System for Receipt Classification

## Project Description

This project aims to build a data labeling and versioning system for the task of classifying images as either containing a shopping receipt or not. The primary goal is to maintain versioned dataset that can be used for training machine learning models to automate receipt detection and, in the future, more granular receipt classification.

### Problem Statement

- **Stage 1:** Classify images as either containing a shopping receipt or not (binary classification).
- **Stage 2 (Future Work):** Further classify detected receipts into categories such as grocery, clothing, electronics, etc. This hierarchical approach allows for scalable annotation and model development as new categories emerge.

### Approach

- **Dataset:** The system supports importing and labeling any image dataset. You can use your own images or public datasets. // TODO: fix
- **Labeling Tool:** The project will use an open-source annotation tool (e.g., [Label Studio](https://labelstud.io/)) for efficient and user-friendly data labeling.
- **Versioning:** Labeled data is stored in a version-controlled format using DVC, ensuring reproducibility and traceability of dataset changes over time.

Further sections of this README will describe:

- The chosen annotation tool and setup instructions
- How to launch and use the labeling interface
- How dataset versioning is organized
- Example use cases and future extensions
