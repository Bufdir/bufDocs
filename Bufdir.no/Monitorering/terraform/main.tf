# 1. Application Insights
resource "azurerm_application_insights" "main" {
  name                = "${var.project_name}-${var.environment}-ai"
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = var.log_analytics_workspace_id
  application_type    = "web"
  retention_in_days   = 30
}

# 2. Action Group for varsling
resource "azurerm_monitor_action_group" "main" {
  name                = "${var.project_name}-${var.environment}-ag"
  resource_group_name = var.resource_group_name
  short_name          = "bufalerts"

  dynamic "email_receiver" {
    for_each = var.alert_email_addresses
    content {
      name                    = "Email-${email_receiver.key}"
      email_address           = email_receiver.value
      use_common_alert_schema = true
    }
  }
}

# 3. Alarmer for Key Vault (Secrets som utløper snart)
resource "azurerm_monitor_scheduled_query_rules_alert" "kv_secret_expiry" {
  name                = "${var.project_name}-${var.environment}-kv-expiry-alert"
  location            = var.location
  resource_group_name = var.resource_group_name

  action {
    action_group = [azurerm_monitor_action_group.main.id]
  }

  data_source_id = var.log_analytics_workspace_id
  description    = "Varsler når en secret i Key Vault nærmer seg utløpsdato"
  enabled        = true
  query          = <<-QUERY
    AzureDiagnostics
    | where ResourceProvider == "MICROSOFT.KEYVAULT"
    | where OperationName == "SecretNearExpiry"
    | project TimeGenerated, Resource, ResultSignature, requestUri_s
    QUERY
  severity    = 1
  frequency   = 1440 # Én gang i døgnet
  window_size = 1440
  trigger {
    operator  = "GreaterThan"
    threshold = 0
  }
}

# 4. Event Grid for Key Vault hendelser
# System Topic for Key Vault
resource "azurerm_eventgrid_system_topic" "kv_topic" {
  name                   = "${var.project_name}-${var.environment}-kv-topic"
  resource_group_name    = var.resource_group_name
  location               = var.location
  source_arm_resource_id = var.key_vault_id
  topic_type             = "Microsoft.KeyVault.vaults"
}

# Event Grid Subscription for utgåtte secrets
resource "azurerm_eventgrid_system_topic_event_subscription" "kv_expiry_sub" {
  name                = "SecretExpirySubscription"
  system_topic        = azurerm_eventgrid_system_topic.kv_topic.name
  resource_group_name = var.resource_group_name

  included_event_types = [
    "Microsoft.KeyVault.SecretNearExpiry",
    "Microsoft.KeyVault.SecretExpired"
  ]

  # Her kan man legge til en webhook (f.eks. til en Azure Function for auto-rotasjon)
  # For nå bruker vi Action Group som mål hvis mulig, eller lar den være klar for utvidelse.
  # Merk: Azure Monitor Action Group kan også trigges av Event Grid via Azure Function/Logic App.
  
  # Eksempel på Logic App eller Function endpoint (må tilpasses faktisk ressurs):
  # webhook_endpoint {
  #   url = "https://..."
  # }
}
