# Data Labeling and Versioning System for Receipt Classification

## Project Description

This project builds a data labeling and versioning system for classifying images as either containing a shopping receipt or not. The primary goal is to maintain a versioned dataset suitable for training machine learning models to automate receipt detection and, in the future, enable more granular receipt classification.

### Problem Statement

- **Stage 1:** Classify images as either containing a shopping receipt or not (binary classification).
- **Stage 2 (Future Work):** Further classify detected receipts into categories such as grocery, clothing, electronics, etc. This hierarchical approach allows for scalable annotation and model development as new categories emerge.

### Approach

- **Dataset:** The system uses S3-compatible object storage (MinIO for local development) to manage datasets. Two main buckets are used:
  - `receipts_dataset`: Stores the original, unlabelled images to be annotated. Upload images or public datasets by placing them in this bucket.
  - `receipts_labeled_dataset`: Contains the annotation files generated after labeling is complete. This bucket is used for training.
  
This setup ensures a clear separation between raw data and labeled data, supporting reproducible machine learning workflows and easy dataset management.

- **Labeling Tool:** The project uses the open-source annotation tool [Label Studio](https://labelstud.io/) for efficient and user-friendly data labeling.
  
- **Versioning:** Labeled data is version-controlled using DVC and stored in the `receipts_dvc_storage` bucket in MinIO. This ensures reproducibility and traceability of dataset changes over time, allowing tracking, sharing, and rolling back dataset versions as needed.

### Usage

#### 1. Start and Use the Annotation Tool

- In the project root directory, start all services (MinIO, PostgreSQL, Label Studio) with:

```sh
docker compose up -d
```

- Open Label Studio in a browser at [http://localhost:8080](http://localhost:8080).
- Register or log in to Label Studio.
- In Label Studio, create a new project for annotation.
- Connect the project to MinIO S3 storage:
  - Go to the project settings > Storage > Add Source Storage > S3.
  - Use the following settings for local MinIO:
    - Bucket name: `receipts_dataset`
    - S3 endpoint: `http://minio:9000`
    - Access key: `minioadmin`
    - Secret key: `minioadmin`
  - Import images from the bucket.
- Annotate images using the Label Studio interface.
- When finished, export the annotations from Label Studio to the `receipts_labeled_dataset` bucket.

#### 2. Version the Dataset with DVC

- Export the labeled dataset from Label Studio in YOLO format using the provided script:

```sh
sh export-yolo.sh {project_id}
```

- Add the exported dataset to DVC tracking:

```sh
dvc add dataset
```

- Commit the changes to git:

```sh
git add .
git commit -m "Add new labeled dataset version"
```

- Push the dataset to remote DVC storage (MinIO S3):

```sh
dvc remote add -d minio s3://receipts_dvc_storage
# If not already configured:
# dvc remote modify minio endpointurl http://localhost:9000
# dvc remote modify minio access_key_id minioadmin
# dvc remote modify minio secret_access_key minioadmin
dvc push
```

- To retrieve a specific version later:

```sh
git checkout <commit-hash>
dvc pull
```

This workflow ensures raw images, annotations, and versioned datasets are organized, reproducible, and easy to manage for machine learning projects.
