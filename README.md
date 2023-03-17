# A Framework to Improve Urban Accessibility and Environmental Conditions in Age-friendly Cities using Graph Modeling and Multi-objective Optimization
Repository containing datasets and simulations scripts for the multi-objective optimization of accessibility, air pollution and environmental noise reduction assets in age-friendly cities.

<img src="./images/diagram.jpg" width="100%" />

### Requirements and dependencies

1. jMetalPy [https://github.com/jMetal/jMetalPy]
2. OSMnx [https://github.com/gboeing/osmnx]
3. NetworkX [https://github.com/networkx/networkx]
4. Other libraries typically included in mainstream Python distributions (Numpy, Pickle, Matplotlib, etc)

### How to run:

Two scripts are provided:

1. mainScenarioClass.py: this script defines a class and methods required to compute the objective values of any given intervention over the area of interest.
2. mainSimulationScript.py: this script exemplifies how the framework would be applied to the scenario A2, using NSGA2 to approach the set of Pareto-optimal interventions.

Results are given in the folder named as such. Other scripts (production of plots, computation of quality statistics, etc) can be provided on demand.

### Contributing

If you find a bug, create a GitHub issue, or even better, submit a pull request. Similarly, if you have questions, simply post them as GitHub issues.

### Citing this work:

*Iñigo Delgado-Enales, Javier Del Ser, Patricia Molina, "A Framework to Improve Urban Accessibility and Environmental Conditions in Age-friendly Cities using Graph Modeling and Multi-objective Optimization", under review, arXiv:XXXXX, 2022*

**Abstract**

The rapid growth of cities in recent decades has unleashed several challenges for urban planning, which have been exacerbated by their ageing population. Among the most pressing problems in cities are those related to mobility and environmental quality, by which a global concern has flourished around enhancing pedestrian accessibility for both environmental and health-related reasons. To tackle this issue, this paper presents a new framework that combines multi-objective optimization with a graph model that aims to support urban planning and management. The framework allows designing urban projects that improve accessibility, reduce noise and/or pollution through the installation of urban elements (ramps and escalators, elevators, acoustic and vegetation panels), while taking into account the overall economic cost of the installation. To explore the trade-off between these objectives, we resort to multi-objective evolutionary algorithms, which permit to compute near Pareto-optimal interventions over the graph model of the urban area under study. We showcase the applicability of the proposed framework over two use cases in the city of Barcelona (Spain), both quantitatively and qualitatively. The results evince that the framework can effectively help urban planners make informed decisions towards enhancing urban accessibility and environmental quality of age-friendly cities. 

[[Link to the paper]](XXX)

```
@article{delgadoenales23journal,
  title={{A Framework to Improve Urban Accessibility and Environmental Conditions in Age-friendly Cities using Graph Modeling and Multi-objective Optimization}},
  author={Delgado-Enales, I\~nigo and Del Ser, Javier and Molina, Patricia},
  journal={Computers, Environment and Urban Systems, accepted, in press},
  year={2023}
}
```

### Contact:

- Iñigo Delgado-Enales, inigodelgado22@gmail.com
- Javier Del Ser, javier.delser@tecnalia.com
- Patricia Molina, patricia.molina@tecnalia.com
