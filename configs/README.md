# Configuration Profiles

This directory contains pre-configured YAML files for common use cases.

## Available Profiles

### default.yaml
Balanced settings suitable for most indoor surveillance scenarios.
- Good balance between sensitivity and noise reduction
- Moderate processing speed
- **Use when**: Processing typical indoor surveillance footage

### high-sensitivity.yaml
Optimized for detecting smaller movements and objects.
- Lower detection thresholds
- Shorter minimum layer lengths
- Less frame averaging
- **Use when**: You need to catch subtle movements or smaller objects
- **Use when**: Indoor scenes with good lighting

### low-sensitivity.yaml
Reduced sensitivity to avoid false positives from environmental noise.
- Higher detection thresholds
- Longer minimum layer lengths
- More frame averaging
- **Use when**: Outdoor scenes with weather changes (clouds, wind)
- **Use when**: You want to focus only on significant movements
- **Use when**: Reducing false positives is more important than catching everything

### fast.yaml
Optimized for processing speed at the cost of some accuracy.
- Lower resolution processing (480p instead of 700p)
- Smaller buffers
- Minimal averaging
- **Use when**: Quick preview or testing
- **Use when**: Processing very long videos
- **Use when**: Running on limited hardware

## Usage

```bash
# Use a specific profile
python main.py input_video.mp4 output_dir configs/default.yaml

# Override specific settings with environment variables
export VIDEO_SUMMARY_THRESHOLD=10
python main.py input_video.mp4 output_dir configs/default.yaml
```

## Creating Custom Profiles

Copy any of these files and modify parameters to create your own profile:

```bash
cp configs/default.yaml configs/my-custom.yaml
# Edit my-custom.yaml with your preferred settings
python main.py input_video.mp4 output_dir configs/my-custom.yaml
```

## Parameter Tuning Guide

### Increasing Sensitivity (detect more movement)
- Decrease `threshold` (e.g., 4-5)
- Decrease `min_area` (e.g., 100-200)
- Decrease `minLayerLength` (e.g., 20-30)

### Decreasing Sensitivity (reduce noise)
- Increase `threshold` (e.g., 10-15)
- Increase `min_area` (e.g., 500-1000)
- Increase `minLayerLength` (e.g., 60-100)
- Increase `avgNum` (e.g., 15-20)

### Improving Performance
- Decrease `resizeWidth` (e.g., 480-600)
- Decrease `videoBufferLength` (e.g., 100-150)
- Decrease `avgNum` (e.g., 5)

### Handling Outdoor Scenes
- Increase `avgNum` (e.g., 15-20) to smooth out clouds/leaves
- Increase `threshold` (e.g., 10-12)
- Increase `ttolerance` (e.g., 80-100) for wind-affected objects
