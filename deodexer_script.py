import os
import subprocess
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging with DEBUG level for more information
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def check_java_installed():
    """
    Ensure that Java is installed and available in the system's PATH.
    """
    try:
        subprocess.run(["java", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("Java is not installed or not available in your system PATH. Please install Java and try again.")
        exit(1)

def deodex_file(baksmali_jar, framework_dir, api_level, odex_file_path, output_dir):
    """
    Deodex a single .odex file using baksmali.
    """
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Construct output path for the specific .odex file
        output_file_path = os.path.join(output_dir, os.path.basename(odex_file_path).replace(".odex", ""))

        # Build the command to run baksmali
        command = [
            "java", "-jar", baksmali_jar,
            "deodex",
            "-a", str(api_level),  # API level option
            "-d", framework_dir,  # Framework directory
            "-o", output_file_path,  # Output directory for the deodexed file
            odex_file_path  # Single .odex file
        ]

        # Log the command for debugging purposes
        logging.debug(f"Running command: {' '.join(command)}")

        # Run the command and capture the output
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Output the result for debugging
        logging.info(f"Successfully deodexed: {odex_file_path}")
        logging.debug(f"Command output: {result.stdout.decode('utf-8')}")
        logging.debug(f"Command errors (if any): {result.stderr.decode('utf-8')}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error deodexing {odex_file_path}: {e.stderr.decode('utf-8')}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

def deodex_all_files(baksmali_jar, framework_dir, api_level, directory, output_dir, max_workers=4):
    """
    Recursively find all .odex files in a directory and deodex them using parallel processing.
    """
    # Collect all .odex files
    odex_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".odex"):
                odex_files.append(os.path.join(root, file))

    # Deodex files using a thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(deodex_file, baksmali_jar, framework_dir, api_level, odex_file, os.path.join(output_dir, os.path.relpath(os.path.dirname(odex_file), directory)))
            for odex_file in odex_files
        ]

        for future in as_completed(futures):
            try:
                future.result()  # To catch any exceptions that were raised
            except Exception as e:
                logging.error(f"Exception in deodexing task: {str(e)}")

def main():
    # Command-line arguments parsing
    parser = argparse.ArgumentParser(description="Deodex .odex files using baksmali.")
    parser.add_argument("--baksmali-jar", required=True, help="Path to baksmali JAR file.")
    parser.add_argument("--framework-dir", required=True, help="Directory containing framework files for bootclasspath.")
    parser.add_argument("--input-dir", required=True, help="Input directory containing .odex files.")
    parser.add_argument("--output-dir", default="output", help="Output directory for deodexed files.")
    parser.add_argument("--api-level", type=int, default=17, help="API level for deodexing (default: 17).")
    parser.add_argument("--max-workers", type=int, default=4, help="Number of worker threads for parallel processing.")
    args = parser.parse_args()

    # Check environment requirements
    check_java_installed()

    # Ensure the output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Deodex files
    logging.info(f"Deodexing .odex files from {args.input_dir} to {args.output_dir} with API level {args.api_level}...")
    deodex_all_files(args.baksmali_jar, args.framework_dir, args.api_level, args.input_dir, args.output_dir, args.max_workers)
    logging.info("Deodexing completed.")

if __name__ == "__main__":
    main()
