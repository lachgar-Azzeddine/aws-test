# SRM-CS Architecture Documentation Website

This directory contains the source code and build system for the **bilingual, interactive architecture documentation website** for the SRM-CS platform.

## Overview

This documentation website is built using **MkDocs with Material theme** and provides:

- ✅ **Bilingual support**: English (primary) and French (secondary) with language switcher
- ✅ **Interactive diagrams**: Mermaid diagrams for network topology, deployment sequences, and traffic flows
- ✅ **Offline-capable**: Fully self-contained website that works without internet connection
- ✅ **Searchable**: Full-text search across all documentation
- ✅ **Mobile-friendly**: Responsive design that works on all devices
- ✅ **Single source of truth**: Content derived from `../ARCHITECTURE.md`

## Features

### Documentation Sections

The website is organized into the following main sections:

1. **Home**: Overview and architectural principles
2. **Deployment Process**: 9-phase deployment sequence with diagrams
3. **Components**:
   - Infrastructure Layer (hypervisors, VMs, networking, load balancers)
   - Middleware Layer (Kubernetes, storage, security, messaging, API management, CI/CD)
   - Application Layer (EServices, GCO, application registry)
   - External Services (databases, LDAP, cloud services, communication)
4. **Dependencies & Communication**: Service interaction flows and dependency graphs
5. **Virtual Machines & Networks**:
   - VMs and Networks overview
   - VM Configurations (100/500/1000/10000 users)
   - Traffic Flow Matrix

### Interactive Diagrams

The documentation includes multiple Mermaid diagrams:

- Network topology diagrams showing VMs, zones, and load balancers
- Deployment sequence timelines
- Component dependency graphs
- Traffic flow diagrams (DMZ, LAN, Integration)
- Monitoring architecture
- Authentication flows

## Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)

### Build the Website

1. Navigate to this directory:

   ```bash
   cd architecture-docs
   ```

2. Run the build script:

   ```bash
   ./build.sh
   ```

   This will:
   - Create a Python virtual environment
   - Install all dependencies
   - Build the static website to `./site` directory

### View the Website Locally

After building, start the local development server:

```bash
./serve.sh
```

Then open your browser to:

- **English**: http://localhost:8000/en/
- **French**: http://localhost:8000/fr/

The server will automatically reload when you make changes to the documentation files.

### View Offline

To view the built website without a server:

1. Open `site/en/index.html` (English) or `site/fr/index.html` (French) in your web browser
2. All features (search, diagrams, navigation) will work offline

## Sharing the Documentation

### Option 1: Share as Archive

Compress the built site and share it:

```bash
# Create archive
tar -czf architecture-docs.tar.gz site/

# Recipients can extract and open in browser
tar -xzf architecture-docs.tar.gz
# Then open: site/en/index.html or site/fr/index.html
```

### Option 2: Deploy to Web Server

Copy the entire `site/` directory to any web server (Apache, Nginx, etc.):

```bash
# Example: Copy to web server
scp -r site/ user@webserver:/var/www/architecture/

# Then access at: https://your-server.com/architecture/en/
```

### Option 3: Deploy to GitHub Pages

```bash
# Push the site directory to gh-pages branch
mkdocs gh-deploy

# Documentation will be available at: https://your-org.github.io/repo-name/
```

## Project Structure

```
architecture-docs/
├── docs/                      # Documentation source files
│   ├── en/                    # English content
│   │   ├── index.md           # Home page
│   │   ├── deployment-process.md
│   │   ├── dependencies.md
│   │   ├── components/        # Component documentation
│   │   │   ├── infrastructure.md
│   │   │   ├── middleware.md
│   │   │   ├── applications.md
│   │   │   └── external-services.md
│   │   └── infrastructure/    # Infrastructure documentation
│   │       ├── vms-and-networks.md
│   │       ├── vm-configurations.md
│   │       └── flow-matrix.md
│   └── fr/                    # French content (same structure as en/)
├── mkdocs.yml                 # MkDocs configuration
├── requirements.txt           # Python dependencies
├── build.sh                   # Build script
├── serve.sh                   # Development server script
├── README.md                  # This file
├── venv/                      # Python virtual environment (created by build.sh)
└── site/                      # Built website (created by build.sh)
```

## Updating the Documentation

### Editing Content

1. Edit the Markdown files in `docs/en/` or `docs/fr/` directories
2. Run `./serve.sh` to preview changes in real-time
3. Rebuild with `./build.sh` to generate the final static site

### Updating from ARCHITECTURE.md

If the main `ARCHITECTURE.md` file is updated:

1. Manually sync changes to the relevant section files in `docs/en/`
2. Update French translations in `docs/fr/` if needed
3. Rebuild the site with `./build.sh`

**Note**: The current English content is complete with all sections. Some French sections are stubs/references to English content and can be fully translated as needed.

### Adding New Diagrams

Mermaid diagrams are embedded directly in Markdown files using fenced code blocks:

```markdown
\`\`\`mermaid
graph TB
    A[Start] --> B[Process]
    B --> C[End]
\`\`\`
```

Supported diagram types:

- `graph` / `flowchart`: Flowcharts and process diagrams
- `sequenceDiagram`: Sequence diagrams for interactions
- `classDiagram`: Class diagrams
- `stateDiagram`: State machines
- `erDiagram`: Entity-relationship diagrams
- `gantt`: Gantt charts

See [Mermaid documentation](https://mermaid.js.org/) for syntax details.

### Customizing the Theme

Edit `mkdocs.yml` to customize:

- Color scheme (primary, accent colors)
- Logo and favicon
- Navigation structure
- Enabled features
- Footer content

See [Material for MkDocs documentation](https://squidfunk.github.io/mkdocs-material/) for all options.

## Advanced Usage

### Manual Build

If you prefer to build manually without the script:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build the site
mkdocs build --clean

# Or serve locally
mkdocs serve
```

### Clean Build

To completely clean and rebuild:

```bash
# Remove virtual environment and built site
rm -rf venv site

# Rebuild from scratch
./build.sh
```

### Change Port for Development Server

Edit `serve.sh` and change the port:

```bash
mkdocs serve -a localhost:9000  # Change from 8000 to 9000
```

## Troubleshooting

### "Python 3 is not installed"

Install Python 3.8 or higher:

- **Ubuntu/Debian**: `sudo apt install python3 python3-venv python3-pip`
- **macOS**: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### "mkdocs.yml not found"

Make sure you're running the scripts from the `architecture-docs` directory:

```bash
cd /path/to/srm-cs/runner-src/backend/architecture-docs
./build.sh
```

### Diagrams Not Rendering

If Mermaid diagrams don't render:

1. Check that `pymdownx.superfences` is enabled in `mkdocs.yml`
2. Verify Mermaid syntax is correct
3. Try clearing browser cache
4. Rebuild the site with `./build.sh`

### Search Not Working

Search should work offline. If it doesn't:

1. Verify `search` plugin is enabled in `mkdocs.yml`
2. Rebuild the site
3. Try opening in a different browser

### Language Switcher Not Showing

Check that:

1. `i18n` plugin is enabled in `mkdocs.yml`
2. Both `en` and `fr` directories exist under `docs/`
3. Files have matching names in both language directories

## Dependencies

All dependencies are defined in `requirements.txt`:

- **mkdocs**: Static site generator
- **mkdocs-material**: Material Design theme
- **mkdocs-static-i18n**: Internationalization plugin
- **mkdocs-mermaid2-plugin**: Mermaid diagram support
- **mkdocs-offline**: Offline support
- **mkdocs-minify-plugin**: HTML/JS/CSS minification
- **pymdown-extensions**: Enhanced Markdown features

## Contributing

### Completing French Translations

Some French sections currently reference the English content. To complete the translations:

1. Translate the content from `docs/en/[section].md` to `docs/fr/[section].md`
2. Maintain the same file structure and Mermaid diagrams (diagrams work in any language)
3. Update technical terms appropriately (some terms like "Kubernetes" remain in English)
4. Rebuild to test: `./build.sh`

### Adding New Sections

1. Create the new `.md` file in `docs/en/` (and `docs/fr/` for French)
2. Add the section to `nav:` in `mkdocs.yml`
3. Add French translation of section title to `nav_translations:` in `mkdocs.yml`
4. Rebuild and test

## License

This documentation is part of the SRM-CS project.

## Support

For questions or issues:

1. Check this README
2. Review the [MkDocs Material documentation](https://squidfunk.github.io/mkdocs-material/)
3. Contact the SRM-CS platform team

---

**Happy documenting!** 📚
