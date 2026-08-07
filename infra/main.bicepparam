using './main.bicep'

param environmentName = '${AZURE_ENV_NAME}'
param location = '${AZURE_LOCATION}'
param appServiceName = '${AZURE_APP_SERVICE_NAME}'
param appServicePlanName = '${AZURE_APP_SERVICE_PLAN_NAME}'
param applicationInsightsName = '${AZURE_APPLICATION_INSIGHTS_NAME}'
param logAnalyticsName = '${AZURE_LOG_ANALYTICS_NAME}'
