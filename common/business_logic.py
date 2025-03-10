import asyncio
import json
from datetime import datetime, timedelta
import random
from common.config import ARTIFICIAL_DELAY, MOCK_DATA_SIZE
import pathlib


def save_mock_data(data):
    """Save mock data to a timestamped file in mock_data_outputs directory."""
    # Create mock_data_outputs directory if it doesn't exist
    output_dir = pathlib.Path("mock_data_outputs")
    output_dir.mkdir(exist_ok=True)

    # Clean up old mock data files
    cleanup_mock_data_files(output_dir)

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"mock_data_{timestamp}.json"

    # Save the data with pretty printing
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nMock data saved to: {output_file}")


def cleanup_mock_data_files(output_dir):
    """Remove all existing mock data files in the output directory."""
    for file in output_dir.glob("mock_data_*.json"):
        try:
            file.unlink()
        except Exception as e:
            print(f"Warning: Could not delete {file}: {e}")


# Mock data generation
def generate_mock_data():
    customers = []
    contracts = []
    billing_history = []
    usage_data = []
    payment_methods = []

    # Generate customers
    for i in range(MOCK_DATA_SIZE["customers"]):
        customer = {
            "id": f"CUST{i:04d}",
            "name": f"Customer {i}",
            "phone": f"+65{i:08d}",  # Singapore number format
            "email": f"customer{i}@example.com",
            "address": f"Block {random.randint(1, 999)}, #{random.randint(1, 20)}-{random.randint(1, 99)}, Singapore {random.randint(100000, 999999)}",
            "joined_date": (
                datetime.now() - timedelta(days=random.randint(0, 730))
            ).isoformat(),
            "preferred_language": random.choice(["English", "Mandarin", "Malay", "Tamil"]),
            "account_status": "Active",  # All customers are active
        }
        customers.append(customer)

    # Generate energy contracts
    for i in range(MOCK_DATA_SIZE["orders"]):  # Using orders size for contracts
        customer = random.choice(customers)
        plan_types = ["Fixed Price Plan", "Discount Off Tariff", "Peak/Off-Peak Plan", "Green Energy Plan"]
        contract_terms = [12, 24]  # Most common contract terms in months
        selected_plan = random.choice(plan_types)
        start_date = datetime.now() - timedelta(days=random.randint(30, 365))
        term_months = random.choice(contract_terms)
        end_date = start_date + timedelta(days=term_months * 30)
        
        contract = {
            "id": f"CONT{i:04d}",
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "term_months": term_months,
            "plan_type": selected_plan,
            "rate": round(random.uniform(0.18, 0.30), 4),  # $ per kWh
            "status": "Active",  # All contracts are active
            "auto_renewal": True,  # Default to auto-renewal
            "green_energy_percentage": 100 if selected_plan == "Green Energy Plan" else random.choice([0, 20, 50]),
        }
        contracts.append(contract)
        
        # Generate detailed billing history for last 2 months
        for month in range(2):
            bill_date = datetime.now() - timedelta(days=30 * month)
            if bill_date > start_date:
                # Base usage varies by housing type and season
                base_usage = random.uniform(300.0, 800.0)  # Average Singapore household usage
                seasonal_factor = 1.0 + (0.15 * (month % 2))  # Higher in current month
                monthly_usage = base_usage * seasonal_factor
                
                # Calculate detailed charges
                energy_charge = monthly_usage * contract["rate"]
                market_support_fee = 4.39  # Fixed MSS charge
                power_grid_charge = monthly_usage * 0.0484  # Grid charge
                transmission_loss_charge = energy_charge * 0.004  # 0.4% of energy cost
                
                # EMC & PSO charges
                emc_charge = monthly_usage * 0.0013  # Energy Market Company charge
                pso_charge = monthly_usage * 0.0007  # Power System Operator charge
                
                # Calculate total before GST
                subtotal = (
                    energy_charge +
                    market_support_fee +
                    power_grid_charge +
                    transmission_loss_charge +
                    emc_charge +
                    pso_charge
                )
                
                # GST
                gst = subtotal * 0.08  # 8% GST
                total_amount = subtotal + gst
                
                bill = {
                    "id": f"BILL{len(billing_history):04d}",
                    "contract_id": contract["id"],
                    "customer_id": customer["id"],
                    "bill_date": bill_date.isoformat(),
                    "due_date": (bill_date + timedelta(days=21)).isoformat(),
                    "billing_period_start": (bill_date - timedelta(days=30)).isoformat(),
                    "billing_period_end": bill_date.isoformat(),
                    "usage_kwh": round(monthly_usage, 2),
                    "charges": {
                        "energy_charge": round(energy_charge, 2),
                        "market_support_fee": round(market_support_fee, 2),
                        "power_grid_charge": round(power_grid_charge, 2),
                        "transmission_loss_charge": round(transmission_loss_charge, 2),
                        "emc_charge": round(emc_charge, 2),
                        "pso_charge": round(pso_charge, 2),
                        "subtotal": round(subtotal, 2),
                        "gst": round(gst, 2),
                    },
                    "total_amount": round(total_amount, 2),
                    "status": "Paid" if month > 0 else "Unpaid",  # Previous month is paid, current month is unpaid
                    "payment_due": (bill_date + timedelta(days=21)).isoformat(),
                }
                billing_history.append(bill)
                
                # Generate daily usage data for each month
                for day in range(30):
                    usage_date = bill_date - timedelta(days=day)
                    
                    # Create realistic daily usage pattern
                    if contract["plan_type"] == "Peak/Off-Peak Plan":
                        # Peak hours (9am-9pm): 70% of daily usage
                        daily_peak = (monthly_usage / 30) * 0.7 * random.uniform(0.9, 1.1)
                        # Off-peak hours: 30% of daily usage
                        daily_off_peak = (monthly_usage / 30) * 0.3 * random.uniform(0.9, 1.1)
                        daily_total = daily_peak + daily_off_peak
                    else:
                        daily_total = (monthly_usage / 30) * random.uniform(0.9, 1.1)
                        daily_peak = None
                        daily_off_peak = None
                    
                    usage_entry = {
                        "customer_id": customer["id"],
                        "contract_id": contract["id"],
                        "date": usage_date.isoformat(),
                        "total_kwh": round(daily_total, 2),
                        "peak_kwh": round(daily_peak, 2) if daily_peak else None,
                        "off_peak_kwh": round(daily_off_peak, 2) if daily_off_peak else None,
                        "carbon_offset_kg": round(daily_total * 0.4 * (contract["green_energy_percentage"] / 100), 2),
                    }
                    usage_data.append(usage_entry)
    
    # Generate payment methods for customers
    for customer in customers:
        # Each customer has exactly one payment method
        payment_type = random.choice(["GIRO", "Credit Card"])
        
        if payment_type == "Credit Card":
            payment_method = {
                "id": f"PAY{len(payment_methods):04d}",
                "customer_id": customer["id"],
                "type": payment_type,
                "card_type": random.choice(["Visa", "MasterCard"]),
                "last_four": f"{random.randint(1000, 9999)}",
                "expiry_date": f"{random.randint(1, 12)}/{random.randint(23, 28)}",
                "is_default": True,
            }
        else:  # GIRO
            payment_method = {
                "id": f"PAY{len(payment_methods):04d}",
                "customer_id": customer["id"],
                "type": payment_type,
                "bank_name": random.choice(["DBS", "OCBC", "UOB"]),
                "account_last_four": f"{random.randint(1000, 9999)}",
                "is_default": True,
            }
        
        payment_methods.append(payment_method)

    # Format sample data for display
    sample_data = []
    sample_customers = random.sample(customers, 3)
    for customer in sample_customers:
        customer_data = {
            "Customer": customer["name"],
            "ID": customer["id"],
            "Phone": customer["phone"],
            "Email": customer["email"],
            "Address": customer["address"],
            "Contracts": [],
            "Current Bill": [],
            "Previous Bill": [],
            "Usage": [],
            "Payment Method": [],
        }

        # Add contracts
        customer_contracts = [c for c in contracts if c["customer_id"] == customer["id"]]
        for contract in customer_contracts[:2]:
            customer_data["Contracts"].append(
                {
                    "ID": contract["id"],
                    "Plan": contract["plan_type"],
                    "Term": f"{contract['term_months']} months",
                    "Rate": f"${contract['rate']}/kWh",
                    "Status": contract["status"],
                    "Start Date": contract["start_date"][:10],
                    "End Date": contract["end_date"][:10],
                    "Auto Renewal": "Yes" if contract["auto_renewal"] else "No",
                    "Green Energy": f"{contract['green_energy_percentage']}%",
                }
            )
            
            # Add billing history (current and previous month)
            contract_bills = [b for b in billing_history if b["contract_id"] == contract["id"]]
            contract_bills.sort(key=lambda x: x["bill_date"], reverse=True)
            
            if contract_bills:
                # Current month's bill
                current_bill = contract_bills[0]
                customer_data["Current Bill"].append({
                    "Bill ID": current_bill["id"],
                    "Period": f"{current_bill['billing_period_start'][:10]} to {current_bill['billing_period_end'][:10]}",
                    "Usage": f"{current_bill['usage_kwh']} kWh",
                    "Energy Charge": f"${current_bill['charges']['energy_charge']}",
                    "Grid Charge": f"${current_bill['charges']['power_grid_charge']}",
                    "Other Charges": f"${current_bill['charges']['market_support_fee'] + current_bill['charges']['transmission_loss_charge'] + current_bill['charges']['emc_charge'] + current_bill['charges']['pso_charge']}",
                    "GST": f"${current_bill['charges']['gst']}",
                    "Total": f"${current_bill['total_amount']}",
                    "Status": current_bill["status"],
                    "Due Date": current_bill["payment_due"][:10],
                })
                
                # Previous month's bill if available
                if len(contract_bills) > 1:
                    prev_bill = contract_bills[1]
                    customer_data["Previous Bill"].append({
                        "Bill ID": prev_bill["id"],
                        "Period": f"{prev_bill['billing_period_start'][:10]} to {prev_bill['billing_period_end'][:10]}",
                        "Usage": f"{prev_bill['usage_kwh']} kWh",
                        "Total": f"${prev_bill['total_amount']}",
                        "Status": prev_bill["status"],
                    })
            
            # Add recent usage data
            contract_usage = [u for u in usage_data if u["contract_id"] == contract["id"]]
            contract_usage.sort(key=lambda x: x["date"], reverse=True)
            for usage in contract_usage[:7]:  # Last 7 days
                usage_entry = {
                    "Date": usage["date"][:10],
                    "Usage": f"{usage['total_kwh']} kWh",
                }
                if usage["peak_kwh"]:
                    usage_entry["Peak"] = f"{usage['peak_kwh']} kWh"
                    usage_entry["Off-Peak"] = f"{usage['off_peak_kwh']} kWh"
                if usage["carbon_offset_kg"]:
                    usage_entry["Carbon Offset"] = f"{usage['carbon_offset_kg']} kg"
                customer_data["Usage"].append(usage_entry)
        
        # Add payment method
        customer_payments = [p for p in payment_methods if p["customer_id"] == customer["id"]]
        for payment in customer_payments:
            if payment["type"] == "Credit Card":
                payment_info = {
                    "Type": payment["type"],
                    "Card": f"{payment['card_type']} ending in {payment['last_four']}",
                    "Expiry": payment["expiry_date"],
                }
            else:  # GIRO
                payment_info = {
                    "Type": payment["type"],
                    "Bank": payment["bank_name"],
                    "Account": f"ending in {payment['account_last_four']}",
                }
            customer_data["Payment Method"].append(payment_info)

        sample_data.append(customer_data)

    # Create data object
    mock_data = {
        "customers": customers,
        "contracts": contracts,
        "billing_history": billing_history,
        "usage_data": usage_data,
        "payment_methods": payment_methods,
        "sample_data": sample_data,
    }

    # Save the mock data
    save_mock_data(mock_data)

    return mock_data


# Initialize mock data
MOCK_DATA = generate_mock_data()


async def simulate_delay(delay_type):
    """Simulate processing delay based on operation type."""
    await asyncio.sleep(ARTIFICIAL_DELAY[delay_type])


async def get_customer(phone=None, email=None, customer_id=None):
    """Look up a customer by phone, email, or ID."""
    await simulate_delay("database")

    if phone:
        customer = next(
            (c for c in MOCK_DATA["customers"] if c["phone"] == phone), None
        )
    elif email:
        customer = next(
            (c for c in MOCK_DATA["customers"] if c["email"] == email), None
        )
    elif customer_id:
        customer = next(
            (c for c in MOCK_DATA["customers"] if c["id"] == customer_id), None
        )
    else:
        return {"error": "No search criteria provided"}

    return customer if customer else {"error": "Customer not found"}


async def get_customer_appointments(customer_id):
    """Get all appointments for a customer."""
    await simulate_delay("database")

    appointments = [
        a for a in MOCK_DATA["appointments"] if a["customer_id"] == customer_id
    ]
    return {"customer_id": customer_id, "appointments": appointments}


async def get_customer_contracts(customer_id):
    """Get all energy contracts for a customer."""
    await simulate_delay("database")

    contracts = [c for c in MOCK_DATA["contracts"] if c["customer_id"] == customer_id]
    return {"customer_id": customer_id, "contracts": contracts}


async def get_customer_billing(customer_id):
    """Get billing history for a customer."""
    await simulate_delay("database")

    bills = [b for b in MOCK_DATA["billing_history"] if b["customer_id"] == customer_id]
    return {"customer_id": customer_id, "billing_history": bills}


async def get_customer_usage(customer_id, days=30):
    """Get usage data for a customer."""
    await simulate_delay("database")

    usage = [u for u in MOCK_DATA["usage_data"] if u["customer_id"] == customer_id]
    # Sort by date and limit to requested days
    usage.sort(key=lambda x: x["date"], reverse=True)
    usage = usage[:days]
    
    return {"customer_id": customer_id, "usage_data": usage}


async def get_customer_payment_methods(customer_id):
    """Get payment methods for a customer."""
    await simulate_delay("database")

    payment_methods = [p for p in MOCK_DATA["payment_methods"] if p["customer_id"] == customer_id]
    return {"customer_id": customer_id, "payment_methods": payment_methods}


async def schedule_appointment(customer_id, date, service):
    """Schedule a new appointment."""
    await simulate_delay("database")

    # Verify customer exists
    customer = await get_customer(customer_id=customer_id)
    if "error" in customer:
        return customer

    # Create new appointment
    appointment_id = f"APT{len(MOCK_DATA['appointments']):04d}"
    appointment = {
        "id": appointment_id,
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "date": date,
        "service": service,
        "status": "Scheduled",
        "location": "JTC Summit (near Jurong East MRT Station)",
        "notes": "",
    }

    MOCK_DATA["appointments"].append(appointment)
    return appointment


async def get_available_appointment_slots(start_date, end_date):
    """Get available appointment slots."""
    await simulate_delay("database")

    # Convert dates to datetime objects
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    # Generate available slots (9 AM to 5 PM, 1-hour slots)
    slots = []
    current = start
    while current <= end:
        if current.hour >= 9 and current.hour < 17:
            slot_time = current.isoformat()
            # Check if slot is already taken
            taken = any(a["date"] == slot_time for a in MOCK_DATA["appointments"])
            if not taken:
                slots.append(slot_time)
        current += timedelta(hours=1)

    return {"available_slots": slots}


async def prepare_agent_filler_message(websocket, message_type):
    """
    Handle agent filler messages while maintaining proper function call protocol.
    Returns a simple confirmation first, then sends the actual message to the client.
    """
    # First prepare the result that will be the function call response
    result = {"status": "queued", "message_type": message_type}

    # Prepare the inject message but don't send it yet
    if message_type == "lookup":
        inject_message = {
            "type": "InjectAgentMessage",
            "message": "Let me look that up for you...",
        }
    else:
        inject_message = {
            "type": "InjectAgentMessage",
            "message": "One moment please...",
        }

    # Return the result first - this becomes the function call response
    # The caller can then send the inject message after handling the function response
    return {"function_response": result, "inject_message": inject_message}


async def prepare_farewell_message(websocket, farewell_type):
    """End the conversation with an appropriate farewell message and close the connection."""
    # Prepare farewell message based on type
    if farewell_type == "thanks":
        message = "Thank you for calling! Have a great day!"
    elif farewell_type == "help":
        message = "I'm glad I could help! Have a wonderful day!"
    else:  # general
        message = "Goodbye! Have a nice day!"

    # Prepare messages but don't send them
    inject_message = {"type": "InjectAgentMessage", "message": message}

    close_message = {"type": "close"}

    # Return both messages to be sent in correct order by the caller
    return {
        "function_response": {"status": "closing", "message": message},
        "inject_message": inject_message,
        "close_message": close_message,
    }
