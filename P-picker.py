
"""
Manually pick wave moveout for events.

Parameters:
TO DO


"""


import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import datetime
import pickle #dictionaries!
import scipy
from scipy import signal #For data cleanup
import obspy
from obspy.core import UTCDateTime #MAYBE useful.
from obspy.core import read
from obspy.signal import trigger #For triggering, required.


def sintela_to_datetime(sintela_times):
    '''
    Returns an array of datetime.datetime 
    Function provided by John-Morgand
    ''' 
    days1970 = datetime.date(1970, 1, 1).toordinal() #total days from 0

    # Vectorize everything
    converttime = np.vectorize(datetime.datetime.fromordinal)
    addday_lambda = lambda x : datetime.timedelta(days=x)
    adddays = np.vectorize(addday_lambda )

    day = days1970 + sintela_times/1e6/60/60/24 #Convert Sintela times to days from microseconds
    thisDateTime = converttime(np.floor(day).astype(int))
    dayFraction = day-np.floor(day)
    thisDateTime = thisDateTime + adddays(dayFraction)

    return thisDateTime


def getpwaves(Event, Catalogue, Dataset, Sensitivity = .05):

    """
    This function allows the user to pick p waves for a given event


    """
    PlotEvent(Event,Catalogue,Dataset,Sensitivity = Sensitivity,doseconds=False) #Plot the event, so that we can take picks.
    fig = plt.gcf() # gets last figure (so that the clicker knows what to look at)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    kid = fig.canvas.mpl_connect('key_press_event', onkey)
    global Cont #Janky function so user can take as many points as they want
    print("Shift left click to take a point, shift right click to remove it. Enter to end.")
    while Cont == True:
        plt.waitforbuttonpress()
        fig.canvas.draw_idle()
    fig.canvas.mpl_disconnect(cid)
    fig.canvas.mpl_disconnect(kid)# Disconnect the click handler
    plt.close()

    #Instead of return, maybe it should just save them directly to the event file? That might be the simplest, especially if I'm running this independent to the catalogue function.
    return PointsMaster


def onclick(event):
    if event.key != 'shift':  # Only handle clicks if Shift is held
        return
    print("Clicked!")
    if event.xdata is None or event.ydata is None:
        print("Click in the box, numbskull.")
        return
    if event.button == 1:
        print(f"Point recorded: ({event.xdata:.2f}, {event.ydata:.2f})")
        PointsMaster.append((event.xdata, event.ydata))

        Pointy = plt.scatter(event.xdata, event.ydata, color='red', s=10)
        PlottedPoints.append(Pointy)
        return
    elif event.button == 3 and PointsMaster != []:
        # Shift+Right-click to remove last point
        print(f"Removed last point: {PointsMaster[-1]}")
        point = PointsMaster.pop()
        Pointy = PlottedPoints.pop()
        Pointy.remove()
    else:
        return


#def onclick(event):
##    if collecting and event.key == 'shift' and event.inaxes:
 #       x, y = event.xdata, event.ydata
 #       PointsMaster.append((x, y))
 #       print(f"Point selected: ({x:.2f}, {y:.2f})")
def onkey(event):
    global Cont
    if event.key == 'enter':
        print("Enter pressed — stopping point collection.")
        Cont = False
        plt.close()  # Close the figure to exit the event loop



def Detect(Section,Dataset,Sensitivity=.05,Lowpass=1,Highpass=50,YLowerLim=None,YUpperLim=None, doseconds = True, show=True):
    """
    Generates a pcolormesh of the desired Section with a designated parameters

    Parameters:
    - Section: The section to plot
    - Dataset: The file location
    - Sensitivity: The sensitivity (in radians)
    - Lowpass: for Lowpass filter (Hz)
    - Highpass: for Highpass filter (Hz)
    - YLowerLim: Lower limit ()
    - YUpperLim: Upper limit ()
    - doseconds: If true, then the time axis is in seconds, if false it's datetime. 
    - show: Whether the plotted image should be shown.

    Returns nothing

    """
    #TO DO: Add an input to allow changing of ACTUAL FILTERING, not just highpass/lowpass.
    #TO DO: Make limits a tuple for simplification.
    #TO DO: Allow option to convert or not to convert to seconds, specifically for p wave picks... I need datetimes.

    Smin = -Sensitivity
    Smax = Sensitivity
    if YLowerLim == None:
        YLowerLim = 0
    if YUpperLim == None:
        YUpperLim = 60
    with h5.File(f'{Dataset}','r') as PulledFile: #WARNING: Generalize this, so that it can be from the "selected" catalogue
        DATA_TEMP = PulledFile['Data']['PosData'][f'Section {Section}']
        TIME_TEMP = PulledFile['Data']['TimeData'][f'Section {Section}']
        INFO = PulledFile['Data']['RootInfo']
        PR = INFO['Acquisition'].attrs['PulseRate']

        channels = np.arange(0,DATA_TEMP.shape[1],1)
        seconds = np.arange(0,DATA_TEMP.shape[0],1)
        Time = sintela_to_datetime(TIME_TEMP[:,]) 

    Seconds = [(T-Time[0]).total_seconds() for T in Time] #Super curious list comprehension function, I don't really get how it works but it's neat, "Vectorizes" the set of data and subtracts the time from each, which produces an array of seconds.
    #Seconds = [x for x in Seconds if YLowerLim <= x <= YUpperLim]

    sos = scipy.signal.butter(10, [Lowpass,Highpass], 'bp', fs = PR, output='sos') #WARNING WARNING: INFO['Acquisition'] IS NOT A GENERALIZED FUNCTION, LACK OF VERSATALITY!!!!
    filtered = signal.sosfiltfilt(sos,DATA_TEMP,axis=0)

    Seconds = np.round(np.array(Seconds),4)
    CorrectedLowerLim = np.where(Seconds == float(YLowerLim))
    CorrectedUpperLim = np.where(Seconds == float(YUpperLim))
    n = YLowerLim
    m = YUpperLim
    count = 0
    max_iters = 20
    while CorrectedLowerLim[0].size == 0:
        n = n - .01
        CorrectedLowerLim = np.where(Seconds == float(n))
        count += 1
        if count >= max_iters:
            n = YLowerLim
            count = 0
            while CorrectedLowerLim[0].size == 0:
                n = n + .01
                CorrectedLowerLim = np.where(Seconds == float(n))
                count +=1
                if count >= max_iters:
                    break
        if count >= max_iters:
            CorrectedLowerLim = (np.array([0]),)
            break

    count = 0
    while CorrectedUpperLim[0].size == 0:
        m = m + .01
        CorrectedUpperLim = np.where(Seconds == float(m))
        count += 1
        if count >= max_iters:
            m = YUpperLim
            count = 0
            while CorrectedUpperLim[0].size == 0:
                m = m - .01
                CorrectedUpperLim = np.where(Seconds == float(m))
                count +=1
                if count >= max_iters:
                    break
        if count >= max_iters:
            CorrectedUpperLim = (np.array([120000]),)
            break

    if doseconds == True:


        Seconds = Seconds[CorrectedLowerLim[0][0]:CorrectedUpperLim[0][0]]

        filtered = filtered[CorrectedLowerLim[0][0]:CorrectedUpperLim[0][0],:]

        fig,ax = plt.subplots()
        smesh = ax.pcolormesh(channels, Seconds, filtered, vmin = Smin, vmax = Smax, cmap = 'seismic',shading='nearest')
        plt.xlabel('channels')
        plt.ylabel('seconds')
        #ax.set_ylim(YLowerLim, YUpperLim)
        fig.colorbar(smesh,ax=ax)

    else:
        Time = Time[CorrectedLowerLim[0][0]:CorrectedUpperLim[0][0]]
        filtered = filtered[CorrectedLowerLim[0][0]:CorrectedUpperLim[0][0],:]

        fig,ax = plt.subplots()
        smesh = ax.pcolormesh(channels,Time,filtered, vmin = Smin, vmax = Smax, cmap = 'seismic',shading='nearest')
        plt.xlabel('channels')
        plt.ylabel('datetime')
        #ax.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f')) 
        #ax.set_ylim(YLowerLim, YUpperLim)
        bar = fig.colorbar(smesh,ax=ax)
        bar.set_label("phase shift (radians)")
    if show==True:
        plt.show()
    return


def PlotEvent(Event,Catalogue,Dataset,Sensitivity=.05,Lowpass = None,Highpass = None,ShowTrig=False,ShowPick=False,Type=None, savefigs = False, folder=None,doseconds=True): #Plots an event from a catalogue.
    """
    Plots an event from the catalogue using its range.

    Parameters:
    - Event
    - Catalogue
    - Dataset
    - Sensitivity: The sensitivity (in radians)
    - Lowpass: for Lowpass filter (Hz)
    - Highpass: for Highpass filter (Hz)
    - ShowTrig: Show the triggers?
    - ShowPick: Show the automatic picks? (CURRENTLY DEPRECATED)
    - Type: Positives, Negatives, All?
    - savefigs: should figures be saved in the given path to folder?
    - folder: path to folder to save figures to
    - doseconds: If true, then the time axis is in seconds, if false it's datetime. 

    Returns nothing

    """
    with h5.File(Dataset,'r') as PulledFile:
        Pulserate = PulledFile['Data']['RootInfo']['Acquisition'].attrs['PulseRate']

        if Lowpass == None:
            Lowpass = PulledFile['Catalogues'][Catalogue].attrs['Lowpass']
        if Highpass == None:
            Highpass = PulledFile['Catalogues'][Catalogue].attrs['Highpass']        


        MyEvent = PulledFile['Catalogues'][Catalogue][f'Event {Event}']
        Section = PulledFile['Catalogues'][Catalogue][f'Event {Event}'].attrs['Section']
        Range = PulledFile['Catalogues'][Catalogue][f'Event {Event}'].attrs['Range']
        time = PulledFile['Data']['TimeData'][f'Section {Section}']
        Timeinit = sintela_to_datetime(time[0])
        doplot = None

        if Type == None:
            doplot = True
        elif Type == 'positive':
            if PulledFile['Catalogues'][Catalogue][f'Event {Event}'].attrs['Error'] == False:
                doplot = True
            else:
                doplot = False
        elif Type == 'negative':
            if PulledFile['Catalogues'][Catalogue][f'Event {Event}'].attrs['Error'] == True:
                doplot = True
            else:
                doplot = False
        else:
            print("Nonvalid Type Parameter")
        if doplot == True:
            Detect(Section,Dataset,Sensitivity = Sensitivity,Lowpass = Lowpass,Highpass = Highpass,YLowerLim=(Range[0]/Pulserate),YUpperLim=(Range[1]/Pulserate),show=False,doseconds=doseconds)
            if ShowTrig==True:
                MyTrig = MyEvent['Triggers']
                MyTrig = MyTrig[:,:]
                plt.scatter(MyTrig[:,0],MyTrig[:,2]/Pulserate,s=7, alpha=.5)
                plt.scatter(MyTrig[:,0],MyTrig[:,1]/Pulserate,s=7, alpha=.5)
            if ShowPick==True:
                MyPick = MyEvent['P_waves']
                MyPick = MyPick[:,:]
                plt.scatter(MyPick[:,0],MyPick[:,1]/Pulserate,s=7, alpha=1)
            fig = plt.gcf()
            plt.title(f"Event {Event} in section {Section}, at {Timeinit}")
            #plt.show()
            if savefigs == True:
                os.makedirs(folder, exist_ok=True) 
                save_path = os.path.join(folder, f"Event_{Event}.png")
                plt.savefig(save_path)


PointsMaster = []
PlottedPoints = []
Cont = True

#First, set the initial data.
Dataset =  "/home/nyandell/Catalogue_Eastwind" #input("Enter File Path:")
Catalogue = "1-50 band sensitive search"#input("Enter Catalogue:")
Event = input("Enter Event Range:")
Type = input("positives/negatives/all?:")
#Event = list(map(int, Notyettuple.split(',')))
#for u in  Event:
#with h5.File(f'{Dataset}','r') as PulledFile:
    #CurrentGraph = PulledFile['Catalogues'][f'{Catalogue}']['Eventlist'][f'Event {Event}']
    #PlotEvent(Event,Catalogue,File)
if Event == 'all':
    with h5.File(Dataset,'r') as PulledFile:
        Totalnum = PulledFile['Catalogues'][Catalogue].attrs['Total']
        Event = (0,Totalnum)
else:
    temptup = Event
    temptup = temptup.strip("()")           # Remove parentheses
    parts = temptup.split(",")        # Split into elements
    Event = tuple(int(x) for x in parts)  # Convert to tuple of ints
for i in range(Event[0],Event[1]):
    tempcheck = False
    if Type != "all":
        if Type == "positives":
            Type = False
        elif Type == "negatives":
            Type = True
        with h5.File(Dataset,'r') as PulledFile:
            if PulledFile['Catalogues'][Catalogue][f'Event {i}'].attrs['Error']==Type:
                tempcheck = True
            else:
                None
        if tempcheck == True:
            print(f"pwaving {i}")
            getpwaves(i,Catalogue,Dataset,Sensitivity = .05) #I have this purposefully to avoid having the dataset already open, it's good to close it before calling the other function.
        else:
            print("skipping")
    else:
        getpwaves(i,Catalogue,Dataset,Sensitivity = .05)
    print(PointsMaster)
    #PointsMaster = [int(np.round(x)) for x in PointsMaster]

    with h5.File(Dataset,'a') as PulledFile:
        EventGroup = PulledFile['Catalogues'][Catalogue][f'Event {i}']
        if "P_waves" in EventGroup: #FIX
            del EventGroup['P_waves']
        EventGroup.create_dataset("P_waves", data=PointsMaster)
        PointsMaster = []
        PlottedPoints = []
        Cont = True




    #Do Ppicker now?
    #save events as an array, then with a 'a' file read append them to to h5 under each respective event.

#Pull the data & create the graph, then save a 1d array of p wave pick tuples, (channel & time).

#So we have PointsMaster, NOTE IT IS A series of tuples of FLOATs. We should save this as a dataset in the event group. Then, tomorrow talk to JM about getting the funciton set up. 






