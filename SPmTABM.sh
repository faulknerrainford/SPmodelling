#!/bin/sh
# Set up while loop for the number of required runs
i=0
while $i<"$1"
do
  # Run the reset script handed into the arguments. Give it enough values to set the save out scripts tag
  python Reset.py i "$3" "$2"
  # Parrallel run the different parts of the model with the run length so they close correctly
  python Monitor.py "$2" &
  python Population.py "$2" "$3" &
  python Structure.py "$2" &
  python Balancer.py "$2" &
  python Flow.py "$2" &
  $i++
done