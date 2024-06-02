<h1 align="center"> CSP Solver </h1>

<div> This project is a Constraint Satisfaction Problem (CSP) Solver implemented in Python. It supports techniques like forward checking and arc consistency to reduce search space. </div>

Two sample inputs are provided, ex1 and ex2. Sample outputs for ex1 presented in .out files. 

**To Run:**  
3 arguments:  
* **.var file:** contains variables and their domains
* **.con file:** specified constraints
* **consistency enforcing procedure:** `none` or `fc`
	* none: no enforcing procedure is applied, uses backtracking to solve
	* fc: use forward checking to enforce consistency
 
`python main.py ex1.var1 ex1.con none`

