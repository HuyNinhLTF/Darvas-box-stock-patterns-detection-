from vnstock import *
import datetime
from concurrent.futures import ThreadPoolExecutor
import mplfinance as mpf

# get all tickers in stock market
def get_securities_list():
    # get df from api
    df_name = listing_companies()
    # get tickers from hose and hnx
    list_name = df_name['ticker'].loc[ (df_name['comGroupCode'] == 'HOSE') | (df_name['comGroupCode']=='HNX')  ]
    # convert dataframe into list
    list_name1 = list_name.tolist()
    # remove etf
    final_list = [i for i in list_name1 if len(i) == 3]
    return final_list

# get data from 1 stock
def fetch_data(symbol):
    try:
        daily_stock_price = get_daily_price(symbol)
        return symbol, daily_stock_price
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# get multiple stock datas by paralleling
def parallel_fetch_data(symbols):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_data, symbols))
    return [result for result in results if result is not None]

# def candle type
def candle_type(ohlc_price):
    HC_index = ohlc_price['high'] / ohlc_price['close']
    CL_index = ohlc_price['close'] / ohlc_price['low']
    return 'doji or red body' if HC_index >= 1.02 else ('hammer or green body' if CL_index >= 1.02 else 'normal')


def map_candle_type(candle):
    return 1 if candle == 'doji or red body' else 0

def check_flat_base(row):
    flat_base_value = row['flat base value']
    value = row['value']
    count_bad_candles = row['count bad candles']
    close = row['close']
    ma_200 = row['ma 200']
    if flat_base_value < 0.08 and value > 15000000000 and close > 10000 and count_bad_candles < 4:
        return 'yes'
    else:
        return 'no'


def get_daily_price(name, start_date='2024-01-01', end_date = None):
    if end_date is None:
        end_date = datetime.datetime.now()
    dataframe = stock_historical_data(name, start_date, datetime.datetime.now().strftime('%Y-%m-%d'))
    dataframe['close'] = dataframe['close'].astype(float)
    dataframe['volume'] = dataframe['volume'].astype(float)
    dataframe['value'] = dataframe['close'] * dataframe['volume']
    # add new column volume 20 average
    dataframe['volume 20 average'] = dataframe['volume'].rolling(window=20, min_periods=20).mean().astype(float)
    # add new column MA 200
    dataframe['ma 200'] = dataframe['close'].rolling(window=200,min_periods=1).mean()
    # add new column candle type
    dataframe['candle type'] = dataframe.apply(candle_type,axis=1)
    # add new column 'highest price in 15 days'
    dataframe['highest price in 15 days'] = dataframe['high'].rolling(window=15,min_periods=1).max()
    # add new column 'lowest price in 15 days'
    dataframe['lowest price in 15 days'] = dataframe['close'].rolling(window=15,min_periods=1).min()
    # add new column 'flat base value'
    dataframe['flat base value'] = (dataframe['highest price in 15 days']- dataframe['lowest price in 15 days'])/ dataframe['lowest price in 15 days']
    # add new column 'integer candle type'
    dataframe['candle type value'] = dataframe['candle type'].apply(map_candle_type)
    # add new column 'count_bad_candles'
    dataframe['count bad candles'] = dataframe['candle type value'].rolling(window=15,min_periods=1).sum()
    # add new column
    dataframe['check flat base'] = dataframe.apply(check_flat_base,axis=1)
    return dataframe


# get all tickers
list_name_companies = get_securities_list()

# Fetch data in parallel
result_data = parallel_fetch_data(list_name_companies)


from collections import OrderedDict

# Dictionary to store breakout dates and corresponding symbols
breakout_dates = OrderedDict()

# Iterate through each dataframe (symbol, dataframe)
for symbol, df in result_data:
    # Filter rows where 'break out' == 'yes'
    breakout_rows = df[df['check flat base'] == 'yes']

    # Iterate through breakout rows
    for index, row in breakout_rows.iterrows():
        date = row['time']  

        # Append symbol to dictionary
        if date in breakout_dates:
            breakout_dates[date].append(symbol)
        else:
            breakout_dates[date] = [symbol]

# Print the dictionary in the desired format, sorted by date
for date, symbols in sorted(breakout_dates.items()):
    print(f"{date} : {' , '.join(symbols)}")

# Extract the final day from the sorted breakout dates
final_day = sorted(breakout_dates.keys())[-1]

# Extract the list of symbols for the final day
final_day_symbols = breakout_dates[final_day]

# Plotting the candlestick chart for each symbol on the final day
for symbol in final_day_symbols:
    # Get the DataFrame for this symbol
    df = None
    for sym, data in result_data:
        if sym == symbol:
            df = data
            break

    if df is not None:
        # Ensure the index is a DatetimeIndex
        df.index = pd.to_datetime(df['time'])

        # Plotting the candlestick chart
        mpf.plot(df, type='candle', style='charles', title=f'Candlestick chart for {symbol} on {final_day}', volume=True)
    else:
        print(f"No data found for symbol {symbol}")











