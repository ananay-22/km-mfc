import pandas as pd
import json
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)

def unpackPcbData(dict_input):
    def safe_get(adc, name, field):
        return dict_input.get(adc, {}).get(name, {}).get(field, None)

    # Explicit fixed order
    v0 = safe_get("ADC0", "voltage 1", "voltage")
    v1 = safe_get("ADC0", "voltage 2", "voltage")
    v2 = safe_get("ADC1", "voltage 1", "voltage")
    v3 = safe_get("ADC1", "voltage 2", "voltage")

    i0 = safe_get("ADC0", "current 1", "current")
    i1 = safe_get("ADC0", "current 2", "current")
    i2 = safe_get("ADC1", "current 1", "current")
    i3 = safe_get("ADC1", "current 2", "current")

    return [v0, v1, v2, v3, i0, i1, i2, i3]


def unpackTerosData(data_dict):
    """
    Extracts elapsed_time, volumetric_water_content, temperature, electric_conductivity.
    Returns None if any field is missing.
    """
    if not isinstance(data_dict, dict):
        return [None, None, None, None]

    return [
        data_dict.get("elapsed_time"),
        data_dict.get("volumetric_water_content"),
        data_dict.get("temperature"),
        data_dict.get("electric_conductivity")
    ]



while(True):
    board = input("Board: ")
    if board in ['KMM1', 'KMM2', 'KMM3', 'KMM4']:
        break

while(True):
    t = int(input("time: "))
    if t in [1, 10, 100]:
        break

cell_names = pd.read_excel("C:\\Users\\omerm\\OneDrive - Georgia Institute of Technology\\Ka Moamoa Lab\\SMFCs\\Reference Materials\\Boards.xlsx")
cell_names = cell_names[board]

waterlogged = pd.read_excel("C:\\Users\\omerm\\OneDrive - Georgia Institute of Technology\\Ka Moamoa Lab\\SMFCs\\Reference Materials\\Waterlogged.xlsx")

flooded_cells = ['Mehmet', 'Suleyman', 'Lanai', 'Oahu', 'Maui', 'Osman']

pcb_json = []
teros_json = []
with open(f"ERPdata/{board}_ERP_{t}s.json", "r") as f:
    for line in f:
        record = json.loads(line)
        if record["sensor_name"] == "pcb_main":
            pcb_json.append(record)
        elif record["sensor_name"] == "teros_main":
            teros_json.append(record)

pcb_df = pd.DataFrame(pcb_json)[['timestamp', 'data']]

try:
    teros_df = pd.DataFrame(teros_json)[['timestamp', 'data']]
    # Flatten 'data' into separate columns
    teros_flat = pd.DataFrame(
        teros_df["data"].map(unpackTerosData).tolist(),
        columns=["elapsed_time", "vwc", "temp", "ec"],
        index=teros_df.index)
    teros_df = pd.concat([teros_df["timestamp"], teros_flat], axis=1)
    teros_df.drop('elapsed_time', axis=1, inplace=True)
    teros_df["Timestamp"] = pd.to_datetime(teros_df.iloc[:, 0], unit='s')
    teros_df.drop("timestamp", axis=1, inplace=True)
    ts = teros_df['Timestamp'].copy()
    teros_df = teros_df.drop(columns=['Timestamp'])
    teros_df.insert(0, 'Timestamp', ts)
except:
    teros_df = pd.DataFrame()


pcb_df["data"] = pcb_df["data"].map(unpackPcbData)
pcb_df[["v0", "v1", "v2", "v3", "i0", "i1", "i2", "i3"]] = pcb_df['data'].tolist()
pcb_df.drop('data', axis=1, inplace=True)



pcb_df["Timestamp"] = pd.to_datetime(pcb_df.iloc[:, 0], unit='s')

pcb_df.drop("timestamp", axis=1, inplace=True)


ts = pcb_df['Timestamp'].copy()
pcb_df = pcb_df.drop(columns=['Timestamp'])
pcb_df.insert(0, 'Timestamp', ts)
if board != 'KMM1':
    try:
        scales = pcb_df['v3'].tolist()
        scales = [x for x in scales if x > 1.0]
        scale = sum(scales) / len(scales)
    except:
        scale = 1.15
else:
    scale = 1.15
v_cols = ['v0', 'v1', 'v2', 'v3']
pcb_df[v_cols] = pcb_df[v_cols].apply(lambda x: x / scale)
pcb_df[['i0', 'i1', 'i2']] = pcb_df[['i0', 'i1', 'i2']].apply(lambda x: abs(x))

print(pcb_df)


# Graph
fig, ax1 = plt.subplots(figsize=(8, 5))

# Plot PCB voltages on the first y-axis
ax1.plot(pcb_df.iloc[:, 0], pcb_df.iloc[:, 1], label='v0')
ax1.plot(pcb_df.iloc[:, 0], pcb_df.iloc[:, 2], label='v1')
ax1.plot(pcb_df.iloc[:, 0], pcb_df.iloc[:, 3], label='v2')
"""
if board == 'KMM1':
    ax1.plot(pcb_df.iloc[:, 0], pcb_df.iloc[:, 4], label=cell_names[3])
"""

ax1.set_xlabel(pcb_df.columns[0])  # x-axis label
ax1.set_ylabel("Voltage")
ax1.set_title("Timestamp x Cell Voltages")
ax1.grid(True)
"""
ax2 = ax1.twinx()
ax2.plot(pcb_df.iloc[:, 0], pcb_df.iloc[:, 5], label="i0", color="pink")
ax2.plot(pcb_df.iloc[:, 0], pcb_df.iloc[:, 6], label="i1", color='purple')
ax2.plot(pcb_df.iloc[:, 0], pcb_df.iloc[:, 7], label="i2", color='brown')
ax2.set_ylabel("Current")

# Collect handles and labels from both axes
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

# Combine handles and labels
combined_handles = handles1 + handles2
combined_labels = labels1 + labels2

# Create a single legend using the combined handles and labels
legend_texts = ax1.legend(combined_handles, combined_labels, loc='lower right').get_texts()
"""
plt.xlim(min(pcb_df['Timestamp'].tolist()), max(pcb_df['Timestamp'].tolist()))

plt.show()
