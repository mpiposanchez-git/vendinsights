# Deployment Guide: Python App with Azure DevOps

This document walks you through the process of deploying a Python-based machine learning application using Azure DevOps.  By following these steps you will learn the mechanics behind continuous integration and continuous deployment (CI/CD), containerization, and hosting a web API.  The goal is to move your code from local development to a reproducible pipeline that builds, tests, and publishes an executable artifact or container and finally runs it in Azure.

Key definitions:
* **CI/CD** – Continuous integration/continuous deployment; automatically running tests and pushing code to environments when you commit.
* **Pipeline** – A YAML file (azure-pipelines.yml) describing build/test/deploy steps.
* **Artifact** – The build output (package wheel, docker image) that can be deployed.
* **Service connection** – An authenticated link between Azure DevOps and Azure resources such as App Service or Container Registry.

Assumptions:
* Your repository contains `mps_package` (Python package) and a simple FastAPI endpoint for serving predictions.
* `azure-pipelines.yml` already exists to orchestrate build steps.

Expected outcome: after completing the guide, pushing changes to the repo will automatically run tests, build the package (and optionally a container), and deploy the application to an Azure App Service instance where it can be accessed via HTTP.

## 1. Prepare Your Environment

**Goal:** set up the basic prerequisites so the pipeline has everything it needs to run.  This stage is all manual work that you perform once before the pipeline takes over.

1. Ensure you have an Azure DevOps organization and project. If you don't have one, create it at https://dev.azure.com.  This is where pipelines, repos, and service connections live.
2. Add your repository to the Azure DevOps project. You can push your existing local repo (which you already did earlier) or import it.  The repository is the source code that triggers pipeline runs.
3. In your local repo, verify the following key files exist:
   - `requirements.txt` – enumerates Python dependencies; pipelines install from this to ensure the correct environment.
   - `azure-pipelines.yml` – defines the build/test/deploy steps executed by Azure DevOps.
   - `Dockerfile` – optional but highly recommended if you want to produce a container image; ensures consistent runtime.
   - `.env.example` – sample environment variables; use it as a template for the actual `.env` file that contains secrets or configuration.
   - Python package structure (`mps_package/` etc.) – your application code organized as a package.
4. Commit and push all changes to the remote.  Pushing triggers the pipeline once configured.

**Rationale:** having a consistent codebase and explicit dependency list lets the pipeline reproduce your development environment on demand.  At this point nothing is automated yet, but you are building the foundation.

**Expected outcome:** when you push, the repository contains everything needed for a build, and you're ready to onboard the pipeline.

## 2. Configure Azure Pipelines

**Goal:** connect your repository to Azure DevOps so that every commit triggers an automated workflow (CI/CD).

1. In your Azure DevOps project, navigate to **Pipelines > Pipelines**.
2. Click **New pipeline** and follow the wizard:
   - Select **Azure Repos Git** (or another source, like GitHub).
   - Choose your repository (`personal` repo).
   - When prompted, Azure should detect `azure-pipelines.yml` automatically. Confirm and save.

Azure DevOps will create a pipeline object linked to your YAML file.  This object represents the CI/CD workflow.

3. The pipeline will run immediately (on commit) and execute the steps defined in the YAML file:
   - **Install Python and dependencies** – ensures the build agent has the required libraries.
   - **Run unit tests with `pytest`** – verifies that code changes didn’t break functionality.
   - **Build the package using `python -m build`** – creates distributable artifacts (sdist, wheel).
   - **Publish the `dist` artifact** – makes the built package available for later stages or downloads.

4. Review the pipeline run output. Look for green checkmarks; if errors occur, the logs will show which step failed.  Fix issues locally and commit updates to retry.

**Rationale:** automated testing and building on each push catch bugs early and keep your codebase in a deployable state.  Automation also serves as documentation of the build process.

**Expected outcome:** pipeline runs successfully, tests pass, and build artifacts appear in the Azure DevOps artifacts tab.

## 3. Build a Docker Image (optional)

**Goal:** produce a self-contained container image that bundles your application and its runtime. Containers simplify deployment across environments and ensure consistency.

1. If you want to containerize the app, your pipeline can include a Docker build step.  Containers are especially useful when deploying to AKS, Azure Container Apps, or if your runtime has specific system dependencies.
2. Add the following task to `azure-pipelines.yml` after the `Build package` step:
   ```yaml
  - task: Docker@2
    displayName: Build and push Docker image
    inputs:
      containerRegistry: '<your service connection>'
      repository: 'mps_package'
      command: 'buildAndPush'
      Dockerfile: 'Dockerfile'
      tags: '$(Build.BuildId)'
   ```
   This task uses the Dockerfile in your repo to create an image and then pushes it to a registry.
3. Create a **Docker registry service connection** under **Project settings > Service connections**. This can point to Azure Container Registry (ACR) or a public registry such as Docker Hub.  It enables the pipeline to authenticate and upload images.
4. Run the pipeline again to verify the image is built and pushed. You should see entries in the registry and a success log.

**Rationale:** a Docker image encapsulates your app, the Python interpreter, and all dependencies.  Deploying containers reduces "it works on my machine" issues and aligns with modern microservices workflows.

**Expected outcome:** pipeline produces a taggable Docker image stored in your registry, ready for deployment to any container host.

## 4. Deploy to Azure App Service

**Goal:** host your application in a managed web service so it can be accessed over the internet or within a corporate network. App Service takes care of scaling, SSL, and process management.

1. **Create an App Service** in the Azure portal:
   - Choose runtime stack `Python 3.11` (or Docker if you built a container).
   - Select a region and pricing tier that fits your budget.
   - If deploying a container, choose **Docker Container** as the publish option.

2. **Add a service connection** in Azure DevOps for Azure Resource Manager (ARM). This gives the pipeline permission to deploy to the App Service.

3. Extend your pipeline with a deployment step. After publishing your build artifacts, add:
   ```yaml
  - task: AzureWebApp@1
    displayName: Deploy Python app to App Service
    inputs:
      azureSubscription: '<service connection name>'
      appType: 'webAppLinux'
      appName: '<your-app-service-name>'
      package: '$(System.DefaultWorkingDirectory)/dist/*.zip'
      runtimeStack: 'PYTHON|3.11'
   ```
   This copies the zipped package produced earlier onto the App Service and restarts the application.

4. If deploying a container image instead, change `appType` to `webAppContainer` and provide the image name/tag from your registry, e.g.:
   ```yaml
   appType: 'webAppContainer'
   imageName: 'myregistry.azurecr.io/mps_package:$(Build.BuildId)'
   ```

5. Configure application settings (in App Service) to match the names in `.env.example` (e.g., `API_HOST`, `API_PORT`, `DATA_PATH`).  These settings are available as environment variables to your code.  You can also update them programmatically using the `AzureAppServiceSettings@1` pipeline task.

**Rationale:** App Service abstracts away infrastructure complexity, allowing you to deploy code or containers simply. It integrates seamlessly with Azure DevOps, so deployments constitute a single pipeline stage.

**Expected outcome:** after pipeline execution, the App Service is running your latest code. Visiting the service URL should return the FastAPI root message, and the `/predict` endpoint should respond (even if stubbed).

## 5. Local Testing and Deployment

**Goal:** verify that your application works correctly before pushing to the remote pipeline. Local testing saves time and helps debug issues early.

1. **Run locally using Docker** (replicates the production container):
   ```bash
   docker build -t mps_package:latest .
   docker run -p 8000:8000 --env-file .env mps_package:latest
   ```
   - This builds an image according to your Dockerfile and starts a container exposing port 8000.
   - The `--env-file` argument loads environment variables from `.env` (make a copy of `.env.example`).

2. **Run without Docker** (pure Python environment):
   ```bash
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn mps_package.api:app --reload
   ```
   - This reinstantiates the development environment on your machine.
   - `--reload` restarts the server when you make code changes.

3. Access the API at `http://localhost:8000` and try the `/predict` endpoint using `curl` or a browser.

**Rationale:** running both Docker and pure Python ensures that the containerized environment behaves the same as local development.  It isolates issues to either code or environment early.

**Expected outcome:** the API responds locally, inputs are accepted, and you can iterate on the code quickly before committing.
## 6. Adding Monitoring and Logging

**Goal:** track the health and performance of your application in production so you can respond to issues and understand usage.

1. For App Service, **enable Application Insights** through the Azure portal.  This provides automated telemetry such as request counts, response times, exceptions, and custom metrics.
2. In `mps_package/utils` implement a standardized logger (using Python's `logging` module) that writes to `stdout` or a file.  App Service and Docker containers automatically collect `stdout` output, which appears in the Azure portal logs.
3. Configure alerts based on Application Insights metrics (e.g., failed requests > 5/minute, CPU > 80%). Alerts can notify you via email or Teams.

**Rationale:** without monitoring, it's difficult to know whether the service is running correctly or performing well.  Logging and telemetry are essential for production-quality systems.

**Expected outcome:** you can view real-time metrics in Azure, inspect logs when errors occur, and be notified if something goes wrong.
## 7. Securing Secrets

**Goal:** protect sensitive information such as API keys, database passwords, and connection strings so they are not exposed in source control or logs.

- **Azure Key Vault** is a managed service for storing secrets.  Create a vault in your subscription and add secrets like `DB_CONNECTION` or `AZURE_STORAGE_KEY`.
- In your pipeline, use the `AzureKeyVault@2` task to retrieve secrets at build or deploy time and expose them as environment variables:
  ```yaml
  - task: AzureKeyVault@2
    inputs:
      azureSubscription: '<service connection>'
      KeyVaultName: '<vault-name>'
      SecretsFilter: '*'  # or list specific secrets
      RunAsPreJob: true
  ```
- Locally, keep a `.env` file with dummy values and add `.env` to `.gitignore` so it's never committed.

**Rationale:** storing secrets in code or repository is a security risk. Key Vault centralizes secret management and integrates with Azure DevOps and App Service.

**Expected outcome:** pipeline and app read required secrets at runtime without ever storing them in source control.
## 8. Continuous Learning and Iteration

**Goal:** make deployment a repeatable, automated process so you can focus on improving your application rather than manual release steps.

1. Each time you push to `main` (or any branch configured in `trigger`), the pipeline runs.  This gives immediate feedback on whether changes break the build or tests.
2. Extend the pipeline with multiple **stages** representing environments such as staging and production.  Use YAML `deployment` jobs and target Azure environments with appropriate approvals:
   ```yaml
   stages:
   - stage: CI
     jobs:
     - job: build
       steps: ...
   - stage: Staging
     dependsOn: CI
     jobs:
     - deployment: DeployStaging
       environment: 'staging'
       strategy:
         runOnce:
           deploy:
             steps: ...
   - stage: Production
     dependsOn: Staging
     jobs: ...
   ```
3. To deploy updates, commit code changes and merge via pull request.  The pipeline will run tests; on success, the deployment stage will push the new version live.

**Rationale:** treating deployment as code ensures consistency and reduces human error.  A staged approach allows testing in a safe environment before exposing changes to users.

**Expected outcome:** your repository becomes a single source of truth.  New features and fixes propagate automatically with minimal manual intervention.
## 9. Example Pipeline with Stages
```yaml
stages:
- stage: CI
  jobs:
  - job: build
    steps: ...
- stage: Deploy
  dependsOn: CI
  jobs:
  - deployment: DeployToApp
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
            - task: AzureWebApp@1
              inputs: ...
```

## 10. Useful Resources
- [Azure DevOps Pipelines docs](https://docs.microsoft.com/azure/devops/pipelines/)
- [Deploy Python apps to Azure App Service](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [FastAPI deployment options](https://fastapi.tiangolo.com/deployment/)
- [Building Python packages](https://packaging.python.org/tutorials/)

---

By following these steps, you'll gain hands‑on experience deploying Python applications with Azure DevOps, from CI/CD pipelines through containerization to production hosting. Keep iterating: add tests, alerts, and monitoring as your model evolves.