import requests
import sys
import random
from time import sleep
from urllib.parse import urljoin


# Base URL for testing
URL = "http://127.0.0.1:5000"


def test_add_transaction(post_json):
    print('Sending POST request to /rewards/transactions: {}'.format(post_json))
    response_post = requests.post(urljoin(URL, 'rewards/transactions'), json=post_json)
    print('POST response:')
    print(response_post.status_code)
    print(response_post.json())
    print("\n")
    return response_post.status_code


def test_spend(post_json):
    print('Sending POST request to /rewards/spend: {}'.format(post_json))
    response_post = requests.post(urljoin(URL, 'rewards/spend'), json=post_json)
    print('POST response:')
    print(response_post.status_code)
    print(response_post.json())
    print("\n")
    return response_post.status_code


def test_balance():
    print('Sending GET request to /rewards/balances')
    response_get = requests.get(urljoin(URL, 'rewards/balances'))
    print("GET Response:")
    print(response_get.status_code)
    print(response_get.json())
    print("\n")
    return response_get.status_code


def test_main():
    '''
    See README.md for more details and expected output
    '''
    if len(sys.argv) < 2:
        print("Usage: python3 run_tests.py <test_no>")
        return
    else:
        arg1 = sys.argv[1]

    if arg1 == '0':
        # Test Case 0: Original Test Case

        post_data_list = [
            {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"},
            {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"},
            {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"},
            {"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"},
            {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"},
        ]

        for data in post_data_list:
            test_add_transaction(data)

        test_spend({"points": 5000})

        test_balance()
    elif arg1 == '1':
        # Test Case 1: Spending Exactly the Total Balance
        post_data_list = [
            {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"},
            {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"},
            {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"},
            {"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"},
            {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"},
        ]
        for data in post_data_list:
            test_add_transaction(data)

        test_spend({"points": 11300})

        test_balance()
    elif arg1 == '2':
        # Test Case 2: Spending more than the allowed balance
        post_data_list = [
            {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"},
            {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"},
            {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"},
            {"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"},
            {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"},
        ]
        for data in post_data_list:
            test_add_transaction(data)

        test_spend({"points": 11301})

        test_balance()
    elif arg1 == '3':
        # Test Case 3: Valid and invalid negative transactions
        post_data_list = [
            {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"},
            {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z"},
            {"payer": "DANNON", "points": -1000, "timestamp": "2020-10-31T15:00:00Z"},
            {"payer": "UNILEVER", "points": -201, "timestamp": "2020-10-31T11:00:01Z"}
        ]
        for data in post_data_list:
            test_add_transaction(data)

        test_balance()
    elif arg1 == '4':
        # Test Case 4: missing/invalid inputs
        post_data_list = [
            {"points": 1000, "timestamp": "2020-11-02T14:00:00Z"},
            {"payer": "UNILEVER", "timestamp": "2020-10-31T11:00:00Z"},
            {"payer": "DANNON", "points": 200},
            {"payer": 1, "points": 10000, "timestamp": "2020-11-01T14:00:00Z"},
            {"payer": "DANNON", "points": 0, "timestamp": "2020-10-31T10:00:00Z"},
            {"payer": "DANNON", "points": 300, "timestamp": -10000}
        ]
        for data in post_data_list:
            test_add_transaction(data)
    elif arg1 == '5':
        # Test Case 5: Stress test/priority queue check
        post_data_list = [
            {"payer": "OLDEST", "points": 100, "timestamp": 1},
            {"payer": "OLDEST", "points": 100, "timestamp": 2},
            {"payer": "OLDEST", "points": 100, "timestamp": 3},
            {"payer": "MIDDLE", "points": 100, "timestamp": 4},
            {"payer": "MIDDLE", "points": 100, "timestamp": 5},
            {"payer": "MIDDLE", "points": 100, "timestamp": 6},
            {"payer": "MIDDLE", "points": 100, "timestamp": 7},
            {"payer": "NEWEST", "points": 100, "timestamp": 8},
            {"payer": "NEWEST", "points": 100, "timestamp": 9},
            {"payer": "NEWEST", "points": 100, "timestamp": 10},
        ]
        for i in range(10):
            random.shuffle(post_data_list)
            print('----ADDING TRANSACTIONS IN RANDOM ORDER----\n')
            sleep(2)
            for data in post_data_list:
                test_add_transaction(data)
                sleep(0.5)
            print('----SPENDING POINTS----\n')
            for j in range(5):
                test_spend({"points": 200})
                sleep(1)
            print('----CHECKING BALANCE----')
            test_balance()
            sleep(4)
    elif arg1 == '6':
        # Test Case 6: spends of 1
        rand_int = random.randint(20, 30)
        print('Will add transaction of {} points'.format(rand_int))
        test_add_transaction({"payer": "DANNON", "points": rand_int, "timestamp": 10})
        spend_calls = 0
        while True:
            if test_spend({'points': 1}) == 200:
                spend_calls += 1
            else:
                break
        test_balance()
        if spend_calls == rand_int:
            print('Test OK: {} == {}'.format(
                rand_int, spend_calls
            ))
        else:
            print('Test Failure! Expected {} successful spends but got {}'.format(
                rand_int, spend_calls
            ))
    elif arg1 == '7':
        # Test Case 7: Custom
        pass
    else:
        print("Usage: python3 run_tests.py <test_no>")


if __name__ == "__main__":
    test_main()
