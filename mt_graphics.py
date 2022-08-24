#!/usr/bin/env python

from PIL import (
    Image,
    ImageOps,
)
from itertools import product


MT_COLORS = [0, 4, 1, 5, 2, 6, 3, 7]

BLOCK_WIDTH = 2
BLOCK_HEIGHT = 3
BLOCK_VAL = [0, 1, 2, 3, 4, 6]


def _block_to_byte(block):
    n = 32
    for i, v in enumerate(BLOCK_VAL):
        if block[i] > 0:
            n += 2**v
    return bytes((n,))


def _make_blocks(img):
    width, height = img.size
    res = []
    for y in range(0, height, BLOCK_HEIGHT):
        curr_row = []
        for x in range(0, width, BLOCK_WIDTH):
            curr_block = []
            for j, i in product(range(BLOCK_HEIGHT), range(BLOCK_WIDTH)):
                curr_block.append(img.getpixel((x+i, y+j)))
            curr_row.append(curr_block)
        res.append(curr_row)
    return res


def _get_most_frequent_color(block):
    color_count = list(set((x, block.count(x)) for x in block))
    color_count.sort(key=lambda x: x[1], reverse=True)
    ranked_colors = [c for c, n in color_count]
    if len(ranked_colors) > 1:
        return tuple(ranked_colors[:2])
    else:
        return tuple(ranked_colors[:1]*2)


def _block_threshold(block, fg, bg):
    res = []
    for v in block:
        if abs(v-fg) < abs(v-bg):
            res.append(1)
        else:
            res.append(0)
    return res


def _blocks_to_bytes(rows, pos=(1, 1)):
    res = b''
    curr_fg = 7
    curr_bg = 0

    x_pos, y_pos = pos

    for row_idx, row in enumerate(rows):
        res += bytes((31, 64+y_pos+row_idx, 64+x_pos))
        res += b'\x0e'
        for col_idx, block in enumerate(row):
            raw_fg, raw_bg = _get_most_frequent_color(block)
            thres_block = _block_threshold(block, raw_fg, raw_bg)
            fg = MT_COLORS[raw_fg >> 5]
            bg = MT_COLORS[raw_bg >> 5]
            if fg != curr_fg or col_idx == 0:
                res += bytes((27,))
                res += bytes((fg+64,))
                curr_fg = fg
            if bg != curr_bg or col_idx == 0:
                res += bytes((27,))
                res += bytes((bg+80,))
                curr_bg = bg
            res += _block_to_byte(thres_block)
    return res


def bytes_from_image(img_file, pos=(1, 1)):
    raw_img = Image.open(img_file)
    pre_img = raw_img.convert("L")
    raw_img.close()
    img = ImageOps.posterize(pre_img, 3)
    raw_blocks = _make_blocks(img)
    return _blocks_to_bytes(raw_blocks, pos)
