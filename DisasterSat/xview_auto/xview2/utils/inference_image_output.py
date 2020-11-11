#####################################################################################################################################################################
# xView2                                                                                                                                                            #
# Copyright 2019 Carnegie Mellon University.                                                                                                                        #
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO    #
# WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY,          # 
# EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, # 
# TRADEMARK, OR COPYRIGHT INFRINGEMENT.                                                                                                                             #
# Released under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.                                                 #
# [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use  #
# and distribution.                                                                                                                                                 #
# This Software includes and/or makes use of the following Third-Party Software subject to its own license:                                                         #
# 1. SpaceNet (https://github.com/motokimura/spacenet_building_detection/blob/master/LICENSE) Copyright 2017 Motoki Kimura.                                         #
# DM19-0988                                                                                                                                                         #
#####################################################################################################################################################################


import json
from shapely import wkt
from shapely.geometry import Polygon
import numpy as np 
from cv2 import fillPoly, imwrite
from PIL import Image, ImageDraw
import rasterio.features
import shapely.geometry
import numpy as np

def open_json(json_file_path):
    """
    :param json_file_path: path to open inference json file
    :returns: the json data dictionary of localized polygon and their classifications 
    """

    with open(json_file_path) as jf:
        json_data = json.load(jf)
        inference_data = json_data['features']['xy']
        return inference_data

def create_image(inference_data):
    """
    :params inference_data: json data dictionary of localized polygon and their classifications
    :returns: an numpy array of 8-bit grey scale image with polygons filled in according to the key provided
    """
    print("CREATE_IMAGE IS BEING CALLED")
    damage_key = {'un-classified': 1, 'no-damage': 1, 'minor-damage': 2, 'major-damage': 3, 'destroyed': 4}

    mask_img = np.zeros((1024,1024,1), np.uint8)
    for poly in inference_data['features']['xy']: #added ['features']['xy']
        damage = poly['properties']['subtype']
        coords = wkt.loads(poly['wkt'])
        poly_np = np.array(coords.exterior.coords, np.int32)
        if damage in ('major-damage'):
            print(damage)
            print(coords)

        
        fillPoly(mask_img, [poly_np], damage_key[damage])
    
    return mask_img

def save_image(polygons, output_path):
    """
    :param polygons: np array with filled in polygons from create_image()
    :param output_path: path to save the final output inference image
    """

    # Output the filled in polygons to an image file
    imwrite(output_path, polygons)
  
def create_inference_image(json_input_path, image_output_path):
    """
    :param json_input_path: Path to output inference json file
    :param image_outut_pat: Path to save the final inference image
    """

    # Getting the inference data from the localization and classification 
    inference_data = open_json(json_input_path)

    # Filling in the polygons and readying the image format 
    polygon_array = create_image(inference_data)

    # Saving the image to the desired location
    save_image(polygon_array, image_output_path)


def create_inference_image2(inference_json, POST_WITH_DAMAGE_CLASS_MASK, POST_IMAGE):
    """
    :param json_input_path: Path to output inference json file
    :param image_outut_pat: Path to save the final inference image
    """

    no_damage_polygons = []
    minor_damage_polygons = []
    major_damage_polygons = []
    destroyed_polygons = []

    # Load the challenge output localization image
    #localization = Image.open(path_to_localization)
    #loc_arr = np.array(localization)
    # load inference_json as an in image..
   ### loc_arr = create_image(inference_json)

    # If the localization has damage values convert all non-zero to 1
    # This helps us find where buildings are, and then use the damage file
    # to get the value of the classified damage
    ###loc_arr = (loc_arr >= 1).astype(np.uint8)

    # Load the challenge output damage image
    #damage = Image.open(path_to_damage)
    #dmg_arr = np.array(damage)
    
    #I don't see why the localization image and damage image are different.. making them same
    dmg_arr = create_image(inference_json)
    # Use the localization to get damage only were they have detected buildings
    mask_arr = dmg_arr####*loc_arr
    print ("Shape of mask_arr", mask_arr.shape)
    #in other code they want (1024,1024) not (1024, 1024, 1)
    mask_arr = np.squeeze(mask_arr)
    # Get the value of each index put into a dictionary like structure
    shapes = rasterio.features.shapes(mask_arr)
    print(shapes)
    # Iterate through the unique values of the shape files 
    # This is a destructive iterator or else we'd use the pythonic for x in shapes if x blah 
    for shape in shapes:
        print("shape[1]", shape[1])
        if shape[1] == 1:
            no_damage_polygons.append(shapely.geometry.Polygon(shape[0]["coordinates"][0]))
        elif shape[1] == 2:
            minor_damage_polygons.append(shapely.geometry.Polygon(shape[0]["coordinates"][0]))
        elif shape[1] == 3:
            major_damage_polygons.append(shapely.geometry.Polygon(shape[0]["coordinates"][0]))
        elif shape[1] == 4:
            destroyed_polygons.append(shapely.geometry.Polygon(shape[0]["coordinates"][0]))
        elif shape[1] == 0:
            continue
        else:
            print("Found non-conforming damage type: {}".format(shape[1]))
    
    # Loading post image
    print('opening post image')
    img = Image.open(POST_IMAGE) 
    
    print(len(no_damage_polygons), 'no damage')
    print(len(major_damage_polygons), 'major damage')
    
    draw = ImageDraw.Draw(img, 'RGBA')
    
    damage_dict = {
        "no-damage": (0, 255, 0, 100),
        "minor-damage": (0, 0, 255, 125),
        "major-damage": (255, 69, 0, 125),
        "destroyed": (255, 0, 0, 125),
        "un-classified": (255, 255, 255, 125)
    }
    
    # Go through each list and write it to the post image we just loaded
    for polygon in no_damage_polygons:
        x,y = polygon.exterior.coords.xy
        coords = list(zip(x,y))
        print('drawing no damage')
        draw.polygon(coords, damage_dict["no-damage"])

    for polygon in minor_damage_polygons:
        x,y = polygon.exterior.coords.xy
        coords = list(zip(x,y))
        print ('drawing minor')
        draw.polygon(coords, damage_dict["minor-damage"])

    for polygon in major_damage_polygons:
        x,y = polygon.exterior.coords.xy
        coords = list(zip(x,y))
        print('Drawing Major')
        draw.polygon(coords, damage_dict["major-damage"])

    for polygon in destroyed_polygons:
        x,y = polygon.exterior.coords.xy
        coords = list(zip(x,y))
        print('Drawing Destroyed')
        draw.polygon(coords, damage_dict["destroyed"])
    print("saving post image", POST_WITH_DAMAGE_CLASS_MASK)
    img.save(POST_WITH_DAMAGE_CLASS_MASK)

if __name__ == '__main__': 
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=
        """inference_image_output.py: Takes the inference localization and classification final outputs in json from and outputs an image ready to be scored based off the challenge parameters""")
    parser.add_argument('--input',
                        required=True,
                        metavar='/path/to/final/inference.json',
                        help="Full path to the final inference json")
    parser.add_argument('--output',
                        required=True,
                        metavar='/path/to/inference.png',
                        help="Full path to save the image to")

    args = parser.parse_args()

    # Creating the scoring image
    create_inference_image(args.input, args.output)
