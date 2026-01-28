# Common Resources Directory

This directory contains shared resources, documentation, and utilities used across the project.

## 📁 Directory Structure

```
common/
├── assets/              # Images, logos, videos, diagrams
├── data/                # Data files and databases
│   ├── raw/            # Raw medical documents
│   ├── parsed_docs/    # Processed documents
│   ├── qdrant_db/      # Vector database
│   └── docs_db/        # Document database
├── sample_images/       # Sample medical images for testing
│   ├── chest_x-ray_covid_and_normal/
│   └── skin_lesion_images/
├── uploads/             # Uploaded files storage
├── docs/                # Project documentation
│   ├── api/            # API documentation
│   ├── setup/          # Setup guides
│   ├── models/         # Model documentation
│   ├── agents/         # Agent documentation
│   └── archive/        # Archived docs
├── scripts/             # Utility scripts
│   ├── data_ingestion/ # Data loading scripts
│   ├── setup/          # Setup scripts
│   ├── tests/          # Test scripts
│   └── utils/          # Utility scripts
└── *.md                 # Project documentation files
```

## 📚 Key Documentation

### Setup & Getting Started
- `GETTING_STARTED.md` - Complete setup guide
- `RESTRUCTURE_PLAN.md` - Architecture overview
- `FINAL_STRUCTURE.md` - Current project structure

### Migration & Changes
- `AGENTS_MOVED.md` - Agent migration details
- `CLEANUP_COMPLETE.md` - Cleanup summary
- `RESTRUCTURE_COMPLETE.md` - Restructuring details

### Configuration
- `.env.example` - Environment variables template
- `.env.gemini` - Gemini API configuration
- `requirements-alternatives.txt` - Alternative dependencies

### Legal
- `LICENSE` - MIT License

## 🔧 Scripts Usage

All scripts should be run from the project root:

```bash
# Data ingestion
python common/scripts/data_ingestion/ingest_rag_data.py

# Setup
python common/scripts/setup/setup_qdrant_local.py

# Tests
python common/scripts/tests/test_psychology_agent.py

# Utils
python common/scripts/utils/check_models.py
```

## 📊 Assets

### Images
- Logo: `assets/logo_rounded.png`
- Flowcharts: `assets/final_medical_assistant_flowchart_*.png`
- Demo Videos: `assets/Multi-Agent-Medical-Assistant-*.mp4`

### Sample Images
Medical image samples for testing:
- Chest X-rays: `sample_images/chest_x-ray_covid_and_normal/`
- Skin lesions: `sample_images/skin_lesion_images/`

## 🗄️ Data

### Raw Data
Medical documents and PDFs in `data/raw/`

### Processed Data
- Parsed documents: `data/parsed_docs/`
- Vector embeddings: `data/qdrant_db/`

### Uploads
User-uploaded files stored in `uploads/` with subdirectories:
- `uploads/backend/` - Backend processed files
- `uploads/frontend/` - Frontend uploaded files
- `uploads/skin_lesion_output/` - Classification results
- `uploads/speech/` - Audio files

## 📖 Documentation

Organized documentation in `docs/`:
- **API docs**: Endpoint documentation
- **Setup guides**: Installation and configuration
- **Model docs**: AI model information
- **Agent docs**: Agent-specific documentation
- **Archive**: Historical documentation

## 🎯 Purpose

This directory keeps the root clean while maintaining access to:
- Shared resources (assets, data, samples)
- Documentation (guides, references, archives)
- Utilities (scripts, tools)
- Configuration examples

## 📝 Notes

- All scripts have been updated to work with the new structure
- Import paths reference `backend/` directory
- Data files remain accessible to both backend and scripts
- Assets can be served by backend or referenced in frontend

---

*Last updated: January 27, 2026*
