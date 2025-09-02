Goals of this Module:

A set of functions that can take in h5 DAS data, quickly create a catalogue given parameters, and then allow methods of plotting & adjusting this catalogue through python with relative ease. I’d like to make this such that even someone fairly inexperienced with python could do so, so lots of handholding (ie globals) that might not be that efficient will be used methinks.

Biggest timesink is the triggering program and manual p-wave selection, faster methods could be done on a later iteration.

---

**GLOBALS**

| currentfile\_NY  | The current h5 File location |
| :---- | :---- |
| currentcatalogue\_NY | The current Catalogue name |
| channel\_locations | The current h5 File’s cable coordinates |

					

---

**Interaction Functions**  
---

**Creating Catalogues**  
---

*DataInit(DASLoc, DASLink, Positionstxt)* 

Creates an h5 file with data from DASLink, specifically in the structure:

- DASLoc: Location of the new h5 File in your computer  
- DASLink: Location of the data located in an h5 file being referenced.  
- Positionstxt: Location of the txt file that contains the physical coordinates of the interrogator & fiber optic cable.

---

*Catalogue\_Classic(CatalogueName,Sections,Low,High,STAn,LTAn,Dataset=currentfile\_NY,TrigOn=2.5,TrigOff=1.5,tdownmax=20, tupevent=60, thr1=5, thr2=10, preset\_len=250, p\_dur=250,loopj=0,loopk=0,loopm=0)*

	Generates a catalogue using the initialized data with the name “CatalogueName” inside the h5 file at {Filename}/Catalogues/{CatalogueName} where CatalogueName is filled with groups, where each group is an individually detected event in the shape:

Initially perform small testruns (visually confirm event, then run until it is reliably detected) to fine tune the parameters, watch for excessive or nonexistent triggers.

- CatalogueName: The name of the Catalogue that is being created.  
- Sections: Desired sections to plot.  
- Low: Lowpass filter  
- High: Highpass filter  
- STAn: The bound of detection.  
- LTAn: The bound of reset.    
- Dataset: Link to the Dataset

Other parameters are:

- Parameters for triggering  
- Loop parameters so a catalogue can be made piecewise rather than all at once (if needed).

---

**Note:** Prior functions will set globals for the file, catalogue, and the coordinates of the cable geometry. Use these functions to set others if you’re not making them:

*setfile(File)*: Sets the global “currentfile\_NY” as string File  
*setcatalogue(Catalogue)*: Sets the global “currentcatalogue\_NY” as string Catalogue  
*setcoords(Positionstxt)*: Sets the global “channel\_locations” as positions of the cable, x,y,z

---

*Detect(Section,Dataset=currentfile\_NY,Sensitivity=.05,Lowpass=1,Highpass=50,YLowerLim=None,YUpperLim=None, doseconds \= True, show=True)*

	Plots a given section of the data, useful for checking events.

- Section: The section to plot  
- Dataset: The file location  
- Sensitivity: The sensitivity (in radians)  
- Lowpass: for Lowpass filter (Hz)  
- Highpass: for Highpass filter (Hz)  
- YLowerLim: Lower limit (s)  
- YUpperLim: Upper limit (s)  
- doseconds: If true, then the time axis is in seconds, if false it's datetime.   
- show: Whether the plotted image should be shown.

---

**Manipulating & Observing Events**

---

*describeevents(Events,Dataset=currentfile\_NY,Catalogue=currentcatalogue\_NY):*

Placeholder function to describe events.

- Events: Tuple of events that dictates the range over which to describe.  
- Dataset: current file  
- Catalogue: current catalogue

---

*PlotEvent(Event,Catalogue=currentcatalogue\_NY,Dataset=currentfile\_NY,Sensitivity=.05,Lowpass \= None,Highpass \= None,ShowTrig=False,ShowPick=False,Type=None, savefigs \= False, folder=None,doseconds=True):* 

Plots a given event using matplotlib, and saves it to a folder if prompted in parameters.

- Event: Event to plot  
- Catalogue: Catalogue to use  
- Dataset: File to reference  
- Sensitivity: The sensitivity (in radians)  
- Lowpass: for Lowpass filter (Hz)  
- Highpass: for Highpass filter (Hz)  
- ShowTrig: Show the triggers?  
- ShowPick: Show the automatic picks? (CURRENTLY DEPRECATED)  
- Type: Positives, Negatives, All?  
- savefigs: should figures be saved in the given path to folder?  
- folder: path to folder to save figures to  
- doseconds: If true, then the time axis is in seconds, if false it's datetime.   
  


---

*categorize(event,string,integer=None,catalogue=currentcatalogue\_NY,data=currentfile\_NY):*

Adds an attribute to an event, allowing to sort events based on manually determined categorizes.

- event: the event to categorize.  
- string: the name of the new attribute.  
- integer: If there's a number associated.  
- catalogue: relevant catalogue.  
- data: relevant file.

---

*change\_event(event,ertype=None,Dataset=currentfile\_NY,Catalogue=currentcatalogue\_NY)*

---

*autochange(Dataset=currentfile\_NY,Catalogue=currentcatalogue\_NY)*

	Only do this after taking Pwave picks, marks any "skipped" events as error (no wave picks taken)  
    

- Dataset: current file  
- Catalogue: current catalogue

---

                     
*totalevents(Dataset=currentfile\_NY,Catalogue=currentcatalogue\_NY)*  
          
	Prints the total number of events  
    

- Dataset: current file  
- Catalogue: current catalogue  
- 

---

*totalpositives(Dataset=currentfile\_NY,Catalogue=currentcatalogue\_NY)*  
     
	Prints the total number of positive events  
    

- Dataset: current file  
- Catalogue: current catalogue

---

*totalnegatives(Dataset=currentfile\_NY,Catalogue=currentcatalogue\_NY)*  
   
Prints the total number of negative events  
    

- Dataset: current file  
- Catalogue: current catalogue

---

**Finding the Origins of Events**  
originfinder(picks, s\_x\_init, s\_y\_init, offset\_init, c\_init, plotit \= False):

---

**Data Processing Functions**  
---

*get\_subsection(Event,Dataset=currentfile\_NY,Catalogue=currentcatalogue\_NY,Sensitivity=.05,Lowpass=1,Highpass=50)*

	Acquires the (manually picked) Pwaves and related data of an event, returning it as Pwaves, Data where Pwaves is an array holding two numpy arrays of channel & datetime, and Data is an array holding each channel for the minute long section the associated event occurs in. *Currently unused*.

---

*sintela\_to\_datetime(sintela\_times):*

	Processes DAS time data into a datetime object

---

*Triggering(Dataset,Section,Low,High,STAn,LTAn,TrigON=3,TrigOFF=2)*

	Generates triggers for a given section, used primarily in the CatalogueClassic function

---

*find\_overlapping\_triggers(all\_trigs, start\_index=0, min\_duration=2)*  
	  
Takes the output of Triggering and determines when triggers are present across adjacent channels, attempting to find common triggering across multiple channels.

---

*group\_triggers\_into\_events(triggers, fs, window=0.2, min\_triggers=50)*	

	Takes the output of find\_overlapping\_triggers and processes it into a list of numpy arrays, each (M,3) in shape with the columns channels, start time, end time)

---

*Variance\_Check(TriggerList, VarianceMin)*

	Evaluates the event list generated by group\_triggers\_into\_events, determining if it is error caused by a “pulse” on a channels in a single chronological instant. It does this by finding the MAD, or Mean Absolute Deviation. This determines the mean deviation of the deviation, trying to determine if there are a great many triggers at a singular time. If this is true, it returns the event as being error.

---

*Overheat\_Check(EventData, Dataset, Catalogue,Section)*

	Evaluates the event list generated by group\_triggers\_into\_events, determining if there is error caused by the overheating of the interrogator, where there are sudden unexpected gaps in recorded data. The function checks if there’s a sudden change in the derivative of the event section’s time data. If this is true, it returns the event as being error.

---

*RangeCalc(eventdata,Pulserate)*

	Calculates the range of the event, providing a tuple (start,stop) time.

---

*AddingPositionData(Dataset,Positionstxt)*

	Used in DataInit, adds the cables position data to the catalogue and makes it a global.

---

**P-wave Picking**

It must be noted that due to server technical issues and some issues with sshing, the p-wave picker currently uses slightly outdated versions of prior functions in a self contained py file, to be run on a computer with a backend that allows interactive matplotlibs.

To pick: Download P-picker.py, run it then input the following parameters when prompted:

- File path  
- Catalogue name  
- Event range tuple:(start,end) can also be “all” for all events.  
- positives/negatives/all

Shift left click to pick points, shift right click to remove them, enter to save and move to the next event. If a false positive appears, just press enter without taking any waves and later run “autochange” to mark all non-pwaved positive events as errors.

---

*originfinder(picks, s\_x\_init, s\_y\_init, offset\_init, c\_init, plotit \= False)*

Finds the origin of an event using wave picks and initial guesses, ensure the parameters are correct for a reasonable answer. Be careful when setting offset\_init, and ensure the x & y guesses are within the set boundaries.  
    

- picks: a 2d array of \[x,y\], x is channel \# y is time in seconds  
- s\_x\_init is: the initial x guess  
- s\_y\_init is: the initial y guess  
- offset\_init: the initial guess of the events time of origin  
- c\_init: the guess of the events wavespeed  
- plotit: determines if the output should be plotted.

