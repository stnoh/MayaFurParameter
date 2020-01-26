import maya.cmds as cmds
import maya.mel as mel

## activate MayaFur when loaded
mel.eval("FurPluginMayaState(0,1);")


###############################################################################
## list of preset
###############################################################################
Preset18 = [
    ## All 18 fur presets in Maya.
    "Bear", "Bison", "CalicoCat", "Dreadlocks", "Duckling", "Gorilla",
    "Grass", "LionMane", "Llama", "Mouse", "PolarBear", "Porcupine",
    "Punk", "Raccoon", "Sheep", "Squirrel", "WetLabrador", "WetOtter"
]
Preset15 = [
    ## 'Regular' 15 fur presets, except {"Porcupine", "Punk", "WetLabrador"}
    "Bear", "Bison", "CalicoCat", "Dreadlocks", "Duckling", "Gorilla",
    "Grass", "LionMane", "Llama", "Mouse", "PolarBear", 
    "Raccoon", "Sheep", "Squirrel", "WetOtter"
]


###############################################################################
## list of attribute name for fur description
###############################################################################
Params89 = [
    ## rendering parameter - color
    "BaseColorR", "BaseColorG", "BaseColorB", "BaseColorNoise", "BaseColorNoiseFreq",
    "TipColorR", "TipColorG", "TipColorB", "TipColorNoise", "TipColorNoiseFreq",
    "BaseAmbientColorR", "BaseAmbientColorG", "BaseAmbientColorB", "BaseAmbientColorNoise", "BaseAmbientColorNoiseFreq",
    "TipAmbientColorR", "TipAmbientColorG", "TipAmbientColorB", "TipAmbientColorNoise", "TipAmbientColorNoiseFreq",
    "SpecularColorR", "SpecularColorG", "SpecularColorB", "SpecularColorNoise", "SpecularColorNoiseFreq",

    ## rendering parameter - etc.
    "SpecularSharpness", "SpecularSharpnessNoise", "SpecularSharpnessNoiseFreq",
    "BaseOpacity", "BaseOpacityNoise", "BaseOpacityNoiseFreq",
    "TipOpacity", "TipOpacityNoise", "TipOpacityNoiseFreq",

    ## shape parameter - fur field
    "Density",

    ## shape parameter - single strand
    "Length", "LengthNoise", "LengthNoiseFreq",
    "BaseWidth", "BaseWidthNoise", "BaseWidthNoiseFreq",
    "TipWidth", "TipWidthNoise", "TipWidthNoiseFreq",
    "BaseCurl", "BaseCurlNoise", "BaseCurlNoiseFreq",
    "TipCurl", "TipCurlNoise", "TipCurlNoiseFreq",

    "Inclination", "InclinationNoise", "InclinationNoiseFreq",
    "Roll", "RollNoise", "RollNoiseFreq",
    "Polar", "PolarNoise", "PolarNoiseFreq",

    ## shape parameter - wisp (strand-to-strand)
    "Scraggle", "ScraggleNoise", "ScraggleNoiseFreq",
    "ScraggleFrequency", "ScraggleFrequencyNoise", "ScraggleFrequencyNoiseFreq",
    "ScraggleCorrelation", "ScraggleCorrelationNoise", "ScraggleCorrelationNoiseFreq",

    "Clumping", "ClumpingNoise", "ClumpingNoiseFreq",
    "ClumpingFrequency", "ClumpingFrequencyNoise", "ClumpingFrequencyNoiseFreq",
    "ClumpShape", "ClumpShapeNoise", "ClumpShapeNoiseFreq",

    ## unused parameter [not interested yet]
    "Baldness", "BaldnessNoise", "BaldnessNoiseFreq",
    "Segments", "SegmentsNoise", "SegmentsNoiseFreq",
    "Attraction", "AttractionNoise", "AttractionNoiseFreq",
    "Offset", "OffsetNoise", "OffsetNoiseFreq"
]


###############################################################################
## setter for fur attribute (color or value)
###############################################################################
def SetFurAttribute_color(desc, attr_color, color):
    """
    Sets fur color attribute value.
    desc : name of fur description (string)
    attr : name of fur attribute (string)
    color: RGB (3-tuple, from 0.0 to 1.0)
           RGB + noise amplitude and frequency (5-tuple)
    """

    ## set RGB values
    cmds.setAttr("{0}.{1}R".format(desc, attr_color), color[0])
    cmds.setAttr("{0}.{1}G".format(desc, attr_color), color[1])
    cmds.setAttr("{0}.{1}B".format(desc, attr_color), color[2])

    ## set spatial variance (amplitude and frequency)
    if (len(color) >= 5):
        cmds.setAttr("{0}.{1}Noise".format(desc, attr_color), color[3])
        cmds.setAttr("{0}.{1}NoiseFreq".format(desc, attr_color), color[4])
    ## no spatial variance (= assign default value)
    else:
        cmds.setAttr("{0}.{1}Noise".format(desc, attr_color), 0.0)
        cmds.setAttr("{0}.{1}NoiseFreq".format(desc, attr_color), 10.0)

    return None

def SetFurAttribute_values(desc, attr, value):
    """
    Sets fur attribute (except of color) value with spatial variance.
    desc : name of fur description (string)
    attr : name of fur attribute (string)
    value: main value and noise amplitude and frequency (3-tuple)
    """

    cmds.setAttr("{0}.{1}".format(desc, attr), value[0])
    cmds.setAttr("{0}.{1}Noise".format(desc, attr), value[1])
    cmds.setAttr("{0}.{1}NoiseFreq".format(desc, attr), value[2])
    return None

def SetFurAttribute_value(desc, attr, value):
    """
    Sets single fur attribute value *without* spatial variance values.
    attr : name of fur attribute (string)
    value: single value
    """

    cmds.setAttr("{0}.{1}".format(desc, attr), value)
    return None


###############################################################################
## Initialize fur description for experiment
###############################################################################
def InitFurDescription(desc):
    """
    Initialize fur description as default status.
    desc : name of fur description (string)
    """

    ## 1-i) rendering parameter - color
    white = (1.0, 1.0, 1.0)
    gray  = (0.5, 0.5, 0.5)
    black = (0.0, 0.0, 0.0)
    SetFurAttribute_color(desc, "BaseColor"       , white)
    SetFurAttribute_color(desc, "TipColor"        , white)
    SetFurAttribute_color(desc, "BaseAmbientColor", black)
    SetFurAttribute_color(desc, "TipAmbientColor" , black)
    SetFurAttribute_color(desc, "SpecularColor"   , gray )

    ## 1-ii) rendering parameter - etc.
    SetFurAttribute_values(desc, "SpecularSharpness", ( 50, 0.0, 10.0)) # default=50
    SetFurAttribute_values(desc, "BaseOpacity"      , (1.0, 0.0, 10.0)) # default=1.0
    SetFurAttribute_values(desc, "TipOpacity"       , (1.0, 0.0, 10.0)) # default=1.0

    ## 2) shape parameter - fur field
    SetFurAttribute_value(desc, "Density", 1000) # default = 1000

    ## 3) shape parameter - single strand
    SetFurAttribute_values(desc, "Length"   , (1.00, 0.0, 10.0)) # default=1.00
    SetFurAttribute_values(desc, "BaseWidth", (0.05, 0.0, 10.0)) # default=0.05
    SetFurAttribute_values(desc, "TipWidth" , (0.03, 0.0, 10.0)) # default=0.03
    SetFurAttribute_values(desc, "BaseCurl" , (0.50, 0.0, 10.0)) # default=0.5
    SetFurAttribute_values(desc, "TipCurl"  , (0.50, 0.0, 10.0)) # default=0.5

    SetFurAttribute_values(desc, "Inclination", (0.0, 0.0, 10.0)) # default=0.0
    SetFurAttribute_values(desc, "Roll"       , (0.5, 0.0, 10.0)) # default=0.5
    SetFurAttribute_values(desc, "Polar"      , (0.5, 0.0, 10.0)) # default=0.5

    ## 4) shape parameter - wisp (strand-to-strand)
    SetFurAttribute_values(desc, "Scraggle"           , (0.00, 0.0, 10.0)) # default=0.0
    SetFurAttribute_values(desc, "ScraggleFrequency"  , (5.00, 0.0, 10.0)) # default=5.0
    SetFurAttribute_values(desc, "ScraggleCorrelation", (0.00, 0.0, 10.0)) # default=0.0

    SetFurAttribute_values(desc, "Clumping"           , (0.00, 0.0, 10.0)) # default=0.0
    SetFurAttribute_values(desc, "ClumpingFrequency"  , (5.00, 0.0, 10.0)) # default=5.0
    SetFurAttribute_values(desc, "ClumpShape"         , (0.00, 0.0, 10.0)) # default=0.0

    ## 5) unused parameter [not interested yet]
    SetFurAttribute_values(desc, "Baldness"  , (1.0,0.0,10.0)) # default=1.0
    SetFurAttribute_values(desc, "Segments"  , ( 20,0.0,10.0)) # default=10 (!)
    SetFurAttribute_values(desc, "Attraction", (1.0,0.0,10.0)) # default=1.0
    SetFurAttribute_values(desc, "Offset"    , (0.0,0.0,10.0)) # default=0.0

    return None


###############################################################################
## setters/getters for multiple fur attributes
###############################################################################
def SetFurDescription(fur_desc, params_dict):
    """
    Sets fur attribute values 
    fur_desc   : name of fur description (string)
    params_dict: fur parameter values (dictionary)
    """

    for key in params_dict:
        SetFurAttribute_value(fur_desc, key, params_dict[key])

    return None

def GetFurAttributeDict(fur_desc, attributes):
    """
    fur_desc  : name of fur description (string)
    attributes: list of fur attributes (list of string)
    """

    params_dict = {}

    for key in attributes:
        value = cmds.getAttr("{0}.{1}".format(fur_desc, key) )
        params_dict[key] = value

    return params_dict

def GetFurAttributeDict_all(fur_desc):
    """
    Returns dictionary of 89 parameter values of the fur description.
    fur_desc : name of fur description (string)
    """

    ## filtering out non-used keywords in our experiment
    _keyword_filter_out = [
        ## filter-out attributes in fur description
        "caching", "frozen", "isHistoricallyInteresting", "nodeState",
        "LightModel", "GlobalScale", "export", "Map", # [TODO] may be next time?
        "Custom", "feedback"
    ]

    ## filtering raw 232 attributes to 89 parameters-of-interest
    attributes_raw = cmds.listAttr(fur_desc, r=True, s=True)
    attributes_all = [attr for attr in attributes_raw 
                        if False==any(xs in attr for xs in _keyword_filter_out) ]

    return GetFurAttributeDict(fur_desc, attributes_all)

def GetFurAttributeDict_color(fur_desc):
    """
    Returns dictionary of 10-dimension color parameters of the fur description.
    fur_desc : name of fur description (string)
    """

    colors_dict = {}

    ## 9-dimension = (Base,Tip,Specular) x (R,G,B)
    for attribute in ["BaseColor", "TipColor", "SpecularColor"]:
        for channel in ["R", "G", "B"]:
            key   = "{0}{1}".format(attribute, channel)
            value = cmds.getAttr("{0}.{1}".format(fur_desc, key))
            colors_dict[key] = value

    ## exception: SpecularSharpness
    colors_dict["SpecularSharpness"] = cmds.getAttr("{0}.{1}".format("SpecularSharpness", key))

    return colors_dict


###############################################################################
## utility, etc.
###############################################################################
def CopyFurBaseColor2Material(fur_desc, material):
    """
    Copies the base color of fur description to material.
    fur_desc : name of fur description (string)
    material : name of material (string)
    """

    colorR = cmds.getAttr("{0}.BaseColorR".format(fur_desc))
    colorG = cmds.getAttr("{0}.BaseColorG".format(fur_desc))
    colorB = cmds.getAttr("{0}.BaseColorB".format(fur_desc))

    cmds.setAttr("{0}.colorR".format(material), colorR)
    cmds.setAttr("{0}.colorG".format(material), colorG)
    cmds.setAttr("{0}.colorB".format(material), colorB)
    
    return None
