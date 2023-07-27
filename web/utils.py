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
from .models import Constraint, UserData
import traceback

MONTHS = [
    "Jan","Feb","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"
]

TSTEPS = [
    "Monthly", "Yearly"
]



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


def neighbourHoodForrDisp(neighbourHoodFileData, listIdRgExpose, listIdRgInfect):
    try:
        lR = listIdRgExpose.shape[0]
        voisinage = np.array([])
        for count in range(lR):
            if stopstat == 1:
                break
            IdNeigbour = neighbourHoodFileData[listIdRgExpose[count],:]
            voisinage = np.union1d(voisinage, IdNeigbour[IdNeigbour!=-1])
        Idx =  np.setdiff1d(voisinage, listIdRgInfect)
        return Idx 
    except Exception as err:
        showerror(title=("Fatal error"), message=(err))



# def showProgress(progMode, progMess):
#     global bar
#     global progressStrg
#     global progressLabel
    
#     if progMode=="indeterminate":
#         bar = ttk.Progressbar(apWindow, length=400, mode="indeterminate")
#         bar.place(x=200, y=10)
#         bar.start(10)
#     else:
#         global percentStrg
#         global percentLabel
#         global barrvalu
        
#         barrvalu = tk.StringVar()
#         percentStrg = tk.StringVar()
        
#         percentStrg.set("0%")
#         bar = ttk.Progressbar(apWindow, length=400, mode="determinate",variable = barrvalu)
#         bar.place(x=200, y=10)
#         barrvalu.set("0")
#         percentLabel = ttk.Label(apWindow, textvariable=percentStrg, background=bgColr, width=8)
#         percentLabel.place(x = 140, y =10)
        
#     progressStrg = tk.StringVar()
#     progressStrg.set(progMess)
    
#     progressLabel = ttk.Label(apWindow, textvariable=progressStrg, background=bgColr, width=40)
#     progressLabel.place(x = 640, y =10)




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
                npNe = pd.read_csv(gridDestination, encoding="latin-1", on_bad_lines='skip').to_numpy()
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




def run_model(constraints:list[Constraint], duration=10, start_month='Jan', start_year=2020, time_step=TSTEPS[0]):
    def stoprunn():
        # currentSimlStepStrg.set("----")
        # totlSimStepStrg.set("----")
        # global containergrph
        # containergrph.destroy()
        # theeLabl.destroy()
        # containergrph = tk.LabelFrame(container3,bg="#F5F5F5", bd=0, width=500, height=400)
        
        
        
        fig = Figure(figsize=(4.9,4), dpi=300)
        a = fig.add_subplot(111)
        a.set_title("Dispersal")
        a.set_xlabel("Longitude")
        a.set_ylabel("Latitude")
        
        
        
        #a.plot([1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10])
        
        # plotPart = FigureCanvasTkAgg(fig, master = containergrph)
        
        # plotPart.draw()
        # containergrph.place(x = pox3, y =poy3 + dif3)
        # plotPart.get_tk_widget().place(x = 0, y =0)
    
    def runnStat():
        try:
            stoprunn()
            global stopstat
            stopstat = 0
            global theeLabl
            # theeLabl = tk.Label(container3, width=400, height=400)
            timeStepSimuCode = duration
            mnth = MONTHS.index(start_month)
            year = start_year
            # currentSimlStepStrg.set("----")
            # totlSimStepStrg.set(timeStepSimuCode)
            # currentTimeYearStrg.set(year)
            # currentTimeMonStrg.set(months[mnth])
            #--------------------------------------data-----------------------------------------------
            # const1Ul = float(const1UpLimtStrg.get())
            # const1Lo = float(const1LoLimtStrg.get())
            # const2Ul = float(const2UpLimtStrg.get())
            # const2Lo = float(const2LoLimtStrg.get())
            # const3Ul = float(const3UpLimtStrg.get())
            # const3Lo = float(const3LoLimtStrg.get())
            # const4Ul = float(const4UpLimtStrg.get())
            # const4Lo = float(const4LoLimtStrg.get())
            
            
            #--------------------------------import start---------------------------------------------
            geoPandaDataFrame = gpd.read_file(os.path.join(settings.BASE_DIR, "static/data/shapefiles/map.shp")).set_crs(epsg=4326)
            points = gpd.GeoSeries([Point(-73.5, 40.5), Point(-74.5, 40.5)], crs=4326)
            points = points.to_crs(32619)
            distance_meters = points[0].distance(points[1])
            
            codeUseGridData = pd.read_csv(os.path.join(settings.BASE_DIR, "static/data/grid.csv"), encoding='latin-1', on_bad_lines='skip').to_numpy()

            constraintDatas = []
            constraintFiles = []

            for item in constraints:
                constraintData = np.zeros(codeUseGridData.shape[0])
                constraintFile = item.file.path
                print(constraintFile)
                if os.path.isfile(constraintFile):
                    constraintData = pd.read_csv(constraintFile,encoding='latin-1', on_bad_lines='skip', header = None).to_numpy()[:,0]
                else:
                    const1Ul = 1
                    const1Lo = -1
                constraintDatas.append(constraintData)
                constraintFiles.append(constraintFile)
            
            neighbourData = pd.read_csv(os.path.join(settings.BASE_DIR, "static/data/neigbourhood.csv"), encoding='latin-1', on_bad_lines='skip', header = None).to_numpy().astype(int)
            
            initialId = pd.read_csv(os.path.join(settings.BASE_DIR, "static/data/Starting.csv"),encoding='latin-1', on_bad_lines='skip', header = None).to_numpy().astype(int)[:,0]
            #--------------------------------import end-----------------------------------------

            initialData = np.concatenate((codeUseGridData[initialId,:], np.ones(initialId.shape[0]).reshape(initialId.shape[0],1)*-1), axis=1)
            idOfSiteInfected = initialId
            idOfSiteExposed = idOfSiteInfected
            
            statut = np.zeros(codeUseGridData.shape[0])
            
            statut[idOfSiteInfected] = 2
            #--------------------------------------data-----------------------------------------------
                
            # apWindow.update_idletasks()
                
            for timeStep in range(timeStepSimuCode):
                if stopstat == 1:
                    stoprunn()
                    # showinfo(title=("Stop"), message=("Run stopped"))
                    break
                #--------------------------------------date-----------------------------------------------
                if time_step == "Monthly":
                    mnth += 1
                    if mnth>=12:
                        mnth = 0
                        year += 1
                        # currentTimeYearStrg.set(year)
                    # currentTimeMonStrg.set(months[mnth])
                else:
                    year += 1
                    # currentTimeYearStrg.set(year)
                #--------------------------------------date-----------------------------------------------
                
                infectData = idOfSiteInfected
                exposeData = idOfSiteExposed
                
                IdVoisin = neighbourHoodForrDisp(neighbourData, np.union1d(exposeData,infectData), infectData)
                
                for p in range(IdVoisin.shape[0]):
                    if stopstat == 1:
                        break
                    idMax = int(IdVoisin[p])
                    statut[idMax] = 1
                    if statut[idMax]!=2 :
                        # and (Constraint1Data[idMax]>const1Lo and Constraint1Data[idMax]<=const1Ul) and (Constraint2Data[idMax]>const2Lo and Constraint2Data[idMax]<=const2Ul) and (Constraint3Data[idMax]>const3Lo and Constraint3Data[idMax]<=const3Ul) and (Constraint4Data[idMax]>const4Lo and Constraint4Data[idMax]<=const4Ul)):
                        statut[idMax]=2
                    
                if stopstat == 1:
                    stoprunn()
                    # showinfo(title=("Stop"), message=("Run stopped"))
                    break
                
                idOfSiteExposed = np.where(statut==1)[0]
                idOfSiteInfected = np.where(statut==2)[0]
                #--------------------------------------plot-----------------------------------------------
            
                csvvfileFolder = os.path.join(settings.BASE_DIR, "static/data/outputs/csv")
                
                if not os.path.isdir(csvvfileFolder):
                    os.makedirs(csvvfileFolder)
                
                tifffileFolder = os.path.join(settings.BASE_DIR, "static/data/outputs/tif")
                
                if not os.path.isdir(tifffileFolder):
                    os.makedirs(tifffileFolder)
                
                csvvDestination = os.path.join(settings.BASE_DIR, "static/data/outputs/csv/Dispersal"+ str(timeStep+1) + ".csv")
                tiffDestination = os.path.join(settings.BASE_DIR, "static/data/outputs/png/Spread" + str(timeStep+1) + ".png")
                
                if os.path.isfile(csvvDestination):
                    os.remove(csvvDestination)

                if os.path.isfile(tiffDestination):
                    os.remove(tiffDestination)
                
                data = pd.DataFrame(np.concatenate((codeUseGridData, statut.reshape(statut.shape[0],1)), axis=1))
                data.columns = ["latitide", "longitude", "data"]
                    
                if stopstat == 1:
                    stoprunn()
                    # showinfo(title=("Stop"), message=("Run stopped"))
                    break
        
                pd.DataFrame(data).to_csv(csvvDestination, index=None)
    
                df = pd.read_csv(csvvDestination, encoding='latin-1', on_bad_lines='skip')
    
                df = pd.DataFrame(np.concatenate((df.to_numpy(), initialData), axis=0))
                df.columns = ["latitide", "longitude", "data"]
                def plotData(row):
                    if row["data"] == -1:
                        return "Initial"
                    if row["data"] == 2:
                        return "Infected"
                    if row["data"] == 1:
                        return "Exposed"
                    if row["data"] == 0:
                        return "Unexposed"
                
                df["plotdata"] = df.apply(lambda row:plotData(row), axis=1)
    
                geometry = [Point(xy) for xy in zip(df.iloc[:, 1], df.iloc[:, 0])]
                
                gdf = gpd.GeoDataFrame(df, geometry=geometry)
                
                fig, ax = plt.subplots(1,1,figsize=(4.8,4), dpi=300)
                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")
                # ax.set_title("Dispersal "+currentTimeMonStrg.get()+" "+currentTimeYearStrg.get())
                ax.set_title("Dispersal: t = "+ str(timeStep))
                
                colrData = {"Unexposed":"blue",
                            "Exposed":"yellow",
                            "Infected":"#7B0059",
                            "Initial":"red"}
                
                
                for ctype, dataH in gdf.groupby("plotdata"):
                    color = colrData[ctype]
                    if color != "blue":
                        dataH.plot(color=color, ax=ax, label=ctype)
    
                x, y, arrow_length = 0.94, 1.0, 0.1
                ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
                            arrowprops=dict(facecolor='black', width=2, headwidth=10),
                            ha='center', va='center', fontsize=10,
                            xycoords=ax.transAxes)
                
                ax.legend(loc="lower left", prop={"size":6})
                dataH.plot(color=color, ax=ax, label=ctype)
                
    #            gdf.plot(ax=ax, column="plotdata",legend=True, categorical=True, cmap="jet")
                            
                            
                            
                geoPandaDataFrame.plot(ax=ax, color="None", edgecolor="black")
                ax.add_artist(ScaleBar(dx = distance_meters, location="lower center", box_alpha=0.4, ))
    
                plt.savefig(tiffDestination)
                
                
                
                
                # ax = None
                # global theeImag
                # theeImag = ImageTk.PhotoImage(Image.open(tiffDestination))
                # global containergrph
                # containergrph.destroy()
                # containergrph = tk.LabelFrame(container3,bg="#F5F5F5", bd=0, width=500, height=400)
                # containergrph.place(x = pox3, y =poy3 + dif3)
                # theeLabl.destroy()
                # currentSimlStepStrg.set(timeStep + 1)
                # theeLabl = tk.Label(containergrph,bg="#F5F5F5", image=theeImag, width=500, height=400)
                # theeLabl.place(x = 0, y =0)
                
                # apWindow.update_idletasks()
                    
                    
                if stopstat == 1:
                    stoprunn()
                    # showinfo(title=("Stop"), message=("Run stopped"))
                    break
                #--------------------------------------plot-----------------------------------------------
            if stopstat != 1:
                return
                # showinfo(title=("Success"), message=("Run complete"))
#            gdal.Grid(tiffDestination, csvvDestination, zfield="data", algorithm = "nearest:radius1=0.3:radius2=0.3:nodata=-9999")   
#            enddProgress("indeterminate")   
        except Exception as err:
            # showerror(title=("Fatal error"), message=(err))
            traceback.print_exc()
    threading.Thread(target=runnStat).start()



