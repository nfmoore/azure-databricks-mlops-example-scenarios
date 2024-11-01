# Getting Started

This example scenario will cover an opinionated way to build, deploy, and manage machine learning workflows for batch processing and online scenarios using Azure Databricks and GitHub Actions.

> [!CAUTION]
> This solution design is intended for proof-of-concept scenarios and is not recommended for enterprise production scenarios. It is advised to review and adjust the design based on your specific requirements if you plan to use this in a production environment. This could include:
>
> - Securing the solution through network controls.
> - Upflift observability by enabling monitoring and logging for different services.
> - Defining an operational support and lifecycle management plan for the solution.
> - Implementing alerting and notification mechanisms to notify support teams of any issues (e.g. performance, budget, etc.).
>
> The Azure Well-Architected Framework provides guidance on best practices for designing, building, and maintaining cloud solutions. For more information, see the [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/what-is-well-architected-framework).

> [!NOTE]
> The current workflows are designed to be triggered manually for ease of demonstration. However, they can be modified to be triggered automatically based on specific events.
>
> After developers have tested their code in the development environment, they can merge their code to the main branch via a pull request. This will trigger steps (1) to (4) automatically, but will not deploy to the production environment. This will validate that the code is working as expected in the staging environment, and allow the team to make adjustments if needed.
>
> The GitHub Action workflow `on` trigger will contain the following block to ensure it is triggered only when pull requests into the main branch are opened:
>
>```yml
>on:
>  pull_request:
>    types:
>      - opened
>      - synchronize
>    branches:
>      - main
> ```
>
> Once the team is ready to deploy to production, the pull request can be approved and merged into the main branch. This will trigger steps (1) to (5) as described above to deploy the code to the production environment.
>
> The GitHub Action workflow `on` trigger will contain the following block to ensure it is triggered only when new code is pushed into the main branch:
>
>```yml
>on:
>  push:
>    branches:
>     - main
> ```

## Related Resources

- [MLOps workflows on Databricks](https://docs.databricks.com/en/machine-learning/mlops/mlops-workflow.html)
- [What are Databricks Asset Bundles?](https://docs.databricks.com/en/dev-tools/bundles/index.html)
