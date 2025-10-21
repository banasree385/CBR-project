"""
FastAPI Application Configuration and Settings
"""

import os
from typing import List, Optional
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    """Application settings and configuration."""
    
    # Application
    app_name: str = "AI Foundry Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    secret_key: str = "test_secret_key_for_demo_only_not_for_production"
    access_token_expire_minutes: int = 30
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = "https://mock-openai-resource.openai.azure.com/"
    azure_openai_api_key: str = "mock_api_key"
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Azure Active Directory
    azure_client_id: str = "mock_client_id"
    azure_client_secret: str = "mock_client_secret"
    azure_tenant_id: str = "mock_tenant_id"
    
    # Azure AI Foundry
    azure_ai_foundry_endpoint: str = "https://mock-ai-foundry.cognitiveservices.azure.com/"
    azure_ai_foundry_key: str = "mock_foundry_key"
    azure_subscription_id: str = "mock_subscription_id"
    azure_resource_group: str = "mock_resource_group"
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database (Optional)
    database_url: Optional[str] = None
    
    # Redis (Optional)
    redis_url: Optional[str] = None
    
    # Monitoring
    enable_telemetry: bool = True
    application_insights_connection_string: Optional[str] = None
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator('secret_key', mode='before')
    @classmethod
    def validate_secret_key(cls, v):
        """Validate secret key is provided."""
        if not v:
            raise ValueError("SECRET_KEY must be provided")
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings