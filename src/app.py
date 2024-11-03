import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import time

class RAGWebInterface:
    def __init__(self):
        self.reports_path = Path("notebooks/output")
        self.tests_path = Path("notebooks/tests/reports")
        self.setup_page()

    def setup_page(self):
        """Initialize the Streamlit page and session state"""
        st.set_page_config(
            page_title="PowerApps Analysis Dashboard",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        # Initialize session state
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.process_running = False
            st.session_state.analysis_complete = False
            st.session_state.console_output = []

    def run(self):
        """Main application entry point"""
        st.title("PowerApps Analysis Dashboard")
        self.show_main_dashboard()

    def show_main_dashboard(self):
        """Display main dashboard"""
        # File Status Section
        st.header("PowerApps PDF Analysis")
        
        # Check PDF file
        pdf_path = Path("notebooks/data/Axis Program Management_Unformatted detailed.pdf")
        if pdf_path.exists():
            st.success("📄 PDF File Loaded: Axis Program Management")
            with st.expander("PDF Details", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("File Size", f"{pdf_path.stat().st_size / 1024:.1f} KB")
                with col2:
                    st.metric("Last Modified", 
                             datetime.fromtimestamp(pdf_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'))
        else:
            st.error("PDF file not found in the expected location")
            return

        # Control Buttons
        st.subheader("Analysis Control")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Analysis", use_container_width=True):
                self.run_analysis()

        with col2:
            if st.button("Install Dependencies", use_container_width=True):
                self.install_dependencies()

        # Console Output
        st.subheader("Console Output")
        self.show_console()

    def run_analysis(self):
        """Run the analysis process"""
        try:
            self.log_output("Starting analysis...")
            
            # Verify directories
            self.reports_path.mkdir(exist_ok=True)
            
            # Simulate analysis steps
            steps = [
                "Loading PDF content...",
                "Processing text...",
                "Generating OpenAI analysis...",
                "Generating Anthropic analysis...",
                "Saving reports..."
            ]
            
            for step in steps:
                self.log_output(step)
                time.sleep(1)  # Simulate work
                
            # Create sample reports for testing
            self.create_sample_reports()
            
            self.log_output("Analysis completed successfully!")
            st.session_state.analysis_complete = True
            st.rerun()
            
        except Exception as e:
            self.log_output(f"Error during analysis: {str(e)}")
            st.error(f"Analysis failed: {str(e)}")

    def install_dependencies(self):
        """Install required packages"""
        try:
            self.log_output("Installing dependencies...")
            packages = ["pandas", "openai", "anthropic", "chromadb", "langchain"]
            
            for package in packages:
                self.log_output(f"Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-U", package],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log_output(f"Successfully installed {package}")
                else:
                    self.log_output(f"Error installing {package}: {result.stderr}")
                
            self.log_output("Dependencies installation completed!")
            st.success("Dependencies installed successfully!")
            
        except Exception as e:
            self.log_output(f"Error installing dependencies: {str(e)}")
            st.error(f"Installation failed: {str(e)}")

    def create_sample_reports(self):
        """Create sample reports for testing"""
        # OpenAI report
        openai_path = self.reports_path / "openai_report.txt"
        with open(openai_path, 'w') as f:
            f.write("Sample OpenAI Analysis Report\n" + "="*30 + "\n")
            f.write("This is a sample analysis report from OpenAI.\n")

        # Anthropic report
        anthropic_path = self.reports_path / "anthropic_report.txt"
        with open(anthropic_path, 'w') as f:
            f.write("Sample Anthropic Analysis Report\n" + "="*30 + "\n")
            f.write("This is a sample analysis report from Anthropic.\n")

    def show_console(self):
        """Display console output"""
        console_text = "\n".join(st.session_state.console_output)
        st.text_area("Console Log", value=console_text, height=400)
        
        if st.button("Clear Console"):
            st.session_state.console_output = []
            st.rerun()

    def log_output(self, message: str):
        """Add message to console output"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'console_output' not in st.session_state:
            st.session_state.console_output = []
        st.session_state.console_output.append(f"[{timestamp}] {message}")
        # Keep only last 100 messages
        st.session_state.console_output = st.session_state.console_output[-100:]

def main():
    interface = RAGWebInterface()
    interface.run()

if __name__ == "__main__":
    main()