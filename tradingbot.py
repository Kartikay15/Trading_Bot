from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from dotenv import load_dotenv, dotenv_values
from alpaca_trade_api import REST
from timedelta import Timedelta
from finbert_utils import estimate_sentiment

config=dotenv_values(".env")
API_KEY = config['API_KEY']
API_SECRET = config['SECRET_KEY']
BASE_URL ="https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY":API_KEY,
    "API_SECRET":API_SECRET,
    "PAPEr":True
}

class MLTrader(Strategy):
    def initialize(self, symbol:str="SPY",cash_at_risk:float=0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL,key_id=API_KEY,secret_key=API_SECRET)
        
    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk/last_price)
        return cash,last_price,quantity

    def get_dates(self):
        today = self.get_datetime()
        threee_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), threee_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol,
                                 start=three_days_prior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probalility, sentiment = estimate_sentiment(news)
        return probalility,sentiment

    def on_trading_iteration(self):
        cash,last_price,quantity = self.position_sizing()
        probalility, sentiment = self.get_sentiment()
        
        if cash>last_price :
            if sentiment == "positive" and probalility > 0.9: 
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    10,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price*1.20,
                    stop_loss_price=last_price*0.95
                )
                self.submit_order(order)
                self.last_trade = "buy"

            elif sentiment == "negative" and probalility > 0.9: 
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    10,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price*0.8,
                    stop_loss_price=last_price*1.05
                )
                self.submit_order(order)
                self.last_trade = "sell"    


start_date = datetime(2020,1,1)
end_date = datetime(2023,12,31)

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat',
                    broker=broker,
                    parameters={"symbol":"SPY",
                                "cash_at_risk":0.5})

strategy.backtest(YahooDataBacktesting,
                  start_date,
                  end_date,
                  parameters={"symbol":"SPY","cash_at_risk":0.5})


