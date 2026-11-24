# Low Level System Design (LLD)
# Face Recognition System — Multimodal AI

**Developer:** Aryan Singh (Reg No: 240410700030)  
**Semester:** 5th Semester  
**Project:** Face Recognition System  

---

## Module 1: Faiss Manager (Database Layer)

### Class Diagram

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
    'classText': '#f8fafc',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
classDiagram
    class FaissManager {
        -String index_path
        -String mapping_path
        -int embedding_dim
        -IndexFlatL2 index
        -List~str~ identities
        
        +__init__(index_path, mapping_path, embedding_dim)
        +add_embeddings(embeddings, labels) void
        +search(query_embedding, k, threshold) List~Tuple~
        +save() void
        +load() void
    }

    class IndexFlatL2 {
        <<Faiss Internal>>
        -int d
        -int ntotal
        +add(x: float32 ndarray) void
        +search(x: float32 ndarray, k: int) Tuple
    }

    FaissManager --> IndexFlatL2 : wraps
```

### Data Structures

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
    A["embeddings_np\nType: numpy.ndarray\nShape: N × 512\ndtype: float32"] --> B["IndexFlatL2\n(Faiss Internal Store)"]
    C["identities\nType: List[str]\nLength: N\n[Bill_Frist, Bill_Frist, ...]"] --> D["identities.json\n(Persisted to Disk)"]
    B --> E["index.faiss\n(Persisted to Disk)"]

    classDef dataNode fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef storeNode fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#f8fafc;

    class A,C dataNode;
    class B,D,E storeNode;
```

---

## Module 2: ML Pipeline (Face Encoder)

### Class Diagram

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
    'classText': '#f8fafc',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
classDiagram
    class FaceEncoder {
        <<Script: face_encoder.py>>
        -device: torch.device
        -mtcnn: MTCNN
        -resnet: InceptionResnetV1
        -manager: FaissManager
        -loader: DataLoader
        -classes: List~str~

        +build_index() void
    }

    class MTCNN {
        <<facenet_pytorch>>
        -image_size: int = 160
        -margin: int = 0
        -min_face_size: int = 20
        -thresholds: List~float~
        -device: torch.device
        +__call__(img: PIL.Image) Tensor or None
    }

    class InceptionResnetV1 {
        <<facenet_pytorch>>
        -pretrained: str = vggface2
        +__call__(x: Tensor) Tensor
    }

    FaceEncoder --> MTCNN : uses
    FaceEncoder --> InceptionResnetV1 : uses
    FaceEncoder --> FaissManager : writes to
```

### Data Flow at Variable Level

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
    A["PIL.Image\n(Raw Image from Disk)"]
    B["face_tensor\nType: torch.Tensor\nShape: 3 x 160 x 160"]
    C["face_tensor batched\nType: torch.Tensor\nShape: 1 x 3 x 160 x 160"]
    D["embedding\nType: torch.Tensor\nShape: 1 x 512"]
    E["embedding_np\nType: numpy.ndarray\nShape: 512\ndtype: float32"]
    F["FaissManager.add_embeddings()"]

    A -->|"mtcnn(img)"| B
    B -->|"unsqueeze(0)"| C
    C -->|"resnet(face)"| D
    D -->|".squeeze().cpu().numpy()"| E
    E --> F

    classDef tensorNode fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef actionNode fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#f8fafc;

    class A,B,C,D,E tensorNode;
    class F actionNode;
```

---

## Module 3: Face Verification (test_match.py)

### Class Diagram

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
    'classText': '#f8fafc',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
classDiagram
    class FaceVerifier {
        <<Script: test_match.py>>
        -device: torch.device
        -mtcnn: MTCNN
        -resnet: InceptionResnetV1
        -manager: FaissManager
        -image_path: str

        +test_match(image_path: str) void
    }

    class MatchResult {
        <<Data Structure>>
        +identity: str
        +distance: float
    }

    FaceVerifier --> FaissManager : reads from
    FaceVerifier --> MatchResult : produces
```

### Search Data Flow

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
    A["Input Image\nPath: str"]
    B["PIL.Image RGB"]
    C["Cropped Face\ntorch.Tensor\n3 x 160 x 160"]
    D["Query Embedding\nnumpy.ndarray\nshape: 512"]
    E["Faiss Search\ndistances: float32 array\nindices: int64 array"]
    F{"distance < threshold 1.5?"}
    G["identities index\nstr — Bill_Frist"]
    H["MATCH FOUND\nReturn identity, distance"]
    I["NO MATCH\nReturn empty list"]

    A -->|"Image.open()"| B
    B -->|"mtcnn(img)"| C
    C -->|"resnet ➔ squeeze ➔ numpy"| D
    D -->|"index.search(query, k=3)"| E
    E --> F
    F -->|Yes| G --> H
    F -->|No| I

    classDef stepNode fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef decisionNode fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef successNode fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef failNode fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc;

    class A,B,C,D,E stepNode;
    class F decisionNode;
    class G,H successNode;
    class I failNode;
```

---

## Module 4: Dataset Loader

### Class Diagram

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
    'classText': '#f8fafc',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
classDiagram
    class DatasetLoader {
        <<Module: dataset.py>>
        -DATA_DIR: Path
        +get_dataloader(batch_size, num_workers) Tuple
        +collate_pil(batch) Tuple
        +pil_loader(path) PIL.Image
    }

    class ImageFolder {
        <<torchvision.datasets>>
        -root: Path
        -loader: Callable
        -classes: List~str~
        -class_to_idx: Dict~str, int~
        -samples: List~Tuple~
        +__getitem__(index) Tuple
        +__len__() int
    }

    class DataLoader {
        <<torch.utils.data>>
        -dataset: ImageFolder
        -batch_size: int
        -shuffle: bool
        -collate_fn: Callable
        +__iter__() Iterator
    }

    DatasetLoader --> ImageFolder : creates
    DatasetLoader --> DataLoader : wraps
```

---

## Module 5: FastAPI Backend

### Class / API Diagram

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
    'classText': '#f8fafc',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
classDiagram
    class FastAPIApp {
        <<backend/app/main.py>>
        -app: FastAPI
        -mtcnn: MTCNN
        -resnet: InceptionResnetV1
        -manager: FaissManager

        +lifespan() void
        +health_check() HealthResponse
        +get_system_config() ConfigResponse
        +register_admin(payload) TokenResponse
        +login_admin(payload) TokenResponse
        +verify_identity(file, threshold, check_liveness) VerifyResponse
        +enroll_new_identity(file, identity_name) EnrollResponse
        +list_enrolled_identities() IdentitiesResponse
        +delete_identity(name) DeleteIdentityResponse
        +get_access_logs(skip, limit) AccessLogsListResponse
        +get_analytics() AnalyticsSummaryResponse
    }

    class FaceService {
        <<app/services/face_service.py>>
        -device: torch.device
        -mtcnn: MTCNN
        -resnet: InceptionResnetV1
        -faiss_manager: FaissManager
        -default_threshold: float = 1.2

        +load_models() void
        +verify_face(image_bytes, threshold, check_liveness) dict
        +enroll_face(image_bytes, identity_name) dict
        +delete_identity(name) dict
        +get_stats() dict
    }

    class LivenessService {
        <<app/services/liveness_service.py>>
        +check_liveness(image: PIL.Image) dict
    }

    class FaissManager {
        <<ml/faiss_manager.py>>
        +add_embeddings(embeddings, labels) void
        +search(query_embedding, k, threshold) List~Tuple~
        +save() void
        +load() void
    }

    class VerifyResponse {
        <<Pydantic Schema>>
        +match_found: bool
        +identity: Optional~str~
        +distance: Optional~float~
        +confidence: Optional~float~
        +is_live: bool
        +liveness_score: Optional~float~
        +status: str
        +message: str
    }

    class AccessLog {
        <<db/models.py SQLAlchemy>>
        +id: int PK
        +status: str
        +matched_identity: Optional~str~
        +l2_distance: Optional~float~
        +confidence_score: Optional~float~
        +is_live: bool
        +liveness_score: Optional~float~
        +ip_address: str
        +message: str
        +created_at: datetime
    }

    class AdminUser {
        <<db/models.py SQLAlchemy>>
        +id: int PK
        +username: str UK
        +hashed_password: str
        +role: str
        +created_at: datetime
    }

    FastAPIApp --> FaceService : delegates to
    FastAPIApp --> AccessLog : persists
    FastAPIApp --> AdminUser : authenticates
    FaceService --> LivenessService : calls
    FaceService --> FaissManager : queries
    FastAPIApp --> VerifyResponse : returns
```

### Request/Response Sequence Diagram — POST /verify

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
    'actorBkg': '#1e293b',
    'actorBorder': '#38bdf8',
    'actorTextColor': '#f8fafc',
    'noteBkgColor': '#334155',
    'noteTextColor': '#f8fafc',
    'activationBkgColor': '#334155',
    'activationBorderColor': '#38bdf8'
  }
}}%%
sequenceDiagram
    participant React as React Frontend
    participant FastAPI
    participant Liveness as LivenessService
    participant MTCNN
    participant FaceNet
    participant Faiss
    participant SQLite

    React->>FastAPI: POST /verify (multipart image)
    FastAPI->>FastAPI: Validate Content-Type & Read bytes
    FastAPI->>Liveness: check_liveness(PIL.Image)
    Liveness-->>FastAPI: {is_live: bool, score: float}

    alt Spoof Detected
        FastAPI-->>React: 200 SPOOF_DETECTED (audit logged)
    else Real Face
        FastAPI->>MTCNN: detect face (160×160 crop)
        MTCNN-->>FastAPI: Tensor 3×160×160 or None

        alt No Face
            FastAPI-->>React: 200 NO_FACE (audit logged)
        else Face Detected
            FastAPI->>FaceNet: forward(face_tensor)
            FaceNet-->>FastAPI: Tensor 1×512
            FastAPI->>Faiss: search(query_vector, k=1, threshold=1.2)
            Faiss-->>FastAPI: identity, distance
            FastAPI->>SQLite: INSERT AccessLog (status, identity, distance)
            SQLite-->>FastAPI: log saved
            FastAPI-->>React: VerifyResponse JSON
        end
    end
```

### Request/Response Sequence Diagram — POST /enroll (Admin Only)

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
    'actorBkg': '#1e293b',
    'actorBorder': '#38bdf8',
    'actorTextColor': '#f8fafc',
    'noteBkgColor': '#334155',
    'noteTextColor': '#f8fafc',
    'activationBkgColor': '#334155',
    'activationBorderColor': '#38bdf8'
  }
}}%%
sequenceDiagram
    participant Admin as Admin Browser
    participant FastAPI
    participant JWT as JWT Guard
    participant MTCNN
    participant FaceNet
    participant FaissManager

    Admin->>FastAPI: POST /enroll (file + identity_name + Bearer Token)
    FastAPI->>JWT: verify_token(bearer)
    JWT-->>FastAPI: username, role

    alt Unauthorized (no or bad token)
        FastAPI-->>Admin: 401 Unauthorized
    else Authorized Admin
        FastAPI->>MTCNN: detect_face(image)
        MTCNN-->>FastAPI: Cropped Tensor 3×160×160
        FastAPI->>FaceNet: forward(face_tensor)
        FaceNet-->>FastAPI: 512-D Embedding
        FastAPI->>FaissManager: add_embeddings([vector], [name])
        FaissManager->>FaissManager: index.add(vector) + identities.append(name)
        FaissManager->>FaissManager: save() → index.faiss + identities.json
        FaissManager-->>FastAPI: success
        FastAPI-->>Admin: 200 EnrollResponse {success: true, identity: name}
    end
```

---

## Module 6: Liveness Anti-Spoofing Service

### Class Diagram

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
    'classText': '#f8fafc',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
classDiagram
    class LivenessService {
        <<app/services/liveness_service.py>>
        -LIVENESS_THRESHOLD: float = 100.0
        +check_liveness(image: PIL.Image) dict
        -_compute_laplacian_variance(img_gray: ndarray) float
        -_analyze_texture(img_gray: ndarray) float
    }

    class LivenessResult {
        <<Data Structure>>
        +is_live: bool
        +liveness_score: float
        +message: str
    }

    LivenessService --> LivenessResult : produces
```

### Liveness Decision Flow

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
    INPUT["PIL.Image (RGB Frame)"] --> GRAY["Convert to Grayscale\nOpenCV cvtColor"]
    GRAY --> LAP["Compute Laplacian Kernel\nvariance = Var(∇²I)"]
    GRAY --> TEX["Analyze Texture Patterns\n(LBP / Gradient histogram)"]
    LAP --> SCORE["Composite Liveness Score"]
    TEX --> SCORE
    SCORE --> THRESH{"Score ≥ 100.0?"}
    THRESH -->|"Yes — Real Human"| LIVE["is_live: True"]
    THRESH -->|"No — Photo / Screen"| SPOOF["is_live: False\n(Reject Request)"]

    classDef inputNode fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef procNode fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#f8fafc;
    classDef decNode fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef liveNode fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef spoofNode fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc;

    class INPUT,GRAY inputNode;
    class LAP,TEX,SCORE procNode;
    class THRESH decNode;
    class LIVE liveNode;
    class SPOOF spoofNode;
```

---

## Module 7: Database & ORM Layer

### SQLAlchemy Models Relationship Diagram

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
    'classText': '#f8fafc',
    'attributeBackgroundColorEven': '#0f172a',
    'attributeBackgroundColorOdd': '#1e293b'
  }
}}%%
classDiagram
    class AccessLog {
        <<SQLAlchemy Model>>
        +id: Integer PK
        +status: String
        +matched_identity: String nullable
        +l2_distance: Float nullable
        +confidence_score: Float nullable
        +is_live: Boolean default True
        +liveness_score: Float nullable
        +ip_address: String
        +message: String nullable
        +created_at: DateTime default now()
    }

    class AdminUser {
        <<SQLAlchemy Model>>
        +id: Integer PK
        +username: String UNIQUE
        +hashed_password: String
        +role: String default ADMIN
        +created_at: DateTime default now()
    }

    class SecurityService {
        <<app/core/security.py>>
        +hash_password(password: str) str
        +verify_password(plain, hashed) bool
        +create_access_token(data: dict) str
        +get_current_admin(token: str) str
    }

    AdminUser --> SecurityService : authenticated via
    AccessLog --> FastAPIApp : written by
```
