# Example Scenarios: MLOps with Azure Databricks

## :books: Overview

This repository provides prescriptive guidance when building, deploying, and monitoring machine learning models with [Azure Databricks](https://learn.microsoft.com/azure/databricks/introduction/) in line with MLOps principles and practices. These example scenarios provide an end-to-end approach for MLOps in Azure based on common inference scenarios that focus on [Azure Databricks](https://learn.microsoft.com/azure/databricks/introduction/) used in conjunction with [GitHub Actions](https://github.com/features/actions).

> **Note**:
> MLOps aims to deploy and maintain machine learning models in production reliably and efficiently. It is supported by a set of repeatable, automated, and collaborative workflows that empower teams of ML professionals to quickly and easily release their machine learning models and monitor their effectiveness.

## :computer: Getting Started

This repository will focus on scenarios that develop, deploy and monitor models with out-of-the-box capabilities of Azure Databricks and not focus on integrations with other Azure services that can be used to play a supporting role. Users of Azure Databricks might choose to integrate with other services available within Azure to better align with existing workflows, enable new inference scenarios, or gain greater flexibility.

All example scenarios will focus on classical machine learning problems. An adapted version of the `UCI Credit Card Client Default` [dataset](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) will be used to illustrate each example scenario. The data is available in the `core/data` directory of this repository.

For more information on the example scenarios are outlined in the [Getting Started](.github/docs/getting-started.md) section of this repository.

### Setup

Detailed instructions for deploying this proof-of-concept are outlined in the [Step-by-Step Setup](.github/docs/step-by-step-setup.md) section of this repository. This proof-of-concept will illustrate how to:

- Promote a machine learning model to downstream environments.
- Deploy models for batch and online inference scenarios.
- Develop automated workflows to build and deploy models for each inference scenarios.
- Monitor workloads for usage, performance and data drift.

### Example Scenarios

This proof-of-concept will cover the following example scenarios:

| Example Scenario | Inference Scenario | Description |
| ---------------- | ------------------ | ----------- |
| Serving Endpoint | Online | Consume a registered model as an serving endpoint within Azure Databricks for low-latency scenarios. |
| Databricks Workflow | Batch | Consume a registered model as a scheduled workflow within Azure Databricks for high-throughput scenarios. |

For more information on the example scenarios are outlined in the [Getting Started](.github/docs/getting-started.md) section of this repository.

## :balance_scale: License

Details on licensing for the project can be found in the [LICENSE](./LICENSE) file.
