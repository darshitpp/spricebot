from telegram.ext import Updater, CommandHandler
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import matplotlib
# Added the next line because apparently, heroku doesn't support matplotlib using tkinter (which it uses by default)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import logging
from io import BytesIO
from telegram.ext.dispatcher import run_async

# You'd need an Alphavantage API key to get the data
alphaVantage_apiKey = os.environ['ALPHAVANTAGE']
telegramKey = os.environ['TELEGRAM']
PORT = int(os.environ.get('PORT', '8443'))

@run_async
def start(bot, update):
    getHelp(bot, update)

@run_async
def getHelp(bot, update):
    helpMessage = '''/daily: Fetches the daily High, Low, Open, Close, Volume for a company listed on NSE \n\n
    e.g. <pre> /daily IDFC </pre>\n\n
    /crypto: Fetches the graph for Cryptocurrency in INR \n\n
    e.g. <pre> /crypto BTC </pre>\n\n
    /graph: Fetches the real time(1 min) graph for the companies listed on NSE. \n\n
    e.g. <pre> /graph IDFC </pre> shows the intraday graph for IDFC \n\n
    Disclaimer: This bot is a work in Progress'''
    
    # Sends the above formatted message to the user
    update.message.reply_html(helpMessage)

@run_async
def getGraph(bot, update, args):   
    
    try:
        # The args contain the company name
        stockName = " ".join(args).upper()
        
        # Call the constructor of the Alphavantage API wrapper
        ts = TimeSeries(key=alphaVantage_apiKey, output_format='pandas')
        
        # Calls the method to fetch intraday prices
        # The .NS is to let the API know we want the prices from NSE
        data, meta_data = ts.get_intraday(stockName+".NS", outputsize='compact')
        # Find the documentation of the Alphavantage API at https://github.com/RomelTorres/alpha_vantage
        
        #Plotting the close values
        data['4. close'].plot()
        
        plt.tight_layout()
        
        #Setting the Graph title
        plotTitle = 'Intraday price for {} (1 min)'.format(stockName)
        plt.title(plotTitle)
        
        # Using a Python Util called Temporary file in order to convert the graph into a file object
        #tmpfile = tempfile.TemporaryFile(suffix=".png")
        tmpfile = BytesIO()
        plt.savefig(tmpfile, format="png")
        tmpfile.seek(0)
        img = tmpfile
        
        # Currently doesn't work :(
        update.message.reply_photo(img)
        plt.close()

    except Exception as e:
        # Catches the exception and prints the stack trace
        logging.exception("message")
        message = '''You probably used the incorrect format for the command.\nUse /graph <pre>'companyName' </pre> \nFor more info, please check /help'''
        # If any exception, send the message showing the frequent cause of exception
        update.message.reply_html(message)
        

@run_async
def getDaily(bot, update, args):
    
    try:
        
        # The args contain the company name
        stockName = " ".join(args).upper()
        
        # Call the constructor of the Alphavantage API wrapper
        ts = TimeSeries(key=alphaVantage_apiKey, output_format='pandas')
        
        # Calls the method to fetch daily prices
        # The .NS is to let the API know we want the prices from NSE
        data, meta_data = ts.get_daily(stockName+".NS", outputsize='compact')
        # Find the documentation of the Alphavantage API at https://github.com/RomelTorres/alpha_vantage

        # Fetches the last data array as the most recent data is at the end
        openVal, highVal, lowVal, closeVal, volume = data.iloc[-1]
        
        message = '''
        <b> {} </b> 
        \n Open: <em>₹{}</em>
        \n Close: <em>₹{}</em>
        \n High: <em>₹{}</em>
        \n Low: <em>₹{}</em>
        \n Volume: <em>{}</em>  
        '''.format(stockName, openVal, closeVal, highVal, lowVal, volume)
        
        # Sends the above formatted message to the user
        update.message.reply_html(message)
        
    except Exception as e:
        # Catches the exception and prints the stack trace
        logging.exception("message")
        message = '''You probably used the incorrect format for the command.\nUse /daily <pre>'companyName' </pre> \nFor more info, please check /help'''
        # If any exception, send the message showing the frequent cause of exception
        update.message.reply_html(message)

@run_async        
def getCrypto(bot, update, args):
    
    try:
        # The args contain the crypto name
        cryptoName = " ".join(args).upper()

        # Call the constructor of the Alphavantage API wrapper
        cc = CryptoCurrencies(key=alphaVantage_apiKey, output_format='pandas')
        
        # Calls the method to fetch intraday prices
        data, meta_data = cc.get_digital_currency_intraday(cryptoName, market='USD')
        
        #Plotting the close values
        data['1a. price (USD)'].plot()
        # To show all of the graph, since crypto prices can spike a lot
        plt.tight_layout()
        
        #Setting the Graph title
        plotTitle = 'Intraday price for {}'.format(cryptoName)
        plt.title(plotTitle)
        
        # Using a Python Util called Temporary file in order to convert the graph into a file object
        #tmpfile = tempfile.TemporaryFile(suffix=".png")
        tmpfile = BytesIO()
        plt.savefig(tmpfile, format="png")
        tmpfile.seek(0)
        img = tmpfile

        # Calls the method to fetch daily prices
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
         \n Low: <em>${}</em>
         \n Volume: <em>{}</em>
         \n Market Cap: <em>${}</em> 
        '''.format(cryptoName, openUSD, highUSD, lowUSD, closeUSD, volume, marketCapUSD)
        
        # Commented the next line because it doesn't work. Id did locally though :(
        update.message.reply_photo(img)
        plt.close()

        # Sends the above formatted message to the user
        update.message.reply_html(message)
        
    except Exception as e:
        # Catches the exception and prints the stack trace
        logging.exception("message")
        message = '''You probably used the incorrect format for the command.\nUse <pre>/crypto <pre>'companyName' </pre>\nFor more info, please check /help'''
        # If any exception, send the message showing the frequent cause of exception
        update.message.reply_html(message)
        
def main():
    # Create Updater object and attach dispatcher to it
    updater = Updater(telegramKey)
    dispatcher = updater.dispatcher

    # Add command handlers to dispatcher
    # These will map the user commands to the methods written here
    # e.g. CommandHandler('daily', getDaily) will call the getDaily() function when the user queries /daily in the chat
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
    
    # Connecting to Telegram through webhooks, as running a program is different than deploying as a website
    # Purpose of Webhook: When Telegram receives the command, it will route the command to this script
    updater.start_webhook(listen="0.0.0.0",port=PORT,url_path=telegramKey)
    updater.bot.set_webhook("https://spricebot.herokuapp.com/" + telegramKey)

    # Run the bot until you press Ctrl-C
    updater.idle()

# Checks if the sript is run directly, or through another script
# If run directly, it will call the main() method
if __name__ == '__main__':
    main()
