variable "project_name" {
  type        = string
  description = "Navn på prosjektet (brukes som prefiks)"
  default     = "bufdirno"
}

variable "environment" {
  type        = string
  description = "Miljø (f.eks. prod, test, dev)"
  default     = "prod"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "Norway East"
}

variable "resource_group_name" {
  type        = string
  description = "Navnet på ressursgruppen"
}

variable "log_analytics_workspace_id" {
  type        = string
  description = "ID til Log Analytics Workspace som skal brukes"
}

variable "alert_email_addresses" {
  type        = list(string)
  description = "Liste over e-postadresser som skal motta varsler"
  default     = []
}

variable "key_vault_id" {
  type        = string
  description = "ID til Key Vault som skal overvåkes"
}
