from PIL import Image, ImageDraw

img = Image.open("qr_binary.png")
width, height = img.size
horizontal_candidates = []

# 横方向に 1:1:3:1:1 を探す
for y in range(height):
    runs = []
    current_black = img.getpixel((0, y)) == 0
    start = 0
    for x in range(1, width):
        black = img.getpixel((x, y)) == 0
        if black != current_black:
            runs.append((current_black, start, x))
            current_black, start = black, x
    runs.append((current_black, start, width))

    for i in range(len(runs) - 4):
        a, b, c, d, e = runs[i : i + 5]
        if [a[0], b[0], c[0], d[0], e[0]] != [True, False, True, False, True]:
            continue
        lengths = [a[2] - a[1], b[2] - b[1], c[2] - c[1], d[2] - d[1], e[2] - e[1]]
        module_size = sum(lengths) / 7
        ok = True
        for actual, ratio in zip(lengths, [1, 1, 3, 1, 1]):
            expected = module_size * ratio
            if abs(actual - expected) >= expected * 0.5:  # 50%の誤差を許容
                ok = False
                break
        if ok:
            horizontal_candidates.append(((c[1] + c[2] - 1) / 2, y))

verified_candidates = []

# 候補を縦方向にも確認する
for center_x, y in horizontal_candidates:
    x = round(center_x)
    top = y
    while top >= 0 and img.getpixel((x, top)) == 0:
        top -= 1
    bottom = y
    while bottom < height and img.getpixel((x, bottom)) == 0:
        bottom += 1
    center_black = bottom - top - 1

    p = top
    while p >= 0 and img.getpixel((x, p)) != 0:
        p -= 1
    upper_white = top - p
    q = p
    while q >= 0 and img.getpixel((x, q)) == 0:
        q -= 1
    upper_black = p - q

    p = bottom
    while p < height and img.getpixel((x, p)) != 0:
        p += 1
    lower_white = p - bottom
    q = p
    while q < height and img.getpixel((x, q)) == 0:
        q += 1
    lower_black = q - p

    lengths = [upper_black, upper_white, center_black, lower_white, lower_black]
    if 0 in lengths:
        continue
    module_size = sum(lengths) / 7
    ok = True
    for actual, ratio in zip(lengths, [1, 1, 3, 1, 1]):
        expected = module_size * ratio
        if abs(actual - expected) >= expected * 0.5:  # 50%の誤差を許容
            ok = False
            break
    if ok:
        verified_candidates.append((center_x, y))

print("Candidates:", len(verified_candidates))

output = img.convert("RGB")
draw = ImageDraw.Draw(output)
for x, y in verified_candidates:
    draw.ellipse((x - 20, y - 20, x + 20, y + 20), fill="red")  # 20pxの半径の円を描画

output.save("qr_candidates.png")
