# Databricks notebook source
# MAGIC %md
# MAGIC # Train Machine Learning Model
# MAGIC
# MAGIC This notebook aims to develop and register an MLFlow Model for deployment consisting of:
# MAGIC - a machine learning model to predict the liklihood of employee attrition.
# MAGIC
# MAGIC This example uses an adapted  version of the [`IBM HR Analytics Employee Attrition & Performance` dataset](https://www.kaggle.com/pavansubhasht/ibm-hr-analytics-attrition-dataset) available from Kaggle.
# MAGIC
# MAGIC > Ensure you have created managed Delta tables in the Hive Metastore with the associated dataset. These [instructions](https://learn.microsoft.com/en-au/azure/databricks/ingestion/add-data/upload-data#upload-the-file) can be used to learn how to upload the dataset.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Import dependencies and define constants

# COMMAND ----------

import json
from typing import Dict, Tuple, Union

import mlflow
import pandas as pd
from hyperopt import STATUS_OK, fmin, hp, tpe
from mlflow.models.signature import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# define notebook parameters
dbutils.widgets.text("curated_dataset_table",
                     "hive_metastore.default.employee_attrition_curated")

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
# MAGIC #### Define functions to build the model

# COMMAND ----------

def prepare_data(df: pd.DataFrame, random_state: int = 2023) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # change data types of target and features
    df[TARGET] = df[TARGET].replace({"Yes": 1, "No": 0})
    df[NUMERIC_FEATURES] = df[NUMERIC_FEATURES].astype("float")
    df[CATEGORICAL_FEATURES] = df[CATEGORICAL_FEATURES].astype("str")

    # split into train and test datasets
    df_train, df_test = train_test_split(
        df[CATEGORICAL_FEATURES + NUMERIC_FEATURES + TARGET],
        test_size=0.20,
        random_state=random_state
    )

    return df_train, df_test

# COMMAND ----------


def make_classifer_pipeline(params: Dict[str, Union[str,  int]]) -> Pipeline:
    """Create sklearn pipeline to apply transforms and a final estimator"""
    # categorical features transformations
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("ohe", OneHotEncoder())]
    )

    # numeric features transformations
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median"))]
    )

    # preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )

    # model training pipeline
    classifer_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(**params, n_jobs=-1))
    ])

    return classifer_pipeline


# COMMAND ----------

# define objective function
def hyperparameter_tuning(params):
    mlflow.sklearn.autolog(silent=True)

    with mlflow.start_run(nested=True):
        # read and process curated data
        df = spark.read.table(dbutils.widgets.get(
            "curated_dataset_table")).toPandas()
        df_train, df_test = prepare_data(df)

        # seperate features and target variables
        x_train, y_train = df_train[CATEGORICAL_FEATURES +
                                    NUMERIC_FEATURES], df_train[TARGET]
        x_test, y_test = df_test[CATEGORICAL_FEATURES +
                                 NUMERIC_FEATURES], df_test[TARGET]

        # train and model
        estimator = make_classifer_pipeline(params)
        estimator = estimator.fit(x_train, y_train.values.ravel())
        y_predict_proba = estimator.predict_proba(x_test)

        # train model
        estimator = make_classifer_pipeline(params)
        estimator.fit(x_train, y_train.values.ravel())

        # calculate evaluation metrics
        y_pred = estimator.predict(x_test)

        validation_accuracy_score = accuracy_score(
            y_test.values.ravel(), y_pred)
        validation_roc_auc_score = roc_auc_score(y_test.values.ravel(), y_pred)
        validation_f1_score = f1_score(y_test.values.ravel(), y_pred)
        validation_precision_score = precision_score(
            y_test.values.ravel(), y_pred)
        validation_recall_score = recall_score(y_test.values.ravel(), y_pred)

        # log evaluation metrics
        mlflow.log_metric("validation_accuracy_score",
                          validation_accuracy_score)
        mlflow.log_metric("validation_roc_auc_score", validation_roc_auc_score)
        mlflow.log_metric("validation_f1_score", validation_f1_score)
        mlflow.log_metric("validation_precision_score",
                          validation_precision_score)
        mlflow.log_metric("validation_recall_score", validation_recall_score)

        # log model
        input_example = x_test.iloc[0].to_dict()
        signature = infer_signature(x_train, y_pred)
        mlflow.sklearn.log_model(
            estimator, "model", signature=signature, input_example=input_example)

        return {"loss": -validation_roc_auc_score, "status": STATUS_OK}

# COMMAND ----------


def train_model():
    # set mlflow tracking uri
    mlflow_client = mlflow.tracking.MlflowClient(tracking_uri='databricks')
    mlflow.set_tracking_uri("databricks")
    # start model training run
    mlflow.set_experiment("/employee-attrition-classifier")
    with mlflow.start_run(run_name="employee-attrition-classifier") as run:
        # define search space
        search_space = {
            "n_estimators": hp.choice("n_estimators", range(100, 1000)),
            "max_depth": hp.choice("max_depth", range(1, 25)),
            "criterion": hp.choice("criterion", ["gini", "entropy"]),
        }

        # hyperparameter tuning
        best_params = fmin(
            fn=hyperparameter_tuning,
            space=search_space,
            algo=tpe.suggest,
            max_evals=10,
        )

        # end run
        mlflow.end_run()

        return run

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Train and register the machine learning model

# COMMAND ----------


# Train model
run = train_model()

# Retreive model from best run
best_run = mlflow.search_runs(filter_string=f"tags.mlflow.parentRunId='{run.info.run_id}'", order_by=[
                              "metrics.testing_auc DESC"]).iloc[0]

# Register model artifact
model_name = "employee-attrition"
result = mlflow.register_model(f"runs:/{best_run.run_id}/model", model_name)

# Return notebook output
json_output = json.dumps(
    {"output": {"MODEL_NAME": result.name, "MODEL_VERSION": result.version}})
dbutils.notebook.exit(json_output)

# COMMAND ----------
