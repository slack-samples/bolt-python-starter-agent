from contextvars import ContextVar

from agent.deps import AgentDeps

agent_deps_var: ContextVar[AgentDeps] = ContextVar("agent_deps")
