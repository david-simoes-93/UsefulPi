#!/usr/bin/env python
# coding: utf-8

"""
This script was adapted from the one in https://github.com/callummcdougall/computational-thread-art/issues
"""

import numpy as np
from itertools import product
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import time
import argparse
import os

from utils import *


def fitness(through_pixels_dict, image, line, darkness, lp, w, w_pos, w_neg, line_norm_mode):
    """
    Measures how much a line improves the image.
    Improvement is difference in penalty between the old and new images (i.e. a large decrease
    in penalty means a large fitness value).
    Penalty depends on the lightness_penalty, w, w_pos, w_neg and line_norm_mode parameters,
    however it is always some kind of weighted average of the absolute values of the pixels in the image.

    @param image image in pixels after being rounded. BLACK is 255, WHITE is 0, outside the circle
        borders is WHITE
    @param line tuple with start and ending hooks
    @param darkness darkness level of the line [0, 255] (higher values means the line is darker)
    @param lp lightness_penalty (higher value means light areas dont get so many lines on them)
    @param w weighted image (values from 1 to 0, where black is 1 in weighted_image.jpg), indicating
        pixels where penalty is worth more than others. Basically, a map of where lines need to be added
    @param w_pos weighted image for DARK (values from 1 to 0, where black is 1 in wpos_image.jpg), indicating
        pixels where penalty is worth more than others. Basically, a map of where lines need to be added
    @param w_neg weighted image for LIGHT (values from 1 to 0, where black is 1 in wneg_image.jpg), indicating
        pixels where penalty is worth more than others. Basically, a map of where lines must not be added
    @param line_norm_mode ?
    """
    pixels = through_pixels_dict[tuple(sorted(line))]

    old_pixel_values = image[tuple(pixels.T)]
    new_pixel_values = old_pixel_values - darkness

    if w is None and w_pos is None:
        new_penalty = new_pixel_values.sum() - (1 + lp) * \
            new_pixel_values[new_pixel_values < 0].sum()
        old_penalty = old_pixel_values.sum() - (1 + lp) * \
            old_pixel_values[old_pixel_values < 0].sum()
    elif w_pos is None:
        pixel_weightings = w[tuple(pixels.T)]
        new_w_pixel_values = new_pixel_values * pixel_weightings
        old_w_pixel_values = old_pixel_values * pixel_weightings
        new_penalty = new_w_pixel_values.sum() - (1 + lp) * \
            new_w_pixel_values[new_pixel_values < 0].sum()
        old_penalty = old_w_pixel_values.sum() - (1 + lp) * \
            old_w_pixel_values[old_pixel_values < 0].sum()
    elif w is None:
        pos_pixel_weightings = w_pos[tuple(pixels.T)]
        neg_pixel_weightings = w_neg[tuple(pixels.T)]
        new_wpos_pixel_values = new_pixel_values * pos_pixel_weightings
        new_wneg_pixel_values = new_pixel_values * neg_pixel_weightings
        old_wpos_pixel_values = old_pixel_values * pos_pixel_weightings
        old_wneg_pixel_values = old_pixel_values * neg_pixel_weightings
        new_penalty = new_wpos_pixel_values[new_pixel_values > 0].sum(
        ) - lp * new_wneg_pixel_values[new_pixel_values < 0].sum()
        old_penalty = old_wpos_pixel_values[old_pixel_values > 0].sum(
        ) - lp * old_wneg_pixel_values[old_pixel_values < 0].sum()

    if line_norm_mode == LineNormalization.LENGTH:
        line_norm = len(pixels)
    elif line_norm_mode == LineNormalization.WEIGHTED_LENGTH:
        if w_pos is None:
            line_norm = pixel_weightings.sum()
        else:
            line_norm = pos_pixel_weightings.sum()
    elif line_norm_mode == LineNormalization.NONE:
        line_norm = 1

    if line_norm == 0:
        return 0
    else:
        return (old_penalty - new_penalty) / line_norm


def optimise_fitness(through_pixels_dict, n_hooks, image, previous_edge, darkness,
                     lightness_penalty, list_of_lines,
                     w, w_pos, w_neg, line_norm_mode, line_sample_fraction):
    """
    Process of adding a new line is as follows:
     1. Generates all possible lines starting from this hook (or a subset of lines, if you are
            using the 'line_sample_fraction' parameter).
     2. Finds the line with the best fitness score.
     2. Subtracts this line from the image.
     3. Returns the new image, and the best line.
    """
    starting_edge = previous_edge

    sides_A = np.ones(n_hooks) * starting_edge
    sides_B = np.arange(n_hooks)
    next_lines = np.stack((sides_A, sides_B)).ravel(
        "F").reshape((n_hooks, 2)).astype(int)
    mask = (np.abs(next_lines.T[1] - next_lines.T[0]) > 10) & (
        np.abs(next_lines.T[1] - next_lines.T[0]) < n_hooks - 10)
    next_lines = next_lines[mask]

    # randomly pick a subset of the lines to evaluate
    if line_sample_fraction == 1:
        next_lines = next_lines.tolist()
    else:
        next_lines = next_lines[np.random.choice(
            np.arange(len(next_lines)), int(len(next_lines) * line_sample_fraction))].tolist()
    # print(next_lines)

    # evaluate and pick best line
    fitness_list = [fitness(through_pixels_dict, image, line, darkness,
                            lightness_penalty, w, w_pos, w_neg, line_norm_mode) for line in next_lines]
    best_line_idx = fitness_list.index(max(fitness_list))
    best_line = next_lines[best_line_idx]

    # subtract the line from the image
    pixels = through_pixels_dict[tuple(sorted(best_line))]
    image[tuple(pixels.T)] -= darkness

    return image, best_line


def find_lines(through_pixels_dict, n_hooks, wheel_pixel_size, image, n_lines, darkness, lightness_penalty,
               line_norm_mode, w=None, w_pos=None, w_neg=None, line_sample_fraction=1):
    """
    Calls 'optimise_fitness' multiple times to draw a set of lines.
    Updates the image and the list of lines with each line drawn.
    Every 100 lines drawn, prints output that describes the progress of the algorithm (including average
    penalty, current runtime, and projected total runtime).
    """
    list_of_lines = []
    previous_edge = np.random.choice(n_hooks)
    print("starting hook: "+str(previous_edge))

    image_copy = image.copy()

    for i in range(n_lines):
        if i == 0:
            t0 = time.time()
            initial_penalty = get_penalty(
                image_copy, lightness_penalty, w, w_pos, w_neg)
            initial_avg_penalty = f'{initial_penalty / (wheel_pixel_size ** 2):.2f}'
        elif i % 100 == 0:
            t_so_far = time.strftime('%M:%S', time.gmtime(time.time() - t0))
            t_left = time.strftime('%M:%S', time.gmtime(
                (time.time() - t0) * (n_lines - i) / i))
            penalty = get_penalty(image, lightness_penalty, w, w_pos, w_neg)
            avg_penalty = f'{penalty / (wheel_pixel_size ** 2):.2f}'
            print(f"{i}/{n_lines}, average penalty = {avg_penalty}/{initial_avg_penalty}, "
                  f"time = {t_so_far}, time left = {t_left}    ", end="\r")

        image, line = optimise_fitness(through_pixels_dict, n_hooks, image_copy, previous_edge,
                                       darkness, lightness_penalty, list_of_lines,
                                       w, w_pos, w_neg, line_norm_mode, line_sample_fraction)
        previous_edge = line[1]
        list_of_lines.append(line)

    penalty = get_penalty(image_copy, lightness_penalty, w, w_pos, w_neg)
    avg_penalty = f'{penalty / (wheel_pixel_size ** 2):.2f}'
    print(f"{len(list_of_lines)}/{n_lines}, average penalty = {avg_penalty}/{initial_avg_penalty}")
    print("time = " + time.strftime('%M:%S', time.gmtime(time.time() - t0)))

    return list_of_lines


def get_penalty(image, lightness_penalty, w, w_pos, w_neg):
    """
    Calculates the total penalty of the image.
    This is different depending on whether importance weightings are being used.
    An image initially is [0, 255]. As lines are added, each pixel is subtracted the 'darkness' value,
    and it can become negative.
    """
    if w is None and w_pos is None:
        # standard image penalty: sum all the pixels (so dark images where lines havent yet been added
        # have more penalty) and then check and add penalty for negative pixels
        return image[image > 0].sum() - lightness_penalty * image[image < 0].sum()
    elif w_pos is None:
        # weighted image penalty: create a weighted image based on w (multiplies all pixel values by [0,1]).
        #  Then sum all the pixels (bigger weights cause higher penalty) and add penalty for negative pixels
        image_w = image * w
        return image_w[image > 0].sum() - lightness_penalty * image_w[image < 0].sum()
    elif w is None:
        # dual-weighted image penalty: create two weighted images, one for positive pixels, one for negatives.
        #  Then sum all the positive pixels (bigger weights cause higher penalty)
        #  and add penalty for negative pixels (bigger weights cause higher penalty)
        image_wpos = image * w_pos
        image_wneg = image * w_neg
        return image_wpos[image > 0].sum() - lightness_penalty * image_wneg[image < 0].sum()


def main(src_file, src_file_weighted, src_file_wpos, src_file_wneg,
         out_file, no_progress_output,
         n_hooks, n_lines, line_darkness, light_penalty,
         wheel_diameter_m, wheel_pixel_size):
    hooks = generate_hooks(n_hooks, wheel_pixel_size)
    through_pixels_dict = build_through_pixels_dict(
        hooks, n_hooks, wheel_pixel_size)

    image_m = prepare_image(src_file, wheel_pixel_size)
    image_w = None
    image_w_pos = None
    image_w_neg = None
    line_norm_mode = LineNormalization.LENGTH
    # image where black are weighted areas: they matter more in terms of accuracy
    # you basically want the target black and the background white/grey
    if src_file_weighted is not None:
        image_w = prepare_image(src_file_weighted,
                                wheel_pixel_size, weighting=True)
        line_norm_mode = LineNormalization.WEIGHTED_LENGTH
    if src_file_wpos is not None and src_file_wneg is not None:
        image_w_pos = prepare_image(src_file_wpos,
                                    wheel_pixel_size, weighting=True)
        image_w_neg = prepare_image(src_file_wneg,
                                    wheel_pixel_size, weighting=True)
        line_norm_mode = LineNormalization.WEIGHTED_LENGTH

    lines = find_lines(through_pixels_dict, n_hooks, wheel_pixel_size,
                       image_m, n_lines=n_lines,
                       darkness=line_darkness, lightness_penalty=light_penalty,
                       w=image_w, w_pos=image_w_pos, w_neg=image_w_neg,
                       line_norm_mode=line_norm_mode,
                       line_sample_fraction=1)

    save_plot([lines], [(0, 0, 0)], out_file, wheel_pixel_size, n_hooks)
    if not no_progress_output:
        save_plot_progress([lines], [(0, 0, 0)], out_file, wheel_pixel_size, n_hooks,
                        np.arange(0.0, 1.0, 1.0/(n_lines//100)))
    total_distance(lines, hooks, wheel_diameter_m, wheel_pixel_size, out_file)
    display_output(lines, out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Creates threaded paintings based on a source image. Records instructions \
            to build them in real life.'''
    )
    parser.add_argument('src', help='''Source file (.jpg, .png, ...)''')
    parser.add_argument('--dst_dir', default="out", dest='dst_dir',
                        help='''Folder to output files into''')
    parser.add_argument('--hooks', type=int, default=360, dest='hooks',
                        help='''Amount of hooks in portrait (default: 360)''')
    group_l = parser.add_mutually_exclusive_group()
    group_l.add_argument('--lines', type=int, default=2500, dest='lines',
                         help='''Amount of thread lines in portrait, crossing the hooks (default: 2500)''')
    group_l.add_argument('--max_lines', action='store_true', dest='max_lines',
                         help='''Whether to make all possible line combinations (use with gray.jpg)''')
    parser.add_argument('--wheel_m', type=float, default=0.540, dest='wheel_m',
                        help='''Diameter (in meters) of wheel portrait (default: 54cm)''')
    parser.add_argument('--line_w', type=float, default=0.7, dest='line_w',
                        help='''Width (in milimeters) of line (default: 0.7mm)''')
    parser.add_argument('--line_darkness', type=int, default=125, dest='line_darkness',
                        help='''Line darkness [0, 255], subtracted from photo with each new line (usually >= 125) (default: 125)''')
    parser.add_argument('--light_penalty', type=float, default=0.5, dest='light_penalty',
                        help='''Ratio [0,1] of how much to penalize for when photo with subtracted lines goes into negative (default: 0.5)''')
    group_w = parser.add_mutually_exclusive_group()
    group_w.add_argument('--weighted', default=None, dest='weighted',
                         help='''A secondary image with more important zones having dark masks''')
    group_w.add_argument('--dual_weighted', default=[None, None], dest='dual_weighted', nargs=2,
                         help='''Two secondary images, with first (wpos) having important zones with dark masks and second (wneg) having clear zones with dark masks''')
    parser.add_argument('--no_progress_output', action='store_true', dest='no_progress_output',
                        help='''Whether to create progress images every 100 lines (default: True)''')
    args = parser.parse_args()

    # sanitize input
    if file_path_invalid(args.src) or \
            file_path_invalid(args.weighted) or \
            file_path_invalid(args.dual_weighted[0]) or \
            file_path_invalid(args.dual_weighted[1]):
        exit(0)
    if len(args.dst_dir) != 0 and not os.path.isdir(args.dst_dir):
        try:
            os.mkdir(dst_dir)
        except Exception:
            print("Unable to create dir " + args.dst_dir)
            exit(0)
    n_hooks = max(3, args.hooks)
    # maximum amount of lines is equal to 1+2+...+n_hooks-1 = (n_hooks-1)*(n_hooks/2)
    max_lines = int((n_hooks-1)*(n_hooks/2))
    n_lines = max_lines if args.max_lines else max(1, min(args.lines, max_lines))
    line_darkness = max(0, min(255, args.line_darkness))
    light_penalty = max(0, min(1, args.light_penalty))
    wheel_m = max(0.1, args.wheel_m)
    line_w_milim = max(0.01, args.line_w)
    line_w_m = line_w_milim / 1000      # line width in meters
    wheel_p = int(1 / line_w_m)         # diameter (in pixels) of thread portrait

    main(args.src, args.weighted, args.dual_weighted[0], args.dual_weighted[1],
         os.path.join(args.dst_dir, "out"), args.no_progress_output,
         n_hooks, n_lines, line_darkness, light_penalty, wheel_m, wheel_p)
