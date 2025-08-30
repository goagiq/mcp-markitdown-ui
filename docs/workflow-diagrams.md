# MarkItDown Workflow Diagrams

This document contains detailed workflow diagrams showing how the different MarkItDown components interact and process files.

## File Conversion Workflow

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web UI
    participant API as FastAPI
    participant MCP as MCP Server
    participant Core as MarkItDown Core
    participant Converter as File Converter
    participant Plugin as Plugin System

    User->>WebUI: Upload file(s)
    WebUI->>API: POST /api/convert
    API->>Core: convert_file()
    
    alt File format detected
        Core->>Converter: Convert to Markdown
        Converter-->>Core: Markdown content
    else Plugin available
        Core->>Plugin: Use custom converter
        Plugin-->>Core: Markdown content
    end
    
    Core-->>API: Conversion result
    API-->>WebUI: JSON response
    WebUI-->>User: Display result
```

## MCP Tools Integration Workflow

```mermaid
sequenceDiagram
    participant Claude as Claude Desktop
    participant MCP as MCP Server
    participant Core as MarkItDown Core
    participant Tools as MCP Tools

    Claude->>MCP: Tool call: convert_file
    MCP->>Tools: Execute convert_file tool
    Tools->>Core: Convert file
    Core-->>Tools: Markdown result
    Tools-->>MCP: Tool response
    MCP-->>Claude: Markdown content

    Claude->>MCP: Tool call: convert_batch
    MCP->>Tools: Execute convert_batch tool
    Tools->>Core: Convert multiple files
    Core-->>Tools: Batch results
    Tools-->>MCP: Tool response
    MCP-->>Claude: Batch conversion results
```

## Plugin System Workflow

```mermaid
graph TD
    A[File Input] --> B{Format Detected?}
    B -->|Yes| C[Use Built-in Converter]
    B -->|No| D{Plugin Available?}
    D -->|Yes| E[Load Plugin]
    D -->|No| F[Error: Unsupported Format]
    
    E --> G[Plugin Converter]
    C --> H[Markdown Output]
    G --> H
    F --> I[Return Error]
    
    H --> J[Post-processing]
    J --> K[Final Output]
```

## Web UI Component Architecture

```mermaid
graph TB
    subgraph "Frontend"
        HTML[HTML Templates]
        CSS[CSS Styles]
        JS[JavaScript]
    end
    
    subgraph "Backend"
        FastAPI[FastAPI Server]
        Routes[API Routes]
        MCP_Int[MCP Integration]
        Static[Static Files]
    end
    
    subgraph "Services"
        Core[MarkItDown Core]
        MCP_Server[MCP Server]
        File_Handler[File Handler]
    end
    
    HTML --> FastAPI
    CSS --> Static
    JS --> FastAPI
    
    FastAPI --> Routes
    FastAPI --> MCP_Int
    FastAPI --> Static
    
    Routes --> Core
    MCP_Int --> MCP_Server
    Routes --> File_Handler
    
    Core --> MCP_Server
```

## Error Handling Workflow

```mermaid
graph TD
    A[File Input] --> B{File Valid?}
    B -->|No| C[Return File Error]
    B -->|Yes| D{Format Supported?}
    
    D -->|No| E[Return Format Error]
    D -->|Yes| F{Conversion Success?}
    
    F -->|No| G[Return Conversion Error]
    F -->|Yes| H[Return Success]
    
    C --> I[Error Response]
    E --> I
    G --> I
    H --> J[Success Response]
```

## Batch Processing Workflow

```mermaid
graph TD
    A[Multiple Files] --> B[Queue Files]
    B --> C[Process File 1]
    B --> D[Process File 2]
    B --> E[Process File N]
    
    C --> F{Success?}
    D --> G{Success?}
    E --> H{Success?}
    
    F -->|Yes| I[Add to Results]
    F -->|No| J[Add to Errors]
    
    G -->|Yes| I
    G -->|No| J
    
    H -->|Yes| I
    H -->|No| J
    
    I --> K[Return Batch Results]
    J --> K
```

## Development Workflow

```mermaid
graph LR
    A[Developer] --> B[Make Changes]
    B --> C[Run Tests]
    C --> D{Tests Pass?}
    D -->|No| E[Fix Issues]
    E --> C
    D -->|Yes| F[Format Code]
    F --> G[Lint Code]
    G --> H{Lint Pass?}
    H -->|No| I[Fix Lint Issues]
    I --> G
    H -->|Yes| J[Type Check]
    J --> K{Type Check Pass?}
    K -->|No| L[Fix Type Issues]
    L --> J
    K -->|Yes| M[Commit Changes]
    M --> N[Push to Repository]
```

## Deployment Workflow

```mermaid
graph TD
    A[Source Code] --> B[Build Docker Image]
    B --> C[Test Image]
    C --> D{Tests Pass?}
    D -->|No| E[Fix Issues]
    E --> B
    D -->|Yes| F[Push to Registry]
    F --> G[Deploy to Production]
    G --> H[Health Check]
    H --> I{Healthy?}
    I -->|No| J[Rollback]
    I -->|Yes| K[Monitor]
    K --> L[Scale if Needed]
```

## API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Nginx as Nginx Proxy
    participant FastAPI as FastAPI Server
    participant Auth as Authentication
    participant RateLimit as Rate Limiter
    participant Handler as Request Handler
    participant Core as MarkItDown Core

    Client->>Nginx: HTTP Request
    Nginx->>FastAPI: Forward Request
    FastAPI->>Auth: Check Authentication
    Auth-->>FastAPI: Auth Result
    FastAPI->>RateLimit: Check Rate Limit
    RateLimit-->>FastAPI: Rate Limit Result
    FastAPI->>Handler: Process Request
    Handler->>Core: Execute Conversion
    Core-->>Handler: Conversion Result
    Handler-->>FastAPI: Response
    FastAPI-->>Nginx: HTTP Response
    Nginx-->>Client: Final Response
```

## Monitoring and Logging

```mermaid
graph TB
    subgraph "Application"
        App[MarkItDown App]
        API[API Endpoints]
        MCP[MCP Server]
    end
    
    subgraph "Monitoring"
        Prometheus[Prometheus]
        Grafana[Grafana]
        Logs[Log Aggregator]
    end
    
    subgraph "Alerts"
        AlertManager[Alert Manager]
        Notifications[Notifications]
    end
    
    App --> Prometheus
    API --> Prometheus
    MCP --> Prometheus
    
    App --> Logs
    API --> Logs
    MCP --> Logs
    
    Prometheus --> Grafana
    Logs --> Grafana
    
    Prometheus --> AlertManager
    AlertManager --> Notifications
```
