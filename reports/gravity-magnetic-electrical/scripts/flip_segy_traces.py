from pathlib import Path
import struct


SOURCE = Path("探地雷达实验/DAT_0002.SGY")
OUTPUT = Path("探地雷达实验/DAT_0002_反向.SGY")

data = SOURCE.read_bytes()
file_header = data[:3600]

# Prism2 exports this SEG-Y variant in little-endian order.
sample_count = struct.unpack("<H", file_header[3220:3222])[0]
sample_format = struct.unpack("<H", file_header[3224:3226])[0]
bytes_per_sample = {1: 4, 2: 4, 3: 2, 5: 4, 8: 1}.get(sample_format)
if bytes_per_sample is None:
    raise ValueError(f"Unsupported SEG-Y sample format: {sample_format}")

trace_size = 240 + sample_count * bytes_per_sample
payload = data[3600:]
if len(payload) % trace_size:
    raise ValueError("SEG-Y payload does not contain whole trace records")

traces = [
    bytearray(payload[offset:offset + trace_size])
    for offset in range(0, len(payload), trace_size)
]
traces.reverse()

# Rewrite trace sequence numbers so the flipped file has ascending trace order.
for number, trace in enumerate(traces, start=1):
    trace[0:4] = struct.pack("<I", number)
    trace[4:8] = struct.pack("<I", number)

OUTPUT.write_bytes(file_header + b"".join(traces))
print(f"{OUTPUT}: {len(traces)} traces, {sample_count} samples/trace")
