# System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph "Load Balancer"
        LB[Nginx/HAProxy]
    end

    subgraph "Application Layer"
        App1[Flask App 1]
        App2[Flask App 2]
        App3[Flask App N]
    end

    subgraph "Background Workers"
        Celery1[Celery Worker 1]
        Celery2[Celery Worker 2]
    end

    subgraph "Caching Layer"
        Redis[(Redis Cache)]
    end

    subgraph "Database Layer"
        MongoDB[(MongoDB Replica Set)]
        Primary[(Primary)]
        Secondary1[(Secondary)]
        Secondary2[(Secondary)]
    end

    subgraph "Message Queue"
        RabbitMQ[RabbitMQ]
    end

    subgraph "External Services"
        OpenAI[OpenAI API]
        Email[Email Service]
    end

    subgraph "Monitoring & Tracing"
        Prometheus[Prometheus]
        Grafana[Grafana]
        Jaeger[Jaeger]
    end

    Web --> LB
    Mobile --> LB
    LB --> App1
    LB --> App2
    LB --> App3

    App1 --> Redis
    App2 --> Redis
    App3 --> Redis

    App1 --> MongoDB
    App2 --> MongoDB
    App3 --> MongoDB

    MongoDB --> Primary
    Primary --> Secondary1
    Primary --> Secondary2

    App1 --> RabbitMQ
    App2 --> RabbitMQ
    App3 --> RabbitMQ

    RabbitMQ --> Celery1
    RabbitMQ --> Celery2

    App1 --> OpenAI
    Celery1 --> Email

    App1 --> Jaeger
    App2 --> Jaeger
    Prometheus --> Grafana
```

## Component Diagram

```mermaid
graph LR
    subgraph "Frontend"
        UI[Web UI]
        MobileUI[Mobile UI]
    end

    subgraph "API Gateway"
        Gateway[API Gateway<br/>Rate Limiting<br/>Authentication]
    end

    subgraph "Core Services"
        Auth[Auth Service]
        Submission[Submission Service]
        Grading[AI Grading Service]
        Plagiarism[Plagiarism Service]
        Gamification[Gamification Service]
    end

    subgraph "Data Layer"
        UserDB[(User Data)]
        SubmissionDB[(Submissions)]
        AnalyticsDB[(Analytics)]
    end

    UI --> Gateway
    MobileUI --> Gateway
    Gateway --> Auth
    Gateway --> Submission
    Gateway --> Grading
    Gateway --> Plagiarism
    Gateway --> Gamification

    Auth --> UserDB
    Submission --> SubmissionDB
    Grading --> SubmissionDB
    Plagiarism --> SubmissionDB
    Gamification --> UserDB
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant Student
    participant WebApp
    participant API
    participant Redis
    participant AIService
    participant MongoDB
    participant Celery

    Student->>WebApp: Submit Code
    WebApp->>API: POST /api/submissions/submit
    API->>Redis: Check Rate Limit
    Redis-->>API: OK
    API->>MongoDB: Save Submission
    MongoDB-->>API: Submission ID
    API->>Celery: Queue Grading Task
    API-->>WebApp: 202 Accepted
    WebApp-->>Student: Grading in Progress

    Celery->>AIService: Grade Code
    AIService-->>Celery: Results
    Celery->>MongoDB: Update Submission
    Celery->>Redis: Cache Results
    Celery->>WebApp: WebSocket Update
    WebApp-->>Student: Show Results
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "AWS/Azure/GCP"
            subgraph "Kubernetes Cluster"
                Ingress[Ingress Controller]
                subgraph "Application Pods"
                    Pod1[Flask Pod 1]
                    Pod2[Flask Pod 2]
                    Pod3[Flask Pod 3]
                end
                subgraph "Worker Pods"
                    Worker1[Celery Pod 1]
                    Worker2[Celery Pod 2]
                end
            end

            subgraph "Managed Services"
                RDS[(Managed MongoDB)]
                ElastiCache[(Redis)]
                S3[Object Storage]
            end

            subgraph "Monitoring"
                CloudWatch[CloudWatch/Azure Monitor]
                APM[Application Insights]
            end
        end

        CDN[CloudFront/Azure CDN]
    end

    Users[Users] --> CDN
    CDN --> Ingress
    Ingress --> Pod1
    Ingress --> Pod2
    Ingress --> Pod3

    Pod1 --> RDS
    Pod2 --> RDS
    Pod3 --> RDS

    Pod1 --> ElastiCache
    Pod2 --> ElastiCache

    Worker1 --> RDS
    Worker2 --> RDS

    Pod1 --> S3
    Worker1 --> S3

    Pod1 --> CloudWatch
    Pod2 --> CloudWatch
    Pod1 --> APM
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        WAF[Web Application Firewall]
        DDoS[DDoS Protection]

        subgraph "Application Security"
            RateLimit[Rate Limiting]
            Auth[JWT Authentication]
            RBAC[Role-Based Access Control]
            InputVal[Input Validation]
            XSS[XSS Protection]
            CSRF[CSRF Protection]
        end

        subgraph "Data Security"
            Encryption[Encryption at Rest]
            TLS[TLS 1.3]
            Secrets[Secret Management]
        end

        subgraph "Monitoring"
            SIEM[Security Monitoring]
            Audit[Audit Logs]
            Alerts[Security Alerts]
        end
    end

    Internet[Internet] --> WAF
    WAF --> DDoS
    DDoS --> RateLimit
    RateLimit --> Auth
    Auth --> RBAC
    RBAC --> Application[Application]

    Application --> Encryption
    Application --> TLS
    TLS --> Database[(Database)]

    Application --> SIEM
    SIEM --> Audit
    Audit --> Alerts
```

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ SUBMISSIONS : creates
    USERS ||--o{ ACHIEVEMENTS : earns
    USERS {
        ObjectId _id
        string email
        string password_hash
        string name
        string role
        datetime created_at
        object profile
    }

    SUBMISSIONS ||--|| GRADING_RESULTS : has
    SUBMISSIONS ||--o{ PLAGIARISM_CHECKS : undergoes
    SUBMISSIONS {
        ObjectId _id
        ObjectId user_id
        ObjectId assignment_id
        string code
        string language
        datetime submitted_at
        string status
    }

    ASSIGNMENTS ||--o{ SUBMISSIONS : receives
    ASSIGNMENTS ||--o{ TEST_CASES : contains
    ASSIGNMENTS {
        ObjectId _id
        string title
        string description
        datetime deadline
        ObjectId creator_id
        array test_cases
    }

    GRADING_RESULTS {
        ObjectId _id
        ObjectId submission_id
        number score
        array test_results
        object feedback
        datetime graded_at
    }

    PLAGIARISM_CHECKS {
        ObjectId _id
        ObjectId submission_id
        number similarity_score
        array matches
        boolean flagged
        datetime checked_at
    }

    ACHIEVEMENTS {
        ObjectId _id
        ObjectId user_id
        string achievement_type
        datetime earned_at
        number points
    }
```

## Technology Stack

```mermaid
graph TB
    subgraph "Frontend"
        HTML[HTML5]
        CSS[CSS3 + TailwindCSS]
        JS[JavaScript]
        D3[D3.js]
        IntroJS[Intro.js]
    end

    subgraph "Mobile"
        RN[React Native]
        RNNav[React Navigation]
    end

    subgraph "Backend"
        Flask[Flask]
        Celery[Celery]
        Python[Python 3.11+]
    end

    subgraph "Databases"
        MongoDB[MongoDB]
        Redis[Redis]
    end

    subgraph "AI/ML"
        OpenAI[OpenAI API]
        NLP[NLTK/spaCy]
    end

    subgraph "DevOps"
        Docker[Docker]
        K8s[Kubernetes]
        GitHub[GitHub Actions]
    end

    subgraph "Monitoring"
        Prometheus[Prometheus]
        Grafana[Grafana]
        Jaeger[Jaeger]
        Sentry[Sentry]
    end
```

## Scaling Strategy

```mermaid
graph LR
    subgraph "Horizontal Scaling"
        LB[Load Balancer]
        App1[App Instance 1]
        App2[App Instance 2]
        App3[App Instance N]
    end

    subgraph "Database Scaling"
        Primary[(Primary)]
        Secondary1[(Read Replica 1)]
        Secondary2[(Read Replica 2)]
        Sharding[Sharding Strategy]
    end

    subgraph "Caching"
        L1[Application Cache]
        L2[Redis Cache]
        CDN[CDN Cache]
    end

    LB --> App1
    LB --> App2
    LB --> App3

    App1 --> Primary
    App2 --> Secondary1
    App3 --> Secondary2

    Primary --> Sharding

    App1 --> L1
    L1 --> L2
    L2 --> CDN
```
