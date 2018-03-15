
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate


#replicationlist = [11147,11148,11149]
def passengerStats(id, testID):
    passengerWaitingTime = []
    passengerTravelTime = []
    passengerDistanceTravelled = []
    #for id in rep:
    passenger = open('/Users/shirley/TaxiResults/Passenger_{}_{}.txt'.format(id, testID))
    for line in passenger.readlines()[1:]:
        line = line.strip('\n')
        line = line.split(',')
        #print(line)
        appear = float(line[1])
        pickup = float(line[2])
        dropoff = float(line[3])
        travelDistance = float(line[4])
        if pickup<=1 or dropoff <=1:
            continue
        passengerWaitingTime.append(int(pickup-appear))
        passengerTravelTime.append(int(dropoff-pickup))
        passengerDistanceTravelled.append(int(travelDistance))

    pwt = np.asarray(passengerWaitingTime)
    ptt = np.asarray(passengerTravelTime)
    pdt = np.asarray(passengerDistanceTravelled)

    plt.figure(1)

    plt.subplot(311)
    plt.title('Large grid model, New taxi is introduced whenever waiting > 1.5*vacant')
    plt.hist(pwt,50,facecolor='g')

    plt.ylabel('Number of Passenger')
    plt.xlabel('Waiting time')

    plt.subplot(312)
    plt.hist(ptt,50,facecolor = 'b')
    plt.ylabel('Number of Passenger')
    plt.xlabel('Travelling time')

    plt.subplot(313)
    plt.hist(pdt,facecolor = 'r')
    plt.ylabel('Number of Passenger')
    plt.xlabel('Travelling Distance')
    #plt.title('Passenger Statistics - Big model with dynamicly introduced taxi', loc = 'left')
    plt.show()




def plotmeeting(repID, testID):
    meet = []
    wait = []
    vac = []
    if type(repID) == int:
        fileName = open('/Users/shirley/TaxiResults/meeting_{}_{}.txt'.format(repID, testID))
        for line in fileName.readlines()[1:]:
            line = line.strip('\n')
            line = line.split(',')

            meet.append(int(line[0]))
            wait.append(int(line[1]))
            vac.append(int(line[2]))
        plt.scatter(vac, wait, c=meet)
        plt.xlabel('vacant vehicle')
        plt.ylabel('waiting passenger')
        plt.colorbar()
        plt.show()
        plt.plot(meet)
        plt.show()

    elif type(repID) == list:
        lenFile = 0
        for id in repID:
            fileName = open('/Users/shirley/TaxiResults/meeting_{}_{}.txt'.format(id, testID))

            for line in fileName.readlines()[1:]:
                line = line.strip('\n')
                line = line.split(',')
                meet.append(int(line[0]))
                wait.append(int(line[1]))
                vac.append(int(line[2]))
            lenFile = len(fileName.readlines()[1:])
            fileName.close()
        vac = np.asarray(vac)
        wait = np.asarray(wait)
        meet = np.asarray(meet)
        plt.scatter(vac, wait, c=meet)
        plt.xlabel('vacant vehicle')
        plt.ylabel('waiting passenger')
        plt.colorbar()
        plt.show()






def plotTimeSteps(repID, testID):
    vacant = []
    waiting = []
    if type(repID) == int:
        fileName = open('/Users/shirley/TaxiResults/TimeSteps_{}_{}.txt'.format(repID, testID))
        for line in fileName.readlines()[1:]:
            line = line.strip('\n')
            line = line.split(',')
            vacant.append(int(line[0]))
            waiting.append(int(line[1]))
        vacant = np.asarray(vacant)
        waiting = np.asarray(waiting)
        fileName.close()

        fileName = open('/Users/shirley/TaxiResults/Passenger_{}_{}.txt'.format(repID, testID))
        meeting = np.zeros(len(vacant))
        for line in fileName.readlines()[1:]:
            line = line.strip('\n')
            line = line.split(',')

            meetingTime = int(float(line[2]))
            if meetingTime !=0:
                meeting[meetingTime]+=5

        print(vacant)
        print(waiting)
        print(meeting)
        plt.plot(vacant,label='vacant vehicles')
        plt.plot(meeting,label='Meeting ')
        plt.plot(waiting,label = 'waiting passengers')
        plt.legend()
        plt.xlabel('Time (sec)')
        plt.show()
    '''
    elif type(repID)==list:
        for id in repID:
            fileName = open('/Users/shirley/TaxiResults/TimeSteps_{}_{}.txt'.format(id,testID))
            for line in fileName.readlines()[1:]:
                line = line.strip('\n')
                line = line.split(',')
                vacant.append(int(line[0]))
                waiting.append(int(line[1]))
            fileName.close()

        vacant = np.asarray(vacant)
        waiting = np.asarray(waiting)
        meeting = np.asarray(meeting)
        time = np.asarray(range(0, len(vacant)))

        print(vacant)
        print(waiting)
        plt.plot(time, vacant, label='vacant vehicles')
        plt.plot(time, waiting, label='waiting passengers')
        plt.legend()
        plt.xlabel('Time')
        plt.show()
    '''

#plotTimeSteps(replicationlist,0)
plotTimeSteps(7553,7)

def plotMFD(repID, testID):
    accumulation = []
    flow = []
    completion = []
    if type(repID)==int:
        fileName = open('/Users/shirley/TaxiResults/Meeting_{}_{}.txt'.format(repID,testID))
        for line in fileName.readlines()[1:]:
            line = line.strip('\n')
            line = line.split(',')

            accumulation.append(float(line[4]))
            flow.append(float(line[5]))
            completion.append(float(line[6]))

        accumulation = np.asarray(accumulation)
        flow = np.asarray(flow)
        completion = np.asarray(completion)
        #print(accumulation)
        #print(flow)
        plt.figure(1)
        plt.subplot(211)
        plt.scatter(accumulation, flow/2)
        plt.xlabel('Accumulation (vehs) ')
        plt.ylabel('Production: sum(flow*section_length)/min')
        plt.title('MFD')

        plt.subplot(212)
        plt.scatter(accumulation, completion/2)
        plt.xlabel('Accumulation (vehs) ')
        plt.ylabel('Trip Completion (vehs/min)')


        plt.show()

    elif type(repID)==list:
        for id in repID:
            fileName = open('/Users/shirley/TaxiResults/MFD_{}_{}.txt'.format(id,testID))
            for line in fileName.readlines()[1:]:
                line = line.strip('\n')
                line = line.split(',')

                accumulation.append(float(line[3]))
                flow.append(float(line[4]))
            fileName.close()
        accumulation = np.asarray(accumulation)
        flow = np.asarray(flow)
        print(accumulation)
        print(flow)
        plt.scatter(accumulation, flow)
        plt.xlabel('Accumulation')
        plt.ylabel('flow')
        plt.title('MFD')
        plt.show()



#passengerStats(replicationlist, 0)
#passengerStats(7553, 4)
plotMFD(7553,7)



def assembleMeetingData(repID, testID, netWorkVeh):

    NetVelocity =[]
    meet = []
    wait = []
    vac = []
    netV = []


    #for id in repID:
        #if type(id) == int:
    fileName = open('/Users/shirley/TaxiResults/meeting_{}_{}.txt'.format(repID, testID))
    #fileName = open('/Users/shirley/TaxiResults/meeting_{}_{}.txt'.format(repID, testID))

        #errorlinecount = [1]
    counter = 1
    for line in fileName.readlines()[2:]:
        line = line.strip('\n')
        line = line.split('\t')
        tempmeet= line[0]
        tempwait= line[1]
        tempvac = line[2]
        tempVel = float(line[5])/float(line[4])
        #combined accumlation and completion.
        if tempmeet==0 or tempwait==0 or tempvac==0:
            counter+=1
            #errorlinecount.append(counter)
            continue
        else:
            meet.append(float(line[0]))
            wait.append(float(line[1]))
            vac.append(float(line[2]))
            netV.append(float(line[5])/float(line[4]))

    fileName.close()



    logmeet = np.log(np.asarray(meet))
    logwait = np.log(np.asarray(wait))
    logvac = np.log(np.asarray(vac))
    lognetV = np.log(np.asarray(netV))

    Twait = logwait[np.logical_not(np.isinf(logmeet))]
    Tvac = logvac[np.logical_not(np.isinf(logmeet))]
    TnetV = lognetV[np.logical_not(np.isinf(logmeet))]
    Tmeet = logmeet[np.logical_not(np.isinf(logmeet))]


    X = np.stack((Twait,Tvac,TnetV)).transpose()





    from sklearn import linear_model
    clf = linear_model.LinearRegression()
    clf.fit(X,Tmeet)
    #print(clf.get_params())

    Rsq= clf.score(X,Tmeet)
    print('Rsq of this is simulation to fit a linear model is: ', Rsq)


    newWait = np.log(np.linspace(min(wait)+1, max(wait), 100))
    newVac = np.log(np.linspace(min(vac)+1, max(vac), 100))
    #newNetV= np.log(np.linspace(min(netV), max(netV), 100))

    if netWorkVeh == 'h':
        avgNetV = np.log(max(netV))
    elif netWorkVeh == 'm':
        avgNetV = np.log((min(netV)+max(netV))/2)
    elif netWorkVeh == 'l':
        avgNetV = np.log(min(netV))
    else:
        print('net work average velocity should be h, m or l')
    newY = np.zeros((100,100))


    for i in range(0,100):
        for j in range(0,100):

                w = newWait[i]
                v = newVac[j]
                V = avgNetV
                newX = np.stack((w,v,V))
                newX = newX.reshape(1, -1)
                newY[i][j]= np.exp(clf.predict(newX))



    CS = plt.contour(np.exp(newWait), np.exp(newVac), newY, 10, linewidths=0.5, colors='k')
    CS = plt.contourf(np.exp(newWait), np.exp(newVac), newY, 10, vmax=abs(newY).max(), vmin=-abs(newY).max())
    plt.xlabel('Predicted vacant vehicle')
    plt.ylabel('Predicted waiting passenger')
    plt.colorbar()
    plt.title("High Network Velocity")
    plt.show()

#repID = [11141,11142,11143,11144,11146,11147,11148,11149]
assembleMeetingData(7553,8,'h')




