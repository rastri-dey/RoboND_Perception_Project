import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from pcl_helper import *


def rgb_to_hsv(rgb_list):
    rgb_normalized = [1.0*rgb_list[0]/255, 1.0*rgb_list[1]/255, 1.0*rgb_list[2]/255]
    hsv_normalized = matplotlib.colors.rgb_to_hsv([[rgb_normalized]])[0][0]
    return hsv_normalized


def compute_color_histograms(cloud, using_hsv=True):

    # Compute histograms for the clusters
    point_colors_list = []

    # Step through each point in the point cloud
    for point in pc2.read_points(cloud, skip_nans=True):
        rgb_list = float_to_rgb(point[3])
	
        if using_hsv:
            point_colors_list.append(rgb_to_hsv(rgb_list) * 255)
        else:
            point_colors_list.append(rgb_list)
    	
    # Populate lists with color values
    channel_1_vals = []
    channel_2_vals = []
    channel_3_vals = []
    
    for color in point_colors_list:
        channel_1_vals.append(color[0])		#H
        channel_2_vals.append(color[1])		#S
        channel_3_vals.append(color[2])		#V
    
    # TODO: Compute histograms
    nbins = 64
    bins_range=(0, 256)
	    # Compute the histogram of the HSV channels separately
    h_hist = np.histogram(channel_1_vals, bins=nbins, range=bins_range)
    s_hist = np.histogram(channel_2_vals, bins=nbins, range=bins_range)
    v_hist = np.histogram(channel_3_vals, bins=nbins, range=bins_range)

 # TODO: Concatenate and normalize the histograms

	    # Concatenate the histograms into a single feature vector
    hist_features = np.concatenate((h_hist[0], s_hist[0], v_hist[0])).astype(np.float64)
	    # Normalize the result
    norm_features = hist_features / np.sum(hist_features)	
    return norm_features 


def compute_normal_histograms(normal_cloud):
    norm_x_vals = []
    norm_y_vals = []
    norm_z_vals = []

    for norm_component in pc2.read_points(normal_cloud,
                                          field_names = ('normal_x', 'normal_y', 'normal_z'),
                                          skip_nans=True):
        norm_x_vals.append(norm_component[0])
        norm_y_vals.append(norm_component[1])
        norm_z_vals.append(norm_component[2])

    # TODO: Compute histograms of normal values (just like with color)
    nbins = 64
    bins_range=(0, 256)
	    # Compute the histogram of the HSV channels separately
    h_hist = np.histogram(norm_x_vals, bins=nbins, range=bins_range)
    s_hist = np.histogram(norm_y_vals, bins=nbins, range=bins_range)
    v_hist = np.histogram(norm_z_vals, bins=nbins, range=bins_range)

    # TODO: Concatenate and normalize the histograms

	    # Concatenate the histograms into a single feature vector
    hist_features = np.concatenate((h_hist[0], s_hist[0], v_hist[0])).astype(np.float64)
	    # Normalize the result
    norm_features = hist_features / np.sum(hist_features)
    

    return norm_features
