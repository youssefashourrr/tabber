# Tabber

**A Searchable Alt-Tab for Power Users**

![Demo](demo.gif)

## Overview

Tabber is a lightweight window switcher for Windows that provides fast, keyboard-driven navigation between open applications. Unlike the traditional Alt+Tab interface, Tabber offers a searchable, always-on-top overlay with fuzzy matching capabilities for quick window discovery and switching.

> **Note:** This is primarily a learning project and proof of concept rather than a polished product. While it includes all the core functionality you'd expect from a window switcher, there's plenty of room for additional features and refinements. I may revisit and expand it in the future, especially if it proves useful to others.

## Features

- **Global Hotkeys**: 
  - `Alt+W` - Open window searchbar
  - `Alt+Ctrl+Q` - Quit application
- **Smart Search**: Fuzzy search across window titles and process names using advanced string matching while excluding system processes and tool windows
- **Real-time Updates**: Automatically refreshes window list as applications open/close
- **System Integration**: Seamlessly brings target windows to foreground, handling minimized windows
- **Performance Optimized**: Cached window enumeration with background monitoring

## Libraries/Modules

### Core Dependencies
- **PyQt5** - Modern GUI framework for the search interface
- **pynput** - Global hotkey detection and keyboard input handling
- **pywin32** - Windows API integration for window management
- **psutil** - System process information and monitoring
- **rapidfuzz** - High-performance fuzzy string matching for search

### Python Standard Library
- `threading` - Background window monitoring
- `logging` - Comprehensive error tracking and debugging
- `time` - Performance timing and caching logic

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
   python src/main.py
   ```

### Usage

1. **Launch Tabber** - Runs silently in the background
2. **Press `Alt+W`** - Open the search interface
3. **Type to search** - Find windows by title or application name
4. **Navigate results** - Use arrow keys or click to select
5. **Press `Enter`** - Switch to the selected window
6. **Press `Escape`** - Close the search interface
7. **Press `Alt+Ctrl+Q`** - Quit Tabber