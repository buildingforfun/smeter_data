import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class SmeterData():
    """Create SmeterData object"""
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

    def preprocess_df(self, column_renames=None, datetime_columns=None):
        if column_renames:
            self.df.rename(columns=column_renames, inplace=True)
        if datetime_columns:
            for col in datetime_columns:
                self.df[col] = pd.to_datetime(self.df[col])
        
        # Create a new column 'Month' with the month and year
        self.df['Start'] = pd.to_datetime(self.df['Start'], utc=True).dt.tz_localize(None)
        self.df['Month'] = self.df['Start'].dt.to_period('M')
        self.df['hour'] = self.df['Start'].dt.hour


    def plot_for_data(self, name_plot, column_plot, colour):
        sns.lineplot(
            x='Start',
            y=column_plot,
            data=self.df,
            label = name_plot,
            color=colour,
        )
        plt.title('Energy consumption over time')
        plt.xlabel('Time')
        plt.ylabel(column_plot)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.ylim(0)
        plt.legend()
        plt.savefig('plots/{}.png'.format(name_plot))
        plt.clf()

    def plot_monthly(self, name_plot):
        # Resample the data to monthly frequency and sum the consumption
        self.monthly_data = self.df.groupby('Month')['Consumption (kwh)'].sum().reset_index()
    
        # convert to monthly
        self.monthly_data['Month'] = self.monthly_data['Month'].dt.to_timestamp()

        # set month as index
        self.monthly_data = self.monthly_data.set_index('Month')

        # Plot the data
        sns.scatterplot(
            x = 'Month',
            y = 'Consumption (kwh)',
            data = self.monthly_data,
            color = 'red',
        )

        plt.title('Energy consumption over time (months)')
        plt.xlabel('Time')
        plt.ylabel('Consumption (kwh)')
        plt.ylim(0)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('plots/{}.png'.format(name_plot+'_monthly'))
        plt.clf()

file_path_gas = "data/consumption_gas_2024.csv"
smeter_gas = SmeterData(file_path_gas)
smeter_gas.preprocess_df(column_renames={' Start': 'Start', ' End':'End'}, datetime_columns=['Start', 'End'])
smeter_gas.plot_for_data('gas', 'Consumption (kwh)', 'blue')
smeter_gas.plot_monthly('gas')

file_path_elec = "data/consumption_elec_2024.csv"
smeter_elec = SmeterData(file_path_elec)
smeter_elec.preprocess_df(column_renames={' Start': 'Start', ' End':'End'}, datetime_columns=['Start', 'End'])
smeter_elec.plot_for_data('elec', 'Consumption (kwh)', 'blue')
smeter_elec.plot_monthly('elec')
