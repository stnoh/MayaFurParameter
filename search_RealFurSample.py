###############################################################################
## Fur parameter search by Feature Space Gradient Descent
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds

import traceback
import shutil, os
from datetime import datetime

import numpy as np
import cv2
from scipy import optimize ## minimize_scalar (line search)

from stNoh import FurParam
import Misc

## optimization routine
import search_BayesOpt
import search_FeatureGrad

###############################################################################
## [TEMPORARY] get background color
###############################################################################
def getBackgroundColor(img_cv2):
    bg_img1 = img_cv2[20:240, 20:180,:] ## left-top part
    bg_img2 = img_cv2[20:240,760:180,:] ## right-top part
    bg_sz  = bg_img1.shape[0]*bg_img1.shape[1] + bg_img2.shape[0]*bg_img2.shape[1]

    ## [0,255] to [0.0:1.0]
    bg_px_b = (np.sum(bg_img1[:,:,0]) + np.sum(bg_img2[:,:,0])) / (255.0 * bg_sz)
    bg_px_g = (np.sum(bg_img1[:,:,1]) + np.sum(bg_img2[:,:,1])) / (255.0 * bg_sz)
    bg_px_r = (np.sum(bg_img1[:,:,2]) + np.sum(bg_img2[:,:,2])) / (255.0 * bg_sz)

    return bg_px_r, bg_px_g, bg_px_b


###############################################################################
## example of usage
###############################################################################
if "__main__" == __name__:

    ############################################################
    ## user-specified values & paths
    ############################################################
    imgFileExt = "jpg"
    folder_reference = "C:/FurImages/Experiment2-RealSamples/_References_960x540"
    folder_temp_root = "C:/FurImages/Experiment2-RealSamples"
    num_of_repeat = 1

    ## camera background color setting
    Camera_name = "RenderCamShape2"

    ########################################
    ## parameter normalization [0.0:1.0]
    ########################################
    def convert_param_geom_func(params01_vec):
        params01_dict = {}
        for cnt, key in enumerate(FurParam.ParamsGeom):
            params01_dict[key] = params01_vec[cnt]

        params_dict = FurParam.ConvertFurParams(params01_dict, True)
        return params_dict

    def convert_param_color_func(params01_vec):
        params01_dict = {}
        for cnt, key in enumerate(FurParam.ParamsColor):
            params01_dict[key] = params01_vec[cnt]

        params_dict = FurParam.ConvertFurParams(params01_dict, True)
        return params_dict

    def invert_geom_func(params_dict):
        params01_vec_dst = []
        for key in FurParam.ParamsGeom:
            value = param_geom_dict[key]
            val01 = FurParam.ConvertFurParam(key, value)
            params01_vec_dst.append(val01)
        return params01_vec_dst

    def invert_color_func(params_dict):
        params01_vec_dst = []
        for key in FurParam.ParamsColor:
            value = param_color_dict[key]
            val01 = FurParam.ConvertFurParam(key, value)
            params01_vec_dst.append(val01)
        return params01_vec_dst

    ## pick reference image files from folder
    fileList = next(os.walk(folder_reference))[2]
    fileList = [imgFile for imgFile in fileList if ".{0}".format(imgFileExt)==os.path.splitext(imgFile)[1]]
    
    ############################################################
    ## iteration:
    ############################################################
    abort = False

    for i in range(num_of_repeat):
        for imgFile in fileList:

            ############################################################
            ## preparation before optimization
            ############################################################
            furRenderer = Misc.FurRenderer()

            img_ref_path = "{0}/{1}".format(folder_reference, imgFile)

            ## get background color from real fur sample images
            img = cv2.imread(img_ref_path)
            bg_px_r, bg_px_g, bg_px_b = getBackgroundColor(img)
            cmds.setAttr("{}.backgroundColor".format(Camera_name), bg_px_r,bg_px_g,bg_px_b, type="double3")

            ############################################################
            ## create temporary folder and copy image file to the folder
            ############################################################
            folder_root = "{0}/{1}_{2}_geom".format(
                folder_temp_root,
                os.path.splitext(imgFile)[0],
                datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            os.makedirs(folder_root) # root folder to preserve optimization progress
            shutil.copy2(img_ref_path, folder_root+"/_ref_image.{0}".format(imgFileExt))

            furRenderer.Init(folder_root)

            ## get default colors for initialization
            init_params_dict = FurParam.ParamsColor
            furRenderer.RenderFur(init_params_dict, folder_root+"/temp", False) ## test rendering ...

            ############################################################
            ## geometry optimization
            ############################################################
            params01_vec_dst = [0.5]*15 ## dummy for consistency

            ## 1) global geometry optimization by BayesOpt
            succeeded, param_geom_dict = search_BayesOpt.BayesOpt(
                vgg_max_gray_gram, calc_cost_func, furRenderer.RenderFur,
                convert_param_geom_func, params01_vec_dst,
                folder_root, imgFileExt, {"max_iter":100}
            )

            ## convert dictionary to vector
            params01_vec_dst = invert_geom_func(param_geom_dict)

            ## 2) local geometry optimization by FeatureGrad
            succeeded, param_geom_dict = search_FeatureGrad.GradientDescent(
                vgg_max_gray_gram, calc_cost_func, furRenderer.RenderFur,
                convert_param_geom_func, params01_vec_dst,
                folder_root, imgFileExt, {"max_iter":20,"max_step":15,"delta":0.1}
            )

            ## render the best result
            furRenderer.RenderFur(param_geom_dict, folder_root+"/_best_geom")
            
            ############################################################
            ## create temporary folder and copy image file to the folder
            ############################################################
            folder_root = "{0}/{1}_{2}_color".format(
                folder_temp_root,
                os.path.splitext(imgFile)[0],
                datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            os.makedirs(folder_root) # root folder to preserve optimization progress
            shutil.copy2(img_ref_path, folder_root+"/_ref_image.{0}".format(imgFileExt))

            furRenderer.Init(folder_root)
            furRenderer.RenderFur(init_params_dict, folder_root+"/temp", False) ## test rendering ...

            ############################################################
            ## color optimization
            ############################################################
            params01_vec_dst = [0.5]*10 ## dummy for consistency

            ## 3) global color optimization by BayesOpt
            succeeded, param_color_dict = search_BayesOpt.BayesOpt(
                vgg_max_color_gram, calc_cost_func, furRenderer.RenderFur,
                convert_param_color_func, params01_vec_dst,
                folder_root, imgFileExt, {"max_iter":50}
            )

            ## convert dictionary to vector
            params01_vec_dst = invert_color_func(param_color_dict)

            ## 4) local color optimization by FeatureGrad
            succeeded, param_color_dict = search_FeatureGrad.GradientDescent(
                vgg_max_color_gram, calc_cost_func, furRenderer.RenderFur,
                convert_param_color_func, params01_vec_dst,
                folder_root, imgFileExt, {"max_iter":20,"max_step":10,"delta":0.075}
            )

            ## render the best result
            furRenderer.RenderFur(param_color_dict, folder_root+"/_best_color")
            
            if False==succeeded:
                abort = True
                break
        
        ## abort remained task
        if abort:
            break

    ############################################################
    ## revert to default setting:
    ############################################################
    cmds.setAttr("{}.backgroundColor".format(Camera_name), 0,0,0, type="double3")
    cv2.destroyAllWindows()
