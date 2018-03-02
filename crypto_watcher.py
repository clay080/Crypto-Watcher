import requests
import json
import smtplib
import notify2


class CryptoGrabber:
    """Makes a dict of all data from each exchange. soon to be added are
    some commands to auto trade and a option for the user to auto trade by
    sending a email or text back to the notification. """

    def __init__(self):
        self.crypto_dict = {}
        self.coinwatch = []

    def bitstamp(self):
        bitstampdict = {}
        coins = ['xrp', 'ltc', 'eth', 'bch']
        for coin in coins:
                req = requests.get('https://www.bitstamp.net/api/v2/ticker_hour/{}usd/'.format(coin))
                j = json.loads(req.text)
                bitstampdict.update({coin: j})
        if len(bitstampdict.values()) == len(coins):
            self.crypto_dict.update({'bitstamp': bitstampdict})
            return json.dumps(bitstampdict, indent=1)

    def bitrex(self):
        coins = ['LTC', 'XRP', 'DASH']
        bitrexdict = {}
        for coin in coins:
            req = requests.get('https://bittrex.com/api/v1.1/public/getticker?market=USDT-{}'.format(coin))
            j = json.loads(req.text)
            data = j['result']
            bitrexdict.update({coin: data})
        if len(bitrexdict.values()) == len(coins):
            self.crypto_dict.update({'bitrex': bitrexdict})
            return json.dumps(bitrexdict, indent=1)

    def bitsane(self):
        req = requests.get('https://bitsane.com/api/public/ticker')
        j = json.loads(req.text)
        ltcusd = j['LTC_USD']
        btcusd = j['BTC_USD']
        bchusd = j['BCH_USD']
        xrpusd = j["XRP_USD"]
        bitsanedict = {'bitsane': {"ltc": ltcusd, 'btc': btcusd, 'bch':bchusd, 'xrp':xrpusd}}

        self.crypto_dict.update(bitsanedict)
        return json.dumps(bitsanedict)

    def show_alll(self):
        return self.bitstamp(), self.bitrex(), self.bitsane()

    def high_last(self):
        floats = {'bitstamp_last:': float(self.crypto_dict['bitstamp']['last']), 'bitrex_last': float(self.crypto_dict['bitrex']['Last']), 'bitsane_last':float(self.crypto_dict['bitsane']['last'])}
        for k, v in floats.items():
            float_list = [v]
            high = max(float_list, key=float)
            if high == v:
                return k, v

    def low_last(self):

        floats = {'bitstamp_last:': float(self.crypto_dict['bitstamp']['last']), 'bitrex_last': float(self.crypto_dict['bitrex']['Last']), 'bitsane_last':float(self.crypto_dict['bitsane']['last'])}
        for k, v in floats.items():
            float_list = [v]
            low = min(float_list, key=float)
            if low == v:
                return k, v

    def high_ask(self):
        floats = {'bitstamp_high_ask:': float(self.crypto_dict['bitstamp']['ask']),
                  'bitrex_high_ask': float(self.crypto_dict['bitrex']['lowestAsk']),
                  'bitsane_high_ask': float(self.crypto_dict['bitsane']['ask'])}
        for k, v in floats.items():
            float_list = [v]
            high = max(float_list, key=float)
            if high == v:
                return k, v

    def low_ask(self):

        floats = {'bitstamp_low_ask:': float(self.crypto_dict['bitstamp']['ask']),
                  'bitrex_low_ask': float(self.crypto_dict['bitrex']['lowestAsk']),
                  'bitsane_low_ask': float(self.crypto_dict['bitsane']['Ask'])}
        for k, v in floats.items():
            float_list = [v]
            low = min(float_list, key=float)
            if low == v:
                return k, v

    @ staticmethod
    def cost(coinprice, wanted):
        cost = coinprice * wanted
        return 'Cost{}'.format(cost)

    @ staticmethod
    def add_coin(coins):
        with open('coin_watch.txt', 'w') as watch:
            for coin in coins:
                watch.writelines(coin + '\n')
                watch.close()

    @staticmethod
    def send_email(user, password, reciver, subject, textbody):
        TO = reciver.split('@')
        SUBJECT = subject
        TEXT = textbody

        gmail_sender = user
        gmail_passwd = password

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_sender, gmail_passwd)

        Body = '\r\n'.join(['To: %s' % TO,
                            'From: %s' % gmail_sender,
                            'Subject: %s', SUBJECT,
                            '', TEXT])

        try:
            server.sendmail(gmail_sender, [TO], Body)

        except:

            print('error')
        server.quit()

    @staticmethod
    def save_notify_data(wantedlow, wantedhigh, sender, rec, passw):
        with open('wanted.txt', 'w') as wanted:
            with open('email.txt', 'w') as email:
                wanted.writelines('high:' + wantedhigh)
                wanted.writelines('low:' + wantedlow + '\n')
                email.writelines('sender:{}'.format(sender))
                email.writelines('rec:{}'.format(rec) + '\n')
                email.writelines('password:{}'.format(passw) + '\n')

    def notify(self):
        excahngehigh, numhigh = self.high_ask()
        exchangelow, lownum = self.low_ask()
        notify2.init('Crypto Maxy')
        ripple = notify2.Notification('notifies when prices change','High Exchange:{0} Price:{1} Low Exchange:{2} Price{3}'.format(excahngehigh, numhigh, exchangelow, lownum),
                                 'some icon')
        with open('wanted.txt', 'r') as rwanted:
            with open('email.txt', 'r') as remail:
                for h, l in rwanted.readline().split(':'):
                    for s, r, p in remail.readline().split(':'):
                        if float(numhigh) <= float(h):
                            ripple.show()
                            self.send_email(s, p, r, 'High price has met goal',
                                'Exchange:{0} Price{1}'.format(str(excahngehigh), str(numhigh)))
                        elif float(lownum) <= float(l):
                            ripple.show()
                            self.send_email(s, p, r, 'Low price has met goal',
                            'Exchange:{0} Price:{1}'.format(str(exchangelow), str(lownum)))

