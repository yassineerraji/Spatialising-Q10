# Corporate Research Project

- **AIDAMS - ESSEC & CentraleSupélec - 4th year - 2026-2027**
- Yassine ERRAJI, William PELTIER, Simon AMAR
- Bertrand Guenet (guenet@geologie.ens.fr)

*École Normale Supérieure*

## Case Description

### Title of the case

Using a Q10 database to develop maps to be used in the land surface model ORCHIDEE

### Short description of the case 

Q10 is a parameter representing the sensitivity of soil organic matter decomposition to temperature. This might be considered as an emerging property of the microbial community but in most of the soil organic decomposition model it is considered as a fixed parameter. 
Several studies show that this Q10 value actually depends on several factors including environmental factors like climate, soil texture, etc. Nevertheless, in land surface models used within climate models to predict climate change among others, this parameter is fixed in space and time leading to important uncertainties in the model projection. 
We propose here to use a database of Q10 value measured on different sites and create a machine learning approach to spatialize the values producing then a maps that will be used in the ORCHIDEE land surface model.

### Dataset description (eg list of variables and their definition, total volume of the dataset, source, etc)

The initial dataset will come from a recent publication:

The Q10 of in situ microbial soil respiration varies with mean annual temperature, precipitation, pH, and plant cover: a meta-analysis and spatial prediction of Q10 (https://doi.org/10.1038/s41598-026-45615-w)