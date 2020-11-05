
import sys
import pandas as pd
import os #Added in order to make paths relative
import cv2
# this program is going to automate everything..

# this program is going to automate everything..
#os.getcwd()
os.chdir('/Users/fire/Desktop/GIT_Repos/xview2_uva/xview_auto')

#GLOBAL VARIABLES
WEIGHT_LOC_PTH = '/Users/fire/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/weights/localization.h5'
MEAN_PTH = '/Users/fire/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/weights/mean.npy'
WEIGHT_DAM_PTH = '/Users/fire/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/weights/classification.hdf5'

PRE_IMAGE = '/Users/fire/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/mexico-earthquake_00000004_pre_disaster.png'
POST_IMAGE = '/Users/fire/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/mexico-earthquake_00000004_post_disaster.png'

POST_WITH_DAMAGE_CLASS_MASK = '/Users/fire/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/mexico-earthquake_00000004_prediction.png'

#input
##pre_image
##post_image

#step 1
## Call Inference.py in (~/xview/xView2_baseline/spacenet/inference/inference.py)
    #input
        ##pre_image
        ##post_image
        ##WEIGHT_LOC_PTH
        ##WEIGHT_LOC_PTH
    #output
        ##labels.json ##contains the label polygons
#i don't know why i couldn't import unet inside of segmentation_cpu. Just copied calss definition in segmentation cpu
from xview2.spacenet.inference import inference
image_label_json = inference.inference2(image=PRE_IMAGE, weights=WEIGHT_LOC_PTH, mean=MEAN_PTH)
#print(image_label_json)

#step 2
#sys.path.append('~/xview/xview_auto/xView2_baseline/model/process_data_inference.py')
##Create Polygon png images from the localization results..
## call process_data_inference
    #input
        ##post_image
        ##image_label_json (output from step 1)
    #output
        ##output_polygons (bunch of .png)
        ##csv file (could use DataFrame)
from xview2.model import process_data_inference
poly_dict = process_data_inference.process_img_poly2(img_path=POST_IMAGE, label_json=image_label_json)
#print(list(poly_dict.items())[:3])

#step 3
#sys.path.append('~/xview/xview_auto/xView2_baseline/model/damage_inference.py')
#Calculate Damage for Each Poly Dict
    #input
        #polygon arrays
        #model weights
    #outpyt
        #classification_json

#I had to copy model.py into damage_inference.py because of same import error.
#classification_json = run_inference2(test_data=poly_dict, model_weights=WEIGHT_DAM_PTH)
from xview2.model import damage_inference
classification_json = damage_inference.run_inference2(test_data=poly_dict, model_weights=WEIGHT_DAM_PTH)

#step 4
#combine jsons

#sys.path.append('~/xview/xview_auto/xView2_baseline/utils/combine_jsons.py')
#matching the json files
#image_label_json classification_json
#combine_output2(pred_polygons=image_label_json, pred_classification=classification_json)
from xview2.utils import combine_jsons

inference_json = combine_jsons.combine_output2(pred_polygons=image_label_json, pred_classification=classification_json)

#print(inference_json)


#step 5
#(xview) -bash-4.2$python ~/xview/xView2_baseline/utils/inference_image_output.py --input ~/xview/xView2_b
#aseline/tmp/inference/inference.json --output ~/xview/xView2_baseline/test/pred/output.png
#sys.path.append('~/xview/xview_auto/xView2_baseline/utils/inference_image_output.py')
from xview2.utils import inference_image_output
inference_image_output.create_inference_image2(inference_json, POST_WITH_DAMAGE_CLASS_MASK, POST_IMAGE)

#step 6
#overlay output
#add better image..
#I think I can in step 5 do all that is asked for in step 6..

