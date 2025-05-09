# server.py
import logging
import os
import sys
from typing import Callable, Literal

from dotenv import load_dotenv
from hyperspell import Hyperspell
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

from hyperspell_mcp.types import Collection, Document, DocumentStatus, Error

logger = logging.getLogger("hyperspell_mcp")


class ServerConfig(BaseModel):
    use_resources: bool = False
    collection: str | None = Field(
        default_factory=lambda: os.getenv("HYPERSPELL_COLLECTION")
    )
    use_tools: bool = True
    api_key: str = Field(default_factory=lambda: os.getenv("HYPERSPELL_TOKEN", ""))

    @field_validator("api_key", mode="after")
    def validate_api_key(cls, value: str) -> str:
        if not value:
            logger.error("HYPERSPELL_TOKEN is not set")
            sys.exit(1)
        return value

    @classmethod
    def from_env(cls, env_file: str = ".env") -> "ServerConfig":
        """Create config from environment variables"""
        if os.path.exists(env_file):
            load_dotenv(env_file)

        # Expose resources or tools?
        # Some MCP clients don't support resources well (looking at you, Claude Desktop),
        # so we can expose them as tools instead.
        tools_or_resources = os.getenv("HYPERSPELL_USE_RESOURCES", "true").lower()
        use_resources = tools_or_resources in ("true", "1", "both")
        use_tools = tools_or_resources in ("false", "0", "both")

        if not use_resources and not use_tools:
            logger.error(
                f"Invalid value for HYPERSPELL_USE_RESOURCES: '{tools_or_resources}'"
            )
            sys.exit(1)

        return cls(
            api_key=os.getenv("HYPERSPELL_TOKEN", ""),
            use_resources=use_resources,
            use_tools=use_tools,
        )


class HyperspellMCPServer(FastMCP):
    def __init__(self, config: ServerConfig, **kwargs):
        super().__init__(**kwargs, dependencies=["hyperspell", "mcp[cli]"])
        self.config = config
        self.api = Hyperspell(api_key=config.api_key)

        if config.use_tools and config.use_resources:
            logger.info("Hyperspell MCP Server initialized using tools AND resources")
        else:
            logger.info(
                f"Hyperspell MCP Server initialized using {'tools' if config.use_tools else 'resources'}"
            )

    def tool_or_resource(self, uri: str, name: str | None = None):
        def decorator(fn: Callable):
            description = fn.__doc__
            if self.config.use_resources:
                self.resource(
                    uri,
                    name=name,
                    description=description,
                    mime_type="application/json",
                )(fn)
            if self.config.use_tools:
                self.add_tool(fn, name=name, description=description)
            return fn

        return decorator

    async def log(
        self, message: str, level: Literal["info", "warning", "error"] = "info"
    ):
        await self._mcp_server.request_context.session.send_log_message(
            level=level,
            data=message,
        )


mcp = HyperspellMCPServer(config=ServerConfig.from_env())


@mcp.tool_or_resource("collection://", name="List Collections")
def list_collections() -> list[Collection]:
    """Get a list of all collections on Hyperspell"""
    r = mcp.api.collections.list()
    return Collection.from_pydantic(r.items)


@mcp.tool_or_resource("collection://{collection_name}", name="Get Collection")
def get_documents(collection_name: str) -> list[Document]:
    """Get a list of all documents in a collection"""
    r = mcp.api.documents.list(collection=collection_name)
    return Document.from_pydantic(r.items)


@mcp.tool_or_resource("document://{document_id}", name="Get Document")
def get_document(document_id: int) -> Document | Error:
    """Get a document from a collection"""
    # try:
    r = mcp.api.documents.get(document_id=document_id)
    return Document.from_pydantic(r)
    # except APIError as e:
    # return Error(error=e.__class__.__name__, message=e.message)


@mcp.tool(
    name="Search Hyperspell", description="Search Hyperspell for documents and data."
)
def query(query: str) -> list[Document]:
    """Search Hyperspell for documents and data."""
    r = mcp.api.query.search(query=query, collections=mcp.config.collection)
    return Document.from_pydantic(r.documents)


@mcp.tool(
    name="Add File", description="Add a file or website from a URL to Hyperspell."
)
def add_file(url: str) -> DocumentStatus:
    """Add a file or URL to Hyperspell."""
    r = mcp.api.documents.add_url(url=url, collection=mcp.config.collection)
    return DocumentStatus.from_pydantic(r)


@mcp.tool(
    name="Add Memory",
    description="Add a plain text document or memory to Hyperspell.",
)
def add_memory(text: str, title: str | None = None) -> DocumentStatus:
    """Add a plain text document or memory to Hyperspell."""
    r = mcp.api.documents.add(
        text=text, collection=mcp.config.collection, title=title, source="mcp"
    )
    return DocumentStatus.from_pydantic(r)


def main():
    mcp.run(transport="stdio")
    logger.info("Server exited")


if __name__ == "__main__":
    main()
