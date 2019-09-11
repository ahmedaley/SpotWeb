# SpotWeb
Code for SpotWeb is slowly rolled over here after cleanup. All code should be online by the end of June.

## Dependencies:

For SpotWeb to run, the following python libraries are needed:

a- boto3

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

a-  The Interface folder contains the interface code that is used to communicate between SpotWeb and AWS.

b- The SpotWeb folder contains all the code used to run the core of SpotWeb, the MPO optimizer.

c- The Autoscaler folder contains the code for an autoscaler that was used for the paper. In addition, we add a pointer to a few more autoscaler implementations.

d- The data folder contains most of the data we collected from monitoring AWS spot markets.

e-The loadbalancer folder contains the code used for managing the load balancing in SpotWeb including the automation and the scripts required to change the loadbalancing coefficients.

f- While we do not show results with sockshop (https://microservices-demo.github.io/), we include scripts that were used to test Spotweb with Sockshop. We note that sockshop had some issues with loadbalancing.

## The VM images
The German Wikipedia images are available here (http://zenky.cs.umu.se/PEAS/)
