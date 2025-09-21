from torchvision import transforms

preprocess_image = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])
