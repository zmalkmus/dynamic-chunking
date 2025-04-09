import thicket as tt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

test = 'liburing'

# Parameters
if test == 'tellico':
    cuda = True
    afo_cuda_usage = '../data/cases/all_first_occur/tellico-compute0-80682-Cuda.memspace_usage'
    afo_host_usage = '../data/cases/all_first_occur/tellico-compute0-80682-Host.memspace_usage'
    afo_events = '../data/cases/all_first_occur/tellico-compute0-80682.mem_events'

    afd_cuda_usage = '../data/cases/all_fixed_duplicates/tellico-compute0-81874-Cuda.memspace_usage'
    afd_host_usage = '../data/cases/all_fixed_duplicates/tellico-compute0-81874-Host.memspace_usage'
    afd_events = '../data/cases/all_fixed_duplicates/tellico-compute0-81874.mem_events'

    sfm_cuda_usage = '../data/cases/shifted_fixed_mix/tellico-compute0-82709-Cuda.memspace_usage'
    sfm_host_usage = '../data/cases/shifted_fixed_mix/tellico-compute0-82709-Host.memspace_usage'
    sfm_events = '../data/cases/shifted_fixed_mix/tellico-compute0-82709.mem_events'

    afo_changes = '../data/cases/all_first_occur/changes.csv'
    afd_changes = '../data/cases/all_fixed_duplicates/changes.csv'
    sfm_changes = '../data/cases/shifted_fixed_mix/changes.csv'

# Parameters LIBURING IMPLEMENTATION
case_path = '/home/zmalk/Research/ANL/checkpoint_restore_analysis/data/liburing/cases/'

if test == 'liburing':
    cuda = False
    afo_host_usage = case_path + '/afo/memtest/1.memspace_usage'
    afo_events = case_path + '/afo/memtest/1.mem_events'

    afd_host_usage = case_path +  '/afd/memtest/1.memspace_usage'
    afd_events = case_path + '/afd/memtest/1.mem_events'

    sfm_host_usage = case_path + '/sfm/memtest/1.memspace_usage'
    sfm_events = case_path + '/sfm/memtest/1.mem_events'

    afo_changes = case_path + '/afo/changes.csv'
    afd_changes = case_path + '/afd/changes.csv'
    sfm_changes = case_path + '/sfm/changes.csv'

if test == 'old':
    cuda = False
    afo_host_usage = case_path + '/afo/baseline/1.memspace_usage'
    afo_events = case_path + '/afo/baseline/1.mem_events'

    afd_host_usage = case_path+  '/afd/baseline/1.memspace_usage'
    afd_events = case_path + '/afd/baseline/1.mem_events'

    sfm_host_usage = case_path + '/sfm/baseline/1.memspace_usage'
    sfm_events = case_path + '/sfm/baseline/1.mem_events'

    afo_changes = case_path + '/afo/changes.csv'
    afd_changes = case_path + '/afd/changes.csv'
    sfm_changes = case_path + '/sfm/changes.csv'

def main():
    print("Processing data...")

    # Read in the data for cuda_usage
    columns_usage = ['Time(s)', 'Size(MB)', 'HighWater(MB)', 'HighWater-Process(MB)']

    if cuda:
        data_afo_cuda_usage = pd.read_csv(afo_cuda_usage, comment='#', header=None, delim_whitespace=True, names=columns_usage)
        data_afd_cuda_usage = pd.read_csv(afd_cuda_usage, comment='#', header=None, delim_whitespace=True, names=columns_usage)
        data_sfm_cuda_usage = pd.read_csv(sfm_cuda_usage, comment='#', header=None, delim_whitespace=True, names=columns_usage)

        # Add a column indicating the test case
        data_afo_cuda_usage['Test Case'] = 'All First Occur'
        data_afd_cuda_usage['Test Case'] = 'All Fixed Duplicates'
        data_sfm_cuda_usage['Test Case'] = 'Shifted Fixed Mix'

    # Similarly for host_usage
    data_afo_host_usage = pd.read_csv(afo_host_usage, comment='#', header=None, delim_whitespace=True, names=columns_usage)
    data_afd_host_usage = pd.read_csv(afd_host_usage, comment='#', header=None, delim_whitespace=True, names=columns_usage)
    data_sfm_host_usage = pd.read_csv(sfm_host_usage, comment='#', header=None, delim_whitespace=True, names=columns_usage)

    data_afo_host_usage['Test Case'] = 'All First Occur'
    data_afd_host_usage['Test Case'] = 'All Fixed Duplicates'
    data_sfm_host_usage['Test Case'] = 'Shifted Fixed Mix'

    # Read in mem_events data
    columns_mem_events = ['Time(s)', 'Ptr', 'Size', 'MemSpace', 'Op', 'Name']

    def read_mem_events(filename):
        data = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or line == '':
                    continue
                else:
                    parts = line.split(maxsplit=5)
                    if len(parts) == 6:
                        data.append(parts)
                    else:
                        data.append(parts + ['']*(6 - len(parts)))
        df = pd.DataFrame(data, columns=columns_mem_events)
        return df

    data_afo_mem_events = read_mem_events(afo_events)
    data_afd_mem_events = read_mem_events(afd_events)
    data_sfm_mem_events = read_mem_events(sfm_events)

    # Add test case column
    data_afo_mem_events['Test Case'] = 'All First Occur'
    data_afd_mem_events['Test Case'] = 'All Fixed Duplicates'
    data_sfm_mem_events['Test Case'] = 'Shifted Fixed Mix'

    # Concatenate data from all test cases for each type
    if cuda:
        cuda_usage_data = pd.concat([data_afo_cuda_usage, data_afd_cuda_usage, data_sfm_cuda_usage], ignore_index=True)
    host_usage_data = pd.concat([data_afo_host_usage, data_afd_host_usage, data_sfm_host_usage], ignore_index=True)
    mem_events_data = pd.concat([data_afo_mem_events, data_afd_mem_events, data_sfm_mem_events], ignore_index=True)

    # Convert columns to appropriate data types
    # For cuda_usage and host_usage
    usage_numeric_cols = ['Time(s)', 'Size(MB)', 'HighWater(MB)', 'HighWater-Process(MB)']
    # cuda_usage_data[usage_numeric_cols] = cuda_usage_data[usage_numeric_cols].apply(pd.to_numeric)
    host_usage_data[usage_numeric_cols] = host_usage_data[usage_numeric_cols].apply(pd.to_numeric)

    # For mem_events
    mem_events_data['Time(s)'] = pd.to_numeric(mem_events_data['Time(s)'], errors='coerce')
    mem_events_data['Size'] = pd.to_numeric(mem_events_data['Size'], errors='coerce')

    # Process mem_events data
    mem_events_data.sort_values(by=['Test Case', 'Time(s)'], inplace=True)
    mem_events_data['Size(MB)'] = mem_events_data['Size'] / (1024 * 1024)
    mem_events_data['Cumulative Size(MB)'] = mem_events_data.groupby('Test Case')['Size(MB)'].cumsum()

    # ================ Plot Data ================

    if cuda:
        # Plotting cuda_usage
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=cuda_usage_data, x='Time(s)', y='Size(MB)', hue='Test Case')
        plt.title('CUDA Usage over Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Size (MB)')
        plt.legend(title='Test Case')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('../graphs/cuda_usage_plot.png')
        plt.show()

    # Plotting host_usage
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=host_usage_data, x='Time(s)', y='Size(MB)', hue='Test Case')
    if test == 'liburing':
        plt.title('Liburing Restore Host Usage Over Time')
    elif test == 'tellico':
        plt.title('Tellico Host Usage Over Time')
    elif test == 'old':
        plt.title('Old Host Usage Over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Size (MB)')
    plt.legend(title='Test Case')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../graphs/host_usage_plot.png')
    plt.show()

    # Plotting mem_events cumulative size
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=mem_events_data, x='Time(s)', y='Cumulative Size(MB)', hue='Test Case')
    if test == 'liburing':
        plt.title('Liburing Restore Memory Events Cumulative Size Over Time')
    elif test == 'tellico':
        plt.title('Tellico Memory Events Cumulative Size Over Time')
    elif test == 'old':
        plt.title('Old Memory Events Cumulative Size Over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Cumulative Size (MB)')
    plt.legend(title='Test Case')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('../graphs/mem_events_cumulative_size_plot.png')
    plt.show()

if __name__ == '__main__':
    main()

print("Done.")
