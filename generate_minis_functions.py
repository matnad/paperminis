# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:12:16 2018

@author: Matthias N.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import json

import numpy as np
import cv2 as cv
from PIL import Image
from fake_useragent import UserAgent
import greedypacker

## settings
do_these = ['Marid', 'Sea Spawn', 'Sea Spawn', 'Storm Giant', 'Sea Spawn', 'Sea Hag']

paper_format = 'a4'
print_margin = np.array([3.5, 4])  # left&right, top&bottom in mm per side
dpmm = 10  # resolution

## init
font = cv.FONT_HERSHEY_SIMPLEX
paper = {'a3': np.array([297, 420]), 'a4': np.array([210, 297])}
canvas = (paper[paper_format] - 2 * print_margin) * dpmm
ua = UserAgent()
header = {'User-Agent': str(ua.chrome)}
with open('monsters.json', encoding='utf-8') as data_file:
    monsters = json.loads(data_file.read())
minis_dir = Path('minis')
minis_dir.mkdir(exist_ok=True)
sheet_dir = Path('sheets')
sheet_dir.mkdir(exist_ok=True)


## main function    
def create_mini(monster):
    # load values
    try:
        creature_size = monsters[monster]['size']
        img_url = monsters[monster]['img_url']
        monster_name = monsters[monster]['name']
    except:
        return 'Monster not found.'

    if img_url == '':
        return 'No image url found.'

    # more settings
    base_width = 24
    if creature_size in ['Medium', 'Small', 'Tiny']:
        m_width = base_width
        max_height = 40
        n_height = 8
        font_size = 1.15
        font_width = 1
    elif creature_size == 'Large':
        m_width = base_width * 2
        max_height = 50
        n_height = 10
        font_size = 2
        font_width = 2
    elif creature_size == 'Huge':
        m_width = base_width * 3
        max_height = 60
        n_height = 12
        font_size = 2.5
        font_width = 2
    elif creature_size == 'Gargantuan':
        m_width = base_width * 4
        max_height = 80
        n_height = 14
        font_size = 3
        font_width = 3
    else:
        return 'Creature size invalid.'

    min_height = 40
    b_height = m_width
    width = m_width * dpmm

    ## generate name plate
    n_img = np.zeros((n_height * dpmm, width, 3), np.uint8) + 255

    x_margin = 0
    y_margin = 0

    # find optimal font size
    while x_margin < 2 or y_margin < 10:
        font_size = round(font_size - 0.05, 2)
        textsize = cv.getTextSize(monster_name, font, font_size, font_width)[0]
        x_margin = n_img.shape[1] - textsize[0]
        y_margin = n_img.shape[0] - textsize[1]

    # write text
    textX = np.floor_divide(x_margin, 2)
    textY = np.floor_divide(n_img.shape[0] + textsize[1], 2)
    cv.putText(n_img, monster_name, (textX, textY), font, font_size, (0, 0, 0), font_width, cv.LINE_AA)
    cv.rectangle(n_img, (0, 0), (n_img.shape[1] - 1, n_img.shape[0] - 1), (0, 0, 0), thickness=1)

    ## generate mimiature image
    req = Request(img_url, headers=header)

    with urlopen(req) as resp:
        arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        m_img = cv.imdecode(arr, -1)  # Load it 'as it is'

    # replace alpha channel with white (for .png, etc)
    if m_img.shape[2] == 4:
        alpha_channel = m_img[:, :, 3]
        mask = (alpha_channel == 0)
        mask = np.dstack((mask, mask, mask))
        color = m_img[:, :, :3]
        color[mask] = 255
        m_img = color

    # resize the image and/or add padding
    if m_img.shape[1] > width - 2:
        f = (width - 2) / m_img.shape[1]
        m_img = cv.resize(m_img, (0, 0), fx=f, fy=f)
        white_vert = np.zeros((m_img.shape[0], 1, 3), np.uint8) + 255
        m_img = np.concatenate((white_vert, m_img, white_vert), axis=1)

    if m_img.shape[0] > max_height * dpmm - 2:
        f = (max_height * dpmm - 2) / m_img.shape[0]
        m_img = cv.resize(m_img, (0, 0), fx=f, fy=f)
        white_horiz = np.zeros((1, m_img.shape[1], 3), np.uint8) + 255
        m_img = np.concatenate((white_horiz, m_img, white_horiz), axis=0)

    if m_img.shape[0] < min_height * dpmm:
        diff = min_height * dpmm - m_img.shape[0]
        top = np.floor_divide(diff, 2)
        bottom = top
        if diff % 2 == 1: bottom += 1
        m_img = np.concatenate((np.zeros((top, m_img.shape[1], 3), np.uint8) + 255, m_img,
                                np.zeros((top, m_img.shape[1], 3), np.uint8) + 255), axis=0)

    if m_img.shape[1] < width:
        diff = width - m_img.shape[1]
        left = np.floor_divide(diff, 2)
        right = left
        if diff % 2 == 1: right += 1
        m_img = np.concatenate((np.zeros((m_img.shape[0], left, 3), np.uint8) + 255, m_img,
                                np.zeros((m_img.shape[0], right, 3), np.uint8) + 255), axis=1)

    cv.rectangle(m_img, (0, 0), (m_img.shape[1] - 1, m_img.shape[0] - 1), (0, 0, 0), thickness=1)

    ## create mini base
    demi_base = b_height // 2 * dpmm
    if creature_size == 'Gargantuan':
        feet_mod = 1
    else:
        feet_mod = 2
    base_height = int(np.floor(demi_base * feet_mod))
    b_img = np.zeros((base_height, width, 3), np.uint8) + 255
    cv.rectangle(b_img, (0, 0), (b_img.shape[1] - 1, demi_base - 1), (0, 0, 0), thickness=-1)
    cv.rectangle(b_img, (0, 0), (b_img.shape[1] - 1, b_img.shape[0] - 1), (0, 0, 0), thickness=1)

    ## construct full miniature
    img = np.concatenate((m_img, n_img, b_img), axis=0)
    flipped_img = cv.flip(img, -1)
    img = np.append(flipped_img, img, axis=0)
    # convert to PIL image so we can save it with the correct dpi
    RGB_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_file = minis_dir / '{}.png'.format(monster)
    im_pil = Image.fromarray(RGB_img)
    im_pil.save(img_file, dpi=(25.4 * dpmm, 25.4 * dpmm))

    return img


## generate all mini images
minis = []
for m in do_these:
    print('Doing {}...'.format(m))
    mini = create_mini(m)
    if not isinstance(mini, str):
        minis.append(mini)
    else:
        print('{} skipped with error: {}'.format(m, mini))

## optimization algorithm to align images on canvas
M = greedypacker.BinManager(canvas[0], canvas[1], bin_algo='bin_best_fit', pack_algo='shelf', heuristic='best_area_fit',
                            split_heuristic='default', rotation=True, rectangle_merge=True, wastemap=True, sorting=True,
                            sorting_heuristic='DESCA')

its = {}
item_id = 0
for it in minis:
    its[item_id] = it
    item = greedypacker.Item(it.shape[1], it.shape[0])
    item.id = item_id
    M.add_items(item)
    item_id += 1

M.execute()
result = M.bins

## Create sheets
sheet_nr = 1
for r in result:
    img = np.zeros((int(canvas[1]),int(canvas[0]), 3), np.uint8) + 255
    for it in r.items:
        x = int(it.x)
        y = int(it.y)
        w = int(it.width)
        h = int(it.height)
        it_id = int(it.id)
        m_img = its[it_id]
        test = m_img
        if w > h:  # rotated (only works as long as minis always have height > width, keep in mind if editing)
            m_img = np.rot90(m_img, axes=(1, 0))
        shape = m_img.shape
        img[y:y + shape[0], x:x + shape[1], :] = m_img

    # save sheets
    RGB_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    sheet_file = sheet_dir / 'sheet_{}.png'.format(sheet_nr)
    im_pil = Image.fromarray(RGB_img)
    im_pil.save(sheet_file, dpi=(25.4 * dpmm, 25.4 * dpmm))
    sheet_nr += 1

    # display result if you want
    # img_small =  cv.resize(img, (0,0), fx=.6, fy=.6)
    # cv.imshow('Img',img_small)
    # cv.waitKey(0)
