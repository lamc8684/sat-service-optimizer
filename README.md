# sat-service-optimizer

## How to run:
1. Install dependencies with requirements.txt
2. From the root directory run `python cli/main.py`
    a. For more options run `python cli/main.py --help`
    b. For example, `python cli/main.py --maximum-fuel-capacity-kg 30` to specify a different maximum fuel capacity

## Implementation:
This script uses a greedy algorithm to find possible maneuver paths by weighing the revenue to fuel cost for each spacecraft and in each path selecting the next "best" service stop based on weight that are within the fuel reserve constraint. I used ChatGPT to help research algorithms that would help solve this problem and picked this greedy algorithm because I could implement it while understanding really well how each step works. I investigated a few other options, but as I was running out of time and saw how long the original implementation was taking, reimplemented another version that is a very rough approximation of this algorithm. It just takes the next highest ranking without considering other "paths". Depending on the constraints of the problem at hand, this solution may be acceptable (although probably not if you're a company investor). To run the lazy version, run `python cli/main.py --optimizer-algorithm greedy_lazy`. 

This is the result from that algorithm using original indexes:
```
Maximum Revenue: $5750000
62  ->  75  ->  70  ->  50  ->  56  ->  10  ->  13  ->  36  ->  28  ->  72  ->  0  ->  79  ->  8  ->  98  ->  76  ->  77  ->  87  ->  60  ->  86  ->  84  ->  100  ->  64  ->  109  ->  108  ->  39  ->  42  ->  96  ->  81  ->  74  ->  91  ->  83
```

## Todos and other areas of improvements:
1. At least some functional tests. These may have even helped me to catch problems earlier on. I chose to spend most of my time on styling and readability for this assignment.
2. I wanted to make a Docker file to better encapsulate the environment, but ran out of time

## Discussion points:
1. `OptimizerAlgorithm.GREEDY` has an eye watering time complexity of 2^n. Refactoring the code to run as a multi-process pool would help to speed up the process
2. This is an example of where an external library would also probably be most appropriate. This problem has already been solved and especially if we're able to use a linear programming library like pulp.
3. Like I mentioned, the huge trade-offs in this implementation are time to compute vs revenue from the found path. If we're operating in an environment where we're worried about the millions (maybe even the 100 thousands), using an approximation like the one implemented saves heavily on compute costs. A more accurate approximation could have been implemented using a Monte Carlo simulation for example that just picked random indexes and then found the maximum of those simulations.. However, depending on if the desire is to squeeze every dollar, a more inclusive trade study of computing cost vs revenue would have to be conducted. Every CPU and minute run-time leads to costs to the bottom dollar as well.