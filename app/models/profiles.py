PROFILES = {
    "Essential": {
        "description": "Everyday essentials for a clean Ubuntu installation.",
        "packages": ["curl", "wget", "git", "vlc", "gnome-tweaks"],
        "services": 1,
        "steps": [
            ("Refresh package index", "apt update", "Required", True),
            ("Install everyday essentials", "curl wget git vlc gnome-tweaks", "5 packages", True),
            ("Review desktop tools", "GNOME utilities and quality-of-life tools", "Optional", False),
            ("Link dotfiles", "Configure links from the Dotfiles page", "Optional", False),
            ("Review services", "Service changes remain explicit", "Optional", False),
        ],
    },
    "Developer": {
        "description": "Core tools for software development.",
        "packages": ["git", "curl", "build-essential", "ripgrep", "python3-pip", "python3-venv"],
        "services": 2,
        "steps": [
            ("Refresh package index", "apt update", "Required", True),
            ("Install developer tools", "git curl build-essential ripgrep python3-pip python3-venv", "6 packages", True),
            ("Install Docker Engine", "Optional container development environment", "Optional", False),
            ("Link dotfiles", "Preview and configure links from the Dotfiles page", "Optional", False),
            ("Enable services", "SSH and UFW are managed explicitly", "Optional", False),
        ],
    },
    "Gaming": {
        "description": "A practical base for Linux gaming.",
        "packages": ["steam", "gamemode", "mangohud", "wine"],
        "services": 0,
        "steps": [
            ("Refresh package index", "apt update", "Required", True),
            ("Install gaming stack", "steam gamemode mangohud wine", "4 packages", True),
            ("Review performance tools", "GameMode and MangoHud", "Included", True),
            ("Link dotfiles", "Optional game/configuration links", "Optional", False),
            ("Review services", "No service changes selected", "Optional", False),
        ],
    },
    "Creator": {
        "description": "Creative applications for graphics, video and streaming.",
        "packages": ["gimp", "blender", "obs-studio", "audacity", "inkscape", "kdenlive"],
        "services": 0,
        "steps": [
            ("Refresh package index", "apt update", "Required", True),
            ("Install creative suite", "gimp blender obs-studio audacity inkscape kdenlive", "6 packages", True),
            ("Review media tools", "Graphics, video, audio and streaming", "Included", True),
            ("Link dotfiles", "Optional application configuration links", "Optional", False),
            ("Review services", "No service changes selected", "Optional", False),
        ],
    },
    "Custom": {
        "description": "Build a setup from packages you select yourself.",
        "packages": [],
        "services": 0,
        "steps": [
            ("Refresh package index", "apt update", "Required", True),
            ("Install selected packages", "Choose software from Package library", "Custom", True),
            ("Review optional tasks", "No preset extras are enabled", "Optional", False),
            ("Link dotfiles", "Configure links from the Dotfiles page", "Optional", False),
            ("Review services", "No service changes selected", "Optional", False),
        ],
    },
}
