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
from enum import Enum

class LineNormalization(Enum):
    NONE = 1
    LENGTH = 2
    WEIGHTED_LENGTH = 3

def generate_hooks(n_hooks, wheel_pixel_size):
    """
    Generates the position of hooks, given a particular number of hooks, wheel pixel size, and hook pixel size.
    Creates 2 lists of positions (one for the anticlockwise side, one for the clockwise), and weaves them 
    together so that the order they appear in the final output is the order of nodes anticlockwise around the frame.
    """
    radius = (wheel_pixel_size / 2) - 1

    theta = np.arange(n_hooks, dtype="float64") / n_hooks * (2 * np.pi)

    x = radius * (1 + np.cos(theta)) + 0.5
    y = radius * (1 + np.sin(theta)) + 0.5

    return np.array((x, y)).T


def through_pixels(p0, p1):
    """
    Given 2 hooks, generates a list of pixels that the line connecting them runs through.
    """
    x_diff = p0[0]-p1[0]
    y_diff = p0[1]-p1[1]
    eucl_dist = np.sqrt(x_diff*x_diff + y_diff*y_diff)
    d = max(int(eucl_dist), 1)

    pixels = p0 + (p1-p0) * np.array([np.arange(d+1), np.arange(d+1)]).T / d
    pixels = np.unique(np.round(pixels), axis=0).astype(int)

    return pixels


def build_through_pixels_dict(hooks, n_hooks, wheel_pixel_size):
    """
    Uses 'through_pixels' to build up a dictionary of all possible lines connecting 2 hooks.
    Can be run at the start of a project, and doesn't need to be run again.
    Prints out an ongoing estimate of how much time is left.
    """
    ignore_next_hooks = 10

    l = [(0, 1)]
    for j in range(n_hooks):
        for i in range(j):
            # only make links to hooks that are further than 'ignore_next_hooks' away
            if j-i > ignore_next_hooks and j-i < (n_hooks - ignore_next_hooks):
                l.append((i, j))

    # list of all indices in a random order
    links_count = len(l)
    random_order = np.random.choice(links_count, links_count, replace=False)
    # why do we need this in random order?

    through_pixels_dict = {}
    t0 = time.time()

    for n in range(links_count):
        (i, j) = l[random_order[n]]
        p0, p1 = hooks[i], hooks[j]
        through_pixels_dict[(i, j)] = through_pixels(p0, p1)

        t = time.time() - t0
        t_left = t * (links_count - n - 1) / (n + 1)
        print(
            f"time left = {time.strftime('%M:%S', time.gmtime(t_left))}", end="\r")

    return through_pixels_dict


def prepare_image(file_name, wheel_pixel_size, colour=False, weighting=False):
    """
    Takes a jpeg or png image file, and converts it into a square array of bytes.
    'colour' (boolean) determines whether image is meant to have its colour read rather than darkness.
    If True then the pixel values will represent the saturation of the image, if False then they will
    represent the darkness.
    'weighting' (boolean) determines whether image is meant to be an importance weighting. If True,
    the array has values between 0 and 1, where black = 1 = maximum importance, and white = 0 = no importance).
    if both are false, image returned is array of pixels, [0, 255] where 255 is BLACK and 0 is WHITE
    """
    image = Image.open(file_name).resize((wheel_pixel_size, wheel_pixel_size))

    if colour:
        image = np.array(image.convert(mode="HSV").getdata()).reshape(
            (wheel_pixel_size, wheel_pixel_size, 3))[:, :, 1]
    elif weighting:
        image = 1 - np.array(image.convert(mode="L").getdata()
                             ).reshape((wheel_pixel_size, wheel_pixel_size)) / 255
    else:
        image = 255 - np.array(image.convert(mode="L").getdata()
                               ).reshape((wheel_pixel_size, wheel_pixel_size))

    coords = np.array(
        list(product(range(wheel_pixel_size), range(wheel_pixel_size))))
    x_coords = coords.T[0]
    y_coords = coords.T[1]
    coords_distance_from_centre = np.sqrt(
        (x_coords - (wheel_pixel_size-1)*0.5)**2 + (y_coords - (wheel_pixel_size-1)*0.5)**2)
    mask = np.array(coords_distance_from_centre > wheel_pixel_size*0.5)
    mask = np.reshape(mask, (-1, wheel_pixel_size))
    image[mask] = 0

    return image.T[:, ::-1]


def save_plot(list_coloured_lines, list_colours, file_name, size, n_hooks):
    """
    Saves the plot of lines as a jpeg with a specified name.
    It can also save multicoloured images; colours are added in the order they appear in the list.
    The colour tuples are interpreted using RGB format.
    """
    new_hooks = generate_hooks(n_hooks, size)

    for i in range(len(new_hooks)):
        new_hooks[i] = [new_hooks[i][0], size - new_hooks[i][1]]

    thread_image = Image.new('RGB', (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(thread_image)

    for (lines, colour) in zip(list_coloured_lines, list_colours):
        pixel_pairs = [(new_hooks[n[0]], new_hooks[n[1]]) for n in lines]
        for j in pixel_pairs:
            draw.line((tuple(j[0]), tuple(j[1])), fill=colour)

    thread_image.save(file_name + ".jpg", format="JPEG")


def save_plot_progress(list_coloured_lines, list_colours, file_name, size, n_hooks, proportion_list):
    """
    Saves multiple plots midway through the construction process.
    'proportion_list' contains a list of floats between 0 and 1, representing the proportion of lines you want to 
    draw (e.g. if the list was [0.5,1], then 2 plots would be saved, one with half the lines drawn and one 
    completely finished.
    """
    for prop in proportion_list:
        file_name_temp = f"{file_name} {int(100*prop)}%"
        lines_temp = list_coloured_lines[-1][:int(
            len(list_coloured_lines[-1])*prop)]
        list_coloured_lines_temp = list_coloured_lines[:-1] + [lines_temp]
        save_plot(list_coloured_lines_temp, list_colours,
                  file_name_temp, size, n_hooks)


def total_distance(lines, hooks, wheel_diameter_m, wheel_pixel_size, out_file):
    """
    Prints out the total distance of thread needed to make the model (in meters).
    """
    d = 0
    for line in lines:
        hook_A, hook_B = hooks[line[0]], hooks[line[1]]
        d += ((hook_A[0]-hook_B[0])**2 + (hook_A[1]-hook_B[1])**2) ** 0.5

    d = d * (wheel_diameter_m / wheel_pixel_size)

    distance_str = f"distance = {int(d)} meters"
    print(distance_str)
    with open(out_file+".txt", 'w') as f:
        f.write(distance_str+'\n')


def display_output(lines, out_file):
    """
    Prints out the lines in a form that can be interpreted (used for manual threading).
    """
    outlist = []
    for i in range(len(lines)):
        line = lines[i]
        output_number = f"{line[1]//2}"
        outlist.append(output_number)
    #print(' '.join(outlist))
    with open(out_file+".txt", 'a') as f:
        f.write(' '.join(outlist))

def file_path_invalid(file_path):
    """
    Returns True if file_path is declared but doesnt exist
    """
    if file_path is not None and not os.path.isfile(file_path):
        print("File " + file_path + " not found")
        return True
    return False
