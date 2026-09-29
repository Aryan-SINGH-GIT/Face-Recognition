import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from tqdm import tqdm
from dataset import get_dataloader
from faiss_manager import FaissManager
from pathlib import Path

def build_index():
    # Set device (CPU is fine, but check for CUDA just in case)
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f"Running on device: {device}")

    # Initialize MTCNN for face detection and cropping
    # MTCNN returns a cropped and normalized tensor (160x160) ready for FaceNet
    mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device
    )

    # Initialize InceptionResnetV1 (FaceNet encoder)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

    # Load dataset
    batch_size = 16
    loader, classes = get_dataloader(batch_size=batch_size)
    
    manager = FaissManager(
        index_path="index.faiss", 
        mapping_path="identities.json", 
        embedding_dim=512
    )

    print("Extracting faces and generating embeddings...")
    
    total_processed = 0
    total_failed = 0
    
    # Process images in batches
    for images, labels in tqdm(loader, desc="Processing batches"):
        # MTCNN can take a list of PIL images and return a tensor of stacked faces
        # However, if a face isn't found in an image, MTCNN returns None for that image.
        # So we process them individually or handle Nones.
        
        batch_embeddings = []
        batch_identities = []
        
        for i, img in enumerate(images):
            # Detect and crop face
            face_tensor = mtcnn(img)
            
            if face_tensor is not None:
                # Add batch dimension: [3, 160, 160] -> [1, 3, 160, 160]
                face_tensor = face_tensor.unsqueeze(0).to(device)
                
                # Generate embedding
                with torch.no_grad():
                    embedding = resnet(face_tensor)
                    
                # Convert to numpy array and store
                embedding_np = embedding.squeeze().cpu().numpy()
                batch_embeddings.append(embedding_np)
                
                # Get the actual string name from the class index
                identity_name = classes[labels[i]]
                batch_identities.append(identity_name)
                
                total_processed += 1
            else:
                total_failed += 1
                
        # Add the valid embeddings from this batch to Faiss
        if batch_embeddings:
            manager.add_embeddings(batch_embeddings, batch_identities)

    # Save the index to disk
    manager.save()
    print(f"\nFinished building index!")
    print(f"Successfully processed {total_processed} faces.")
    print(f"Failed to detect faces in {total_failed} images.")

if __name__ == "__main__":
    build_index()
