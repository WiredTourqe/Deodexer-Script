
# Deodexer Script

This script deodexes `.odex` files using the [baksmali](https://github.com/JesusFreke/smali) tool. It supports multithreading, enabling it to process multiple files at once for improved speed and efficiency.

## Requirements

- **Java**: Ensure Java is installed and accessible from the command line. Verify installation with:
  ```bash
  java -version
  ```
- **baksmali**: The baksmali JAR file is required for deodexing. Download the latest version from the [baksmali GitHub repository](https://github.com/JesusFreke/smali).

## Installation

1. Download or clone this repository.
2. Ensure `baksmali.jar` is accessible, noting its path for the script.

## Usage

Run the script from the command line as follows:

```bash
python deodexer.py --baksmali-jar /path/to/baksmali.jar \
                   --framework-dir /path/to/framework/dir \
                   --input-dir /path/to/input/dir \
                   --output-dir /path/to/output/dir \
                   --api-level 17 \
                   --max-workers 4
```

### Command-Line Arguments

- **--baksmali-jar** (required): Path to `baksmali.jar`.
- **--framework-dir** (required): Directory containing framework files (e.g., `/system/framework`).
- **--input-dir** (required): Directory containing `.odex` files to deodex.
- **--output-dir**: Directory for saving deodexed files (default: `output` in the current directory).
- **--api-level**: API level to use for deodexing (default: `17`).
- **--max-workers**: Number of threads for parallel processing (default: `4`). Increase if your system supports it for faster processing.

### Example Command

```bash
python deodexer.py --baksmali-jar /usr/local/bin/baksmali.jar \
                   --framework-dir /system/framework \
                   --input-dir /system/app \
                   --output-dir ./deodexed_output \
                   --api-level 29 \
                   --max-workers 8
```

In this example:
- The `baksmali.jar` file is located at `/usr/local/bin/baksmali.jar`.
- The framework directory is `/system/framework`.
- `.odex` files are read from `/system/app`.
- Deodexed files are saved to `./deodexed_output`.
- API level for deodexing is set to `29`.
- Eight threads are used for parallel processing.

## Logging

The script provides detailed logging to aid tracking and debugging:

- **INFO**: Logs high-level operations, including each successful deodex operation.
- **DEBUG**: Provides command details and subprocess outputs, useful for troubleshooting.
- **ERROR**: Captures issues, such as failed operations or missing dependencies.

All logs are printed to the console.

## Troubleshooting

If you encounter issues:
1. Check that **Java** is installed (`java -version`).
2. Verify the **baksmali JAR** file path.
3. Confirm the **framework directory** contains necessary files for deodexing.

## License

This script is open-source and distributed under the MIT License. Feel free to modify and distribute it as per the terms of the license.
