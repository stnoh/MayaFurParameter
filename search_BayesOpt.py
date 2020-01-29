###############################################################################
## Fur parameter search by Bayesian Optimization
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds

import traceback
import shutil, os
from datetime import datetime
from collections import OrderedDict

import numpy as np
import cv2
from skopt import Optimizer ## Bayesian optimization

from stNoh import FurParam
import Misc


###############################################################################
## optimization routine
###############################################################################
def BayesOpt(
        get_feature_func, calc_cost_func, render_and_load,
        convert_param_func, params01_vec_dst,
        folder_path, image_ext, opt_params_dict={},
    ):

    ############################################################
    ## prepara optimization routine
    ############################################################

    ## set constants for optimization in advance
    max_iter = 80  if opt_params_dict.get('max_iter') is None else opt_params_dict['max_iter'] ## 50: ~5-min / 100: ~10-min

    ## prepare reference image
    path_img_ref = folder_path + "/_ref_image.{0}".format(image_ext)
    img_ref_cv2  = cv2.imread(path_img_ref)
    G_ref, _     = get_feature_func(img_ref_cv2)
    
    Misc.show_text_on_image_cv2(img_ref_cv2, "", "reference")

    ## wrapping evaluation function
    def eval_cost(x, num_iter):
        x = np.clip(np.array(x), 0.0, 1.0)

        params_dict = convert_param_func(x)

        path_dst          = '{0}/bayesopt/iter_{1:04d}'.format(folder_path, num_iter)
        img_dst_cv2, _, _ = render_and_load(params_dict, path_dst)
        G_dst, _          = get_feature_func(img_dst_cv2)

        Cost = calc_cost_func(G_ref, G_dst)

        img_text = "Cost: {0}\n#iter {1}".format(Cost, num_iter)
        Misc.show_text_on_image_cv2(img_dst_cv2, img_text, "find_step")

        ## show the progress bar here
        cmds.progressWindow(edit=True, progress=num_iter)
        if cmds.progressWindow(query=1, isCancelled=1):
            raise StopIteration

        return Cost
    
    
    ############################################################
    ## run optimization loop
    ############################################################
    success = True

    ## initial cost = Infinity (Unknown)
    Cost_best  = np.inf
    params_01_vec_best = params01_vec_dst[:]

    ## start the progress bar here
    maxValue = max_iter+1
    cmds.progressWindow(isInterruptable=1, minValue=0, maxValue=maxValue)

    try:
        bound = [(0.0, 1.0)] * len(params01_vec_dst)

        opt = Optimizer(bound, "GP", acq_func="EI",
               acq_func_kwargs={'kappa':1.96} ## exploit based on 95% estimation
               )

        ## run until criterion is matched (or reaches max iteration)
        for num_iter in range(max_iter):
            next_x = opt.ask()
            Cost_this = eval_cost(next_x, num_iter)
            opt.tell(next_x, Cost_this)

            ## change the best result
            if  Cost_this < Cost_best:
                Cost_best = Cost_this
                params_01_vec_best = next_x[:]

                ## show the tentative solution
                path_dst = '{0}/bayesopt/iter_{1:04d}_tmp.{2}'.format(folder_path, num_iter, image_ext)
                img_dst_cv2 = cv2.imread(path_dst)
                img_text = "Cost: {0}\n#iter {1}".format(Cost_this, num_iter)
                Misc.show_text_on_image_cv2(img_dst_cv2, img_text, "target")
        
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
            furRenderer.RenderFur(init_params_dict, folder_root+"/temp", False) ## we don't need this parameter
            
            ############################################################
            ## invert initial parameter dictionary as vector
            ############################################################
            params01_vec_dst = [0.5]*15 ## dummy for consistency

            ############################################################
            ## run optimization on GEOMETRY parameters
            ############################################################
            succeeded, shape_param_dict = BayesOpt(
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
