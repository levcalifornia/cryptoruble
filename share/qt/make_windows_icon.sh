#!/bin/bash
# create multiresolution windows icon
ICON_SRC=../../src/qt/res/icons/cryptoruble.png
ICON_DST=../../src/qt/res/icons/cryptoruble.ico
convert ${ICON_SRC} -resize 16x16 cryptoruble-16.png
convert ${ICON_SRC} -resize 32x32 cryptoruble-32.png
convert ${ICON_SRC} -resize 48x48 cryptoruble-48.png
convert cryptoruble-16.png cryptoruble-32.png cryptoruble-48.png ${ICON_DST}

