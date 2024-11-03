import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import sys
import os
from datetime import datetime

class AxisRAGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Axis RAG Analysis Tool")
        self.root.geometry("800x600")
        
        # Configure grid weight for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Initialize process tracking
        self.current_process = None
        self.is_running = False
        self.animation_index = 0
        self.animation_frames = ["⋮", "⋰", "⋯", "⋱"]  # Loading animation frames
        self.animation_id = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with grid weights for resizing
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(2, weight=1)  # Make console expand
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="Axis RAG Analysis Tool", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        buttons_frame.grid_columnconfigure(3, weight=1)
        buttons_frame.grid_columnconfigure(4, weight=1)
        
        # Action Buttons
        ttk.Button(buttons_frame, text="Run Full Analysis", 
                  command=self.run_analysis, style='Action.TButton').grid(
                      row=0, column=0, padx=5, sticky="ew")
        
        ttk.Button(buttons_frame, text="Launch Web Interface", 
                  command=self.launch_interface, style='Action.TButton').grid(
                      row=0, column=1, padx=5, sticky="ew")
        
        ttk.Button(buttons_frame, text="Run Analysis + Launch Interface", 
                  command=self.run_both, style='Action.TButton').grid(
                      row=0, column=2, padx=5, sticky="ew")
        
        ttk.Button(buttons_frame, text="Install/Update Dependencies", 
                  command=self.install_deps, style='Action.TButton').grid(
                      row=0, column=3, padx=5, sticky="ew")
        
        # Add Tests Button (before Force Stop button)
        ttk.Button(buttons_frame, text="Run Tests", 
                  command=self.run_tests, style='Action.TButton').grid(
                      row=0, column=4, padx=5, sticky="ew")
        
        # Force Stop Button (moved to column 5)
        self.stop_button = ttk.Button(buttons_frame, text="Force Stop", 
                                    command=self.force_stop, style='Stop.TButton')
        self.stop_button.grid(row=0, column=5, padx=5, sticky="ew")
        self.stop_button['state'] = 'disabled'
        
        # Style for Stop Button
        style = ttk.Style()
        style.configure('Stop.TButton', foreground='red', padding=10, font=('Arial', 10))
        
        # Console Frame (expandable)
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="5")
        console_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)
        
        # Console (expandable)
        self.console = scrolledtext.ScrolledText(console_frame, height=20)
        self.console.grid(row=0, column=0, sticky="nsew")
        
        # Status Bar with animation
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky="ew", pady=(5,0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Add progress indicator and status label
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            font=('Arial', 10)
        )
        self.status_label.grid(row=0, column=0, sticky="w")

    def animate_status(self):
        """Animate the status text while process is running"""
        if self.is_running:
            self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
            current_frame = self.animation_frames[self.animation_index]
            self.status_var.set(f"Running {current_frame}")
            self.animation_id = self.root.after(300, self.animate_status)  # Update every 300ms

    def stop_animation(self):
        """Stop the status animation"""
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

    def run_command(self, command, success_message):
        """Run a command and handle its output"""
        try:
            self.is_running = True
            self.stop_button['state'] = 'normal'
            self.animate_status()  # Start animation
            
            self.current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            
            # Read output in real-time
            while self.is_running:
                output = self.current_process.stdout.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                if output:
                    self.log_output(output.strip())
            
            # Check for errors
            if self.current_process.returncode == 0:
                self.log_output(success_message)
            else:
                error = self.current_process.stderr.read()
                self.log_output(f"Error: {error}")
                
        except Exception as e:
            self.log_output(f"Error: {str(e)}")
        finally:
            self.is_running = False
            self.stop_button['state'] = 'disabled'
            self.stop_animation()  # Stop animation
            self.status_var.set("Ready")
            self.current_process = None

    def log_output(self, message):
        """Add timestamped message to console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        
    def run_in_thread(self, command, success_message):
        """Run command in separate thread to keep GUI responsive"""
        thread = threading.Thread(
            target=self.run_command,
            args=(command, success_message)
        )
        thread.daemon = True
        thread.start()
        
    def run_analysis(self):
        self.log_output("Starting analysis...")
        command = 'python notebooks/AxisRAG.py --pdf_path "notebooks/data/Axis Program Management_Unformatted detailed.pdf"'
        self.run_in_thread(command, "Analysis completed successfully")
        
    def launch_interface(self):
        self.log_output("Launching web interface...")
        command = "streamlit run notebooks/app.py"
        self.run_in_thread(command, "Web interface launched successfully")
        
    def run_both(self):
        self.log_output("Running analysis and launching interface...")
        self.run_analysis()
        self.root.after(5000, self.launch_interface)  # Launch interface after 5 seconds
        
    def install_deps(self):
        """Install or update required dependencies"""
        self.log_output("Installing dependencies...")
        command = "pip install streamlit plotly pandas openai anthropic chromadb langchain"
        self.run_in_thread(command, "Dependencies installed successfully")

    def force_stop(self):
        """Force stop all running processes"""
        if self.current_process:
            try:
                self.is_running = False
                self.stop_animation()  # Stop animation
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.current_process.pid)])
                else:
                    self.current_process.kill()
                self.log_output("Process forcefully stopped")
                self.stop_button['state'] = 'disabled'
                self.status_var.set("Ready")
            except Exception as e:
                self.log_output(f"Error stopping process: {str(e)}")

    def run_tests(self):
        """Launch the test GUI"""
        self.log_output("Launching test suite...")
        subprocess.Popen([sys.executable, "notebooks/tests/test_axis_rag.py"])

def main():
    root = tk.Tk()
    app = AxisRAGGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 