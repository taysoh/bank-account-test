## how to install (required python 3.4 or higher)
-- 1. Clone repo and enter folder `git clone https://github.com/taysoh/bank-account-test.git bank` cd `bank`
-- 2. Create environment `python3 -m venv env`
-- 3. Activate it `source env/bin/activate`
-- 4. Install dependencies `pip install -r requirements.txt`
-- 5. run server `python3 ./transactions/main.py`

you'll able to test sockets on page `http://0.0.0.0:8080/`

### Test applications for multi-currency bank account that.

Assume we are building the back-end for a multi-currency bank account to support 5
currencies, 'USD', 'GBP', 'EUR', 'JPY' and 'RUB'.

Please provide a websocket interface that can handle the following messages:

{'method': 'deposit',
'account': 'bob',
'amt' : 10,
'ccy': 'EUR'}

{'method': 'withdrawal,
'account': 'alice',
'amt' : 10,
'ccy': 'EUR'}

{'method': 'transfer',
'from_account': 'alice',
'to_account': 'bob',
'amt': 100,
'ccy': 'GBP'}

{'method': 'get_balances',
'date': '2018-10-01',
'account': 'bob'}
Deposits, withdrawals and transfers should debit and credit the appropriate
accounts. When we call get_balances we should see a result like:

{'date' : '2018-10-01'
'balances':
{
'USD': 0,
'EUR': 10,
'GBP': 0,
'JPY': 0,
'RUB': 20
}
}
To comply with anti money laundering checks, the total value of the the
transfers that can be made from one account in a consecutive 5 day period is
10,000 eur. If this occurs we should not allow the transfer.

You may need exchange rate data to calculate the value of the transfers in EUR,
this can be obtained from http://openrates.io/

Feel free to solve this problem using a database, or, if you prefer, in memory.