# Databricks notebook source
# MAGIC %md
# MAGIC # Data Drift Monitoring
# MAGIC
# MAGIC This notebook uses [Evidently AI](https://www.evidentlyai.com) to calculate data drift metrics by comparing a reference dataset (i.e. training data) and a target dataset (e.g. inference data). Data Drift metrics will be captured by MLFlow for monitoring purposes.
# MAGIC
# MAGIC This example uses an adapted version of the [`IBM HR Analytics Employee Attrition & Performance` dataset](https://www.kaggle.com/pavansubhasht/ibm-hr-analytics-attrition-dataset) available from Kaggle.
# MAGIC
# MAGIC > Ensure you have created managed Delta tables in the Hive Metastore with the associated dataset. These [instructions](https://learn.microsoft.com/en-au/azure/databricks/ingestion/add-data/upload-data#upload-the-file) can be used to learn how to upload the dataset.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Import dependencies and define constants

# COMMAND ----------

from datetime import datetime

import mlflow
import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.report import Report

# define notebook parameters
dbutils.widgets.text("reference_dataset_table",
                     "hive_metastore.default.employee_attrition_curated")
dbutils.widgets.text("target_dataset_table",
                     "hive_metastore.default.employee_attrition_inference")

# define target column
TARGET = ["Attrition"]

# define categorical feature columns
CATEGORICAL_FEATURES = [
    "Gender",
    "Education",
    "EducationField",
    "Department",
    "JobRole",
    "JobLevel",
    "PerformanceRating",
    "JobInvolvement",
    "JobSatisfaction",
    "RelationshipSatisfaction",
    "EnvironmentSatisfaction",
    "BusinessTravel",
    "OverTime",
    "WorkLifeBalance",
    "MaritalStatus",
    "StockOptionLevel"
]

# define numeric feature columns
NUMERIC_FEATURES = [
    "Age",
    "DistanceFromHome",
    "MonthlyIncome",
    "NumCompaniesWorked",
    "PercentSalaryHike",
    "TotalWorkingYears",
    "TrainingTimesLastYear",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager"
]


# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Define functions to monitor data drift

# COMMAND ----------

def load_data():

    # load datasets
    reference_df = spark.read.table(
        dbutils.widgets.get("reference_dataset_table")).toPandas()
    target_df = spark.read.table(
        dbutils.widgets.get("target_dataset_table")).toPandas()

    # change data types of features
    reference_df[CATEGORICAL_FEATURES] = reference_df[CATEGORICAL_FEATURES].astype(
        "str")
    reference_df[NUMERIC_FEATURES] = reference_df[NUMERIC_FEATURES].astype(
        "float")
    target_df[CATEGORICAL_FEATURES] = target_df[CATEGORICAL_FEATURES].astype(
        "str")
    target_df[NUMERIC_FEATURES] = target_df[NUMERIC_FEATURES].astype(
        "float")

    return reference_df, target_df

# COMMAND ----------

# evaluate data drift with Evidently Profile


def evaluate_drift(reference_df, target_df):

    # define column mapping for evidently
    column_mapping = ColumnMapping()
    column_mapping.target = None
    column_mapping.prediction = None
    column_mapping.id = None
    column_mapping.datetime = None
    column_mapping.numerical_features = NUMERIC_FEATURES
    column_mapping.categorical_features = CATEGORICAL_FEATURES

    # generate drift metrics
    data_drift_report = Report(metrics=[DataDriftPreset()])
    data_drift_report.run(reference_data=reference_df,
                          current_data=target_df, column_mapping=column_mapping)
    report = data_drift_report.as_dict()

    # process drift metrics
    drift_metrics = []

    for feature in column_mapping.numerical_features + column_mapping.categorical_features:
        drift_metrics.append(
            (feature, report["metrics"][1]["result"]["drift_by_columns"][feature]["drift_score"]))

    return drift_metrics

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Monitor for data drift

# COMMAND ----------


with mlflow.start_run() as run:  # inside brackets run_name='test'

    # Log datetime
    mlflow.log_param("datetime", str(datetime.now()))

    # Load datasets
    reference_df, target_df = load_data()

    # Log metrics
    drift_metrics = evaluate_drift(reference_df, target_df)

    for feature in drift_metrics:
        mlflow.log_metric(feature[0], round(feature[1], 3))

    # end run
    mlflow.end_run()

# COMMAND ----------
