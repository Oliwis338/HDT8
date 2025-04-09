import simpy
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict

# Set random seed for reproducibility
random.seed(10)

# Simulation parameters
SIM_TIME = 24 * 60  # 24 hours in minutes
ARRIVAL_RATE = {
    "weekday": 1/12,       # One patient every 12 minutes on weekdays
    "weekend": 1/6,        # One patient every 6 minutes on weekends
    "holiday": 1/4         # One patient every 4 minutes on holidays
}

# Resource costs (monthly)
COSTS = {
    "nurse": 3500,        # USD per month
    "doctor": 15000,      # USD per month
    "lab_technician": 2500,  # USD per month
    "xray_machine": 5000,  # Amortized cost per month
    "lab_equipment": 3000  # Amortized cost per month
}

# Process times (in minutes)
TIMES = {
    "registration": 5,
    "triage": {
        1: 3,  # Critical cases are assessed quickly
        2: 5,
        3: 8,
        4: 10,
        5: 12
    },
    "doctor_examination": {
        1: 20,  # Critical cases need more doctor time
        2: 25,
        3: 15,
        4: 12,
        5: 10
    },
    "lab_test": {
        1: 15,
        2: 20,
        3: 25,
        4: 25,
        5: 30
    },
    "xray": {
        1: 10,
        2: 15,
        3: 20,
        4: 20,
        5: 25
    },
    "treatment": {
        1: 60,  # Critical cases need more treatment time
        2: 45,
        3: 30,
        4: 20,
        5: 15
    }
}

# Probability of needing different services based on severity
NEEDS_LAB = {1: 0.9, 2: 0.8, 3: 0.7, 4: 0.5, 5: 0.3}
NEEDS_XRAY = {1: 0.7, 2: 0.6, 3: 0.5, 4: 0.3, 5: 0.2}

class EmergencyDepartment:
    def __init__(self, env, 
                num_nurses=2, 
                num_doctors=2, 
                num_lab_techs=1,
                num_xray_machines=1,
                day_type="weekday"):
        
        self.env = env
        
        # Resources
        self.registration = simpy.Resource(env, capacity=1)
        self.nurses = simpy.PriorityResource(env, capacity=num_nurses)
        self.doctors = simpy.PriorityResource(env, capacity=num_doctors)
        self.lab_techs = simpy.PriorityResource(env, capacity=num_lab_techs)
        self.xray_machines = simpy.PriorityResource(env, capacity=num_xray_machines)
        
        # Statistics
        self.patient_wait_times = []
        self.total_times = []
        self.patient_counts = 0
        self.patient_details = []
        self.resource_usage = {
            "nurses": [],
            "doctors": [],
            "lab_techs": [],
            "xray_machines": []
        }
        
        # Set arrival rate based on day type
        self.arrival_rate = ARRIVAL_RATE[day_type]
        
        # Setup monitoring
        self.env.process(self.monitor_resources())
        
    def monitor_resources(self):
        """Monitor resource usage over time"""
        while True:
            self.resource_usage["nurses"].append(
                (self.env.now, len(self.nurses.queue) + self.nurses.count)
            )
            self.resource_usage["doctors"].append(
                (self.env.now, len(self.doctors.queue) + self.doctors.count)
            )
            self.resource_usage["lab_techs"].append(
                (self.env.now, len(self.lab_techs.queue) + self.lab_techs.count)
            )
            self.resource_usage["xray_machines"].append(
                (self.env.now, len(self.xray_machines.queue) + self.xray_machines.count)
            )
            yield self.env.timeout(10)  # Record every 10 minutes
    
    def patient_generator(self):
        """Generate new patients arriving at the ED"""
        patient_id = 0
        while True:
            # Wait for a new patient to arrive
            inter_arrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            
            # Create a new patient
            patient_id += 1
            self.env.process(self.patient_journey(patient_id))
            
    def patient_journey(self, patient_id):
        """Simulate the journey of a patient through the ED"""
        arrival_time = self.env.now
        
        # Generate patient severity (1-5) with distribution favoring less severe cases
        # 1: immediate (life threatening) - 5: non-urgent
        weights = [0.05, 0.15, 0.30, 0.30, 0.20]  # 5% level 1, 15% level 2, etc.
        severity = random.choices([1, 2, 3, 4, 5], weights=weights)[0]
        
        # Priority in simpy is inverted: lower values are higher priority
        priority = severity
        
        patient_data = {
            "id": patient_id,
            "severity": severity,
            "arrival_time": arrival_time,
            "wait_time": 0,
            "total_time": 0,
            "times_at_stages": {}
        }
        
        print(f"Time {self.env.now:.1f}: Patient {patient_id} (Severity {severity}) arrived")
        
        # Registration
        start = self.env.now
        patient_data["times_at_stages"]["registration_start"] = start
        with self.registration.request() as req:
            yield req
            # Registration process
            yield self.env.timeout(TIMES["registration"])
        patient_data["times_at_stages"]["registration_end"] = self.env.now
        
        # Triage - assessment by nurse
        start = self.env.now
        patient_data["times_at_stages"]["triage_start"] = start
        with self.nurses.request(priority=priority) as req:
            yield req
            # Triage process
            yield self.env.timeout(TIMES["triage"][severity])
        patient_data["times_at_stages"]["triage_end"] = self.env.now
        
        # Doctor examination
        start = self.env.now
        patient_data["times_at_stages"]["doctor_start"] = start
        with self.doctors.request(priority=priority) as req:
            yield req
            # Doctor examination process
            yield self.env.timeout(TIMES["doctor_examination"][severity])
        patient_data["times_at_stages"]["doctor_end"] = self.env.now
        
        # Lab tests if needed
        if random.random() < NEEDS_LAB[severity]:
            start = self.env.now
            patient_data["times_at_stages"]["lab_start"] = start
            with self.lab_techs.request(priority=priority) as req:
                yield req
                # Lab testing process
                yield self.env.timeout(TIMES["lab_test"][severity])
            patient_data["times_at_stages"]["lab_end"] = self.env.now
        
        # X-ray if needed
        if random.random() < NEEDS_XRAY[severity]:
            start = self.env.now
            patient_data["times_at_stages"]["xray_start"] = start
            with self.xray_machines.request(priority=priority) as req:
                yield req
                # X-ray process
                yield self.env.timeout(TIMES["xray"][severity])
            patient_data["times_at_stages"]["xray_end"] = self.env.now
        
        # Treatment
        start = self.env.now
        patient_data["times_at_stages"]["treatment_start"] = start
        
        # For treatment, severe cases need both doctor and nurse
        if severity <= 2:
            with self.doctors.request(priority=priority) as doc_req, \
                 self.nurses.request(priority=priority) as nurse_req:
                yield doc_req & nurse_req
                yield self.env.timeout(TIMES["treatment"][severity])
        else:
            # Less severe cases might only need a nurse
            with self.nurses.request(priority=priority) as req:
                yield req
                yield self.env.timeout(TIMES["treatment"][severity])
        
        patient_data["times_at_stages"]["treatment_end"] = self.env.now
        
        # Calculate waiting time (total time - actual service time)
        service_time = 0
        for stage in ["registration", "triage", "doctor_examination", "lab_test", "xray", "treatment"]:
            if f"{stage}_start" in patient_data["times_at_stages"] and f"{stage}_end" in patient_data["times_at_stages"]:
                service_time += TIMES.get(stage, {}).get(severity, 0) if isinstance(TIMES.get(stage, {}), dict) else TIMES.get(stage, 0)
        
        # Calculate total time spent in system
        exit_time = self.env.now
        total_time = exit_time - arrival_time
        wait_time = total_time - service_time
        
        # Record stats
        patient_data["wait_time"] = wait_time
        patient_data["total_time"] = total_time
        
        self.patient_wait_times.append(wait_time)
        self.total_times.append(total_time)
        self.patient_counts += 1
        self.patient_details.append(patient_data)
        
        print(f"Time {self.env.now:.1f}: Patient {patient_id} (Severity {severity}) discharged. "
              f"Total time: {total_time:.1f} mins, Wait time: {wait_time:.1f} mins")


def run_simulation(config, day_type="weekday", sim_time=SIM_TIME):
    """Run a simulation with given configuration."""
    env = simpy.Environment()
    
    # Create emergency department
    ed = EmergencyDepartment(
        env=env,
        num_nurses=config["nurses"],
        num_doctors=config["doctors"],
        num_lab_techs=config["lab_techs"],
        num_xray_machines=config["xray_machines"],
        day_type=day_type
    )
    
    # Start patient generator
    env.process(ed.patient_generator())
    
    # Run simulation
    env.run(until=sim_time)
    
    # Calculate costs
    monthly_cost = (
        config["nurses"] * COSTS["nurse"] +
        config["doctors"] * COSTS["doctor"] +
        config["lab_techs"] * COSTS["lab_technician"] +
        config["xray_machines"] * COSTS["xray_machine"]
    )
    
    # Return statistics
    results = {
        "config": config,
        "day_type": day_type,
        "avg_wait_time": np.mean(ed.patient_wait_times) if ed.patient_wait_times else 0,
        "avg_total_time": np.mean(ed.total_times) if ed.total_times else 0,
        "patient_count": ed.patient_counts,
        "monthly_cost": monthly_cost,
        "patient_details": ed.patient_details,
        "resource_usage": ed.resource_usage
    }
    
    return results

def analyze_results(results_list):
    """Analyze the results of multiple simulations."""
    df = pd.DataFrame([
        {
            "nurses": r["config"]["nurses"],
            "doctors": r["config"]["doctors"],
            "lab_techs": r["config"]["lab_techs"],
            "xray_machines": r["config"]["xray_machines"],
            "day_type": r["day_type"],
            "avg_wait_time": r["avg_wait_time"],
            "avg_total_time": r["avg_total_time"],
            "patient_count": r["patient_count"],
            "monthly_cost": r["monthly_cost"],
            "cost_per_patient": r["monthly_cost"] / r["patient_count"] if r["patient_count"] > 0 else float('inf')
        }
        for r in results_list
    ])
    
    return df

def generate_report_charts(results_df, best_configs):
    """Generate charts for the report."""
    # Plot the relationship between resources and wait times
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # Filter for weekday results
    weekday_df = results_df[results_df['day_type'] == 'weekday']
    
    # Group by number of nurses and calculate average wait times
    nurse_data = weekday_df.groupby('nurses')['avg_wait_time'].mean().reset_index()
    axes[0, 0].plot(nurse_data['nurses'], nurse_data['avg_wait_time'], marker='o')
    axes[0, 0].set_title('Average Wait Time vs Number of Nurses (Weekday)')
    axes[0, 0].set_xlabel('Number of Nurses')
    axes[0, 0].set_ylabel('Average Wait Time (minutes)')
    axes[0, 0].grid(True)
    
    # Group by number of doctors and calculate average wait times
    doctor_data = weekday_df.groupby('doctors')['avg_wait_time'].mean().reset_index()
    axes[0, 1].plot(doctor_data['doctors'], doctor_data['avg_wait_time'], marker='o')
    axes[0, 1].set_title('Average Wait Time vs Number of Doctors (Weekday)')
    axes[0, 1].set_xlabel('Number of Doctors')
    axes[0, 1].set_ylabel('Average Wait Time (minutes)')
    axes[0, 1].grid(True)
    
    # Group by number of lab techs and calculate average wait times
    lab_tech_data = weekday_df.groupby('lab_techs')['avg_wait_time'].mean().reset_index()
    axes[1, 0].plot(lab_tech_data['lab_techs'], lab_tech_data['avg_wait_time'], marker='o')
    axes[1, 0].set_title('Average Wait Time vs Number of Lab Techs (Weekday)')
    axes[1, 0].set_xlabel('Number of Lab Techs')
    axes[1, 0].set_ylabel('Average Wait Time (minutes)')
    axes[1, 0].grid(True)
    
    # Group by number of X-ray machines and calculate average wait times
    xray_data = weekday_df.groupby('xray_machines')['avg_wait_time'].mean().reset_index()
    axes[1, 1].plot(xray_data['xray_machines'], xray_data['avg_wait_time'], marker='o')
    axes[1, 1].set_title('Average Wait Time vs Number of X-ray Machines (Weekday)')
    axes[1, 1].set_xlabel('Number of X-ray Machines')
    axes[1, 1].set_ylabel('Average Wait Time (minutes)')
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('resource_vs_wait_time.png')
    
    # Compare wait times for different day types with best configurations
    day_types = ['weekday', 'weekend', 'holiday']
    wait_times = []
    total_times = []
    
    for day_type in day_types:
        day_df = results_df[results_df['day_type'] == day_type]
        best_config_for_day = best_configs[day_type]
        
        # Get the row with this configuration
        config_row = day_df[(day_df['nurses'] == best_config_for_day['nurses']) & 
                            (day_df['doctors'] == best_config_for_day['doctors']) & 
                            (day_df['lab_techs'] == best_config_for_day['lab_techs']) & 
                            (day_df['xray_machines'] == best_config_for_day['xray_machines'])]
        
        wait_times.append(config_row['avg_wait_time'].values[0])
        total_times.append(config_row['avg_total_time'].values[0])
    
    # Plot wait times by day type
    plt.figure(figsize=(10, 6))
    plt.bar(day_types, wait_times)
    plt.title('Average Wait Times for Best Configurations by Day Type')
    plt.xlabel('Day Type')
    plt.ylabel('Average Wait Time (minutes)')
    plt.grid(axis='y')
    plt.savefig('wait_times_by_day_type.png')
    
    # Plot total times by day type
    plt.figure(figsize=(10, 6))
    plt.bar(day_types, total_times)
    plt.title('Average Total Times for Best Configurations by Day Type')
    plt.xlabel('Day Type')
    plt.ylabel('Average Total Time (minutes)')
    plt.grid(axis='y')
    plt.savefig('total_times_by_day_type.png')
    
    # Plot cost comparison of different configurations
    plt.figure(figsize=(12, 8))
    
    # Get unique configurations
    unique_configs = []
    for day_type in day_types:
        config = best_configs[day_type]
        config_tuple = (config['nurses'], config['doctors'], config['lab_techs'], config['xray_machines'])
        if config_tuple not in unique_configs:
            unique_configs.append(config_tuple)
    
    # Calculate costs for each unique configuration
    config_labels = []
    config_costs = []
    
    for config in unique_configs:
        nurses, doctors, lab_techs, xray_machines = config
        cost = (nurses * COSTS['nurse'] + 
                doctors * COSTS['doctor'] + 
                lab_techs * COSTS['lab_technician'] + 
                xray_machines * COSTS['xray_machine'])
        
        label = f"N:{nurses} D:{doctors} L:{lab_techs} X:{xray_machines}"
        config_labels.append(label)
        config_costs.append(cost)
    
    plt.bar(config_labels, config_costs)
    plt.title('Monthly Cost Comparison of Different Resource Configurations')
    plt.xlabel('Configuration (N:Nurses, D:Doctors, L:Lab Techs, X:X-ray Machines)')
    plt.ylabel('Monthly Cost (USD)')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig('configuration_costs.png')

def main():
    # Define various configurations to test
    configurations = []
    
    # Base configurations
    for nurses in range(2, 6):
        for doctors in range(2, 6):
            for lab_techs in range(1, 4):
                for xray_machines in range(1, 4):
                    configurations.append({
                        "nurses": nurses,
                        "doctors": doctors,
                        "lab_techs": lab_techs,
                        "xray_machines": xray_machines
                    })
    
    # Run simulations for each configuration and day type
    results = []
    day_types = ["weekday", "weekend", "holiday"]
    
    for config in configurations:
        for day_type in day_types:
            print(f"\nRunning simulation for {day_type} with configuration: {config}")
            result = run_simulation(config, day_type)
            results.append(result)
            print(f"Average wait time: {result['avg_wait_time']:.2f} minutes")
            print(f"Average total time: {result['avg_total_time']:.2f} minutes")
            print(f"Patients treated: {result['patient_count']}")
            print(f"Monthly cost: ${result['monthly_cost']}")
    
    # Analyze results
    results_df = analyze_results(results)
    
    # Find the best configuration for each day type
    # Define 'best' as lowest wait time while keeping cost reasonable
    # We'll set a threshold of acceptable wait time and then choose the cheapest configuration
    acceptable_wait_time = 30  # minutes
    
    best_configs = {}
    for day_type in day_types:
        day_df = results_df[results_df['day_type'] == day_type]
        # Filter for configurations with acceptable wait times
        acceptable_df = day_df[day_df['avg_wait_time'] <= acceptable_wait_time]
        
        if len(acceptable_df) > 0:
            # Choose the cheapest configuration among those with acceptable wait times
            best_row = acceptable_df.loc[acceptable_df['monthly_cost'].idxmin()]
        else:
            # If no configuration meets the threshold, choose the one with lowest wait time
            best_row = day_df.loc[day_df['avg_wait_time'].idxmin()]
        
        best_configs[day_type] = {
            "nurses": int(best_row['nurses']),
            "doctors": int(best_row['doctors']),
            "lab_techs": int(best_row['lab_techs']),
            "xray_machines": int(best_row['xray_machines']),
            "avg_wait_time": best_row['avg_wait_time'],
            "monthly_cost": best_row['monthly_cost']
        }
    
    # Generate charts for the report
    generate_report_charts(results_df, best_configs)
    
    # Print the best configurations
    print("\nRecommended Resource Configurations:")
    for day_type, config in best_configs.items():
        print(f"\n{day_type.capitalize()}:")
        print(f"  Nurses: {config['nurses']}")
        print(f"  Doctors: {config['doctors']}")
        print(f"  Lab Technicians: {config['lab_techs']}")
        print(f"  X-ray Machines: {config['xray_machines']}")
        print(f"  Average Wait Time: {config['avg_wait_time']:.2f} minutes")
        print(f"  Monthly Cost: ${config['monthly_cost']}")
    
    # guarda los resultados del CSV 
    results_df.to_csv('simulation_results.csv', index=False)
    
    # guarda la configuracion para el reporte
    with open('recommended_configurations.txt', 'w') as f:
        f.write("Recommended Resource Configurations:\n")
        for day_type, config in best_configs.items():
            f.write(f"\n{day_type.capitalize()}:\n")
            f.write(f"  Nurses: {config['nurses']}\n")
            f.write(f"  Doctors: {config['doctors']}\n")
            f.write(f"  Lab Technicians: {config['lab_techs']}\n")
            f.write(f"  X-ray Machines: {config['xray_machines']}\n")
            f.write(f"  Average Wait Time: {config['avg_wait_time']:.2f} minutes\n")
            f.write(f"  Monthly Cost: ${config['monthly_cost']}\n")
    main()