
# Deodexer Pro - Advanced Android Deodexer

A comprehensive, modern Android deodexer application with GUI interface and advanced post-graduate level features.

## 🚀 Features

### Core Capabilities
- **Modern GUI Interface**: Built with tkinter featuring a professional dashboard, job management, and real-time monitoring
- **Advanced Deodexing Engine**: Asynchronous processing with optimization and performance monitoring
- **Database Integration**: SQLite-based job tracking, history, and analytics
- **Machine Learning Optimization**: Intelligent parameter optimization based on file characteristics and system load
- **Performance Monitoring**: Real-time system metrics and operation analytics
- **Comprehensive Logging**: Structured logging with multiple output formats

### Post-Graduate Level Features
- **Modular Architecture**: Clean separation of concerns with pluggable components
- **Configuration Management**: YAML-based configuration with environment variable overrides
- **File Analysis**: Advanced ODEX file validation and characteristic analysis
- **Batch Processing**: Concurrent processing with progress tracking and error handling
- **Export Capabilities**: Multiple export formats (JSON, CSV, PDF reports)
- **System Integration**: Cross-platform compatibility with system monitoring
- **Security Features**: Input validation, error handling, and secure file operations

## 📋 Requirements

- **Python**: 3.8 or higher
- **Java**: Required for baksmali execution
- **baksmali**: The baksmali JAR file for deodexing operations

### System Dependencies
```bash
# Core dependencies
pip install PyYAML sqlalchemy psutil numpy matplotlib

# Optional dependencies for full functionality
pip install structlog rich flask fastapi
```

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/WiredTourqe/Deodexer-Script
   cd Deodexer-Script
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

## 🎯 Usage

### GUI Application
Launch the modern GUI interface:
```bash
python -m src.deodexer_pro.main gui

# With dark theme
python -m src.deodexer_pro.main gui --theme dark
```

### Command Line Interface
For direct command-line usage:
```bash
python -m src.deodexer_pro.main cli \
    --baksmali-jar /path/to/baksmali.jar \
    --framework-dir /system/framework \
    --input-dir /system/app \
    --output-dir ./output \
    --api-level 29 \
    --max-workers 8
```

### Batch Processing
For automated batch processing:
```bash
python -m src.deodexer_pro.main batch \
    --input /path/to/odex/files \
    --output ./batch_output \
    --config config/production.yaml
```

### API Server (Coming Soon)
Start the REST API server:
```bash
python -m src.deodexer_pro.main api --port 8080
```

## 📁 Project Structure

```
Deodexer-Script/
├── src/deodexer_pro/           # Main application package
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── logger.py          # Logging system
│   │   └── deodexer.py        # Main deodexing engine
│   ├── database/              # Database models and management
│   │   ├── models.py          # SQLAlchemy models
│   │   └── manager.py         # Database operations
│   ├── gui/                   # GUI components
│   │   ├── main.py            # Main GUI application
│   │   └── components/        # UI components
│   ├── utils/                 # Utility modules
│   │   ├── file_utils.py      # File operations
│   │   └── performance.py     # Performance monitoring
│   ├── ml/                    # Machine learning components
│   │   └── optimizer.py       # ML optimization
│   └── main.py                # Application entry point
├── config/                    # Configuration files
├── tests/                     # Test suite
├── docs/                      # Documentation
└── data/                      # Data directory
```

## 🎨 GUI Features

### Dashboard
- **System Statistics**: Real-time overview of jobs, success rates, and performance
- **Performance Charts**: Visual analytics of system metrics and job completion
- **Activity Log**: Recent operations and their status

### Job Manager
- **Job Creation**: Easy setup of deodexing jobs with parameter validation
- **Progress Tracking**: Real-time progress monitoring with detailed status
- **History Management**: Complete job history with search and filtering

### Settings
- **Configuration Management**: GUI-based configuration editing
- **Theme Selection**: Light and dark theme support
- **Performance Tuning**: Optimization parameter adjustment

## 🔧 Configuration

Configuration is managed through YAML files with environment variable overrides:

```yaml
# config/default.yaml
app:
  name: "Deodexer Pro"
  version: "2.0.0"
  debug: false

deodexing:
  default_api_level: 29
  max_workers: 8
  timeout: 300

gui:
  theme: "dark"
  window:
    width: 1200
    height: 800

database:
  type: "sqlite"
  path: "data/deodexer_pro.db"
```

Environment variables can override any configuration:
```bash
export DEODEXER_API_LEVEL=30
export DEODEXER_MAX_WORKERS=16
export DEODEXER_LOG_LEVEL=DEBUG
```

## 📊 Performance Features

### Machine Learning Optimization
- **Automatic Parameter Tuning**: ML-based optimization of deodexing parameters
- **System Load Adaptation**: Dynamic adjustment based on system resources
- **Learning from Results**: Continuous improvement from operation feedback

### Monitoring and Analytics
- **Real-time Metrics**: CPU, memory, and disk usage monitoring
- **Operation Tracking**: Detailed timing and throughput analysis
- **Performance Reports**: Comprehensive analytics and export capabilities

## 🧪 Testing

Run the test suite:
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# All tests with coverage
python -m pytest tests/ --cov=src/deodexer_pro
```

## 📖 Documentation

- **User Guide**: [docs/user/README.md](docs/user/README.md)
- **Developer Guide**: [docs/developer/README.md](docs/developer/README.md)
- **API Documentation**: [docs/api/README.md](docs/api/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

### Upcoming Features
- [ ] REST API implementation
- [ ] Plugin architecture
- [ ] Advanced ML models
- [ ] Web-based interface
- [ ] Cloud integration
- [ ] Advanced security features
- [ ] Multi-language support

### Version 2.1.0 (Planned)
- Enhanced ML optimization algorithms
- Plugin system for extensibility
- Advanced reporting and analytics
- Performance optimizations

### Version 3.0.0 (Future)
- Web-based interface
- Cloud processing capabilities
- Advanced security features
- Enterprise features

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/WiredTourqe/Deodexer-Script/issues)
- **Discussions**: [GitHub Discussions](https://github.com/WiredTourqe/Deodexer-Script/discussions)
- **Documentation**: [Project Wiki](https://github.com/WiredTourqe/Deodexer-Script/wiki)

## 🙏 Acknowledgments

- [JesusFreke](https://github.com/JesusFreke) for the baksmali tool
- The Android development community
- Contributors and testers

---

**Deodexer Pro** - Transforming Android deodexing with modern technology and post-graduate level sophistication.
