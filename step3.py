from PIL import Image, ImageDraw

img = Image.open("qr_binary.png").convert("RGB")

width, height = img.size
horizontal_candidates = []

# ------------------------------
# 横方向に 1:1:3:1:1 を探す
# ------------------------------

for y in range(height):
    runs = []

    r, g, b = img.getpixel((0, y))
    current_black = (r + g + b) / 3 < 128
    start = 0

    for x in range(1, width):
        r, g, b = img.getpixel((x, y))
        black = (r + g + b) / 3 < 128

        if black != current_black:
            runs.append(
                (
                    current_black,
                    start,
                    x,
                )
            )

            current_black = black
            start = x

    runs.append(
        (
            current_black,
            start,
            width,
        )
    )

    # 連続する5区間を調べる
    for i in range(len(runs) - 4):
        a, b, c, d, e = runs[i : i + 5]

        # 黒 → 白 → 黒 → 白 → 黒
        if [a[0], b[0], c[0], d[0], e[0]] != [
            True,
            False,
            True,
            False,
            True,
        ]:
            continue

        lengths = [
            a[2] - a[1],
            b[2] - b[1],
            c[2] - c[1],
            d[2] - d[1],
            e[2] - e[1],
        ]

        module_size = sum(lengths) / 7
        ratios = [1, 1, 3, 1, 1]

        ok = True

        for actual, ratio in zip(lengths, ratios):
            expected = module_size * ratio

            # 理想値から50%未満のずれを許容
            if abs(actual - expected) >= expected * 0.5:
                ok = False
                break

        if not ok:
            continue

        # 中央の黒区間の中心
        center_x = (c[1] + c[2] - 1) / 2

        horizontal_candidates.append(
            (
                center_x,
                y,
            )
        )


# ------------------------------
# 横方向で見つかった候補を
# 今度は縦方向に確認する
# ------------------------------

verified_candidates = []

for center_x, center_y in horizontal_candidates:
    x = round(center_x)
    y = center_y

    # 候補の中心は黒のはず
    r, g, b = img.getpixel((x, y))

    if (r + g + b) / 3 >= 128:
        continue

    # 中央の黒区間を上方向へたどる
    top = y

    while top >= 0:
        r, g, b = img.getpixel((x, top))

        if (r + g + b) / 3 >= 128:
            break

        top -= 1

    # 中央の黒区間を下方向へたどる
    bottom = y

    while bottom < height:
        r, g, b = img.getpixel((x, bottom))

        if (r + g + b) / 3 >= 128:
            break

        bottom += 1

    center_black = bottom - top - 1

    # 中央より上の白区間
    p = top

    while p >= 0:
        r, g, b = img.getpixel((x, p))

        if (r + g + b) / 3 < 128:
            break

        p -= 1

    upper_white = top - p

    # さらに上の黒区間
    q = p

    while q >= 0:
        r, g, b = img.getpixel((x, q))

        if (r + g + b) / 3 >= 128:
            break

        q -= 1

    upper_black = p - q

    # 中央より下の白区間
    p = bottom

    while p < height:
        r, g, b = img.getpixel((x, p))

        if (r + g + b) / 3 < 128:
            break

        p += 1

    lower_white = p - bottom

    # さらに下の黒区間
    q = p

    while q < height:
        r, g, b = img.getpixel((x, q))

        if (r + g + b) / 3 >= 128:
            break

        q += 1

    lower_black = q - p

    lengths = [
        upper_black,
        upper_white,
        center_black,
        lower_white,
        lower_black,
    ]

    # 画像端などで区間を取得できなかった場合
    if 0 in lengths:
        continue

    module_size = sum(lengths) / 7
    ratios = [1, 1, 3, 1, 1]

    ok = True

    for actual, ratio in zip(lengths, ratios):
        expected = module_size * ratio

        if abs(actual - expected) >= expected * 0.5:
            ok = False
            break

    if not ok:
        continue

    # 縦方向でも 1:1:3:1:1 だった
    verified_candidates.append(
        (
            center_x,
            center_y,
        )
    )


# ------------------------------
# 縦横の両方を通過した候補を描画
# ------------------------------

output = img.copy()
draw = ImageDraw.Draw(output)

for x, y in verified_candidates:
    radius = 10

    draw.ellipse(
        (
            x - radius,
            y - radius,
            x + radius,
            y + radius,
        ),
        fill=(255, 0, 0),
    )

output.save("qr_candidates.png")
