#install.packages('fda')
library('fda')



Lag <- function(x, k) {
  c(rep(NA, k), x)[1 : length(x)]
}


pred_load_data <- function(filename) {
    pvector1 <<- NULL                                                      ## defining our predictor vector for 1 hour
    pvector24 <- NULL                                                     ## defining our predictor vector for 1 day
    pvector168 <- NULL                                                    ## defining our predictor vector for 1 week
    pe <<- 0                                                               ## Prediction Error vector
    AR <<- 0
    indexup <<- NULL
    indexdown <<- NULL
    index <<- NULL
    pos_err <- NULL
    neg_err <- NULL

    data  <- read.table(filename)                                         ## Reading the data
    training_data <- data[(1):(336),5]                                    ## Taking the 1st and 2nd week for training data
    eval_data <<- training_data
    x <- seq(1:168)                                                       ## Create amount of days vector 2x168 hours = 2 weeks
    x[169:336] <- seq(1:168)                                              ## ..For the 2nd week.
    next_i <<- 336                                                        ## Setting up next i in this.

    basis <<- create.bspline.basis(c(0,168), 87, 4)                        ## Create a bspline basis system from 0 to 168 with 83 knots (87-4)
    basismat <<- eval.basis(x,basis)                                       ## Evaluate the basis system to the vector x values
    lscoef <<- lsfit(basismat,training_data ,intercept=FALSE)$coef         ## using a Least-Square fit to estimate the coefficients C
    cloudfd <<- fd(lscoef,basis,list("Hours", "Week", "Requests"))         ## Defining a functional data object
    residual <<- lsfit(basismat,training_data ,intercept=FALSE)$residual                       ## Saving the residualiduals for the AR model
    std_dev_residual <<- sd(lsfit(basismat,training_data ,intercept=FALSE)$residual, na.rm=TRUE)     ## saving the std dev of the residualidauls and removing any NA values
    AR <<- lsfit(Lag(residual,1), residual,intercept=TRUE )$coef                               ## Saves the prediction error for the first 2 weeks and makes it a LS-fit
	print ("FUnction done")


}

# current_requests - Current requests is the number of request known for the last hour.
# number_of_predictions - How many predicts in the future that the prediction should predict.

pred_predict <- function(current_requests, number_of_predictions) {
  i <- next_i + 1
  next_i <<- i

  eval_data <<- c(eval_data, current_requests)
  eval_current <- eval_data[i]
  eval_sliding <- eval_data[(i-335):i]




  maxi <- max(predict(cloudfd,seq(1:168),0)) + std_dev_residual*2         ## Storing the max value+5std dev to compare with real data
  mini <- min(predict(cloudfd,seq(1:168),0)) - std_dev_residual*2         ## Storing the min value-5std dev to compare with real data
  
  

  if(is.na(eval_current)) {                                               ## Checks if data is NA, if it is it sets it to the predicted value
    eval_current <- predict(cloudfd,1,0)
  }


  if( !(maxi  < eval_current) & !(max(0,mini) >= eval_current) ) {        # If it is not an outlier...
    residual <<- residual[-1]
    residual[336] <<- eval_current-predict(cloudfd,1,0)
    pe <<- 0
    index <- cbind(index,i[1])
  }

  if( maxi  < eval_current) {                                             ## To see if if position i in eval_data is bigger than maxi or is NA
    pe <<- eval_current - predict(cloudfd,1,0)
    eval_current <<- predict(cloudfd,1,0)
    residual <<- residual[-1]
    residual[336] <<- 0
    indexup <- cbind(indexup,i[1])
  }

  if( max(0,mini) >= eval_current) {                                      ## To see if if position i in eval_data is smaller than mini or is NA
    eval_current <- pvector1[i-336]                                       ## Take last instead.
    residual <<- residual[-1]
    residual[336] <<- 0
    pe <<- 0
    indexdown <- cbind(indexdown,i[1])
  }


  lscoef <<- lsfit(basismat, eval_sliding, intercept=FALSE)$coef                                 ## using a Least-Square fit to estimate the new
                                                                                                ## coefficients with the new predicted value(s)
  std_dev_residual <<- sd(lsfit(basismat, eval_sliding, intercept=FALSE)$residual, na.rm= TRUE)  ## Updating the residuals for the next step
  cloudfd <<- fd(lscoef,basis,list("Hours", "Week", "Requests"))                                 ## Defining a functional data object again for the new loop
  AR <<- lsfit(Lag(residual,1), residual, intercept=TRUE )$coef                                  ## Refitting
  confidens<-qnorm(0.975)*maxi/sqrt(336)
  print(confidens)
  pvector1[i-335] <<- predict(cloudfd,seq(1,5),0) + AR[[1]] + AR[[2]] * residual[336] + pe                      ## storing the prediction values in a vector using the AR model on residuals
  poutpred<-(predict(cloudfd,seq(1,number_of_predictions),0,se.fit=TRUE) + AR[[1]] + AR[[2]] * residual[336] + pe)
  result<-c(poutpred,confidens)
}


