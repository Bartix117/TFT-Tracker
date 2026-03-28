# ♟️ TFT Match & Meta Tracker

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet)
![Riot API](https://img.shields.io/badge/Riot%20Games-API-red)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

A modern, asynchronous desktop application built with Python that tracks Teamfight Tactics (TFT) player statistics, live game status, and current meta compositions. It utilizes the official Riot Games API to fetch real-time data and presents it in a sleek, dark-themed UI.

<p align="center">
  </p>

## ✨ Features

* **Global Player Search:** Supports searching for players across multiple regions (EUNE, EUW, NA, etc.) using Riot ID (Name + Tag).
* **Ranked Statistics:** Instantly displays current rank, LP, wins, and losses for both TFT Ranked Solo and Double Up queues.
* **Live Game Detection:** Asynchronously checks if a player is currently in a match.
* **Real-time Match Timer:** Visual timer that syncs with the live game duration without freezing the GUI, powered by background threading.
* **Meta Compositions Viewer:** Fetches and displays up-to-date TFT meta team comps, including tiers, strategies, and full unit rosters.
* **Modern UI/UX:** Built with `customtkinter` for a native, responsive, and dark-mode-first aesthetic, including dynamic progress bars and hover effects.

## 🛠️ Technologies Used

* **CustomTkinter** - For the modern graphical user interface.
* **Requests** - For handling HTTP GET requests to the Riot Games API.
* **Threading** - For asynchronous API calls and background validation loops to keep the UI responsive.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/tft-tracker.git](https://github.com/YOUR_USERNAME/tft-tracker.git)
   cd tft-tracker


TFT-Tracker isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.