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
  databricksName: 'dbw01${serviceSuffix}'
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

module databricks './modules/databricks.bicep' = {
  name: '${resources.databricksName}-deployment'
  scope: resourceGroup
  params: {
    name: resources.databricksName
    location: location
    tags: {
      environment: 'shared'
    }
    managedResourceGroupName: mrgDatabricksName
    logAnalyticsWorkspaceId: logAnalyticsWorkspace.outputs.id
  }
}

//********************************************************
// Outputs
//********************************************************

output storageAccountName string = storageAccount.outputs.name
output logAnalyticsWorkspaceName string = logAnalyticsWorkspace.outputs.name
output databricksName string = databricks.outputs.name
output databricksHostname string = databricks.outputs.hostname
