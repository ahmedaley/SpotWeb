# SpotWeb
Code for SpotWeb is slowly rolled over here after cleanup. All code should be online by the end of June.

## Dependencies:

For SpotWeb to run, the following python libraries are needed:

a- boto3 ( for connecting with AWS)

b-flask

c-rpy2 (for the splines predictor)

d- pandas

e-flask_restful

f-pickle (for storing the output from the experiments)

g- cvxportfolio

h- cvxpy


For plotting:

a- seaborn

b-matplotlib

## Folders:

There are six folders in the repo:

a-  The SpotWeb folder contains all the code used to run the core of SpotWeb, the MPO optimizer, and the simulations. SpotWeb is now released as a library. For example usage, please check the simulation code or contact us. To connect SpotWeb to a cloud provider, you will need to design an interface to connect to the Cloud provider. 

c- The Autoscaler folder contains the code for an autoscaler that was used for the paper. In addition, we add a pointer to a few more autoscaler implementations.

d- The data folder contains most of the data we collected from monitoring AWS spot markets.

e-The loadbalancer folder contains the code used for managing the load balancing in SpotWeb including the automation and the scripts required to change the loadbalancing coefficients.



## The VM images
The German Wikipedia images are available here (http://zenky.cs.umu.se/PEAS/)
