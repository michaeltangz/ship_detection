# Satellite Image Ship Detection

This script processes satellite imagery to detect ships using NDWI (Normalized Difference Water Index) and image processing techniques.

## Description

The script performs the following main operations:
1.  Loads a true-color RGB image and a pre-calculated NDWI (Normalized Difference Water Index) image.
2.  Applies a threshold to the NDWI image to create a water mask (separating water from land).
3.  Refines the water mask using a mode filter and binary erosion to reduce noise and shoreline effects.
4.  Applies a set of line detection filters (high-pass filters) to the original NDWI array within the eroded water mask to identify potential ship-like features. Ships are expected to appear darker than the surrounding water in the NDWI image.
5.  Highlights detected ships with red squares on the true-color RGB image.
6.  Optionally, generates an animation sequence showing the detection process (though this part might be resource-intensive or modified).

## Input Files

The script expects the following input files to be present in the same directory:

*   `True_color7.png`: The true-color RGB satellite image. (Originally sourced from Sentinel Hub EO Browser)
*   `Custom_script7.png`: A single-band image representing the NDWI values. This script assumes it's a grayscale image where pixel values correspond to NDWI.

## Key Parameters (from `main1.py`)

These parameters can be adjusted within `main1.py` to fine-tune the detection:

*   `manual_threshold_for_ndwi = 140.0`: The threshold applied to the raw NDWI array to create the initial water mask. Pixels with NDWI values greater than this are considered water.
*   `threshold_for_ship = 25`: A sensitivity threshold for ship detection. The line detection filters produce a response; if the minimum (most negative) response for a pixel is less than or equal to `-threshold_for_ship`, it's considered a potential ship.
*   `square_side = 16`: The side length (in pixels) of the red squares drawn around detected ships for visualization.
*   `iterations` for `ndi.binary_erosion` (currently `5`): The number of iterations for the binary erosion step applied to the water mask. This helps to shrink the water mask and remove small connections, potentially reducing shoreline false positives.

## Core Processing Steps

1.  **Load Data**: Opens RGB and NDWI images using GDAL.
2.  **NDWI Thresholding**: Creates a binary water mask using `manual_threshold_for_ndwi`.
3.  **Mode Filtering**: Applies a 3x3 mode filter to the binary water mask to remove salt-and-pepper noise.
4.  **Erosion**: Erodes the mode-filtered water mask to further refine it and reduce shoreline effects.
5.  **Line Detection for Ships**:
    *   Iterates through pixels within the eroded water mask.
    *   Applies four 3x3 line detection masks (horizontal, vertical, +45 degrees, -45 degrees) to a 3x3 window of the original `array_ndwi`.
    *   Calculates the sum of the element-wise product for each mask.
    *   Identifies ships where the minimum sum (most negative response) is less than or equal to `-threshold_for_ship`.
6.  **Visualization**: Saves intermediate and final processed images (thresholded NDWI, mode-filtered NDWI, eroded NDWI, ships in NDWI, and ships highlighted on RGB).
7.  **Animation**: Generates a series of PNG images for an animation, showing ships being detected with scanning bars (this part might be modified or removed in some versions).

## Output Files

The script saves its output to the `results/` and `animation/` subdirectories (ensure these exist or are created by the script if needed, though a `.gitignore` is set up to ignore them).

**In `results/` (filenames depend on thresholds):**
*   `tn<NDWI_THRESH>_ts<SHIP_THRESH>_threshold_ndwi.png`: The binary water mask after applying the NDWI threshold.
*   `tn<NDWI_THRESH>_ts<SHIP_THRESH>_mode_threshold_ndwi.png`: The water mask after mode filtering.
*   `tn<NDWI_THRESH>_ts<SHIP_THRESH>_eroded_mode_threshold_ndwi.png`: The water mask after erosion.
*   `tn<NDWI_THRESH>_ts<SHIP_THRESH>_ships_in_ndwi.png`: A binary image showing detected ship pixels within the NDWI domain.
*   `tn<NDWI_THRESH>_ts<SHIP_THRESH>_ships_in_rgb.png`: The original RGB image with detected ships highlighted by red squares.

**In `animation/`:**
*   A sequence of `ships_in_rgb_step_XXXXXX.png` files if the animation part is active.

## Dependencies

The script relies on the following Python libraries:

*   `osgeo` (GDAL): For reading geospatial raster data (GeoTIFF and other formats like PNG if georeferenced or treated as plain rasters).
*   `matplotlib`: For plotting and saving images, and for drawing patches (squares).
*   `numpy`: For numerical operations, especially array manipulation.
*   `scipy`: Specifically `scipy.stats` for the mode filter and `scipy.ndimage` for morphological operations (erosion).
*   `scikit-image`: Specifically `skimage.filters.threshold_otsu` (though currently commented out in favor of a manual NDWI threshold).

You can typically install these using pip:
\`\`\`bash
pip install GDAL matplotlib numpy scipy scikit-image
\`\`\`
(Note: GDAL installation can sometimes be complex depending on your OS and Python environment. Using a package manager like Conda is often recommended for GDAL.)

## How to Run

1.  Ensure all dependencies are installed.
2.  Place the required input PNG files (`True_color7.png`, `Custom_script7.png`) in the same directory as `main1.py`.
3.  Modify parameters within `main1.py` as needed (especially `manual_threshold_for_ndwi` and `threshold_for_ship`).
4.  Run the script from your terminal:
    \`\`\`bash
    python main1.py
    \`\`\`
5.  Output images will be saved in the `results/` directory. Animation frames (if active) will be in `animation/`.

## Original Author

*   Thales Sehn Körting (http://youtube.com/tkorting)

This README provides a general overview based on the provided `main1.py` script. 