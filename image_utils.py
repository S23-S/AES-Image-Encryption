from PIL import Image

def load_image(path):
    img = Image.open(path).convert('RGB')
    return img, img.tobytes(), img.size


def save_image(data, size, path):
    img = Image.frombytes('RGB', size, data)
    img.save(path)