# Tabber <img src=".assets/tab.png" alt="Tab" width="34" height="24"> 
#### A Searchable Alt-Tab for Power Users

---

## Overview

Tabber is a lightweight window switcher for Windows that provides fast, keyboard-driven navigation between open applications. Unlike the traditional Alt+Tab interface, Tabber offers a searchable, always-on-top overlay with fuzzy matching capabilities for quick window discovery and switching.

![Demo](.assets/demo.gif)


> **Note:** This is primarily a learning project and proof of concept rather than a polished product. While it includes all the core functionality you'd expect from a window switcher, there's plenty of room for additional features and refinements. I may revisit and expand it in the future, especially if it proves useful to others.

---

## Features

- **Global Hotkeys**: Instant access via `Alt+W` to start search and `Alt+Ctrl+Q` to quit
- **Smart Search & Filtering**: Fast fuzzy matching on window titles with automatic filtering of system processes
- **Real-time Updates**: Automatically detects new windows and closed applications
- **Seamless Switching**: Brings target windows to foreground, including minimized ones

---

## Dependencies

### Libraries/Modules
- **PyQt5** - Modern GUI framework for the search interface
- **pynput** - Global hotkey detection and keyboard input handling
- **pywin32** - Windows API integration for window management
- **psutil** - System process information and monitoring
- **rapidfuzz** - High-performance fuzzy string matching

### Standard Library
- `threading` - Background window monitoring
- `logging` - Comprehensive error tracking and debugging
- `time` - Performance timing and caching logic

---

## Setup

### Prerequisites
- Windows 10/11
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/youssefashourrr/tabber.git
   cd tabber
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

---

## Usage

1. **Launch Tabber** - Runs silently in the background
2. **Press `Alt+W`** - Open the search interface
3. **Type to search** - Find windows by title or application name
4. **Navigate results** - Use arrow keys or click to select
5. **Press `Enter`** - Switch to the selected window
6. **Press `Escape`** - Close the search interface
7. **Press `Alt+Ctrl+Q`** - Quit Tabber