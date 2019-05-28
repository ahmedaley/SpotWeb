##Variable definitions####

pvector1 <- NULL                                                      ## defining our predictor vector for 1 hour
pvector24 <- NULL                                                     ## defining our predictor vector for 1 day
pvector168 <- NULL                                                    ## defining our predictor vector for 1 week
pe <- 0                                                               ## Prediction Error vector
AR <- 0
indexup <- NULL
indexdown <- NULL
index <- NULL
poserr <- NULL
negerr <- NULL

Lag <- function(x, k)                    
{
  c(rep(NA, k), x)[1 : length(x)] 
}

data  <- read.table("AggReq.out")                                     ## Reading the data
data4 <- data[(1):(336),5]                                            ## Taking the 1st and 2nd week for training data
data3 <- data[,5]                                               ## Taking all the years data for evaluation
data2 <- data[,5]                                                   ## Taking all the years data for evaluation

x <- seq(1:168)                                                       ## Create amount of days vector 2x168 hours = 2 weeks
x[169:336] <- seq(1:168)

basis <- create.bspline.basis(c(0,168), 87, 4)                        ## Create a bspline basis system from 0 to 168 with 83 knots (87-4)
basismat <- eval.basis(x,basis)                                       ## Evaluate the basis system to the vector x values
lscoef <- lsfit(basismat,data4 ,intercept=FALSE)$coef                 ## using a Least-Square fit to estimate the coefficients C
cloudfd <- fd(lscoef,basis,list("Hours", "Week", "Requests"))         ## Defining a functional data object
res <- lsfit(basismat,data4 ,intercept=FALSE)$res                     ## Saving the residuals for the AR model
sdres <- sd(lsfit(basismat,data4 ,intercept=FALSE)$res, na.rm=TRUE)   ## saving the std dev of the residauls and removing any NA values
#AR <- cbind(0,0)
AR <- lsfit(Lag(res,1), res,intercept=TRUE )$coef                     ## Saves the prediction error for the first 2 weeks and makes it a LS-fit
##AR2 <- lsfit(res,Lag(res,2), intercept=TRUE )$coef
##AR3 <- lsfit(res,Lag(res,3), intercept=TRUE )$coef

pvector1[1] <- predict(cloudfd,1,0)+AR[[1]]+AR[[2]]*res[336]          ## storing the prediction values in a 
pvectorPRED <- pvector1[1]
## vector using the AR modell on resduals
