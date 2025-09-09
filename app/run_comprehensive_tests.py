#!/usr/bin/env python3
"""
Comprehensive test runner for markdown slides generator.

Runs all test suites with detailed reporting and performance metrics.
"""

import sys
import time
import subprocess
from pathlib import Path
import argparse
from typing import List, Dict, Any


class TestRunner:
    """Comprehensive test runner with reporting."""
    
    def __init__(self):
        self.test_suites = {
            'unit': [
                'tests/test_directive_parser.py',
                'tests/test_content_routing.py',
                'tests/test_latex_processor.py',
                'tests/test_latex_integration.py',
                'tests/test_math_renderer.py',
                'tests/test_quarto_orchestrator.py',
                'tests/test_template_manager.py',
                'tests/test_theme_manager.py',
                'tests/test_cli.py'
            ],
            'comprehensive': [
                'tests/test_quarto_orchestrator_comprehensive.py',
                'tests/test_batch_processing_comprehensive.py',
                'tests/test_config_comprehensive.py',
                'tests/test_directive_parser.py'  # Enhanced version
            ],
            'performance': [
                'tests/test_performance_comprehensive.py'
            ],
            'integration': [
                'tests/test_integration_academic_content.py'
            ],
            'regression': [
                'tests/test_regression_suite.py'
            ]
        }
        
        self.results = {}
    
    def run_test_suite(self, suite_name: str, test_files: List[str], verbose: bool = False) -> Dict[str, Any]:
        """Run a test suite and return results."""
        print(f"\n{'='*60}")
        print(f"Running {suite_name.upper()} Test Suite")
        print(f"{'='*60}")
        
        suite_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'execution_time': 0,
            'files': {}
        }
        
        suite_start_time = time.time()
        
        for test_file in test_files:
            print(f"\nRunning {test_file}...")
            
            # Build pytest command
            cmd = [
                sys.executable, '-m', 'pytest',
                test_file,
                '-v' if verbose else '-q',
                '--tb=short',
                '--durations=10',
                '--strict-markers'
            ]
            
            # Add coverage for unit tests (if pytest-cov is available)
            if suite_name == 'unit':
                try:
                    import pytest_cov
                    cmd.extend([
                        '--cov=markdown_slides_generator',
                        '--cov-report=term-missing'
                    ])
                except ImportError:
                    # Skip coverage if pytest-cov is not installed
                    pass
            
            file_start_time = time.time()
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per file
                )
                
                file_execution_time = time.time() - file_start_time
                
                # Parse pytest output
                output_lines = result.stdout.split('\n')
                
                # Extract test counts
                summary_line = None
                for line in reversed(output_lines):
                    if 'passed' in line or 'failed' in line or 'error' in line:
                        summary_line = line
                        break
                
                file_results = self._parse_pytest_output(summary_line, result.returncode)
                file_results['execution_time'] = file_execution_time
                file_results['stdout'] = result.stdout
                file_results['stderr'] = result.stderr
                
                suite_results['files'][test_file] = file_results
                suite_results['total_tests'] += file_results['total_tests']
                suite_results['passed'] += file_results['passed']
                suite_results['failed'] += file_results['failed']
                suite_results['skipped'] += file_results['skipped']
                
                if file_results['failed'] > 0 or result.returncode != 0:
                    suite_results['errors'].append({
                        'file': test_file,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode
                    })
                
                # Print summary for this file
                status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
                print(f"  {status} - {file_results['total_tests']} tests in {file_execution_time:.2f}s")
                
                if verbose and result.returncode != 0:
                    print(f"  Error output: {result.stderr}")
                
            except subprocess.TimeoutExpired:
                print(f"  ⏰ TIMEOUT - Test file exceeded 5 minute limit")
                suite_results['errors'].append({
                    'file': test_file,
                    'error': 'Timeout after 5 minutes',
                    'returncode': -1
                })
            
            except Exception as e:
                print(f"  💥 ERROR - {str(e)}")
                suite_results['errors'].append({
                    'file': test_file,
                    'error': str(e),
                    'returncode': -1
                })
        
        suite_results['execution_time'] = time.time() - suite_start_time
        
        # Print suite summary
        print(f"\n{suite_name.upper()} Suite Summary:")
        print(f"  Total Tests: {suite_results['total_tests']}")
        print(f"  Passed: {suite_results['passed']} ✅")
        print(f"  Failed: {suite_results['failed']} ❌")
        print(f"  Skipped: {suite_results['skipped']} ⏭️")
        print(f"  Execution Time: {suite_results['execution_time']:.2f}s")
        print(f"  Success Rate: {(suite_results['passed'] / max(suite_results['total_tests'], 1)) * 100:.1f}%")
        
        return suite_results
    
    def _parse_pytest_output(self, summary_line: str, return_code: int) -> Dict[str, Any]:
        """Parse pytest output to extract test counts."""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        if not summary_line:
            return results
        
        # Parse different pytest output formats
        import re
        
        # Look for patterns like "5 passed", "2 failed", "1 skipped"
        passed_match = re.search(r'(\d+) passed', summary_line)
        failed_match = re.search(r'(\d+) failed', summary_line)
        skipped_match = re.search(r'(\d+) skipped', summary_line)
        error_match = re.search(r'(\d+) error', summary_line)
        
        if passed_match:
            results['passed'] = int(passed_match.group(1))
        
        if failed_match:
            results['failed'] = int(failed_match.group(1))
        
        if skipped_match:
            results['skipped'] = int(skipped_match.group(1))
        
        if error_match:
            results['failed'] += int(error_match.group(1))
        
        results['total_tests'] = results['passed'] + results['failed'] + results['skipped']
        
        return results
    
    def run_all_suites(self, suites: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """Run all or specified test suites."""
        if suites is None:
            suites = list(self.test_suites.keys())
        
        print("🧪 Markdown Slides Generator - Comprehensive Test Suite")
        print("=" * 60)
        
        overall_start_time = time.time()
        overall_results = {
            'suites': {},
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'total_skipped': 0,
            'total_execution_time': 0,
            'success_rate': 0
        }
        
        for suite_name in suites:
            if suite_name not in self.test_suites:
                print(f"⚠️  Unknown test suite: {suite_name}")
                continue
            
            suite_results = self.run_test_suite(
                suite_name, 
                self.test_suites[suite_name], 
                verbose
            )
            
            overall_results['suites'][suite_name] = suite_results
            overall_results['total_tests'] += suite_results['total_tests']
            overall_results['total_passed'] += suite_results['passed']
            overall_results['total_failed'] += suite_results['failed']
            overall_results['total_skipped'] += suite_results['skipped']
        
        overall_results['total_execution_time'] = time.time() - overall_start_time
        
        if overall_results['total_tests'] > 0:
            overall_results['success_rate'] = (
                overall_results['total_passed'] / overall_results['total_tests']
            ) * 100
        
        # Print overall summary
        self._print_overall_summary(overall_results)
        
        return overall_results
    
    def _print_overall_summary(self, results: Dict[str, Any]):
        """Print overall test summary."""
        print(f"\n{'='*60}")
        print("🏁 OVERALL TEST SUMMARY")
        print(f"{'='*60}")
        
        print(f"Total Test Suites: {len(results['suites'])}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['total_passed']} ✅")
        print(f"Failed: {results['total_failed']} ❌")
        print(f"Skipped: {results['total_skipped']} ⏭️")
        print(f"Total Execution Time: {results['total_execution_time']:.2f}s")
        print(f"Overall Success Rate: {results['success_rate']:.1f}%")
        
        # Suite breakdown
        print(f"\n📊 Suite Breakdown:")
        for suite_name, suite_results in results['suites'].items():
            status = "✅" if suite_results['failed'] == 0 else "❌"
            success_rate = (suite_results['passed'] / max(suite_results['total_tests'], 1)) * 100
            print(f"  {status} {suite_name:12} - {suite_results['total_tests']:3} tests, "
                  f"{success_rate:5.1f}% success, {suite_results['execution_time']:6.2f}s")
        
        # Error summary
        if results['total_failed'] > 0:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for suite_name, suite_results in results['suites'].items():
                if suite_results['errors']:
                    print(f"\n  {suite_name.upper()} Suite Errors:")
                    for error in suite_results['errors']:
                        print(f"    - {error['file']}")
                        if 'error' in error:
                            print(f"      Error: {error['error']}")
        
        # Performance insights
        print(f"\n⚡ Performance Insights:")
        slowest_suites = sorted(
            results['suites'].items(),
            key=lambda x: x[1]['execution_time'],
            reverse=True
        )[:3]
        
        for suite_name, suite_results in slowest_suites:
            print(f"  {suite_name:12} - {suite_results['execution_time']:6.2f}s "
                  f"({suite_results['execution_time']/results['total_execution_time']*100:4.1f}% of total)")
        
        # Final verdict
        if results['total_failed'] == 0:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"\n⚠️  {results['total_failed']} TESTS FAILED")
            print("   Please review the errors above and fix the issues.")
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None):
        """Generate detailed test report."""
        if output_file is None:
            output_file = f"test_report_{int(time.time())}.md"
        
        report_content = f"""# Markdown Slides Generator - Test Report

**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Test Suites:** {len(results['suites'])}
- **Total Tests:** {results['total_tests']}
- **Passed:** {results['total_passed']} ✅
- **Failed:** {results['total_failed']} ❌
- **Skipped:** {results['total_skipped']} ⏭️
- **Success Rate:** {results['success_rate']:.1f}%
- **Total Execution Time:** {results['total_execution_time']:.2f}s

## Suite Details

"""
        
        for suite_name, suite_results in results['suites'].items():
            success_rate = (suite_results['passed'] / max(suite_results['total_tests'], 1)) * 100
            status = "✅ PASSED" if suite_results['failed'] == 0 else "❌ FAILED"
            
            report_content += f"""### {suite_name.title()} Suite {status}

- **Tests:** {suite_results['total_tests']}
- **Passed:** {suite_results['passed']}
- **Failed:** {suite_results['failed']}
- **Skipped:** {suite_results['skipped']}
- **Success Rate:** {success_rate:.1f}%
- **Execution Time:** {suite_results['execution_time']:.2f}s

"""
            
            if suite_results['errors']:
                report_content += "#### Errors:\n\n"
                for error in suite_results['errors']:
                    report_content += f"- **{error['file']}**\n"
                    if 'error' in error:
                        report_content += f"  - Error: `{error['error']}`\n"
                    report_content += "\n"
        
        # Write report
        Path(output_file).write_text(report_content)
        print(f"\n📄 Detailed report saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run comprehensive tests for markdown slides generator')
    parser.add_argument(
        '--suites', 
        nargs='+', 
        choices=['unit', 'comprehensive', 'performance', 'integration', 'regression', 'all'],
        default=['all'],
        help='Test suites to run'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--report', '-r',
        type=str,
        help='Generate detailed report to specified file'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Skip performance tests for faster execution'
    )
    
    args = parser.parse_args()
    
    # Handle 'all' suite selection
    if 'all' in args.suites:
        suites = ['unit', 'comprehensive', 'integration', 'regression']
        if not args.fast:
            suites.append('performance')
    else:
        suites = args.suites
    
    # Run tests
    runner = TestRunner()
    results = runner.run_all_suites(suites, args.verbose)
    
    # Generate report if requested
    if args.report:
        runner.generate_report(results, args.report)
    
    # Exit with appropriate code
    exit_code = 0 if results['total_failed'] == 0 else 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()