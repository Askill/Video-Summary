
# Video Synopsis and Classification

## Example:
![docs/demo.gif](./docs/demo.gif)  
What you see above is a 15 second exerpt of a 2 minute overlayed synopsis of a 2.5h video from an on campus web cam.  
The synopsis took 40 minutes from start to finish on a 8 core machine and used a maximum of 6Gb of RAM.

## Benchmark
Below you can find the benchmark results for a 10 minutes clip, with the stacked time per componenent on the x-axis.  
The tests were done on a machine with a Ryzen 3700X with 8 cores 16 threads and 32 Gb of RAM.
![docs/demo.gif](./docs/bm.jpg)  



#### notes:

install tensorflow==1.15.0 and tensorflow-gpu==1.15.0, cuda 10.2 and 10.0, copy missing files from 10.0 to 10.2, restart computer, set maximum vram
