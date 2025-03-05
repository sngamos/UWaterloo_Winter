# Assignment 2 Report Submission

**Group**:  
**Names**: Sng Amos, Pea Darren  
**Student ID**: 21175177,  

## 1. MLE and MAP Derivation
### 1. MLE Derivation
Key information from assignment brief:
N samples, $x_1,...,x_i,...,x_N$  
$x_i \sim Kumaraswamy(a,b): f(x|a,b) = abx^{\alpha -1}(1-x^\alpha)^{(b-1)}$, where $x_i \in (0,1)$
$a$ is known, and we want to estimate $b$

#### (a) Define likelihood function
Given N independent samples, the likelihood function is:  
$L(b) = \prod_{i=1}^{N}{f(x_i|a,b)}=\prod_{i=1}^{N}[abx_i^{\alpha -1}(1-x_i^\alpha)^{(b-1)}]$
#### (b) log likelihood
$\ln{L(b)} = \ln{[\prod_{i=1}^{N}[abx_i^{\alpha -1}(1-x_i^\alpha)^{(b-1)}]]}$  
$=\sum_{i=1}^{N}{\ln{[abx_i^{\alpha -1}(1-x_i^\alpha)^{(b-1)}]}}$  
$= \sum_{i=1}^{N}{[\ln{(a)+\ln{(b)}+(\alpha-1)\ln{(x_i)}+(b-1)\ln{(1-x_i^a)}}]}$   
$= N\ln{(a)} + N\ln{(b)} + (a-1)\sum_{i=1}^{N}{\ln{(x_i)}} + (b-1)\sum_{i=1}^{N}{\ln{(1-x_i^a)}}$

#### (c) Differentiate the log-likelihood w.r.t $b$
$\frac{d}{db}[{N\ln{(a)} + N\ln{(b)} + (a-1)\sum_{i=1}^{N}{\ln{(x_i)}} + (b-1)\sum_{i=1}^{N}{\ln{(1-x_i^a)}}}]$  
$=0+ \frac{N}{b} + 0 +  \sum_{i=1}^{N}{\ln{(1-x_i^a)}}$

#### (d) Equating the derivative to 0 and solving
$\frac{N}{b} + \sum_{i=1}^{N}{\ln{(1-x_i^a)}} = 0$  
$b = -\frac{N}{\sum_{i=1}^{N}{\ln{(1-x_i^a)}}}$

MLE for $b$ is $-\frac{N}{\sum_{i=1}^{N}{\ln{(1-x_i^a)}}}$

### 2. MAP Derivation
$p(b|x_1,...x_N) \propto L(b)p(b)$  

From above we know,  
$L(b) = \prod_{i=1}^{N}[abx_i^{\alpha -1}(1-x_i^\alpha)^{(b-1)}]$

From the passage we know,  
$b \sim \mathcal{N}{(\mu,\sigma^2)} = e^{-\frac{(b-\mu)^2}{2\sigma^2}}$ 
#### (a) Log posterior including prior
$\ln{p(b)} = \ln{e^{-\frac{(b-\mu)^2}{2\sigma^2}}} =-\frac{(b-\mu)^2}{2\sigma^2} $ 
From the likelihood from part 1,
$L(b) = N\ln{(a)} + N\ln{(b)} + (a-1)\sum_{i=1}^{N}{\ln{(x_i)}} + (b-1)\sum_{i=1}^{N}{\ln{(1-x_i^a)}}$
since $N\ln(a)$ and $(a-1)\sum_{i=1}^{N}{\ln{(x_i)}}$ depend on a known $a$, they are constant, we can simplify $L(b)$ into,
$L(b) =(b-1)\sum_{i=1}^{N}{\ln{(1-x_i^a)}} + constant$
For the prior we can ignore the normalizing constant that does not depend on b,
$\ln{p(b|x_1,...,x_N)} = \ln{L(b)} + \ln{p(b)}$
$ = N\ln{(b)} + (b-1)\sum_{i=1}^{N}{\ln{(1-x_i^a)}} -\frac{(b-\mu)^2}{2\sigma^2}$

#### (b) Differentiate the log-posterior w.r.t $b$
$\frac{d}{db}\ln{p(b|x_1,...,x_N)} =\frac{d}{db} [N\ln{(b)} + (b-1)\sum_{i=1}^{N}{\ln{(1-x_i^a)}} -\frac{(b-\mu)^2}{2\sigma^2}]$ 
$= \frac{N}{b} + \sum_{i=1}^{N}{\ln{(1-x_i^a)}} - \frac{(b-\mu)}{\sigma^2}$

#### (c) Equate derivative to 0 and solve
$\frac{N}{b} + \sum_{i=1}^{N}{\ln{(1-x_i^a)}} - \frac{(b-\mu)}{\sigma^2} =0$
$\frac{\sigma^2N}{b} + \sigma^2\sum_{i=1}^{N}{\ln{(1-x_i^a)}} - (b-\mu) = 0$
$-b^2 + b\mu +b\sigma^2\sum_{i=1}^{N}{\ln{(1-x_i^a)}} + \sigma^2N= 0$
$b^2 -b[\mu+\sigma^2\sum_{i=1}^{N}{\ln{(1-x_i^a)}}]-\sigma^2N =0 $
Simplifying the equation by substitutions,
$C = \mu+\sigma^2\sum_{i=1}^{N}{\ln{(1-x_i^a)}}$ and $ D = \sigma^2N$
we get the simplified form,
$b^2 - Cb -D =0$
then solving with the general solution to quadratic equations,
$b=\frac{C\pm\sqrt{C^2+4D} }{2}$
since b>0 we choose the positive root, then substituting the initial constants back,
$\hat{b}_{MAP} = \frac{\mu+\sigma^2\sum_{i=1}^{N}{\ln{(1-x_i^a)}}+\sqrt{(\mu+\sigma^2\sum_{i=1}^{N}{\ln{(1-x_i^a)}})^2+4\sigma^2N}}{2}$








