'''This file should be put under Aimsun API: AAPI folder. '''
from AAPI import *
import sys
SITEPACKAGES = "/usr/local/lib/python2.7/site-packages"
if SITEPACKAGES not in sys.path:
    sys.path.append(SITEPACKAGES)

from random import randint
import numpy as np
import networkx as nx
id=0
i=0
path=[]
origins = []
destinations = []
passenger = 10 # number of passengers
clock=0
clock2=0
numberofpassenger=0
stoptime = 0
firststop=True
stopping=False
pickuptime=[]
dropofftime=[]
Passengerlist=[]
Taxilist={}
CARS = 30
accumulation=0
numbersinsection=0
numbersinjuction=0
astring=0
counter=0



class Passenger:
    passengerCount = 0
    '''
    All instance of Passenger need to have the following options.
    '''
    def __init__(self, origin, destination, take, appeartime, pickuptime, dropofftime, distance_travelled):
        self.origin = origin
        self.destination = destination
        self.take = take
        self.appeartime = appeartime
        self.pickuptime = pickuptime
        self.dropofftime = dropofftime
        self.distance_travelled=distance_travelled
        Passenger.passengerCount += 1

    def udate_pickup(self, pickuptime):
        self.pickuptime = pickuptime

    def get_time(self):
        return


class Taxi:
    taxiCount = 0

    def __init__(self,occupy, passengerid,origin,destination, path,stoptime,firststop,stopping, occupied_distance, empty_distance, occupied_time,sectionlength,midsection,noofpath,i,droptime):
        self.occupy = occupy
        self.passengerid = passengerid
        self.origin=origin
        self.destination=destination
        self.path=path
        self.stoptime=stoptime
        self.firststop=firststop
        self.stopping=stopping
        self.occupied_distance = occupied_distance
        self.empty_distance = empty_distance
        self.occupied_time = occupied_time
        self.sectionlength=sectionlength
        self.midsection=midsection
        #self.noofpath=noofpath
        self.i=i
        self.droptime=droptime
        self.vacant_time=[]
        self.vacant_distance=[]
        self.currentPathLength = 0
        Taxi.taxiCount += 1 #counter increase when generate new taxi instance.


#SectionNumber=515

#Using toolbox called netowrkx, which is a sophiscated graph tool box.

NG = nx.DiGraph()
#NG is a directed graph, as sections are single direction only.

'''
TODO: add weighting of edges(sections) and apply dijkstra.
1. write script in Aimsun to extract length information as weighting of the graph. 
2. apply length weighting in the graph construction (add_edge)
'''
f = open("network_withlength_boxhill.txt") #netowrk connectivity data input, from Aimsun script.


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

intsecIDs = list(map(int, list(G.nodes)))#in case of usage.

print(G.nodes)
print(G.edges)



def AAPILoad():
    '''
    It is called when the module is loaded by Aimsun.
    Optional:
    '''
    AKIPrintString("Load...-shows this module is entered")
    #print(list(G.nodes))
    return 0


def AAPIInit():
    '''
    It is called when Aimsun starts the simulation and can be used to initialise whatever the module needs.
    '''
    global passenger,Passengerlist,Taxilist,CARS

    import random

    '''
    Innitial passenger generation
    '''
    for z in range(0, passenger):

        start = random.choice(secIDs)
        while (True):
            end = random.choice(secIDs)
            if start != end and end in innerSec.keys():#make sure the start & end both be in
                break
        Passengerlist.insert(z, Passenger(start, end, 0, 0, 0, 0, 0))

    #This section is entered just once.
    return 0


def AAPIManage(time, timeSta, timeTrans, acycle):
    #print('Current Manage step -------------------------------------------------------------------')
    import traceback, random
    import networkx.algorithms as na
    try:
        global clock, numberofpassenger, Passengerlist, Taxilist, CARS, clock2, accumulation, numbersinsection, numbersinjunction, astring
        global counter

        numberofpassenger = len(Passengerlist)

        wait = 0
        for s in range(0, numberofpassenger):
            if Passengerlist[s].take == 0:
                wait = wait + 1
        print ('Number of passenger waiting: ', wait)

        if clock == 90: #introduces new passenger every 90 sec.
            #print('CLOCK IS 90!!!!!!!')

            start = random.choice(secIDs)
            while (True):
                end = random.choice(secIDs)
                if start != end:
                    break
            appeartime = AKIGetCurrentSimulationTime()  # get current time.
            Passengerlist.append(Passenger(start, end, 0, appeartime, 0, 0, 0))
            clock = 0

        else:
            clock = clock + 1
        #print clock


        #print('We have ----------------------- Taxi.taxiCount:',Taxi.taxiCount)
        for c in Taxilist:


            if Taxilist[c].path==0:
                '''
                Make this vacant taxi go to the passenger.
                '''
                InfVeh = AKIVehTrackedGetInf(c)
                '''
                AKIVehTrackedGetInf: Read the informaiton of a tracked vehicle.
                '''
                Taxilist[c].origin = str(InfVeh.idSection)
                Taxilist[c].destination = str(Passengerlist[Taxilist[c].passengerid].origin)
                #print('Taxi origin:', Taxilist[c].origin)
                #print('Taxi destination:', Taxilist[c].destination)
                Taxilist[c].path=na.dijkstra_path(G, Taxilist[c].origin , Taxilist[c].destination)

                Taxilist[c].currentPathLength = na.dijkstra_path_length(G, Taxilist[c].origin , Taxilist[c].destination)

                Taxilist[c].vacant_distance.append(Taxilist[c].currentPathLength)


            '''
            idSection = 32766 because it exceeded visible network. 
            '''

            #print('Taxi',c,' has Current Section ID', InfVeh.idSection, 'its next step is', weirdValue)

            AKIVehTrackedModifyNextSection(c, int(Taxilist[c].path[Taxilist[c].i])) #Vechicle id starting from 1 instead of 0

            #get the information of the vehicle again.
            InfVeh = AKIVehTrackedGetInf(c)

            if InfVeh.idSection == int(Taxilist[c].path[Taxilist[c].i]):

                #Taxilist[c].noofpath=len(Taxilist[c].path)  #length of all steps

                if Taxilist[c].i < len(Taxilist[c].path) - 1:    #if number of steps < all steps

                    Taxilist[c].i = Taxilist[c].i +1    #move on to next step. This is incremented every for step.
                    AKIVehTrackedModifyNextSection(c, int(Taxilist[c].path[Taxilist[c].i]))   #move on to next step



            InfVeh = AKIVehTrackedGetInf(c)

            '''
            Passenger pick up.
            '''
            if InfVeh.idSection == int(Taxilist[c].destination):

                Taxilist[c].i = 0


                A2KSectionInf = AKIInfNetGetSectionANGInf(int(Taxilist[c].destination))
                Taxilist[c].sectionlength = A2KSectionInf.length
                Taxilist[c].midsection=Taxilist[c].sectionlength*0.5


                if Taxilist[c].midsection-10<InfVeh.distance2End<Taxilist[c].midsection+10:

                    Taxilist[c].stopping=True#stop it on the midsection, as if the passenger emerges at midsection.


                if Taxilist[c].stopping==True:

                    if Taxilist[c].firststop==True: #only record the first stopping time-- otherwise this value could be re-write up to 5sec.

                        Taxilist[c].stoptime = AKIGetCurrentSimulationTime() #current time.
                        Taxilist[c].firststop = False
                    AKIVehTrackedModifySpeed(c, 0) #temporary stop



                print ('Taxi ',c, "has its passenger ", Taxilist[c].passengerid, " now on trip to ", Passengerlist[Taxilist[c].passengerid].destination)  # have taken the passenger, then send the passenger to his destination

                if time - Taxilist[c].stoptime > 5 and Taxilist[c].stopping==True: #if taxi restarts.
                    #current senario: taxi is stopped.
                    #Decide if it is a drop off or pick up senario.

                    Taxilist[c].stopping=False
                    Taxilist[c].firststop=True #change firststop back until next time the taxi stops.
                    counter = counter + 1

                    print('Taxi',c,'should Passenger that has origin ',Passengerlist[Taxilist[c].passengerid].origin, 'and destination',Passengerlist[Taxilist[c].passengerid].destination)

                    '''
                    A searching and pickup senario: taxi reaching for passenger: taxi's destination = current passenger's origin.
                    A taxi sending passenger reaching its destination : taxi's destinations = current passenger's destination.
                    '''
                    Pickup = Taxilist[c].destination==Passengerlist[Taxilist[c].passengerid].origin
                    Dropoff = Taxilist[c].destination==Passengerlist[Taxilist[c].passengerid].destination

                    if Pickup:

                        Passengerlist[Taxilist[c].passengerid].pickuptime = Taxilist[c].stoptime
                        #Taxilist[c].noofpath=len(Taxilist[c].path)

                        Taxilist[c].empty_distance=Taxilist[c].currentPathLength
                        '''
                        vacant_time, a list. 
                        =: the taxi's drop off time of the LAST passenger) - (the taxi's pick up time of the NEXT passenger)
                        '''
                        Taxilist[c].vacant_time.append(Passengerlist[Taxilist[c].passengerid].pickuptime - Taxilist[c].droptime)
                        Taxilist[c].occupy = 1
                        Taxilist[c].origin=Passengerlist[Taxilist[c].passengerid].origin
                        Taxilist[c].destination=Passengerlist[Taxilist[c].passengerid].destination

                        Taxilist[c].path = na.dijkstra_path(G, str(Taxilist[c].origin), str(Taxilist[c].destination))

                        print ('Taxi ',c,"has picked up", Taxilist[c].passengerid, "on desination to", Taxilist[c].destination) # have arrived the destination of the passenger and then go to take the next passenger

                    elif Dropoff:

                        Passengerlist[Taxilist[c].passengerid].dropofftime = Taxilist[c].stoptime #current time
                        Taxilist[c].droptime = Taxilist[c].stoptime #
                        #Taxilist[c].noofpath=len(Taxilist[c].path)
                        Taxilist[c].occupied_distance=Taxilist[c].occupied_distance + Taxilist[c].currentPathLength
                        Passengerlist[Taxilist[c].passengerid].distance_travelled=Taxilist[c].currentPathLength
                        Taxilist[c].occupy=0 #becomes vacant

                        Taxilist[c].occupied_time=Taxilist[c].occupied_time + (Passengerlist[Taxilist[c].passengerid].dropofftime - Passengerlist[Taxilist[c].passengerid].pickuptime)
                        #accummulate occupied time.

                        def SequentialPickup():
                            for d in range(0, numberofpassenger):
                                if Passengerlist[d].take == 0:  # subsequently take on the next waiting passenger on the given list.
                                    Taxilist[c].passengerid = d
                                    Passengerlist[d].take = 1
                                    break

                        def DistancePriorityPickup():

                            steps = []
                            # a tuple list storing (no.of steps needed to get passenger, passenger id )

                            for d in range(0, numberofpassenger):
                                if Passengerlist[d].take == 0:
                                    steps.append((na.dijkstra_path_length(G,Taxilist[c].destination,Passengerlist[d].origin),d))

                            steps = sorted(steps, key=lambda x: (x[0], x[1]))
                            # sorted by : firstly, smallest steps to get,
                            # secondly passenger id (if steps equal, first come first serve)
                            if len(steps)>0:
                                d = steps[0][1]
                                Taxilist[c].passengerid = d
                                Passengerlist[d].take = 1


                        #SequentialPickup()
                        DistancePriorityPickup()
                        Taxilist[c].origin=Taxilist[c].destination #since after drop off, taxi's place is actually its destination. Hence new origin = its currentplace.
                        Taxilist[c].destination=Passengerlist[Taxilist[c].passengerid].origin

                        if Taxilist[c].origin==Taxilist[c].destination: #if the taxi happen to be on the same section as the passenger
                            Passengerlist[Taxilist[c].passengerid].pickuptime = Taxilist[c].stoptime
                            Taxilist[c].vacant_time.append(0)
                            Taxilist[c].vacant_distance.append(0)
                            Taxilist[c].destination=Passengerlist[Taxilist[c].passengerid].destination
                            Taxilist[c].path = na.dijkstra_path(G, str(Taxilist[c].origin),str(Taxilist[c].destination)) #go to passenger's destination
                        else:
                            Taxilist[c].path = na.dijkstra_path(G, str(Taxilist[c].origin), str(Taxilist[c].destination)) #go to passenger's origin
                            Taxilist[c].vacant_distance.append(Taxilist[c].currentPathLength)


    except Exception:
        traceback.print_exc()

    return 0


def AAPIPostManage(time, timeSta, timeTrans, acycle):

            #rep = AKIVehTrackedModifyNextSection(10, idSection)
    return 0


def AAPIFinish():
    import traceback, random
    try:
        global numberofpassenger,CARS,counter
        fileName = 'statistics_test.txt'
        file = open(fileName, "w")
        file.write('Taxi ID\t Occupied distance\t Empty distance\t Occupied time\t Vacant time\t Vacant distance\n')

        for f in Taxilist:
            file.write(str(f))
            file.write(',')
            file.write(str(Taxilist[f].occupied_distance))
            file.write(',')
            file.write(str(Taxilist[f].empty_distance))
            file.write(',')
            file.write(str(Taxilist[f].occupied_time))
            file.write('\n')
            file.write('Vacant time\t Vacant distance\n')
            for g in range(0,len(Taxilist[f].vacant_time)):
                file.write(str(Taxilist[f].vacant_time[g]))
                file.write(',')
                file.write(str(Taxilist[f].vacant_distance[g]))
                file.write('\n')




        file.write('Passenger ID\t Appear time\t Pickup time\t Dropoff time\t Distance travelled\n')
        for e in range(0,numberofpassenger):
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
        # file.write(str(counter))
        # file.write('\n')
        # file.write(str(len(vacant_time)))
        # file.write('\n')
        # file.write(str(len(vacant_distance)))


        file.close()


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
        global CARS
        #and str(idsection) in secIDs
        if len(Taxilist)<=CARS: #only introduce tracked vehicle when it enters connected G.

            AKIVehSetAsTracked(idveh)
            InfVeh = AKIVehTrackedGetInf(idveh)

            if str(InfVeh.idSection) not in list(G.nodes):
                #print('Taxi coming from non SCP, have to throw it away')
                AKIVehSetAsNoTracked(idveh)
            else:
                #print ("Car", idveh, "is tracked")


                #occupy, passengerid, origin, destination, path, stoptime, firststop, stopping, occupied_distance, empty_distance, occupied_time, sectionlength, midsection, noofpath, i, droptime

                Taxi_current_pos = str(InfVeh.idSection)
                #print('Current IDsection,', Taxi_current_pos)
                steps = []
                # a tuple list storing (no.of steps needed to get passenger, passenger id )

                for d in range(0, numberofpassenger):
                    if Passengerlist[d].take == 0:

                        steps.append((na.dijkstra_path_length(G, Taxi_current_pos, Passengerlist[d].origin), d))

                steps = sorted(steps, key=lambda x: (x[0], x[1]))
                # sorted by : firstly, smallest steps to get,
                # secondly passenger id (if steps equal, first come first serve)
                if len(steps) > 0:
                    d = steps[0][1]
                    Taxilist[idveh] = Taxi(0, 0, 0, 0, 0, 0, True, False, 0, 0, 0, 0, 0, 0, 0, 0)
                    Taxilist[idveh].passengerid = d
                    Passengerlist[d].take = 1
                    print (idveh, "got passenger", d)


                else:
                    AKIVehSetAsNoTracked(idveh)

                #for b in range(0, passenger):
                    #if Passengerlist[b].take == 0:

                        #Taxilist[idveh].passengerid = b
                        #Passengerlist[b].take = 1
                        #print (idveh,"got passenger", b)
                        #break


    except Exception:
        traceback.print_exc()

    return 0


def AAPIExitVehicle(idveh, idsection):
    return 0


def AAPIEnterPedestrian(idPedestrian, originCentroid):
    return 0


def AAPIExitPedestrian(idPedestrian, destinationCentroid):
    return 0


def AAPIEnterVehicleSection(idveh, idsection, atime):
    return 0


def AAPIExitVehicleSection(idveh, idsection, atime):
    return 0
