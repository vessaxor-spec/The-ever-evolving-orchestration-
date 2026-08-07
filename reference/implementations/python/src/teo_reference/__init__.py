"""TEO Phase 5 reference orchestration engine."""

from .anthropic_adapter import AnthropicMessagesAdapter, execute_anthropic_canary_once
from .engine import OrchestrationEngine as BaseOrchestrationEngine
from .google_adapter import GeminiInteractionsAdapter, execute_gemini_canary_once
from .openai_adapter import OpenAIResponsesAdapter, execute_openai_canary_once
from .provider_adapter import (
    ProviderAdapter,
    ProviderAdapterContractError,
    ProviderExecutionRequest,
    ProviderExecutionResponse,
    ProviderFailure,
    ReasoningEffort,
    execute_provider_once,
)
from .provider_connection import (
    HeaderProviderConnection,
    ProviderConnection,
    ProviderConnectionError,
    ProviderConnectionRequest,
    ProviderConnectionResponse,
)
from .runtime_canary import CanaryRuntimeOutcome, execute_guarded_canary
from .runtime_circuit_breaker import (
    CircuitStateStore,
    InMemoryCircuitStateStore,
    JsonFileCircuitStateStore,
    ProviderCircuitBreaker,
    ProviderCircuitPolicy,
    ProviderCircuitRecord,
)
from .runtime_retry import RetryExecution, RetryPolicy, execute_with_transient_retry
from .schemas import DispatchRecord, FinalOutcome, TaskRequest, VerificationResult
from .specialist_routing import SpecialistRoutingEngine

OrchestrationEngine = SpecialistRoutingEngine

__all__ = [
    "AnthropicMessagesAdapter",
    "BaseOrchestrationEngine",
    "CanaryRuntimeOutcome",
    "CircuitStateStore",
    "DispatchRecord",
    "FinalOutcome",
    "GeminiInteractionsAdapter",
    "HeaderProviderConnection",
    "InMemoryCircuitStateStore",
    "JsonFileCircuitStateStore",
    "OpenAIResponsesAdapter",
    "OrchestrationEngine",
    "ProviderAdapter",
    "ProviderAdapterContractError",
    "ProviderCircuitBreaker",
    "ProviderCircuitPolicy",
    "ProviderCircuitRecord",
    "ProviderConnection",
    "ProviderConnectionError",
    "ProviderConnectionRequest",
    "ProviderConnectionResponse",
    "ProviderExecutionRequest",
    "ProviderExecutionResponse",
    "ProviderFailure",
    "ReasoningEffort",
    "RetryExecution",
    "RetryPolicy",
    "SpecialistRoutingEngine",
    "TaskRequest",
    "VerificationResult",
    "execute_anthropic_canary_once",
    "execute_gemini_canary_once",
    "execute_guarded_canary",
    "execute_openai_canary_once",
    "execute_provider_once",
    "execute_with_transient_retry",
]
