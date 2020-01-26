from collections import OrderedDict
import csv

###############################################################################
## default values for MayaFur parameters
###############################################################################

## major 15 parameters for geometry variation
ParamsGeom = OrderedDict([
    ("Density",15000.0),

    ("Length",1.0),
    ("BaseWidth",0.08),
    ("TipWidth",0.0),

    ("Inclination",0.0),
    ("PolarNoise",0.0),
    ("PolarNoiseFreq",5.0),
    
    ("BaseCurl",0.5),
    ("TipCurl",0.5), 

    ("Scraggle",0.0),
    ("ScraggleFrequency",5.0),
    ("ScraggleCorrelation",0.0),

    ("Clumping",0.0),
    ("ClumpingFrequency",5.0),
    ("ClumpShape",0.0),
])

## major 10 parameters for color variation
ParamsColor = OrderedDict([
    ("TipColorR",0.404),
    ("TipColorG",0.275),
    ("TipColorB",0.169),

    ("BaseColorR",0.091),
    ("BaseColorG",0.057),
    ("BaseColorB",0.030),

    ("SpecularColorR",0.240),
    ("SpecularColorG",0.246),
    ("SpecularColorB",0.280),

    ("SpecularSharpness",50.0),
])

## value ranges for MayaFur parameters
def _getParameterRange(key):
    """
    Returns fur's default parameter range as 2-tuple (min, max).
    key: fur attribute (string)
    """
    if "Density"  ==key: return (10000.0, 30000.0)

    ## geometry attributes (1) for single strand
    if "Length"   ==key: return (1.00, 5.00)
    if "BaseWidth"==key: return (0.01, 0.10)
    if "TipWidth" ==key: return (0.00, 0.10)

    ## geometry attributes (2) for strand root distribution
    if "Inclination"   ==key: return (0.0,  0.9) # 1.0 makes extrusion
    if "PolarNoise"    ==key: return (0.0,  0.5)
    if "PolarNoiseFreq"==key: return (1.0, 20.0)

    if "BaseCurl"==key: return (0.5, 1.0) # [0.0:0.5] usually makes extrusion
    if "TipCurl" ==key: return (0.0, 1.0)

    ## geometry attributes (4) for noise in fields
    if "Scraggle"           ==key: return (0.0,  0.5)
    if "ScraggleCorrelation"==key: return (0.0,  0.5)
    if "ScraggleFrequency"  ==key: return (1.0, 10.0)

    ## geometry attributes (3) for clumping
    if "Clumping"         ==key: return ( 0.0,  0.5)
    if "ClumpingFrequency"==key: return ( 1.0, 50.0)
    if "ClumpShape"       ==key: return (+1.0, +5.0)

    ## color attributes: special
    if "SpecularSharpness"  ==key: return (0.0, 100.0)

    # otherwise, all values should be [0.0:1.0]
    return (0.0, 1.0)


###############################################################################
## normalized fur parameter <-> fur parameter in renderer
###############################################################################
def ConvertFurParam(key, value, inverse=False):
    """
    Converts a single fur parameter to normalized space [0.0:1.0], vice versa
    key     : 
    value   : 
    inverse : it controls the conversion direction
              False: [min:max] -> [0.0:1.0] (parameter normalization)
              True : [0.0:1.0] -> [min:max] (default parameter)
    """
    Convert01 = lambda val,min,max,inverse:(max-min)*val + min if inverse else (val-min) / (max-min)
    
    _min, _max = _getParameterRange(key)
    value_converted = Convert01(value, _min, _max, inverse)
    return value_converted

def ConvertFurParams(params_dict, inverse=False):
    """
    Converts fur parameters to normalized space [0.0:1.0], vice versa
    params_dict : fur parameters
    inverse     : when it is True, it revert the parameter from normalization.
    """
    params_dict_new = {}

    for key in params_dict:
        params_dict_new[key] = ConvertFurParam(key, params_dict[key], inverse)

    return params_dict_new


###############################################################################
## dictionary <-> csv file
###############################################################################
def dict2csv(params_dict, csv_path):
    """
    Exports fur parameter dictionary to CSV file.
    params_dict: fur parameters
    csv_path   : filepath to export csv (string)
    """

    with open(csv_path, 'w') as csv_file:
        fieldnames = ['first_name', 'last_name']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator='\n')

        # shape parameters
        for key in ParamsGeom:
            if params_dict.get(key) is not None:
                value = params_dict[key]
                writer.writerow( { 'first_name':key,'last_name':value } )

        # color parameters
        for key in ParamsColor:
            if params_dict.get(key) is not None:
                value = params_dict[key]
                writer.writerow( { 'first_name':key,'last_name':value } )

    return None

def csv2dict(csv_path):
    """
    Loads fur parameters from CSV and returns them as dictionary.
    csv_file: csv file which contains the fur parameters (string)
    """

    params_dict = {}

    with open(csv_path, 'r') as csv_file:
        fieldnames = csv.reader(csv_file, delimiter=',')

        for kv in fieldnames:
            key   = kv[0]
            value = float(kv[1])
            params_dict[key] = value

    return params_dict
