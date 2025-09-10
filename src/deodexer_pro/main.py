"""
Main entry point for Deodexer Pro application
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from deodexer_pro.core.config import config
from deodexer_pro.core.logger import logger
from deodexer_pro.core.deodexer import DeodexerEngine
from deodexer_pro.database.manager import DatabaseManager


def create_arg_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Deodexer Pro - Advanced Android Deodexer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s gui                                    # Launch GUI interface
  %(prog)s cli --help                            # Show CLI help
  %(prog)s api --port 8080                       # Start API server
  %(prog)s batch --input /path/to/odex           # Batch process files
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Launch GUI interface')
    gui_parser.add_argument('--theme', choices=['light', 'dark'], help='GUI theme')
    
    # CLI command
    cli_parser = subparsers.add_parser('cli', help='Command line interface')
    cli_parser.add_argument('--baksmali-jar', required=True, help='Path to baksmali JAR')
    cli_parser.add_argument('--framework-dir', required=True, help='Framework directory')
    cli_parser.add_argument('--input-dir', required=True, help='Input directory with ODEX files')
    cli_parser.add_argument('--output-dir', default='output', help='Output directory')
    cli_parser.add_argument('--api-level', type=int, default=29, help='API level')
    cli_parser.add_argument('--max-workers', type=int, default=4, help='Maximum worker threads')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Start API server')
    api_parser.add_argument('--host', default='127.0.0.1', help='Server host')
    api_parser.add_argument('--port', type=int, default=8000, help='Server port')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch processing')
    batch_parser.add_argument('--config', help='Configuration file path')
    batch_parser.add_argument('--input', required=True, help='Input directory')
    batch_parser.add_argument('--output', default='batch_output', help='Output directory')
    
    return parser


async def run_cli_command(args) -> int:
    """Run CLI deodexing command"""
    try:
        logger.info("Starting CLI deodexing", 
                   input_dir=args.input_dir,
                   output_dir=args.output_dir)
        
        # Initialize engine
        engine = DeodexerEngine()
        
        # Set baksmali JAR
        if not engine.set_baksmali_jar(args.baksmali_jar):
            logger.error("Invalid baksmali JAR path")
            return 1
        
        # Validate inputs
        if not engine.file_validator.validate_framework_directory(args.framework_dir):
            logger.error("Invalid framework directory")
            return 1
        
        # Run batch deodexing
        results = await engine.deodex_batch_async(
            input_dir=args.input_dir,
            framework_dir=args.framework_dir,
            output_dir=args.output_dir,
            api_level=args.api_level,
            max_workers=args.max_workers,
            progress_callback=lambda progress: logger.info(
                "Progress", 
                completed=progress['completed'],
                total=progress['total']
            )
        )
        
        # Generate report
        report = engine.generate_report(results)
        report_file = engine.export_report(results, 'json')
        
        logger.info("CLI deodexing completed", 
                   total_files=report['summary']['total_files'],
                   successful=report['summary']['successful'],
                   failed=report['summary']['failed'],
                   report_file=report_file)
        
        return 0 if report['summary']['failed'] == 0 else 1
        
    except Exception as e:
        logger.error("CLI command failed", error=str(e))
        return 1


def run_gui_command(args) -> int:
    """Run GUI application"""
    try:
        # Import GUI modules here to avoid unnecessary imports for CLI usage
        from deodexer_pro.gui.main import DeodexerProGUI
        
        logger.info("Starting GUI application")
        
        # Apply theme if specified
        if args.theme:
            config.set('gui.theme', args.theme)
        
        # Create and run GUI
        app = DeodexerProGUI()
        app.run()
        
        return 0
        
    except Exception as e:
        logger.error("GUI startup failed", error=str(e))
        return 1


def run_api_command(args) -> int:
    """Run API server"""
    try:
        logger.info("Starting API server", host=args.host, port=args.port)
        
        # For now, just a placeholder
        print(f"API server would start on {args.host}:{args.port}")
        print("API server not yet implemented in this version")
        
        return 0
        
    except Exception as e:
        logger.error("API server failed", error=str(e))
        return 1


async def run_batch_command(args) -> int:
    """Run batch processing"""
    try:
        logger.info("Starting batch processing", input_dir=args.input)
        
        # Load configuration if provided
        if args.config:
            import yaml
            with open(args.config, 'r') as f:
                batch_config = yaml.safe_load(f)
            config.update(batch_config)
        
        # Initialize components
        engine = DeodexerEngine()
        db_manager = DatabaseManager()
        
        # Create job in database
        job = db_manager.create_job(
            job_name=f"Batch_{Path(args.input).name}",
            input_directory=args.input,
            output_directory=args.output,
            framework_directory=config.get('deodexing.framework_dir', ''),
            api_level=config.get('deodexing.default_api_level', 29),
            max_workers=config.get('deodexing.max_workers', 4)
        )
        
        logger.info("Batch job created", job_id=job.id)
        
        # For now, just show what would be processed
        print(f"Batch processing would process files from: {args.input}")
        print(f"Output would go to: {args.output}")
        print(f"Job ID: {job.id}")
        
        return 0
        
    except Exception as e:
        logger.error("Batch processing failed", error=str(e))
        return 1


def main():
    """Main entry point"""
    try:
        # Parse arguments
        parser = create_arg_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 1
        
        # Initialize configuration and logging
        logger.info("Deodexer Pro starting", 
                   version=config.get('app.version', '2.0.0'),
                   command=args.command)
        
        # Route to appropriate command handler
        if args.command == 'gui':
            return run_gui_command(args)
        elif args.command == 'cli':
            return asyncio.run(run_cli_command(args))
        elif args.command == 'api':
            return run_api_command(args)
        elif args.command == 'batch':
            return asyncio.run(run_batch_command(args))
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error("Application failed", error=str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())