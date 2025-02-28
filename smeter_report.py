import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Constants
GAS_COST_PER_KWH = 0.0731
GAS_STANDING_CHARGE = 0.2747
ELEC_COST_PER_KWH = 0.2922
ELEC_STANDING_CHARGE = 0.42

class PersonalEnergyData():
    """ Create a PersonalEnergyData object"""
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

    def preprocess_df(self, column_renames=None, datetime_columns=None):
        if column_renames:
            self.df.rename(columns=column_renames, inplace=True)
        if datetime_columns:
            for col in datetime_columns:
                self.df[col] = pd.to_datetime(self.df[col])
    
        # Create a new column 'Month' with the month and year information 
        self.df['Start'] = pd.to_datetime(self.df['Start'], utc=True) # Convert to UTC
        self.df['Month'] = self.df['Start'].dt.to_period('M')

        # Resample the data to monthly frequency and sum the 'Consumption (kWh)' column
        self.monthly_data = self.df.groupby('Month')['Consumption (kwh)'].sum().reset_index()

    def cost_data(self, cost_per_kwh):
        self.df["Consumption (£)"] = self.df['Consumption (kwh)'] * cost_per_kwh

    def standing_charge(self, standing_charge, duration_in_days):
        return standing_charge * duration_in_days

    def lineplot_for_data(self, name_of_plot, column_to_plot, colour):
        # Plot the data
        sns.set(style="whitegrid")
        sns.lineplot(
            x='Start',
            y= column_to_plot,
            data = self.df,
            label = name_of_plot,
            color = colour
            )
        plt.title('Energy Consumption Over Time')
        plt.xlabel('Time')
        plt.ylabel(column_to_plot)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.ylim(0)
        plt.legend()
        plt.savefig('plots/{}.png'.format(name_of_plot))
        plt.clf()
    
    def lineplot_for_mon(self, name_of_plot):
        # Convert 'Month' column to datetime
        self.monthly_data['Month'] = self.monthly_data['Month'].dt.to_timestamp()

        # Set the 'Month' column as the index
        self.monthly_data = self.monthly_data.set_index('Month')
        # Plot the data
        sns.set(style="whitegrid")
        sns.scatterplot(
            x='Month',
            y= 'Consumption (kwh)',
            data = self.monthly_data,
            label = 'Monthly data',
            color = 'red'
            )
        plt.title('Energy Consumption Over Time (months)')
        plt.xlabel('Time')
        plt.ylim(0)
        plt.savefig('plots/{}.png'.format(name_of_plot+'_monthly'))
        plt.clf()

    
    def reportdata(self, plottype, standing_charge):
        # Calculate key statistics
        total_consumption = self.df['Consumption (kwh)'].sum()
        average_consumption = self.df['Consumption (kwh)'].mean()
        max_consumption = self.df['Consumption (kwh)'].max()

        total_consumption_cost = self.df['Consumption (£)'].sum()
        average_consumption_cost = self.df['Consumption (£)'].mean()
        max_consumption_cost = self.df['Consumption (£)'].max()
        total_charge = standing_charge+total_consumption_cost

        # Add key statistics to the report
        key_statistics = [
            ["Total Consumption " +str(plottype), f"{total_consumption:.2f} kwh"],
            ["Average Consumption "+str(plottype), f"{average_consumption:.2f} kwh"],
            ["Maximum Consumption "+str(plottype), f"{max_consumption:.2f} kwh"],
            ["Total Consumption " +str(plottype), f"£{total_consumption_cost:.2f}"],
            ["Average Consumption "+str(plottype), f"£{average_consumption_cost:2f}"],
            ["Maximum Consumption "+str(plottype), f"£{max_consumption_cost:.2f}"],
            ["Standing Charge "+str(plottype), f"£{standing_charge:.2f}"],
            ["Total Charge "+str(plottype), f"£{total_charge:.2f}"]
        ]
        return key_statistics, total_charge

def build_report(
    key_statistics_gas,
    key_statistics_elec,
    total_charge_list,
    ):
    # Create a PDF report
    doc = SimpleDocTemplate("reports/report.pdf", pagesize=letter)
    content = []

    # Add title and subtitle to the report
    title = "Cost of Energy Consumption Report"
    content.append(Paragraph(title, getSampleStyleSheet()['Title']))
    content.append(Spacer(1, 12))

    content.append(Table(key_statistics_elec, colWidths=[200, 100]))
    content.append(Table(key_statistics_gas, colWidths=[200, 100]))
    content.append(Table(total_charge_list, colWidths=[200, 100]))

    # Add plot to the report using Image class
    content.append(Image('plots/elec.png', width=400, height=300))
    content.append(Image('plots/elec_monthly.png', width=400, height=300))
    content.append(Image('plots/gas.png', width=400, height=300))
    content.append(Image('plots/gas_monthly.png', width=400, height=300))

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    content[2].setStyle(style)
    content[3].setStyle(style)
    content[4].setStyle(style)

    # Build the PDF report
    doc.build(content)

"""Time"""
start_time = pd.to_datetime('2024-01-01 00:00:00+00:00')
end_time = pd.to_datetime('2024-12-30 00:00:00+00:00')
duration_in_days = (end_time- start_time).days

"""Gas data"""
file_path_to_data_gas = "data/consumption_gas_2024.csv"
personal_ener_data_gas = PersonalEnergyData(file_path_to_data_gas)
personal_ener_data_gas.preprocess_df(column_renames={' Start': 'Start', ' End': 'End'}, datetime_columns=['Start', 'End'])
personal_ener_data_gas.cost_data(GAS_COST_PER_KWH)
standing_charge_gas  = personal_ener_data_gas.standing_charge(GAS_STANDING_CHARGE, duration_in_days)
personal_ener_data_gas.lineplot_for_data("gas", 'Consumption (£)', 'blue')
key_statistics_gas, total_charge_gas = personal_ener_data_gas.reportdata("gas", standing_charge_gas)
personal_ener_data_gas.lineplot_for_mon("gas")

"""Electricity"""
file_path_to_data_elec = "data/consumption_elec_2024.csv"
personal_ener_data_elec = PersonalEnergyData(file_path_to_data_elec)
personal_ener_data_elec.preprocess_df(column_renames={' Start': 'Start', ' End': 'End'}, datetime_columns=['Start', 'End'])
personal_ener_data_elec.cost_data(ELEC_COST_PER_KWH)
standing_charge_elec = personal_ener_data_elec.standing_charge(ELEC_STANDING_CHARGE, duration_in_days)
personal_ener_data_elec.lineplot_for_data("elec", 'Consumption (£)', 'red')
key_statistics_elec, total_charge_elec = personal_ener_data_elec.reportdata("elec", standing_charge_elec)
personal_ener_data_elec.lineplot_for_mon("elec")


"""Totals"""
total_charge_gas_elec = total_charge_elec+total_charge_gas
total_charge_list = [
    ["Total Charge for elec and gas", f"£{total_charge_gas_elec:.2f}"],
    ["Total Charge for elec and gas (monthly)", f"£{total_charge_gas_elec/12:.2f}"]
    ]

build_report(
    key_statistics_gas,
    key_statistics_elec,
    total_charge_list,
    )

