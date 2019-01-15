import datetime
import json
from collections import defaultdict

import aiohttp
import aiohttp_jinja2
from aiohttp import web


class Payments:
    CURRENCIES = ["USD", "GBP", "EUR", "JPY" ,"RUB"]
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSFER = 'transfer'
    BALANCE = 'get_balances'
    TRANSACTION_TYPES = [DEPOSIT, WITHDRAWAL, TRANSFER, BALANCE]
    TRANSACTIONS = defaultdict(list)

    def __init__(self, data, rates):
        self.rates = rates
        self.method = data.get('method')
        self.data = data
        self.transactions = self.TRANSACTIONS[self.data.get('from_account')]
        if not self.method == self.BALANCE:
            self.data['date'] = datetime.date.today()
            data['amt'] = float(data['amt'])

            if self.method == self.TRANSFER:
                self.recipient_transactions = self.TRANSACTIONS[self.data.get('to_account')]
            self.used_limit = self.get_used_amount_euro()
            self.euro_amount = self.get_current_amount_euro()
        else:
            self.used_limit = self.euro_amount = 0

    def validate_data(self):
        if not self.method or self.method not in Payments.TRANSACTION_TYPES:
            return False, {'action': 'error', 'text': "Method not allowed"}

        if not self.data.get('from_account'):
            return False, {'action': 'error', 'text': "from user required"}

        if self.method == self.TRANSFER and not self.data.get('to account'):
            return False, {'action': 'error', 'text': "to user required"}

        return True, ''

    def get_current_amount_euro(self):
        currency = self.data.get('ccy')
        return abs(self.data.get('amt')) / self.rates.get(currency, 1)

    def get_used_amount_euro(self):
        last_5_days_transactions = filter(
            lambda x: x['date'] <= datetime.date.today() - datetime.timedelta(days=5),
            self.transactions
        )
        amount = sum([abs(x.get('amt')) / self.rates.get(x.get('ccy'), 1) for x in last_5_days_transactions])
        return amount

    def check_limit(self):
        return self.euro_amount > 10000 or self.euro_amount + self.used_limit > 10000

    def deposit(self):
        self.transactions.append(self.data)
        return "{} success".format(self.method)

    def withdrawal(self):
        self.data['amt'] = self.data['amt'] * -1
        self.transactions.append(self.data)
        return "{} success".format(self.method)

    def transfer(self):
        self.recipient_transactions.append(self.data)
        self.data['amt'] = self.data['amt'] * -1
        self.transactions.append(self.data)
        return "{} success".format(self.method)

    def get_balances(self):
        date = self.data.get('date')
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        date_transactions = filter(lambda x: x.get('date') == date, self.transactions)
        transactions_by_currency = defaultdict(list)
        [transactions_by_currency[x['ccy']].append(x['amt']) for x in date_transactions]
         # example of output defaultdict(list, {'EUR': [22.0], 'USD': [11.0, -2.0]})"

        # fill missed currencies
        for c in self.CURRENCIES:
            if c not in transactions_by_currency:
                transactions_by_currency[c] = [0]

        return {
            "date": date.strftime('%Y-%m-%d'),
            "balances": {x: sum(y) for x, y in transactions_by_currency.items()}
        }

    def proceed(self):
        valid, errors = self.validate_data()
        if not valid:
            return errors
        if self.check_limit():
            return {'action': 'error', 'text': "user reach 5 days limit"}

        return {'action': 'success', 'text': getattr(self, self.method)()}


async def index(request):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        data = {
            'currencies': Payments.CURRENCIES,
            'transaction_types': Payments.TRANSACTION_TYPES
        }
        return aiohttp_jinja2.render_template('index.html', request, data)

    await ws_current.prepare(request)
    request.app['websockets'].append(ws_current)
    while True:
        msg = await ws_current.receive()
        if msg.type == aiohttp.WSMsgType.text:
            data = json.loads(msg.data)

            payment = Payments(data, request.app['rates'])
            await ws_current.send_json(payment.proceed())
        else:
            break

    del request.app['websockets'][request.app['websockets'].index(ws_current)]

    return ws_current