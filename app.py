from telegram.ext import Updater, CommandHandler
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tempfile
import os
import logging

alphaVantage_apiKey = os.environ['ALPHAVANTAGE']
telegramKey = os.environ['TELEGRAM']
PORT = int(os.environ.get('PORT', '8443'))

def start(bot, update):
    getHelp(bot, update)


def getHelp(bot, update):
    helpMessage = "/daily: Fetches the daily High, Low, Open, Close, Volume for a company listed on NSE \n\ne.g. <pre> /daily IDFC </pre>\n\n/crypto: Fetches the graph for Cryptocurrency in INR \n\ne.g. <pre> /crypto BTC </pre>\n\n BETA: \n/graph: Fetches the real time(1 min) graph for the companies listed on NSE. \n\ne.g. <pre> /graph IDFC </pre> shows the intraday graph for IDFC \n\n Disclaimer: This bot is a work in Progress"
    update.message.reply_html(helpMessage)

def getGraph(bot, update, args):   
    
    try:
        stockName = " ".join(args).upper()
        
        ts = TimeSeries(key=alphaVantage_apiKey, output_format='pandas')
        data, meta_data = ts.get_intraday(stockName+".NS", outputsize='compact')
       
        data['4. close'].plot()
        plotTitle = 'Intraday price for {} (1 min)'.format(stockName)
        plt.title(plotTitle)
        tmpfile = tempfile.TemporaryFile(suffix=".png")
        plt.savefig(tmpfile, format="png")
        tmpfile.seek(0)
        img = tmpfile
        update.message.reply_photo(img)
        

    except Exception as e:
        logging.exception("message")
        message = '''You probably used the incorrect format for the command.\nUse /graph <pre>'companyName' </pre> \nFor more info, please check /help'''
        update.message.reply_html(message)

def getDaily(bot, update, args):
    
    try:
        stockName = " ".join(args).upper()
        ts = TimeSeries(key=alphaVantage_apiKey, output_format='pandas')
        data, meta_data = ts.get_daily(stockName+".NS", outputsize='compact')
        openVal, highVal, lowVal, closeVal, volume = data.iloc[-1]
        message = '''
        <b> {} </b> 
        \n Open: <em>₹{}</em>
        \n Close: <em>₹{}</em>
        \n High: <em>₹{}</em>
        \n Low: <em>₹{}</em>
        \n Volume: <em>{}</em>  
        '''.format(stockName, openVal, closeVal, highVal, lowVal, volume)
        
        update.message.reply_html(message)
        
    except Exception as e:
        logging.exception("message")
        message = '''You probably used the incorrect format for the command.\nUse /daily <pre>'companyName' </pre> \nFor more info, please check /help'''
        update.message.reply_html(message)
        
def getCrypto(bot, update, args):
    
    try:
        cryptoName = " ".join(args).upper()

        cc = CryptoCurrencies(key=alphaVantage_apiKey, output_format='pandas')
        data, meta_data = cc.get_digital_currency_intraday(cryptoName, market='USD')
        
        
        data['1a. price (USD)'].plot()
        plt.tight_layout()
        plotTitle = 'Intraday price for {}'.format(cryptoName)
        plt.title(plotTitle)
        tmpfile = tempfile.TemporaryFile(suffix=".png")
        plt.savefig(tmpfile, format="png")
        tmpfile.seek(0)
        img = tmpfile

        data, meta_data = cc.get_digital_currency_daily(cryptoName, market='USD')
        dataList = data.iloc[-1]
        
        openUSD = dataList['1a. open (USD)']
        highUSD = dataList['2a. high (USD)']
        lowUSD = dataList['3a. low (USD)']
        closeUSD = dataList['4a. close (USD)']
        volume = dataList['5. volume']
        marketCapUSD = dataList['6. market cap (USD)']
        
        message = '''
         <b> {} </b> 
         \n Open: <em>${}</em>
         \n Close: <em>${}</em>
         \n High: <em>${}</em>
         \n Low: <em>₹{}</em>
         \n Volume: <em>{}</em>
         \n Market Cap: <em>${}</em> 
        '''.format(cryptoName, openUSD, highUSD, lowUSD, closeUSD, volume, marketCapUSD)
        
        #update.message.reply_photo(img)
        update.message.reply_html(message)
        
    except Exception as e:
        logging.exception("message")
        message = '''You probably used the incorrect format for the command.\nUse <pre>/crypto <pre>'companyName' </pre>\nFor more info, please check /help'''
        update.message.reply_html(message)
        
def main():
    # Create Updater object and attach dispatcher to it
    updater = Updater(telegramKey)
    dispatcher = updater.dispatcher

    # Add command handler to dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    help_handler = CommandHandler('help', getHelp)
    dispatcher.add_handler(help_handler)

    graph_handler = CommandHandler('graph', getGraph, pass_args=True)
    dispatcher.add_handler(graph_handler)
    
    daily_handler = CommandHandler('daily', getDaily, pass_args=True)
    dispatcher.add_handler(daily_handler)
    
    crypto_handler = CommandHandler('crypto', getCrypto, pass_args=True)
    dispatcher.add_handler(crypto_handler)
    
    updater.start_webhook(listen="0.0.0.0",port=PORT,url_path=telegramKey)
    updater.bot.set_webhook("https://spricebot.herokuapp.com/" + telegramKey)

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()