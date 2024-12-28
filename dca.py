import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

ticker = input("Enter the ticker symbol of the asset (e.g., AAPL for Apple): ")
investment_amount = float(input("Enter the amount you want to invest every interval (in USD): "))

start_date = input("Enter the start date (YYYY-MM-DD): ")
end_date = input("Enter the end date (YYYY-MM-DD): ")

# Download historical data from Yahoo Finance
data = yf.download(ticker, start=start_date, end=end_date)
data.dropna()

# Resample for both monthly and weekly investments
resampled_monthly_data = data.resample('1M').first()  # Monthly resampling
resampled_weekly_data = data.resample('1W').first()  # Weekly resampling

# Get custom DCA interval from the user
custom_dca_interval = input("Enter custom DCA interval (e.g., 2W for two weeks, 3M for three months): ").strip()

# Resample for custom interval
resampled_custom_data = data.resample(custom_dca_interval).first()  # Custom resampling based on user input

# Function to simulate DCA for a given resampled data
def simulate_dca(resampled_data):
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
monthly_dca_df, total_investment_monthly, total_shares_monthly = simulate_dca(resampled_monthly_data)
weekly_dca_df, total_investment_weekly, total_shares_weekly = simulate_dca(resampled_weekly_data)
custom_dca_df, total_investment_custom, total_shares_custom = simulate_dca(resampled_custom_data)

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

# Visualization
plt.figure(figsize=(12, 8))
# plt.style.use('seaborn-darkgrid')

# Plot for Monthly DCA
plt.plot(monthly_dca_df['Date'], monthly_dca_df['Portfolio Value'], label="Portfolio Value (Monthly)", color="#1f77b4", linestyle='-', marker='o', markersize=3, linewidth=2)
plt.plot(monthly_dca_df['Date'], monthly_dca_df['Total Investment'], label="Total Investment (Monthly)", color="#ff7f0e", linestyle='--', marker='o', markersize=3, linewidth=2)

# Plot for Weekly DCA
plt.plot(weekly_dca_df['Date'], weekly_dca_df['Portfolio Value'], label="Portfolio Value (Weekly)", color="#2ca02c", linestyle='-', marker='o', markersize=3, linewidth=2)
plt.plot(weekly_dca_df['Date'], weekly_dca_df['Total Investment'], label="Total Investment (Weekly)", color="#d62728", linestyle='--', marker='o', markersize=3, linewidth=2)

# Plot for Custom DCA
plt.plot(custom_dca_df['Date'], custom_dca_df['Portfolio Value'], label=f"Portfolio Value ({custom_dca_interval})", color="#9467bd", linestyle='-', marker='o', markersize=3, linewidth=2)
plt.plot(custom_dca_df['Date'], custom_dca_df['Total Investment'], label=f"Total Investment ({custom_dca_interval})", color="#8c564b", linestyle='--', marker='o', markersize=3, linewidth=2)

# Customize plot
plt.xlabel('Date', fontsize=14, fontweight='bold', color='darkslategray')
plt.ylabel('Value in USD', fontsize=14, fontweight='bold', color='darkslategray')
plt.title('Dollar Cost Averaging Portfolio Over Time (Monthly, Weekly, and Custom)', fontsize=16, fontweight='bold', color='darkslategray')
plt.legend(loc='upper left', fontsize=12, frameon=True, edgecolor='black', shadow=True)
plt.grid(True, linestyle='-', color='lightgray', alpha=0.6)

# Add annotation for investment information
plt.annotate(f"Total Investment (Monthly): ${print_if_series(total_investment_monthly):.2f}\n"
             f"Final Portfolio Value (Monthly): ${print_if_series(final_portfolio_value_monthly):.2f}\n"
             f"Total Profit (Monthly): ${print_if_series(total_profit_monthly):.2f}",
             xy=(1.05, 0.95), xycoords='axes fraction', ha='left', va='top', fontsize=10, color='blue', 
             bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=1'))

plt.annotate(f"Total Investment (Weekly): ${print_if_series(total_investment_weekly):.2f}\n"
             f"Final Portfolio Value (Weekly): ${print_if_series(final_portfolio_value_weekly):.2f}\n"
             f"Total Profit (Weekly): ${print_if_series(total_profit_weekly):.2f}",
             xy=(1.05, 0.75), xycoords='axes fraction', ha='left', va='top', fontsize=10, color='green', 
             bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=1'))

plt.annotate(f"Total Investment (Custom): ${print_if_series(total_investment_custom):.2f}\n"
             f"Final Portfolio Value (Custom): ${print_if_series(final_portfolio_value_custom):.2f}\n"
             f"Total Profit (Custom): ${print_if_series(total_profit_custom):.2f}",
             xy=(1.05, 0.55), xycoords='axes fraction', ha='left', va='top', fontsize=10, color='purple', 
             bbox=dict(facecolor='white', edgecolor='purple', boxstyle='round,pad=1'))

# Show the plot
plt.tight_layout()
plt.show()
