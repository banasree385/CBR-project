"""
FastAPI Application Configuration and Settings
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        # Application
        self.app_name = os.getenv("APP_NAME", "AI Foundry Agent")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # API Configuration
        self.api_v1_str = os.getenv("API_V1_STR", "/api/v1")
        self.secret_key = os.getenv("SECRET_KEY", "test_secret_key_for_demo_only_not_for_production")
        
        # Azure OpenAI / Azure AI Foundry Configuration
        # Prefer explicit environment values; default to empty to avoid accidental use of mocks
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        # For Azure AI Foundry, use AZURE_AI_FOUNDRY_KEY if AZURE_OPENAI_API_KEY is not set
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_AI_FOUNDRY_KEY", "")
        self.azure_openai_deployment_name = os.getenv("AGENT_MODEL_DEPLOYMENT_NAME", "gpt41")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")

        # Azure AI Foundry project-specific configuration
        self.azure_ai_foundry_endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT", "")
        self.azure_ai_foundry_key = os.getenv("AZURE_AI_FOUNDRY_KEY", "")
        self.azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "")
        self.azure_resource_group = os.getenv("AZURE_RESOURCE_GROUP", "")
        self.azure_project_name = os.getenv("AZURE_PROJECT_NAME", "")

        # CORS Configuration
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:8001,http://127.0.0.1:3000,http://127.0.0.1:8000,http://127.0.0.1:8001")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings