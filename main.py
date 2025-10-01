"""
FFmpeg GUI - Main Application
Supports video conversion, editing, audio extraction and more
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
import json
from pathlib import Path

class FFmpegGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg GUI - Complete Edition")
        self.root.geometry("1200x800")

        # Config file path
        self.config_file = Path("config.json")
        self.load_config()

        # Current processing task
        self.current_process = None
        self.is_processing = False

        # Create main UI
        self.create_menu()
        self.create_main_ui()

        # Check FFmpeg
        self.check_ffmpeg()

    def load_config(self):
        """Load configuration file"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'ffmpeg_path': 'ffmpeg',
                'last_input_dir': '',
                'last_output_dir': '',
                'default_format': 'mp4',
                'default_codec': 'libx264'
            }
            self.save_config()

    def save_config(self):
        """Save configuration file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Set FFmpeg Path", command=self.set_ffmpeg_path)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="FFmpeg Command Help", command=self.show_ffmpeg_help)

    def create_main_ui(self):
        """Create main UI"""
        # Create notebook tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Function tabs (placeholders for now)
        self.create_convert_tab()
        self.create_edit_tab()
        self.create_audio_extract_tab()
        self.create_batch_tab()
        self.create_advanced_tab()

        # Bottom status bar and log
        self.create_bottom_panel()

    def create_convert_tab(self):
        """Basic conversion tab"""
        self.convert_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.convert_frame, text="Format Conversion")

        # Main container with scrollbar
        main_container = ttk.Frame(self.convert_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Input file section
        input_frame = ttk.LabelFrame(main_container, text="Input File", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.convert_input_entry = ttk.Entry(input_frame, width=70)
        self.convert_input_entry.pack(side='left', fill='x', expand=True, padx=5)

        ttk.Button(input_frame, text="Browse",
                  command=self.browse_convert_input).pack(side='left', padx=5)

        # Output settings section
        output_frame = ttk.LabelFrame(main_container, text="Output Settings", padding=10)
        output_frame.pack(fill='x', pady=5)

        # Output path
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill='x', pady=5)
        ttk.Label(path_frame, text="Output:").pack(side='left', padx=5)
        self.convert_output_entry = ttk.Entry(path_frame, width=60)
        self.convert_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(path_frame, text="Browse",
                  command=self.browse_convert_output).pack(side='left', padx=5)

        # Format selection
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill='x', pady=5)
        ttk.Label(format_frame, text="Format:").pack(side='left', padx=5)
        self.convert_format_var = tk.StringVar(value="mp4")
        formats = ["mp4", "avi", "mkv", "mov", "flv", "webm", "wmv", "m4v", "3gp", "mpg", "mpeg"]
        ttk.Combobox(format_frame, textvariable=self.convert_format_var,
                    values=formats, width=15, state='readonly').pack(side='left', padx=5)

        # Video codec
        vcodec_frame = ttk.Frame(output_frame)
        vcodec_frame.pack(fill='x', pady=5)
        ttk.Label(vcodec_frame, text="Video Codec:").pack(side='left', padx=5)
        self.convert_vcodec_var = tk.StringVar(value="libx264")
        vcodecs = ["copy", "libx264", "libx265", "libvpx-vp9", "libaom-av1", "mpeg4", "libxvid"]
        ttk.Combobox(vcodec_frame, textvariable=self.convert_vcodec_var,
                    values=vcodecs, width=15, state='readonly').pack(side='left', padx=5)

        ttk.Label(vcodec_frame, text="  Audio Codec:").pack(side='left', padx=5)
        self.convert_acodec_var = tk.StringVar(value="aac")
        acodecs = ["copy", "aac", "mp3", "libmp3lame", "libopus", "libvorbis", "ac3", "flac"]
        ttk.Combobox(vcodec_frame, textvariable=self.convert_acodec_var,
                    values=acodecs, width=15, state='readonly').pack(side='left', padx=5)

        # Quality settings
        quality_frame = ttk.LabelFrame(main_container, text="Quality Settings", padding=10)
        quality_frame.pack(fill='x', pady=5)

        # Preset
        preset_frame = ttk.Frame(quality_frame)
        preset_frame.pack(fill='x', pady=5)
        ttk.Label(preset_frame, text="Preset:").pack(side='left', padx=5)
        self.convert_preset_var = tk.StringVar(value="medium")
        presets = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
        ttk.Combobox(preset_frame, textvariable=self.convert_preset_var,
                    values=presets, width=15, state='readonly').pack(side='left', padx=5)

        # CRF (quality)
        crf_frame = ttk.Frame(quality_frame)
        crf_frame.pack(fill='x', pady=5)
        ttk.Label(crf_frame, text="CRF (Quality):").pack(side='left', padx=5)
        self.convert_crf_var = tk.StringVar(value="23")
        ttk.Spinbox(crf_frame, from_=0, to=51, textvariable=self.convert_crf_var,
                   width=10).pack(side='left', padx=5)
        ttk.Label(crf_frame, text="(0=best, 51=worst, 23=default)").pack(side='left', padx=5)

        # Bitrate
        bitrate_frame = ttk.Frame(quality_frame)
        bitrate_frame.pack(fill='x', pady=5)
        ttk.Label(bitrate_frame, text="Video Bitrate:").pack(side='left', padx=5)
        self.convert_vbitrate_var = tk.StringVar(value="")
        ttk.Entry(bitrate_frame, textvariable=self.convert_vbitrate_var,
                 width=15).pack(side='left', padx=5)
        ttk.Label(bitrate_frame, text="(e.g., 2M, 5000k)").pack(side='left', padx=5)

        # Resolution
        resolution_frame = ttk.LabelFrame(main_container, text="Resolution", padding=10)
        resolution_frame.pack(fill='x', pady=5)

        res_controls = ttk.Frame(resolution_frame)
        res_controls.pack(fill='x', pady=5)

        self.convert_resize_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(res_controls, text="Resize",
                       variable=self.convert_resize_var).pack(side='left', padx=5)

        self.convert_resolution_var = tk.StringVar(value="1920x1080")
        resolutions = ["3840x2160", "2560x1440", "1920x1080", "1280x720", "854x480", "640x360", "Custom"]
        ttk.Combobox(res_controls, textvariable=self.convert_resolution_var,
                    values=resolutions, width=15, state='readonly').pack(side='left', padx=5)

        # Custom resolution
        custom_res_frame = ttk.Frame(resolution_frame)
        custom_res_frame.pack(fill='x', pady=5)
        ttk.Label(custom_res_frame, text="Custom Width:").pack(side='left', padx=5)
        self.convert_width_var = tk.StringVar(value="")
        ttk.Entry(custom_res_frame, textvariable=self.convert_width_var,
                 width=10).pack(side='left', padx=5)
        ttk.Label(custom_res_frame, text="Height:").pack(side='left', padx=5)
        self.convert_height_var = tk.StringVar(value="")
        ttk.Entry(custom_res_frame, textvariable=self.convert_height_var,
                 width=10).pack(side='left', padx=5)
        ttk.Label(custom_res_frame, text="(leave empty to keep aspect ratio)").pack(side='left', padx=5)

        # FPS
        fps_frame = ttk.Frame(resolution_frame)
        fps_frame.pack(fill='x', pady=5)
        self.convert_fps_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fps_frame, text="Change FPS:",
                       variable=self.convert_fps_var).pack(side='left', padx=5)
        self.convert_fps_value_var = tk.StringVar(value="30")
        ttk.Spinbox(fps_frame, from_=1, to=120, textvariable=self.convert_fps_value_var,
                   width=10).pack(side='left', padx=5)

        # Advanced options
        advanced_frame = ttk.LabelFrame(main_container, text="Advanced Options", padding=10)
        advanced_frame.pack(fill='x', pady=5)

        adv_controls = ttk.Frame(advanced_frame)
        adv_controls.pack(fill='x', pady=5)

        self.convert_2pass_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_controls, text="2-Pass Encoding",
                       variable=self.convert_2pass_var).pack(side='left', padx=5)

        self.convert_hw_accel_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_controls, text="Hardware Acceleration",
                       variable=self.convert_hw_accel_var).pack(side='left', padx=5)

        # Custom FFmpeg arguments
        custom_frame = ttk.Frame(advanced_frame)
        custom_frame.pack(fill='x', pady=5)
        ttk.Label(custom_frame, text="Custom Args:").pack(side='left', padx=5)
        self.convert_custom_args_var = tk.StringVar(value="")
        ttk.Entry(custom_frame, textvariable=self.convert_custom_args_var,
                 width=60).pack(side='left', fill='x', expand=True, padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Start Conversion",
                  command=self.start_conversion).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Command",
                  command=self.show_convert_command).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Preview Input",
                  command=lambda: self.preview_video(self.convert_input_entry.get())).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_process).pack(side='left', padx=5)

    def create_edit_tab(self):
        """Video editing tab"""
        self.edit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_frame, text="Video Editing")

        # Create sub-tabs for different editing functions
        edit_notebook = ttk.Notebook(self.edit_frame)
        edit_notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Trim/Cut tab
        self.create_trim_tab(edit_notebook)

        # Merge/Concatenate tab
        self.create_merge_tab(edit_notebook)

        # Filters tab
        self.create_filter_tab(edit_notebook)

    def create_trim_tab(self, parent):
        """Create trim/cut video tab"""
        trim_frame = ttk.Frame(parent)
        parent.add(trim_frame, text="Trim/Cut")

        main_container = ttk.Frame(trim_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Input file
        input_frame = ttk.LabelFrame(main_container, text="Input File", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.trim_input_entry = ttk.Entry(input_frame, width=70)
        self.trim_input_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(input_frame, text="Browse",
                  command=self.browse_trim_input).pack(side='left', padx=5)

        # Trim settings
        trim_settings = ttk.LabelFrame(main_container, text="Trim Settings", padding=10)
        trim_settings.pack(fill='x', pady=5)

        # Start time
        start_frame = ttk.Frame(trim_settings)
        start_frame.pack(fill='x', pady=5)
        ttk.Label(start_frame, text="Start Time (HH:MM:SS):").pack(side='left', padx=5)
        self.trim_start_var = tk.StringVar(value="00:00:00")
        ttk.Entry(start_frame, textvariable=self.trim_start_var,
                 width=15).pack(side='left', padx=5)

        # End time or duration
        self.trim_mode_var = tk.StringVar(value="duration")
        ttk.Radiobutton(start_frame, text="Duration",
                       variable=self.trim_mode_var,
                       value="duration").pack(side='left', padx=10)
        ttk.Radiobutton(start_frame, text="End Time",
                       variable=self.trim_mode_var,
                       value="end").pack(side='left', padx=5)

        # Duration
        duration_frame = ttk.Frame(trim_settings)
        duration_frame.pack(fill='x', pady=5)
        ttk.Label(duration_frame, text="Duration (HH:MM:SS):").pack(side='left', padx=5)
        self.trim_duration_var = tk.StringVar(value="00:00:10")
        ttk.Entry(duration_frame, textvariable=self.trim_duration_var,
                 width=15).pack(side='left', padx=5)

        # End time
        end_frame = ttk.Frame(trim_settings)
        end_frame.pack(fill='x', pady=5)
        ttk.Label(end_frame, text="End Time (HH:MM:SS):").pack(side='left', padx=5)
        self.trim_end_var = tk.StringVar(value="00:00:10")
        ttk.Entry(end_frame, textvariable=self.trim_end_var,
                 width=15).pack(side='left', padx=5)

        # Re-encode option
        reencode_frame = ttk.Frame(trim_settings)
        reencode_frame.pack(fill='x', pady=5)
        self.trim_reencode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(reencode_frame, text="Re-encode (slower but more accurate)",
                       variable=self.trim_reencode_var).pack(side='left', padx=5)

        # Output file
        output_frame = ttk.LabelFrame(main_container, text="Output File", padding=10)
        output_frame.pack(fill='x', pady=5)

        self.trim_output_entry = ttk.Entry(output_frame, width=70)
        self.trim_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(output_frame, text="Browse",
                  command=self.browse_trim_output).pack(side='left', padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Trim Video",
                  command=self.start_trim).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Command",
                  command=self.show_trim_command).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_process).pack(side='left', padx=5)

    def create_merge_tab(self, parent):
        """Create merge/concatenate videos tab"""
        merge_frame = ttk.Frame(parent)
        parent.add(merge_frame, text="Merge")

        main_container = ttk.Frame(merge_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # File list
        list_frame = ttk.LabelFrame(main_container, text="Video Files (will be merged in order)", padding=10)
        list_frame.pack(fill='both', expand=True, pady=5)

        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side='right', fill='y')

        self.merge_listbox = tk.Listbox(list_container, height=10,
                                        yscrollcommand=scrollbar.set)
        self.merge_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.merge_listbox.yview)

        # List control buttons
        list_buttons = ttk.Frame(list_frame)
        list_buttons.pack(fill='x', pady=5)

        ttk.Button(list_buttons, text="Add Files",
                  command=self.add_merge_files).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Remove Selected",
                  command=self.remove_merge_file).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Clear All",
                  command=self.clear_merge_files).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Move Up",
                  command=self.move_merge_up).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Move Down",
                  command=self.move_merge_down).pack(side='left', padx=5)

        # Merge options
        options_frame = ttk.LabelFrame(main_container, text="Merge Options", padding=10)
        options_frame.pack(fill='x', pady=5)

        self.merge_reencode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Re-encode (required if videos have different formats/resolutions)",
                       variable=self.merge_reencode_var).pack(side='left', padx=5)

        # Output file
        output_frame = ttk.LabelFrame(main_container, text="Output File", padding=10)
        output_frame.pack(fill='x', pady=5)

        self.merge_output_entry = ttk.Entry(output_frame, width=70)
        self.merge_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(output_frame, text="Browse",
                  command=self.browse_merge_output).pack(side='left', padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Merge Videos",
                  command=self.start_merge).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Command",
                  command=self.show_merge_command).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_process).pack(side='left', padx=5)

        # Store file list
        self.merge_files = []

    def create_filter_tab(self, parent):
        """Create video filters tab"""
        filter_frame = ttk.Frame(parent)
        parent.add(filter_frame, text="Filters")

        main_container = ttk.Frame(filter_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Input file
        input_frame = ttk.LabelFrame(main_container, text="Input File", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.filter_input_entry = ttk.Entry(input_frame, width=70)
        self.filter_input_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(input_frame, text="Browse",
                  command=self.browse_filter_input).pack(side='left', padx=5)

        # Filters
        filters_frame = ttk.LabelFrame(main_container, text="Available Filters", padding=10)
        filters_frame.pack(fill='both', expand=True, pady=5)

        # Rotation/Flip
        rotation_frame = ttk.LabelFrame(filters_frame, text="Rotation & Flip", padding=5)
        rotation_frame.pack(fill='x', pady=5)

        rot_controls = ttk.Frame(rotation_frame)
        rot_controls.pack(fill='x')

        self.filter_rotate_var = tk.StringVar(value="none")
        ttk.Radiobutton(rot_controls, text="None", variable=self.filter_rotate_var,
                       value="none").pack(side='left', padx=5)
        ttk.Radiobutton(rot_controls, text="90° CW", variable=self.filter_rotate_var,
                       value="90").pack(side='left', padx=5)
        ttk.Radiobutton(rot_controls, text="90° CCW", variable=self.filter_rotate_var,
                       value="270").pack(side='left', padx=5)
        ttk.Radiobutton(rot_controls, text="180°", variable=self.filter_rotate_var,
                       value="180").pack(side='left', padx=5)

        flip_controls = ttk.Frame(rotation_frame)
        flip_controls.pack(fill='x', pady=5)

        self.filter_hflip_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(flip_controls, text="Flip Horizontal",
                       variable=self.filter_hflip_var).pack(side='left', padx=5)

        self.filter_vflip_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(flip_controls, text="Flip Vertical",
                       variable=self.filter_vflip_var).pack(side='left', padx=5)

        # Speed adjustment
        speed_frame = ttk.LabelFrame(filters_frame, text="Speed Adjustment", padding=5)
        speed_frame.pack(fill='x', pady=5)

        speed_controls = ttk.Frame(speed_frame)
        speed_controls.pack(fill='x')

        ttk.Label(speed_controls, text="Speed Multiplier:").pack(side='left', padx=5)
        self.filter_speed_var = tk.StringVar(value="1.0")
        ttk.Spinbox(speed_controls, from_=0.25, to=4.0, increment=0.25,
                   textvariable=self.filter_speed_var, width=10).pack(side='left', padx=5)
        ttk.Label(speed_controls, text="(0.5=half speed, 2.0=double speed)").pack(side='left', padx=5)

        # Brightness/Contrast
        brightness_frame = ttk.LabelFrame(filters_frame, text="Brightness & Contrast", padding=5)
        brightness_frame.pack(fill='x', pady=5)

        bright_controls = ttk.Frame(brightness_frame)
        bright_controls.pack(fill='x')

        ttk.Label(bright_controls, text="Brightness:").pack(side='left', padx=5)
        self.filter_brightness_var = tk.StringVar(value="0")
        ttk.Spinbox(bright_controls, from_=-1.0, to=1.0, increment=0.1,
                   textvariable=self.filter_brightness_var, width=10).pack(side='left', padx=5)

        ttk.Label(bright_controls, text="Contrast:").pack(side='left', padx=10)
        self.filter_contrast_var = tk.StringVar(value="1.0")
        ttk.Spinbox(bright_controls, from_=0, to=3.0, increment=0.1,
                   textvariable=self.filter_contrast_var, width=10).pack(side='left', padx=5)

        # Saturation
        sat_controls = ttk.Frame(brightness_frame)
        sat_controls.pack(fill='x', pady=5)

        ttk.Label(sat_controls, text="Saturation:").pack(side='left', padx=5)
        self.filter_saturation_var = tk.StringVar(value="1.0")
        ttk.Spinbox(sat_controls, from_=0, to=3.0, increment=0.1,
                   textvariable=self.filter_saturation_var, width=10).pack(side='left', padx=5)

        # Blur/Sharpen
        blur_frame = ttk.LabelFrame(filters_frame, text="Blur & Sharpen", padding=5)
        blur_frame.pack(fill='x', pady=5)

        blur_controls = ttk.Frame(blur_frame)
        blur_controls.pack(fill='x')

        self.filter_blur_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(blur_controls, text="Apply Blur (radius):",
                       variable=self.filter_blur_var).pack(side='left', padx=5)
        self.filter_blur_radius_var = tk.StringVar(value="5")
        ttk.Spinbox(blur_controls, from_=1, to=20, increment=1,
                   textvariable=self.filter_blur_radius_var, width=10).pack(side='left', padx=5)

        # Output file
        output_frame = ttk.LabelFrame(main_container, text="Output File", padding=10)
        output_frame.pack(fill='x', pady=5)

        self.filter_output_entry = ttk.Entry(output_frame, width=70)
        self.filter_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(output_frame, text="Browse",
                  command=self.browse_filter_output).pack(side='left', padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Apply Filters",
                  command=self.start_filter).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Command",
                  command=self.show_filter_command).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_process).pack(side='left', padx=5)

    def create_audio_extract_tab(self):
        """Audio extraction tab"""
        self.audio_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_frame, text="Audio Extraction")

        main_container = ttk.Frame(self.audio_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Input file section
        input_frame = ttk.LabelFrame(main_container, text="Input Video File", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.audio_input_entry = ttk.Entry(input_frame, width=70)
        self.audio_input_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(input_frame, text="Browse",
                  command=self.browse_audio_input).pack(side='left', padx=5)

        # Audio settings
        settings_frame = ttk.LabelFrame(main_container, text="Audio Settings", padding=10)
        settings_frame.pack(fill='x', pady=5)

        # Output format
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill='x', pady=5)
        ttk.Label(format_frame, text="Output Format:").pack(side='left', padx=5)
        self.audio_format_var = tk.StringVar(value="mp3")
        formats = ["mp3", "aac", "wav", "flac", "ogg", "m4a", "wma", "opus", "ac3"]
        ttk.Combobox(format_frame, textvariable=self.audio_format_var,
                    values=formats, width=15, state='readonly').pack(side='left', padx=5)

        # Audio codec
        codec_frame = ttk.Frame(settings_frame)
        codec_frame.pack(fill='x', pady=5)
        ttk.Label(codec_frame, text="Audio Codec:").pack(side='left', padx=5)
        self.audio_codec_var = tk.StringVar(value="auto")
        codecs = ["auto", "copy", "libmp3lame", "aac", "libopus", "libvorbis", "flac", "pcm_s16le", "ac3"]
        ttk.Combobox(codec_frame, textvariable=self.audio_codec_var,
                    values=codecs, width=15, state='readonly').pack(side='left', padx=5)
        ttk.Label(codec_frame, text="(auto = best for format)").pack(side='left', padx=5)

        # Bitrate
        bitrate_frame = ttk.Frame(settings_frame)
        bitrate_frame.pack(fill='x', pady=5)
        ttk.Label(bitrate_frame, text="Bitrate:").pack(side='left', padx=5)
        self.audio_bitrate_var = tk.StringVar(value="192k")
        bitrates = ["64k", "96k", "128k", "160k", "192k", "256k", "320k"]
        ttk.Combobox(bitrate_frame, textvariable=self.audio_bitrate_var,
                    values=bitrates, width=15).pack(side='left', padx=5)

        # Sample rate
        sample_frame = ttk.Frame(settings_frame)
        sample_frame.pack(fill='x', pady=5)
        ttk.Label(sample_frame, text="Sample Rate:").pack(side='left', padx=5)
        self.audio_sample_var = tk.StringVar(value="44100")
        samples = ["22050", "44100", "48000", "96000"]
        ttk.Combobox(sample_frame, textvariable=self.audio_sample_var,
                    values=samples, width=15, state='readonly').pack(side='left', padx=5)
        ttk.Label(sample_frame, text="Hz").pack(side='left', padx=5)

        # Channels
        channel_frame = ttk.Frame(settings_frame)
        channel_frame.pack(fill='x', pady=5)
        ttk.Label(channel_frame, text="Channels:").pack(side='left', padx=5)
        self.audio_channels_var = tk.StringVar(value="stereo")
        ttk.Radiobutton(channel_frame, text="Mono", variable=self.audio_channels_var,
                       value="mono").pack(side='left', padx=5)
        ttk.Radiobutton(channel_frame, text="Stereo", variable=self.audio_channels_var,
                       value="stereo").pack(side='left', padx=5)

        # Volume adjustment
        volume_frame = ttk.LabelFrame(main_container, text="Volume Adjustment", padding=10)
        volume_frame.pack(fill='x', pady=5)

        vol_controls = ttk.Frame(volume_frame)
        vol_controls.pack(fill='x', pady=5)

        self.audio_volume_enable_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(vol_controls, text="Adjust Volume:",
                       variable=self.audio_volume_enable_var).pack(side='left', padx=5)

        self.audio_volume_var = tk.StringVar(value="1.0")
        ttk.Scale(vol_controls, from_=0.0, to=2.0, orient='horizontal',
                 variable=self.audio_volume_var, length=200).pack(side='left', padx=5)

        self.audio_volume_label = ttk.Label(vol_controls, text="1.0x")
        self.audio_volume_label.pack(side='left', padx=5)

        # Update label when scale changes
        def update_volume_label(*args):
            val = float(self.audio_volume_var.get())
            self.audio_volume_label.config(text=f"{val:.2f}x")

        self.audio_volume_var.trace_add('write', update_volume_label)

        # Trim audio section
        trim_frame = ttk.LabelFrame(main_container, text="Trim Audio (Optional)", padding=10)
        trim_frame.pack(fill='x', pady=5)

        trim_controls = ttk.Frame(trim_frame)
        trim_controls.pack(fill='x', pady=5)

        self.audio_trim_enable_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(trim_controls, text="Enable Trim",
                       variable=self.audio_trim_enable_var).pack(side='left', padx=5)

        ttk.Label(trim_controls, text="Start:").pack(side='left', padx=5)
        self.audio_trim_start_var = tk.StringVar(value="00:00:00")
        ttk.Entry(trim_controls, textvariable=self.audio_trim_start_var,
                 width=12).pack(side='left', padx=5)

        ttk.Label(trim_controls, text="Duration:").pack(side='left', padx=5)
        self.audio_trim_duration_var = tk.StringVar(value="00:00:30")
        ttk.Entry(trim_controls, textvariable=self.audio_trim_duration_var,
                 width=12).pack(side='left', padx=5)

        # Fade effects
        fade_frame = ttk.LabelFrame(main_container, text="Fade Effects (Optional)", padding=10)
        fade_frame.pack(fill='x', pady=5)

        fade_controls = ttk.Frame(fade_frame)
        fade_controls.pack(fill='x', pady=5)

        self.audio_fadein_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fade_controls, text="Fade In:",
                       variable=self.audio_fadein_var).pack(side='left', padx=5)
        self.audio_fadein_duration_var = tk.StringVar(value="3")
        ttk.Spinbox(fade_controls, from_=0, to=10, increment=0.5,
                   textvariable=self.audio_fadein_duration_var, width=8).pack(side='left', padx=5)
        ttk.Label(fade_controls, text="sec").pack(side='left', padx=5)

        self.audio_fadeout_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fade_controls, text="Fade Out:",
                       variable=self.audio_fadeout_var).pack(side='left', padx=10)
        self.audio_fadeout_duration_var = tk.StringVar(value="3")
        ttk.Spinbox(fade_controls, from_=0, to=10, increment=0.5,
                   textvariable=self.audio_fadeout_duration_var, width=8).pack(side='left', padx=5)
        ttk.Label(fade_controls, text="sec").pack(side='left', padx=5)

        # Output file
        output_frame = ttk.LabelFrame(main_container, text="Output Audio File", padding=10)
        output_frame.pack(fill='x', pady=5)

        self.audio_output_entry = ttk.Entry(output_frame, width=70)
        self.audio_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(output_frame, text="Browse",
                  command=self.browse_audio_output).pack(side='left', padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Extract Audio",
                  command=self.start_audio_extract).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Command",
                  command=self.show_audio_command).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_process).pack(side='left', padx=5)

    def create_batch_tab(self):
        """Batch processing tab"""
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="Batch Processing")

        main_container = ttk.Frame(self.batch_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # File list section
        list_frame = ttk.LabelFrame(main_container, text="Input Files", padding=10)
        list_frame.pack(fill='both', expand=True, pady=5)

        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side='right', fill='y')

        self.batch_listbox = tk.Listbox(list_container, height=12,
                                        yscrollcommand=scrollbar.set)
        self.batch_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.batch_listbox.yview)

        # List control buttons
        list_buttons = ttk.Frame(list_frame)
        list_buttons.pack(fill='x', pady=5)

        ttk.Button(list_buttons, text="Add Files",
                  command=self.add_batch_files).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Add Folder",
                  command=self.add_batch_folder).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Remove Selected",
                  command=self.remove_batch_file).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Clear All",
                  command=self.clear_batch_files).pack(side='left', padx=5)

        # Operation type
        operation_frame = ttk.LabelFrame(main_container, text="Batch Operation", padding=10)
        operation_frame.pack(fill='x', pady=5)

        op_controls = ttk.Frame(operation_frame)
        op_controls.pack(fill='x', pady=5)

        ttk.Label(op_controls, text="Operation:").pack(side='left', padx=5)
        self.batch_operation_var = tk.StringVar(value="convert")
        operations = [
            ("Format Conversion", "convert"),
            ("Audio Extraction", "audio"),
            ("Resize Video", "resize"),
            ("Apply Filter", "filter")
        ]
        for text, value in operations:
            ttk.Radiobutton(op_controls, text=text,
                           variable=self.batch_operation_var,
                           value=value,
                           command=self.update_batch_options).pack(side='left', padx=5)

        # Options container (will change based on operation)
        self.batch_options_frame = ttk.LabelFrame(main_container, text="Options", padding=10)
        self.batch_options_frame.pack(fill='x', pady=5)

        # Create option frames for each operation type
        self.create_batch_convert_options()
        self.create_batch_audio_options()
        self.create_batch_resize_options()
        self.create_batch_filter_options()

        # Show default options
        self.update_batch_options()

        # Output settings
        output_frame = ttk.LabelFrame(main_container, text="Output Settings", padding=10)
        output_frame.pack(fill='x', pady=5)

        out_controls = ttk.Frame(output_frame)
        out_controls.pack(fill='x', pady=5)

        ttk.Label(out_controls, text="Output Folder:").pack(side='left', padx=5)
        self.batch_output_entry = ttk.Entry(out_controls, width=50)
        self.batch_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(out_controls, text="Browse",
                  command=self.browse_batch_output).pack(side='left', padx=5)

        # Filename pattern
        pattern_frame = ttk.Frame(output_frame)
        pattern_frame.pack(fill='x', pady=5)
        ttk.Label(pattern_frame, text="Filename Pattern:").pack(side='left', padx=5)
        self.batch_pattern_var = tk.StringVar(value="{name}_converted{ext}")
        ttk.Entry(pattern_frame, textvariable=self.batch_pattern_var,
                 width=30).pack(side='left', padx=5)
        ttk.Label(pattern_frame, text="({name}=original name, {ext}=extension)").pack(side='left', padx=5)

        # Progress section
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding=10)
        progress_frame.pack(fill='x', pady=5)

        self.batch_progress_label = ttk.Label(progress_frame, text="Ready")
        self.batch_progress_label.pack(pady=5)

        self.batch_progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.batch_progress_bar.pack(fill='x', pady=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Start Batch Processing",
                  command=self.start_batch_processing).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_batch_processing).pack(side='left', padx=5)

        # Store batch file list
        self.batch_files = []
        self.batch_processing = False

    def create_batch_convert_options(self):
        """Create options for batch conversion"""
        self.batch_convert_frame = ttk.Frame(self.batch_options_frame)

        ttk.Label(self.batch_convert_frame, text="Output Format:").pack(side='left', padx=5)
        self.batch_convert_format_var = tk.StringVar(value="mp4")
        formats = ["mp4", "avi", "mkv", "mov", "webm"]
        ttk.Combobox(self.batch_convert_frame, textvariable=self.batch_convert_format_var,
                    values=formats, width=10, state='readonly').pack(side='left', padx=5)

        ttk.Label(self.batch_convert_frame, text="Codec:").pack(side='left', padx=10)
        self.batch_convert_codec_var = tk.StringVar(value="libx264")
        codecs = ["libx264", "libx265", "copy"]
        ttk.Combobox(self.batch_convert_frame, textvariable=self.batch_convert_codec_var,
                    values=codecs, width=10, state='readonly').pack(side='left', padx=5)

        ttk.Label(self.batch_convert_frame, text="CRF:").pack(side='left', padx=10)
        self.batch_convert_crf_var = tk.StringVar(value="23")
        ttk.Spinbox(self.batch_convert_frame, from_=0, to=51,
                   textvariable=self.batch_convert_crf_var, width=8).pack(side='left', padx=5)

    def create_batch_audio_options(self):
        """Create options for batch audio extraction"""
        self.batch_audio_frame = ttk.Frame(self.batch_options_frame)

        ttk.Label(self.batch_audio_frame, text="Audio Format:").pack(side='left', padx=5)
        self.batch_audio_format_var = tk.StringVar(value="mp3")
        formats = ["mp3", "aac", "wav", "flac"]
        ttk.Combobox(self.batch_audio_frame, textvariable=self.batch_audio_format_var,
                    values=formats, width=10, state='readonly').pack(side='left', padx=5)

        ttk.Label(self.batch_audio_frame, text="Bitrate:").pack(side='left', padx=10)
        self.batch_audio_bitrate_var = tk.StringVar(value="192k")
        bitrates = ["128k", "192k", "256k", "320k"]
        ttk.Combobox(self.batch_audio_frame, textvariable=self.batch_audio_bitrate_var,
                    values=bitrates, width=10).pack(side='left', padx=5)

    def create_batch_resize_options(self):
        """Create options for batch resize"""
        self.batch_resize_frame = ttk.Frame(self.batch_options_frame)

        ttk.Label(self.batch_resize_frame, text="Resolution:").pack(side='left', padx=5)
        self.batch_resize_resolution_var = tk.StringVar(value="1920x1080")
        resolutions = ["3840x2160", "2560x1440", "1920x1080", "1280x720", "854x480"]
        ttk.Combobox(self.batch_resize_frame, textvariable=self.batch_resize_resolution_var,
                    values=resolutions, width=12, state='readonly').pack(side='left', padx=5)

    def create_batch_filter_options(self):
        """Create options for batch filter"""
        self.batch_filter_frame = ttk.Frame(self.batch_options_frame)

        ttk.Label(self.batch_filter_frame, text="Filter:").pack(side='left', padx=5)
        self.batch_filter_type_var = tk.StringVar(value="none")
        filters = ["none", "grayscale", "blur", "sharpen"]
        ttk.Combobox(self.batch_filter_frame, textvariable=self.batch_filter_type_var,
                    values=filters, width=12, state='readonly').pack(side='left', padx=5)

    def update_batch_options(self):
        """Update visible batch options based on operation type"""
        # Hide all option frames
        for frame in [self.batch_convert_frame, self.batch_audio_frame,
                     self.batch_resize_frame, self.batch_filter_frame]:
            frame.pack_forget()

        # Show appropriate frame
        operation = self.batch_operation_var.get()
        if operation == "convert":
            self.batch_convert_frame.pack(fill='x', pady=5)
        elif operation == "audio":
            self.batch_audio_frame.pack(fill='x', pady=5)
        elif operation == "resize":
            self.batch_resize_frame.pack(fill='x', pady=5)
        elif operation == "filter":
            self.batch_filter_frame.pack(fill='x', pady=5)

    def create_advanced_tab(self):
        """Advanced features tab"""
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text="Advanced")

        # Create sub-tabs for different advanced functions
        advanced_notebook = ttk.Notebook(self.advanced_frame)
        advanced_notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Subtitle tab
        self.create_subtitle_tab(advanced_notebook)

        # Watermark tab
        self.create_watermark_tab(advanced_notebook)

        # Video info tab
        self.create_video_info_tab(advanced_notebook)

    def create_subtitle_tab(self, parent):
        """Create subtitle embedding tab"""
        subtitle_frame = ttk.Frame(parent)
        parent.add(subtitle_frame, text="Subtitles")

        main_container = ttk.Frame(subtitle_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Input video
        input_frame = ttk.LabelFrame(main_container, text="Input Video", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.subtitle_input_entry = ttk.Entry(input_frame, width=70)
        self.subtitle_input_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(input_frame, text="Browse",
                  command=self.browse_subtitle_input).pack(side='left', padx=5)

        # Subtitle file
        subtitle_file_frame = ttk.LabelFrame(main_container, text="Subtitle File", padding=10)
        subtitle_file_frame.pack(fill='x', pady=5)

        self.subtitle_file_entry = ttk.Entry(subtitle_file_frame, width=70)
        self.subtitle_file_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(subtitle_file_frame, text="Browse",
                  command=self.browse_subtitle_file).pack(side='left', padx=5)

        # Subtitle options
        options_frame = ttk.LabelFrame(main_container, text="Subtitle Options", padding=10)
        options_frame.pack(fill='x', pady=5)

        # Subtitle type
        type_frame = ttk.Frame(options_frame)
        type_frame.pack(fill='x', pady=5)

        self.subtitle_type_var = tk.StringVar(value="soft")
        ttk.Radiobutton(type_frame, text="Soft Subtitle (can be toggled on/off)",
                       variable=self.subtitle_type_var, value="soft").pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="Hard Subtitle (burned into video)",
                       variable=self.subtitle_type_var, value="hard").pack(side='left', padx=5)

        # Subtitle style (for hard subtitles)
        style_frame = ttk.LabelFrame(options_frame, text="Hard Subtitle Style", padding=5)
        style_frame.pack(fill='x', pady=5)

        style_controls = ttk.Frame(style_frame)
        style_controls.pack(fill='x', pady=5)

        ttk.Label(style_controls, text="Font Size:").pack(side='left', padx=5)
        self.subtitle_fontsize_var = tk.StringVar(value="24")
        ttk.Spinbox(style_controls, from_=10, to=72, textvariable=self.subtitle_fontsize_var,
                   width=8).pack(side='left', padx=5)

        ttk.Label(style_controls, text="Font Color:").pack(side='left', padx=10)
        self.subtitle_color_var = tk.StringVar(value="white")
        colors = ["white", "yellow", "red", "green", "blue", "black"]
        ttk.Combobox(style_controls, textvariable=self.subtitle_color_var,
                    values=colors, width=10, state='readonly').pack(side='left', padx=5)

        # Output file
        output_frame = ttk.LabelFrame(main_container, text="Output File", padding=10)
        output_frame.pack(fill='x', pady=5)

        self.subtitle_output_entry = ttk.Entry(output_frame, width=70)
        self.subtitle_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(output_frame, text="Browse",
                  command=self.browse_subtitle_output).pack(side='left', padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Add Subtitles",
                  command=self.start_add_subtitle).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Command",
                  command=self.show_subtitle_command).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_process).pack(side='left', padx=5)

    def create_watermark_tab(self, parent):
        """Create watermark tab"""
        watermark_frame = ttk.Frame(parent)
        parent.add(watermark_frame, text="Watermark")

        main_container = ttk.Frame(watermark_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Input video
        input_frame = ttk.LabelFrame(main_container, text="Input Video", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.watermark_input_entry = ttk.Entry(input_frame, width=70)
        self.watermark_input_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(input_frame, text="Browse",
                  command=self.browse_watermark_input).pack(side='left', padx=5)

        # Watermark image
        watermark_file_frame = ttk.LabelFrame(main_container, text="Watermark Image (PNG/JPG)", padding=10)
        watermark_file_frame.pack(fill='x', pady=5)

        self.watermark_file_entry = ttk.Entry(watermark_file_frame, width=70)
        self.watermark_file_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(watermark_file_frame, text="Browse",
                  command=self.browse_watermark_file).pack(side='left', padx=5)

        # Watermark position
        position_frame = ttk.LabelFrame(main_container, text="Position", padding=10)
        position_frame.pack(fill='x', pady=5)

        pos_controls = ttk.Frame(position_frame)
        pos_controls.pack(fill='x', pady=5)

        ttk.Label(pos_controls, text="Position:").pack(side='left', padx=5)
        self.watermark_position_var = tk.StringVar(value="top-right")
        positions = [
            ("Top-Left", "top-left"),
            ("Top-Right", "top-right"),
            ("Bottom-Left", "bottom-left"),
            ("Bottom-Right", "bottom-right"),
            ("Center", "center")
        ]
        for text, value in positions:
            ttk.Radiobutton(pos_controls, text=text,
                           variable=self.watermark_position_var,
                           value=value).pack(side='left', padx=5)

        # Margin and opacity
        margin_frame = ttk.Frame(position_frame)
        margin_frame.pack(fill='x', pady=5)

        ttk.Label(margin_frame, text="Margin (pixels):").pack(side='left', padx=5)
        self.watermark_margin_var = tk.StringVar(value="10")
        ttk.Spinbox(margin_frame, from_=0, to=100, textvariable=self.watermark_margin_var,
                   width=8).pack(side='left', padx=5)

        ttk.Label(margin_frame, text="Opacity:").pack(side='left', padx=10)
        self.watermark_opacity_var = tk.StringVar(value="0.8")
        ttk.Scale(margin_frame, from_=0.0, to=1.0, orient='horizontal',
                 variable=self.watermark_opacity_var, length=150).pack(side='left', padx=5)

        self.watermark_opacity_label = ttk.Label(margin_frame, text="0.8")
        self.watermark_opacity_label.pack(side='left', padx=5)

        def update_opacity_label(var=None, index=None, mode=None):
            val = float(self.watermark_opacity_var.get())
            self.watermark_opacity_label.config(text=f"{val:.2f}")

        self.watermark_opacity_var.trace_add('write', update_opacity_label)

        # Output file
        output_frame = ttk.LabelFrame(main_container, text="Output File", padding=10)
        output_frame.pack(fill='x', pady=5)

        self.watermark_output_entry = ttk.Entry(output_frame, width=70)
        self.watermark_output_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(output_frame, text="Browse",
                  command=self.browse_watermark_output).pack(side='left', padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Add Watermark",
                  command=self.start_add_watermark).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Show Command",
                  command=self.show_watermark_command).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop",
                  command=self.stop_process).pack(side='left', padx=5)

    def create_video_info_tab(self, parent):
        """Create video info tab"""
        info_frame = ttk.Frame(parent)
        parent.add(info_frame, text="Video Info")

        main_container = ttk.Frame(info_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Input file
        input_frame = ttk.LabelFrame(main_container, text="Video File", padding=10)
        input_frame.pack(fill='x', pady=5)

        self.info_input_entry = ttk.Entry(input_frame, width=70)
        self.info_input_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(input_frame, text="Browse",
                  command=self.browse_info_input).pack(side='left', padx=5)

        # Action button
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Get Video Info",
                  command=self.get_video_info).pack(side='left', padx=5)

        # Info display
        info_display_frame = ttk.LabelFrame(main_container, text="Video Information", padding=10)
        info_display_frame.pack(fill='both', expand=True, pady=5)

        self.info_text = scrolledtext.ScrolledText(info_display_frame, height=20, wrap='word')
        self.info_text.pack(fill='both', expand=True)

    def create_bottom_panel(self):
        """Create bottom panel (status bar, progress bar, log)"""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill='x', padx=5, pady=5)

        # Progress bar
        progress_frame = ttk.Frame(bottom_frame)
        progress_frame.pack(fill='x', pady=2)

        ttk.Label(progress_frame, text="Progress:").pack(side='left', padx=5)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=5)

        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack(side='left', padx=5)

        # Log area
        log_frame = ttk.LabelFrame(bottom_frame, text="Log Output", height=150)
        log_frame.pack(fill='both', expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

    def log(self, message):
        """Add log message"""
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run([self.config['ffmpeg_path'], '-version'],
                                   capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.log(f"✓ FFmpeg found: {version_line}")
                return True
            else:
                self.log("✗ FFmpeg not found or cannot run")
                self.show_ffmpeg_setup_dialog()
                return False
        except FileNotFoundError:
            self.log("✗ FFmpeg not installed or not in system PATH")
            self.show_ffmpeg_setup_dialog()
            return False
        except Exception as e:
            self.log(f"✗ Error checking FFmpeg: {str(e)}")
            return False

    def show_ffmpeg_setup_dialog(self):
        """Show FFmpeg setup dialog"""
        msg = ("FFmpeg not found!\n\n"
               "Please ensure:\n"
               "1. FFmpeg is installed\n"
               "2. FFmpeg is added to system PATH environment variable\n"
               "3. Or specify ffmpeg.exe location via menu 'File -> Set FFmpeg Path'")
        messagebox.showwarning("FFmpeg Not Found", msg)

    def set_ffmpeg_path(self):
        """Set FFmpeg path"""
        path = filedialog.askopenfilename(
            title="Select ffmpeg.exe",
            filetypes=[("FFmpeg Executable", "ffmpeg.exe"), ("All Files", "*.*")]
        )
        if path:
            self.config['ffmpeg_path'] = path
            self.save_config()
            self.log(f"FFmpeg path set to: {path}")
            self.check_ffmpeg()

    # Conversion tab methods
    def browse_convert_input(self):
        """Browse for input file"""
        path = filedialog.askopenfilename(
            title="Select Input Video File",
            filetypes=[
                ("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm *.m4v *.mpg *.mpeg *.3gp"),
                ("All Files", "*.*")
            ],
            initialdir=self.config.get('last_input_dir', '')
        )
        if path:
            self.convert_input_entry.delete(0, 'end')
            self.convert_input_entry.insert(0, path)
            self.config['last_input_dir'] = os.path.dirname(path)
            self.save_config()

            # Auto-suggest output filename
            base = os.path.splitext(path)[0]
            ext = self.convert_format_var.get()
            suggested_output = f"{base}_converted.{ext}"
            self.convert_output_entry.delete(0, 'end')
            self.convert_output_entry.insert(0, suggested_output)

    def browse_convert_output(self):
        """Browse for output file"""
        ext = self.convert_format_var.get()
        path = filedialog.asksaveasfilename(
            title="Save Output File As",
            defaultextension=f".{ext}",
            filetypes=[
                (f"{ext.upper()} Files", f"*.{ext}"),
                ("All Files", "*.*")
            ],
            initialdir=self.config.get('last_output_dir', '')
        )
        if path:
            self.convert_output_entry.delete(0, 'end')
            self.convert_output_entry.insert(0, path)
            self.config['last_output_dir'] = os.path.dirname(path)
            self.save_config()

    def build_convert_command(self):
        """Build FFmpeg command for conversion"""
        input_file = self.convert_input_entry.get().strip()
        output_file = self.convert_output_entry.get().strip()

        if not input_file or not output_file:
            raise ValueError("Please specify both input and output files")

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        cmd = [self.config['ffmpeg_path'], '-i', input_file]

        # Hardware acceleration
        if self.convert_hw_accel_var.get():
            cmd.extend(['-hwaccel', 'auto'])

        # Video codec
        vcodec = self.convert_vcodec_var.get()
        cmd.extend(['-c:v', vcodec])

        # Quality settings (only if not copying)
        if vcodec != 'copy':
            # CRF
            if vcodec in ['libx264', 'libx265']:
                cmd.extend(['-crf', self.convert_crf_var.get()])

            # Preset
            if vcodec in ['libx264', 'libx265']:
                cmd.extend(['-preset', self.convert_preset_var.get()])

            # Bitrate (if specified)
            bitrate = self.convert_vbitrate_var.get().strip()
            if bitrate:
                cmd.extend(['-b:v', bitrate])

        # Audio codec
        acodec = self.convert_acodec_var.get()
        cmd.extend(['-c:a', acodec])

        # Resolution
        if self.convert_resize_var.get():
            width = self.convert_width_var.get().strip()
            height = self.convert_height_var.get().strip()

            if width and height:
                cmd.extend(['-vf', f'scale={width}:{height}'])
            elif width:
                cmd.extend(['-vf', f'scale={width}:-2'])
            elif height:
                cmd.extend(['-vf', f'scale=-2:{height}'])
            else:
                # Use preset resolution
                resolution = self.convert_resolution_var.get()
                if resolution != 'Custom':
                    cmd.extend(['-vf', f'scale={resolution}'])

        # FPS
        if self.convert_fps_var.get():
            fps = self.convert_fps_value_var.get()
            cmd.extend(['-r', fps])

        # Custom arguments
        custom_args = self.convert_custom_args_var.get().strip()
        if custom_args:
            cmd.extend(custom_args.split())

        # Output file
        cmd.extend(['-y', output_file])

        return cmd

    def show_convert_command(self):
        """Show the FFmpeg command that will be executed"""
        try:
            cmd = self.build_convert_command()
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)

            msg_window = tk.Toplevel(self.root)
            msg_window.title("FFmpeg Command")
            msg_window.geometry("800x200")

            text = scrolledtext.ScrolledText(msg_window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', cmd_str)
            text.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_conversion(self):
        """Start the conversion process"""
        if self.is_processing:
            messagebox.showwarning("Busy", "A process is already running!")
            return

        try:
            cmd = self.build_convert_command()
            self.log(f"Starting conversion: {' '.join(cmd)}")

            self.is_processing = True
            self.progress_label.config(text="Converting...")
            self.progress_bar.start(10)

            # Run in separate thread
            thread = threading.Thread(target=self.run_ffmpeg_process, args=(cmd,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {str(e)}")

    def run_ffmpeg_process(self, cmd):
        """Run FFmpeg process in background with progress tracking"""
        import re

        try:
            # Add progress flag to FFmpeg command
            cmd_with_progress = cmd[:1] + ['-progress', 'pipe:2'] + cmd[1:]

            self.current_process = subprocess.Popen(
                cmd_with_progress,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # Get video duration first
            duration_seconds = None

            # Read stderr (FFmpeg outputs to stderr)
            for line in self.current_process.stderr:
                line_stripped = line.strip()

                # Parse duration from FFmpeg output
                if not duration_seconds:
                    duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                    if duration_match:
                        hours, minutes, seconds = duration_match.groups()
                        duration_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        self.log(f"Video duration: {duration_seconds:.2f}s")
                        # Switch progress bar to determinate mode
                        self.root.after(0, lambda: self.progress_bar.stop())
                        self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=100))

                # Parse progress
                if duration_seconds:
                    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                    if time_match:
                        hours, minutes, seconds = time_match.groups()
                        current_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        progress = min((current_seconds / duration_seconds) * 100, 100)

                        # Update progress bar and label
                        self.root.after(0, lambda p=progress: self.progress_bar.config(value=p))
                        self.root.after(0, lambda p=progress, c=current_seconds, d=duration_seconds:
                                      self.progress_label.config(text=f"Processing: {p:.1f}% ({c:.1f}s / {d:.1f}s)"))

                # Log important messages
                if 'error' in line_stripped.lower() or 'warning' in line_stripped.lower():
                    self.log(line_stripped)

            self.current_process.wait()

            if self.current_process.returncode == 0:
                self.log("✓ Processing completed successfully!")
                self.root.after(0, lambda: self.progress_bar.config(value=100))
                self.root.after(0, lambda: messagebox.showinfo("Success", "Processing completed!"))
            else:
                self.log(f"✗ Processing failed with code {self.current_process.returncode}")
                self.root.after(0, lambda: messagebox.showerror("Error", "Processing failed!"))

        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.is_processing = False
            self.current_process = None
            self.root.after(0, lambda: self.progress_bar.config(mode='indeterminate', value=0))
            self.root.after(0, lambda: self.progress_label.config(text="Ready"))

    def stop_process(self):
        """Stop the current process"""
        if self.current_process:
            self.current_process.terminate()
            self.log("Process stopped by user")
            self.is_processing = False
            self.progress_bar.stop()
            self.progress_label.config(text="Stopped")

    def preview_video(self, video_path):
        """Preview video using FFplay"""
        if not video_path or not os.path.exists(video_path):
            messagebox.showwarning("No File", "Please select a valid video file first")
            return

        try:
            # Try to find ffplay in the same directory as ffmpeg
            ffmpeg_path = self.config['ffmpeg_path']
            if ffmpeg_path == 'ffmpeg':
                ffplay_path = 'ffplay'
            else:
                ffplay_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffplay.exe')
                if not os.path.exists(ffplay_path):
                    ffplay_path = 'ffplay'

            # Run ffplay in a separate process
            subprocess.Popen(
                [ffplay_path, '-autoexit', video_path],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.log(f"Opening preview: {os.path.basename(video_path)}")

        except FileNotFoundError:
            messagebox.showwarning("FFplay Not Found",
                                 "FFplay not found. Please ensure FFplay is installed and in your PATH.\n"
                                 "FFplay comes with FFmpeg full builds.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot preview video: {str(e)}")

    # Video editing tab methods - Trim
    def browse_trim_input(self):
        """Browse for trim input file"""
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm"), ("All Files", "*.*")]
        )
        if path:
            self.trim_input_entry.delete(0, 'end')
            self.trim_input_entry.insert(0, path)
            base = os.path.splitext(path)[0]
            self.trim_output_entry.delete(0, 'end')
            self.trim_output_entry.insert(0, f"{base}_trimmed{os.path.splitext(path)[1]}")

    def browse_trim_output(self):
        """Browse for trim output file"""
        path = filedialog.asksaveasfilename(
            title="Save Trimmed Video As",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov"), ("All Files", "*.*")]
        )
        if path:
            self.trim_output_entry.delete(0, 'end')
            self.trim_output_entry.insert(0, path)

    def build_trim_command(self):
        """Build FFmpeg command for trimming"""
        input_file = self.trim_input_entry.get().strip()
        output_file = self.trim_output_entry.get().strip()

        if not input_file or not output_file:
            raise ValueError("Please specify both input and output files")

        cmd = [self.config['ffmpeg_path'], '-i', input_file]

        # Start time
        start_time = self.trim_start_var.get().strip()
        if start_time and start_time != "00:00:00":
            cmd.extend(['-ss', start_time])

        # Duration or end time
        if self.trim_mode_var.get() == "duration":
            duration = self.trim_duration_var.get().strip()
            if duration:
                cmd.extend(['-t', duration])
        else:
            end_time = self.trim_end_var.get().strip()
            if end_time:
                cmd.extend(['-to', end_time])

        # Re-encode or copy
        if self.trim_reencode_var.get():
            cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
        else:
            cmd.extend(['-c', 'copy'])

        cmd.extend(['-y', output_file])
        return cmd

    def show_trim_command(self):
        """Show trim command"""
        try:
            cmd = self.build_trim_command()
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
            msg_window = tk.Toplevel(self.root)
            msg_window.title("FFmpeg Command")
            msg_window.geometry("800x200")
            text = scrolledtext.ScrolledText(msg_window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', cmd_str)
            text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_trim(self):
        """Start trim process"""
        if self.is_processing:
            messagebox.showwarning("Busy", "A process is already running!")
            return
        try:
            cmd = self.build_trim_command()
            self.log(f"Starting trim: {' '.join(cmd)}")
            self.is_processing = True
            self.progress_label.config(text="Trimming...")
            self.progress_bar.start(10)
            thread = threading.Thread(target=self.run_ffmpeg_process, args=(cmd,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {str(e)}")

    # Video editing tab methods - Merge
    def add_merge_files(self):
        """Add files to merge list"""
        files = filedialog.askopenfilenames(
            title="Select Video Files to Merge",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm"), ("All Files", "*.*")]
        )
        for file in files:
            if file not in self.merge_files:
                self.merge_files.append(file)
                self.merge_listbox.insert('end', file)

    def remove_merge_file(self):
        """Remove selected file from merge list"""
        selection = self.merge_listbox.curselection()
        if selection:
            idx = selection[0]
            self.merge_listbox.delete(idx)
            del self.merge_files[idx]

    def clear_merge_files(self):
        """Clear all files from merge list"""
        self.merge_listbox.delete(0, 'end')
        self.merge_files.clear()

    def move_merge_up(self):
        """Move selected file up in the list"""
        selection = self.merge_listbox.curselection()
        if selection and selection[0] > 0:
            idx = selection[0]
            self.merge_files[idx], self.merge_files[idx-1] = self.merge_files[idx-1], self.merge_files[idx]
            self.merge_listbox.delete(idx)
            self.merge_listbox.insert(idx-1, self.merge_files[idx-1])
            self.merge_listbox.selection_set(idx-1)

    def move_merge_down(self):
        """Move selected file down in the list"""
        selection = self.merge_listbox.curselection()
        if selection and selection[0] < len(self.merge_files) - 1:
            idx = selection[0]
            self.merge_files[idx], self.merge_files[idx+1] = self.merge_files[idx+1], self.merge_files[idx]
            self.merge_listbox.delete(idx)
            self.merge_listbox.insert(idx+1, self.merge_files[idx+1])
            self.merge_listbox.selection_set(idx+1)

    def browse_merge_output(self):
        """Browse for merge output file"""
        path = filedialog.asksaveasfilename(
            title="Save Merged Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if path:
            self.merge_output_entry.delete(0, 'end')
            self.merge_output_entry.insert(0, path)

    def build_merge_command(self):
        """Build FFmpeg command for merging"""
        if len(self.merge_files) < 2:
            raise ValueError("Please add at least 2 files to merge")

        output_file = self.merge_output_entry.get().strip()
        if not output_file:
            raise ValueError("Please specify output file")

        # Create temp concat file
        import tempfile
        fd, concat_file = tempfile.mkstemp(suffix='.txt', text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for file in self.merge_files:
                f.write(f"file '{file}'\n")

        cmd = [self.config['ffmpeg_path'], '-f', 'concat', '-safe', '0', '-i', concat_file]

        if self.merge_reencode_var.get():
            cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
        else:
            cmd.extend(['-c', 'copy'])

        cmd.extend(['-y', output_file])

        # Store concat file path for cleanup
        self.temp_concat_file = concat_file
        return cmd

    def show_merge_command(self):
        """Show merge command"""
        try:
            cmd = self.build_merge_command()
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
            msg_window = tk.Toplevel(self.root)
            msg_window.title("FFmpeg Command")
            msg_window.geometry("800x200")
            text = scrolledtext.ScrolledText(msg_window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', cmd_str)
            text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_merge(self):
        """Start merge process"""
        if self.is_processing:
            messagebox.showwarning("Busy", "A process is already running!")
            return
        try:
            cmd = self.build_merge_command()
            self.log(f"Starting merge: {' '.join(cmd)}")
            self.is_processing = True
            self.progress_label.config(text="Merging...")
            self.progress_bar.start(10)
            thread = threading.Thread(target=self.run_ffmpeg_process, args=(cmd,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {str(e)}")

    # Video editing tab methods - Filters
    def browse_filter_input(self):
        """Browse for filter input file"""
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm"), ("All Files", "*.*")]
        )
        if path:
            self.filter_input_entry.delete(0, 'end')
            self.filter_input_entry.insert(0, path)
            base = os.path.splitext(path)[0]
            self.filter_output_entry.delete(0, 'end')
            self.filter_output_entry.insert(0, f"{base}_filtered{os.path.splitext(path)[1]}")

    def browse_filter_output(self):
        """Browse for filter output file"""
        path = filedialog.asksaveasfilename(
            title="Save Filtered Video As",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov"), ("All Files", "*.*")]
        )
        if path:
            self.filter_output_entry.delete(0, 'end')
            self.filter_output_entry.insert(0, path)

    def build_filter_command(self):
        """Build FFmpeg command with filters"""
        input_file = self.filter_input_entry.get().strip()
        output_file = self.filter_output_entry.get().strip()

        if not input_file or not output_file:
            raise ValueError("Please specify both input and output files")

        cmd = [self.config['ffmpeg_path'], '-i', input_file]

        # Build filter chain
        filters = []

        # Rotation
        rotate = self.filter_rotate_var.get()
        if rotate != "none":
            if rotate == "90":
                filters.append("transpose=1")
            elif rotate == "270":
                filters.append("transpose=2")
            elif rotate == "180":
                filters.append("transpose=1,transpose=1")

        # Flip
        if self.filter_hflip_var.get():
            filters.append("hflip")
        if self.filter_vflip_var.get():
            filters.append("vflip")

        # Speed
        speed = float(self.filter_speed_var.get())
        if speed != 1.0:
            filters.append(f"setpts={1/speed}*PTS")

        # Brightness/Contrast/Saturation
        brightness = float(self.filter_brightness_var.get())
        contrast = float(self.filter_contrast_var.get())
        saturation = float(self.filter_saturation_var.get())
        if brightness != 0 or contrast != 1.0 or saturation != 1.0:
            filters.append(f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}")

        # Blur
        if self.filter_blur_var.get():
            radius = self.filter_blur_radius_var.get()
            filters.append(f"boxblur={radius}:{radius}")

        # Apply filters
        if filters:
            filter_str = ','.join(filters)
            cmd.extend(['-vf', filter_str])

        cmd.extend(['-c:v', 'libx264', '-c:a', 'copy', '-y', output_file])
        return cmd

    def show_filter_command(self):
        """Show filter command"""
        try:
            cmd = self.build_filter_command()
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
            msg_window = tk.Toplevel(self.root)
            msg_window.title("FFmpeg Command")
            msg_window.geometry("800x200")
            text = scrolledtext.ScrolledText(msg_window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', cmd_str)
            text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_filter(self):
        """Start filter process"""
        if self.is_processing:
            messagebox.showwarning("Busy", "A process is already running!")
            return
        try:
            cmd = self.build_filter_command()
            self.log(f"Starting filter: {' '.join(cmd)}")
            self.is_processing = True
            self.progress_label.config(text="Applying filters...")
            self.progress_bar.start(10)
            thread = threading.Thread(target=self.run_ffmpeg_process, args=(cmd,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {str(e)}")

    # Audio extraction tab methods
    def browse_audio_input(self):
        """Browse for audio input file"""
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm"), ("All Files", "*.*")]
        )
        if path:
            self.audio_input_entry.delete(0, 'end')
            self.audio_input_entry.insert(0, path)
            base = os.path.splitext(path)[0]
            ext = self.audio_format_var.get()
            self.audio_output_entry.delete(0, 'end')
            self.audio_output_entry.insert(0, f"{base}.{ext}")

    def browse_audio_output(self):
        """Browse for audio output file"""
        ext = self.audio_format_var.get()
        path = filedialog.asksaveasfilename(
            title="Save Audio File As",
            defaultextension=f".{ext}",
            filetypes=[
                (f"{ext.upper()} Files", f"*.{ext}"),
                ("All Files", "*.*")
            ]
        )
        if path:
            self.audio_output_entry.delete(0, 'end')
            self.audio_output_entry.insert(0, path)

    def build_audio_command(self):
        """Build FFmpeg command for audio extraction"""
        input_file = self.audio_input_entry.get().strip()
        output_file = self.audio_output_entry.get().strip()

        if not input_file or not output_file:
            raise ValueError("Please specify both input and output files")

        cmd = [self.config['ffmpeg_path'], '-i', input_file]

        # Trim if enabled
        if self.audio_trim_enable_var.get():
            start = self.audio_trim_start_var.get().strip()
            duration = self.audio_trim_duration_var.get().strip()
            if start and start != "00:00:00":
                cmd.extend(['-ss', start])
            if duration:
                cmd.extend(['-t', duration])

        # Build audio filter chain
        audio_filters = []

        # Volume
        if self.audio_volume_enable_var.get():
            volume = float(self.audio_volume_var.get())
            if volume != 1.0:
                audio_filters.append(f"volume={volume}")

        # Fade in
        if self.audio_fadein_var.get():
            fadein_duration = float(self.audio_fadein_duration_var.get())
            audio_filters.append(f"afade=t=in:st=0:d={fadein_duration}")

        # Fade out (need duration - will estimate if trimming)
        if self.audio_fadeout_var.get():
            fadeout_duration = float(self.audio_fadeout_duration_var.get())
            # For fade out, we need to know the end time
            # This is approximate - may need adjustment
            audio_filters.append(f"afade=t=out:d={fadeout_duration}")

        # Apply audio filters
        if audio_filters:
            filter_str = ','.join(audio_filters)
            cmd.extend(['-af', filter_str])

        # No video
        cmd.append('-vn')

        # Audio codec
        codec = self.audio_codec_var.get()
        if codec == "auto":
            # Auto-select codec based on format
            format_codec_map = {
                "mp3": "libmp3lame",
                "aac": "aac",
                "m4a": "aac",
                "wav": "pcm_s16le",
                "flac": "flac",
                "ogg": "libvorbis",
                "opus": "libopus",
                "ac3": "ac3"
            }
            codec = format_codec_map.get(self.audio_format_var.get(), "aac")

        cmd.extend(['-c:a', codec])

        # Bitrate (if not using lossless codec)
        if codec not in ['flac', 'pcm_s16le']:
            bitrate = self.audio_bitrate_var.get()
            cmd.extend(['-b:a', bitrate])

        # Sample rate
        sample_rate = self.audio_sample_var.get()
        cmd.extend(['-ar', sample_rate])

        # Channels
        if self.audio_channels_var.get() == "mono":
            cmd.extend(['-ac', '1'])
        else:
            cmd.extend(['-ac', '2'])

        cmd.extend(['-y', output_file])
        return cmd

    def show_audio_command(self):
        """Show audio extraction command"""
        try:
            cmd = self.build_audio_command()
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
            msg_window = tk.Toplevel(self.root)
            msg_window.title("FFmpeg Command")
            msg_window.geometry("800x200")
            text = scrolledtext.ScrolledText(msg_window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', cmd_str)
            text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_audio_extract(self):
        """Start audio extraction process"""
        if self.is_processing:
            messagebox.showwarning("Busy", "A process is already running!")
            return
        try:
            cmd = self.build_audio_command()
            self.log(f"Starting audio extraction: {' '.join(cmd)}")
            self.is_processing = True
            self.progress_label.config(text="Extracting audio...")
            self.progress_bar.start(10)
            thread = threading.Thread(target=self.run_ffmpeg_process, args=(cmd,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {str(e)}")

    # Batch processing methods
    def add_batch_files(self):
        """Add files to batch list"""
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm"), ("All Files", "*.*")]
        )
        for file in files:
            if file not in self.batch_files:
                self.batch_files.append(file)
                self.batch_listbox.insert('end', os.path.basename(file))

    def add_batch_folder(self):
        """Add all video files from a folder"""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg')
            for file in os.listdir(folder):
                if file.lower().endswith(video_extensions):
                    full_path = os.path.join(folder, file)
                    if full_path not in self.batch_files:
                        self.batch_files.append(full_path)
                        self.batch_listbox.insert('end', file)

    def remove_batch_file(self):
        """Remove selected file from batch list"""
        selection = self.batch_listbox.curselection()
        if selection:
            idx = selection[0]
            self.batch_listbox.delete(idx)
            del self.batch_files[idx]

    def clear_batch_files(self):
        """Clear all files from batch list"""
        self.batch_listbox.delete(0, 'end')
        self.batch_files.clear()

    def browse_batch_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.batch_output_entry.delete(0, 'end')
            self.batch_output_entry.insert(0, folder)

    def build_batch_command(self, input_file, output_file):
        """Build FFmpeg command for batch operation"""
        operation = self.batch_operation_var.get()
        cmd = [self.config['ffmpeg_path'], '-i', input_file]

        if operation == "convert":
            # Format conversion
            codec = self.batch_convert_codec_var.get()
            cmd.extend(['-c:v', codec])
            if codec != 'copy':
                crf = self.batch_convert_crf_var.get()
                cmd.extend(['-crf', crf])
            cmd.extend(['-c:a', 'aac'])

        elif operation == "audio":
            # Audio extraction
            cmd.append('-vn')
            format_codec_map = {"mp3": "libmp3lame", "aac": "aac", "wav": "pcm_s16le", "flac": "flac"}
            format_ext = self.batch_audio_format_var.get()
            codec = format_codec_map.get(format_ext, "aac")
            cmd.extend(['-c:a', codec])
            if codec not in ['flac', 'pcm_s16le']:
                bitrate = self.batch_audio_bitrate_var.get()
                cmd.extend(['-b:a', bitrate])

        elif operation == "resize":
            # Resize video
            resolution = self.batch_resize_resolution_var.get()
            cmd.extend(['-vf', f'scale={resolution}'])
            cmd.extend(['-c:v', 'libx264', '-c:a', 'copy'])

        elif operation == "filter":
            # Apply filter
            filter_type = self.batch_filter_type_var.get()
            if filter_type == "grayscale":
                cmd.extend(['-vf', 'hue=s=0'])
            elif filter_type == "blur":
                cmd.extend(['-vf', 'boxblur=5:5'])
            elif filter_type == "sharpen":
                cmd.extend(['-vf', 'unsharp=5:5:1.0:5:5:0.0'])
            cmd.extend(['-c:a', 'copy'])

        cmd.extend(['-y', output_file])
        return cmd

    def start_batch_processing(self):
        """Start batch processing"""
        if not self.batch_files:
            messagebox.showwarning("No Files", "Please add files to process")
            return

        output_folder = self.batch_output_entry.get().strip()
        if not output_folder:
            messagebox.showwarning("No Output Folder", "Please specify output folder")
            return

        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create output folder: {str(e)}")
                return

        self.batch_processing = True
        self.batch_progress_bar['value'] = 0
        self.batch_progress_bar['maximum'] = len(self.batch_files)

        # Run batch processing in thread
        thread = threading.Thread(target=self.run_batch_processing, args=(output_folder,))
        thread.daemon = True
        thread.start()

    def run_batch_processing(self, output_folder):
        """Run batch processing in background"""
        operation = self.batch_operation_var.get()
        pattern = self.batch_pattern_var.get()

        # Determine output extension
        if operation == "audio":
            out_ext = f".{self.batch_audio_format_var.get()}"
        elif operation == "convert":
            out_ext = f".{self.batch_convert_format_var.get()}"
        else:
            out_ext = ".mp4"

        for idx, input_file in enumerate(self.batch_files):
            if not self.batch_processing:
                break

            # Generate output filename
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_name = pattern.replace("{name}", base_name).replace("{ext}", out_ext)
            output_file = os.path.join(output_folder, output_name)

            self.log(f"Processing {idx+1}/{len(self.batch_files)}: {os.path.basename(input_file)}")
            self.root.after(0, lambda i=idx, fn=os.path.basename(input_file): self.batch_progress_label.config(
                text=f"Processing {i+1}/{len(self.batch_files)}: {fn}"))

            try:
                cmd = self.build_batch_command(input_file, output_file)
                self.log(f"Command: {' '.join(cmd)}")

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )

                # Read output to prevent buffer blocking
                output_lines = []
                for line in process.stdout:
                    output_lines.append(line.strip())

                # Wait for process to complete
                process.wait()

                if process.returncode == 0:
                    self.log(f"✓ Completed: {os.path.basename(input_file)}")
                else:
                    self.log(f"✗ Failed: {os.path.basename(input_file)} (return code: {process.returncode})")
                    # Log last few lines of output for debugging
                    for line in output_lines[-5:]:
                        if line:
                            self.log(f"  {line}")

            except Exception as e:
                self.log(f"✗ Error processing {os.path.basename(input_file)}: {str(e)}")
                import traceback
                self.log(traceback.format_exc())

            # Update progress
            self.root.after(0, lambda: self.batch_progress_bar.step(1))

        # Batch complete
        self.batch_processing = False
        self.root.after(0, lambda: self.batch_progress_label.config(text="Batch processing complete!"))
        self.root.after(0, lambda: messagebox.showinfo("Complete", "Batch processing finished!"))
        self.log("Batch processing complete!")

    def stop_batch_processing(self):
        """Stop batch processing"""
        self.batch_processing = False
        self.log("Batch processing stopped by user")
        self.batch_progress_label.config(text="Stopped")

    # Advanced tab methods - Subtitle
    def browse_subtitle_input(self):
        """Browse for subtitle input video"""
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov"), ("All Files", "*.*")]
        )
        if path:
            self.subtitle_input_entry.delete(0, 'end')
            self.subtitle_input_entry.insert(0, path)
            base = os.path.splitext(path)[0]
            self.subtitle_output_entry.delete(0, 'end')
            self.subtitle_output_entry.insert(0, f"{base}_subtitled{os.path.splitext(path)[1]}")

    def browse_subtitle_file(self):
        """Browse for subtitle file"""
        path = filedialog.askopenfilename(
            title="Select Subtitle File",
            filetypes=[("Subtitle Files", "*.srt *.ass *.ssa *.vtt"), ("All Files", "*.*")]
        )
        if path:
            self.subtitle_file_entry.delete(0, 'end')
            self.subtitle_file_entry.insert(0, path)

    def browse_subtitle_output(self):
        """Browse for subtitle output file"""
        path = filedialog.asksaveasfilename(
            title="Save Video As",
            filetypes=[("Video Files", "*.mp4 *.mkv *.avi"), ("All Files", "*.*")]
        )
        if path:
            self.subtitle_output_entry.delete(0, 'end')
            self.subtitle_output_entry.insert(0, path)

    def build_subtitle_command(self):
        """Build FFmpeg command for adding subtitles"""
        input_file = self.subtitle_input_entry.get().strip()
        subtitle_file = self.subtitle_file_entry.get().strip()
        output_file = self.subtitle_output_entry.get().strip()

        if not input_file or not subtitle_file or not output_file:
            raise ValueError("Please specify input video, subtitle file, and output file")

        cmd = [self.config['ffmpeg_path'], '-i', input_file]

        subtitle_type = self.subtitle_type_var.get()

        if subtitle_type == "soft":
            # Soft subtitle (embedded in container)
            cmd.extend(['-i', subtitle_file, '-c', 'copy', '-c:s', 'mov_text'])
        else:
            # Hard subtitle (burned into video)
            # Escape path for Windows
            subtitle_path = subtitle_file.replace('\\', '/').replace(':', '\\:')
            fontsize = self.subtitle_fontsize_var.get()
            color = self.subtitle_color_var.get()

            # Build subtitles filter
            subtitle_filter = f"subtitles='{subtitle_path}':force_style='FontSize={fontsize},PrimaryColour=&H{color}&'"

            cmd.extend(['-vf', subtitle_filter, '-c:v', 'libx264', '-c:a', 'copy'])

        cmd.extend(['-y', output_file])
        return cmd

    def show_subtitle_command(self):
        """Show subtitle command"""
        try:
            cmd = self.build_subtitle_command()
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
            msg_window = tk.Toplevel(self.root)
            msg_window.title("FFmpeg Command")
            msg_window.geometry("800x200")
            text = scrolledtext.ScrolledText(msg_window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', cmd_str)
            text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_add_subtitle(self):
        """Start adding subtitle"""
        if self.is_processing:
            messagebox.showwarning("Busy", "A process is already running!")
            return
        try:
            cmd = self.build_subtitle_command()
            self.log(f"Adding subtitles: {' '.join(cmd)}")
            self.is_processing = True
            self.progress_label.config(text="Adding subtitles...")
            self.progress_bar.start(10)
            thread = threading.Thread(target=self.run_ffmpeg_process, args=(cmd,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {str(e)}")

    # Advanced tab methods - Watermark
    def browse_watermark_input(self):
        """Browse for watermark input video"""
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov"), ("All Files", "*.*")]
        )
        if path:
            self.watermark_input_entry.delete(0, 'end')
            self.watermark_input_entry.insert(0, path)
            base = os.path.splitext(path)[0]
            self.watermark_output_entry.delete(0, 'end')
            self.watermark_output_entry.insert(0, f"{base}_watermarked{os.path.splitext(path)[1]}")

    def browse_watermark_file(self):
        """Browse for watermark image"""
        path = filedialog.askopenfilename(
            title="Select Watermark Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*")]
        )
        if path:
            self.watermark_file_entry.delete(0, 'end')
            self.watermark_file_entry.insert(0, path)

    def browse_watermark_output(self):
        """Browse for watermark output file"""
        path = filedialog.asksaveasfilename(
            title="Save Video As",
            filetypes=[("Video Files", "*.mp4 *.mkv *.avi"), ("All Files", "*.*")]
        )
        if path:
            self.watermark_output_entry.delete(0, 'end')
            self.watermark_output_entry.insert(0, path)

    def build_watermark_command(self):
        """Build FFmpeg command for adding watermark"""
        input_file = self.watermark_input_entry.get().strip()
        watermark_file = self.watermark_file_entry.get().strip()
        output_file = self.watermark_output_entry.get().strip()

        if not input_file or not watermark_file or not output_file:
            raise ValueError("Please specify input video, watermark image, and output file")

        cmd = [self.config['ffmpeg_path'], '-i', input_file, '-i', watermark_file]

        # Calculate position
        position = self.watermark_position_var.get()
        margin = self.watermark_margin_var.get()
        opacity = self.watermark_opacity_var.get()

        # Position mapping
        position_map = {
            "top-left": f"{margin}:{margin}",
            "top-right": f"W-w-{margin}:{margin}",
            "bottom-left": f"{margin}:H-h-{margin}",
            "bottom-right": f"W-w-{margin}:H-h-{margin}",
            "center": "(W-w)/2:(H-h)/2"
        }

        overlay_pos = position_map.get(position, f"{margin}:{margin}")

        # Build overlay filter with opacity
        overlay_filter = f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[wm];[0:v][wm]overlay={overlay_pos}"

        cmd.extend(['-filter_complex', overlay_filter, '-c:v', 'libx264', '-c:a', 'copy', '-y', output_file])
        return cmd

    def show_watermark_command(self):
        """Show watermark command"""
        try:
            cmd = self.build_watermark_command()
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
            msg_window = tk.Toplevel(self.root)
            msg_window.title("FFmpeg Command")
            msg_window.geometry("800x200")
            text = scrolledtext.ScrolledText(msg_window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', cmd_str)
            text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_add_watermark(self):
        """Start adding watermark"""
        if self.is_processing:
            messagebox.showwarning("Busy", "A process is already running!")
            return
        try:
            cmd = self.build_watermark_command()
            self.log(f"Adding watermark: {' '.join(cmd)}")
            self.is_processing = True
            self.progress_label.config(text="Adding watermark...")
            self.progress_bar.start(10)
            thread = threading.Thread(target=self.run_ffmpeg_process, args=(cmd,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Error: {str(e)}")

    # Advanced tab methods - Video Info
    def browse_info_input(self):
        """Browse for info input video"""
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm"), ("All Files", "*.*")]
        )
        if path:
            self.info_input_entry.delete(0, 'end')
            self.info_input_entry.insert(0, path)

    def get_video_info(self):
        """Get video information using ffprobe"""
        input_file = self.info_input_entry.get().strip()

        if not input_file or not os.path.exists(input_file):
            messagebox.showwarning("No File", "Please select a valid video file")
            return

        try:
            # Try to find ffprobe
            ffmpeg_path = self.config['ffmpeg_path']
            if ffmpeg_path == 'ffmpeg':
                ffprobe_path = 'ffprobe'
            else:
                ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe.exe')
                if not os.path.exists(ffprobe_path):
                    ffprobe_path = 'ffprobe'

            # Run ffprobe
            cmd = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_file]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)

                # Format the information
                info_lines = []
                info_lines.append(f"=== File Information ===\n")
                info_lines.append(f"Filename: {os.path.basename(input_file)}\n")
                info_lines.append(f"Path: {input_file}\n\n")

                if 'format' in data:
                    fmt = data['format']
                    info_lines.append(f"=== Format ===\n")
                    info_lines.append(f"Format: {fmt.get('format_long_name', 'N/A')}\n")
                    info_lines.append(f"Duration: {float(fmt.get('duration', 0)):.2f} seconds\n")
                    info_lines.append(f"Size: {int(fmt.get('size', 0)) / (1024*1024):.2f} MB\n")
                    info_lines.append(f"Bitrate: {int(fmt.get('bit_rate', 0)) / 1000:.0f} kb/s\n\n")

                for stream in data.get('streams', []):
                    codec_type = stream.get('codec_type', 'unknown')

                    if codec_type == 'video':
                        info_lines.append(f"=== Video Stream ===\n")
                        info_lines.append(f"Codec: {stream.get('codec_long_name', 'N/A')}\n")
                        info_lines.append(f"Resolution: {stream.get('width', 'N/A')}x{stream.get('height', 'N/A')}\n")
                        info_lines.append(f"Frame Rate: {stream.get('r_frame_rate', 'N/A')} fps\n")
                        info_lines.append(f"Bitrate: {int(stream.get('bit_rate', 0)) / 1000:.0f} kb/s\n")
                        info_lines.append(f"Pixel Format: {stream.get('pix_fmt', 'N/A')}\n\n")

                    elif codec_type == 'audio':
                        info_lines.append(f"=== Audio Stream ===\n")
                        info_lines.append(f"Codec: {stream.get('codec_long_name', 'N/A')}\n")
                        info_lines.append(f"Sample Rate: {stream.get('sample_rate', 'N/A')} Hz\n")
                        info_lines.append(f"Channels: {stream.get('channels', 'N/A')}\n")
                        info_lines.append(f"Bitrate: {int(stream.get('bit_rate', 0)) / 1000:.0f} kb/s\n\n")

                # Display in text widget
                self.info_text.delete('1.0', 'end')
                self.info_text.insert('1.0', ''.join(info_lines))
                self.log(f"Retrieved video info for: {os.path.basename(input_file)}")

            else:
                messagebox.showerror("Error", "Failed to get video information")

        except FileNotFoundError:
            messagebox.showwarning("FFprobe Not Found",
                                 "FFprobe not found. Please ensure FFprobe is installed and in your PATH.\n"
                                 "FFprobe comes with FFmpeg full builds.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot get video info: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """FFmpeg GUI Complete Edition

Version: 1.0.0
Author: Claude & User

A comprehensive FFmpeg GUI tool supporting
video conversion, editing, audio extraction,
batch processing and more.

Tech Stack: Python + Tkinter + FFmpeg"""
        messagebox.showinfo("About", about_text)

    def show_ffmpeg_help(self):
        """Show FFmpeg command help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("FFmpeg Command Reference")
        help_window.geometry("800x600")

        text = scrolledtext.ScrolledText(help_window, wrap='word')
        text.pack(fill='both', expand=True, padx=10, pady=10)

        help_text = """FFmpeg Common Commands Reference:

1. Format Conversion:
   ffmpeg -i input.avi output.mp4

2. Compress Video:
   ffmpeg -i input.mp4 -crf 23 output.mp4

3. Trim Video:
   ffmpeg -i input.mp4 -ss 00:00:10 -t 00:00:30 output.mp4

4. Extract Audio:
   ffmpeg -i input.mp4 -vn -acodec copy output.aac

5. Merge Videos:
   ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

6. Add Watermark:
   ffmpeg -i input.mp4 -i logo.png -filter_complex "overlay=10:10" output.mp4

7. Change Resolution:
   ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

8. Adjust Bitrate:
   ffmpeg -i input.mp4 -b:v 2M output.mp4

More commands: https://ffmpeg.org/documentation.html
"""
        text.insert('1.0', help_text)
        text.config(state='disabled')


def main():
    root = tk.Tk()
    app = FFmpegGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
