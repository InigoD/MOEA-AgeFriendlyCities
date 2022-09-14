from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator.crossover import CompositeCrossover, IntegerSBXCrossover, SBXCrossover
from jmetal.operator.mutation import CompositeMutation, PolynomialMutation
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.core.problem import Problem
from jmetal.core.solution import FloatSolution, CompositeSolution, IntegerSolution
from jmetal.util.observer import ProgressBarObserver, BasicObserver
from jmetal.util.evaluator import MultiprocessEvaluator
from jmetal.util.ckecking import Check
from jmetal.core.operator import Mutation
import mainScenarioClass
import random
import pickle

class IntegerRandomMutation(Mutation[IntegerSolution]):

    def __init__(self, probability: float):
        super(IntegerRandomMutation, self).__init__(probability=probability)

    def execute(self, solution: IntegerSolution) -> IntegerSolution:
        Check.that(issubclass(type(solution), IntegerSolution), "Solution type invalid")

        for i in range(solution.number_of_variables):
            if random.random() <= self.probability:
                if solution.lower_bound[i]==0 and solution.upper_bound[i]==1:
                    y = 1-solution.variables[i]
                else:
                    possibles = list(range(solution.lower_bound[i],solution.upper_bound[i]))
                    y = random.choice(possibles)
                
                if y < solution.lower_bound[i]:
                    y = solution.lower_bound[i]
                if y > solution.upper_bound[i]:
                    y = solution.upper_bound[i]
                
                solution.variables[i] = y
                
        return solution

    def get_name(self):
        return 'Random mutation (Integer)'

class FloatRandomMutation(Mutation[FloatSolution]):

    def __init__(self, probability: float, sigma: float):
        super(FloatRandomMutation, self).__init__(probability=probability)
        self.sigma = sigma

    def execute(self, solution: FloatSolution) -> FloatSolution:
        Check.that(issubclass(type(solution), FloatSolution), "Solution type invalid")

        for i in range(solution.number_of_variables):
            if random.random() <= self.probability:
                y = solution.variables[i] + self.sigma*random.random()
                
                if y < solution.lower_bound[i]:
                    y = solution.lower_bound[i]
                if y > solution.upper_bound[i]:
                    y = solution.upper_bound[i]

                solution.variables[i] = y
        return solution

    def get_name(self):
        return 'Random mutation (Float)'

# =============================================================================
# Class myProblem
# =============================================================================

class myProblem(Problem):
    def __init__(self, n_ramps=30, n_panels=50, n_ecopanels = 50, scenario = None):
        
        super(myProblem, self).__init__()
        self.number_of_objectives = 4
        self.number_ramps = n_ramps
        self.number_panels = n_panels #SONIDO
        self.number_ecopanels = n_ecopanels #POLUCION
        self.scenario = scenario
        self.problematicEdgesAngle = scenario.allProblematicEdgesAngle
        self.problematicEdgesNoise = scenario.allProblematicEdgesNoise #SONIDO
        self.problematicEdgesPolution= scenario.allProblematicEdgesAir #POLUCION

        self.number_of_variables = 3*self.number_ramps + 3*self.number_panels + 3*self.number_ecopanels
        self.number_of_integer_variables = 2*self.number_ramps + 2*self.number_panels + 2*self.number_ecopanels
        self.number_of_float_variables = self.number_ramps + self.number_panels + self.number_ecopanels
        
        self.number_of_constraints = 0

        self.obj_directions = [self.MINIMIZE, self.MINIMIZE, self.MINIMIZE, self.MINIMIZE]
        self.obj_labels = ['Average path time','Average path noise','Average path pollution','Economical cost']
        
        self.int_lower_bound = [0 for _ in range(self.number_of_integer_variables)]
        self.int_upper_bound = [1 for _ in range(self.number_ramps+self.number_panels+self.number_ecopanels)] + [(len(self.problematicEdgesAngle))-1 for _ in range(self.number_ramps)] + [(len(self.problematicEdgesNoise))-1 for _ in range(self.number_panels)] + [(len(self.problematicEdgesPolution))-1 for _ in range(self.number_ecopanels)]

        
        self.float_lower_bound = [0 for _ in range(self.number_of_float_variables)]
        self.float_upper_bound = [1 for _ in range(self.number_of_float_variables)]
        

    def evaluate(self, solution: CompositeSolution) -> CompositeSolution:
                
        cs_eval_ramps = sum([[self.problematicEdgesAngle[solution.variables[0].variables[self.number_ramps+self.number_panels+i]],solution.variables[1].variables[i]] if solution.variables[0].variables[i]==1 else [] for i in range(self.number_ramps)],[])
        cs_eval_panels = sum([[self.problematicEdgesNoise[solution.variables[0].variables[2*(self.number_ramps)+self.number_panels+i]],solution.variables[1].variables[self.number_ramps+i]] if solution.variables[0].variables[self.number_ramps + i]==1 else [] for i in range(self.number_panels)],[])
        cs_eval_ecopanels = sum([[self.problematicEdgesPolution[solution.variables[0].variables[2*(self.number_ramps)+2*(self.number_panels)+self.number_ecopanels+i]],solution.variables[1].variables[self.number_ramps+ self.number_panels+i]] if solution.variables[0].variables[self.number_ramps + self.number_panels + i]==1 else [] for i in range(self.number_ecopanels)],[])
        
        cost, sound, air, price = self.scenario.simulationResult(cs_eval_ramps,cs_eval_panels,cs_eval_ecopanels)#,w1,w2,w3)

        solution.objectives[0] = cost
        solution.objectives[1] = sound
        solution.objectives[2] = air
        solution.objectives[3] = price

        return solution

    def create_solution(self) -> CompositeSolution:
        integer_solution = IntegerSolution(self.int_lower_bound, self.int_upper_bound, self.number_of_objectives,
                                           self.number_of_constraints)
        float_solution = FloatSolution(
            self.float_lower_bound,
            self.float_upper_bound,
            self.number_of_objectives, self.number_of_constraints)

        float_solution.variables = \
            [random.uniform(self.float_lower_bound[i], self.float_upper_bound[i]) for i in
             range(len(self.float_lower_bound))]

        integer_solution.variables = \
            [random.randint(self.int_lower_bound[i], self.int_upper_bound[i]) for i in
             range(len(self.int_lower_bound))]

        return CompositeSolution([integer_solution, float_solution])

    def get_name(self) -> str:
        return "Routing problem"

# =============================================================================
# MAIN CLASS
# =============================================================================

if __name__ == '__main__':
    
    NRUNS = 20
    
    for i in range(NRUNS):
        
        graphFileName = "G_nx_MDT5_A2.gpickle"
        N_RAMPS = 20
        N_PANELS = 20 
        N_ECOPANELS = 20 
        NCORES = 2
        ORIGINS = [257,496,623,67,400]
        DESTINATIONS = [100,5349,982,589,1144,2269]
        
        bcn = mainScenarioClass.MultiCriteriaUrbanAssetDeploymentProblem(origins=ORIGINS,destinations=DESTINATIONS, graph = graphFileName)
        bcn.computeShortestPathswithoutRamp()
        bcn.computeShortestPathswithoutPanels()
        bcn.computeShortestPathswithoutEcopanels()
        bcn.computeProblematicEdges()
        bcn.computeProblematicEdgesNoise()
        bcn.computeProblematicEdgesAir()
        
        problem = myProblem(n_ramps=N_RAMPS,n_panels=N_PANELS,n_ecopanels= N_ECOPANELS, scenario=bcn)
        
        max_evaluations = 20000
        algorithm = NSGAII(
            problem=problem,
            population_evaluator=MultiprocessEvaluator(NCORES),
            population_size=100,
            offspring_population_size=100,
            mutation=CompositeMutation([IntegerRandomMutation(0.1), PolynomialMutation(0.1, 20)]),
            crossover=CompositeCrossover([IntegerSBXCrossover(probability=0.8, distribution_index=20),
                                           SBXCrossover(probability=0.8, distribution_index=20)]),
            termination_criterion=StoppingByEvaluations(max_evaluations=max_evaluations)
        ) 
        
        algorithm.observable.register(observer=ProgressBarObserver(max=max_evaluations))
        algorithm.observable.register(observer=BasicObserver())
        algorithm.run()
        
        front_i = get_non_dominated_solutions(algorithm.get_result())
        
        with open('front_pickled_nsgaII_' + str(i) + '.p','wb') as fid:
            pickle.dump(front_i, fid)
        
        with open('results_nsgaII_' + str(i) + '.txt','w') as fid:
            for f in front_i:
                fid.write(str(f.objectives[0])+';'+str(f.objectives[1])+';' +str(f.objectives[2])+';' +str(f.objectives[3])+';' +str(f.variables[0].variables)+';' +str(f.variables[1].variables)+'\n')
           