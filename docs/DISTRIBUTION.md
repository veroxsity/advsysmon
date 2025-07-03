# Creating Your Own APT Repository

To make your Advanced System Monitor installable via `apt`, you need to create a personal APT repository. Here's how:

## Option 1: Using GitHub Releases + Custom Repository

### Step 1: Create a GitHub Repository
1. Create a new repository on GitHub: `advsysmon`
2. Upload your built `.deb` package to GitHub Releases

### Step 2: Set Up APT Repository Structure
```bash
# Create repository structure
mkdir -p repo/dists/stable/main/binary-amd64
mkdir -p repo/pool/main/a/advanced-sysmon

# Copy your .deb file
cp packaging/advanced-sysmon.deb repo/pool/main/a/advanced-sysmon/

# Create Packages file
cd repo
dpkg-scanpackages pool/ /dev/null | gzip -9c > dists/stable/main/binary-amd64/Packages.gz
dpkg-scanpackages pool/ /dev/null > dists/stable/main/binary-amd64/Packages

# Create Release file
cat > dists/stable/Release << EOF
Archive: stable
Component: main
Origin: YourName
Label: Advanced System Monitor Repository
Architecture: amd64
Description: Repository for Advanced System Monitor
EOF
```

### Step 3: Sign the Repository (Optional but Recommended)
```bash
# Generate GPG key if you don't have one
gpg --full-generate-key

# Sign the Release file
cd dists/stable
gpg --clearsign -o InRelease Release
gpg -abs -o Release.gpg Release
```

### Step 4: Host the Repository
You can host this on:
- GitHub Pages
- Your own web server
- Services like Packagecloud.io
- Launchpad PPA (for Ubuntu)

## Option 2: Using Packagecloud.io (Recommended)

1. Sign up at https://packagecloud.io
2. Create a new repository
3. Upload your `.deb` file
4. They provide installation instructions automatically

## Option 3: Ubuntu PPA (Launchpad)

1. Create account at https://launchpad.net
2. Create a PPA
3. Upload source package (requires source format)
4. Ubuntu builds it automatically

## Option 4: Local Repository

For local/internal use:

```bash
# Create local repository
sudo mkdir -p /var/www/html/repo
sudo cp -r repo/* /var/www/html/repo/

# Add to sources.list
echo "deb [trusted=yes] http://your-server/repo stable main" | sudo tee /etc/apt/sources.list.d/advanced-sysmon.list

# Update and install
sudo apt update
sudo apt install advanced-sysmon
```

## Quick Start with Your Package

For now, users can install directly:

```bash
# Download and install the .deb package
wget https://github.com/veroxsity/advsysmon/releases/download/v1.0.0/advanced-sysmon.deb
sudo dpkg -i advanced-sysmon.deb
# Dependencies are installed automatically during package installation

# Run the application
advanced-sysmon

# Or use the Python package
pip install advanced-sysmon

# Or use the installation script
wget https://github.com/veroxsity/advsysmon/releases/download/v1.0.0/advanced-sysmon-install.tar.gz
tar -xzf advanced-sysmon-install.tar.gz
./install.sh
```

## Package Installation Notes

The Debian package automatically handles dependency installation using pip3 with the `--break-system-packages` flag for newer systems, falling back to `--user` installation if needed. This ensures compatibility across different Linux distributions and Python setups.

## Distribution Methods Summary

1. **`.deb` package**: Best for Debian/Ubuntu systems
2. **PyPI package**: Cross-platform Python installation
3. **Installation script**: Universal installation method
4. **APT repository**: Professional distribution method

Choose the method that best fits your distribution needs!
