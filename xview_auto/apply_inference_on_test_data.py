import sys
import pandas as pd
import os #Added in order to make paths relative
import cv2
from pathlib import Path
import shapely.wkt
# this program is going to automate everything..

os.chdir(os.getcwd())
print(os.getcwd()) #For testing. Can be removed whenever, but won't affect performance

path=os.getcwd()
print('path is' + path)

#GLOBAL VARIABLES

WEIGHT_LOC_PTH = path +'/xview2/weights/localization.h5'
MEAN_PTH = path +'/xview2/weights/mean.npy'
WEIGHT_DAM_PTH = path +'/xview2/weights/classification.hdf5'

PRE_IMAGE = path +'/xview2/test/mexico-earthquake_00000004_post_disaster.png' 
POST_IMAGE = path +'/xview2/test/mexico-earthquake_00000004_post_disaster.png' 

if __name__ == '__main__': 
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--nbr',
                        required=True)
    parser.add_argument('--disaster',
                        required=True)
    args = parser.parse_args()
    
test_files = os.listdir(path +'/test/images')
post_disasters = []
disaster_names = []
disaster_post_dict = {}
for label in test_files:
    if 'post' in label:
        post_disasters.append(label)

        disaster_name = label.split('_')[0]
        if disaster_name not in disaster_names:
            disaster_names.append(disaster_name)

# now I want to create a dictionary with disaster_names as key and list of post_disasters
for i in disaster_names:
    disaster_post_dict[i]= [d for d in post_disasters if i in d]

from xview2.spacenet.inference import inference
from xview2.model import process_data_inference
from xview2.model import damage_inference
from xview2.utils import combine_jsons

def calculate_inference(PRE_IMAGE, POST_IMAGE):
    print(PRE_IMAGE, POST_IMAGE)
    image_label_json = inference.inference2(image=PRE_IMAGE, weights=WEIGHT_LOC_PTH, mean=MEAN_PTH)
    if len(image_label_json['features']['xy']) > 0:
        poly_dict = process_data_inference.process_img_poly2(img_path=POST_IMAGE, label_json=image_label_json)
        classification_json = damage_inference.run_inference2(test_data=poly_dict, model_weights=WEIGHT_DAM_PTH)
        inference_json = combine_jsons.combine_output2(pred_polygons=image_label_json, pred_classification=classification_json)
        return inference_json
    else:
        return None
df_combined = pd.DataFrame()
feat_types = []
sub_types = []
polygon_areas = []

file_labels = disaster_post_dict[args.disaster]
start = 0 + (6*int(args.nbr))
if start + 6 > len(file_labels):
    end = len(file_labels)
else:
    end = start + 6


for file_label in file_labels[start:end]:
    
    data = calculate_inference(os.path.join(path, 'test/images', file_label.replace('_post_', '_pre_')), os.path.join(path, 'test/images', file_label))
    if data:
        for x in data['features']['xy']:
            feat_type = x['properties']['feature_type']
            sub_type = x['properties']['subtype']
            polygon_geom = shapely.wkt.loads(x['wkt'])
            polygon_area = polygon_geom.area
            feat_types.append(feat_type)
            sub_types.append(sub_type)
            polygon_areas.append(polygon_area)
    
    df = pd.DataFrame(list(zip(feat_types, sub_types, polygon_areas)), 
           columns =['feature', 'sub_type', 'area'])
    df['disaster'] = args.disaster
    
    df_combined = df_combined.append(df)

df_combined.to_csv('test_df_' +str(args.disaster) + str(args.nbr) + '.csv')
#for disaster_i in disaster_names:
#    feat_types = []
#    sub_types = []
#    polygon_areas = []
#    for file_label in disaster_post_dict[disaster_i]:
#        data = calculate_inference(os.path.join(path, 'test/images', file_label.replace('_post_', '_pre_')), os.path.join(path, 'test/images', file_label))
#        if data:
#            for x in data['features']['xy']:
#                feat_type = x['properties']['feature_type']
#                sub_type = x['properties']['subtype']
#                polygon_geom = shapely.wkt.loads(x['wkt'])
#                polygon_area = polygon_geom.area
#                feat_types.append(feat_type)
#                sub_types.append(sub_type)
#                polygon_areas.append(polygon_area)
#    df = pd.DataFrame(list(zip(feat_types, sub_types, polygon_areas)), 
#               columns =['feature', 'sub_type', 'area'])
#    df['disaster'] = disaster_i
    
#    df_combined = df_combined.append(df)

#df_combined.to_csv('test_df2.csv')

