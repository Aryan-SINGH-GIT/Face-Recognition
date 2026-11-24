# High Level System Design (HLD)
# Face Recognition & Access Control System — Multimodal AI

**Developer:** Aryan Singh (Reg No: 240410700030)  
**Semester:** 5th Semester  
**Project Track:** Face Recognition System Multimodal AI  
**Version:** 2.0.0  

---

## 1. Executive System Overview

The **Enterprise Multimodal Face Recognition & Access Control System** provides real-time, zero-shot biometric identity verification, employee enrollment, anti-spoofing liveness verification, and tamper-evident audit logging. 

It fuses deep convolutional neural networks (**MTCNN** and **Inception-ResNet-v1 FaceNet**) with high-performance vector indexing (**Facebook AI Similarity Search - Faiss**) and an asynchronous REST API layer (**FastAPI**), managed by a secure **React** single-page management dashboard.

---

## 2. End-to-End System Architecture (Macro View)

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'mainBkg': '#1e293b',
    'textColor': '#f8fafc',
    'primaryColor': '#1e293b',
    'primaryTextColor': '#f8fafc',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#38bdf8',
    'secondaryColor': '#334155',
    'tertiaryColor': '#0f172a'
  }
}}%%
flowchart TB
    subgraph CLIENT_LAYER["🖥️ Client & Edge Ingestion Layer"]
        direction LR
        UI["React SPA Dashboard\n(Vite + TailwindCSS)"]
        CAM["Edge Camera / CCTV\n(Webcam / RTSP Stream)"]
        TURN["Access Turnstile /\nPhysical Edge Relay"]
    end

    subgraph GATEWAY_LAYER["🛡️ Security & API Gateway Layer"]
        direction TB
        PROXY["Reverse Proxy / Nginx\n(TLS 1.3 Termination & Rate Limiting)"]
        CORS["CORS & Request Sanity\n(Payload Validation & Multipart Handler)"]
        AUTH["JWT Authenticator\n(Admin RBAC Token Verification)"]
    end

    subgraph APP_LAYER["⚡ FastAPI Application & Orchestration Layer"]
        direction TB
        ROUTER["API Routers\n(/verify, /enroll, /auth, /logs)"]
        LIVENESS["Anti-Spoofing Liveness Engine\n(Laplacian Variance + Texture Analysis)"]
        SERVICE["FaceService Core Orchestrator\n(Model Pre-warm & Inference Director)"]
        AUDITOR["Audit Logger & Event Recorder\n(Persistent Access History)"]
    end

    subgraph AI_INFERENCE_LAYER["🧠 Deep Learning Biometric Inference Engine"]
        direction LR
        MTCNN_MOD["MTCNN Detector & Aligner\n(P-Net ➔ R-Net ➔ O-Net Cascade)\nTarget: 3 × 160 × 160"]
        FACENET_MOD["InceptionResnetV1 (FaceNet)\nPretrained: VGGFace2\nOutput: 512-D L2 Normalized Vector"]
    end

    subgraph PERSISTENCE_LAYER["💾 Persistence & Vector Storage Layer"]
        direction LR
        FAISS_STORE[("Faiss Vector Index\n(IndexFlatL2: 512-D\nindex.faiss")]
        MAPPING_STORE[("Identity Registry\n(JSON Name Pointer\nidentities.json")]
        RELATIONAL_DB[("Relational Database\n(SQLite / PostgreSQL\nAdmin & Audit Logs)")]
    end

    %% Connections
    CAM -->|"Raw Video Stream / Snapshots"| UI
    UI -->|"HTTPS / Multipart Form POST"| PROXY
    PROXY --> CORS --> ROUTER
    AUTH -.->|"Protects Admin Routes"| ROUTER

    ROUTER -->|"Verify Request"| LIVENESS
    LIVENESS -->|"Real Live Human"| SERVICE
    LIVENESS -.->|"Spoof Detected"| AUDITOR

    SERVICE -->|"1. Raw Image"| MTCNN_MOD
    MTCNN_MOD -->|"2. Cropped & Aligned Face"| FACENET_MOD
    FACENET_MOD -->|"3. 512-D Query Vector"| SERVICE

    SERVICE -->|"4. Fast k-NN Search"| FAISS_STORE
    FAISS_STORE -->|"5. Nearest Distance + Index"| SERVICE
    SERVICE -->|"6. Resolve Index Name"| MAPPING_STORE
    
    SERVICE -->|"7. Log Access Decision"| AUDITOR
    AUDITOR -->|"Insert AccessLog"| RELATIONAL_DB
    
    SERVICE -->|"8. Verification Result"| UI
    UI -->|"Trigger Door Relay (Grant)"| TURN

    classDef edgeClass fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef gateClass fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#f8fafc;
    classDef appClass fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#f8fafc;
    classDef mlClass fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef storeClass fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#f8fafc;

    class UI,CAM,TURN edgeClass;
    class PROXY,CORS,AUTH gateClass;
    class ROUTER,LIVENESS,SERVICE,AUDITOR appClass;
    class MTCNN_MOD,FACENET_MOD mlClass;
    class FAISS_STORE,MAPPING_STORE,RELATIONAL_DB storeClass;
```

---

## 3. Tiered / Layered Architecture Diagram

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'mainBkg': '#1e293b',
    'textColor': '#f8fafc',
    'primaryColor': '#1e293b',
    'primaryTextColor': '#f8fafc',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#38bdf8'
  }
}}%%
flowchart TD
    subgraph PRESENTATION["1. Presentation Tier (Frontend UI)"]
        direction LR
        P1["Live Webcam Feed & Overlay"]
        P2["Biometric Verification HUD"]
        P3["Employee Enrollment Panel"]
        P4["Audit Logs & Analytics Dashboard"]
    end

    subgraph API_GATEWAY["2. Gateway & Security Tier"]
        direction LR
        G1["FastAPI CORS Middleware"]
        G2["JWT Bearer Authentication"]
        G3["Pydantic v2 Request/Response Validation"]
    end

    subgraph APPLICATION_SERVICES["3. Core Business & Application Services Tier"]
        direction LR
        S1["FaceService Core Engine"]
        S2["LivenessService (Anti-Spoofing)"]
        S3["SecurityService (Password Hashing / Tokens)"]
        S4["AuditService (Access Tracking)"]
    end

    subgraph AI_PIPELINE["4. Deep Learning AI & Vision Tier"]
        direction LR
        M1["MTCNN Face Detector & Landmark Aligner"]
        M2["FaceNet (Inception-ResNet-v1) Feature Extractor"]
        M3["PyTorch CUDA / CPU Tensor Runtime Engine"]
    end

    subgraph DATA_PERSISTENCE["5. Persistence & Vector Storage Tier"]
        direction LR
        D1["Faiss IndexFlatL2 (In-Memory + Disk Sync)"]
        D2["SQLite / PostgreSQL DB (SQLAlchemy ORM)"]
        D3["Identity Label Mapping (identities.json)"]
    end

    PRESENTATION ==> API_GATEWAY
    API_GATEWAY ==> APPLICATION_SERVICES
    APPLICATION_SERVICES ==> AI_PIPELINE
    APPLICATION_SERVICES ==> DATA_PERSISTENCE
    AI_PIPELINE -.->|"Write/Query Vectors"| DATA_PERSISTENCE

    classDef tier1 fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef tier2 fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#f8fafc;
    classDef tier3 fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#f8fafc;
    classDef tier4 fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef tier5 fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#f8fafc;

    class P1,P2,P3,P4 tier1;
    class G1,G2,G3 tier2;
    class S1,S2,S3,S4 tier3;
    class M1,M2,M3 tier4;
    class D1,D2,D3 tier5;
```

---

## 4. End-to-End Operational Workflows

### 4.1 Verification & Access Decision Flow (High Level)

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'mainBkg': '#1e293b',
    'textColor': '#f8fafc',
    'primaryColor': '#1e293b',
    'primaryTextColor': '#f8fafc',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#38bdf8'
  }
}}%%
flowchart TD
    START(["👤 User Approaches Camera"]) --> CAPTURE["Edge Camera Captures Frame (JPEG/PNG)"]
    CAPTURE --> API_CALL["POST /verify (Multipart Image)"]
    API_CALL --> LIVENESS{"Anti-Spoofing Filter\nLiveness Score > 100.0?"}

    LIVENESS -- "Fake / Photo / Screen (Spoof)" --> LOG_SPOOF["Create Audit Log: SPOOF_DETECTED"]
    LOG_SPOOF --> DENY_SPOOF(["⛔ ACCESS DENIED: Liveness Failed"])

    LIVENESS -- "Real Human Face" --> DETECT{"MTCNN Detects Face?\nBounding Box & Landmarks"}
    
    DETECT -- "No Face Detected" --> LOG_NOFACE["Create Audit Log: NO_FACE"]
    LOG_NOFACE --> DENY_NOFACE(["⚠️ NO FACE DETECTED"])

    DETECT -- "Face Cropped & Aligned" --> ENCODE["FaceNet Extracts 512-D L2 Embedding"]
    ENCODE --> SEARCH["Faiss IndexFlatL2 k-NN Search (k=1)"]
    SEARCH --> THRESHOLD{"Euclidean Distance < 1.2?"}

    THRESHOLD -- "Yes (Distance <= 1.2)" --> RESOLVE["Resolve Identity from identities.json"]
    RESOLVE --> LOG_GRANT["Create Audit Log: GRANTED\nIdentity, Distance, Confidence"]
    LOG_GRANT --> GRANT(["✅ ACCESS GRANTED: Door Unlocked"])

    THRESHOLD -- "No (Distance > 1.2)" --> LOG_DENY["Create Audit Log: DENIED\nUnknown Person"]
    LOG_DENY --> DENY_UNKNOWN(["🚫 ACCESS DENIED: Unknown Face"])

    classDef startClass fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef decisionClass fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef grantClass fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef denyClass fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc;
    classDef stepClass fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;

    class START,CAPTURE,API_CALL,ENCODE,SEARCH,RESOLVE stepClass;
    class LIVENESS,DETECT,THRESHOLD decisionClass;
    class LOG_GRANT,GRANT grantClass;
    class LOG_SPOOF,DENY_SPOOF,LOG_NOFACE,DENY_NOFACE,LOG_DENY,DENY_UNKNOWN denyClass;
```

---

### 4.2 Zero-Shot Employee Enrollment Workflow (High Level)

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'mainBkg': '#1e293b',
    'textColor': '#f8fafc',
    'primaryColor': '#1e293b',
    'primaryTextColor': '#f8fafc',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#38bdf8'
  }
}}%%
flowchart LR
    ADMIN(["Security Admin"]) -->|"Enters Identity Name +\nUploads HD Portrait"| UI["Admin Portal (React)"]
    UI -->|"POST /enroll\n(Bearer JWT Token)"| GATEWAY["FastAPI Gateway"]
    GATEWAY -->|"Verify Admin Token"| AUTH["Security Engine"]
    AUTH -->|"Authorized"| MTCNN["MTCNN Face Detector"]
    MTCNN -->|"Extracts 160×160 Crop"| FACENET["InceptionResnetV1 Encoder"]
    FACENET -->|"512-D float32 Vector"| FAISS["FaissManager Engine"]
    
    subgraph ATOMIC_PERSIST["Atomic Storage Persistence"]
        direction TB
        FAISS -->|"1. index.add(vector)"| VEC_FILE[("index.faiss")]
        FAISS -->|"2. identities.append(name)"| MAP_FILE[("identities.json")]
    end
    
    ATOMIC_PERSIST -->|"Success Confirmation"| RESP["HTTP 200: Successfully Enrolled"]
    RESP --> UI

    classDef nodeStyle fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef persistStyle fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#f8fafc;
    classDef successStyle fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;

    class ADMIN,UI,GATEWAY,AUTH,MTCNN,FACENET,FAISS nodeStyle;
    class VEC_FILE,MAP_FILE persistStyle;
    class RESP successStyle;
```

---

## 5. Security & Trust Boundary Architecture

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'mainBkg': '#1e293b',
    'textColor': '#f8fafc',
    'primaryColor': '#1e293b',
    'primaryTextColor': '#f8fafc',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#38bdf8'
  }
}}%%
flowchart TB
    subgraph UNTRUSTED_ZONE["🌐 Untrusted / External Zone"]
        CAM["Edge Camera Terminal"]
        BROWSER["Web Client / Browser"]
    end

    subgraph DMZ_ZONE["🛡️ Demilitarized Zone (DMZ)"]
        NGINX["Reverse Proxy (Nginx)"]
        WAF["Rate Limiting & DDoS Shield"]
        TLS["TLS 1.3 Termination"]
    end

    subgraph TRUSTED_APP_ZONE["🔒 Trusted Application Core Zone"]
        FASTAPI["FastAPI ASGI Server (Uvicorn)"]
        AUTH_GUARD["OAuth2 / JWT RBAC Guard"]
        LIVENESS_FILTER["Passive Liveness Filter"]
        INFERENCE_ENG["PyTorch Inference (MTCNN + FaceNet)"]
    end

    subgraph DATA_VAULT_ZONE["🗄️ Biometric Data & Vault Zone"]
        FAISS_VAULT["Faiss Vector Vault (index.faiss)"]
        MAP_VAULT["Identity Registry (identities.json)"]
        SQL_VAULT["Relational DB (access_control.db)"]
    end

    CAM -->|"HTTPS Request"| NGINX
    BROWSER -->|"HTTPS Request"| NGINX
    NGINX --> WAF --> TLS
    TLS -->|"Internal Network Traffic"| FASTAPI
    FASTAPI --> AUTH_GUARD
    AUTH_GUARD --> LIVENESS_FILTER --> INFERENCE_ENG
    INFERENCE_ENG -->|"Internal Bus"| FAISS_VAULT
    INFERENCE_ENG -->|"Internal Bus"| MAP_VAULT
    FASTAPI -->|"SQLAlchemy ORM"| SQL_VAULT

    classDef untrusted fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc;
    classDef dmz fill:#312e81,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef trusted fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef vault fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;

    class CAM,BROWSER untrusted;
    class NGINX,WAF,TLS dmz;
    class FASTAPI,AUTH_GUARD,LIVENESS_FILTER,INFERENCE_ENG trusted;
    class FAISS_VAULT,MAP_VAULT,SQL_VAULT vault;
```

---

## 6. AWS Cloud Deployment & Infrastructure Topology Diagram

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'mainBkg': '#1e293b',
    'textColor': '#f8fafc',
    'primaryColor': '#1e293b',
    'primaryTextColor': '#f8fafc',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#38bdf8'
  }
}}%%
flowchart TB
    subgraph CLIENT_EDGE["🖥️ Client & Edge Devices"]
        WEB_CLIENT["Admin Workstation\n(React Web Dashboard)"]
        TURNSTILE_CAM["Edge Camera / Turnstile\n(RTSP / Video Stream Snapshot)"]
    end

    subgraph AWS_EDGE_TIER["🌐 AWS Edge & Security Tier"]
        R53["Amazon Route 53\n(Global DNS Routing)"]
        ACM["AWS Certificate Manager (ACM)\n(Free SSL/TLS Certificates)"]
        WAF["AWS WAF\n(DDoS & Rate Limiting)"]
        CF["Amazon CloudFront (CDN)\n(Global Edge Caching)"]
    end

    subgraph AWS_FRONTEND["📦 Static Web Hosting Tier"]
        S3_FRONT["Amazon S3 Bucket\n(React + Vite Static Build: HTML/JS/CSS)"]
    end

    subgraph AWS_VPC["🛡️ AWS Virtual Private Cloud (VPC)"]
        subgraph PUBLIC_SUBNET["Public Subnet"]
            ALB["Application Load Balancer (ALB)\n(HTTPS Port 443 Termination)"]
            NAT["NAT Gateway\n(Outbound Internet for Updates)"]
        end

        subgraph PRIVATE_APP_SUBNET["Private Application Subnet (Compute)"]
            subgraph ECS_CLUSTER["AWS ECS / EKS Cluster (or EC2 Compute)"]
                TASK_1["FastAPI Backend Task 1\n(Uvicorn + PyTorch + MTCNN + FaceNet)"]
                TASK_2["FastAPI Backend Task 2\n(Auto-Scaled Replica)"]
            end
            SECRETS["AWS Secrets Manager\n(JWT Secret, DB Passwords)"]
        end

        subgraph PRIVATE_DATA_SUBNET["Private Data & Storage Subnet"]
            EFS_STORE[("Amazon EFS (Shared Elastic File System)\n• index.faiss (512-D Vectors)\n• identities.json (Name Map)")]
            RDS_DB[("Amazon RDS PostgreSQL\n(Multi-AZ Active/Standby)\n• Users & Roles\n• Access Logs & Audits")]
            S3_AUDIT[("Amazon S3 Audit Bucket\n(Encrypted Snapshot Photos)")]
        end
    end

    %% Edge & Frontend Flows
    WEB_CLIENT -->|"1. HTTPS Request"| R53
    R53 --> CF
    ACM -.->|"SSL Certificate"| CF
    WAF --- CF
    CF -->|"2. Load Static Assets"| S3_FRONT

    %% API Verification & Admin Flows
    WEB_CLIENT -->|"3. REST API /auth, /enroll, /logs"| ALB
    TURNSTILE_CAM -->|"3. POST /verify (Image Payload)"| ALB
    ACM -.->|"SSL Certificate"| ALB
    WAF --- ALB

    ALB -->|"4. Load Balances Traffic"| TASK_1
    ALB -->|"4. Load Balances Traffic"| TASK_2

    %% Backend Dependencies & Storage Connections
    TASK_1 -.->|"Fetch Config"| SECRETS
    TASK_2 -.->|"Fetch Config"| SECRETS

    TASK_1 ==>|"5. Vector I/O (Read/Write)"| EFS_STORE
    TASK_2 ==>|"5. Vector I/O (Read/Write)"| EFS_STORE

    TASK_1 ==>|"6. SQLAlchemy ORM (SQL Logs)"| RDS_DB
    TASK_2 ==>|"6. SQLAlchemy ORM (SQL Logs)"| RDS_DB

    TASK_1 -.->|"7. Archive Face Snapshots"| S3_AUDIT
    TASK_2 -.->|"7. Archive Face Snapshots"| S3_AUDIT

    classDef clientStyle fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef edgeStyle fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#f8fafc;
    classDef frontStyle fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#f8fafc;
    classDef vpcStyle fill:#0f172a,stroke:#334155,stroke-width:2px,color:#f8fafc;
    classDef appStyle fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef dataStyle fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;

    class WEB_CLIENT,TURNSTILE_CAM clientStyle;
    class R53,ACM,WAF,CF,ALB,NAT edgeStyle;
    class S3_FRONT frontStyle;
    class AWS_VPC,PUBLIC_SUBNET,PRIVATE_APP_SUBNET,PRIVATE_DATA_SUBNET,ECS_CLUSTER vpcStyle;
    class TASK_1,TASK_2,SECRETS appStyle;
    class EFS_STORE,RDS_DB,S3_AUDIT dataStyle;
```

### AWS Service Mapping & Architecture Decisions

| System Layer | AWS Service | Purpose in Architecture | Key Technical Rationale |
|---|---|---|---|
| **Frontend CDN & DNS** | **Amazon CloudFront + Route 53** | Global distribution of React single-page app and DNS resolution. | Edge caching reduces UI latency to < 50ms worldwide and offloads traffic from backend servers. |
| **Frontend Storage** | **Amazon S3 (Simple Storage Service)** | Host compiled static web assets (`index.html`, JavaScript, CSS). | Serverless, highly available (99.999999999% durability), and costs pennies per month compared to running a VM. |
| **SSL / TLS Encryption** | **AWS Certificate Manager (ACM)** | Manages public HTTPS certificates for CloudFront and ALB. | Free, auto-renewing SSL certificates securing communication from cameras and web browsers. |
| **API Gateway & Routing** | **Application Load Balancer (ALB)** | Reverse proxy, path routing (`/api/*`), and SSL termination. | Automatically health-checks FastAPI workers and distributes incoming verification traffic evenly. |
| **Compute & Inference** | **AWS ECS (Fargate) or EC2 (`g4dn` / `t3.large`)** | Runs containerized FastAPI, PyTorch (MTCNN + FaceNet), and Liveness engine. | Keeps heavy neural network weights pre-warmed in memory (eliminating the 5-10s cold-start delays of AWS Lambda). |
| **Vector Database Storage** | **Amazon EFS (Elastic File System)** | Persistent shared file system for `index.faiss` and `identities.json`. | Native POSIX network file system mountable across auto-scaled container tasks without rewriting Faiss code. |
| **Relational Database** | **Amazon RDS PostgreSQL (Multi-AZ)** | Stores admin users, credentials, roles, and immutable verification audit logs. | Fully managed SQL engine with automatic backups, failover, and zero-code migration via existing SQLAlchemy ORM. |
| **Secrets & Credentials** | **AWS Secrets Manager** | Stores JWT signing secret, database passwords, and encryption keys. | Eliminates plaintext secrets in source code and enables automatic credential rotation. |

---

## 7. State Machine Diagram: Access Verification Lifecycle

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'mainBkg': '#1e293b',
    'textColor': '#f8fafc',
    'primaryColor': '#1e293b',
    'primaryTextColor': '#f8fafc',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#38bdf8'
  }
}}%%
stateDiagram-v2
    [*] --> Standby: System Initialized (Models Pre-warmed)
    Standby --> FrameAcquired: Camera snapshot uploaded (/verify)
    
    FrameAcquired --> LivenessValidation: Check Laplacian variance & texture
    LivenessValidation --> SpoofDetected: Variance < 100.0 (Spoof/Photo)
    LivenessValidation --> FaceDetection: Variance >= 100.0 (Live human)

    SpoofDetected --> AuditLogged: Log verification_status = "SPOOF_DETECTED"
    
    FaceDetection --> NoFaceFound: MTCNN detects 0 faces
    FaceDetection --> FaceAligned: MTCNN detects bounding box + 5 landmarks
    
    NoFaceFound --> AuditLogged: Log verification_status = "NO_FACE"
    
    FaceAligned --> FeatureExtraction: Crop to 160×160 & forward to FaceNet
    FeatureExtraction --> VectorSearch: Produce 512-D float32 vector & query Faiss
    
    VectorSearch --> MatchVerified: Nearest distance <= 1.2
    VectorSearch --> MatchRejected: Nearest distance > 1.2
    
    MatchVerified --> AuditLogged: Log status = "GRANTED", identity, distance
    MatchRejected --> AuditLogged: Log status = "DENIED", unknown person
    
    AuditLogged --> Standby: Response returned to client
