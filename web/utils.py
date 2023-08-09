import tkinter as tk
from PIL import ImageTk, Image
# from tkinter import ttk, filedialog
# from tkinter.messagebox import showerror
# from tkinter.messagebox import showinfo
import threading
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib
from matplotlib import pyplot as plt
from shapely.geometry import Point
# matplotlib.use("TkAgg")
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import geopandas as gpd
import rasterio as rio
import numpy as np
import pandas as pd
# from osgeo import gdal
import shutil
import os
import shapefile as shp
import math
from django.conf import settings
from .models import Constraint, Request, Workspace
import traceback
from pathlib import Path

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
        # print(err)
        traceback.print_exc()


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
        traceback.print_exc()
        # showerror(title=("Fatal error"), message=(err))


# functions
def produce_grid(workspace:Workspace=None, udata:Request=None, cellsize=4):
    def real_start():
        # try:
        #----------------------------------stat progress------------------------------------------------
        # showProgress("indeterminate", "Producing grid")
        #--------------------------------import start---------------------------------------
        # shapefileLocation = os.path.join(shapefileParent, "static/data/shapefiles/map.shp")
        shapefileLocation = udata.shp_file.path
        sf = shp.Reader(shapefileLocation)
        minx,miny,maxx,maxy = sf.bbox
        sf = None
        # cellsize = int(cellSizegridStrg.get())
        print(f"#####=====>{type(cellsize)}")
        if cellsize<=0:
            raise Exception("Cell size cannot be zero or less than zero")
        cellsizeInDegrees = cellsize*0.00833
        dx = cellsizeInDegrees
        dy = cellsizeInDegrees
        nx = int(math.ceil(abs(maxx - minx)/dx))
        ny = int(math.ceil(abs(maxy - miny)/dy))
        # gridshapefileLocation = os.path.join(settings.BASE_DIR, "static/data/gridFiles/grid")
        gridshapefileLocation = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/gridFiles/grid")
        print(f"####>>> {gridshapefileLocation}")
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
        # gridfileFolder = os.path.join(settings.BASE_DIR, "static/data")
        gridfileFolder = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/")
        if not os.path.isdir(gridfileFolder):
            os.makedirs(gridfileFolder)
        # gridDestination = os.path.join(settings.BASE_DIR, "static/data/grid.csv")
        gridDestination = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/grid.csv")
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
    thread = threading.Thread(target=real_start)
    thread.start()
    return thread



def produce_neighbourhood(workspace:Workspace=None, udata:Request=None, spedStrg=4):
    def real_negh():
        try:
            #----------------------------------stat progress------------------------------------------------
            # showProgress("determinate", "Producing neigbourhood")
            travelDist = spedStrg
            # gridDestination = os.path.join(settings.BASE_DIR, "static/data/grid.csv")
            gridDestination = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/grid.csv")
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
            # neghDestination = os.path.join(settings.BASE_DIR, "static/data/neigbourhood.csv")
            neghDestination = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/neigbourhood.csv")
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
    thread = threading.Thread(target=real_negh)
    thread.start()
    return thread


def test_constraints(constraints:list, cdatalist, idMax) -> bool:
    res = True
    for i in list(range(0, len(constraints))):
        if cdatalist[i][idMax] <= float(constraints[i].maximum) and cdatalist[i][idMax] > float(constraints[i].minimum):
            res = res and True
        else:
            res = res and False
    return res


def readData(fileLocation, fileExention):
    try:
        rawwData = pd.DataFrame()
        if fileExention=="xlsx":
            rawwData = pd.read_excel(fileLocation, header=None)
            if (type(rawwData.iloc[0,0])==str):
                rawwData = pd.read_excel(fileLocation)
        else:
            rawwData = pd.read_csv(fileLocation, header=None)
            if (type(rawwData.iloc[0,0])==str):
                rawwData = pd.read_csv(fileLocation)
        return rawwData.to_numpy()
    except Exception as err:
        traceback.print_exc()


def importConstraint(dataPath, ConstraintNumber):
    try: 
        dataPath = r"{}".format(dataPath)
        if dataPath:
            def real_start():
                importConstraintThreadStat(dataPath, ConstraintNumber)
            threading.Thread(target=real_start).start()
        # else:
        #     showerror(title=("Import error"), message=("Please import " + ConstraintNumber + " data"))
    except Exception as err:
        traceback.print_exc()



def readTiff(filePath, tiffFrme):
    try:
        with rio.open(filePath) as tifsrc:
            tiffdata = tifsrc.read()
        rowIndex, colIndex = tifsrc.index(tiffFrme["longitude"], tiffFrme["latitude"])
        nprow = np.array(rowIndex)
        nprow[nprow>(tiffdata.shape[1]-1)] = tiffdata.shape[1]-1
        npcol = np.array(colIndex)
        npcol[npcol>(tiffdata.shape[2]-1)] = tiffdata.shape[2]-1
        areaData = tiffdata[0, nprow, npcol]
        areaData[areaData<0] = 0
        return areaData
    except Exception as err:
        traceback.print_exc()



def importConstraintThreadStat(dataPathInConst, ConstraintNumberInConst):
    try:
        #----------------------------------stat progress------------------------------------------------
        docmExtn = os.path.splitext(dataPathInConst)[1]
        dataImpt = np.empty(0)
        gridForDataImportDestination = os.path.join(settings.BASE_DIR,"static/data/grid.csv")
        gridForDataImport = pd.read_csv(gridForDataImportDestination)
        if docmExtn==".tif":
            dataImpt = readTiff(dataPathInConst, gridForDataImport)
        elif docmExtn==".xlsx" or docmExtn==".xls":
            dataImpt = readData(dataPathInConst, "xlsx")
        elif docmExtn==".csv":
            dataImpt = readData(dataPathInConst, "csv")
        # else:
        #     showerror(title=("Import error"), message=("Please import a valid .tif, .xlsx, .xls or .csv data"))
        datafileFolder = os.path.join(settings.BASE_DIR,"static/data")
        if not os.path.isdir(datafileFolder):
            os.makedirs(datafileFolder)
        dataDestination = os.path.join(settings.BASE_DIR,"static/data"+ ConstraintNumberInConst + ".csv")
        if os.path.isfile(dataDestination):
            os.remove(dataDestination)
        pd.DataFrame(dataImpt).to_csv(dataDestination, header=None, index=None)
        checkImportShapeFiles()
        #----------------------------------endd progress------------------------------------------------
    except Exception as err:
        traceback.print_exc()



def importShp(shpPth, fileFormat):
    try:
        shpPth = filedialog.askopenfilename(title="Import a " + fileFormat + " file", 
                                              filetypes=[(fileFormat + " files", "*." + fileFormat)])
        shpPth = r"{}".format(shpPth)
        if shpPth:
            def real_start():
                shapefileFolder = os.path.join(settings.BASE_DIR,f'static/data/shapefiles')
                if not os.path.isdir(shapefileFolder):
                    os.makedirs(shapefileFolder)
                shpDestination = os.path.join(settings.BASE_DIR, 'static/data/shapefiles/map.'+fileFormat)
                if os.path.isfile(shpDestination):
                    os.remove(shpDestination)
                shutil.copyfile(shpPth, shpDestination)
                checkImportShapeFiles()
            threading.Thread(target=real_start).start() 
        else:
            print("No shape file path provided")
    except Exception as err:
        traceback.print_exc()


def checkImportShapeFiles():
    try:
        checkShape = os.path.join(settings.BASE_DIR, 'static/data/shapefiles/map.')
        if os.path.isfile(checkShape + "shp"):
            # areamenu.entryconfig(0,label="shp file") # Shape files
            pass
        else:
            # areamenu.entryconfig(0,label="shp file *") # Shape files
            pass
        if os.path.isfile(checkShape + "dbf"):
            # areamenu.entryconfig(1,label="dbf file") # Shape files
            pass
        else:
            # areamenu.entryconfig(1,label="dbf file *") # Shape files
            pass
        if os.path.isfile(checkShape + "shx"):
            # areamenu.entryconfig(2,label="shx file") # Shape files
            pass
        else:
            # areamenu.entryconfig(2,label="shx file *") # Shape files
            pass
        if (os.path.isfile(checkShape + "shp")) and (os.path.isfile(checkShape + "dbf")) and (os.path.isfile(checkShape + "shx")):
            # menubar.entryconfig(2,label="Shape files") # Shape files
            pass
        else:
            # menubar.entryconfig(2,label="Shape files *") # Shape files
            pass
    except Exception as err:
        traceback.print_exc()


# def tif_do_df(tifpath):
#     ds = gdal.Open("dem.tif")



def run_model(constraints:list, duration=10, start_month='Jan', start_year=2020, time_step=TSTEPS[0], workspace=None, udata=None):
    def stoprunn():
        fig = Figure(figsize=(4.9,4), dpi=300)
        a = fig.add_subplot(111)
        a.set_title("Dispersal")
        a.set_xlabel("Longitude")
        a.set_ylabel("Latitude")
    
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
            #--------------------------------import start---------------------------------------------
            # geoPandaDataFrame = gpd.read_file(os.path.join(settings.BASE_DIR, f"static/data/shapefiles/map.shp")).set_crs(epsg=4326)
            geoPandaDataFrame = gpd.read_file(udata.shp_file.path).set_crs(epsg=4326)
            points = gpd.GeoSeries([Point(-73.5, 40.5), Point(-74.5, 40.5)], crs=4326)
            points = points.to_crs(32619)
            distance_meters = points[0].distance(points[1])
            
            # codeUseGridData = pd.read_csv(os.path.join(settings.BASE_DIR, "static/data/grid.csv"), encoding='latin-1', on_bad_lines='skip').to_numpy()
            codeUseGridData = pd.read_csv(os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/grid.csv"), encoding='latin-1', on_bad_lines='skip').to_numpy()
            # codeUseGridData = pd.read_csv(os.path.join(settings.BASE_DIR, "static/data/grid.csv"), encoding='latin-1', on_bad_lines='skip').to_numpy()
            constraintDatas = []
            constraintFiles = []

            for item in constraints:
                constraintData = np.zeros(codeUseGridData.shape[0])
                constraintFile = item.file.path
                print(constraintFile)
                if os.path.isfile(constraintFile) and constraintFile.endswith(".csv"):
                    constraintData = pd.read_csv(constraintFile,encoding='latin-1', on_bad_lines='skip', header = None).to_numpy()[:,0]
                elif os.path.isfile(constraintFile) and constraintFile.endswith(".tif"):
                    # gridForDataImportDestination = os.path.join(settings.BASE_DIR, "static/data/grid.csv")
                    gridForDataImportDestination = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/grid.csv")
                    gridForDataImport = pd.read_csv(gridForDataImportDestination)
                    # if docmExtn==".tif":
                    constraintData = readTiff(constraintFile, gridForDataImport)
                    # img = Image.open(constraintFile)
                    # imageMat = np.asarray(img)
                    # constraintData = imageMat.reshape(imageMat.shape[0],-1)
                else:
                    const1Ul = 1
                    const1Lo = -1
                constraintDatas.append(constraintData)
                constraintFiles.append(constraintFile)
            
            neighbourData = pd.read_csv(os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/neigbourhood.csv"), encoding='latin-1', on_bad_lines='skip', header = None).to_numpy().astype(int)
            # neighbourData = pd.read_csv(os.path.join(settings.BASE_DIR, "static/data/neigbourhood.csv"), encoding='latin-1', on_bad_lines='skip', header = None).to_numpy().astype(int)
            importAffectedArea(udata)
            initialId = pd.read_csv(os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/Starting.csv"), encoding='latin-1', on_bad_lines='skip', header = None).to_numpy().astype(int)[:,0]
            # initialId = pd.read_csv(udata.affected_area.path, encoding='latin-1', on_bad_lines='skip', skiprows=[0],header = None).to_numpy().astype(int)[:,0]
            # print(f"###### {initialId}")
            # initialId = pd.read_csv(os.path.join(settings.BASE_DIR, "static/data/Starting.csv"),encoding='latin-1', on_bad_lines='skip', header = None).to_numpy().astype(int)[:,0]
            #--------------------------------import end-----------------------------------------

            initialData = np.concatenate((codeUseGridData[initialId,:], np.ones(initialId.shape[0]).reshape(initialId.shape[0],1)*-1), axis=1)
            idOfSiteInfected = initialId
            idOfSiteExposed = idOfSiteInfected
            
            statut = np.zeros(codeUseGridData.shape[0])
            
            statut[idOfSiteInfected] = 2
            #--------------------------------------data-----------------------------------------------
                
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
                    if statut[idMax]!=2 and test_constraints(constraints, constraintDatas, idMax):
                        statut[idMax]=2
                    
                if stopstat == 1:
                    stoprunn()
                    # showinfo(title=("Stop"), message=("Run stopped"))
                    break
                
                idOfSiteExposed = np.where(statut==1)[0]
                idOfSiteInfected = np.where(statut==2)[0]
                #--------------------------------------plot-----------------------------------------------
                csvvfileFolder = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/outputs/csv")
                # csvvfileFolder = os.path.join(settings.BASE_DIR, "static/data/outputs/csv")
                
                if not os.path.isdir(csvvfileFolder):
                    os.makedirs(csvvfileFolder)
                
                # tifffileFolder = os.path.join(settings.BASE_DIR, "static/data/outputs/png")

                tifffileFolder = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/outputs/png")
                
                if not os.path.isdir(tifffileFolder):
                    os.makedirs(tifffileFolder)
                
                csvvDestination = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/outputs/csv/Dispersal{str(timeStep+1)}.csv")
                tiffDestination = os.path.join(settings.MEDIA_ROOT, f"workspaces/{workspace.id}/data/{udata.req_uid}/outputs/png/Spread{str(timeStep+1)}.png")
                # csvvDestination = os.path.join(settings.BASE_DIR, "static/data/outputs/csv/Dispersal"+ str(timeStep+1) + ".csv")
                # tiffDestination = os.path.join(settings.BASE_DIR, "static/data/outputs/png/Spread" + str(timeStep+1) + ".png")
                
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
                ax.set_title(f"Dispersal: {start_month} {start_year + timeStep}")
                
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
                    break
                #--------------------------------------plot-----------------------------------------------
            if stopstat != 1:
                return
                # showinfo(title=("Success"), message=("Run complete"))   
        except Exception as err:
            traceback.print_exc()
    thread = threading.Thread(target=runnStat)
    thread.start()
    return thread



def importAffectedArea(udata:Request):
    """convert user's imported data to usable format in csv (Starging.csv) 
    within his workspace as initial points"""
    filepath = udata.affected_area.path
    gridForDataImport = pd.read_csv(os.path.join(settings.MEDIA_ROOT, f"workspaces/{udata.workspace.id}/data/{udata.req_uid}/grid.csv")).to_numpy()
    if str(filepath).endswith(".xlsx") or str(filepath).endswith(".xls"):
        dataImpt = readData(filepath, "xlsx")
    elif str(filepath).endswith(".csv"):
        dataImpt = readData(filepath, "csv")
    coloData = np.array([])
    for countrow in range(dataImpt.shape[0]):    
        origin = dataImpt[countrow]
        rangeDistance = distance(origin, gridForDataImport)
        coloData = np.union1d(coloData, np.where(rangeDistance==np.min(rangeDistance))[0][0])
    datafileFolder = os.path.join(settings.MEDIA_ROOT, f"workspaces/{udata.workspace.id}/data/{udata.req_uid}")
    if not os.path.isdir(datafileFolder):
        os.makedirs(datafileFolder)
    dataDestination = os.path.join(settings.MEDIA_ROOT, f"workspaces/{udata.workspace.id}/data/{udata.req_uid}/Starting.csv")
    if os.path.isfile(dataDestination):
        os.remove(dataDestination)
    pd.DataFrame(coloData).to_csv(dataDestination, header=None, index=None)
