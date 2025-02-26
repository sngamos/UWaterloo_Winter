# CS453 Assignment 2 

## package1: 

details: exploit fuzzer cannot find single specific 'magic' string input that will induce crash. 

analysis report: 
```
curl http://ugster72d.student.cs.uwaterloo.ca:9000/status/a97e34433e160760ec58d36d464a4d71acf3023beb9530fdd855232820f8a99e
```
output: SUCCESS

## package2: 
details: exploit fuzzer statelessness, cannot find specific multi-byte input, that will cause program to crash, avoids its random mutation heuristic.

analysis report: 
```
curl http://ugster72d.student.cs.uwaterloo.ca:9000/status/c90f1d4d9462c3a638f780e4ea8ed6c98ae952656499a21117e0dd234dd716e7
```
output: SUCCESS

## package3: 
details: exploit fuzzer weakness in generate highly structured inputs, in this case a ascendingly sorted array of bytes.

analysis report: 
```
curl http://ugster72d.student.cs.uwaterloo.ca:9000/status/13bf50666c1f04eb24e50a674c227e76a4d71c2b68d8e37f0a67f021fde59c6a
```
output: SUCCESS

## package4: 
details: exploit the fuzzer’s difficulty producing inputs meeting precise, complex invariants, extremely unlikely via random mutation processes.

analysis report: 
```
curl http://ugster72d.student.cs.uwaterloo.ca:9000/status/b5c42b381d098bcfa4b5e7a7620e5ee241505af2e8c875be6986032359ac34b0
```
output: SUCCESS

## package5: 
details: exploit fuzzer's weakness in satisfying rigid, interdependent structural conditions. The fuzzer has difficulty finding a certain type of input (palindrome) that will crash the program.

analysis report: 
```
curl http://ugster72d.student.cs.uwaterloo.ca:9000/status/3c6ace17a677a7f9de1c6d5406a7c554849c7714e336a403b780bedf1a40b42f
```
output: SUCCESS