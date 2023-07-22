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




plt.ioff()




# functions




def importAffected(affectedNumber):
    try:
        dataPath = filedialog.askopenfilename(title="Import " + affectedNumber + " area data", 
                                              filetypes=[("xlsx files", "*.xlsx"), ("xls files", "*.xls"), ("csv files", "*.csv")])
        
        dataPath = r"{}".format(dataPath)
        
        
        
        if dataPath:
            def real_start():
                importAffectedThreadStat(dataPath, affectedNumber)
            
            threading.Thread(target=real_start).start()
                
        else:
            showerror(title=("Import error"), message=("Please import " + affectedNumber + " area data"))
            
    except Exception as err:
        showerror(title=("Fatal error"), message=(err))




def importAffectedThreadStat(dataPathInaffected, affectedNumberInaffected):
    try:
        
        
        
        
        
        #----------------------------------stat progress------------------------------------------------
        showProgress("indeterminate", "Importing " + affectedNumberInaffected + " area data")
        docmExtn = os.path.splitext(dataPathInaffected)[1]
        dataImpt = np.empty(0)
        gridForDataImport = pd.read_csv(r"{}".format(pathname+"/resources/data/grid.csv")).to_numpy()
        if docmExtn==".xlsx" or docmExtn==".xls":
            dataImpt = readData(dataPathInaffected, "xlsx")
        
        elif docmExtn==".csv":
            dataImpt = readData(dataPathInaffected, "csv")
        else:
            showerror(title=("Import error"), message=("Please import a valid .xlsx, .xls or .csv data"))
        coloData = np.array([])
        
        for countrow in range(dataImpt.shape[0]):
                
            origin = dataImpt[countrow]
            rangeDistance = distance(origin, gridForDataImport)
            coloData = np.union1d(coloData, np.where(rangeDistance==np.min(rangeDistance))[0][0])
            
        
        datafileFolder = r"{}".format(pathname+"/resources/data")
        
        
        if not os.path.isdir(datafileFolder):
            os.makedirs(datafileFolder)
        
        dataDestination = r"{}".format(pathname+"/resources/data/" + affectedNumberInaffected + ".csv")
        
        
        
        if os.path.isfile(dataDestination):
            os.remove(dataDestination)
        
        pd.DataFrame(coloData).to_csv(dataDestination, header=None, index=None)
        
        checkImportShapeFiles()
        
        apWindow.update_idletasks()
        
        enddProgress("indeterminate")
        #----------------------------------endd progress------------------------------------------------
            
    except Exception as err:
        
        enddProgress("indeterminate")
        showerror(title=("Fatal error"), message=(err))




def importConstraintThreadStat(dataPathInConst, ConstraintNumberInConst):
    try:
        
        
        
        
        
        #----------------------------------stat progress------------------------------------------------
        showProgress("indeterminate", "Importing " + ConstraintNumberInConst + " data")
        docmExtn = os.path.splitext(dataPathInConst)[1]
        dataImpt = np.empty(0)
        
        gridForDataImportDestination = r"{}".format(pathname+"/resources/data/grid.csv")
        gridForDataImport = pd.read_csv(gridForDataImportDestination)
        if docmExtn==".tif":
            dataImpt = readTiff(dataPathInConst, gridForDataImport)
        
        elif docmExtn==".xlsx" or docmExtn==".xls":
            dataImpt = readData(dataPathInConst, "xlsx")
        
        elif docmExtn==".csv":
            dataImpt = readData(dataPathInConst, "csv")
        else:
            showerror(title=("Import error"), message=("Please import a valid .tif, .xlsx, .xls or .csv data"))
            
        
        datafileFolder = r"{}".format(pathname+"/resources/data")
        
        
        if not os.path.isdir(datafileFolder):
            os.makedirs(datafileFolder)
        
        dataDestination = r"{}".format(pathname+"/resources/data/" + ConstraintNumberInConst + ".csv")
        
        
        
        if os.path.isfile(dataDestination):
            os.remove(dataDestination)
        
        pd.DataFrame(dataImpt).to_csv(dataDestination, header=None, index=None)
        
        checkImportShapeFiles()
        
        apWindow.update_idletasks()
        
        enddProgress("indeterminate")
        #----------------------------------endd progress------------------------------------------------
            
    except Exception as err:
        
        enddProgress("indeterminate")
        showerror(title=("Fatal error"), message=(err))




def importConstraint(ConstraintNumber):
    try:
        dataPath = filedialog.askopenfilename(title="Import " + ConstraintNumber + " data", 
                                              filetypes=[("tif files", "*.tif")])
#                                              filetypes=[("tif files", "*.tif"), ("xlsx files", "*.xlsx"), ("xls files", "*.xls"), ("csv files", "*.csv")])
        
        dataPath = r"{}".format(dataPath)
        
        
        
        if dataPath:
            def real_start():
                importConstraintThreadStat(dataPath, ConstraintNumber)
            
            threading.Thread(target=real_start).start()
                
        else:
            showerror(title=("Import error"), message=("Please import " + ConstraintNumber + " data"))
            
    except Exception as err:
        showerror(title=("Fatal error"), message=(err))




def importShp(fileFormat):
    try:
        shpPth = filedialog.askopenfilename(title="Import a " + fileFormat + " file", 
                                              filetypes=[(fileFormat + " files", "*." + fileFormat)])
        
        shpPth = r"{}".format(shpPth)
        
        
        
        if shpPth:
            #-----------------------------progress bar start here--------------------------------------------
            def real_start():
                showProgress("indeterminate", "Importing " + fileFormat + " file")
                #--------------------------------import start------------------------------------------------
                shapefileFolder = r"{}".format(pathname+"/resources/shapefiles")
                
                if not os.path.isdir(shapefileFolder):
                    os.makedirs(shapefileFolder)
                
                shpDestination = r"{}".format(pathname+"/resources/shapefiles/map." + fileFormat)
                
                
                
                if os.path.isfile(shpDestination):
                    os.remove(shpDestination)
                
                shutil.copyfile(shpPth, shpDestination)
                #----------------------------------import end------------------------------------------------
                
                checkImportShapeFiles()
                
                apWindow.update_idletasks()
                
                enddProgress("indeterminate")
            
            threading.Thread(target=real_start).start()
            #--------------------------------progress bar end here-------------------------------------------
                
        else:
            showerror(title=("Import error"), message=("Please import " + fileFormat + " file"))
            
    except Exception as err:
        
        enddProgress("indeterminate")
        showerror(title=("Fatal error"), message=(err))




def checkImportShapeFiles():

    try:
        checkShape = r"{}".format(pathname+"/resources/shapefiles/map.")
        
        if os.path.isfile(checkShape + "shp"):
            areamenu.entryconfig(0,label="shp file") # Shape files
        else:
            areamenu.entryconfig(0,label="shp file *") # Shape files
        
        if os.path.isfile(checkShape + "dbf"):
            areamenu.entryconfig(1,label="dbf file") # Shape files
        else:
            areamenu.entryconfig(1,label="dbf file *") # Shape files
        
        if os.path.isfile(checkShape + "shx"):
            areamenu.entryconfig(2,label="shx file") # Shape files
        else:
            areamenu.entryconfig(2,label="shx file *") # Shape files
        
        if (os.path.isfile(checkShape + "shp")) and (os.path.isfile(checkShape + "dbf")) and (os.path.isfile(checkShape + "shx")):
            menubar.entryconfig(2,label="Shape files") # Shape files
        else:
            menubar.entryconfig(2,label="Shape files *") # Shape files
            
    except Exception as err:
        showerror(title=("Fatal error"), message=(err))




def onClick():
    pass




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







def prodGrid():
    def real_start():
    
        try:
            
            
            
            
            
            #----------------------------------stat progress------------------------------------------------
            showProgress("indeterminate", "Producing grid")
            #--------------------------------import start---------------------------------------
            shapefileLocation = r"{}".format(pathname+"/resources/shapefiles/map.shp")
            
            sf = shp.Reader(shapefileLocation)
            
            minx,miny,maxx,maxy = sf.bbox
            
            
            sf = None
            cellsize = int(cellSizegridStrg.get())
            if cellsize<=0:
                raise Exception("Cell size cannot be zero or less than zero")
            
            
            
            
            cellsizeInDegrees = cellsize*0.00833
            dx = cellsizeInDegrees
            dy = cellsizeInDegrees
            
            nx = int(math.ceil(abs(maxx - minx)/dx))
            ny = int(math.ceil(abs(maxy - miny)/dy))
            
            gridshapefileLocation = r"{}".format(pathname+"/resources/gridFiles/grid")
            
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
                
            
            gridfileFolder = r"{}".format(pathname+"/resources/data")
            
            
            if not os.path.isdir(gridfileFolder):
                os.makedirs(gridfileFolder)
            
            gridDestination = r"{}".format(pathname+"/resources/data/grid.csv")
            
            
            
            if os.path.isfile(gridDestination):
                os.remove(gridDestination)
            
            points_clipFrme[["latitude", "longitude"]].to_csv(gridDestination, index=False)
            
            
            points_clipFrme = None
                
            enddProgress("indeterminate")
            #----------------------------------endd progress------------------------------------------------
                
        except Exception as err:
                
            enddProgress("indeterminate")
            showerror(title=("Fatal error"), message=(err))
    
    
    #--------------------------------thread start-------------------------------------------
    threading.Thread(target=real_start).start()







def prodNeig():
    
    def real_negh():
    
        try:
            
            
            
            
            
            #----------------------------------stat progress------------------------------------------------
            showProgress("determinate", "Producing neigbourhood")
            
            
            travelDist = int(spedStrg.get())
            
            gridDestination = r"{}".format(pathname+"/resources/data/grid.csv")
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
                percentStrg.set(settValu + "%")
                barrvalu.set(settValu)
                    
                apWindow.update_idletasks()
            
            
            
            
            npNe = None
            
            
        
            neghDestination = r"{}".format(pathname+"/resources/data/neigbourhood.csv")
            
            
            
            if os.path.isfile(neghDestination):
                os.remove(neghDestination)
        
            pd.DataFrame(neigbourFile).to_csv(neghDestination, header=None, index=None)
            
            
            
            
            neigbourFile = None
            
            checkImportShapeFiles()
            
            apWindow.update_idletasks()
                        
            enddProgress("determinate")
            #----------------------------------endd progress------------------------------------------------
            
        except Exception as err:
                        
            enddProgress("determinate")
            showerror(title=("Fatal error"), message=(err))
    
    
    #--------------------------------thread start-------------------------------------------
    threading.Thread(target=real_negh).start()






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
        showerror(title=("Fatal error"), message=(err))






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
        showerror(title=("Fatal error"), message=(err))






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
        showerror(title=("Fatal error"), message=(err))




# functions
def stopButtonOnPres():
    global stopstat
    stopstat = 1




# functions
def runnButtonOnPres():
    def stoprunn():
        currentSimlStepStrg.set("----")
        totlSimStepStrg.set("----")
        global containergrph
        containergrph.destroy()
        theeLabl.destroy()
        containergrph = tk.LabelFrame(container3,bg="#F5F5F5", bd=0, width=500, height=400)
        
        
        
        fig = Figure(figsize=(4.9,4), dpi=100)
        a = fig.add_subplot(111)
        a.set_title("Dispersal")
        a.set_xlabel("Longitude")
        a.set_ylabel("Latitude")
        
        
        
        #a.plot([1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10])
        
        plotPart = FigureCanvasTkAgg(fig, master = containergrph)
        
        # plotPart.draw()
        containergrph.place(x = pox3, y =poy3 + dif3)
        plotPart.get_tk_widget().place(x = 0, y =0)
    
    
    
    
    def runnStat():
#        showProgress("indeterminate", "Running")

        try:
            stoprunn()
            global stopstat
            stopstat = 0
            global theeLabl
            theeLabl = tk.Label(container3, width=400, height=400)
            timeStepSimuCode = int(duraStrg.get())
            mnth = months.index(startTimeMonStrg.get())
            year = int(startTimeYearStrg.get())
            currentSimlStepStrg.set("----")
            totlSimStepStrg.set(timeStepSimuCode)
            currentTimeYearStrg.set(year)
            currentTimeMonStrg.set(months[mnth])
            #--------------------------------------data-----------------------------------------------
            const1Ul = float(const1UpLimtStrg.get())
            const1Lo = float(const1LoLimtStrg.get())
            const2Ul = float(const2UpLimtStrg.get())
            const2Lo = float(const2LoLimtStrg.get())
            const3Ul = float(const3UpLimtStrg.get())
            const3Lo = float(const3LoLimtStrg.get())
            const4Ul = float(const4UpLimtStrg.get())
            const4Lo = float(const4LoLimtStrg.get())
            
            
            #--------------------------------import start---------------------------------------------
            geoPandaDataFrame = gpd.read_file(r"{}".format(pathname+"/resources/shapefiles/map.shp")).set_crs(epsg=4326)
            points = gpd.GeoSeries([Point(-73.5, 40.5), Point(-74.5, 40.5)], crs=4326)
            points = points.to_crs(32619)
            distance_meters = points[0].distance(points[1])
            
            
            codeUseGridData = pd.read_csv(r"{}".format(pathname+"/resources/data/grid.csv")).to_numpy()
    
            Constraint1Data = np.zeros(codeUseGridData.shape[0])
            Constraint2Data = np.zeros(codeUseGridData.shape[0])
            Constraint3Data = np.zeros(codeUseGridData.shape[0])
            Constraint4Data = np.zeros(codeUseGridData.shape[0])
            
            Constraint1File = r"{}".format(pathname+"/resources/data/Constraint 1.csv")
            if os.path.isfile(Constraint1File):
                Constraint1Data = pd.read_csv(Constraint1File, header = None).to_numpy()[:,0]
            else:
                const1Ul = 1
                const1Lo = -1
            
            Constraint2File = r"{}".format(pathname+"/resources/data/Constraint 2.csv")
            if os.path.isfile(Constraint2File):
                Constraint2Data = pd.read_csv(Constraint2File, header = None).to_numpy()[:,0]
            else:
                const2Ul = 1
                const2Lo = -1
            
            Constraint3File = r"{}".format(pathname+"/resources/data/Constraint 3.csv")
            if os.path.isfile(Constraint3File):
                Constraint3Data = pd.read_csv(Constraint3File, header = None).to_numpy()[:,0]
            else:
                const3Ul = 1
                const3Lo = -1
            
            Constraint4File = r"{}".format(pathname+"/resources/data/Constraint 4.csv")
            if os.path.isfile(Constraint4File):
                Constraint4Data = pd.read_csv(Constraint4File, header = None).to_numpy()[:,0]
            else:
                const4Ul = 1
                const4Lo = -1
            
            neighbourData = pd.read_csv(r"{}".format(pathname+"/resources/data/neigbourhood.csv"), header = None).to_numpy().astype(int)
            
            initialId = pd.read_csv(r"{}".format(pathname+"/resources/data/Starting.csv"), header = None).to_numpy().astype(int)[:,0]
            #--------------------------------import end-----------------------------------------

            initialData = np.concatenate((codeUseGridData[initialId,:], np.ones(initialId.shape[0]).reshape(initialId.shape[0],1)*-1), axis=1)
            idOfSiteInfected = initialId
            idOfSiteExposed = idOfSiteInfected
            
            
            statut = np.zeros(codeUseGridData.shape[0])
            
            statut[idOfSiteInfected] = 2
            #--------------------------------------data-----------------------------------------------
                
            apWindow.update_idletasks()
                
            for timeStep in range(timeStepSimuCode):
                    
                    
                if stopstat == 1:
                    stoprunn()
                    showinfo(title=("Stop"), message=("Run stopped"))
                    break
                #--------------------------------------date-----------------------------------------------
                
                if timeStrg.get()=="Monthly":
                    mnth += 1
                    if mnth>=12:
                        mnth = 0
                        year += 1
                        currentTimeYearStrg.set(year)
                    
                    currentTimeMonStrg.set(months[mnth])
                else:
                    year += 1
                    currentTimeYearStrg.set(year)
                #--------------------------------------date-----------------------------------------------
                
                
                infectData = idOfSiteInfected
                exposeData = idOfSiteExposed
                
                IdVoisin = neighbourHoodForrDisp(neighbourData, np.union1d(exposeData,infectData), infectData)
                
                for p in range(IdVoisin.shape[0]):
                    
                    
                    if stopstat == 1:
                        break
                    
                    
                    idMax = int(IdVoisin[p])
                    statut[idMax] = 1
                    if ((statut[idMax]!=2) and (Constraint1Data[idMax]>const1Lo and Constraint1Data[idMax]<=const1Ul) and (Constraint2Data[idMax]>const2Lo and Constraint2Data[idMax]<=const2Ul) and (Constraint3Data[idMax]>const3Lo and Constraint3Data[idMax]<=const3Ul) and (Constraint4Data[idMax]>const4Lo and Constraint4Data[idMax]<=const4Ul)):
                        statut[idMax]=2
                    
                    
                if stopstat == 1:
                    stoprunn()
                    showinfo(title=("Stop"), message=("Run stopped"))
                    break
                
                idOfSiteExposed = np.where(statut==1)[0]
                idOfSiteInfected = np.where(statut==2)[0]
                #--------------------------------------plot-----------------------------------------------
                
            
                csvvfileFolder = r"{}".format(pathname+"/Output/csv")
                
                
                if not os.path.isdir(csvvfileFolder):
                    os.makedirs(csvvfileFolder)
                    
                
                tifffileFolder = r"{}".format(pathname+"/Output/tif")
                
                
                if not os.path.isdir(tifffileFolder):
                    os.makedirs(tifffileFolder)
                    
                
                csvvDestination = r"{}".format(pathname+"/Output/csv/Dispersal" + str(timeStep+1) + ".csv")
                tiffDestination = r"{}".format(pathname+"/Output/tif/Spread" + str(timeStep+1) + ".tif")
                
                
                
                if os.path.isfile(csvvDestination):
                    os.remove(csvvDestination)
                
                
                
                if os.path.isfile(tiffDestination):
                    os.remove(tiffDestination)
                
                
                data = pd.DataFrame(np.concatenate((codeUseGridData, statut.reshape(statut.shape[0],1)), axis=1))
                data.columns = ["latitide", "longitude", "data"]
                    
                    
                if stopstat == 1:
                    stoprunn()
                    showinfo(title=("Stop"), message=("Run stopped"))
                    break
        
                pd.DataFrame(data).to_csv(csvvDestination, index=None)
    
                df = pd.read_csv(csvvDestination)
    
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
                
                
                
                
                fig, ax = plt.subplots(1,1,figsize=(4.8,4), dpi=100)
                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")
                ax.set_title("Dispersal "+currentTimeMonStrg.get()+" "+currentTimeYearStrg.get())
                
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
                
                
                
                
                ax = None
                global theeImag
                theeImag = ImageTk.PhotoImage(Image.open(tiffDestination))
                global containergrph
                containergrph.destroy()
                containergrph = tk.LabelFrame(container3,bg="#F5F5F5", bd=0, width=500, height=400)
                containergrph.place(x = pox3, y =poy3 + dif3)
                theeLabl.destroy()
                currentSimlStepStrg.set(timeStep + 1)
                theeLabl = tk.Label(containergrph,bg="#F5F5F5", image=theeImag, width=500, height=400)
                theeLabl.place(x = 0, y =0)
                
                apWindow.update_idletasks()
                    
                    
                if stopstat == 1:
                    stoprunn()
                    showinfo(title=("Stop"), message=("Run stopped"))
                    break
            
            
            
                #--------------------------------------plot-----------------------------------------------
                
                
            if stopstat != 1:
                showinfo(title=("Success"), message=("Run complete"))
        
            
         
            
            
#            gdal.Grid(tiffDestination, csvvDestination, zfield="data", algorithm = "nearest:radius1=0.3:radius2=0.3:nodata=-9999")
                
#            enddProgress("indeterminate")
                    
        except Exception as err:
            showerror(title=("Fatal error"), message=(err))
            
            
    threading.Thread(target=runnStat).start()




def valdButtonOnPres():
        
        
    def vald_stat():
    
        try:
            global stopstat
            stopstat = 0
            showProgress("indeterminate", "Calibrating")
            mseeStrg.set("--------")
            
            
            #--------------------------------global variables--------------------------------------------
            global timeComl
            timeComl = timeStrg.get()
            
            #--------------------------------global variables--------------------------------------------
            
            
            #--------------------------------simulation variables ---------------------------------------
            const1Ul = float(const1UpLimtStrg.get())
            const1Lo = float(const1LoLimtStrg.get())
            const2Ul = float(const2UpLimtStrg.get())
            const2Lo = float(const2LoLimtStrg.get())
            const3Ul = float(const3UpLimtStrg.get())
            const3Lo = float(const3LoLimtStrg.get())
            const4Ul = float(const4UpLimtStrg.get())
            const4Lo = float(const4LoLimtStrg.get())
            latdVald = float(latdStrg.get())
            longVald = float(longStrg.get())
            
            if timeComl=="Monthly":
                diffPrac = (((int(enddTimeYearStrg.get()) - int(startTimeYearStrg.get()))*12) + (months.index(enddTimeMontStrg.get())-months.index(startTimeMonStrg.get())))
            else:
                diffPrac = int(enddTimeYearStrg.get()) - int(startTimeYearStrg.get())
            
            if diffPrac<=0:
                raise Exception("Check start and end dates again")
        
            #--------------------------------simulation variables ---------------------------------------
            
            
            
            
            #--------------------------------import start---------------------------------------
            codeUseGridData = pd.read_csv(r"{}".format(pathname+"/resources/data/grid.csv")).to_numpy()
    
            Constraint1Data = np.zeros(codeUseGridData.shape[0])
            Constraint2Data = np.zeros(codeUseGridData.shape[0])
            Constraint3Data = np.zeros(codeUseGridData.shape[0])
            Constraint4Data = np.zeros(codeUseGridData.shape[0])
            
            Constraint1File = r"{}".format(pathname+"/resources/data/Constraint 1.csv")
            if os.path.isfile(Constraint1File):
                Constraint1Data = pd.read_csv(Constraint1File, header = None).to_numpy()[:,0]
            else:
                const1Ul = 1
                const1Lo = -1
            
            Constraint2File = r"{}".format(pathname+"/resources/data/Constraint 2.csv")
            if os.path.isfile(Constraint2File):
                Constraint2Data = pd.read_csv(Constraint2File, header = None).to_numpy()[:,0]
            else:
                const2Ul = 1
                const2Lo = -1
            
            Constraint3File = r"{}".format(pathname+"/resources/data/Constraint 3.csv")
            if os.path.isfile(Constraint3File):
                Constraint3Data = pd.read_csv(Constraint3File, header = None).to_numpy()[:,0]
            else:
                const3Ul = 1
                const3Lo = -1
            
            Constraint4File = r"{}".format(pathname+"/resources/data/Constraint 4.csv")
            if os.path.isfile(Constraint4File):
                Constraint4Data = pd.read_csv(Constraint4File, header = None).to_numpy()[:,0]
            else:
                const4Ul = 1
                const4Lo = -1
            
            neighbourHood = pd.read_csv(r"{}".format(pathname+"/resources/data/neigbourhood.csv"), header = None).to_numpy().astype(int)
            
            initialId = pd.read_csv(r"{}".format(pathname+"/resources/data/Starting.csv"), header = None).to_numpy().astype(int)[:,0]
            #--------------------------------import end-----------------------------------------
            
            idOfSiteInfected = initialId
            idOfSiteExposed = idOfSiteInfected
                
            origin = np.array([latdVald, longVald])
            rangeDistance = distance(origin, codeUseGridData)
            
            
            idOfSiteValidation = np.where(rangeDistance==np.min(rangeDistance))[0][0]
            
            
            rangeDistance = None
            
            
            
            
            statut = np.zeros(codeUseGridData.shape[0])
            
            statut[idOfSiteInfected] = 2
            statut[idOfSiteValidation] = 0
            timeStep = 0
            
            
            
            while True:
                    
                    
                if stopstat == 1:
                    break
                
                
                if statut[idOfSiteValidation]==1 or statut[idOfSiteValidation] == 2:
                    break
                
                
                infectData = idOfSiteInfected
                exposeData = idOfSiteExposed
                neighbourData = neighbourHood
                
                IdVoisin = neighbourHoodForrDisp(neighbourData, np.union1d(exposeData,infectData), infectData)
                
                for p in range(IdVoisin.shape[0]):
                    
                    
                    if stopstat == 1:
                        break
                    
                    
                    idMax = int(IdVoisin[p])
                    statut[idMax] = 1
                    if ((statut[idMax]!=2) and (Constraint1Data[idMax]>const1Lo and Constraint1Data[idMax]<=const1Ul) and (Constraint2Data[idMax]>const2Lo and Constraint2Data[idMax]<=const2Ul) and (Constraint3Data[idMax]>const3Lo and Constraint3Data[idMax]<=const3Ul) and (Constraint4Data[idMax]>const4Lo and Constraint4Data[idMax]<=const4Ul)):
                        statut[idMax]=2
                    
                    
                if stopstat == 1:
                    break
                
                idOfSiteExposed = np.where(statut==1)[0]
                idOfSiteInfected = np.where(statut==2)[0]
                apWindow.update_idletasks()
                
                
                timeStep += 1
                    
                    
            if stopstat == 1:
                mseeStrg.set("----")
        
                enddProgress("indeterminate")
                showinfo(title=("Stop"), message=("Calibration stopped"))
                return
                    
                    
                    
                    
            statut = None
            
            
            
            
            diffRela = timeStep - diffPrac
            abslDiff = abs(diffRela)
            
            if diffRela>=0:
                
                if timeComl=="Monthly":
                    mseeStrg.set(str(int(abslDiff)) + " Months ahead")
                else:
                    mseeStrg.set(str(int(abslDiff)) + " Years ahead")
            else:
                
                if timeComl=="Monthly":
                    mseeStrg.set(str(int(abslDiff)) + " Months delay")
                else:
                    mseeStrg.set(str(int(abslDiff)) + " Years delay")
            
            
            #--------------------------------global variables--------------------------------------------
            
            #--------------------------------global variables--------------------------------------------
                    
                    
            if stopstat == 1:
                mseeStrg.set("----")
        
                enddProgress("indeterminate")
                showinfo(title=("Stop"), message=("Calibration stopped"))
                return
        
            enddProgress("indeterminate")
            
            
            
            
            showinfo(title=("Success"), message=("Calibration complete with " + str(int(abslDiff)) + " Months delay"))
                
        except Exception as err:
            
            enddProgress("indeterminate")
            showerror(title=("Fatal error"), message=(err))
            
            
    threading.Thread(target=vald_stat).start()




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




def enddProgress(progMode):
    
    if progMode=="indeterminate":
        bar.stop()
        bar.destroy()
        progressLabel.destroy()
    else:
        bar.destroy()
        progressLabel.destroy()
        percentLabel.destroy()




def readProjectFolderLocation():

    try:
        global pathname
        pathFldr = filedialog.askdirectory(title="Select working folder now")
        pathFldr = r"{}".format(pathFldr)
        
        
        if pathFldr:
            pathname = pathFldr
            checkImportShapeFiles()
            filemenu.entryconfig(0,label="Select project folder")
            menubar.entryconfig(1,label="File")
              
        else:
            pass
            
    except Exception as err:
        showerror(title=("Fatal error"), message=(err))


        
    






apWindow = tk.Tk()
buttonWidth = 28

apWindow.wm_title("PyDisp")  # the title
apWindow.geometry("1200x600+100+40")
#apWindow.iconbitmap(r"C:\Users\peter\Downloads\facebook_cover_photo_1.ico")
apWindow.configure(background="#F5F5F5")




# variables
onColr = "#28BE28"
ofColr = "#28BE28"
bgColr = "#F5F5F5"

months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
timeSteps = ("Monthly", "Yearly")


statusFl = {"shp": 0, "dbf": 0, "shx": 0, "bio1": 0, "bio2": 0, "abio1": 0, "abio2": 0, "start": 0, "valid": 0}
stopstat = 0


const1UpLimtStrg = tk.StringVar()
const1LoLimtStrg = tk.StringVar()
const2UpLimtStrg = tk.StringVar()
const2LoLimtStrg = tk.StringVar()
const3UpLimtStrg = tk.StringVar()
const3LoLimtStrg = tk.StringVar()
const4UpLimtStrg = tk.StringVar()
const4LoLimtStrg = tk.StringVar()


spedStrg = tk.StringVar()
cellSizegridStrg = tk.StringVar()
timeStrg = tk.StringVar()
duraStrg = tk.StringVar()
startTimeMonStrg = tk.StringVar()
startTimeYearStrg = tk.StringVar()
currentTimeMonStrg = tk.StringVar()
currentTimeYearStrg = tk.StringVar()
currentSimlStepStrg = tk.StringVar()
totlSimStepStrg = tk.StringVar()
mseeStrg = tk.StringVar()


latdStrg = tk.StringVar()
longStrg = tk.StringVar()
enddTimeMontStrg = tk.StringVar()
enddTimeYearStrg = tk.StringVar()



const1UpLimtStrg.set("0.0")
const1LoLimtStrg.set("0.0")
const2UpLimtStrg.set("0.0")
const2LoLimtStrg.set("0.0")
const3UpLimtStrg.set("0.0")
const3LoLimtStrg.set("0.0")
const4UpLimtStrg.set("0.0")
const4LoLimtStrg.set("0.0")


spedStrg.set("0")
cellSizegridStrg.set("0")
timeStrg.set(timeSteps[0])
duraStrg.set("1")
startTimeMonStrg.set(months[0])
startTimeYearStrg.set("2020")
currentTimeMonStrg.set("----")
currentTimeYearStrg.set("----")
currentSimlStepStrg.set("----")
totlSimStepStrg.set("----")
mseeStrg.set("--------")


latdStrg.set("0.0")
longStrg.set("0.0")
enddTimeMontStrg.set(months[0])
enddTimeYearStrg.set("2021")




#clen
container1 = tk.LabelFrame(apWindow,bg="#F5F5F5", text="Data inputs", width=260, height=500)
container2 = tk.LabelFrame(apWindow,bg="#F5F5F5", text="Starting period", width=260, height=190)
container3 = tk.LabelFrame(apWindow,bg="#F5F5F5", text="Output", width=560, height=500)
container4 = tk.LabelFrame(apWindow,bg="#F5F5F5", width=260, height=280)
containergrph = tk.LabelFrame(container3,bg="#F5F5F5", bd=0, width=500, height=400)




noteBook = ttk.Notebook(container4, width=248, height=248)
valdNote = ttk.Frame(noteBook)
runnNote = ttk.Frame(noteBook)
noteBook.add(valdNote, text="Calibration")
noteBook.add(runnNote, text="Run")



#menu
menubar = tk.Menu(apWindow)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Select project folder *", command=readProjectFolderLocation)
menubar.add_cascade(label="File *", menu=filemenu)

areamenu = tk.Menu(menubar, tearoff=0)
areamenu.add_command(label="shp file *", command=lambda: importShp("shp"))
areamenu.add_command(label="dbf file *", command=lambda: importShp("dbf"))
areamenu.add_command(label="shx file *", command=lambda: importShp("shx"))
menubar.add_cascade(label="Shape files *", menu=areamenu)

gridmenu = tk.Menu(menubar, tearoff=0)
gridmenu.add_command(label="Produce grid *", command=prodGrid)
gridmenu.add_command(label="Produce neigbourhood *", command=prodNeig)
menubar.add_cascade(label="Grid/Neigbourhood *", menu=gridmenu)

datamenu = tk.Menu(menubar, tearoff=0)
datamenu.add_command(label="Constraint 1 *", command=lambda: importConstraint("Constraint 1"))
datamenu.add_command(label="Constraint 2 *", command=lambda: importConstraint("Constraint 2"))
datamenu.add_command(label="Constraint 3 *", command=lambda: importConstraint("Constraint 3"))
datamenu.add_command(label="Constraint 4 *", command=lambda: importConstraint("Constraint 4"))
menubar.add_cascade(label="Import data *", menu=datamenu)

valdmenu = tk.Menu(menubar, tearoff=0)
valdmenu.add_command(label="Starting area *", command=lambda: importAffected("Starting"))
menubar.add_cascade(label="Affected area *", menu=valdmenu)

apWindow.config(menu=menubar)


menubar.entryconfig(0,state="normal") # Shape files
menubar.entryconfig(1,state="normal") # Import data
menubar.entryconfig(2,state="normal") # Affected area




# labels
const1UpLimtLabl = ttk.Label(container1, text="Constraint 1 upper limit", background=bgColr)
const1LoLimtLabl = ttk.Label(container1, text="Constraint 1 lower limit", background=bgColr)
const2UpLimtLabl = ttk.Label(container1, text="Constraint 2 upper limit", background=bgColr)
const2LoLimtLabl = ttk.Label(container1, text="Constraint 2 lower limit", background=bgColr)
const3UpLimtLabl = ttk.Label(container1, text="Constraint 3 upper limit", background=bgColr)
const3LoLimtLabl = ttk.Label(container1, text="Constraint 3 lower limit", background=bgColr)
const4UpLimtLabl = ttk.Label(container1, text="Constraint 4 upper limit", background=bgColr)
const4LoLimtLabl = ttk.Label(container1, text="Constraint 4 lower limit", background=bgColr)


spedLabl = ttk.Label(container1, text="Travel speed (km/time step)", background=bgColr)
cellSizegridLabl = ttk.Label(container1, text="Cell size (km)", background=bgColr)
timeLabl = ttk.Label(container2, text="Time step", background=bgColr)
duraLabl = ttk.Label(runnNote, text="Duration", background=bgColr)
startTimeMonLabl = ttk.Label(container2, text="Month", background=bgColr)
startTimeYearLabl = ttk.Label(container2, text="Year", background=bgColr)
outOfStepLabl = ttk.Label(container3, text="out of", background=bgColr)
currentSimlStepLabl = ttk.Label(container3, textvariable=currentSimlStepStrg, background=bgColr, width=4)
totlSimStepLabl = ttk.Label(container3, textvariable=totlSimStepStrg, background=bgColr, width=4)
simlValuStepLabl = ttk.Label(container3, text="Simulation", background=bgColr)
mseeLabl = ttk.Label(valdNote, text="Diff = ", background=bgColr)
mseeOutpValdLabl = ttk.Label(valdNote, textvariable=mseeStrg, background=bgColr, width=20)


latdLablInVald = ttk.Label(valdNote, text="Lat", background=bgColr)
longLablInVald = ttk.Label(valdNote, text="Lon", background=bgColr)
startTimeMonLablInVald = ttk.Label(valdNote, text="Month", background=bgColr)
startTimeYearLablInVald = ttk.Label(valdNote, text="Year", background=bgColr)




# text inputs
const1UpLimtEntry= ttk.Entry(container1, textvariable=const1UpLimtStrg, width=10)
const1LoLimtEntry= ttk.Entry(container1, textvariable=const1LoLimtStrg, width=10)
const2UpLimtEntry= ttk.Entry(container1, textvariable=const2UpLimtStrg, width=10)
const2LoLimtEntry= ttk.Entry(container1, textvariable=const2LoLimtStrg, width=10)
const3UpLimtEntry= ttk.Entry(container1, textvariable=const3UpLimtStrg, width=10)
const3LoLimtEntry= ttk.Entry(container1, textvariable=const3LoLimtStrg, width=10)
const4UpLimtEntry= ttk.Entry(container1, textvariable=const4UpLimtStrg, width=10)
const4LoLimtEntry= ttk.Entry(container1, textvariable=const4LoLimtStrg, width=10)


spedEntry= ttk.Entry(container1, textvariable=spedStrg, width=10)
cellSizegridEntry= ttk.Entry(container1, textvariable=cellSizegridStrg, width=10)
duraEntry= ttk.Entry(runnNote, textvariable=duraStrg, width=12)
startTimeYearEntry= ttk.Entry(container2, textvariable=startTimeYearStrg, width=12)


latdEntry= ttk.Entry(valdNote, textvariable=latdStrg, width=14)
longEntry= ttk.Entry(valdNote, textvariable=longStrg, width=14)
enddTimeYearEntry= ttk.Entry(valdNote, textvariable=enddTimeYearStrg, width=14)




# buttons
runnButton = ttk.Button(runnNote, text="Run", width=14, command=runnButtonOnPres)
valdButton = ttk.Button(valdNote, text="Calibrate", width=14, command=valdButtonOnPres)
stopButtonrunnstat = ttk.Button(runnNote, text="Stop", width=14, command=stopButtonOnPres)
stopButtonvaldstat = ttk.Button(valdNote, text="Stop", width=14, command=stopButtonOnPres)




#spinbox
startTimeMonSpin = ttk.Spinbox(container2, values=months, width=10, state="readonly", textvariable=startTimeMonStrg)
timeSpin= ttk.Spinbox(container2, values=timeSteps, width=10, state="readonly", textvariable=timeStrg)
enddTimeMontSpin= ttk.Spinbox(valdNote, values=months, width=12, state="readonly", textvariable=enddTimeMontStrg)
theeLabl = tk.Label(container3, width=400, height=400)




#placing elements
container1.place(x = 20, y =60)
container2.place(x = 320, y =60)
container3.place(x = 620, y =60)
container4.place(x = 320, y =280)




dif1 = 44
pox1 = 20
pxx1 = pox1 + 150
poy1 = 40

const1UpLimtLabl.place(x = pox1, y =poy1)
const1LoLimtLabl.place(x = pox1, y =poy1 + dif1)
const2UpLimtLabl.place(x = pox1, y =poy1 + (dif1*2))
const2LoLimtLabl.place(x = pox1, y =poy1 + (dif1*3))
const3UpLimtLabl.place(x = pox1, y =poy1 + (dif1*4))
const3LoLimtLabl.place(x = pox1, y =poy1 + (dif1*5))
const4UpLimtLabl.place(x = pox1, y =poy1 + (dif1*6))
const4LoLimtLabl.place(x = pox1, y =poy1 + (dif1*7))
spedLabl.place(x = pox1, y =poy1 + (dif1*9))
cellSizegridLabl.place(x = pox1, y =poy1 + (dif1*8))

const1UpLimtEntry.place(x = pxx1, y =poy1)
const1LoLimtEntry.place(x = pxx1, y =poy1 + dif1)
const2UpLimtEntry.place(x = pxx1, y =poy1 + (dif1*2))
const2LoLimtEntry.place(x = pxx1, y =poy1 + (dif1*3))
const3UpLimtEntry.place(x = pxx1, y =poy1 + (dif1*4))
const3LoLimtEntry.place(x = pxx1, y =poy1 + (dif1*5))
const4UpLimtEntry.place(x = pxx1, y =poy1 + (dif1*6))
const4LoLimtEntry.place(x = pxx1, y =poy1 + (dif1*7))
spedEntry.place(x = pxx1, y =poy1 + (dif1*9))
cellSizegridEntry.place(x = pxx1, y =poy1 + (dif1*8))



  
dif2 = 40
pox2 = 10
pxx2 = pox2 + 70
poy2 = 40

startTimeMonLabl.place(x = pox2, y =poy2)
startTimeMonSpin.place(x = pxx2, y =poy2)
startTimeYearLabl.place(x = pox2, y =poy2 + dif2)
startTimeYearEntry.place(x = pxx2, y =poy2 + dif2)

timeLabl.place(x = pox2, y =poy2 + (dif2*2))
timeSpin.place(x = pxx2, y =poy2 + (dif2*2))




dif3 = 40
pox3 = 28
pxx3 = pox3 + 160
poy3 = 10

simlValuStepLabl.place(x = pxx3, y =poy3)
currentSimlStepLabl.place(x = pxx3+80, y =poy3)
outOfStepLabl.place(x = pxx3+120, y =poy3)
totlSimStepLabl.place(x = pxx3+160, y =poy3)



  
dif4 = 30
pox4 = 10
pxx4 = pox4 + 60
poy4 = 20

runnButton.place(x = pox4, y =poy4 + (dif4*6.5))
valdButton.place(x = pox4, y =poy4 + (dif4*6.5))
stopButtonrunnstat.place(x = pxx4 + 68, y =poy4 + (dif4*6.5))
stopButtonvaldstat.place(x = pxx4 + 68, y =poy4 + (dif4*6.5))


latdLablInVald.place(x = pox4, y =poy4)
longLablInVald.place(x = pox4, y =poy4 + dif4)
startTimeMonLablInVald.place(x = pox4, y =poy4 + (dif4*2))
startTimeYearLablInVald.place(x = pox4, y =poy4 + (dif4*3))


latdEntry.place(x = pxx4, y =poy4)
longEntry.place(x = pxx4, y =poy4 + dif4)
enddTimeMontSpin.place(x = pxx4, y =poy4 + (dif4*2))
enddTimeYearEntry.place(x = pxx4, y =poy4 + (dif4*3))

mseeLabl.place(x = pox4, y =poy4 + (dif4*5))

mseeOutpValdLabl.place(x = pxx4, y =poy4 + (dif4*5))

noteBook.place(x = 2.8, y =1)

duraLabl.place(x = pox4, y =poy4 + (dif4*3))
duraEntry.place(x = pxx4, y =poy4+ (dif4*3))



fig = Figure(figsize=(4.9,4), dpi=100)
a = fig.add_subplot(111)
a.set_title("Dispersal")
a.set_xlabel("Longitude")
a.set_ylabel("Latitude")



#a.plot([1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10])

plotPart = FigureCanvasTkAgg(fig, master = containergrph)

# plotPart.draw()
containergrph.place(x = pox3, y =poy3 + dif3)
plotPart.get_tk_widget().place(x = 0, y =0)




#folderButton.config(state="disabled")







apWindow.mainloop()



