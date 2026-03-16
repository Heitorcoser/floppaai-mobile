"""
Coloque a imagem da porta do Floppa nesta pasta como 'icon_source.png'
e execute este script para gerar o icon.ico para o .exe
e os icons para o mobile.
"""
from PIL import Image
import os

src = "icon_source.png"
if not os.path.exists(src):
    print(f"ERRO: Coloque a imagem como '{src}' nesta pasta.")
    exit(1)

img = Image.open(src).convert("RGBA")

# .ico para Windows (multiplos tamanhos)
sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
imgs  = [img.resize(s, Image.LANCZOS) for s in sizes]
imgs[0].save("assets/icon.ico", format="ICO", sizes=sizes, append_images=imgs[1:])
print("✅ assets/icon.ico gerado!")

# PNG para mobile PWA
img.resize((192,192), Image.LANCZOS).save("mobile/icon-192.png")
img.resize((512,512), Image.LANCZOS).save("mobile/icon-512.png")
print("✅ mobile/icon-192.png e icon-512.png gerados!")
print("\nAgora execute build.bat para gerar o .exe!")
