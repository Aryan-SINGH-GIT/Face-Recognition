# Entity Relationship Diagram (ERD)
# Face Recognition & Access Control System

**Project:** Face Recognition System Multimodal AI  
**Developer:** Aryan Singh (Reg No: 240410700030)  
**Semester:** 5th Semester  

---

## 1. System Entity Relationship Diagram

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
    'edgeLabelBackground': '#1e293b',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
erDiagram
    USERS ||--o{ FACE_ENROLLMENTS : "has biometric profiles"
    USERS ||--o{ ACCESS_LOGS : "generates events"
    USERS }o--|| ROLES : "assigned to"
    ACCESS_DEVICES ||--o{ ACCESS_LOGS : "captures at terminal"
    ROLES ||--o{ PERMISSION_POLICIES : "governs access"

    USERS {
        uuid user_id PK
        string employee_code UK
        string full_name
        string email UK
        string department
        string role_id FK
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    FACE_ENROLLMENTS {
        uuid enrollment_id PK
        uuid user_id FK
        int faiss_index_id "Index pointer in Vector DB"
        int embedding_dimension "Default 512"
        string model_architecture "InceptionResnetV1"
        string model_weights "vggface2"
        string face_image_path "Encrypted storage URI"
        float detection_confidence "MTCNN score"
        timestamp enrolled_at
    }

    ACCESS_DEVICES {
        uuid device_id PK
        string device_name "e.g., Main Entrance Turnstile"
        string location_zone "e.g., Floor 2 - Data Center"
        string ip_address
        string device_status "ONLINE / OFFLINE"
        float distance_threshold "e.g., 1.0 or 1.2"
        timestamp last_heartbeat
    }

    ACCESS_LOGS {
        uuid log_id PK
        uuid user_id FK "Nullable if unknown face"
        uuid device_id FK
        string verification_status "GRANTED / DENIED / NO_FACE"
        float l2_distance "Euclidean distance from Faiss"
        float confidence_score "1 - normalized distance"
        string matched_identity "Identity string label"
        string snapshot_image_path "Audit trail image"
        timestamp captured_at
    }

    ROLES {
        string role_id PK "ADMIN / EMPLOYEE / VISITOR"
        string role_name
        string description
    }

    PERMISSION_POLICIES {
        uuid policy_id PK
        string role_id FK
        string zone_name "e.g., Server Room, Executive Office"
        time allowed_start_time
        time allowed_end_time
        boolean requires_two_factor
    }
```

---

## 2. Relational Mapping & Vector DB Hybrid Model

In an enterprise multimodal AI architecture:
- **Relational Metadata (PostgreSQL / SQLite):** Stores user identity profiles, device credentials, audit logs, and access policies.
- **In-Memory Vector Store (Faiss):** Stores the dense 512-dimensional floating-point embeddings (`IndexFlatL2`).
- **Foreign Key Bridge:** `FACE_ENROLLMENTS.faiss_index_id` maps the relational record directly to the internal position in `index.faiss` and `identities.json`.

### Hybrid Storage Architecture

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
    subgraph RELATIONAL["Relational Store (SQLite / PostgreSQL)"]
        direction TB
        T_USERS["USERS\nemployee_code, email, role"]
        T_ENROLL["FACE_ENROLLMENTS\nfaiss_index_id, model_weights"]
        T_LOGS["ACCESS_LOGS\nstatus, l2_distance, identity"]
        T_ROLES["ROLES + PERMISSION_POLICIES"]
    end

    subgraph VECTOR_STORE["Vector Store (Faiss)"]
        direction TB
        V_FAISS["index.faiss\nIndexFlatL2\nN × 512 float32"]
        V_MAP["identities.json\nList of identity strings\n(positional mapping)"]
    end

    T_ENROLL -->|"faiss_index_id (int)\n→ row index in Faiss"| V_FAISS
    T_ENROLL -->|"identity label position"| V_MAP
    V_FAISS -->|"k-NN search result index"| T_LOGS
    V_MAP -->|"identity name lookup"| T_LOGS

    classDef relNode fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef vecNode fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#f8fafc;

    class T_USERS,T_ENROLL,T_LOGS,T_ROLES relNode;
    class V_FAISS,V_MAP vecNode;
```

---

## 3. Data Dictionary

| Table | Column | Type | Constraints | Description |
|---|---|---|---|---|
| `USERS` | `user_id` | UUID | PK, NOT NULL | Unique identifier for employee |
| `USERS` | `employee_code` | VARCHAR(50) | UNIQUE, NOT NULL | Organization badge/ID code |
| `USERS` | `full_name` | VARCHAR(100) | NOT NULL | Display name |
| `FACE_ENROLLMENTS` | `enrollment_id` | UUID | PK, NOT NULL | Unique face sample entry |
| `FACE_ENROLLMENTS` | `faiss_index_id` | INTEGER | NOT NULL | Row index in Faiss vector matrix |
| `FACE_ENROLLMENTS` | `embedding_dimension` | INTEGER | DEFAULT 512 | Length of feature vector |
| `ACCESS_DEVICES` | `device_id` | UUID | PK, NOT NULL | Edge camera or turnstile reader |
| `ACCESS_LOGS` | `log_id` | UUID | PK, NOT NULL | Immutable verification log entry |
| `ACCESS_LOGS` | `l2_distance` | FLOAT | NULLABLE | Vector distance from nearest neighbor |
| `ACCESS_LOGS` | `verification_status` | ENUM | NOT NULL | `GRANTED`, `DENIED`, `NO_FACE` |
