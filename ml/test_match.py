import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import sys
from faiss_manager import FaissManager

def test_match(image_path):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    
    mtcnn = MTCNN(image_size=160, margin=0, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    
    manager = FaissManager()
    if manager.index.ntotal == 0:
        print("Faiss index is empty! Run face_encoder.py first.")
        return

    print(f"Loading image: {image_path}")
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    print("Detecting face...")
    face_tensor = mtcnn(img)
    
    if face_tensor is None:
        print("No face detected in the image.")
        return
        
    print("Generating embedding...")
    face_tensor = face_tensor.unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = resnet(face_tensor)
        
    embedding_np = embedding.squeeze().cpu().numpy()
    
    print("Searching database...")
    # Threshold controls how strict the matching is.
    # A smaller L2 distance means higher similarity.
    results = manager.search(embedding_np, k=3, threshold=1.5)
    
    if results:
        print("\n--- MATCH FOUND ---")
        for idx, (identity, dist) in enumerate(results):
            print(f"{idx+1}. Identity: {identity} (Distance: {dist:.4f})")
    else:
        print("\n--- NO MATCH FOUND ---")
        print("Distance exceeded threshold.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_match.py <path_to_image.jpg>")
    else:
        test_match(sys.argv[1])
