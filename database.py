import heapq
from collections import defaultdict


class RewardsDatabase:
    '''
    In-Memory "Database" of our solution

    Transaction "schema" (python tuple):
    (
        UNIX timestamp: int,
        points: int,
        payer: str
    )

    Transactions stored in a min-heap
    priority queue by earliest timestamp
    '''
    def __init__(self):
        # priorirty q sorts by earliest timestamp
        self.transaction_queue = []

        # total and per-payer balances
        self.total_balance = 0
        self.balances = defaultdict(int)

    def __update_balances(self, payer, change):
        '''
        Updates balance for payer and overall balance
        '''
        self.balances[payer] += change
        self.total_balance += change

    def add_transaction(self, payer, points, timestamp):
        '''
        Adds transaction to "database" and updates
        overall balances

        Returns:
        (True, '') on success
        (False, <error info string>) on error
        '''
        if self.balances[payer] + points < 0:
            return False, 'Balance is too low'
        # add transaction element to priorty queue (heap)
        transaction = (timestamp, points, payer)
        heapq.heappush(self.transaction_queue, transaction)

        self.__update_balances(payer, points)
        return True, ''

    def spend_points(self, points):
        '''
        Spends points.

        Returns:
        (True, <spend list>) on success
        (False, <error info string>) on error
        '''
        if points > self.total_balance:
            return False, 'Balance is too low'

        spent_dict = {}  # aggregate balance change per payer
        order_list = []  # preserve order

        while points > 0:
            # head of min heap always the oldest
            oldest = self.transaction_queue[0]
            timestamp, p_oldest, payer = oldest
            spent = 0
            if p_oldest > points:
                # transaction still has balance: decrease its points
                self.transaction_queue[0] = (timestamp, p_oldest - points, payer)
                spent = points
                points = 0
            else:
                # transaction is fully consumed: remove from queue
                heapq.heappop(self.transaction_queue)
                points -= p_oldest
                spent = p_oldest

            self.__update_balances(payer, -spent)
            if payer not in spent_dict:
                spent_dict[payer] = 0
                order_list.append(payer)
            spent_dict[payer] -= spent

        res_list = []

        for payer in order_list:
            if spent_dict[payer] != 0:
                res_list.append({
                    'payer': payer,
                    'points': spent_dict[payer]
                })

        return True, res_list

    def get_balance(self):
        '''
        Returns dictionary of balances for
        all existing payers
        '''
        return dict(self.balances)
