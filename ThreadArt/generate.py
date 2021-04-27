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

    return np.array((x,y)).T


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
    #n_hook_sides = n_hooks * 2
    ignore_next_hooks = 10

    l = [(0,1)]
    for j in range(n_hooks):
        for i in range(j):
            # only make links to hooks that are further than 'ignore_next_hooks' away
            if j-i > ignore_next_hooks and j-i < (n_hooks - ignore_next_hooks):
                l.append((i, j))

    # list of all indices in a random order
    links_count = len(l)
    random_order = np.random.choice(links_count,links_count,replace=False)
    # why do we need this in random order?

    through_pixels_dict = {}
    t0 = time.time()

    for n in range(links_count):
        (i, j) = l[random_order[n]]
        p0, p1 = hooks[i], hooks[j]
        through_pixels_dict[(i,j)] = through_pixels(p0, p1)

        t = time.time() - t0
        t_left = t * (links_count - n - 1) / (n + 1)
        print(f"time left = {time.strftime('%M:%S', time.gmtime(t_left))}", end="\r")

    return through_pixels_dict


def fitness(through_pixels_dict, image, line, darkness, lp, w, w_pos, w_neg, line_norm_mode):
    """
    Measures how much a line improves the image.
    Improvement is difference in penalty between the old and new images (i.e. a large decrease in penalty means a large fitness value).
    Penalty depends on the lightness_penalty, w, w_pos, w_neg and line_norm_mode parameters, however it is always some kind of weighted average of the absolute values of the pixels in the image.

    @param image image in pixels after being rounded. BLACK is 255, WHITE is 0, outside the circle borders is WHITE
    @param line ?
    @param darkness darkness level of the line [0, 255] (higher values means the line is darker)
    @param lp lightness_penalty this is irrelevant lol
    """
    pixels = through_pixels_dict[tuple(sorted(line))]

    old_pixel_values = image[tuple(pixels.T)]
    new_pixel_values = old_pixel_values - darkness

    if type(w) == bool and type(w_pos) == bool:
        new_penalty = new_pixel_values.sum() - (1 + lp) * new_pixel_values[new_pixel_values < 0].sum()
        old_penalty = old_pixel_values.sum() - (1 + lp) * old_pixel_values[old_pixel_values < 0].sum()
    elif type(w_pos) == bool:
        pixel_weightings = w[tuple(pixels.T)]
        new_w_pixel_values = new_pixel_values * pixel_weightings
        old_w_pixel_values = old_pixel_values * pixel_weightings
        new_penalty = new_w_pixel_values.sum() - (1 + lp) * new_w_pixel_values[new_pixel_values < 0].sum()
        old_penalty = old_w_pixel_values.sum() - (1 + lp) * old_w_pixel_values[old_pixel_values < 0].sum()
    elif type(w) == bool:
        pos_pixel_weightings = w_pos[tuple(pixels.T)]
        neg_pixel_weightings = w_neg[tuple(pixels.T)]
        new_wpos_pixel_values = new_pixel_values * pos_pixel_weightings
        new_wneg_pixel_values = new_pixel_values * neg_pixel_weightings
        old_wpos_pixel_values = old_pixel_values * pos_pixel_weightings
        old_wneg_pixel_values = old_pixel_values * neg_pixel_weightings
        new_penalty = new_wpos_pixel_values[new_pixel_values > 0].sum() - lp * new_wneg_pixel_values[new_pixel_values < 0].sum()
        old_penalty = old_wpos_pixel_values[old_pixel_values > 0].sum() - lp * old_wneg_pixel_values[old_pixel_values < 0].sum()

    if line_norm_mode == "length":
        line_norm = len(pixels)
    elif line_norm_mode == "weighted length":
        if type(w_pos) == bool:
            line_norm = pixel_weightings.sum()
        else:
            line_norm = pos_pixel_weightings.sum()
    elif line_norm_mode == "none":
        line_norm = 1

    if line_norm == 0:
        return 0
    else:
        return (old_penalty - new_penalty) / line_norm


def optimise_fitness(through_pixels_dict, n_hooks, image, previous_edge, darkness, lightness_penalty, list_of_lines,
                     w, w_pos, w_neg, line_norm_mode, time_saver):
    """
    Process of adding a new line is as follows:
     1. Generates all possible lines starting from this hook (or a subset of lines, if you are using the 'time_saver' parameter).
     2. Finds the line with the best fitness score.
     2. Subtracts this line from the image.
     3. Returns the new image, and the best line.
    """
    starting_edge = previous_edge

    sides_A = np.ones(n_hooks) * starting_edge
    sides_B = np.arange(n_hooks)
    next_lines = np.stack((sides_A, sides_B)).ravel("F").reshape((n_hooks, 2)).astype(int)
    mask = (np.abs(next_lines.T[1] - next_lines.T[0]) > 10) & (np.abs(next_lines.T[1] - next_lines.T[0]) < n_hooks - 10)
    next_lines = next_lines[mask]

    # randomly pick a subset of the lines to evaluate
    if time_saver == 1:
        next_lines = next_lines.tolist()
    else:
        next_lines = next_lines[np.random.choice(np.arange(len(next_lines)), int(len(next_lines) * time_saver))].tolist()
    #print(next_lines)

    # evaluate and pick best line
    fitness_list = [fitness(through_pixels_dict, image, line, darkness, lightness_penalty, w, w_pos, w_neg, line_norm_mode) for line in next_lines]
    best_line_idx = fitness_list.index(max(fitness_list))
    best_line = next_lines[best_line_idx]

    # subtract the line from the image
    pixels = through_pixels_dict[tuple(sorted(best_line))]
    image[tuple(pixels.T)] -= darkness

    return image, best_line


def find_lines(through_pixels_dict, n_hooks, wheel_pixel_size, image, n_lines, darkness, lightness_penalty, 
               line_norm_mode, w=False, w_pos=False, w_neg=False, time_saver=1):
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
            initial_penalty = get_penalty(image_copy, lightness_penalty, w, w_pos, w_neg)
            initial_avg_penalty = f'{initial_penalty / (wheel_pixel_size ** 2):.2f}'
        elif i%100 == 0:
            t_so_far = time.strftime('%M:%S', time.gmtime(time.time() - t0))
            t_left = time.strftime('%M:%S', time.gmtime((time.time() - t0) * (n_lines - i) / i))
            penalty = get_penalty(image, lightness_penalty, w, w_pos, w_neg)
            avg_penalty = f'{penalty / (wheel_pixel_size ** 2):.2f}'
            print(f"{i}/{n_lines}, average penalty = {avg_penalty}/{initial_avg_penalty}, time = {t_so_far}, time left = {t_left}    ", end="\r")

        image, line = optimise_fitness(through_pixels_dict, n_hooks, image_copy, previous_edge, darkness, lightness_penalty, list_of_lines,
                                       w, w_pos, w_neg, line_norm_mode, time_saver)
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
    """
    #print(image[True])
    #for row in image[True]:
    #    print(row)
    #print(image[image<0])
    #for row in image[image<0]:
    #    print(row)
    #print(lightness_penalty)
    #input("cont?")
    if type(w) == bool and type(w_pos) == bool:
        #print(image.sum() - (1 + 0) * image[image<50].sum())
        #print(image.sum() - (1 + 0.35) * image[image<50].sum())
        #print(image.sum() - (1 + 0.8) * image[image<50].sum())
        #print(image.sum() - (1 + 1.2) * image[image<50].sum())
        #input("cont?")
        return image.sum() - (1 + lightness_penalty) * image[image<0].sum()
    elif type(w_pos) == bool:
        image_w = image * w
        return image_w.sum() - (1 + lightness_penalty) * image_w[image<0].sum()
    elif type(w) == bool:
        image_wpos = image * w_pos
        image_wneg = image * w_neg
        return image_wpos[image>0].sum() - (1 + lightness_penalty) * image_wneg[image<0].sum()


def prepare_image(file_name, wheel_pixel_size, colour=False, weighting=False):
    """
    Takes a jpeg or png image file, and converts it into a square array of bytes.
    'colour' (boolean) determines whether image is meant to have its colour read rather than darkness. 
    If True then the pixel values will represent the saturation of the image, if False then they will 
    represent the darkness.
    'weighting' (boolean) determines whether image is meant to be an importance weighting. If True, 
    the array has values between 0 and 1, where black = 1 = maximum importance, and white = 0 = no importance).
    """
    image = Image.open(file_name).resize((wheel_pixel_size, wheel_pixel_size))

    if colour:
        image = np.array(image.convert(mode="HSV").getdata()).reshape((wheel_pixel_size, wheel_pixel_size,3))[:,:,1]
    elif weighting:
        image = 1 - np.array(image.convert(mode="L").getdata()).reshape((wheel_pixel_size, wheel_pixel_size)) / 255
    else:
        image = 255 - np.array(image.convert(mode="L").getdata()).reshape((wheel_pixel_size, wheel_pixel_size))

    coords = np.array(list(product(range(wheel_pixel_size), range(wheel_pixel_size))))
    x_coords = coords.T[0]
    y_coords = coords.T[1]
    coords_distance_from_centre = np.sqrt((x_coords - (wheel_pixel_size-1)*0.5)**2 + (y_coords - (wheel_pixel_size-1)*0.5)**2)
    mask = np.array(coords_distance_from_centre > wheel_pixel_size*0.5)
    mask = np.reshape(mask, (-1, wheel_pixel_size))
    image[mask] = 0

    return image.T[:,::-1]


def display_images(image_list):
    fig, axs = plt.subplots(1,len(image_list),figsize=(30,30));
    for (i,j) in zip(range(len(image_list)), image_list):
        axs[i].set_yticklabels([])
        axs[i].set_xticklabels([])
        axs[i].imshow(j[:,::-1].T, cmap=plt.get_cmap("Greys"));


def save_plot(list_coloured_lines, list_colours, file_name, size, n_hooks):
    """
    Saves the plot of lines as a jpeg with a specified name.
    It can also save multicoloured images; colours are added in the order they appear in the list.
    The colour tuples are interpreted using RGB format.
    """
    new_hooks = generate_hooks(n_hooks, size)

    for i in range(len(new_hooks)):
        new_hooks[i] = [new_hooks[i][0], size - new_hooks[i][1]]

    thread_image = Image.new('RGB', (size,size), (255,255,255))
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
        lines_temp = list_coloured_lines[-1][:int(len(list_coloured_lines[-1])*prop)]
        list_coloured_lines_temp = list_coloured_lines[:-1] + [lines_temp]
        save_plot(list_coloured_lines_temp, list_colours, file_name_temp, size, n_hooks)


def total_distance(lines, hooks, wheel_diameter_m, wheel_pixel_size):
    """
    Prints out the total distance of thread needed to make the model (in meters).
    """
    d = 0
    for line in lines:
        hook_A, hook_B = hooks[line[0]], hooks[line[1]]
        d += ((hook_A[0]-hook_B[0])**2 + (hook_A[1]-hook_B[1])**2) ** 0.5

    d = d * (wheel_diameter_m / wheel_pixel_size)

    print(f"distance = {int(d)} meters")


def display_output(lines):
    """
    Prints out the lines in a form that can be interpreted (used for manual threading).
    """
    #print(f"{lines[0][0]//2}-{lines[0][0]%2}")
    outlist=[]
    for i in range(len(lines)):
        if i%100 == 0 and i>0:
            #print(f"\n{i}\n")
            outlist.append('\n')
        line = lines[i]
        #output_number = f"{line[1]//2}-{line[1]%2}"
        output_number = f"{line[1]//2}"
        #print(output_number)
        outlist.append(output_number)
        #print(line)
    print(' '.join(outlist))


def main(src_file, src_file_weighted, out_file, n_hooks, n_lines, wheel_diameter_m, wheel_pixel_size):
    hooks = generate_hooks(n_hooks, wheel_pixel_size)
    through_pixels_dict = build_through_pixels_dict(hooks, n_hooks, wheel_pixel_size)

    image_m = prepare_image(src_file, wheel_pixel_size)
    image_w = False
    # image where black are weighted areas: they matter more in terms of accuracy
    # you basically want the target black and the background white/grey
    if src_file_weighted is not None:
        image_w = prepare_image("example_weighted.jpg", wheel_pixel_size, weighting=True)

    lines = find_lines(through_pixels_dict, n_hooks, wheel_pixel_size,
                       image_m, n_lines=n_lines,
                       darkness=250, lightness_penalty=0,
                       w=image_w,
                       line_norm_mode="weighted length" if type(image_w) != bool else "length",
                       time_saver=0.5)

    save_plot([lines], [(0,0,0)], out_file, wheel_pixel_size, n_hooks)
    save_plot_progress([lines], [(0,0,0)], out_file, wheel_pixel_size, n_hooks,
                       np.arange(0.0, 1.0, 1.0/(n_lines//100)))
    total_distance(lines, hooks, wheel_diameter_m, wheel_pixel_size)
    display_output(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Creates threaded paintings based on a source image. Records instructions to build them in real life.'''
    )
    parser.add_argument('src', help='''Source file (.jpg, .png, ...)''')
    parser.add_argument('--dst_dir', default="out", dest='dst_dir',
                        help='''Folder to output files into''')
    parser.add_argument('--hooks', type=int, default=180, dest='hooks',
                        help='''Amount of hooks in portrait''')
    parser.add_argument('--lines', type=int, default=2500, dest='lines',
                        help='''Amount of thread lines in portrait, crossing the hooks''')
    parser.add_argument('--wheel_m', type=float, default=0.540, dest='wheel_m',
                        help='''Diameter (in meters) of wheel portrait''')
    parser.add_argument('--wheel_p', type=int, default=1500, dest='wheel_p',
                        help='''Diameter (in pixels) of output images''')
    parser.add_argument('--weighted', default=None, dest='weighted',
                        help='''A secondary image with more important zones having dark masks''')
    parser.add_argument('--verbose', action='store_true', dest='verbose',
                        help='''Whether to print all info''')
    args = parser.parse_args()

    # sanitize input
    if not os.path.isfile(args.src):
        print("File " + args.src + " not found")
        exit(0)
    if args.weighted is not None and not os.path.isfile(args.weighted):
        print("File " + args.weighted + " not found")
        exit(0)
    if len(args.dst_dir) != 0 and not os.path.isdir(args.dst_dir):
        try:
            os.mkdir(dst_dir)
        except Exception:
            print("Unable to create dir " + args.dst_dir)
            exit(0)
    n_hooks = max(3, args.hooks)
    # maximum amount of lines is equal to 1+2+...+n_hooks-1
    n_lines = max(1, min(args.lines, int((n_hooks-1)*(n_hooks/2))))
    wheel_m = max(0.1, args.wheel_m)
    wheel_p = max(10, args.wheel_p)

    main(args.src, args.weighted,
         os.path.join(args.dst_dir, "out"),
         n_hooks, n_lines,
         wheel_m, wheel_p)