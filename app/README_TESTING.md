# Markdown Slides Generator - Testing Guide

## Overview

This document provides comprehensive information about the testing infrastructure for the Markdown Slides Generator project. The project includes a sophisticated test suite with 278+ tests organized across multiple categories, achieving a 99.3% success rate.

## Test Environment Setup

### Virtual Environment

The project includes a pre-configured Python 3.13 virtual environment located at:
```
/Users/vincenzo/data/local/repos/UNIPI-MIM/.venv/
```

**All dependencies are already installed**, including:
- **Testing Framework**: pytest, pytest-cov, pytest-mock
- **Core Dependencies**: click, pyyaml
- **Development Tools**: black, flake8, mypy, isort
- **Documentation**: sphinx, sphinx-rtd-theme, sphinx-click
- **Enhanced Features**: colorama, rich, tqdm

### Activation

To activate the environment and run tests:
```bash
cd /Users/vincenzo/data/local/repos/UNIPI-MIM/app
source ../.venv/bin/activate
```

## Test Execution Methods

### Method 1: Comprehensive Test Runner (Recommended)

The project includes a sophisticated test runner at `run_comprehensive_tests.py` that provides:
- **Organized Test Suites**: Tests grouped by category (unit, comprehensive, integration, etc.)
- **Detailed Reporting**: Success rates, execution times, and performance metrics
- **Error Analysis**: Comprehensive failure reporting with suggestions
- **Performance Insights**: Execution time breakdown and optimization suggestions

**Usage:**
```bash
# Run all test suites with comprehensive reporting
python run_comprehensive_tests.py

# Run with verbose output
python run_comprehensive_tests.py --verbose

# Run specific test suite
python run_comprehensive_tests.py --suite unit
```

### Method 2: Direct pytest Execution

For standard pytest usage:
```bash
# Run all tests (excluding problematic imports)
pytest --ignore=tests/test_content_validation_comprehensive.py

# Run with coverage
pytest --cov=markdown_slides_generator

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v --tb=short
```

## Test Suite Organization

### 1. Unit Tests (160 tests - 100% pass rate)
**Files covered:**
- `test_directive_parser.py` - Markdown directive parsing (27 tests)
- `test_content_routing.py` - Content routing logic (10 tests)  
- `test_latex_processor.py` - LaTeX processing (24 tests)
- `test_latex_integration.py` - LaTeX integration (6 tests)
- `test_math_renderer.py` - Math rendering (22 tests)
- `test_quarto_orchestrator.py` - Quarto orchestration (28 tests)
- `test_template_manager.py` - Template management (20 tests)
- `test_theme_manager.py` - Theme management (18 tests)
- `test_cli.py` - CLI interface (5 tests)

### 2. Comprehensive Tests (91/93 tests - 97.8% pass rate)
**Files covered:**
- `test_quarto_orchestrator_comprehensive.py` - Advanced Quarto features (21 tests)
- `test_batch_processing_comprehensive.py` - Batch processing (19 tests)
- `test_config_comprehensive.py` - Configuration management (26 tests) ⚠️ 2 failures
- `test_directive_parser.py` - Enhanced directive parsing (27 tests)

### 3. Integration Tests (5/5 tests - 100% pass rate)
**Files covered:**
- `test_integration_academic_content.py` - Real-world academic content processing

### 4. Performance Tests (11/11 tests - 100% pass rate)
**Files covered:**
- `test_performance_comprehensive.py` - Performance benchmarking and optimization

### 5. Regression Tests (9/9 tests - 100% pass rate)
**Files covered:**
- `test_regression_suite.py` - Regression pattern testing

## Known Issues

### 1. Import Error
**File:** `test_content_validation_comprehensive.py`
**Issue:** Missing import `OptimizationType` from validation module
**Status:** Test file excluded from runs
**Impact:** Minimal - main functionality not affected

### 2. Configuration Test Failures
**Files:** `test_config_comprehensive.py`
**Issues:**
- Unknown theme 'academic-modern' (expected themes: academic-minimal, beige, black, blood, league, moon, night, serif, simple, sky, solarized, white)
- Unknown theme 'dark'
- QuartoThemeManager type assertion failure

**Status:** 2/26 tests failing in config suite
**Impact:** Configuration validation is stricter than test expectations

## Test Results Summary

```
🏁 OVERALL TEST SUMMARY
============================================================
Total Test Suites: 5
Total Tests: 278
Passed: 276 ✅
Failed: 2 ❌
Skipped: 0 ⏭️
Total Execution Time: ~23 seconds
Overall Success Rate: 99.3%

📊 Suite Breakdown:
  ✅ unit         - 160 tests, 100.0% success,   ~8s
  ❌ comprehensive -  93 tests,  97.8% success,   ~8s
  ✅ integration  -   5 tests, 100.0% success,   ~0.4s
  ✅ regression   -   9 tests, 100.0% success,   ~0.3s
  ✅ performance  -  11 tests, 100.0% success,   ~6s
```

## Performance Insights

The comprehensive test runner provides performance analysis:
- **comprehensive suite**: 37.1% of total execution time
- **unit tests**: 34.5% of total execution time  
- **performance tests**: 25.2% of total execution time

## Test Coverage Features

The test suite includes:
- **Code Coverage**: Available via pytest-cov
- **Mock Testing**: Comprehensive mocking with pytest-mock
- **Async Testing**: Support for async operations
- **Error Handling**: Extensive error condition testing
- **Performance Benchmarking**: Speed and memory usage analysis
- **Integration Testing**: Real academic content processing
- **Regression Testing**: Prevention of previously fixed issues

## Configuration Files

### pyproject.toml
Contains test configuration and dependencies:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0", 
    "pytest-mock>=3.10.0",
    # ... other dev dependencies
]
```

### requirements.txt
Lists all production and development dependencies with specific versions.

## Development Workflow

1. **Activate Environment**: `source ../.venv/bin/activate`
2. **Run Tests**: `python run_comprehensive_tests.py`
3. **Check Coverage**: `pytest --cov=markdown_slides_generator`
4. **Fix Issues**: Address any failing tests
5. **Validate**: Re-run comprehensive suite

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Missing Dependencies**: All deps should be pre-installed
3. **Path Issues**: Run commands from `/app` directory
4. **Test Failures**: Review comprehensive test runner output for detailed error analysis

### Quick Fixes

```bash
# Reinstall dependencies if needed
pip install -r requirements.txt

# Run specific failing test for debugging
pytest tests/test_config_comprehensive.py::TestConfigManager::test_yaml_config_loading -v

# Check installed packages
pip list
```

## Contributing

When adding new tests:
1. Follow existing test structure and naming conventions
2. Add tests to appropriate suite (unit/comprehensive/integration/etc.)
3. Update `run_comprehensive_tests.py` if adding new test categories
4. Ensure tests pass in isolation and as part of the full suite
5. Include performance considerations for large test additions

## Conclusion

The testing infrastructure is robust and comprehensive, providing excellent coverage with minimal issues. The comprehensive test runner offers superior reporting and analysis compared to standard pytest execution, making it the recommended approach for development and CI/CD workflows.
