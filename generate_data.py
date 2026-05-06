import pandas as pd
import random
from datetime import datetime, timedelta

# -------------------------------
# Setup
# -------------------------------
NUM_PROSPECTS = 300

services = [
    "Interior Design",
    "Luxury Villa",
    "Office Space",
    "Apartment Design"
]

sources = ["organic", "ads", "referral", "direct"]
devices = ["mobile", "desktop"]

start_date = datetime(2026, 4, 1)
end_date = datetime(2026, 4, 30)
date_range = pd.date_range(start=start_date, end=end_date)

records = []

# -------------------------------
# Behavior Probabilities
# -------------------------------
def get_probabilities(service, source):
    # base probabilities
    view_p = 0.75
    enquiry_p = 0.25
    deal_p = 0.35
    move_p = 0.8

    # adjust by source quality
    if source == "ads":
        enquiry_p *= 0.8
        deal_p *= 0.8
    elif source == "organic":
        enquiry_p *= 1.2
        deal_p *= 1.1

    # adjust by service value
    if service == "Luxury Villa":
        deal_p *= 1.2
    elif service == "Apartment Design":
        move_p *= 1.1

    return view_p, enquiry_p, deal_p, move_p

# -------------------------------
# Generate Data
# -------------------------------
for i in range(NUM_PROSPECTS):
    prospect_id = f"P{str(i).zfill(3)}"
    service = random.choice(services)
    source = random.choice(sources)
    device = random.choice(devices)

    visit_date = random.choice(date_range)

    # Visit
    records.append([visit_date, prospect_id, service, "visit", source, device, 0])

    view_p, enquiry_p, deal_p, move_p = get_probabilities(service, source)

    # View
    if random.random() < view_p:
        records.append([visit_date, prospect_id, service, "view_project", source, device, 0])

    # Enquiry
    if random.random() < enquiry_p:
        enquiry_date = visit_date + timedelta(days=random.randint(1, 3))
        records.append([enquiry_date, prospect_id, service, "enquiry", source, device, 1])

        # Deal Closed (delayed)
        if random.random() < deal_p:
            deal_date = enquiry_date + timedelta(days=random.randint(5, 15))
            deal_value = random.randint(5_00_000, 50_00_000)

            records.append([deal_date, prospect_id, service, "deal_closed", source, device, deal_value])

            # Move-in (final stage)
            if random.random() < move_p:
                move_date = deal_date + timedelta(days=random.randint(10, 30))
                records.append([move_date, prospect_id, service, "move_in", source, device, deal_value])

# -------------------------------
# Save Data
# -------------------------------
df = pd.DataFrame(records, columns=[
    "date", "prospect_id", "service", "event",
    "source", "device", "value"
])

df.to_csv("architecture_pipeline_data.csv", index=False)

print("Dataset generated successfully.")