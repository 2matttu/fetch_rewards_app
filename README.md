# Fetch Rewards Coding Exercise Documentation - Matthew Tu

## Overview
To complete this assignment, I used the Flask web framework, a lightweight Python web framework for simple web apps. Since this backend was fairly straightforward, it was a suitable choice.

For storing the transaction data and total balances, I used Python data structures in memory. More on this in the Design and Implementation section.

## Brief Demo
https://youtu.be/ak_-S89ouVU

## Installation Guide
__Note: This project is entirely in Python 3. For larger projects, I would have used a `requirements.txt` file to install all dependencies, but for this project, I will list the `pip3` commands since there are very few (just 2).__

I was using macOS to develop and run this so the setup might be slightly different for Linux and Windows machines.

- Step 0: Download the repository in .zip form or git clone it. Many of the following steps assumes you are in that working directory (where app.py is).
- Step 1: Install the latest stable version of [Python 3](https://www.python.org/downloads/) (as of 3/1 it's 3.12.2 but I'm on 3.9.6 so a relatively new version should also work :). Confirm the installation by running `python` or `python3` in your Terminal.
- Step 2: Now you should also have access to `pip3`, the package manager for Python 3. Using `pip3`, you will install the following packages in the project working directory using Terminal:
```
pip3 install flask
pip3 install requests
```
- That's it! Make sure flask was installed correctly by typing `flask` in a new Terminal window. It should output the usage notes for flask. If there's any issues please consult the [flask documentation](https://flask.palletsprojects.com/en/3.0.x/).

## Starting up the server
__Note: make sure that the entire project directory is executable__

__In the project directory__, enter `flask --app app run` in the Terminal. This will start a local Flask web server on your localhost. It should say `Running on http://127.0.0.1:5000`. http://127.0.0.1:5000 is the root address of the server. It's important to use the correct port as well (5000 in this case).

__If the address is different from the address above, use that address before the route names below.__

## HTTP Route Information

*The full URLs would be: http://127.0.0.1:5000/rewards/transactions, etc*

`/rewards/transactions` (POST)
- This is the route that adds transactions for a specific payer, date and number of points
- It takes 3 required arguments in the JSON request body:
    - `payer`: the name of the payer (non-empty string)
    - `points`: the amount of points (non-zero int)
    - `timestamp`: either a timestamp in the format of `"%Y-%m-%dT%H:%M:%SZ"` OR [Unix Timestamp](https://www.unixtimestamp.com/) as a positive int
- If any 3 arguments are missing or invalid, the route will respond with `400 - Bad Request` and a JSON with error details.
- If the transaction is valid, the server will attempt to commit the transaction. It will return `200 - OK` and a JSON with more info.
```
    {
        "status": "success",
        "message": "Resource created successfully",
        "data": {
            "payer": <payer str>,
            "points": <points int>,
            "timestamp": <unix_timestamp int>
        }
    }
```
- The server will return `400 - Bad Request` if the transaction failed. i.e. if it's a __negative transaction and the payer balance would be negative if the transaction was committed.__

`/rewards/spend` (POST)
- This is the route to spend points, using the oldest points first, and not having any payer account go negative.
- It takes 1 required argument:
    - `points`: the amount of points to spend (positive int)
- If this argument is missing/invalid, it will return `400 - Bad Request` and a JSON with error details.
- If the argument is valid, the server will attempt to commit the spend. It will return `200 - OK` and a JSON with the list of dictionaries with points spent by payer like so:
```
[{'payer': 'DANNON', 'points': -100}, {'payer': 'UNILEVER', 'points': -200}, {'payer': 'MILLER COORS', 'points': -4700}]
```
- The server will return `400 - Bad Request` if the Total Balance of all accounts is too low, as it would result in negative balances.

__Note: Based on my assumption of the problem, my logic is to aggregate the changes to each payer's balance, but still preserving the order of what payer's balance was removed first in the list.__

`/rewards/balances` (GET)
- This is the route to return all payer point balances.
- It doesn't take any required arguments. __Although, in future iterations of this project, it could take arguments such as specific payers, if a client only wants to look at those balances__
- It returns `200 - OK` and a JSON dict of each payer (key) and thier respective balances (value):
```
{'DANNON': 1000, 'MILLER COORS': 5300, 'UNILEVER': 0}
```

## Design and Implementation
- I devided my code into two files - the app server file and database handling file. The app server handled requests from the 3 routes, while the database handler processed the transactions, updated the internal data structure
- One of the most important requirements to this problem was that we wanted the __oldest__ points to be spent first __based on their timestamp and not the order they're received__. To accomplish this in a time-efficient manner, I made the data structure holding all the remaining transactions into a __priority queue__, implemented as a min-heap. I sorted the priority queue by ascending timestamp, so the time complexity of dequeuing the oldest timestamp was `O(log(N))`, where `N` is the number of active transactions. If we stored the transactions in a linear array, we would always have to do a linear `O(N)` scan of all transactions to find the one with the earliest timestamp. Thus, my implementation, as the number of active transactions increase, would be far more scalable than a linear array approach.
    - The tradeoff is the time complexity of adding a transaction. Where a transaction can be added in `O(1)` time in a linear array approach, my approach needs `O(log(N))` to maintain the heap invariant. However, in a more sophisticated system, the `O(log(N))` work to maintain the heap invariant could be done asynchronously.
    - The overall time complexity of one `spend` route is `O(M*log(N))`, where `M` is the number of point transactions removed during the route. When `M` is small, the advantages of the heap approach shines, and as `M` approaches `N`, the time savings decrease.
- To maintain code cleanliness, I made sure to implement certain helper functions, like `dt_to_ts()` which converts a certain format of datetime to UNIX timestamp, as well as `error_json_res()`, which generates an error JSON response for to handle multiple invalid/missing argument cases. I also implemented `__update_balances()` in my database class to tightly couple balance processing, avoiding potential human error if I had hard coded the balance changes to both individual and total balances.
- On negative transactions: I treat negative transactions almost the same as positive transactions. When the database logic of a `spend` route encounters a negative transaction, it will subtract the negative value from the remaining `points` left to process, essentially adding more points. This increase would still never cause a negative balance, as the negative balance is already accounted for in the total balance in the intial balance check. It would also "add" to the overall change of balances for that payer. For instance, in the PDF example, the change went from -300 (`{ "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }`) back to -100 from (`{ "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" }`), which was the ultimate change for `"DANNON"`. At least that's how I interpreted it. Note that this can result in positive values in the list returned by the spend route.
- __For more implementation details, please look at the docstrings and other comments in the source code!__

## Testing
__IMPORTANT__: You NEED be running the server using `flask --app app run` before running each test. Before running another test, you NEED to stop and re-launch the server to clear the transaction data.

Separate from the backend code itself, I created a basic `run_tests.py` script. To use, you can directly run it in the working directory using `python3 run_tests.py <test_no>`, where `test_no` is the following:

- __`0`: orignal test case in the original PDF__
    - expected output: see orig PDF
- `1`: spending exactly the total balance
    - same inputs as case 0, except spend call is the entire total balance
    - expected output: ending balances of zero, no errors should be returned
- `2`: spending more than the allowed balance
    - same inputs as case 0 + 1, except spend call is one more than total balance
    - expected output: 400 error on spend request (balance too low)
- `3`: negative transaction equal to and more than current points for that payer
    - adds 1000 to DANNON and 200 to UNILEVER, and then attempts negative transactions of -1000 for DANNON and -201 for UNILEVER
    - expected output: 200 OK on DANNON neg. transaction. 400 INVALID on UNIVEVER
- `4`: invalid/missing inputs
    - call 1: missing payer
    - call 2: missing points
    - call 3: missing timestamp
    - call 4: invalid payer (not string)
    - call 5: invalid points (0)
    - call 6: invalid timestamp (negative)
- __`5`: stress test/making sure priority queue works__
    - *Note: I put `sleep()` calls to make the input more readable and not happen all at once*
    - This test uses a fixed list of positive transactions - some with payer='OLDEST' with the oldest timestamps, payer='NEWEST' with most recent timestamps, and payer = 'MIDDLE' with timestamps in between. The test then randomizes the order in which the transactions are posted to the server. The test then spends all the points in equal increments. Because the timestamps, not insertion order determines spending order, the spending calls should return the same output below. All the points will be spent, so the ending balance should be 0 after the spends. This test will loop a total of 10 times to ensure reliability.
```
----SPENDING POINTS----

Sending POST request to /rewards/spend: {'points': 200}
POST response:
200
[{'payer': 'OLDEST', 'points': -200}]


Sending POST request to /rewards/spend: {'points': 200}
POST response:
200
[{'payer': 'OLDEST', 'points': -100}, {'payer': 'MIDDLE', 'points': -100}]


Sending POST request to /rewards/spend: {'points': 200}
POST response:
200
[{'payer': 'MIDDLE', 'points': -200}]


Sending POST request to /rewards/spend: {'points': 200}
POST response:
200
[{'payer': 'MIDDLE', 'points': -100}, {'payer': 'NEWEST', 'points': -100}]


Sending POST request to /rewards/spend: {'points': 200}
POST response:
200
[{'payer': 'NEWEST', 'points': -200}]


----CHECKING BALANCE----
Sending GET request to /rewards/balances
GET Response:
200
{'MIDDLE': 0, 'NEWEST': 0, 'OLDEST': 0}
```
- `6`: small spends of 1
    - creates a transaction of random positive number. calls spends of 1 and checks if the random number equals the number of successful spends. also confirms that balance is zero.
- `7`: custom test case
    - you can use `test_add_transaction()`, `test_spend()`, and `test_balance()` to create your own tests. For `test_add_transaction()`, `test_spend()`, you need to provide a request body in the form of a Python Dictionary.

__Note__: if your base URL for the slack server is different from http://127.0.0.1:5000/, you will have


## Limitations
- __Data Durability and Race Conditions__: This in-memory pseudo database is *supposingly* thread-safe because of CPython's [GlobalInterpretorLock](https://wiki.python.org/moin/GlobalInterpreterLock), preventing race conditions if multiple clients send parallel requests. That being said, GlobalInterpretorLock will degrade performance because only one request can have access to the "Database" at a time. Also, since it's stored in memory, the data is wiped every time the server is quit.
- __Scalability__: Real financial transaction systems probably serve millions of requests a minute. We would need multiple application servers, caching, database, and other services to maintain good availability, latency, and so on. The codebase itself would also have to adhere to stricter design principles.
- __Cleaning up "-x" and "+x" transactions__: There can in theory be a string of positive +x, negative -x transactions that will not allow to "spend" route to clear them out, as the technical balance would be 0. __One of my assumptions was that negative transactions are much more rare than positive ones, i.e. a points adjustment after refuding a purchase that originally gave you points__. However, we could implement a periodic cleanup routine that clears those transactions out.

## Hypothetical Next Steps
- Logging
- More comprehensive and automated testing
- Database integration
- More complex routes and arguments
- Async procedures and cleaup procedures

## Thank you!
