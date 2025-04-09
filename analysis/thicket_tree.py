import thicket as tt
from sys import argv

if len(argv) != 2:
    print("Usage: python thicket.py <caliper_file>")
    exit(1)

filepath = argv[1]
th = tt.Thicket.from_caliperreader(filepath)
print(th.tree(metric_column="Avg time/rank"))
