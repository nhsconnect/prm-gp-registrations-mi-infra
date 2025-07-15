from degrade_utils.generate_weekly_reports import generate_weekly_report
import os

""" Adhoc script to generate a weekly summary report with historical data,
    Date to be in format YYYY-MM-DD
    Populate the environmental variables with the MI Registrations bucket name and region it is hosted"""

if __name__ == "__main__":
    date = "2024-02-19"
    os.environ["REGISTRATIONS_MI_EVENT_BUCKET"] = ""
    os.environ["REGION"] = ""

    generate_weekly_report(date)