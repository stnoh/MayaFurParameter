# Parmametric Fur Estimation from an Image

This is experimental module for **MayaFur** parameter optimization.  
I recommend git clone of this module under the following location (default location for script loading in Maya):  
```sh
C:\Users\{your_account}\Document\maya\{maya_version}\scripts
```

## Installation [[link]](https://bitbucket.org/stnoh/Maya-PythonPackages)

It's too long to write down here. Please refer the link above.  

## Preparation (0) activate MayaFur

Because this is deprecated feature, we need to revert them from its disable status.  
1. "Menu bar -> Windows -> Setting/Preferences -> Plug-in Manager", then you got **Plug-in Manager** window.  
2. Scroll down and find "**Fur.mll**". Both **Loaded** and **Auto load** should be checked.  
3. Push **Refresh** button. Now you can use MayaFur.  

Once MayaFur is activated, you can activate MayaFur in the menubar.  
Change to "**Rendering**" mode, and run the following MEL script.  
```sh
FurPluginMayaState(0,1);
```
The equivalent Python script is below:  
```python
import maya.mel as mel
mel.eval("FurPluginMayaState(0,1);")
```

## Preparation (1) Prepare 3D scene & load Python modules

Now it's time to prepare 3D scene and load computation module for MayaFur optimization.  
Open the script editor: "Menu bar -> Windows -> General Editors -> Script Editor" (or Click the ";" icon in the right below).  
These codes are supposed to be run once before running the optimization.  
I recommend you to load them as default ("File -> Open script").

1. load "**init_scene.py**" in this repository and run.  
2. load "**init_feature.py**" in this repository and run.  

## Optimization

This has several stages, so we separate them and summarize as a single .py files.  

- **search_BayesOpt.py**: initial global search based on Bayesian optimization.  
- **search_FeatureGrad.py**: local search based on feature-parameter space gradient descent.  
