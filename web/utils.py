import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror
from tkinter.messagebox import showinfo
import threading
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib
from matplotlib import pyplot as plt
from shapely.geometry import Point
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import geopandas as gpd
import rasterio as rio
import numpy as np
import pandas as pd
import shutil
import os
import shapefile as shp
import math
from django.conf import settings

plt.ioff()


def distance(originInDs, npdfInDs):
    try:
        lat1, lon1 = originInDs
        lat2 = npdfInDs[:,0]
        lon2 = npdfInDs[:,1]
        radius = 6371  # km
        dlat = np.radians(lat2-lat1)
        dlon = np.radians(lon2-lon1)
        a = np.square(np.sin(dlat/2)) + np.cos(np.radians(lat1)) \
            * np.cos(np.radians(lat2)) * np.square(np.sin(dlon/2))
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        d = radius * c
        return d
    except Exception as err:
        print(err)




def showProgress(progMode, progMess):
    global bar
    global progressStrg
    global progressLabel
    
    if progMode=="indeterminate":
        bar = ttk.Progressbar(apWindow, length=400, mode="indeterminate")
        bar.place(x=200, y=10)
        bar.start(10)
    else:
        global percentStrg
        global percentLabel
        global barrvalu
        
        barrvalu = tk.StringVar()
        percentStrg = tk.StringVar()
        
        percentStrg.set("0%")
        bar = ttk.Progressbar(apWindow, length=400, mode="determinate",variable = barrvalu)
        bar.place(x=200, y=10)
        barrvalu.set("0")
        percentLabel = ttk.Label(apWindow, textvariable=percentStrg, background=bgColr, width=8)
        percentLabel.place(x = 140, y =10)
        
    progressStrg = tk.StringVar()
    progressStrg.set(progMess)
    
    progressLabel = ttk.Label(apWindow, textvariable=progressStrg, background=bgColr, width=40)
    progressLabel.place(x = 640, y =10)




# def enddProgress(progMode):
    
#     if progMode=="indeterminate":
#         bar.stop()
#         bar.destroy()
#         progressLabel.destroy()
#     else:
#         bar.destroy()
#         progressLabel.destroy()
#         percentLabel.destroy()


# functions
def produce_grid(cellsize=4):
    def real_start():
        # try:
        #----------------------------------stat progress------------------------------------------------
        # showProgress("indeterminate", "Producing grid")
        #--------------------------------import start---------------------------------------
        shapefileLocation = os.path.join(settings.BASE_DIR, "static/data/shapefiles/map.shp")
        sf = shp.Reader(shapefileLocation)
        minx,miny,maxx,maxy = sf.bbox
        sf = None
        # cellsize = int(cellSizegridStrg.get())
        if cellsize<=0:
            raise Exception("Cell size cannot be zero or less than zero")
        cellsizeInDegrees = cellsize*0.00833
        dx = cellsizeInDegrees
        dy = cellsizeInDegrees
        nx = int(math.ceil(abs(maxx - minx)/dx))
        ny = int(math.ceil(abs(maxy - miny)/dy))
        gridshapefileLocation = os.path.join(settings.BASE_DIR, "static/data/gridFiles/grid")
        w = shp.Writer(gridshapefileLocation)
        w.autoBalance = 1
        w.field("ID")
        id=0
        for i in range(ny):
            for j in range(nx):
                id+=1
                vertices = []
                parts = []
                vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)])
                vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)])
                vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)])
                vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)])
                parts.append(vertices)
                w.poly(parts)
                w.record(id)
        w.close()
        gridshapefileLocation = r"{}".format(gridshapefileLocation+".shp")
        gridarea = gpd.read_file(gridshapefileLocation)
        shaparea = gpd.read_file(shapefileLocation)
        points_clip = gpd.clip(gridarea, shaparea).centroid
        gridarea = None
        shaparea = None
        points_clipFrme = pd.DataFrame()
        points_clipFrme["latitude"]=points_clip.y
        points_clipFrme["longitude"]=points_clip.x
        points_clip = None
        gridfileFolder = os.path.join(settings.BASE_DIR, "static/data")
        if not os.path.isdir(gridfileFolder):
            os.makedirs(gridfileFolder)
        gridDestination = os.path.join(settings.BASE_DIR, "static/data/grid.csv")
        if os.path.isfile(gridDestination):
            os.remove(gridDestination)
        points_clipFrme[["latitude", "longitude"]].to_csv(gridDestination, index=False)
        points_clipFrme = None  
        # enddProgress("indeterminate")
        #----------------------------------endd progress------------------------------------------------ 
        # except Exception as err:  
        # enddProgress("indeterminate")
        # showerror(title=("Fatal error"), message=(err))
        #--------------------------------thread start-------------------------------------------
    threading.Thread(target=real_start).start()



def produce_neighbourhood(spedStrg=4):
    def real_negh():
        try:
            #----------------------------------stat progress------------------------------------------------
            # showProgress("determinate", "Producing neigbourhood")
            travelDist = spedStrg
            gridDestination = os.path.join(settings.BASE_DIR, "static/data/grid.csv")
            if os.path.isfile(gridDestination):
                npNe = pd.read_csv(gridDestination).to_numpy()
            else:
                raise Exception("Produce grid file first") 
            neigbourFile1 = (np.ones(npNe.shape[0])*-1).reshape(npNe.shape[0], 1)
            neigbourFile = neigbourFile1
            prevcol = 1
            totalRuns = npNe.shape[0]
            for row in range(totalRuns):
                origin = npNe[row]	
                rangeDistance = distance(origin, npNe)
                neighbourId = np.where(rangeDistance<travelDist)[0]
                neighbourId = neighbourId[neighbourId!=row]
                maxcol = neighbourId.shape[0]
                if maxcol>prevcol:
                    neigbourFile1 = (np.ones(npNe.shape[0]*maxcol)*-1).reshape(npNe.shape[0], maxcol)
                    neigbourFile1[:,0:prevcol]=neigbourFile
                    prevcol = maxcol
                neigbourFile1[row,0:maxcol]=neighbourId
                neigbourFile = neigbourFile1
                settValu = str(int((row/(totalRuns)*100)))
                # percentStrg.set(settValu + "%")
                # barrvalu.set(settValu) 
                # apWindow.update_idletasks()
            npNe = None
            neghDestination = os.path.join(settings.BASE_DIR, "static/data/neigbourhood.csv")
            if os.path.isfile(neghDestination):
                os.remove(neghDestination)
            pd.DataFrame(neigbourFile).to_csv(neghDestination, header=None, index=None)
            neigbourFile = None
            # checkImportShapeFiles()
            # apWindow.update_idletasks()          
            # enddProgress("determinate")
            #----------------------------------endd progress------------------------------------------------
        except Exception as err: 
            print(err)           
        #     enddProgress("determinate")
        #     showerror(title=("Fatal error"), message=(err))
    #--------------------------------thread start-------------------------------------------
    threading.Thread(target=real_negh).start()




def run_model():
    pass


