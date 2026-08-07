"""TEO Phase 5 reference orchestration engine."""

from .anthropic_adapter import AnthropicMessagesAdapter, execute_anthropic_canary_once
from .engine import OrchestrationEngine as BaseOrchestrationEngine
from .provider_adapter import (
    ProviderAdapter,
    ProviderAdapterContractError,
    ProviderExecutionRequest,
    ProviderExecutionResponse,
    ProviderFailure,
    execute_provider_once,
)
from .provider_connection import (
    HeaderProviderConnection,
    ProviderConnection,
    ProviderConnectionError,
    ProviderConnectionRequest,
    ProviderConnectionResponse,
)
from .schemas import DispatchRecord, FinalOutcome, TaskRequest, VerificationResult
from .specialist_routing import SpecialistRoutingEngine

OrchestrationEngine = SpecialistRoutingEngine

__all__ = [
    "AnthropicMessagesAdapter",
    "BaseOrchestrationEngine",
    "DispatchRecord",
    "FinalOutcome",
    "HeaderProviderConnection",
    "OrchestrationEngine",
    "ProviderAdapter",
    "ProviderAdapterContractError",
    "ProviderConnection",
    "ProviderConnectionError",
    "ProviderConnectionRequest",
    "ProviderConnectionResponse",
    "ProviderExecutionRequest",
    "ProviderExecutionResponse",
    "ProviderFailure",
    "SpecialistRoutingEngine",
    "TaskRequest",
    "VerificationResult",
    "execute_anthropic_canary_once",
    "execute_provider_once",
]
