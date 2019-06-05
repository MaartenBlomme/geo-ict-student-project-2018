# Projectwerk GEO-ict

This repository contains the material of the student project GEO-ict at faculty of Geography in collaboration with INBO/UAntwerpen. 

## Rationale

The project will focus on the Herring Gull data provided by the Lifewatch project. An open data is available at the Global Biodiversity Information Facility (GBIF) as [published data set](https://www.gbif.org/dataset/83e20573-f7dd-4852-9159-21566e1e691e).  

> Stienen E W, Desmet P, Aelterman B, Courtens W, Feys S, Vanermen N, Verstraete H, Van de walle M, Deneudt K, Hernandez F, Houthoofdt R, Vanhoorne B, Bouten W, Buijs R, Kavelaars M M, Müller W, Herman D, Matheve H, Sotillo A, Lens L (2017). Bird tracking - GPS tracking of Lesser Black-backed Gulls and Herring Gulls breeding at the southern North Sea coast. Version 5.6. Research Institute for Nature and Forest (INBO). Occurrence dataset https://doi.org/10.15468/02omly accessed via GBIF.org on 2018-10-15.

Within the scope of the project, the Herring Gulls are studied on a more extended data set, containing also the accelerometer data and linked behaviour information (annotated by experts).

Data exploration was done at the start of the project. After which various analyzes have been attempted on the data. Pre-processing was necessary to perform these analyzes.

## Results

- [Exploratory notebook](notebooks/data_exploration.ipynb)
- [Exploratory notebook on temporal resolution](notebooks/tempore_resoluties.ipynb)
- [Get timeintervals when gulls are close to each other](src/MeeuwenInElkaarsBuurt.py)
- [REMO analysis on flight direction](src/REMO_analyse_meeuwen_in_elkaars_buurt.py)

## Contributors

- Maarten Blomme
- Thibeaut Formesyn
- Jolie de Geyter

## License

[MIT license](LICENSE)
