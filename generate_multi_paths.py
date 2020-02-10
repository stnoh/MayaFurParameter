###############################################################################
## Continuous fur parameter changing
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import numpy as np

from stNoh import FurParam

###############################################################################
## example of usage
###############################################################################
if "__main__" == __name__:

    ############################################################
    ## user-specified values & paths
    ############################################################

    folder_path = "C:/FurImages/for_video"
    initial_csv = "C:/FurImages/initial.csv"

    ## chaning attribute pairs in animation
    lst_changing = [
        ("Density","Length"),
        ("BaseWidth","TipWidth"),
        ("BaseCurl","TipCurl"),
        ("Inclination","PolarNoise"),
        ("PolarNoise","PolarNoiseFreq"),
        ("Scraggle","ScraggleFrequency"),
        ("Scraggle","ScraggleCorrelation"),
        ("Clumping","ClumpingFrequency"),
        ("Clumping","ClumpShape"),
    ]

    ############################################################
    ## load initial parameters from csv file
    ############################################################
    '''
    params01_vec = [0.5]*15
    def convert_param_geom_func(params01_vec):
        params01_dict = {}
        for cnt, key in enumerate(FurParam.ParamsGeom):
            params01_dict[key] = params01_vec[cnt]

        return params01_dict

    params01_dict = convert_param_geom_func(params01_vec)
    '''

    params_dict = FurParam.csv2dict(initial_csv)
    params01_dict = FurParam.ConvertFurParams(params_dict, False)

    ############################################################
    ## 
    ############################################################
    global count
    count = 0

    def write_csv(kv_id1, kv_id2):
        global count

        params01_dict[kv_id1[0]] = kv_id1[1]
        params01_dict[kv_id2[0]] = kv_id2[1]
        export_path = "{0}/Space{1:04}.csv".format(folder_path, count)
        FurParam.dict2csv( FurParam.ConvertFurParams(params01_dict, True), export_path)

        count = count + 1
        return None

    ############################################################
    ## create multiple paths on parameter space
    ############################################################
    for attrs in lst_changing:
        attr_id1 = attrs[0]
        attr_id2 = attrs[1]

        init_value_id1 = params01_dict[attr_id1]
        init_value_id2 = params01_dict[attr_id2]

        ## path #1: (?,?) --> (0.0,0.0)
        for inc in np.linspace(0.0, 1.0, 11):
            value_id1 = max(init_value_id1 - inc, 0.0)
            value_id2 = max(init_value_id2 - inc, 0.0)
            if value_id1 == 0.0 and value_id2 == 0.0:
                break
            write_csv((attr_id1, value_id1), (attr_id2, value_id2))

        ## path #2: (0.0,0.0) --> (0.5,0.0)
        for inc in np.linspace(0.0, 0.5, 6):
            value_id1 = inc
            write_csv((attr_id1, value_id1), (attr_id2, 0.0))

        ## path #3: (0.5,0.0) --> (0.5,1.0)
        for inc in np.linspace(0.1, 1.0, 10):
            value_id2 = inc
            write_csv((attr_id1, 0.5), (attr_id2, value_id2))

        ## path #4: (0.5,1.0) --> (1.0,1.0)
        for inc in np.linspace(0.1, 0.5, 5):
            value_id1 = 0.5 + inc
            write_csv((attr_id1, value_id1), (attr_id2, 1.0))

        ## path #5: (1.0,1.0) --> (0.5,0.5)
        for inc in np.linspace(0.1, 0.5, 5):
            value_id1 = 1.0 - inc
            value_id2 = 1.0 - inc
            write_csv((attr_id1, value_id1), (attr_id2, value_id2))

        ## path #6: (0.5,0.5) --> (0.0,1.0)
        for inc in np.linspace(0.1, 0.5, 5):
            value_id1 = 0.5 - inc
            value_id2 = 0.5 + inc
            write_csv((attr_id1, value_id1), (attr_id2, value_id2))

        ## path #7: (0.0,1.0) --> (0.0,0.5)
        for inc in np.linspace(0.1, 0.5, 5):
            value_id2 = 1.0 - inc
            write_csv((attr_id1, 0.0), (attr_id2, value_id2))

        ## path #8: (0.0,0.5) --> (1.0,0.5)
        for inc in np.linspace(0.1, 1.0, 10):
            value_id1 = inc
            write_csv((attr_id1, value_id1), (attr_id2, 0.5))

        ## path #9: (1.0,0.5) --> (1.0,0.0)
        for inc in np.linspace(0.1, 0.5, 5):
            value_id2 = 0.5 - inc
            write_csv((attr_id1, 1.0), (attr_id2, value_id2))

        ## path #10: (1.0,0.0) --> (0.5,0.5)
        for inc in np.linspace(0.1, 0.5, 5):
            value_id1 = 1.0 - inc
            value_id2 = inc
            write_csv((attr_id1, value_id1), (attr_id2, value_id2))

        ## revert parameter values
        params01_dict[attr_id1] = init_value_id1
        params01_dict[attr_id2] = init_value_id2
