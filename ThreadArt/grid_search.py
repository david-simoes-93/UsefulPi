#!/usr/bin/env python
# coding: utf-8

"""
Conducts a grid search over parameters
"""

from generate import *


def main(src_file, src_file_weighted, src_file_wpos, src_file_wneg,
         out_file, no_progress_output,
         n_hooks, n_lines, line_darkness, light_penalty,
         wheel_diameter_m, wheel_pixel_size,
         hooks, through_pixels_dict):

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
    n_hooks_vals = [180, 360]
    line_w_milim_vals = [0.5, 0.8]
    n_lines_vals = [4000]
    line_darkness_vals = [125, 180]
    light_penalty_vals = [0.5]
    wheel_m_vals = [0.540]
    
    for n_hooks in n_hooks_vals:
        for line_w_milim in line_w_milim_vals:
            line_w_m = line_w_milim / 1000      # line width in meters
            wheel_p = int(1 / line_w_m)         # diameter (in pixels) of thread portrait
            hooks = generate_hooks(n_hooks, wheel_p)
            through_pixels_dict = build_through_pixels_dict(
                hooks, n_hooks, wheel_p)
            
            for n_lines in n_lines_vals:
                for line_darkness in line_darkness_vals:
                    for light_penalty in light_penalty_vals:
                        for wheel_m in wheel_m_vals:
                            dst_dir = "out_"+str(n_hooks)+"_"+str(line_w_milim)+"_"+str(n_lines)+"_"+str(line_darkness)+"_"+str(light_penalty)+"_"+str(wheel_m)
                            os.mkdir(dst_dir)
                            main(os.path.join("CheHigh", "che2.png"), None, os.path.join("CheHigh", "che_wpos.png"), os.path.join("CheHigh", "che_wneg.png"),
                                 os.path.join(dst_dir, "out"),
                                 False, n_hooks, n_lines, line_darkness, light_penalty, wheel_m, wheel_p,
                                 hooks, through_pixels_dict)
