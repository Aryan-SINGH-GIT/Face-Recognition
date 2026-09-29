import os
from pathlib import Path
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Point directly to the local dataset provided by the user
DATA_DIR = Path(__file__).parent / "dataset atelier 4"

def get_dataloader(batch_size=32, num_workers=0):
    """Returns a PyTorch DataLoader for the local dataset."""
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found at {DATA_DIR}")
        
    # We will let MTCNN handle the resizing and cropping, so we just load the raw images here as Tensors
    # However, to use ImageFolder, images need to be tensors. 
    # MTCNN in facenet-pytorch can take PIL images or Tensors.
    # Let's just return PIL images so MTCNN can process them.
    def pil_loader(path):
        from PIL import Image
        with open(path, 'rb') as f:
            img = Image.open(f)
            return img.convert('RGB')
            
    # We don't apply ToTensor() here because MTCNN expects PIL images for easiest bounding box extraction
    dataset = datasets.ImageFolder(root=DATA_DIR, loader=pil_loader)
    
    # Custom collate_fn is needed if returning PIL images because default collate_fn expects tensors
    def collate_pil(batch):
        images = [item[0] for item in batch]
        labels = [item[1] for item in batch]
        return images, labels

    dataloader = DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=False, # Don't shuffle so we can map embeddings to identities predictably
        num_workers=num_workers,
        collate_fn=collate_pil
    )
    
    return dataloader, dataset.classes

if __name__ == "__main__":
    loader, classes = get_dataloader(batch_size=4)
    print(f"Total identities (classes): {len(classes)}")
    
    for images, labels in loader:
        print(f"Loaded a batch of {len(images)} PIL images.")
        print(f"Labels: {labels}")
        break
