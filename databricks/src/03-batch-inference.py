# Databricks notebook source
# MAGIC %md
# MAGIC #### Import dependencies, define notebook parameters and constants

# COMMAND ----------

import mlflow
from pyspark.sql.functions import struct

# COMMAND ----------

# define notebook parameters
dbutils.widgets.text("model_uri", "models:/credit-default-uci-sklearn/1")

dbutils.widgets.text(
    "inference_dataset_table", "hive_metastore.default.credit_default_uci_inference"
)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Run batch inference

# COMMAND ----------

# define parameters
inference_dataset_table = dbutils.widgets.get("inference_dataset_table")
model_uri = dbutils.widgets.get("model_uri")

# define column names
id_column_name = "id"
predicted_result_column_name = "prediction"

# COMMAND ----------

# read inference dataset
inference_df = spark.read.table(inference_dataset_table)

# filter for records that have not predictions
batch_df = spark.read.table(inference_dataset_table).filter("prediction IS NULL")

# create spark user-defined function for model prediction
predict = mlflow.pyfunc.spark_udf(spark, model_uri, result_type="string")

# generate predictions
predictions_df = batch_df.withColumn(predicted_result_column_name, predict(struct(*batch_df.columns)))

# update inference dataset with predictions
updated_inference_df = inference_df.filter("prediction IS NOT NULL").union(predictions_df)

# COMMAND ----------

# write results to inference dataset table
updated_inference_df.write.mode("overwrite").saveAsTable(inference_dataset_table)
