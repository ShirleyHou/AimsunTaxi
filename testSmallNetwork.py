'''This file should be put under Aimsun API: AAPI folder. '''
from AAPI import *
import sys
print("Your python is at: ", sys.path)
SITEPACKAGES = "/usr/local/lib/python2.7/site-packages"
if SITEPACKAGES not in sys.path:
    sys.path.append(SITEPACKAGES)


import numpy as np
import networkx as nx

clock = 0
testID = 0
id=0
i=0
path=[]
origins = []
destinations = []
firststop=True
stopping=False
stoptime = 0



'''
Parameter you can change for observation.

DiscreteInterval : the interval of sample time. Currently set to 2 minutes
sinscale : to managing the variation of vacant/waiting passenger. smaller sinscale corresponds to quicker variation rate (not desirable) 
passenger: initial passenger number
CARS: initial taxi number
'''
DiscreteInterval = 120
sinscale = 400
passenger = 30
CARS = 30


'''
Information storage
'''
Passengerlist=[]
Taxilist={}
#meeting function
meeting = []
meetingCount = 0
waitAccumulation = 0
vacantAccumulation = 0
vacantTimeSteps = []
waitingTimeSteps = []
#MFD
accumulation=0
accumulations=[]
flow=0
flows=[]
completions=[]
completion=0
#netowrk/graph infomtion
totallength=0
nbsections=0
nbjunctions=0
sectionid=[]
junctionid=[]



class Passenger:
    passengerCount = 0
    '''
    All instance of Passenger need to have the following options.
    '''
    def __init__(self, origin, destination, take, assigned, appeartime, pickuptime, dropofftime, distance_travelled):
        self.origin = origin
        self.destination = destination
        self.take = take
        self.assigned = assigned
        self.appeartime = appeartime
        self.pickuptime = pickuptime
        self.dropofftime = dropofftime
        self.distance_travelled=distance_travelled
        Passenger.passengerCount += 1


class Taxi:
    taxiCount = 0

    def __init__(self,occupy, passengerid,origin,destination, path,stoptime,firststop,stopping, sectionlength,midsection,i):
        self.occupy = occupy
        self.passengerid = passengerid
        self.origin=origin
        self.destination=destination
        self.path=path
        self.stoptime=stoptime
        self.firststop=firststop
        self.stopping=stopping
        #self.occupied_distance = occupied_distance
        #self.empty_distance = empty_distance
        #self.occupied_time = occupied_time
        self.sectionlength=sectionlength
        self.midsection=midsection
        #self.noofpath=noofpath
        self.speedAccumulation=0
        self.i=i
        #self.droptime=droptime
        #self.vacant_time=[]
        #self.vacant_distance=[]
        self.currentPathLength = 0
        self.completedPassenger = []
        Taxi.taxiCount += 1 #counter increase when generate new taxi instance.


#Using toolbox called netowrkx, which is a sophiscated graph tool box.

NG = nx.DiGraph()
#NG is a directed graph, as sections are single direction only.


f = open("network_withlength.txt") #netowrk connectivity data input, from Aimsun script.

innerSec = {}
outSec = {}
inSec = {}
secLength = {}
'''
new: a list of all sections (Edges) that links Nodes. 
new[n][0]=ID, new[n][1]=Origin Node, new[n][2]=Destination Node.
Nodes could be demands origins/destinations 
'''

for line in f.readlines()[1:]:
    temp1 = line.strip('\n')
    temp2 = temp1.split('\t')
    secID = temp2[0]
    section_Length = temp2[1]
    secLength[secID] = float(section_Length)
    oNode = temp2[2]
    dNode = temp2[3]
    if oNode[0]=='X' and dNode[0]!='X': #exclude all centroids.
        inSec[secID]= [oNode, dNode]
    elif oNode[0]!='X' and dNode[0]!='X':
        innerSec[secID] = [oNode, dNode]

    else:
        outSec[secID] = [oNode, dNode]
f.close()

NG.add_nodes_from([item[0] for item in innerSec.keys()]) #add all section as nodes.

for x in innerSec.keys():
    for y in innerSec.keys():
        if innerSec[x][1] == innerSec[y][0] and innerSec[x][0] != innerSec[y][1]:
            # try to find reachable section from this section. this.destination == others.origin --> these two sections are connected.
            # if new[x][1] != new[y][2] and (new[x][1][1:3] != new[y][2][1:3]):
            # this.origin != other.destination: just to make sure they are not same one in reverse.
            mid2mid_length = (secLength[x] + secLength[y]) / 2
            NG.add_edge(x,y,weight = mid2mid_length)
# Create a graph given in the above diagram

G = max(nx.strongly_connected_component_subgraphs(NG), key=len)
#only wants the largest strongly component in our Graph. Use G from now on instead of NG.
secIDs = list(G.nodes) #secID represents strongly connect part IDs. do not put this line after the next for loop.
secIDsOrigins = [innerSec[x][0] for x in secIDs]


for x in inSec.keys():  # exclude title: ['Section ID', ' Origin Node', ' Destination Node']
    for y in range(0,len(secIDs)):
        dNode = inSec[x][1]
        oNode = secIDsOrigins[y]

        if dNode == oNode:
            # try to find reachable section from this section. this.destination == others.origin --> these two sections are connected.
            # if new[x][1] != new[y][2] and (new[x][1][1:3] != new[y][2][1:3]):
            # this.origin != other.destination: just to make sure they are not same one in reverse.
            G.add_node(x)
            mid2mid_length = (secLength[x] + secLength[secIDs[y]]) / 2
            G.add_edge(x, secIDs[y], weight=mid2mid_length)


#now the graph includes not only strongly connected parts, but also ingoing centroid sections that connected to the SCP (where Cars can enter hence be tracked)
#Make sure: any(G.nodes) in outSec.keys() == False

def AAPILoad():
    '''
    It is called when the module is loaded by Aimsun.
    '''
    #print(list(G.nodes))
    TaxiStats = '/Users/shirley/TaxiResults/Taxi_{}_{}.txt'.format(str(ANGConnGetReplicationId()), testID)
    TaxiAveSpeed = '/Users/shirley/TaxiResults/TaxiAveSpeed_{}_{}.txt'.format(str(ANGConnGetReplicationId()), testID)
    PassengerStats = '/Users/shirley/TaxiResults/Passenger_{}_{}.txt'.format(str(ANGConnGetReplicationId()), testID)
    MeetingStats = '/Users/shirley/TaxiResults/meeting_{}_{}.txt'.format(str(ANGConnGetReplicationId()), testID)
    TimeSteps = '/Users/shirley/TaxiResults/TimeSteps_{}_{}.txt'.format(str(ANGConnGetReplicationId()), testID)

    '''
    Refresh all existing files
    '''
    open(TaxiStats,'w').close()
    open(TaxiAveSpeed, 'w').close()
    open(PassengerStats, 'w').close()
    open(MeetingStats, 'w').close()
    open(TimeSteps,'w').close()
    return 0


def AAPIInit():
    '''
    It is called when Aimsun starts the simulation and can be used to initialise whatever the module needs.
    '''

    '''
    Getting ready for the MFD
    We need the total length of network.
    Production/Output = sum(flow*section_length)/sum(section_length)
    '''
    global passenger,Passengerlist,Taxilist,CARS
    global nbsections, sectionid, nbjunctions
    #sectionid: list of sections.

    nbsections = AKIInfNetNbSectionsANG() #read the number of sections in the entire network.
    for a in range(0, nbsections):
        sectionid.append(AKIInfNetGetSectionANGId(a)) #get section id by iterating over section id list.

    nbjunctions = AKIInfNetNbJunctions() #read the number of junctions in the entire network

    for b in range(0, nbjunctions - 1):
        junctionid.append(AKIInfNetGetJunctionId(b)) #similarly

    global totallength

    for id in sectionid: #iterate over all section id
        A2KSectionInf = AKIInfNetGetSectionANGInf(id) #use id to extract information of this section
        totallength = totallength + A2KSectionInf.length #calculate total network id.



    '''
        Innitial passenger generation: when program starts, automaticly generates a given number of passenger. 
    '''
    print('Connected network section id:', secIDs)
    print('Connected inner section id:', innerSec.keys())
    import random
    #Passengerlist.insert(0, Passenger(0, end, 0, 0, 0, 0, 0, 0))
    for z in range(0, passenger):

        start = random.choice(secIDs)
        while (True):
            end = random.choice(secIDs)
            if start != end and end in innerSec.keys():#make sure the End has to be within innerSec.keys(), or the taxi won't be able to come back.
                break
        #origin, destination, take, assigned, appeartime, pickuptime, dropofftime, distance_travelled
        Passengerlist.insert(z, Passenger(start, end, 0, 0, 0, 0, 0, 0))

    #This section is entered just once.
    return 0


def AAPIManage(time, timeSta, timeTrans, acycle):

    import traceback, random
    import networkx.algorithms as na
    global clock
    try:
        '''
        Taxi Pickup & Drop off management
        '''

        global Passengerlist, Taxilist, CARS, meeting, \
            meetingCount, vacant, waitAccumulation, vacantAccumulation, vacantTaxi, waitingTimeSteps, vacantTimeSteps, clock

        clock += 1  # this steps

        for p in range(1,len(Passengerlist)):
            if Passengerlist[p] == None:
                continue
            #print('Passenger', p, 'Has origin', Passengerlist[p].origin, 'destination', Passengerlist[p].destination, 'Is taken?', Passengerlist[p].take, 'Is assigned', Passengerlist[p].assigned)


        def DistancePriorityPickup(c, meetingCount):
            '''
            param c: Taxi id.
            if success, taxi will have non 0 passengerid, path, i=0
            '''

            InfVeh = AKIVehTrackedGetInf(c)
            currentpos = str(InfVeh.idSection)
            steps = []
            # a tuple list storing (no.of steps needed to get passenger, passenger id )

            for d in range(1, len(Passengerlist)):
                if Passengerlist[d]==None:
                    continue
                if Passengerlist[d].assigned == 0:
                    path = na.dijkstra_path_length(G, currentpos, Passengerlist[d].origin)
                    steps.append((path, d))

            steps = sorted(steps, key=lambda x: (x[0], x[1]))
            # sorted by : firstly, smallest steps to get,
            # secondly passenger id (if steps equal, first come first serve)
            if len(steps) > 0:
                d = steps[0][1]
                Taxilist[c].passengerid = d
                Passengerlist[d].assigned = 1

                Taxilist[c].origin = currentpos# since after drop off, taxi's place is actually its destination. Hence new origin = its currentplace.
                Taxilist[c].destination = Passengerlist[Taxilist[c].passengerid].origin

                if Taxilist[c].origin == Taxilist[
                    c].destination:  # if the taxi happen to be on the same section as the passenger
                    Passengerlist[Taxilist[c].passengerid].pickuptime = Taxilist[c].stoptime
                    Taxilist[c].destination = Passengerlist[Taxilist[c].passengerid].destination
                    Taxilist[c].occupy = 1
                    meetingCount += 1

                    Passengerlist[Taxilist[c].passengerid].take = 1
                    Taxilist[c].path = na.dijkstra_path(G, str(Taxilist[c].origin), str(
                        Taxilist[c].destination))  # go to passenger's destination
                    Taxilist[c].i = 0
                else:
                    Taxilist[c].path = na.dijkstra_path(G, str(Taxilist[c].origin), str(
                        Taxilist[c].destination))  # go to passenger's origin
                    Taxilist[c].i = 0

            else:
                Taxilist[c].passengerid = 0
                Taxilist[c].path = []
                Taxilist[c].origin = 0
                Taxilist[c].destination = 0
                print(
                    '................................Currently no waiting passenger to assign for taxi :',
                    c)


        def removeTaxi(c, meetingCount):
            '''
            Param: c is the taxi idveh
            return 0 if successful. return 1 if not successful
            '''
            if Taxilist[c] == None:
                print('Taxi', c, 'is already deleted!', Taxilist[c].passengerid)
                return 1
            if Taxilist[c].passengerid!=0:
                #sometimes you really can't control it when it's taking a turn........This is logically incorrect, but rarely happens,  due to Aimsun
                if Passengerlist[Taxilist[c].passengerid].take ==1:
                    #But at least we know if the passenger is taken, meeting is successful.
                    Passengerlist[Taxilist[c].passengerid]=None
                else:
                    Passengerlist[Taxilist[c].passengerid].assigned = 0


                Taxilist.pop(c, None)
                AKIVehSetAsNoTracked(c)
                print(
                    'Decrease in Taxi Number!--------------------------------------------------------------------------')
                print('Should not delete taxi',c,'! Currently carrying passenger!', Taxilist[c].passengerid)
                Taxilist[c] = None  # discard this taxi.
                return 1

            TaxiAveSpeed = '/Users/shirley/TaxiResults/TaxiAveSpeed_{}_{}.txt'.format(str(ANGConnGetReplicationId()),
                                                                                      testID)
            file = open(TaxiAveSpeed, "a")
            file.write(str(c))
            file.write(',')
            file.write(str(format(Taxilist[c].speedAccumulation/clock, '.2f')))
            file.write(',')
            file.write(str(clock))
            file.write('\n')
            file.close()  # only discard one taxi at a time.

            Taxilist[c] = None #discard this taxi.
            Taxilist.pop(c, None)
            AKIVehSetAsNoTracked(c)
            print('Deleted Taxi',c,'-----------------------------------------------------------------------------------------------------------')
            return 0

        for c in Taxilist.keys():

            if Taxilist[c] == None:
                continue
            InfVeh = AKIVehTrackedGetInf(c)
            print("Taxi", c, "position", InfVeh.idSection, "is currently assigned with", Taxilist[c].passengerid," and Has completed the trip of", Taxilist[c].completedPassenger)



            if len(Taxilist[c].path)!=0:

                #print('Taxi',c, 'has path', Taxilist[c].path,'i',Taxilist[c].i,'next section',Taxilist[c].path[Taxilist[c].i])
                #AKIVehTrackedModifyNextSection(c, int(Taxilist[c].path[Taxilist[c].i]))  # Track vehicle by using its (key) Vechicle id c

                # get the information of the vehicle again.
                # InfVeh = AKIVehTrackedGetInf(c)


                if InfVeh.idSection == -1:
                    pass
                    # if AKIVehTrackedModifyNextSection(c, int(Taxilist[c].path[Taxilist[c].i]))!=0:
                    #     print('Error   1 :   Taxi', c, 'currently on', InfVeh.idSection,'has error modifying turning into the correct next step',
                    #     Taxilist[c].path[Taxilist[c].i])
                #elif Taxilist[c].i != Taxilist[c].path.index(str(InfVeh.idSection))-1:
                    #print('i should be ',Taxilist[c].i, 'and index should be',Taxilist[c].path.index(str(InfVeh.idSection)))
                    #Taxilist[c].i == Taxilist[c].path.index(str(InfVeh.idSection))
                    #print('Error__________________3 :   Taxi', c, 'Currently on', InfVeh.idSection,
                          #' has error modifying to the correct next step',
                          #Taxilist[c].path[Taxilist[c].i])


                elif InfVeh.idSection == int(Taxilist[c].path[Taxilist[c].i]) and Taxilist[c].i < len(
                        Taxilist[c].path) - 1:
                    Taxilist[c].i += 1  # move on to next step. This is incremented every for step.
                    if AKIVehTrackedModifyNextSection(c, int(Taxilist[c].path[Taxilist[c].i]))!=0:
                        print('Error_____________2 :   Taxi', c, 'Currently on', InfVeh.idSection,' has error modifying to the correct next step',
                              Taxilist[c].path[Taxilist[c].i])



                     # move on to the next step

            #InfVeh = AKIVehTrackedGetInf(c)

            Taxilist[c].speedAccumulation += InfVeh.CurrentSpeed
            # Taxilist[c].path == 0 and

            if str(InfVeh.idSection) not in G.nodes() and InfVeh.idSection != -1:
                Passengerlist[Taxilist[c].passengerid].assigned = 0
                AKIVehSetAsNoTracked(c)
                print(
                    "^^^^^^^Taxi", c, " is discarded for wondering out of the graph while not on a node^^^^^^^^^^^^^")
                removeTaxi(c, meetingCount)
                continue

            if (Taxilist[c].passengerid == 0 or len(Taxilist[c].path)==0)and InfVeh.idSection!=-1: #case no customer.

                DistancePriorityPickup(c, meetingCount)


            InfVeh = AKIVehTrackedGetInf(c)
            '''
            Passenger pick up & droppoff management
            '''
            if len(Taxilist[c].path)!=0 and InfVeh.idSection == int(Taxilist[c].path[-1]):
                #print('Car', c, 'is enterrring last step~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                Taxilist[c].i = 0

                A2KSectionInf = AKIInfNetGetSectionANGInf(int(Taxilist[c].path[-1]))
                Taxilist[c].sectionlength = A2KSectionInf.length
                Taxilist[c].midsection = Taxilist[c].sectionlength * 0.5

                if Taxilist[c].midsection -40 < InfVeh.distance2End < Taxilist[c].midsection +40:
                    #print('Car', c, 'should be      stopped!!!!!!!!!!!!!!!---------------------------')
                    Taxilist[c].stopping = True  # stop it on the midsection, as if the passenger emerges at midsection.

                if Taxilist[c].stopping == True:

                    if Taxilist[
                        c].firststop == True:  # only record the first stopping time-- otherwise this value could be re-write up to 5sec.

                        Taxilist[c].stoptime = AKIGetCurrentSimulationTime()  # current time.
                        Taxilist[c].firststop = False
                    AKIVehTrackedModifySpeed(c, 0)  # temporary stop
                    #print('Car', c, 'is stopped!!!!!!!!!!!!!!!---------------------------')

                if clock - Taxilist[c].stoptime > 3 and Taxilist[c].stopping == True:  # if taxi restarts.
                    # current senario: taxi is stopped.
                    # Decide if it is a drop off or pick up senario.

                    Taxilist[c].stopping = False
                    #print('Car', c, 'should go back to movement!!!!!!!!!!!!!!!---------------------------')
                    Taxilist[c].firststop = True  # change firststop back until next time the taxi stops.

                    # counter = counter + 1

                    # print('Taxi',c,'should Passenger that has origin ',Passengerlist[Taxilist[c].passengerid].origin, 'and destination',Passengerlist[Taxilist[c].passengerid].destination)

                    '''
                    A searching and pickup senario: taxi reaching for passenger: taxi's destination = current passenger's origin.
                    A taxi sending passenger reaching its destination : taxi's destinations = current passenger's destination.
                    '''
                    Pickup = (Taxilist[c].path[-1] == Passengerlist[Taxilist[c].passengerid].origin)
                    Dropoff = (Taxilist[c].path[-1] == Passengerlist[Taxilist[c].passengerid].destination)

                    if Pickup:
                        Passengerlist[Taxilist[c].passengerid].take = 1
                        Passengerlist[Taxilist[c].passengerid].pickuptime = Taxilist[c].stoptime

                        # Taxilist[c].empty_distance=Taxilist[c].currentPathLength
                        '''
                        vacant_time, a list. 
                        =: the taxi's drop off time of the LAST passenger) - (the taxi's pick up time of the NEXT passenger)
                        '''
                        # Taxilist[c].vacant_time.append(Passengerlist[Taxilist[c].passengerid].pickuptime - Taxilist[c].droptime)
                        Taxilist[c].occupy = 1
                        Taxilist[c].origin = Passengerlist[Taxilist[c].passengerid].origin
                        Taxilist[c].destination = Passengerlist[Taxilist[c].passengerid].destination

                        Taxilist[c].path = na.dijkstra_path(G, str(Taxilist[c].origin), str(Taxilist[c].destination))

                        print('Taxi ', c, "has picked up", Taxilist[c].passengerid, "on desination to", Taxilist[
                            c].destination)  # have arrived the destination of the passenger and then go to take the next passenger
                        meetingCount += 1
                        Passengerlist[Taxilist[c].passengerid].take = 1

                    elif Dropoff:

                        Passengerlist[Taxilist[c].passengerid].dropofftime = Taxilist[c].stoptime  # current time

                        # Taxilist[c].droptime = Taxilist[c].stoptime #first stop time.
                        # Taxilist[c].occupied_distance=Taxilist[c].occupied_distance + Taxilist[c].currentPathLength
                        Passengerlist[Taxilist[c].passengerid].distance_travelled = Taxilist[c].currentPathLength
                        print('Taxi', c, 'dropped off passenger', Taxilist[c].passengerid,"________________________________")
                        Taxilist[c].completedPassenger.append(Taxilist[c].passengerid)
                        Taxilist[c].occupy = 0  # becomes vacant
                        Taxilist[c].passengerid = 0
                        Taxilist[c].i = 0

                        # Taxilist[c].occupied_time=Taxilist[c].occupied_time + (Passengerlist[Taxilist[c].passengerid].dropofftime - Passengerlist[Taxilist[c].passengerid].pickuptime)
                        # accummulate occupied time.

                        '''
                        After dropping off, this part is our main concern: 
                        what pick up strategy is the best?
                        '''
                        # SequentialPickup()
                        DistancePriorityPickup(c, meetingCount)




        '''
        Define Vacant and Meeting.
        '''
        wait = 0
        for s in range(1, len(Passengerlist)):
            if Passengerlist[s]==None:
                continue
            if Passengerlist[s].take == 0:
                wait = wait + 1
        print ('Number of passenger waiting: ', wait)

        waitingTimeSteps.append(wait)

        '''
        unassigned = 0
        for s in range(1, len(Passengerlist)):
            if Passengerlist[s]==None:
                continue
            if Passengerlist[s].assigned == 0:
                unassigned = unassigned + 1
        #print ('Number of passenger unassigned: ', unassigned)
        '''

        vacant = 0
        for c in Taxilist.keys():
            if Taxilist[c] == None:
                #Taxilist.pop(c,None)
                continue
            elif Taxilist[c].occupy == 0:
                vacant += 1
        print ('Number of vacant taxi: ', vacant)
        vacantTimeSteps.append(vacant)


        waitAccumulation += wait
        vacantAccumulation += vacant
        print("Meeting happened in this interval:", meetingCount)
        '''
        In test small network, no complicated sin distribution is tested. 
        Manages the introducing of new passengers. and the reduction of existing vacant taxis
        '''
        def decision(time, sinscale):
            import random
            return random.random() < np.sin(time / sinscale)


        if clock % 60 == 0: #and decision(clock+100, 200): #introduces new passenger every DI sec.

            start = random.choice(secIDs)
            while (True):
                end = random.choice(secIDs)
                if start != end and end in innerSec.keys():
                    break
            appeartime = AKIGetCurrentSimulationTime()  # get current time.
            Passengerlist.append(Passenger(start, end, 0, 0, appeartime, 0, 0, 0))


        global sinscale
        if (clock % 10 == 0) and decision(clock,sinscale):
            for c in Taxilist.keys():
                if Taxilist[c] == None or Taxilist[c].passengerid != 0:
                    continue
                if (removeTaxi(c, meetingCount)==0):
                    break


        '''
        Manages the calculation of meeting function statistics.
        '''
        '''
                MFD generation
                '''
        global accumulation, flow, flows, accumulations, completion, completions, sectionid, junctionid, totallength, DiscreteInterval

        if clock % DiscreteInterval == 1:
            for id in sectionid:
                estad2 = AKIEstGetParcialStatisticsSection(id, timeSta, 0)

                A2KSectionInf = AKIInfNetGetSectionANGInf(id)

                sectionlength = A2KSectionInf.length

                if (estad2.report == 0):  # default, refer to manual.
                    flow += estad2.Flow * sectionlength
            if flow != 0:
                flows.append(flow / 3600)
                flow = 0
            print('flows:', flows)




        if clock % DiscreteInterval == 0:

            meeting.append([meetingCount, waitAccumulation / DiscreteInterval, vacantAccumulation / DiscreteInterval])
              # flows: a list of normalised production/output over time.
            completions.append(completion) #see exitvehicle
            print('Completionss:', completions)
            completion = 0
            for sectionnumbmer in sectionid:
                numbersinsection = AKIVehStateGetNbVehiclesSection(sectionnumbmer, True) #total number of vehicle on the section
                accumulation = accumulation + numbersinsection #sums all vehicles on all sections.

            for junctionnumber in junctionid:
                numbersinjunction = AKIVehStateGetNbVehiclesJunction(junctionnumber)
                accumulation = accumulation + numbersinjunction #similarly, sums all vehicles on all junctions.



            accumulations.append(accumulation)
            #print(accumulations)
            #print('Accumulations:', accumulations)
            accumulation = 0

            waitAccumulation=0
            vacantAccumulation=0
            meetingCount = 0


    except Exception:
        traceback.print_exc()

    return 0


def AAPIPostManage(time, timeSta, timeTrans, acycle):


    return 0


def AAPIFinish():
    import traceback, random
    try:
        '''
        MFD
        '''
        global accumulations, flows, completions, totallength, testID, clock
        '''
        fileName = '/Users/shirley/TaxiResults/MFD_{}_{}.txt'.format(str(ANGConnGetReplicationId()), testID)
        file = open(fileName, "w")
        file.write('Accumulation\t Flow\t Completion\n')
        nba = len(accumulations)
        nbf = len(flows)
        for a in range(0, nba):
            file.write(str(accumulations[a]))
            file.write(',')
            file.write(str(flows[a]))
            file.write(',')
            file.write(str(completions[a]))
            file.write('\n')

        file.close()
        '''

        '''
        Meeting Function
        '''
        global Passengerlist, Taxilist, CARS

        print('This replication id is:', ANGConnGetReplicationId())

        TaxiStats = '/Users/shirley/TaxiResults/Taxi_{}_{}.txt'.format(str(ANGConnGetReplicationId()),testID)
        TaxiAveSpeed = '/Users/shirley/TaxiResults/TaxiAveSpeed_{}_{}.txt'.format(str(ANGConnGetReplicationId()),testID)
        PassengerStats = '/Users/shirley/TaxiResults/Passenger_{}_{}.txt'.format(str(ANGConnGetReplicationId()),testID)
        MeetingStats = '/Users/shirley/TaxiResults/meeting_{}_{}.txt'.format(str(ANGConnGetReplicationId()),testID)
        TimeSteps = '/Users/shirley/TaxiResults/TimeSteps_{}_{}.txt'.format(str(ANGConnGetReplicationId()),testID)

        file = open(TaxiAveSpeed, "a")
        for f in Taxilist:
            if Taxilist[f] ==None:
                continue
            else:
                file.write(str(f))
                file.write(',')
                file.write(str(Taxilist[f].speedAccumulation/clock))
        file.close()

        file = open(PassengerStats, "w")
        file.write('Passenger ID\t Appear time\t Pickup time\t Dropoff time\t Distance travelled\n')
        for e in range(0,len(Passengerlist)):
            if Passengerlist[e]==None:
                continue
            else:
                file.write(str(e))
                file.write(',')
                file.write(str(Passengerlist[e].appeartime))
                file.write(',')
                file.write(str(Passengerlist[e].pickuptime))
                file.write(',')
                file.write(str(Passengerlist[e].dropofftime))
                file.write(',')
                file.write(str(Passengerlist[e].distance_travelled))
                file.write(',')
                file.write('\n')
        
        file.close()

        file = open(MeetingStats, "w")
        file.write("meetingCount\t wait\t vacant\t Accumulation\t Flow\t Completion\n'")
        print('len(flows)',len(flows))
        print('len(accumulations)', len(accumulations))
        print('len(completions)', len(completions))

        for v in range(0,len(flows)):
            file.write(str(meeting[v][0]))
            file.write(',')
            file.write(str(meeting[v][1]))
            file.write(',')
            file.write(str(meeting[v][2]))
            file.write(',')
            file.write(str(accumulations[v]))
            file.write(',')
            file.write(str(flows[v]))
            file.write(',')
            file.write(str(completions[v]))
            file.write('\n')


        file.close()

        file = open(TimeSteps, "w")
        file.write("Vacant\t Waiting\n")
        for i in range(0,len(vacantTimeSteps)):
            file.write(str(vacantTimeSteps[i])),
            file.write(',')
            file.write(str(waitingTimeSteps[i])),
            file.write('\n')


    except Exception:
        traceback.print_exc()

    finally:
        return 0


def AAPIUnLoad():
    return 0


def AAPIPreRouteChoiceCalculation(time, timeSta):
    return 0


def AAPIEnterVehicle(idveh, idsection):
    #print('Car enters with', idveh)
    import networkx.algorithms as na
    import traceback
    try:
        global CARS, waitingTimeSteps,vacantTimeSteps, clock
        #and str(idsection) in secIDs



        if len(Taxilist) <= CARS or clock % 120==0 : # and not CARcondition : #only introduce tracked vehicle when it enters connected G.

            AKIVehSetAsTracked(idveh)
            InfVeh = AKIVehTrackedGetInf(idveh)

            if str(InfVeh.idSection) not in list(G.nodes):
                #print('Taxi coming from non SCP, have to throw it away')
                AKIVehSetAsNoTracked(idveh)
            else:

                Taxi_current_pos = str(InfVeh.idSection)

                steps = []
                # a tuple list storing (no.of steps needed to get passenger, passenger id )

                for d in range(1, len(Passengerlist)):
                    if Passengerlist[d]==None:
                        continue
                    if Passengerlist[d].assigned == 0:
                        steps.append((na.dijkstra_path_length(G, Taxi_current_pos, Passengerlist[d].origin), d))

                #print(steps)
                if len(steps)==0:
                    Taxilist[idveh] = Taxi(0, 0, 0, 0, 0, 0, True, False, 0, 0, 0)
                    Taxilist[idveh].path = []
                    print(idveh,"initialized, does not have unassigned waiting passenger")

                else:
                    steps = sorted(steps, key=lambda x: (x[0], x[1])) #distance priority pick up
                    # sorted by : firstly, smallest steps to get,
                    # secondly passenger id (if steps equal, first come first serve)
                    if len(steps) > 0:
                        d = steps[0][1]
                        Taxilist[idveh] = Taxi(0, 0, 0, 0, 0, 0, True, False, 0, 0, 0)
                        Taxilist[idveh].passengerid = d
                        Passengerlist[d].assigned = 1
                        Taxilist[idveh].origin = str(InfVeh.idSection)
                        Taxilist[idveh].destination = str(Passengerlist[Taxilist[idveh].passengerid].origin)
                        Taxilist[idveh].path = na.dijkstra_path(G, Taxilist[idveh].origin, Taxilist[idveh].destination)
                        #print(idveh, "is assigned to passenger", d, 'at section', Passengerlist[d].origin, 'with path', Taxilist[idveh].path)


            if idveh not in Taxilist.keys():
                AKIVehSetAsNoTracked(idveh)




    except Exception:
        traceback.print_exc()

    return 0


def AAPIExitVehicle(idveh, idsection):
    global completion
    completion = completion + 1
    return 0


def AAPIEnterPedestrian(idPedestrian, originCentroid):
    return 0


def AAPIExitPedestrian(idPedestrian, destinationCentroid):
    return 0


def AAPIEnterVehicleSection(idveh, idsection, atime):
    return 0


def AAPIExitVehicleSection(idveh, idsection, atime):
    return 0
