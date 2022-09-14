import networkx as nx
#import osmnx as ox
#import utm
import numpy as np

class MultiCriteriaUrbanAssetDeploymentProblem:
 
    def __init__(self,origins=[100],destinations=[230], graph = None):
        # initialize the data:
        
        self.AIRTHRESHOLD = 40 #ug/m3
        self.NOISETHRESHOLD = 61 #dB
        self.FACTORHIKE = 1.1/1.6666 #max 1.1 metros/segundo a una rampa negativa de -2 grados
        self.ANGLETHRESHOLD_DEGREES = 8
        self.ANGLETHRESHOLD_DEGREES_RAMP = 20
        self.ANGLETHRESHOLD_DEGREES_STAIR = 40
        self.costBasePerRamp = 25000
        self.costBasePerElevator = 100000
        self.costBasePerStair = 40000
        self.rampPricePerMeter = 6800
        self.stairPricePerMeter = 7500
        self.costBasePerPanel= 100 
        self.panelPricePerMeter = 40 
        self.costBasePerEcopanel= 100 
        self.ecopanelPricePerMeter = 40 
        self.lenght = 0 
        self.origins = origins
        self.destinations = destinations
        self.NPATHS = len(self.origins)*len(self.destinations)
        self.edgesShortestPaths = []
        self.edgesShortestPathsNoise = []
        self.edgesShortestPathsAir = []
        self.graph_fileName = graph
        self.TotalmaxCost = (26342.1984126873 * 1.4) 
        self.TotalmaxNoise = (4681.0 * 315.0)  
        self.TotalmaxAir = (2155.6666666666665 * 400.0)
        self.TotalmaxPrice = 1000000.0
        self.wnoise = 0.33
        self.wacc = 0.33
        self.wair = 0.33
        
        self.__initData()
        self.INTERPOLATION_GRID_NUM = 5

    def __initData(self):
       self.G_nx = nx.read_gpickle(self.graph_fileName)
       
       self.listEdges = list(self.G_nx.edges())
       for edge in self.listEdges:
           
            cost, price = self.f_noramp(edge)
            self.G_nx[edge[0]][edge[1]][0]['weight']  = cost
            
            sound, price = self.f_nopanel(edge)
            self.G_nx[edge[0]][edge[1]][0]['noise']  = sound
            
            pollution, price = self.f_noecopanel(edge)
            self.G_nx[edge[0]][edge[1]][0]['air']  = pollution
           
    def computeAirEdge(self,edge):
        
        u,v = edge[0:2]
        air = self.G_nx[u][v][0]['air']
        return air

    
    def computeShortestPathswithoutEcopanels(self):
        
        self.edgesShortestPathAir = []
        
        for i_origin in range(len(self.origins)):
            
            for i_destination in range(len(self.destinations)):
                
                path = nx.dijkstra_path(self.G_nx, self.origins[i_origin], self.destinations[i_destination], weight ='weight')
                self.edgesShortestPathsAir.extend([self.listEdges.index((path[i_node-1],path[i_node])) for i_node in range(1,len(path))])
    
        self.edgesShortestPathsAir = list(set(self.edgesShortestPathsAir))
        
    def computeProblematicEdgesAir(self):
        
        self.allProblematicEdgesAir = []
        
        for i_edge in range(len(self.listEdges)):
            
            if np.abs(self.computeAirEdge(self.listEdges[i_edge]))>self.AIRTHRESHOLD:  
                self.allProblematicEdgesAir.append(i_edge)
 
        
    def f_noecopanel(self,edge):  
        
         u,v = edge[0:2]
        
         x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
         x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[v]['z_utm']]).astype(float)

         distanceTotal = np.sqrt(((x2[0]-x1[0])**2) + (x2[1]-x1[1])**2)    
         pollution = distanceTotal * self.G_nx[u][v][0]['air']

         return (pollution,0)
    
    def f_ecopanel(self,edge,ecopanelen):  
        
         u,v = edge[0:2]
        
         x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
         x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
         
         air = self.G_nx[u][v][0]['air']
         
         distanceTotal= np.sqrt(((x2[0]-x1[0])**2 + (x2[1]-x1[1])**2))
         
         if (ecopanelen*distanceTotal) > 500.0: #Longitud maxima que puede tener una panel
             distanceMax = 500
             pollution = (distanceMax*(air*0.7)) + (distanceTotal-distanceMax)*air
             price = distanceMax*self.ecopanelPricePerMeter + self.costBasePerEcopanel
         else:
             pollution = (ecopanelen*distanceTotal*(air*0.7)) + ((1-ecopanelen)*distanceTotal*air)
             price = ecopanelen*distanceTotal*self.ecopanelPricePerMeter + self.costBasePerEcopanel
            
         return (pollution,price)
            
    def computeNoiseEdge(self,edge):  
        
        u,v = edge[0:2]
        noise = self.G_nx[u][v][0]['noise']
        return noise

    def computeShortestPathswithoutPanels(self): 
        
        self.edgesShortestPathNoise = []
        
        for i_origin in range(len(self.origins)):
            
            for i_destination in range(len(self.destinations)):
                
                path = nx.dijkstra_path(self.G_nx, self.origins[i_origin], self.destinations[i_destination], weight ='weight')
                self.edgesShortestPathsNoise.extend([self.listEdges.index((path[i_node-1],path[i_node])) for i_node in range(1,len(path))])
    
        self.edgesShortestPathsNoise = list(set(self.edgesShortestPathsNoise))
        
    def computeProblematicEdgesNoise(self):  
        
        self.allProblematicEdgesNoise = []
        
        for i_edge in range(len(self.listEdges)):
            
            if np.abs(self.computeNoiseEdge(self.listEdges[i_edge]))>self.NOISETHRESHOLD:  
                self.allProblematicEdgesNoise.append(i_edge)
 
        
    def f_nopanel(self,edge):  
        
         u,v = edge[0:2]
        
         x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
         x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[v]['z_utm']]).astype(float)

         distanceTotal = np.sqrt(((x2[0]-x1[0])**2 + (x2[1]-x1[1])**2))   
         sound = distanceTotal * self.G_nx[u][v][0]['noise']

         return (sound,0)
    
    def f_panel(self,edge,panelen):  
        
         u,v = edge[0:2]
        
         x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
         x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
         
         noise = self.G_nx[u][v][0]['noise']
         
         distanceTotal= np.sqrt(((x2[0]-x1[0])**2 + (x2[1]-x1[1])**2))
         
         if (panelen*distanceTotal) > 500.0: #Longitud maxima que puede tener una panel
             distanceMax = 500
             sound = (distanceMax*(noise*0.7)) + (distanceTotal-distanceMax)*noise
             price = distanceMax*self.panelPricePerMeter + self.costBasePerPanel
         else:
             sound = ((panelen*distanceTotal)*(noise*0.7)) + (((1-panelen)*distanceTotal)*noise)
             price = (panelen*distanceTotal)*self.panelPricePerMeter + self.costBasePerPanel
            
         return (sound,price)
        
    def computeAngleEdge(self,edge):
        
        u,v = edge[0:2]
        
        x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
        x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[v]['z_utm']]).astype(float)

        rise = x2[2]-x1[2]
        run = np.sqrt((x2[0]-x1[0])**2 + (x2[1]-x1[1])**2)
        angle = np.degrees(np.arctan(rise/run))
        return angle

    
    def hike(self,degree):

         if np.abs(degree)<self.ANGLETHRESHOLD_DEGREES:
             return self.FACTORHIKE*6 * np.exp(-3.5 * abs(np.tan(np.radians(degree)) + 0.05))*1000/3600.
         else:
             return 0.01*self.FACTORHIKE*6 * np.exp(-3.5 * abs(np.tan(np.radians(degree)) + 0.05))*1000/3600.

    def computeShortestPathswithoutRamp(self):
        
        for edge in self.G_nx.edges:
            cost, price = self.f_noramp(edge)
            self.G_nx[edge[0]][edge[1]][0]['weight']  = cost
            
        self.edgesShortestPaths = []
        
        for i_origin in range(len(self.origins)):
            
            for i_destination in range(len(self.destinations)):
                
                path = nx.dijkstra_path(self.G_nx, self.origins[i_origin], self.destinations[i_destination], weight ='weight')
                self.edgesShortestPaths.extend([self.listEdges.index((path[i_node-1],path[i_node])) for i_node in range(1,len(path))])
    
        self.edgesShortestPaths = list(set(self.edgesShortestPaths))
        
    def computeProblematicEdges(self): 
        
        self.allProblematicEdgesAngle = []
        
        for i_edge in range(len(self.listEdges)):
            
            if np.abs(self.computeAngleEdge(self.listEdges[i_edge]))>self.ANGLETHRESHOLD_DEGREES:  
                self.allProblematicEdgesAngle.append(i_edge)

    def f_noramp(self,edge):
        
        u,v = edge[0:2]
        
        x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
        x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[v]['z_utm']]).astype(float)

        rise = x2[2]-x1[2]
        run = np.sqrt((x2[0]-x1[0])**2 + (x2[1]-x1[1])**2)
        angle = np.degrees(np.arctan(rise/run))

        walkingSpeed = self.hike(angle) 
        distanceTotal= np.linalg.norm(x1-x2)
        
        cost = distanceTotal/walkingSpeed
        
        return (cost,0)
    
    def f_ramp(self,edge,ramplen):
        
        u,v = edge[0:2]
        
        x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
        x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[v]['z_utm']]).astype(float)

        rise = x2[2]-x1[2]
        run = np.sqrt((x2[0]-x1[0])**2 + (x2[1]-x1[1])**2)
        angle = np.degrees(np.arctan(rise/run))

        walkingSpeed = self.hike(angle)
        distanceTotal= np.linalg.norm(x1-x2)
        if (ramplen*distanceTotal) > 100.0: 
            distanceMax = 100
            cost = (distanceMax/0.5) + ((distanceTotal-distanceMax)/walkingSpeed)
            price = distanceMax*self.rampPricePerMeter + self.costBasePerRamp
        else:
            cost = ((ramplen*distanceTotal)/0.5) + (((1-ramplen)*distanceTotal)/walkingSpeed)
            price = ramplen*distanceTotal*self.rampPricePerMeter + self.costBasePerRamp
            
        return (cost,price)
        
    
    def f_stair(self,edge,ramplen):
            
        u,v = edge[0:2]
        
        x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
        x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[v]['z_utm']]).astype(float)

        rise = x2[2]-x1[2]
        run = np.sqrt((x2[0]-x1[0])**2 + (x2[1]-x1[1])**2)
        angle = np.degrees(np.arctan(rise/run))

        walkingSpeed = self.hike(angle)
        distanceTotal= np.linalg.norm(x1-x2)
        if (ramplen*distanceTotal) > 100.0:
            distanceMax = 100
            cost = (distanceMax/0.5) + ((distanceTotal-distanceMax)/walkingSpeed)
            price = distanceMax*self.rampPricePerMeter + self.costBasePerRamp
        else:
            cost = ((ramplen*distanceTotal)/0.5) + (((1-ramplen)*distanceTotal)/walkingSpeed)
            price = ramplen*distanceTotal*self.stairPricePerMeter + self.costBasePerStair
    
        
        return (cost,price)
    
    def f_elevator(self,edge):
        
        u,v = edge[0:2]
        
        x1 = np.array([self.G_nx.nodes[u]['x_utm'],self.G_nx.nodes[u]['y_utm'],self.G_nx.nodes[u]['z_utm']]).astype(float)
        x2 = np.array([self.G_nx.nodes[v]['x_utm'],self.G_nx.nodes[v]['y_utm'],self.G_nx.nodes[v]['z_utm']]).astype(float)

        distanceTotal= np.linalg.norm(x1-x2)
        cost = (distanceTotal/2)
        price = self.costBasePerElevator
        
        return (cost,price)

    def simulateSolution(self, cromosome_ramps, cromosome_panels, cromosome_ecopanels):
        
        edgelist = list(self.G_nx.edges())
        local_G_nx = self.G_nx.copy()
        
        for edge in self.listEdges:
            
            pollution, _ = self.f_noecopanel(edge)
            local_G_nx[edge[0]][edge[1]][0]['air']  = pollution
            sound, _ = self.f_nopanel(edge)
            local_G_nx[edge[0]][edge[1]][0]['noise']  = sound 
            cost,_ = self.f_noramp(edge)
            local_G_nx[edge[0]][edge[1]][0]['weight'] = cost

        totalPrice = 0
        totalSound = 0
        totalPollution = 0
        
        
        for iecopanel in range(int(len(cromosome_ecopanels)/2)):
        
            edgenum = cromosome_ecopanels[2*iecopanel]
            panelen = cromosome_ecopanels[(2*iecopanel) + 1]
            edgeecopanel = edgelist[edgenum] #(u,v)
            
            for edge in self.listEdges:
                edgeair = abs(self.computeAirEdge(edge))
                
                if self.AIRTHRESHOLD <= edgeair:
                    if edgeecopanel[0] == edge[0] and edgeecopanel[1] == edge[1]:
                        pollution, price = self.f_ecopanel(edge,panelen)
                        local_G_nx[edge[0]][edge[1]][0]['air'] = pollution
                        totalPrice = totalPrice + price
                        
        for ipanel in range(int(len(cromosome_panels)/2)):
        
            edgenum = cromosome_panels[2*ipanel]
            panelen = cromosome_panels[(2*ipanel) + 1]
            edgepanel = edgelist[edgenum] #(u,v)

            for edge in self.listEdges:
                edgenoise = abs(self.computeNoiseEdge(edge))
                
                if self.NOISETHRESHOLD <= edgenoise:
                    if edgepanel[0] == edge[0] and edgepanel[1] == edge[1]:
                        sound, price = self.f_panel(edge,panelen)
                        local_G_nx[edge[0]][edge[1]][0]['noise'] = sound
                        totalPrice = totalPrice + price
        
        for iramp in range(int(len(cromosome_ramps)/2)):
        
            edgenumber = cromosome_ramps[2*iramp]
            ramplen = cromosome_ramps[(2*iramp) + 1]
            edgeramp = edgelist[edgenumber] #(u,v)

            for edge in self.listEdges:
                edgeangle = abs(self.computeAngleEdge(edge))         
                
                if self.ANGLETHRESHOLD_DEGREES <= edgeangle and edgeangle < self.ANGLETHRESHOLD_DEGREES_RAMP:
                    if edgeramp[0] == edge[0] and edgeramp[1] == edge[1]:
                        #print('RAMPA',edge,edgeramp,edgeangle,edgenumber)
                        cost, price = self.f_ramp(edge,ramplen)
                        local_G_nx[edge[0]][edge[1]][0]['weight'] = cost
                        totalPrice = totalPrice + price
                elif edgeangle > self.ANGLETHRESHOLD_DEGREES_RAMP and edgeangle < self.ANGLETHRESHOLD_DEGREES_STAIR:
                    if edgeramp[0] == edge[0] and edgeramp[1] == edge[1]:
                        #print('STAIR',edge,edgeramp,edgeangle,edgenumber)
                        cost, price = self.f_stair(edge,ramplen)
                        local_G_nx[edge[0]][edge[1]][0]['weight'] = cost
                        totalPrice = totalPrice + price
                elif edgeangle >= self.ANGLETHRESHOLD_DEGREES_STAIR: 
                    if edgeramp[0] == edge[0] and edgeramp[1] == edge[1]:
                        #print('ELEVATOR',edge,edgeramp,edgeangle,edgenumber)
                        cost, price = self.f_elevator(edge)
                        local_G_nx[edge[0]][edge[1]][0]['weight'] = cost
                        totalPrice = totalPrice + price

        for edge in self.listEdges:
            noise_wt = local_G_nx[edge[0]][edge[1]][0]['noise'] 
            cost_wt = local_G_nx[edge[0]][edge[1]][0]['weight']
            air_wt = local_G_nx[edge[0]][edge[1]][0]['air']
            totalWeight = self.wnoise*noise_wt + self.wacc*cost_wt + self.wair*air_wt
            local_G_nx[edge[0]][edge[1]][0]['totWeight'] = totalWeight
        
        totalSound = []
        totalCost = []
        totalPollution = []
        paths =  []
        
        for i_origin in range(len(self.origins)):
            
            for i_destination in range(len(self.destinations)):
        
                 origin = self.origins[i_origin]
                 destination = self.destinations[i_destination]

                 path = nx.dijkstra_path(local_G_nx, origin, destination, weight = 'totWeight')
                 paths.append(path)
                 
                 totalSound.append(0.0)
                 totalCost.append(0.0)
                 totalPollution.append(0.0)
                
                 for index_nodeinpath in range(1,len(path)):
                     firstLineNode = path[index_nodeinpath-1]
                     secondLineNode = path[index_nodeinpath]
                     totalCost[-1] = totalCost[-1] + local_G_nx.edges[firstLineNode, secondLineNode,0]['weight']
                     totalSound[-1] = totalSound[-1] + local_G_nx.edges[firstLineNode, secondLineNode,0]['noise']
                     totalPollution[-1] = totalPollution[-1] + local_G_nx.edges[firstLineNode, secondLineNode,0]['air']
        
        
        normalizeCost = (np.mean(totalCost))/(self.TotalmaxCost)
        normalizeSound = (np.mean(totalSound))/(self.TotalmaxNoise)
        normalizePollution = (np.mean(totalPollution))/(self.TotalmaxAir)
        normalizePrice = (totalPrice)/(self.TotalmaxPrice)
        
        return(normalizeCost,normalizeSound,normalizePollution,normalizePrice)
    
      
