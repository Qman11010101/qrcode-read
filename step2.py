from PIL import Image

img = Image.open("qr_gray.png")

w, h = img.size
binary = [[0] * w for _ in range(h)]

for y in range(h):
    for x in range(w):
        brightness = img.getpixel((x, y))
        if brightness < 128:
            binary[y][x] = 1
        else:
            binary[y][x] = 0

binary_img = Image.new("1", (w, h))
for y in range(h):
    for x in range(w):
        # Pillowでは 0=黒、255=白 として書く
        binary_img.putpixel((x, y), 0 if binary[y][x] == 1 else 255)

binary_img.save("qr_binary.png")
