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
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Azure OpenAI Configuration
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mock-openai-resource.openai.azure.com/")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY", "mock_api_key")
        self.azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Azure Active Directory
        self.azure_client_id = os.getenv("AZURE_CLIENT_ID", "mock_client_id")
        self.azure_client_secret = os.getenv("AZURE_CLIENT_SECRET", "mock_client_secret")
        self.azure_tenant_id = os.getenv("AZURE_TENANT_ID", "mock_tenant_id")
        
        # Azure AI Foundry
        self.azure_ai_foundry_endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT", "https://mock-ai-foundry.cognitiveservices.azure.com/")
        self.azure_ai_foundry_key = os.getenv("AZURE_AI_FOUNDRY_KEY", "mock_foundry_key")
        self.azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "mock_subscription_id")
        self.azure_resource_group = os.getenv("AZURE_RESOURCE_GROUP", "mock_resource_group")
        
        # CORS Configuration
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        # Database (Optional)
        self.database_url = os.getenv("DATABASE_URL")
        
        # Redis (Optional)
        self.redis_url = os.getenv("REDIS_URL")
        
        # Monitoring
        self.enable_telemetry = os.getenv("ENABLE_TELEMETRY", "true").lower() in ("true", "1", "yes")
        self.application_insights_connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings