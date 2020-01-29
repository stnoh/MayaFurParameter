###############################################################################
## Fur parameter search by Feature Space Gradient Descent
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds

import traceback
import shutil, os
from datetime import datetime
from collections import OrderedDict

import numpy as np
import cv2
from scipy import optimize

from stNoh import FurParam
import Misc


def LocalSearch(
        get_feature_func, calc_cost_func, render_and_load,
        convert_param_func, params01_vec_dst,
        folder_path, image_ext, opt_params_dict={},
    ):

    ############################################################
    ## prepare optimization routine
    ############################################################

    ## set constants for optimization in advance
    max_iter = 600  if opt_params_dict.get('max_iter') is None else opt_params_dict['max_iter']
    delta    = 0.10 if opt_params_dict.get('delta')    is None else opt_params_dict['delta']

    ## prepare reference image & get perceptual feature
    path_img_ref = folder_path + "/_ref_image.{0}".format(image_ext)
    img_ref_cv2  = cv2.imread(path_img_ref)
    G_ref, _     = get_feature_func(img_ref_cv2)

    Misc.show_text_on_image_cv2(img_ref_cv2, "", "reference")


    ############################################################
    ## function to evaluate
    ############################################################
    global success 
    success = True
    
    global num_iter
    num_iter = 0

    ## initial cost = Infinity (Unknown)
    global Cost_best
    Cost_best  = np.inf
    global params_01_vec_best
    params_01_vec_best = params01_vec_dst[:]

    ## wrapping evaluation function
    def eval_cost(params01_vec_dst):
        global Cost_best, params_01_vec_best
        global num_iter, success
        num_iter += 1

        params_dict = convert_param_func(params01_vec_dst)

        path_dst          = '{0}/iter_{1:04d}'.format(folder_path, num_iter)
        img_dst_cv2, _, _ = render_and_load(params_dict, path_dst)
        G_dst, _          = get_feature_func(img_dst_cv2)
        Cost_this         = calc_cost_func(G_ref, G_dst)

        img_text = "Cost: {0}\n#iter {1}".format(Cost_this, num_iter)
        Misc.show_text_on_image_cv2(img_dst_cv2, img_text, "find_step")

        ## change the best result
        if  Cost_this < Cost_best:
            Cost_best = Cost_this
            params_01_vec_best = params01_vec_dst[:]
    
        ## show the progress bar here
        prog = num_iter + 1
        cmds.progressWindow(edit=True, progress=prog)
        if cmds.progressWindow(query=1, isCancelled=1):
            success = False ## [ABORT]
            raise StopIteration

        return Cost_this

    ############################################################
    ## run optimization loop
    ############################################################

    ## start the progress bar here
    maxValue = max_iter+1
    cmds.progressWindow(isInterruptable=1, minValue=0, maxValue=maxValue)

    try:
        bounds = [(0.0, 1.0)] * len(params01_vec_dst)

        ## minimize with "bounds": SLSQP, trust-constr, L-BFGS-B, TNC
        opt = optimize.minimize( eval_cost, params01_vec_dst, 
                method='SLSQP',
                bounds=bounds,
                options={'eps':delta, 'maxiter':max_iter}
                )

        best_params_dict = convert_param_func(opt.x)
        success = True
    
    except Exception as e:
        traceback.print_exc()
        success = False
        pass

    ## best parameter until the last iteration ...
    best_params_dict = convert_param_func(params_01_vec_best)
    
    cmds.progressWindow(endProgress=1)
    return success, best_params_dict


###############################################################################
## example of usage
###############################################################################
if "__main__" == __name__:

    ############################################################
    ## user specified parameters
    ############################################################
    imgFileExt = "jpg"
    folder_reference = "C:/FurImages/Experiment1-CGSamples/_References_960x540"
    folder_temp_root = "C:/FurImages/Experiment1-CGSamples"
    num_of_repeat = 1

    ########################################
    ## parameter normalization [0.0:1.0]
    ########################################
    def convert_param_func(params01_vec):
        params01_dict = {}
        for cnt, key in enumerate(FurParam.ParamsGeom):
            params01_dict[key] = params01_vec[cnt]

        params_dict = FurParam.ConvertFurParams(params01_dict, True)
        return params_dict
    
    ## pick reference image files from folder
    fileList = next(os.walk(folder_reference))[2]
    fileList = [imgFile for imgFile in fileList if ".{0}".format(imgFileExt)==os.path.splitext(imgFile)[1]]

    ############################################################
    ## main iteration
    ############################################################
    abort = False

    for i in range(num_of_repeat):
        for imgFile in fileList:

            ## initialize renderer wrapper
            furRenderer = Misc.FurRenderer()

            ############################################################
            ## create temporary folder and copy image file to the folder
            ############################################################
            img_ref_path = "{0}/{1}".format(folder_reference, imgFile)

            folder_root = "{0}/{1}_{2}".format(
                folder_temp_root,
                os.path.splitext(imgFile)[0],
                datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            os.makedirs(folder_root) # root folder to preserve optimization progress
            shutil.copy2(img_ref_path, folder_root+"/_ref_image.{0}".format(imgFileExt))

            furRenderer.Init(folder_root)

            ############################################################
            ## get default colors for initialization
            ############################################################
            init_params_dict = FurParam.ParamsColor

            ## get .csv if exists
            csv_ref_path = os.path.splitext(img_ref_path)[0]+".csv"
            if True==os.path.isfile(csv_ref_path):
                shutil.copy2(csv_ref_path, folder_root+"/_ref_image.csv")

                ## read .csv and add to init_params_dict
                init_params_dict_file = FurParam.csv2dict(csv_ref_path)

                init_params_dict = OrderedDict( 
                    list(init_params_dict.items()) +
                    list(init_params_dict_file.items())
                )
            
            ## assign the initial color parameters before optimization
            furRenderer.RenderFur(init_params_dict, folder_root+"/temp")
            
            ############################################################
            ## invert initial parameter dictionary as vector
            ############################################################

            ## 1) random initial parameters [NOT SO USEFUL]
            #params01_vec_dst = np.random.random(15)

            ## 2) use initial parameters from Bayesian optimization
            #'''
            csv_ref_path = os.path.splitext(img_ref_path)[0]+"_bayesopt.csv"
            init_params_dict = FurParam.csv2dict(csv_ref_path)
            params01_vec_dst = []
            #'''

            for key in FurParam.ParamsGeom:
                value = init_params_dict[key]
                val01 = FurParam.ConvertFurParam(key, value)
                params01_vec_dst.append(val01)

            ############################################################
            ## run optimization on GEOMETRY parameters
            ############################################################
            succeeded, shape_param_dict = LocalSearch(
                vgg_max_gray_gram, calc_cost_func, furRenderer.RenderFur,
                convert_param_func, params01_vec_dst,
                folder_root, imgFileExt
            )
            
            ## render the best result
            furRenderer.RenderFur(shape_param_dict, folder_root+"/_best_shape")

            if False==succeeded:
                abort = True
                break
        
        ## abort remained task
        if abort:
            break
    
    ############################################################
    ## end
    ############################################################
    cv2.destroyAllWindows()
