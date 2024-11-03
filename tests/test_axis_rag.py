import unittest
import sys
import os
from pathlib import Path
import time
import json
from unittest.runner import TextTestRunner
from unittest.suite import TestSuite
import tkinter as tk
from tkinter import ttk, scrolledtext
from queue import Queue
import threading

class TestAxisRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test environment and load API keys from config"""
        try:
            # Load API keys from config file
            config_path = Path("config/api_keys.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    os.environ["OPENAI_API_KEY"] = config.get("OPENAI_API_KEY", "")
                    os.environ["ANTHROPIC_API_KEY"] = config.get("ANTHROPIC_API_KEY", "")
            
            cls.test_pdf = "notebooks/data/Axis Program Management_Unformatted detailed.pdf"
            cls.output_dir = Path("notebooks/output")
            cls.message_queue = Queue()
            print("Test environment setup completed")
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            raise

    def setUp(self):
        """Setup for each test"""
        self.output_dir.mkdir(exist_ok=True)

    def test_dependencies(self):
        """Test if required packages are installed"""
        required_packages = ["openai", "anthropic", "chromadb", "streamlit"]
        for package in required_packages:
            try:
                __import__(package)
                print(f"Package {package} is installed")
            except ImportError:
                self.fail(f"Required package {package} is not installed")
        print("Dependencies test passed")

class TestOutputGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Axis RAG Test Runner")
        self.root.geometry("1000x700")
        self.message_queue = Queue()
        self.reports_dir = Path("notebooks/tests/reports")
        self.setup_gui()
        
    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Left panel for test output
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Right panel for reports
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        main_frame.grid_columnconfigure(0, weight=2)  # Test output gets more space
        main_frame.grid_columnconfigure(1, weight=1)  # Reports panel
        
        # Test Output Section
        self.setup_test_output(left_panel)
        
        # Reports Section
        self.setup_reports_panel(right_panel)
        
    def setup_test_output(self, parent):
        # Header
        self.header_var = tk.StringVar(value="Running Axis RAG Tests")
        self.header = ttk.Label(
            parent, 
            textvariable=self.header_var,
            font=('Arial', 14, 'bold')
        )
        self.header.grid(row=0, column=0, pady=10)
        
        # Console output
        self.console = scrolledtext.ScrolledText(parent, height=20, width=80)
        self.console.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # Progress frame
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame, 
            mode='indeterminate', 
            length=300
        )
        self.progress.grid(row=0, column=0, sticky="ew")
        
        # Status label
        self.status_var = tk.StringVar(value="Initializing tests...")
        self.status_label = ttk.Label(
            progress_frame, 
            textvariable=self.status_var,
            font=('Arial', 10)
        )
        self.status_label.grid(row=1, column=0, pady=5)
        
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def setup_reports_panel(self, parent):
        # Reports Header
        ttk.Label(
            parent,
            text="Test Reports",
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, pady=10)
        
        # Reports List
        self.reports_frame = ttk.Frame(parent)
        self.reports_frame.grid(row=1, column=0, sticky="nsew")
        
        # Refresh button
        ttk.Button(
            parent,
            text="↻ Refresh Reports",
            command=self.refresh_reports
        ).grid(row=2, column=0, pady=10)
        
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        self.refresh_reports()
        
    def refresh_reports(self):
        # Clear existing reports
        for widget in self.reports_frame.winfo_children():
            widget.destroy()
            
        # List all report files
        reports = sorted(
            self.reports_dir.glob("test_report_*.txt"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Create scrollable frame for reports
        canvas = tk.Canvas(self.reports_frame)
        scrollbar = ttk.Scrollbar(self.reports_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add report entries
        for i, report in enumerate(reports):
            report_frame = ttk.Frame(scrollable_frame)
            report_frame.grid(row=i, column=0, pady=2, sticky="ew")
            
            timestamp = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(report.stat().st_mtime)
            )
            
            ttk.Label(
                report_frame,
                text=f"Report {timestamp}"
            ).grid(row=0, column=0, padx=5)
            
            ttk.Button(
                report_frame,
                text="View",
                command=lambda r=report: self.view_report(r)
            ).grid(row=0, column=1, padx=5)
            
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.reports_frame.grid_rowconfigure(0, weight=1)
        self.reports_frame.grid_columnconfigure(0, weight=1)
        
    def view_report(self, report_path):
        """Open report in a new window"""
        report_window = tk.Toplevel(self.root)
        report_window.title(f"Test Report - {report_path.name}")
        report_window.geometry("800x600")
        
        # Report content
        report_text = scrolledtext.ScrolledText(
            report_window,
            wrap=tk.WORD,
            font=('Courier', 10)
        )
        report_text.pack(expand=True, fill="both", padx=10, pady=10)
        
        with open(report_path) as f:
            report_text.insert(tk.END, f.read())
        
        report_text.configure(state='disabled')  # Make read-only

class GUITestRunner(TextTestRunner):
    def __init__(self, gui_output, **kwargs):
        super().__init__(**kwargs)
        self.gui_output = gui_output
        
    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        result.gui_output = self.gui_output
        startTime = time.time()
        
        self.gui_output.write('Running tests...\n')
        try:
            test(result)
        finally:
            stopTime = time.time()
            
        timeTaken = stopTime - startTime
        result.printErrors()
        
        self.gui_output.write(f"\nRan {result.testsRun} tests in {timeTaken:.3f}s\n")
        
        expectedFails = len(result.expectedFailures)
        unexpectedSuccesses = len(result.unexpectedSuccesses)
        skipped = len(result.skipped)
        
        infos = []
        if skipped:
            infos.append(f"skipped={skipped}")
        if expectedFails:
            infos.append(f"expected failures={expectedFails}")
        if unexpectedSuccesses:
            infos.append(f"unexpected successes={unexpectedSuccesses}")
            
        if result.wasSuccessful():
            self.gui_output.write("OK")
            if infos:
                self.gui_output.write(f" ({', '.join(infos)})")
            self.gui_output.write("\n")
        else:
            self.gui_output.write("FAILED")
            self.gui_output.write(f" (failures={len(result.failures)}, ")
            self.gui_output.write(f"errors={len(result.errors)})")
            if infos:
                self.gui_output.write(f" ({', '.join(infos)})")
            self.gui_output.write("\n")
            
        return result

def run_tests():
    """Run all tests with GUI output"""
    gui_output = TestOutputGUI()
    
    # Create test suite
    suite = TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAxisRAG))
    
    # Create output directory
    output_dir = Path("notebooks/tests/reports")
    output_dir.mkdir(exist_ok=True)
    
    # Run tests with both GUI and file output
    output_file = output_dir / f"test_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    
    def run_test_suite():
        with open(output_file, 'w') as f:
            runner = GUITestRunner(
                gui_output,
                stream=f,
                verbosity=2
            )
            result = runner.run(suite)
            
            summary = f"\nTest Results:\n"
            summary += f"Ran {result.testsRun} tests\n"
            summary += f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}\n"
            summary += f"Failures: {len(result.failures)}\n"
            summary += f"Errors: {len(result.errors)}\n"
            
            gui_output.write(summary)
            f.write(summary)
            
            gui_output.progress.stop()
            gui_output.update_status("Testing completed")
            
            return result
    
    # Run tests in a separate thread
    test_thread = threading.Thread(target=run_test_suite)
    test_thread.start()
    
    # Start GUI main loop
    gui_output.root.mainloop()

if __name__ == '__main__':
    run_tests() 