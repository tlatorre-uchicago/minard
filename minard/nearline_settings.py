# List of all nearline job types
jobTypes = ["All","DAQ","SMELLIE","BLINDNESS_CHUNKER","PCA_TELLIE","RUN","TELLIE","ECA","PING_CRATES","PMTCalStatus","ANALYSIS","DQHL","CHS","DQLL","PMTNOISE","CHANNEL_FLAGS","CLOCK_JUMPS"]

# Map failures modes to failure type
failModes = {1: "Failure", 2: "Warning", 3: "Debug", 4: "Not Run", 97: "Timed Out", 98: "Not Executable", -1: "Killed By Signal", 0: "All Failure Types", -99: "Everything", -98: "Not Launched"}
