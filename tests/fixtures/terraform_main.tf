terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket = "skillayer-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Service = "skillayer"
    }
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be dev or prod."
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "skillayer-artifacts-${var.environment}"

  tags = {
    Service = "skillayer"
  }
}

resource "aws_iam_role" "worker" {
  name = "skillayer-worker"
  arn  = "arn:aws:iam::123456789012:role/legacy"
}

resource "kubernetes_namespace" "app" {
  metadata {
    name = "skillayer"
  }
}

resource "google_project_iam_member" "viewer" {
  project = "skillayer"
  role    = "roles/viewer"
  member  = "group:platform@example.com"
}

resource "azurerm_resource_group" "app" {
  name     = "skillayer-rg"
  location = "eastus"

  tags = {
    Service = "skillayer"
  }
}

data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "network-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"
}

output "artifact_bucket" {
  description = "Artifact bucket name."
  value       = aws_s3_bucket.artifacts.id
}
