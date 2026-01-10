# Research Manager Flow Diagram

```mermaid
flowchart TD
    A[User Input Query] --> B[ResearchManager.run]
    B --> C[Generate Trace ID]
    C --> D[Initialize Printer]
    D --> E[Plan Searches]
    
    E --> F[Planner Agent]
    F --> G[WebSearchPlan Output]
    G --> H[Perform Searches]
    
    H --> I[Batch Searches<br/>max_concurrent=5]
    I --> J[Search Agent]
    J --> K[WebSearchTool]
    K --> L[Search Results]
    
    L --> M{More Batches?}
    M -->|Yes| I
    M -->|No| N[Write Report]
    
    N --> O[Writer Agent]
    O --> P[ReportData Output]
    P --> Q[Display Final Report]
    
    Q --> R[Show Follow-up Questions]
    R --> S[End]
    
    %% Styling
    classDef agentClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef toolClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef processClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class F,J,O agentClass
    class K toolClass
    class G,L,P dataClass
    class B,H,N processClass
```

## Agent Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant ResearchManager
    participant PlannerAgent
    participant SearchAgent
    participant WebSearchTool
    participant WriterAgent
    participant Printer

    User->>ResearchManager: Input query
    ResearchManager->>ResearchManager: Generate trace_id
    ResearchManager->>Printer: Initialize progress display
    
    ResearchManager->>PlannerAgent: Query for search plan
    PlannerAgent-->>ResearchManager: WebSearchPlan (structured output)
    
    loop For each batch of searches
        ResearchManager->>SearchAgent: Search term + reason
        SearchAgent->>WebSearchTool: Perform web search
        WebSearchTool-->>SearchAgent: Search results
        SearchAgent-->>ResearchManager: Summarized results
        ResearchManager->>Printer: Update progress
    end
    
    ResearchManager->>WriterAgent: Query + search results
    WriterAgent-->>ResearchManager: ReportData (markdown + questions)
    
    ResearchManager->>Printer: Display final report
    ResearchManager-->>User: Complete research report
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Layer"
        A[User Query]
    end
    
    subgraph "Planning Layer"
        B[Planner Agent]
        C[WebSearchPlan<br/>- searches: List[WebSearchItem]<br/>- reason: str<br/>- query: str]
    end
    
    subgraph "Execution Layer"
        D[Search Agent]
        E[WebSearchTool]
        F[Search Results<br/>List[str]]
    end
    
    subgraph "Synthesis Layer"
        G[Writer Agent]
        H[ReportData<br/>- short_summary: str<br/>- markdown_report: str<br/>- follow_up_questions: List[str]]
    end
    
    subgraph "Output Layer"
        I[Final Report]
        J[Follow-up Questions]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    H --> J
    
    classDef inputClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef planningClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef executionClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef synthesisClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef outputClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class A inputClass
    class B,C planningClass
    class D,E,F executionClass
    class G,H synthesisClass
    class I,J outputClass
``` 