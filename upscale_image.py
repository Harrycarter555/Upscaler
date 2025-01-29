import torch
from torchvision.transforms import ToTensor, ToPILImage
from PIL import Image
from fsrcnn import FSRCNN

def load_model():
    model = FSRCNN(scale_factor=2)
    model.load_state_dict(torch.load('fsrcnn.pth'))  # Load pre-trained weights
    model.eval()
    return model

def upscale_image(image_path, model):
    img = Image.open(image_path).convert('RGB')
    lr = ToTensor()(img).unsqueeze(0)
    
    with torch.no_grad():
        sr = model(lr).squeeze(0)

    return ToPILImage()(sr)

if __name__ == "__main__":
    model = load_model()
    upscaled_image = upscale_image('input_image.jpg', model)
    upscaled_image.save('output_image.jpg')
