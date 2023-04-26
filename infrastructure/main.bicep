//********************************************************
// General Parameters
//********************************************************

@description('Workload Identifier')
param workloadIdentifier string = substring(uniqueString(resourceGroup().id), 0, 6)

@description('Resource Instance')
param resourceInstance string = '001'

//********************************************************
// Resource Config Parameters
//********************************************************

@description('Databricks Workspace Name')
param databricksWorkspaceName string = 'dbw${workloadIdentifier}${resourceInstance}'

@description('Databricks Workspace Location')
param databricksWorkspaceLocation string = resourceGroup().location

@description('Databricks Managed Resource Group Name')
param databricksManagedResourceGroupName string = '${resourceGroup().name}-dbw-mngd'

@description('The pricing tier of workspace.')
@allowed([
  'standard'
  'premium'
])
param pricingTier string = 'premium'

//********************************************************
// Variables
//********************************************************

//********************************************************
// Resources
//********************************************************
// Databricks Workspace
resource r_databricksWorkspace 'Microsoft.Databricks/workspaces@2018-04-01' = {
  name: databricksWorkspaceName
  location: databricksWorkspaceLocation
  sku: {
    name: pricingTier
  }
  properties: {
    managedResourceGroupId: r_databricksManagedResourceGroup.id
    parameters: {
      enableNoPublicIp: {
        value: false
      }
    }
  }
}

resource r_databricksManagedResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  scope: subscription()
  name: databricksManagedResourceGroupName
}

//********************************************************
// RBAC Role Assignments
//********************************************************

//********************************************************
// Deployment Scripts
//********************************************************

//********************************************************
// Outputs
//********************************************************
