targetScope = 'subscription'

//********************************************************
// Parameters
//********************************************************

@description('Resource group name')
param resourceGroupName string = 'rg-example-scenario-azure-databricks-mlops'

@description('Databricks managed resource group name')
param mrgDatabricksName string = 'rgm-example-scenario-azure-databricks-mlops-databricks'

@description('Location for resources')
param location string = 'australiaeast'

//********************************************************
// Variables
//********************************************************

var serviceSuffix = substring(uniqueString(resourceGroupName), 0, 5)

var resources = {
  databricksStagingName: 'dbw01${serviceSuffix}'
  databricksProductionName: 'dbw02${serviceSuffix}'
  logAnalyticsWorkspaceName: 'log01${serviceSuffix}'
  storageAccountName: 'st01${serviceSuffix}'
}

//********************************************************
// Resources
//********************************************************

resource resourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: resourceGroupName
  location: location
}

// ********************************************************
// Modules
// ********************************************************

module storageAccount './modules/storage-account.bicep' = {
  name: '${resources.storageAccountName}-deployment'
  scope: resourceGroup
  params: {
    name: resources.storageAccountName
    location: location
    tags: {
      environment: 'shared'
    }
  }
}

module logAnalyticsWorkspace './modules/log-analytics-workspace.bicep' = {
  name: '${resources.logAnalyticsWorkspaceName}-deployment'
  scope: resourceGroup
  params: {
    name: resources.logAnalyticsWorkspaceName
    location: location
    tags: {
      environment: 'shared'
    }
    storageAccountId: storageAccount.outputs.id
  }
}

var databricksWorkspaces = [
  { name: resources.databricksStagingName, environment: 'staging' }
  { name: resources.databricksProductionName, environment: 'production' }
]

module databricks './modules/databricks.bicep' = [
  for databricks in databricksWorkspaces: {
    name: '${databricks.name}-deployment'
    scope: resourceGroup
    params: {
      name: databricks.name
      location: location
      tags: {
        environment: databricks.environment
      }
      managedResourceGroupName: '${mrgDatabricksName}-${databricks.environment}'
      logAnalyticsWorkspaceId: logAnalyticsWorkspace.outputs.id
    }
  }
]

//********************************************************
// Outputs
//********************************************************

output storageAccountName string = storageAccount.outputs.name
output logAnalyticsWorkspaceName string = logAnalyticsWorkspace.outputs.name
output databricksStagingName string = databricks[0].outputs.name
output databricksProductionName string = databricks[1].outputs.name
output databricksStagingHostname string = databricks[0].outputs.hostname
output databricksProductionHostname string = databricks[1].outputs.hostname
