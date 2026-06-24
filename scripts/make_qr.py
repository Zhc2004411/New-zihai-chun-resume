from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


CAPACITY_BYTES_L = {
    1: 17,
    2: 32,
    3: 53,
    4: 78,
    5: 106,
}

DATA_CODEWORDS_L = {
    1: 19,
    2: 34,
    3: 55,
    4: 80,
    5: 108,
}

ECC_CODEWORDS_L = {
    1: 7,
    2: 10,
    3: 15,
    4: 20,
    5: 26,
}

ALIGNMENT_CENTERS = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
}


def choose_version(data: bytes) -> int:
    for version, capacity in CAPACITY_BYTES_L.items():
        if len(data) <= capacity:
            return version
    raise ValueError("URL is too long for this lightweight QR generator. Use a shorter URL.")


def bits_to_codewords(bits: list[int]) -> list[int]:
    return [int("".join(str(bit) for bit in bits[i : i + 8]), 2) for i in range(0, len(bits), 8)]


def encode_data(data: bytes, version: int) -> list[int]:
    bits: list[int] = []
    bits += [0, 1, 0, 0]
    length = len(data)
    bits += [(length >> i) & 1 for i in range(7, -1, -1)]

    for byte in data:
        bits += [(byte >> i) & 1 for i in range(7, -1, -1)]

    data_bits = DATA_CODEWORDS_L[version] * 8
    bits += [0] * min(4, data_bits - len(bits))
    while len(bits) % 8:
        bits.append(0)

    codewords = bits_to_codewords(bits)
    pads = [0xEC, 0x11]
    while len(codewords) < DATA_CODEWORDS_L[version]:
        codewords.append(pads[len(codewords) % 2])
    return codewords


def gf_tables() -> tuple[list[int], list[int]]:
    exp = [0] * 512
    log = [0] * 256
    value = 1
    for i in range(255):
        exp[i] = value
        log[value] = i
        value <<= 1
        if value & 0x100:
            value ^= 0x11D
    for i in range(255, 512):
        exp[i] = exp[i - 255]
    return exp, log


GF_EXP, GF_LOG = gf_tables()


def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]


def rs_generator(degree: int) -> list[int]:
    poly = [1]
    for i in range(degree):
        next_poly = [0] * (len(poly) + 1)
        for j, coefficient in enumerate(poly):
            next_poly[j] ^= gf_mul(coefficient, GF_EXP[i])
            next_poly[j + 1] ^= coefficient
        poly = next_poly
    return poly


def rs_remainder(data: list[int], degree: int) -> list[int]:
    generator = rs_generator(degree)
    result = [0] * degree
    for byte in data:
        factor = byte ^ result.pop(0)
        result.append(0)
        for i in range(degree):
            result[i] ^= gf_mul(generator[i], factor)
    return result


def blank_matrix(size: int) -> tuple[list[list[bool]], list[list[bool]]]:
    return [[False] * size for _ in range(size)], [[False] * size for _ in range(size)]


def set_module(matrix: list[list[bool]], function: list[list[bool]], x: int, y: int, value: bool, is_function: bool = True) -> None:
    matrix[y][x] = value
    if is_function:
        function[y][x] = True


def draw_finder(matrix: list[list[bool]], function: list[list[bool]], x: int, y: int) -> None:
    size = len(matrix)
    for dy in range(-1, 8):
        for dx in range(-1, 8):
            xx = x + dx
            yy = y + dy
            if 0 <= xx < size and 0 <= yy < size:
                is_dark = 0 <= dx <= 6 and 0 <= dy <= 6 and (dx in (0, 6) or dy in (0, 6) or (2 <= dx <= 4 and 2 <= dy <= 4))
                set_module(matrix, function, xx, yy, is_dark)


def draw_alignment(matrix: list[list[bool]], function: list[list[bool]], cx: int, cy: int) -> None:
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            is_dark = max(abs(dx), abs(dy)) != 1
            set_module(matrix, function, cx + dx, cy + dy, is_dark)


def draw_function_patterns(matrix: list[list[bool]], function: list[list[bool]], version: int) -> None:
    size = len(matrix)
    draw_finder(matrix, function, 0, 0)
    draw_finder(matrix, function, size - 7, 0)
    draw_finder(matrix, function, 0, size - 7)

    for i in range(8, size - 8):
        value = i % 2 == 0
        set_module(matrix, function, 6, i, value)
        set_module(matrix, function, i, 6, value)

    for cx in ALIGNMENT_CENTERS[version]:
        for cy in ALIGNMENT_CENTERS[version]:
            if function[cy][cx]:
                continue
            draw_alignment(matrix, function, cx, cy)

    set_module(matrix, function, 8, size - 8, True)

    for i in range(9):
        if i != 6:
            function[8][i] = True
            function[i][8] = True
    for i in range(8):
        function[8][size - 1 - i] = True
        function[size - 1 - i][8] = True


def format_bits(mask: int) -> int:
    data = (1 << 3) | mask
    value = data << 10
    generator = 0x537
    for i in range(14, 9, -1):
        if value & (1 << i):
            value ^= generator << (i - 10)
    return ((data << 10) | value) ^ 0x5412


def draw_format_bits(matrix: list[list[bool]], mask: int) -> None:
    size = len(matrix)
    bits = format_bits(mask)

    def bit(i: int) -> bool:
        return ((bits >> i) & 1) != 0

    for i in range(6):
        matrix[i][8] = bit(i)
    matrix[7][8] = bit(6)
    matrix[8][8] = bit(7)
    matrix[8][7] = bit(8)
    for i in range(9, 15):
        matrix[8][14 - i] = bit(i)

    for i in range(8):
        matrix[8][size - 1 - i] = bit(i)
    for i in range(8, 15):
        matrix[size - 15 + i][8] = bit(i)
    matrix[size - 8][8] = True


def mask_bit(mask: int, x: int, y: int) -> bool:
    if mask == 0:
        return (x + y) % 2 == 0
    if mask == 1:
        return y % 2 == 0
    if mask == 2:
        return x % 3 == 0
    if mask == 3:
        return (x + y) % 3 == 0
    if mask == 4:
        return (x // 3 + y // 2) % 2 == 0
    if mask == 5:
        return (x * y) % 2 + (x * y) % 3 == 0
    if mask == 6:
        return ((x * y) % 2 + (x * y) % 3) % 2 == 0
    return ((x + y) % 2 + (x * y) % 3) % 2 == 0


def place_data(matrix: list[list[bool]], function: list[list[bool]], codewords: list[int], mask: int) -> None:
    size = len(matrix)
    bits = [(byte >> i) & 1 for byte in codewords for i in range(7, -1, -1)]
    bit_index = 0
    upward = True
    x = size - 1
    while x > 0:
        if x == 6:
            x -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for y in rows:
            for dx in range(2):
                xx = x - dx
                if function[y][xx]:
                    continue
                value = bit_index < len(bits) and bits[bit_index] == 1
                bit_index += 1
                if mask_bit(mask, xx, y):
                    value = not value
                set_module(matrix, function, xx, y, value, is_function=False)
        upward = not upward
        x -= 2


def penalty(matrix: list[list[bool]]) -> int:
    size = len(matrix)
    score = 0

    for y in range(size):
        run_color = matrix[y][0]
        run_len = 1
        for x in range(1, size):
            if matrix[y][x] == run_color:
                run_len += 1
            else:
                if run_len >= 5:
                    score += 3 + run_len - 5
                run_color = matrix[y][x]
                run_len = 1
        if run_len >= 5:
            score += 3 + run_len - 5

    for x in range(size):
        run_color = matrix[0][x]
        run_len = 1
        for y in range(1, size):
            if matrix[y][x] == run_color:
                run_len += 1
            else:
                if run_len >= 5:
                    score += 3 + run_len - 5
                run_color = matrix[y][x]
                run_len = 1
        if run_len >= 5:
            score += 3 + run_len - 5

    for y in range(size - 1):
        for x in range(size - 1):
            color = matrix[y][x]
            if matrix[y][x + 1] == color and matrix[y + 1][x] == color and matrix[y + 1][x + 1] == color:
                score += 3

    dark = sum(1 for row in matrix for module in row if module)
    percent = dark * 100 // (size * size)
    score += abs(percent - 50) // 5 * 10
    return score


def make_matrix(text: str) -> list[list[bool]]:
    data = text.encode("utf-8")
    version = choose_version(data)
    data_codewords = encode_data(data, version)
    ecc = rs_remainder(data_codewords, ECC_CODEWORDS_L[version])
    codewords = data_codewords + ecc
    size = 17 + version * 4

    best_matrix: list[list[bool]] | None = None
    best_score: int | None = None
    for mask in range(8):
        matrix, function = blank_matrix(size)
        draw_function_patterns(matrix, function, version)
        place_data(matrix, function, codewords, mask)
        draw_format_bits(matrix, mask)
        score = penalty(matrix)
        if best_score is None or score < best_score:
            best_score = score
            best_matrix = matrix
    assert best_matrix is not None
    return best_matrix


def render_png(matrix: list[list[bool]], output: Path, scale: int = 12, border: int = 4) -> None:
    size = len(matrix)
    image_size = (size + border * 2) * scale
    image = Image.new("RGB", (image_size, image_size), "white")
    pixels = image.load()
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if not dark:
                continue
            x0 = (x + border) * scale
            y0 = (y + border) * scale
            for yy in range(y0, y0 + scale):
                for xx in range(x0, x0 + scale):
                    pixels[xx, yy] = (17, 24, 39)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a QR code PNG for the resume website URL.")
    parser.add_argument("url", help="Public website URL, for example https://username.github.io/resume/")
    parser.add_argument("-o", "--output", default="docs/assets/site-qrcode.png", help="Output PNG path")
    args = parser.parse_args()

    if not (args.url.startswith("https://") or args.url.startswith("http://")):
        raise SystemExit("The URL must start with http:// or https://")

    matrix = make_matrix(args.url)
    render_png(matrix, Path(args.output))
    print(f"QR code generated: {args.output}")


if __name__ == "__main__":
    main()
