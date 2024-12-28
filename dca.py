import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

ticker = input("Enter the ticker symbol of the asset (e.g., AAPL for Apple): ")
investment_amount = float(input("Enter the amount you want to invest every interval (in USD): "))

start_date = input("Enter the start date (YYYY-MM-DD): ")
end_date = input("Enter the end date (YYYY-MM-DD): ")

# Get custom DCA interval from the user
custom_dca_interval = input("Enter custom DCA interval (e.g., 2W for two weeks, 3M for three months): ").strip()

# Download historical data from Yahoo Finance
data = yf.download(ticker, start=start_date, end=end_date)
data.dropna()

# Resample for both monthly and weekly investments
resampled_monthly_data = data.resample('1M').first()  # Monthly resampling
resampled_monthly_data = resampled_monthly_data[resampled_monthly_data.index <= pd.to_datetime(end_date)]

resampled_weekly_data = data.resample('1W').first()  # Weekly resampling
resampled_weekly_data = resampled_weekly_data[resampled_weekly_data.index <= pd.to_datetime(end_date)]

# Resample for custom interval
resampled_custom_data = data.resample(custom_dca_interval).first()  # Custom resampling based on user input
resampled_custom_data = resampled_custom_data[resampled_custom_data.index <= pd.to_datetime(end_date)]

# Function to simulate DCA for a given resampled data
def simulate_dca(resampled_data, investment_amount):
    total_investment = 0
    total_shares = 0
    dca_log = []
    
    for date, row in resampled_data.iterrows():
        price = row['Close']
        shares_bought = investment_amount / price
        total_shares += shares_bought
        total_investment += investment_amount
        
        dca_log.append({
            "Date": date,
            "Price": price,
            "Shares Bought": shares_bought,
            "Total Shares": total_shares,
            "Total Investment": total_investment,
            "Portfolio Value": total_shares * price
        })
    
    return pd.DataFrame(dca_log), total_investment, total_shares

# Simulate DCA for monthly, weekly, and custom intervals
monthly_dca_df, total_investment_monthly, total_shares_monthly = simulate_dca(resampled_monthly_data, investment_amount*4)
weekly_dca_df, total_investment_weekly, total_shares_weekly = simulate_dca(resampled_weekly_data, investment_amount)
if custom_dca_interval[-1] == 'W':
    custom_dca_df, total_investment_custom, total_shares_custom = simulate_dca(resampled_custom_data, investment_amount*int(custom_dca_interval[:-1]))
else:
    custom_dca_df, total_investment_custom, total_shares_custom = simulate_dca(resampled_custom_data, investment_amount*4*int(custom_dca_interval[:-1]))

# Calculate final portfolio value and profit for monthly, weekly, and custom
final_price = data['Close'].iloc[-1]  # Final price for portfolio value calculation
final_portfolio_value_monthly = total_shares_monthly * final_price
final_portfolio_value_weekly = total_shares_weekly * final_price
final_portfolio_value_custom = total_shares_custom * final_price

total_profit_monthly = final_portfolio_value_monthly - total_investment_monthly
total_profit_weekly = final_portfolio_value_weekly - total_investment_weekly
total_profit_custom = final_portfolio_value_custom - total_investment_custom

# Function to handle pandas Series and print scalar values
def print_if_series(value):
    if isinstance(value, pd.Series):
        return value.iloc[0]
    return value

# Output the results
if data.empty:
    print(f"No data found for ticker: {ticker}")
else:
    print(f"Total Investment (Monthly): ${print_if_series(total_investment_monthly):.2f}")
    print(f"Final Portfolio Value (Monthly): ${print_if_series(final_portfolio_value_monthly):.2f}")
    print(f"Total Profit (Monthly): ${print_if_series(total_profit_monthly):.2f}")
    
    print(f"Total Investment (Weekly): ${print_if_series(total_investment_weekly):.2f}")
    print(f"Final Portfolio Value (Weekly): ${print_if_series(final_portfolio_value_weekly):.2f}")
    print(f"Total Profit (Weekly): ${print_if_series(total_profit_weekly):.2f}")
    
    print(f"Total Investment (Custom): ${print_if_series(total_investment_custom):.2f}")
    print(f"Final Portfolio Value (Custom): ${print_if_series(final_portfolio_value_custom):.2f}")
    print(f"Total Profit (Custom): ${print_if_series(total_profit_custom):.2f}")

future_dates = pd.date_range(start=resampled_monthly_data.index[-1], end=end_date, freq='D')  # Adjust the frequency as needed

def extend_dca_df(dca_df, future_dates, final_portfolio_value, total_investment, final_price, total_shares):
    extended_dca_df = dca_df.copy()
    extended_dca_df = pd.concat([extended_dca_df, pd.DataFrame({
        'Date': future_dates,
        'Portfolio Value': [final_portfolio_value] * len(future_dates),
        'Total Investment': [total_investment] * len(future_dates),
        'Price': [final_price] * len(future_dates),
        'Total Shares': [total_shares] * len(future_dates),
        'Shares Bought': [0] * len(future_dates)
    })], ignore_index=True)
    
    return extended_dca_df

extended_monthly_dca_df = extend_dca_df(monthly_dca_df, future_dates, final_portfolio_value_monthly, total_investment_monthly, final_price, total_shares_monthly)
extended_weekly_dca_df = extend_dca_df(weekly_dca_df, future_dates, final_portfolio_value_weekly, total_investment_weekly, final_price, total_shares_weekly)
extended_custom_dca_df = extend_dca_df(custom_dca_df, future_dates, final_portfolio_value_custom, total_investment_custom, final_price, total_shares_custom)


# Visualization
fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# Monthly DCA Plot
axes[0].plot(extended_monthly_dca_df['Date'], extended_monthly_dca_df['Portfolio Value'], label="Portfolio Value (Monthly)", color="#1f77b4", linestyle='-', marker='o', markersize=1, linewidth=2)
axes[0].plot(extended_monthly_dca_df['Date'], extended_monthly_dca_df['Total Investment'], label="Total Investment (Monthly)", color="#1f77b4", linestyle='--', marker='o', markersize=1, linewidth=2)
axes[0].set_ylabel('Value in USD', fontsize=14, fontweight='bold', color='darkslategray')
axes[0].set_title(f'Monthly Dollar Cost Averaging for {ticker}', fontsize=16, fontweight='bold', color='darkslategray')
axes[0].legend(loc='upper left', fontsize=12, frameon=True, edgecolor='black', shadow=True)
axes[0].grid(True, linestyle='-', color='lightgray', alpha=0.6)
axes[0].annotate(f"Total Investment (Monthly): ${print_if_series(total_investment_monthly):.2f}\n"
                 f"Final Portfolio Value (Monthly): ${print_if_series(final_portfolio_value_monthly):.2f}\n"
                 f"Total Profit (Monthly): ${print_if_series(total_profit_monthly):.2f}",
                 xy=(1.05, 0.95), xycoords='axes fraction', ha='left', va='top', fontsize=10, color='#1f77b4', 
                 bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=1'))

# Weekly DCA Plot
axes[1].plot(extended_weekly_dca_df['Date'], extended_weekly_dca_df['Portfolio Value'], label="Portfolio Value (Weekly)", color="#2ca02c", linestyle='-', marker='o', markersize=1, linewidth=2)
axes[1].plot(extended_weekly_dca_df['Date'], extended_weekly_dca_df['Total Investment'], label="Total Investment (Weekly)", color="#2ca02c", linestyle='--', marker='o', markersize=1, linewidth=2)
axes[1].set_ylabel('Value in USD', fontsize=14, fontweight='bold', color='darkslategray')
axes[1].set_title(f'Weekly Dollar Cost Averaging for {ticker}', fontsize=16, fontweight='bold', color='darkslategray')
axes[1].legend(loc='upper left', fontsize=12, frameon=True, edgecolor='black', shadow=True)
axes[1].grid(True, linestyle='-', color='lightgray', alpha=0.6)
axes[1].annotate(f"Total Investment (Weekly): ${print_if_series(total_investment_weekly):.2f}\n"
                 f"Final Portfolio Value (Weekly): ${print_if_series(final_portfolio_value_weekly):.2f}\n"
                 f"Total Profit (Weekly): ${print_if_series(total_profit_weekly):.2f}",
                 xy=(1.05, 0.75), xycoords='axes fraction', ha='left', va='top', fontsize=10, color='#2ca02c', 
                 bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=1'))

# Custom DCA Plot
axes[2].plot(extended_custom_dca_df['Date'], extended_custom_dca_df['Portfolio Value'], label=f"Portfolio Value ({custom_dca_interval})", color="#9467bd", linestyle='-', marker='o', markersize=1, linewidth=2)
axes[2].plot(extended_custom_dca_df['Date'], extended_custom_dca_df['Total Investment'], label=f"Total Investment ({custom_dca_interval})", color="#9467bd", linestyle='--', marker='o', markersize=1, linewidth=2)
axes[2].set_xlabel('Date', fontsize=14, fontweight='bold', color='darkslategray')
axes[2].set_ylabel('Value in USD', fontsize=14, fontweight='bold', color='darkslategray')
axes[2].set_title(f'Custom Dollar Cost Averaging for {ticker}', fontsize=16, fontweight='bold', color='darkslategray')
axes[2].legend(loc='upper left', fontsize=12, frameon=True, edgecolor='black', shadow=True)
axes[2].grid(True, linestyle='-', color='lightgray', alpha=0.6)
axes[2].annotate(f"Total Investment ({custom_dca_interval}): ${print_if_series(total_investment_custom):.2f}\n"
                 f"Final Portfolio Value ({custom_dca_interval}): ${print_if_series(final_portfolio_value_custom):.2f}\n"
                 f"Total Profit ({custom_dca_interval}): ${print_if_series(total_profit_custom):.2f}",
                 xy=(1.05, 0.55), xycoords='axes fraction', ha='left', va='top', fontsize=10, color='#9467bd', 
                 bbox=dict(facecolor='white', edgecolor='purple', boxstyle='round,pad=1'))

# Adjust layout
plt.tight_layout()
plt.show()
