# GEO-ICT student project

This repository contains the material of the geo-ICT student project at faculty of Geography in collaboration with INBO/UAntwerpen. 

### Student members

* Thibeaut Formesyn
* Maarten Blomme
* Jolie De Geyter

## Application 

### Introduction

The project will focus on the Herring Gull data provided by the Lifewatch project. An open data is available at the Global Biodiversity Information Facility (GBIF) as [published data set](https://www.gbif.org/dataset/83e20573-f7dd-4852-9159-21566e1e691e).  

> Stienen E W, Desmet P, Aelterman B, Courtens W, Feys S, Vanermen N, Verstraete H, Van de walle M, Deneudt K, Hernandez F, Houthoofdt R, Vanhoorne B, Bouten W, Buijs R, Kavelaars M M, Müller W, Herman D, Matheve H, Sotillo A, Lens L (2017). Bird tracking - GPS tracking of Lesser Black-backed Gulls and Herring Gulls breeding at the southern North Sea coast. Version 5.6. Research Institute for Nature and Forest (INBO). Occurrence dataset https://doi.org/10.15468/02omly accessed via GBIF.org on 2018-10-15.

Within the scope of the project, the Herring Gulls are studied on a more extended data set, containing also the accelerometer data and linked behaviour information (annotated by experts).

### Inspiration

Relevant literature will be stored in the `literature` subfolder. Furthermore, following links are worthwhile to have a look:

- Dutch partner institute uva-Bits, developing the GPS trackers and providing some additional tools to access and check the data, http://www.uva-bits.nl/virtual-lab/
- INBO R package with some enrichment functionalities to analyze the bird tracking data,https://github.com/inbo/bird-tracking-etl
- Interactieve voorstelling bird tracking data developed by Lifewatch, http://inbo.github.io/bird-tracking/explorer/index.html check the code [here](https://github.com/inbo/bird-tracking)
- Interactive exploration tool of migration patterns develope on the open data set of the gulls, developed by Maximilian Konzack, http://www.win.tue.nl/~kbuchin/proj/gullmigration/ check the code [here](https://github.com/komax/migration-patterns-gull-data). The paper is in the literature folder. The output was part of a student workshop, see [report](https://komax.github.io/papers/gull_migration_vcma.pdf).



## Administration

### Useful learning material

*advice to the students to improve their skillset*

- Highly recommended read: [Good enough practices in scientific computing](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510)
- As we use Github, you will write a lot of `markdown` (readme files, issues,...). The syntax is rather intuitive and [this cheat sheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet) will get you quickly up to speed! 
- As we are working with observation data, this fits in a so-called `data.frame`. Both R and Python do have packages to support the handling (reading, writing, slicing, filtering,..) of a `data.frame`. Python-eers, check the [Pandas](http://pandas.pydata.org/pandas-docs/stable/10min.html) library  and maybe [this course](https://datacarpentry.org/python-ecology-lesson/). The geopgraphical component can be handled by using [Geopandas](http://geopandas.org/). R-people, check the [tidyverse](https://www.tidyverse.org/) packages. 


### Project folder structure

The folder structure of the project is organized as follows, please keep this in mind when adding new material:

```
geo-ict-student-project-2018
|-- data
|-- src
|-- literature
```
