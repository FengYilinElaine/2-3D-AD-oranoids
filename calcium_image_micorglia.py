import os
import glob
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Start time should not be indented if it's not inside a function or loop
start_time = time.time()

# Define your main folder path
main_folder_path = '/Users/ellinfff/Desktop/AD类器官&电生理/DATA/calcium image/230722 mg withtornot'

# Find all CSV files in the subfolders
csv_files = glob.glob(os.path.join(main_folder_path, '**/*.csv'), recursive=True)

# Process each CSV file
for file_path in csv_files:
    # Read the CSV file
    data = pd.read_csv(file_path)
    

# Assuming your DataFrame has columns like 'Frame', 'Area1', 'IntDen1', 'Area2', 'IntDen2', ...

    # Find the count of 'Area[number]' columns
    area_columns = [col for col in data.columns if col.startswith('Area')]
    n = len(area_columns)

    # Initialize an empty DataFrame for roi_data
    roi_data = pd.DataFrame()

    # Loop over the range of Area numbers
    for i in range(1, n + 1):
        if f'Area{i}' in data.columns and f'IntDen{i}' in data.columns:
            temp = data[['Frame', f'Area{i}', f'IntDen{i}']].copy()
            temp.rename(columns={f'Area{i}': 'Area', f'IntDen{i}': 'IntDen'}, inplace=True)
            temp['ROI'] = i
            roi_data = pd.concat([roi_data, temp])

    # Calculate F0 for each ROI
    F0 = roi_data.groupby('ROI')['IntDen'].apply(lambda x: x.quantile(0.25))

    # Calculate Delta F and Delta F/F0
    roi_data = roi_data.merge(F0.rename('F0'), on='ROI')
    roi_data['Delta_F'] = roi_data['IntDen'] - roi_data['IntDen'].min()  # Assuming F background is the minimum IntDen
    roi_data['Delta_F_F0'] = roi_data['Delta_F'] / roi_data['F0']

    # Calculate maximum Delta F/F0 for each ROI
    max_delta_f_f0 = roi_data.groupby('ROI')['Delta_F_F0'].max()

    # Calculate AUC for each ROI
    auc = roi_data.groupby('ROI')['Delta_F_F0'].apply(np.trapz)

    def analyze_spikes(data, threshold, window_size, min_interval):
        spikes = 0
        intervals = []
        amplitudes = []
        decay_times = []
        last_spike_frame = -min_interval  # Initialize to start outside the min interval

        # Check for spikes within each possible window
        for i in range(len(data) - window_size):
            for j in range(i + 1, i + window_size + 1):  # Nested loop to check every possible end point in the window
                window_data = data.iloc[i:j]

                max_val = window_data.max()
                min_val = window_data.min()
                max_index = window_data.idxmax()
                min_index = window_data.idxmin()

                # Check for spike characteristics and interval criteria
                if max_index > min_index and max_val - min_val >= threshold:
                    decay_time = abs(max_index - min_index) + 1

                    # Check if absolute decay time is within the specified limit
                    if 3 <= decay_time <= 100 and j - last_spike_frame >= min_interval:
                        spikes += 1
                        amplitude = max_val - min_val
                        amplitudes.append(amplitude)
                        decay_times.append(decay_time)

                        intervals.append(j - last_spike_frame)
                        last_spike_frame = j
                        break  # Break out of the inner loop once a spike is found

        return spikes, intervals, amplitudes, decay_times  # Correctly indented inside the function


    # Set your spike detection parameters
    threshold = 0.6  # Define your threshold for a spike
    window_size = 35  # Window size for detecting spike
    min_spike_interval = 25  # Minimum interval between spikes

    # Analyze spikes for each ROI
    spike_info = roi_data.groupby('ROI')['Delta_F_F0'].apply(lambda x: analyze_spikes(x, threshold, window_size, min_spike_interval))

    # Extract spike counts, intervals, and amplitudes
    spike_counts = spike_info.apply(lambda x: x[0])
    spike_intervals = spike_info.apply(lambda x: x[1])
    spike_amplitudes = spike_info.apply(lambda x: x[2])

    # Create a summary DataFrame
    summary_df = pd.DataFrame({
        'Area Number': spike_counts.index,
        'AUC': auc.values
    })

    # Extract spike counts, intervals, amplitudes, and decay times
    spike_counts = spike_info.apply(lambda x: x[0])
    spike_intervals = spike_info.apply(lambda x: x[1])
    spike_amplitudes = spike_info.apply(lambda x: x[2])
    spike_decay_times = spike_info.apply(lambda x: x[3])

    # Create a summary DataFrame for spike metrics
    spike_metrics_summary = pd.DataFrame({
        'ROI': spike_info.index,
        'Spike Count': spike_counts.values,
        'Spike Intervals': spike_intervals.apply(lambda x: str(x)).values,
        'Spike Amplitudes': spike_amplitudes.apply(lambda x: str(x)).values,
        'Decay Time': spike_decay_times.apply(lambda x: str(x)).values
    })

    # Initialize a list to store the detailed spike data
    detailed_spike_data = []

    # Iterate over each ROI to extract and number the spikes
    for roi in spike_info.index:
        num_spikes = spike_info.loc[roi][0]  # Number of spikes for this ROI
        intervals = spike_info.loc[roi][1]
        amplitudes = spike_info.loc[roi][2]
        decay_times = spike_info.loc[roi][3]

    # Only proceed if there are spikes
    if num_spikes > 0:
        for spike_num in range(num_spikes):
            spike_detail = {
                'ROI': roi,
                'Spike Number': spike_num + 1,  # Spike numbering starts from 1
                'Interval': intervals[spike_num] if spike_num < len(intervals) else None,
                'Amplitude': amplitudes[spike_num] if spike_num < len(amplitudes) else None,
                'Decay Time': decay_times[spike_num] if spike_num < len(decay_times) else None
            }
            detailed_spike_data.append(spike_detail)

   # Create a DataFrame from the detailed spike data
    detailed_spike_df = pd.DataFrame(detailed_spike_data)

    # Get the directory of the current CSV file
    current_dir = os.path.dirname(file_path)

    # Save all processed data back to the same subfolder
    roi_data.to_csv(os.path.join(current_dir, 'deltaf_results.csv'), index=False)
    max_delta_f_f0.to_csv(os.path.join(current_dir, 'max_delta_f_f0.csv'), index=False)
    summary_df.to_csv(os.path.join(current_dir, 'auc.csv'), index=False)
    spike_metrics_summary.to_csv(os.path.join(current_dir, 'spike_metrics.csv'), index=False)
    detailed_spike_df.to_csv(os.path.join(current_dir, 'detailed_spike_data.csv'), index=False)

    print(f"Processed data saved in {current_dir}")

    # End the timer for each file and print the duration
    end_time = time.time()
    duration = end_time - start_time
    print(f"Processed {file_path} in {duration} seconds.")

# Global end time
global_end_time = time.time()
global_duration = global_end_time - start_time
print(f"Total processing time: {global_duration} seconds.")
