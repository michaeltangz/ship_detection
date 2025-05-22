# Subscribe to my channel, share and like my videos at
# http://youtube.com/tkorting
#
# Feel free to use and share this code.
#
# Thales Sehn Körting

# importing libraries
# needed to open GeoTIFF files
from osgeo import gdal
from osgeo import gdalconst
# needed to create plots and squares
import matplotlib.pyplot as plt
import matplotlib.patches as patches
# needed to manipulate arrays
import numpy as np
# needed to compute mode from arrays
from scipy import stats
# needed to deal with colorbars
from mpl_toolkits.axes_grid1 import make_axes_locatable # This is imported but not used in the simplified version. Can be removed if not needed elsewhere.
# For Otsu's thresholding
from skimage.filters import threshold_otsu
# For morphological operations (erosion)
import scipy.ndimage as ndi

# define constants
figure_border = 25
epsilon = 0.0001 # Not used in this simplified version. Can be removed.
max_y = 5000 # Used in removed histogram part. Can be removed.
max_steps = 500 # Used in animation parts. Keep for ship highlighting animation.
square_side = 16
# threshold_for_ndwi will be determined automatically by Otsu's method below
# threshold_for_ndwi = 153.0 # We use this fixed value now. Adjusted for 0-255 scaled NDWI
threshold_for_ship = 25 # Adjusted for 0-255 scaled NDWI. Decreased to find more ships.

# define filenames
filename_rgb = "True_color7.png" # available at https://apps.sentinel-hub.com/eo-browser/?lat=-24.1176&lng=-46.3688&zoom=12&time=2019-04-02
# Removed filenames for green and nir bands as we will load NDWI directly.
filename_ndwi = "Custom_script7.png" # Assuming you have this file ready with NDWI values.

# load the datasets
dataset_rgb = gdal.Open(filename_rgb, gdalconst.GA_ReadOnly)
# Removed datasets for green and nir.
dataset_ndwi = gdal.Open(filename_ndwi, gdalconst.GA_ReadOnly) # Load the pre-calculated NDWI dataset.

# retrieve metadata from RGB raster (assuming NDWI has the same dimensions)
rows = dataset_rgb.RasterYSize
columns = dataset_rgb.RasterXSize
N = rows * columns # Not used in this simplified version. Can be removed.
bands = 3 # Refers to RGB bands.

# get arrays
# Removed calculation of NDWI from green and nir.
# Read the NDWI array directly.
# IMPORTANT: Ensure your 'ndwi.png' file contains float data representing NDWI
# or adjust the 'threshold_for_ndwi' value if 'ndwi.png' is an 8-bit (0-255) representation.
# If it's 8-bit, you'll likely need to scale the threshold. Assuming float data here.
array_ndwi = dataset_ndwi.GetRasterBand(1).ReadAsArray().astype(float)

# ADD DIAGNOSTIC PRINTS
print(f"NDWI Array Min: {np.min(array_ndwi)}")
print(f"NDWI Array Max: {np.max(array_ndwi)}")
print(f"NDWI Array Mean: {np.mean(array_ndwi)}")
print(f"NDWI Array Shape: {array_ndwi.shape}")
print(f"NDWI Array Data Type: {array_ndwi.dtype}")

# Determine NDWI threshold using Otsu's method (COMMENTED OUT - Using manual threshold below)
# threshold_for_ndwi_otsu = threshold_otsu(array_ndwi)
# print(f"Otsu's calculated threshold for NDWI: {threshold_for_ndwi_otsu}")

# MANUAL NDWI THRESHOLD (Adjust as needed for NDWI1.png)
manual_threshold_for_ndwi = 140.0 
print(f"Using manual NDWI threshold: {manual_threshold_for_ndwi}")

# get true color raster to show result
array_rgb = np.zeros((rows, columns, 3), dtype=np.uint8)
array_rgb[:,:,0] = dataset_rgb.GetRasterBand(1).ReadAsArray()
array_rgb[:,:,1] = dataset_rgb.GetRasterBand(2).ReadAsArray()
array_rgb[:,:,2] = dataset_rgb.GetRasterBand(3).ReadAsArray()

# print basic metadata
print ("image metadata:")
print (rows, "rows x", columns, "columns x", bands, "bands")

# create plot with input ndwi band (optional, just to visualize the input NDWI)
output_fig = plt.figure()
ndwi_ax = output_fig.add_subplot(111)
# Use a suitable colormap for NDWI, e.g., 'viridis' or 'gray'.
# If your input ndwi.png is 0-255, 'gray' might be appropriate.
# If it's float (-1 to 1), consider 'viridis' or a custom colormap.
ndwi_img = plt.imshow(array_ndwi, cmap="gray") # Or cmap="viridis" if float
ndwi_ax.set_xlim([0 - figure_border, columns + figure_border])
ndwi_ax.set_ylim([rows + figure_border, 0 - figure_border])
# Add a colorbar if using a colormap other than gray and it represents a range
# divider = make_axes_locatable(ndwi_ax)
# cax = divider.append_axes("right", size="5%", pad=0.05)
# plt.colorbar(ndwi_img, cax=cax)
# output_fig.savefig("results/input_ndwi.png", format='png', dpi=200) # Changed output name to reflect it's input NDWI

# Removed the animation for finding threshold in ndwi

filename_in_results = "results/tn" + str(manual_threshold_for_ndwi).replace('.','') + "_ts"+str(threshold_for_ship).zfill(3)+"_" # Updated filename for manual NDWI thresh

# create plot with ndwi band with threshold
threshold_ndwi = array_ndwi > manual_threshold_for_ndwi # Apply the MANUAL threshold
output_fig = plt.figure()
threshold_ndwi_ax = output_fig.add_subplot(111)
threshold_ndwi_img = plt.imshow(threshold_ndwi, cmap="gray")
threshold_ndwi_ax.set_xlim([0 - figure_border, columns + figure_border])
threshold_ndwi_ax.set_ylim([rows + figure_border, 0 - figure_border])
output_fig.savefig(filename_in_results+"threshold_ndwi.png", format='png', dpi=200)

# apply 3x3 mode filter to remove noise and save plot
mode_threshold_ndwi = np.copy(threshold_ndwi)
# Start loops from 1 and end at rows/columns - 1 to avoid indexing errors at borders
for i in range(1,rows - 1):
    for j in range(1,columns - 1):
        values = np.array(threshold_ndwi[i-1:i+2, j-1:j+2])
        # Convert boolean array to integers (0 and 1) before calculating mode
        values_int = values.astype(int)
        mode_result = stats.mode(values_int.ravel(), keepdims=False)
        # The mode result is now a scalar, so we can use it directly
        mode_threshold_ndwi[i, j] = bool(mode_result.mode)

output_fig = plt.figure()
mode_threshold_ndwi_ax = output_fig.add_subplot(111)
mode_threshold_ndwi_img = plt.imshow(mode_threshold_ndwi, cmap="gray")
mode_threshold_ndwi_ax.set_xlim([0 - figure_border, columns + figure_border])
mode_threshold_ndwi_ax.set_ylim([rows + figure_border, 0 - figure_border])
output_fig.savefig(filename_in_results+"mode_threshold_ndwi.png", format='png', dpi=200)

# Erode the water mask to remove shoreline edges from ship detection consideration
eroded_mode_threshold_ndwi = ndi.binary_erosion(mode_threshold_ndwi, iterations=5).astype(mode_threshold_ndwi.dtype)
# Optional: Save the eroded mask to visualize its effect
output_fig_eroded = plt.figure()
eroded_ax = output_fig_eroded.add_subplot(111)
plt.imshow(eroded_mode_threshold_ndwi, cmap="gray")
eroded_ax.set_xlim([0 - figure_border, columns + figure_border])
eroded_ax.set_ylim([rows + figure_border, 0 - figure_border])
output_fig_eroded.savefig(filename_in_results+"eroded_mode_threshold_ndwi.png", format='png', dpi=200)
plt.close(output_fig_eroded) # Close the figure for the eroded mask

# apply 3x3 filter to find points related to ships (highpass filter set)
ships_in_ndwi = np.zeros_like(array_ndwi, dtype=bool) # Initialize as boolean array
line_detection_mask_horizontal = np.array((-1, -1, -1, 2, 2, 2, -1, -1, -1)).reshape(3,3) # Original masks
line_detection_mask_plus45 = np.array((-1, -1, 2, -1, 2, -1, 2, -1, -1)).reshape(3,3) # Original masks
line_detection_mask_vertical = np.array((-1, 2, -1, -1, 2, -1, -1, 2, -1)).reshape(3,3) # Original masks
line_detection_mask_minus45 = np.array((2, -1, -1, -1, 2, -1, -1, -1, 2)).reshape(3,3) # Original masks

# Start loops from 1 and end at rows/columns - 1 for 3x3 kernel
for i in range(1,rows - 1):
    for j in range(1,columns - 1):
        # Only process pixels that are considered water after mode filtering AND erosion
        if eroded_mode_threshold_ndwi[i, j]:
            values = np.array(array_ndwi[i-1:i+2, j-1:j+2])

            # Ensure the window is the correct shape (should be 3x3 from the loops)
            # No need for the shape check `if values.ravel().shape == line_detection_mask_horizontal.shape:`
            # as the loops ensure a 3x3 window (except maybe borders, handled by loop range)

            # Calculate raw sums for each mask direction
            sum_h = (values * line_detection_mask_horizontal).sum()
            sum_p45 = (values * line_detection_mask_plus45).sum()
            sum_v = (values * line_detection_mask_vertical).sum()
            sum_m45 = (values * line_detection_mask_minus45).sum()

            # Ships are darker than water, so they produce a negative response with these masks.
            # We look for the most negative response (minimum sum).
            min_sum = min(sum_h, sum_p45, sum_v, sum_m45)
            
            # A ship is detected if the most negative response is strong enough.
            # threshold_for_ship is a positive value (e.g., 90), so we compare to -threshold_for_ship.
            if min_sum <= -threshold_for_ship:
                ships_in_ndwi[i, j] = True
            else:
                ships_in_ndwi[i, j] = False # Ensure it's explicitly False otherwise

output_fig = plt.figure()
ships_in_ndwi_ax = output_fig.add_subplot(111)
ships_in_ndwi_img = plt.imshow(ships_in_ndwi, cmap="gray")
ships_in_ndwi_ax.set_xlim([0 - figure_border, columns + figure_border])
ships_in_ndwi_ax.set_ylim([rows + figure_border, 0 - figure_border])
output_fig.savefig(filename_in_results+"ships_in_ndwi.png", format='png', dpi=200)

# create plot with rgb image with ships highlighted
output_fig = plt.figure(figsize=(9, 5))

rgb_ax = output_fig.add_subplot(111)
rgb_img = plt.imshow(array_rgb)
rectangles = np.zeros_like(ships_in_ndwi, dtype=float) # Use float for sum comparison
# Loop over points to draw squares
# Iterate through all pixels as ship locations can be anywhere
for row in range(rows):
    for column in range(columns):
        if ships_in_ndwi[row, column]:
            column_start = int(max(0, column - square_side/2)) # Ensure start is not negative
            column_end = int(min(columns, column + square_side/2)) # Ensure end is within bounds
            row_start = int(max(0, row - square_side/2)) # Ensure start is not negative
            row_end = int(min(rows, row + square_side/2)) # Ensure end is within bounds

            # Check if the area around the potential ship is already covered by a rectangle
            if rectangles[row_start:row_end, column_start:column_end].sum() == 0:
                ship_square = patches.Rectangle((column_start,row_start),square_side,square_side,linewidth=1,edgecolor='r',facecolor='none')
                rgb_ax.add_patch(ship_square)
                # Mark the area covered by the rectangle
                rectangles[row_start:row_end, column_start:column_end] = 1.0

rgb_ax.set_xlim([0 - figure_border, columns + figure_border])
rgb_ax.set_ylim([rows + figure_border, 0 - figure_border])
output_fig.savefig(filename_in_results+"ships_in_rgb.png", format='png', dpi=500)


# Create ship detection animation (kept this part as it's not threshold finding)
filename_in_animation = "animation/ships_in_rgb_step_"
step = 0
bar_rows = np.linspace(0, rows, max_steps)
bar_columns = np.linspace(0, columns, max_steps)

for bar_row, bar_column in zip(bar_rows, bar_columns):
    print (f"Animation step: {step}") # Use f-string for cleaner printing
    output_fig = plt.figure(figsize=(9, 5))

    rgb_ax = output_fig.add_subplot(111)
    rgb_img = plt.imshow(array_rgb)

    # Draw scanning bars (optional, can remove if not desired)
    rgb_ax.barh(bar_row, columns, 3, fc='r')
    rgb_ax.bar(bar_column, rows, 3, fc='r')

    rectangles = np.zeros_like(ships_in_ndwi, dtype=float) # Reset rectangles for each frame

    # Only draw rectangles for detected ships within the scanned area
    for row in range(int(bar_row)):
        for column in range(int(bar_column)):
            if ships_in_ndwi[row, column]:
                column_start = int(max(0, column - square_side/2))
                column_end = int(min(columns, column + square_side/2))
                row_start = int(max(0, row - square_side/2))
                row_end = int(min(rows, row + square_side/2))

                if rectangles[row_start:row_end, column_start:column_end].sum() == 0:
                    ship_square = patches.Rectangle((column_start,row_start),square_side,square_side,linewidth=1,edgecolor='r',facecolor='none')
                    rgb_ax.add_patch(ship_square)
                    rectangles[row_start:row_end, column_start:column_end] = 1.0

    rgb_ax.set_xlim([0 - figure_border, columns + figure_border])
    rgb_ax.set_ylim([rows + figure_border, 0 - figure_border])
    output_fig.savefig(filename_in_animation+str(step).zfill(6)+".png", format='png', dpi=200)
    step = step + 1
    plt.close(output_fig) # Close figure to free memory

# close all datasets
dataset_rgb = None
dataset_ndwi = None # Close the NDWI dataset instead of green/nir