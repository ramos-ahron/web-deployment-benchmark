# monitoring

Owner: Aaron

Scripts that collect CPU and memory usage at about one-second intervals on the web VM, database VM, and load generator VM. Container statistics are collected as extra information.

The whole-web-VM measurements are the main source for the native vs Docker resource comparison. Timestamps must line up with the measured portion of each k6 run, and output files use the run ID.
