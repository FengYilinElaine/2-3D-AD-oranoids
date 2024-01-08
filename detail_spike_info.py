import os
import glob
import pandas as pd

# Define the main folder path
main_folder_path = '/Users/ellinfff/Desktop/AD类器官&电生理/DATA/calcium image/230722 mg withtornot'

# Find all 'spike_metrics.csv' files in the subfolders
spike_metrics_files = glob.glob(os.path.join(main_folder_path, '**/spike_metrics.csv'), recursive=True)

# Process each 'spike_metrics.csv' file
for file_path in spike_metrics_files:
    # Read the spike metrics summary file
    spike_metrics_summary = pd.read_csv(file_path)

    # Initialize an empty list to store the detailed spike data
    detailed_spike_data = []

    # Iterate over each row in the spike_metrics_summary to extract and number the spikes
    for index, row in spike_metrics_summary.iterrows():
        roi = row['ROI']
        num_spikes = row['Spike Count']
        intervals = eval(row['Spike Intervals'])  # Convert string representation of list back to list
        amplitudes = eval(row['Spike Amplitudes'])
        decay_times = eval(row['Decay Time'])

        if num_spikes > 0:
            for spike_num in range(num_spikes):
                spike_detail = {
                    'ROI': roi,
                    'Spike Number': spike_num + 1,
                    'Interval': intervals[spike_num] if spike_num < len(intervals) else None,
                    'Amplitude': amplitudes[spike_num] if spike_num < len(amplitudes) else None,
                    'Decay Time': decay_times[spike_num] if spike_num < len(decay_times) else None
                }
                detailed_spike_data.append(spike_detail)

    # Convert the list of detailed spike data to a DataFrame
    detailed_spike_df = pd.DataFrame(detailed_spike_data)

    # Get the directory of the current spike_metrics.csv file
    current_dir = os.path.dirname(file_path)

    # Save the detailed spike data DataFrame back to the same subfolder
    detailed_spike_df.to_csv(os.path.join(current_dir, 'detailed_spikeofallroi_data.csv'), index=False)

    print(f"Detailed spike data saved in {current_dir}")
