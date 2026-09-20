from PIL import Image

img = Image.open("qr.jpg")

w, h = img.size
gray = [[0] * w for _ in range(h)]

for y in range(h):
    for x in range(w):
        r, g, b = img.getpixel((x, y))
        gray[y][x] = (299 * r + 587 * g + 114 * b) // 1000

gray_img = Image.new("L", (w, h))
for y in range(h):
    for x in range(w):
        gray_img.putpixel((x, y), gray[y][x])

gray_img.save("qr_gray.png")
